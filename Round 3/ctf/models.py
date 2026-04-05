import hashlib

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    """Round 3 user model — separate auth table for CTF round."""
    ROLE_PARTICIPANT = 'participant'
    ROLE_EVALUATOR = 'evaluator'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_PARTICIPANT, 'Participant'),
        (ROLE_EVALUATOR, 'Evaluator'),
        (ROLE_ADMIN, 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PARTICIPANT)
    is_approved = models.BooleanField(default=False)
    total_points = models.IntegerField(default=0)
    last_flag_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-total_points', 'last_flag_at']
        db_table = 'r3_user'

    @property
    def is_admin_user(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_evaluator_user(self):
        return self.role == self.ROLE_EVALUATOR or self.is_admin_user

    @property
    def is_participant(self):
        return self.role == self.ROLE_PARTICIPANT

    def recalculate_points(self):
        """Recalculate total points from all approved scores."""
        total = Score.objects.filter(
            user=self, is_approved=True
        ).aggregate(
            total=models.Sum(models.F('flag_points') + models.F('explanation_points'))
        )['total'] or 0
        self.total_points = total
        latest = Score.objects.filter(
            user=self, is_approved=True
        ).order_by('-submitted_at').first()
        if latest:
            self.last_flag_at = latest.submitted_at
        self.save(update_fields=['total_points', 'last_flag_at'])

    def __str__(self):
        return self.username


class SiteSettings(models.Model):
    """Singleton settings for the competition."""
    event_active = models.BooleanField(default=False)
    leaderboard_public = models.BooleanField(default=False)
    challenges_revealed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
        db_table = 'r3_sitesettings'

    def __str__(self):
        return "Site Settings"

    @classmethod
    def get(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Challenge(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
        ('Expert', 'Expert'),
    ]

    order = models.IntegerField(unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, blank=True)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Medium')
    total_points = models.IntegerField(default=0)
    flag_points_max = models.IntegerField(default=1, help_text="Maximum points for the flag itself")
    explanation_points_max = models.IntegerField(default=1, help_text="Maximum points for the explanation")
    is_revealed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        db_table = 'r3_challenge'

    def __str__(self):
        return self.title

    @property
    def flags_count(self):
        return self.flags.count()


class Flag(models.Model):
    """A flag associated with a challenge."""
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='flags')
    flag_content = models.CharField(max_length=500)
    flag_order = models.IntegerField(default=1)
    points_value = models.IntegerField(default=1)
    description = models.CharField(max_length=500, blank=True, help_text="Hint or description for this flag")

    class Meta:
        ordering = ['flag_order']
        unique_together = [('challenge', 'flag_order')]
        db_table = 'r3_flag'

    def __str__(self):
        return f"{self.challenge.title} - Flag {self.flag_order}"


class ChallengeResource(models.Model):
    """Files associated with a challenge (notebooks, datasets)."""
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='resources')
    display_name = models.CharField(max_length=200)
    local_name = models.CharField(max_length=200)

    class Meta:
        db_table = 'r3_challengeresource'

    def __str__(self):
        return f"{self.challenge.title} - {self.display_name}"


class Submission(models.Model):
    """A flag submission attempt."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='r3_submissions')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='submissions')
    flag = models.ForeignKey(Flag, on_delete=models.CASCADE, related_name='submissions')
    submitted_value = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        db_table = 'r3_submission'

    def __str__(self):
        return f"{self.user.username} -> {self.challenge.title} Flag {self.flag.flag_order}"


class Score(models.Model):
    """Approved score entry. Created when a correct flag is submitted; pending until evaluator approves."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='r3_scores')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='scores')
    flag = models.ForeignKey(Flag, on_delete=models.CASCADE, related_name='scores')
    flag_points = models.IntegerField(default=0)
    explanation_points = models.IntegerField(default=0)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='r3_approved_scores')
    approved_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'flag')]
        ordering = ['-submitted_at']
        db_table = 'r3_score'

    def __str__(self):
        status = "Approved" if self.is_approved else "Pending"
        return f"{self.user.username} - {self.challenge.title} Flag {self.flag.flag_order} [{status}]"

    @property
    def total_score(self):
        return self.flag_points + self.explanation_points


class EvaluatorAssignment(models.Model):
    """Maps evaluators to participants."""
    evaluator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='r3_evaluator_assignments')
    participant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='r3_participant_assignments')
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('participant',)]
        db_table = 'r3_evaluatorassignment'

    def __str__(self):
        return f"{self.evaluator.username} -> {self.participant.username}"


class UserFlag(models.Model):
    """Per-user unique flags. Five flags (one per challenge) are generated
    when a participant registers, so every user has a different flag string."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_flags')
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='user_flags')
    flag_value = models.CharField(max_length=500, help_text='Unique flag for this user+challenge')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'challenge')]
        ordering = ['challenge__order']
        db_table = 'r3_userflag'

    def __str__(self):
        return f"{self.user.username} — {self.challenge.title}: {self.flag_value}"

    @staticmethod
    def generate_flag(user_id, challenge_order, secret=None):
        """Derive a deterministic, unique flag string using SHA-256.
        Format: MLFEST{<prefix>_<8-char hex>}
        """
        if secret is None:
            secret = settings.SECRET_KEY
        raw = f"{secret}:{user_id}:{challenge_order}".encode()
        digest = hashlib.sha256(raw).hexdigest()[:8]
        # Short mnemonic prefix per challenge for readability
        PREFIXES = {
            1: 'p01s0n',
            2: 'sh4d0w',
            3: 'r3p41r',
            4: 's3nt1n3l',
            5: 'w31ght',
        }
        prefix = PREFIXES.get(challenge_order, f'ch{challenge_order}')
        return f"MLFEST{{{prefix}_{digest}}}"

    @classmethod
    def generate_flags_for_user(cls, user):
        """Create 5 unique UserFlag rows (one per challenge) for *user*.
        Skips any that already exist."""
        from .models import Challenge  # prevent circular import edge-case
        challenges = Challenge.objects.all().order_by('order')
        created = []
        for ch in challenges:
            flag_value = cls.generate_flag(user.id, ch.order)
            obj, was_created = cls.objects.get_or_create(
                user=user,
                challenge=ch,
                defaults={'flag_value': flag_value},
            )
            if was_created:
                created.append(obj)
        return created
