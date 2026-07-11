"""
Custom user model for GymPro.

Adds role based access control on top of Django's ``AbstractUser`` so we
can distinguish between super admins, gym managers, trainers,
receptionists and members throughout the application.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    """The available user roles in the system."""

    SUPER_ADMIN = "super_admin", "Super Admin"
    MANAGER = "manager", "Gym Manager"
    TRAINER = "trainer", "Trainer"
    RECEPTIONIST = "receptionist", "Receptionist"
    MEMBER = "member", "Member"


class Gender(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"
    OTHER = "other", "Other"


class User(AbstractUser):
    """Application user with an explicit role and profile information."""

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
        help_text="Determines what the user is allowed to access.",
    )
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    class Meta:
        ordering = ["first_name", "last_name", "username"]

    def __str__(self) -> str:
        return self.get_full_name() or self.username

    # -- Convenience helpers ------------------------------------------------
    @property
    def display_name(self) -> str:
        """A friendly name for templates."""
        return self.get_full_name() or self.username

    @property
    def role_label(self) -> str:
        return self.get_role_display()

    @property
    def is_super_admin(self) -> bool:
        return self.role == Role.SUPER_ADMIN or self.is_superuser

    @property
    def is_manager(self) -> bool:
        return self.role == Role.MANAGER

    @property
    def is_trainer(self) -> bool:
        return self.role == Role.TRAINER

    @property
    def is_receptionist(self) -> bool:
        return self.role == Role.RECEPTIONIST

    @property
    def is_member(self) -> bool:
        return self.role == Role.MEMBER

    @property
    def is_staff_role(self) -> bool:
        """True for any privileged (non plain member) role."""
        return self.role in {
            Role.SUPER_ADMIN,
            Role.MANAGER,
            Role.TRAINER,
            Role.RECEPTIONIST,
        }
