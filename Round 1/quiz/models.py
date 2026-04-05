from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone


class CustomUser(AbstractUser):
    """Round 1 user model — separate auth table for this round."""

    class Meta:
        db_table = 'r1_user'

    def __str__(self):
        return self.username


class Event(models.Model):
    name = models.CharField(max_length=200, default="ML Fest MCQ Round")
    is_active = models.BooleanField(default=False)
    duration_minutes = models.PositiveIntegerField(default=30)
    max_tab_switches = models.PositiveIntegerField(default=3)
    started_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    leaderboard_public = models.BooleanField(default=True)
    show_score_to_participant = models.BooleanField(default=True)

    class Meta:
        db_table = 'r1_event'

    def __str__(self):
        return self.name

    @property
    def is_running(self):
        """Event is running when admin has activated it."""
        return self.is_active


class Question(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='questions')
    question_no = models.PositiveIntegerField()
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=[
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    ])

    class Meta:
        ordering = ['question_no']
        db_table = 'r1_question'

    def __str__(self):
        return f"Q{self.question_no}: {self.question_text[:50]}"


class Participant(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('disqualified', 'Disqualified'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='r1_participant')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, default='')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    tab_switch_count = models.PositiveIntegerField(default=0)
    tab_switch_violated = models.BooleanField(default=False)
    score = models.IntegerField(default=0)
    time_taken_ms = models.BigIntegerField(default=0)
    has_submitted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-score', 'time_taken_ms']
        db_table = 'r1_participant'

    def __str__(self):
        return f"{self.user.username} - {self.get_status_display()}"

    @property
    def time_remaining_seconds(self):
        """Per-participant timer: duration starts from when they began the quiz."""
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
        correct = 0
        answers = self.answers.select_related('question')
        for ans in answers:
            if ans.selected_option == ans.question.correct_answer:
                correct += 1
        self.score = correct
        if self.started_at and self.finished_at:
            delta = self.finished_at - self.started_at
            self.time_taken_ms = int(delta.total_seconds() * 1000)
        self.save()
        return correct


class Answer(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.CharField(max_length=1, choices=[
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    ], blank=True, null=True)

    class Meta:
        unique_together = ('participant', 'question')
        db_table = 'r1_answer'

    def __str__(self):
        return f"{self.participant.user.username} - Q{self.question.question_no}: {self.selected_option}"
