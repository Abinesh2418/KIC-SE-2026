from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Event, Challenge, Participant, Submission


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'duration_minutes', 'started_at')


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'challenge_type', 'total_bugs', 'order', 'event')
    list_filter = ('challenge_type',)


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'score', 'has_submitted', 'tab_switch_count')
    list_filter = ('status', 'has_submitted')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('participant', 'challenge', 'submitted_at', 'score', 'is_graded')
    list_filter = ('is_graded', 'challenge__challenge_type')
