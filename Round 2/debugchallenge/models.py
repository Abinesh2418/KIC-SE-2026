from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone


class CustomUser(AbstractUser):
    """Round 2 user model — separate auth table for this round."""

    class Meta:
        db_table = 'r2_user'

    def __str__(self):
        return self.username


class Event(models.Model):
    name = models.CharField(max_length=200, default="ML Fest Round 2 - ML Debugging Challenge")
    is_active = models.BooleanField(default=False)
    duration_minutes = models.PositiveIntegerField(default=60)
    max_tab_switches = models.PositiveIntegerField(default=3)
    started_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    leaderboard_public = models.BooleanField(default=True)
    show_score_to_participant = models.BooleanField(default=True)

    class Meta:
        db_table = 'r2_event'

    def __str__(self):
        return self.name

    @property
    def is_running(self):
        """Event is running when admin has activated it."""
        return self.is_active


class Challenge(models.Model):
    CHALLENGE_TYPES = [
        ('classification', 'Classification'),
        ('regression', 'Regression'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='challenges')
    title = models.CharField(max_length=200)
    description = models.TextField()
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    notebook_filename = models.CharField(max_length=200, help_text="Filename in Yugam_ML_Challenge-2/ folder")
    total_bugs = models.PositiveIntegerField(default=0)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        db_table = 'r2_challenge'

    def __str__(self):
        return f"{self.title} ({self.get_challenge_type_display()})"


class Participant(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('disqualified', 'Disqualified'),
    ]
    ROLE_CHOICES = [
        ('participant', 'Participant'),
        ('evaluator', 'Evaluator'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='r2_participant')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, default='')
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='participant')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    evaluator = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='assigned_participants',
        limit_choices_to={'role': 'evaluator'},
    )
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    tab_switch_count = models.PositiveIntegerField(default=0)
    tab_switch_violated = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    time_taken_ms = models.BigIntegerField(default=0)
    has_submitted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-score', 'time_taken_ms']
        db_table = 'r2_participant'

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"

    @property
    def time_remaining_seconds(self):
        """Per-participant timer: duration starts from when they began the challenge."""
        if not self.event:
            return 0
        if not self.started_at:
            return self.event.duration_minutes * 60
        elapsed = (timezone.now() - self.started_at).total_seconds()
        remaining = (self.event.duration_minutes * 60) - elapsed
        return max(0, int(remaining))

    @property
    def is_time_up(self):
        """Check if participant's individual timer has expired."""
        if not self.started_at or not self.event:
            return False
        elapsed = (timezone.now() - self.started_at).total_seconds()
        return elapsed >= self.event.duration_minutes * 60

    def calculate_score(self):
        """Calculate total score from evaluations by the assigned evaluator."""
        total = 0
        if self.evaluator:
            # Only count evaluations from the currently assigned evaluator
            for ev in self.evaluations_received.filter(evaluator=self.evaluator):
                total += ev.score
        else:
            # Fallback: sum all evaluations if no evaluator assigned
            for ev in self.evaluations_received.all():
                total += ev.score
        self.score = total
        self.save()
        return total


class Evaluation(models.Model):
    """Per-bug evaluation by an evaluator for a participant's notebook."""
    CHALLENGE_TYPES = [
        ('classification', 'Classification'),
        ('regression', 'Regression'),
    ]
    evaluator = models.ForeignKey(
        Participant, on_delete=models.CASCADE,
        related_name='evaluations_given',
        limit_choices_to={'role': 'evaluator'},
    )
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE,
        related_name='evaluations_received',
    )
    challenge_type = models.CharField(max_length=20, choices=CHALLENGE_TYPES)
    bug_results = models.JSONField(
        default=dict,
        help_text='Dict of bug_number(str): is_correct(bool)',
    )
    score = models.IntegerField(default=0)
    evaluated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('evaluator', 'participant', 'challenge_type')
        ordering = ['participant', 'challenge_type']
        db_table = 'r2_evaluation'

    def __str__(self):
        return (
            f"{self.evaluator.user.username} -> "
            f"{self.participant.user.username} ({self.challenge_type}: {self.score})"
        )

    def calculate_score(self):
        self.score = sum(1 for v in self.bug_results.values() if v)
        return self.score


class Submission(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='submissions')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    uploaded_file = models.FileField(upload_to='submissions/%Y/%m/%d/')
    submitted_at = models.DateTimeField(auto_now=True)
    score = models.IntegerField(default=0)
    is_graded = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True, default='')

    class Meta:
        unique_together = ('participant', 'challenge')
        ordering = ['-submitted_at']
        db_table = 'r2_submission'

    def __str__(self):
        return f"{self.participant.user.username} - {self.challenge.title} (Score: {self.score})"
