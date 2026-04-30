from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'roll_no', 'email', 'role', 'is_approved', 'is_active')
    list_filter = ('role', 'is_approved', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'roll_no')
    list_editable = ('is_approved', 'role')
    ordering = ('roll_no',)

    fieldsets = UserAdmin.fieldsets + (
        ('KIC AIML Fields', {
            'fields': ('roll_no', 'domain', 'role', 'is_approved'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('KIC AIML Fields', {
            'fields': ('roll_no', 'domain', 'role', 'is_approved'),
        }),
    )
