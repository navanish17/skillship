"""
File:    backend/apps/accounts/admin.py
Purpose: Register the custom User model in Django admin.
Owner:   Prashant

MAIN_ADMIN uses this during early development to inspect / repair user rows.
The Skillship-specific fields (role, school, phone, admission_number) are
added to the standard Django change + add forms.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("username", "email", "role", "school", "is_active")
    list_filter = ("role", "school", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Skillship", {"fields": ("role", "school", "phone", "admission_number")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Skillship", {"fields": ("email", "role", "school")}),
    )
