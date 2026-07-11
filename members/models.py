"""Member profile model with medical, emergency and BMI information."""

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Member(models.Model):
    """A gym member."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        SUSPENDED = "suspended", "Suspended"

    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    # Optional link to a login account (role=member).
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="member_profile",
    )
    membership_id = models.CharField(
        max_length=20, unique=True, blank=True, help_text="Auto-generated if blank."
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to="members/", blank=True, null=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)

    # Assigned trainer
    trainer = models.ForeignKey(
        "trainers.Trainer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
    )

    # Health / BMI
    height_cm = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True, help_text="Height in cm"
    )
    weight_kg = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True, help_text="Weight in kg"
    )
    medical_info = models.TextField(
        blank=True, help_text="Allergies, conditions, injuries, etc."
    )

    # Emergency contact
    emergency_contact_name = models.CharField(max_length=120, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    join_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self) -> str:
        return self.full_name

    def get_absolute_url(self):
        return reverse("members:detail", args=[self.pk])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Generate a stable, human-friendly membership id after first save.
        if not self.membership_id:
            self.membership_id = f"GYM{self.pk:05d}"
            super().save(update_fields=["membership_id"])

    # -- Derived data -------------------------------------------------------
    @property
    def age(self):
        if not self.date_of_birth:
            return None
        today = timezone.localdate()
        return (
            today.year
            - self.date_of_birth.year
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )

    @property
    def bmi(self):
        """Body Mass Index, rounded to one decimal."""
        if not self.height_cm or not self.weight_kg or self.height_cm == 0:
            return None
        height_m = float(self.height_cm) / 100
        return round(float(self.weight_kg) / (height_m * height_m), 1)

    @property
    def bmi_category(self):
        bmi = self.bmi
        if bmi is None:
            return "N/A"
        if bmi < 18.5:
            return "Underweight"
        if bmi < 25:
            return "Normal"
        if bmi < 30:
            return "Overweight"
        return "Obese"

    @property
    def active_membership(self):
        """Return the most recent active membership, if any."""
        return (
            self.memberships.filter(status="active")
            .order_by("-start_date")
            .first()
        )
