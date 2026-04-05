from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Shared user model across all ML Fest rounds.
    Rounds 1 & 2 use the basic auth fields (username, email, password).
    Round 3 additionally uses role, is_approved, total_points, last_flag_at.
    """
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
        db_table = 'shared_auth_user'

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
        """Recalculate total points from all approved scores (Round 3 CTF only)."""
        try:
            from ctf.models import Score
        except ImportError:
            return
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
