from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_approved', 'is_staff', 'is_active')
    list_filter = ('role', 'is_approved', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_editable = ('is_approved', 'role')
    ordering = ('-date_joined',)

    # Add custom fields to the admin forms
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
