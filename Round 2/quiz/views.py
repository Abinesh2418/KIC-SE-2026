from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib import messages
from django.conf import settings as django_settings
from .models import Event, Challenge, Participant, Submission
from .forms import ParticipantRegisterForm, LoginForm, EventSettingsForm
import json
import os
import zipfile
import tempfile


def home(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('quiz:admin_dashboard')
        return redirect('quiz:waiting_room')
    return render(request, 'quiz/home.html')


def register(request):
    if request.method == 'POST':
        form = ParticipantRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            event = Event.objects.first()
            Participant.objects.create(
                user=user,
                event=event,
                phone_number=form.cleaned_data.get('phone_number', ''),
            )
            messages.success(request, 'Registration successful! Please wait for admin approval.')
            return redirect('quiz:login')
    else:
        form = ParticipantRegisterForm()
    return render(request, 'quiz/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                if user.is_staff:
                    return redirect('quiz:admin_dashboard')
                return redirect('quiz:waiting_room')
            else:
                messages.error(request, 'Invalid credentials.')
    else:
        form = LoginForm()
    return render(request, 'quiz/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('quiz:home')


@login_required
def waiting_room(request):
    if request.user.is_staff:
        return redirect('quiz:admin_dashboard')
    try:
        participant = request.user.participant
    except Participant.DoesNotExist:
        event = Event.objects.first()
        participant = Participant.objects.create(user=request.user, event=event)

    event = participant.event
    context = {
        'participant': participant,
        'event': event,
    }

    if participant.status == 'disqualified':
        return render(request, 'quiz/disqualified.html', context)

    if participant.has_submitted:
        return redirect('quiz:result')

    if participant.status == 'approved' and event and event.is_running:
        return redirect('quiz:quiz')

    return render(request, 'quiz/waiting_room.html', context)


@login_required
def challenge_view(request):
    """Main challenge page — participants download notebooks, fix bugs, and upload."""
    if request.user.is_staff:
        return redirect('quiz:admin_dashboard')
    try:
        participant = request.user.participant
    except Participant.DoesNotExist:
        return redirect('quiz:waiting_room')
    event = participant.event

    if participant.status != 'approved':
        return redirect('quiz:waiting_room')

    if not event or not event.is_running:
        if not participant.has_submitted and participant.started_at:
            participant.finished_at = timezone.now()
            participant.has_submitted = True
            participant.calculate_score()
        return redirect('quiz:waiting_room')

    if participant.has_submitted:
        return redirect('quiz:result')

    if participant.status == 'disqualified':
        return render(request, 'quiz/disqualified.html', {
            'participant': participant,
            'event': event,
        })

    # Mark participant start time (their personal timer starts now)
    if not participant.started_at:
        participant.started_at = timezone.now()
        participant.save()

    # Auto-submit if participant's personal timer has expired
    if participant.is_time_up:
        participant.finished_at = timezone.now()
        participant.has_submitted = True
        participant.calculate_score()
        return redirect('quiz:result')

    challenges = Challenge.objects.filter(event=event).order_by('order')

    # Get existing submissions for this participant
    existing_submissions = {}
    for sub in Submission.objects.filter(participant=participant, challenge__event=event):
        existing_submissions[sub.challenge_id] = {
            'filename': os.path.basename(sub.uploaded_file.name) if sub.uploaded_file else '',
            'submitted_at': sub.submitted_at.strftime('%H:%M:%S') if sub.submitted_at else '',
        }

    context = {
        'challenges': challenges,
        'event': event,
        'participant': participant,
        'time_remaining': participant.time_remaining_seconds,
        'max_tab_switches': event.max_tab_switches,
        'tab_switch_count': participant.tab_switch_count,
        'existing_submissions': json.dumps(existing_submissions),
        'submission_count': len(existing_submissions),
        'total_challenges': challenges.count(),
    }
    return render(request, 'quiz/challenge.html', context)


@login_required
def upload_submission(request):
    """Handle notebook file upload for a challenge."""
    if request.method == 'POST':
        participant = request.user.participant

        if participant.has_submitted or participant.status == 'disqualified':
            return JsonResponse({'status': 'error', 'message': 'Already submitted or disqualified'})

        challenge_id = request.POST.get('challenge_id')
        uploaded_file = request.FILES.get('notebook_file')

        if not challenge_id or not uploaded_file:
            return JsonResponse({'status': 'error', 'message': 'Missing challenge_id or file'})

        # Validate file type
        if not uploaded_file.name.endswith('.ipynb'):
            return JsonResponse({'status': 'error', 'message': 'Only .ipynb files are accepted'})

        # Max file size: 10MB
        if uploaded_file.size > 10 * 1024 * 1024:
            return JsonResponse({'status': 'error', 'message': 'File too large. Max 10MB.'})

        challenge = get_object_or_404(Challenge, id=challenge_id)

        # Create or update submission
        submission, created = Submission.objects.update_or_create(
            participant=participant,
            challenge=challenge,
            defaults={'uploaded_file': uploaded_file}
        )

        return JsonResponse({
            'status': 'ok',
            'filename': os.path.basename(submission.uploaded_file.name),
            'submitted_at': submission.submitted_at.strftime('%H:%M:%S') if submission.submitted_at else '',
        })

    return JsonResponse({'status': 'error'}, status=400)


@login_required
def record_tab_switch(request):
    if request.method == 'POST':
        participant = request.user.participant
        event = participant.event

        if participant.has_submitted or participant.status == 'disqualified':
            return JsonResponse({'status': 'already_done'})

        participant.tab_switch_count += 1
        violated = participant.tab_switch_count >= event.max_tab_switches
        participant.tab_switch_violated = violated
        participant.save()

        if violated:
            # Auto-submit
            participant.finished_at = timezone.now()
            participant.has_submitted = True
            participant.calculate_score()
            return JsonResponse({
                'status': 'violated',
                'message': 'Tab switch limit exceeded. Your submissions have been auto-finalized.',
                'count': participant.tab_switch_count,
            })

        return JsonResponse({
            'status': 'warning',
            'count': participant.tab_switch_count,
            'remaining': event.max_tab_switches - participant.tab_switch_count,
        })
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def submit_challenge(request):
    """Finalize the challenge — no more uploads after this."""
    if request.method == 'POST':
        participant = request.user.participant
        if not participant.has_submitted:
            participant.finished_at = timezone.now()
            participant.has_submitted = True
            participant.calculate_score()
        return JsonResponse({'status': 'ok', 'score': participant.score})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def time_remaining(request):
    try:
        participant = request.user.participant
    except Participant.DoesNotExist:
        return JsonResponse({'remaining': 0, 'is_running': False})
    event = participant.event
    if event:
        remaining = participant.time_remaining_seconds
        # Auto-submit server-side if time is up
        if participant.is_time_up and not participant.has_submitted and participant.started_at:
            participant.finished_at = timezone.now()
            participant.has_submitted = True
            participant.calculate_score()
            return JsonResponse({'remaining': 0, 'is_running': False, 'time_up': True})
        return JsonResponse({
            'remaining': remaining,
            'is_running': event.is_running,
        })
    return JsonResponse({'remaining': 0, 'is_running': False})


@login_required
def event_status(request):
    try:
        participant = request.user.participant
    except Participant.DoesNotExist:
        return JsonResponse({'is_active': False, 'is_running': False, 'status': 'error'})
    event = participant.event
    if event:
        return JsonResponse({
            'is_active': event.is_active,
            'is_running': event.is_running,
            'status': participant.status,
            'has_submitted': participant.has_submitted,
        })
    return JsonResponse({'is_active': False, 'is_running': False, 'status': participant.status})


@login_required
def result_view(request):
    participant = request.user.participant
    event = participant.event
    challenges = Challenge.objects.filter(event=event) if event else Challenge.objects.none()
    submissions = Submission.objects.filter(participant=participant).select_related('challenge')
    total_bugs = sum(c.total_bugs for c in challenges)
    context = {
        'participant': participant,
        'total': total_bugs,
        'submissions': submissions,
        'challenges': challenges,
        'show_score': event.show_score_to_participant if event else False,
    }
    return render(request, 'quiz/result.html', context)


def leaderboard(request):
    event = Event.objects.first()
    is_admin = request.user.is_authenticated and request.user.is_staff

    # Check if leaderboard is public or user is admin
    if event and not event.leaderboard_public and not is_admin:
        return render(request, 'quiz/leaderboard_private.html', {'event': event})

    participants = Participant.objects.filter(
        event=event,
        has_submitted=True,
    ).exclude(status='disqualified').order_by('-score', 'time_taken_ms')

    total_bugs = sum(c.total_bugs for c in Challenge.objects.filter(event=event)) if event else 0

    context = {
        'participants': participants,
        'event': event,
        'is_admin': is_admin,
        'total_bugs': total_bugs,
    }
    return render(request, 'quiz/leaderboard.html', context)


@login_required
def download_notebook(request, challenge_id):
    """Download a single challenge notebook."""
    try:
        participant = request.user.participant
    except Participant.DoesNotExist:
        return redirect('quiz:waiting_room')

    if participant.status != 'approved':
        return redirect('quiz:waiting_room')

    event = participant.event
    if not event or not event.is_running:
        return redirect('quiz:waiting_room')

    challenge = get_object_or_404(Challenge, id=challenge_id, event=event)
    round2_dir = os.path.join(django_settings.BASE_DIR, 'Yugam_ML_Challenge-2')
    notebook_path = os.path.join(round2_dir, challenge.notebook_filename)

    if not os.path.exists(notebook_path):
        raise Http404("Notebook file not found.")

    return FileResponse(
        open(notebook_path, 'rb'),
        content_type='application/octet-stream',
        as_attachment=True,
        filename=challenge.notebook_filename
    )


@login_required
def download_all_materials(request):
    """Download all Round 2 materials as a ZIP file."""
    try:
        participant = request.user.participant
    except Participant.DoesNotExist:
        return redirect('quiz:waiting_room')

    if participant.status != 'approved':
        return redirect('quiz:waiting_room')

    event = participant.event
    if not event or not event.is_running:
        return redirect('quiz:waiting_room')

    round2_dir = os.path.join(django_settings.BASE_DIR, 'Yugam_ML_Challenge-2')
    if not os.path.exists(round2_dir):
        raise Http404("Round 2 materials not found.")

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
    try:
        with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zf:
            files_to_include = [
                'ml_debug_classification_final.ipynb',
                'ml_debug_regression_final.ipynb',
                'titanic_data.csv',
                'requirements.txt',
                'setup.bat',
            ]
            for fname in files_to_include:
                fpath = os.path.join(round2_dir, fname)
                if os.path.exists(fpath):
                    zf.write(fpath, os.path.join('Yugam_ML_Challenge-2', fname))

        tmp.close()
        tmp_path = tmp.name
        f = open(tmp_path, 'rb')
        response = FileResponse(
            f,
            content_type='application/zip',
            as_attachment=True,
            filename='ML_Fest_Round2_Materials.zip'
        )
        # Clean up temp file after response is served
        response['X-Sendfile'] = tmp_path
        import atexit
        atexit.register(lambda: os.path.exists(tmp_path) and os.unlink(tmp_path))
        return response
    except Exception:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)
        raise


# ============ ADMIN VIEWS ============

@staff_member_required
def admin_dashboard(request):
    event = Event.objects.first()
    if not event:
        event = Event.objects.create(name="ML Fest Round 2 - ML Debugging Challenge")

    challenges = Challenge.objects.filter(event=event)
    participants = Participant.objects.filter(event=event).select_related('user')
    pending = participants.filter(status='pending')
    approved = participants.filter(status='approved')
    disqualified = participants.filter(status='disqualified')
    submitted = participants.filter(has_submitted=True)
    violated = participants.filter(tab_switch_violated=True)

    # Get submission counts per participant
    submission_data = {}
    for p in participants:
        subs = Submission.objects.filter(participant=p)
        submission_data[p.id] = {
            'count': subs.count(),
            'graded': subs.filter(is_graded=True).count(),
        }

    settings_form = EventSettingsForm(initial={
        'duration_minutes': event.duration_minutes,
        'max_tab_switches': event.max_tab_switches,
        'leaderboard_public': event.leaderboard_public,
        'show_score_to_participant': event.show_score_to_participant,
    })

    context = {
        'event': event,
        'challenges': challenges,
        'participants': participants,
        'pending': pending,
        'approved': approved,
        'disqualified': disqualified,
        'submitted': submitted,
        'violated': violated,
        'settings_form': settings_form,
        'total_challenges': challenges.count(),
        'submission_data': submission_data,
    }
    return render(request, 'quiz/admin_dashboard.html', context)


@staff_member_required
def approve_participant(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    participant.status = 'approved'
    participant.save()
    messages.success(request, f'{participant.user.username} has been approved.')
    return redirect('quiz:admin_dashboard')


@staff_member_required
def approve_all(request):
    event = Event.objects.first()
    if event:
        Participant.objects.filter(event=event, status='pending').update(status='approved')
        messages.success(request, 'All pending participants have been approved.')
    return redirect('quiz:admin_dashboard')


@staff_member_required
def disqualify_participant(request, participant_id):
    participant = get_object_or_404(Participant, id=participant_id)
    participant.status = 'disqualified'
    if not participant.has_submitted and participant.started_at:
        participant.finished_at = timezone.now()
        participant.has_submitted = True
        participant.calculate_score()
    participant.save()
    messages.success(request, f'{participant.user.username} has been disqualified.')
    return redirect('quiz:admin_dashboard')


@staff_member_required
def start_event(request):
    event = Event.objects.first()
    if event:
        event.is_active = True
        if not event.started_at:
            event.started_at = timezone.now()
        event.save()
        messages.success(request, 'Event started! Each participant\'s timer begins when they enter the challenge.')
    return redirect('quiz:admin_dashboard')


@staff_member_required
def stop_event(request):
    event = Event.objects.first()
    if event:
        event.is_active = False
        event.save()
        # Auto-submit all who haven't submitted
        active = Participant.objects.filter(event=event, has_submitted=False, started_at__isnull=False)
        for p in active:
            p.finished_at = timezone.now()
            p.has_submitted = True
            p.calculate_score()
        messages.success(request, 'Event stopped! All pending submissions auto-finalized.')
    return redirect('quiz:admin_dashboard')


@staff_member_required
def update_settings(request):
    if request.method == 'POST':
        form = EventSettingsForm(request.POST)
        if form.is_valid():
            event = Event.objects.first()
            if event:
                event.duration_minutes = form.cleaned_data['duration_minutes']
                event.max_tab_switches = form.cleaned_data['max_tab_switches']
                event.leaderboard_public = form.cleaned_data['leaderboard_public']
                event.show_score_to_participant = form.cleaned_data['show_score_to_participant']
                event.save()
                messages.success(request, 'Settings updated!')
    return redirect('quiz:admin_dashboard')


@staff_member_required
def reset_challenge(request):
    """Reset challenge: clear all submissions, scores, and submission state."""
    event = Event.objects.first()
    if event:
        # Delete all submissions (files + records)
        Submission.objects.filter(participant__event=event).delete()

        # Reset all participant state but keep their registration and approval
        Participant.objects.filter(event=event).update(
            started_at=None,
            finished_at=None,
            tab_switch_count=0,
            tab_switch_violated=False,
            score=0,
            time_taken_ms=0,
            has_submitted=False,
            status='approved',
        )

        # Reset event state
        event.is_active = False
        event.started_at = None
        event.save()

        messages.success(request, 'Challenge has been reset! All registered participants are approved and ready.')
    return redirect('quiz:admin_dashboard')


@staff_member_required
def remove_participant(request, participant_id):
    """Remove a participant and their user account from the system entirely."""
    participant = get_object_or_404(Participant, id=participant_id)
    username = participant.user.username
    user = participant.user
    Submission.objects.filter(participant=participant).delete()
    participant.delete()
    user.delete()
    messages.success(request, f'{username} has been removed from the system.')
    return redirect('quiz:admin_dashboard')


@staff_member_required
def grade_submission(request, submission_id):
    """Admin grades a submission — sets score."""
    if request.method == 'POST':
        submission = get_object_or_404(Submission, id=submission_id)
        try:
            score = int(request.POST.get('score', 0))
        except (ValueError, TypeError):
            score = 0
        notes = request.POST.get('admin_notes', '')
        submission.score = score
        submission.admin_notes = notes
        submission.is_graded = True
        submission.save()

        # Recalculate participant's total score
        submission.participant.calculate_score()

        messages.success(request, f'Graded {submission.participant.user.username} — {submission.challenge.title}: {score} pts')
    return redirect('quiz:admin_dashboard')


@staff_member_required
def download_submission(request, submission_id):
    """Admin downloads a participant's submitted notebook."""
    submission = get_object_or_404(Submission, id=submission_id)
    if not submission.uploaded_file:
        raise Http404("No file uploaded.")

    filename = f"{submission.participant.user.username}_{submission.challenge.challenge_type}.ipynb"
    return FileResponse(
        submission.uploaded_file.open('rb'),
        content_type='application/octet-stream',
        as_attachment=True,
        filename=filename
    )


@staff_member_required
def view_submissions(request, participant_id):
    """View all submissions for a specific participant."""
    participant = get_object_or_404(Participant, id=participant_id)
    submissions = Submission.objects.filter(participant=participant).select_related('challenge')
    challenges = Challenge.objects.filter(event=participant.event)

    context = {
        'participant': participant,
        'submissions': submissions,
        'challenges': challenges,
    }
    return render(request, 'quiz/view_submissions.html', context)
