from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """User model for KIC AIML 2026 Assessment."""

    ROLE_STUDENT = 'student'
    ROLE_ADMIN = 'admin'
    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_ADMIN, 'Admin'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    is_approved = models.BooleanField(default=False)
    roll_no = models.CharField(max_length=20, unique=True, blank=True, default='')
    domain = models.CharField(max_length=50, default='AIML')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['roll_no']
        db_table = 'shared_auth_user'

    @property
    def is_admin_user(self):
        return self.role == self.ROLE_ADMIN or self.is_superuser

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT
