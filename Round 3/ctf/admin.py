from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    CustomUser, SiteSettings, Challenge, Flag, ChallengeResource,
    Submission, Score, EvaluatorAssignment,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_approved', 'is_staff', 'is_active')
    list_filter = ('role', 'is_approved', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_editable = ('is_approved', 'role')
    ordering = ('-date_joined',)

    fieldsets = UserAdmin.fieldsets + (
        ('ML Fest Fields', {
            'fields': ('role', 'is_approved', 'total_points', 'last_flag_at'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('ML Fest Fields', {
            'fields': ('role', 'is_approved'),
        }),
    )


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('event_active', 'leaderboard_public', 'challenges_revealed')

    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()


class FlagInline(admin.TabularInline):
    model = Flag
    extra = 0


class ChallengeResourceInline(admin.TabularInline):
    model = ChallengeResource
    extra = 0


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'category', 'difficulty', 'total_points', 'is_revealed')
    list_filter = ('difficulty', 'is_revealed')
    list_editable = ('is_revealed',)
    inlines = [FlagInline, ChallengeResourceInline]
    ordering = ('order',)


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'flag_order', 'points_value', 'flag_content')
    list_filter = ('challenge',)


@admin.register(ChallengeResource)
class ChallengeResourceAdmin(admin.ModelAdmin):
    list_display = ('challenge', 'display_name', 'local_name')
    list_filter = ('challenge',)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'flag', 'is_correct', 'submitted_at')
    list_filter = ('is_correct', 'challenge')
    search_fields = ('user__username',)
    ordering = ('-submitted_at',)


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'challenge', 'flag', 'flag_points', 'explanation_points', 'is_approved', 'approved_by', 'approved_at')
    list_filter = ('is_approved', 'challenge')
    search_fields = ('user__username',)
    ordering = ('-submitted_at',)


@admin.register(EvaluatorAssignment)
class EvaluatorAssignmentAdmin(admin.ModelAdmin):
    list_display = ('evaluator', 'participant', 'assigned_at')
    search_fields = ('evaluator__username', 'participant__username')
