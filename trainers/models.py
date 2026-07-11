"""Trainer models: profile, schedule and attendance."""

from django.conf import settings
from django.db import models
from django.urls import reverse


class Trainer(models.Model):
    """A gym trainer / coach."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        INACTIVE = "inactive", "Inactive"
        ON_LEAVE = "on_leave", "On Leave"

    # Optionally link to a login account (role=trainer).
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trainer_profile",
    )
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    photo = models.ImageField(upload_to="trainers/", blank=True, null=True)
    specialization = models.CharField(
        max_length=120,
        blank=True,
        help_text="e.g. Yoga, Strength Training, Cardio",
    )
    bio = models.TextField(blank=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hire_date = models.DateField(null=True, blank=True)
    schedule = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g. Mon-Fri 6am-2pm",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self) -> str:
        return self.full_name

    def get_absolute_url(self):
        return reverse("trainers:detail", args=[self.pk])

    @property
    def assigned_members_count(self) -> int:
        return self.members.count()


class TrainerAttendance(models.Model):
    """Daily attendance record for a trainer."""

    trainer = models.ForeignKey(
        Trainer, on_delete=models.CASCADE, related_name="attendances"
    )
    date = models.DateField()
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    present = models.BooleanField(default=True)
    note = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-date"]
        unique_together = ("trainer", "date")

    def __str__(self) -> str:
        return f"{self.trainer} - {self.date}"
