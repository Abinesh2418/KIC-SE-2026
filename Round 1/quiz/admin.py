from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Event, Question, Participant, Answer


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'duration_minutes', 'started_at')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_no', 'question_text', 'correct_answer')
    list_filter = ('event',)


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'score', 'has_submitted', 'tab_switch_count')
    list_filter = ('status', 'has_submitted')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('participant', 'question', 'selected_option')
