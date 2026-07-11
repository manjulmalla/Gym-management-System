"""Admin configuration for the custom user model."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Extend Django's UserAdmin with our custom fields."""

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
    )
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    search_fields = ("username", "first_name", "last_name", "email", "phone")

    fieldsets = BaseUserAdmin.fieldsets + (
        (
            "GymPro Profile",
            {
                "fields": (
                    "role",
                    "phone",
                    "gender",
                    "date_of_birth",
                    "address",
                    "avatar",
                )
            },
        ),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("GymPro Profile", {"fields": ("role", "email", "first_name", "last_name")}),
    )
