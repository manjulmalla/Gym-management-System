"""Membership plans and member subscriptions."""

from datetime import timedelta

from django.db import models
from django.utils import timezone


class MembershipPlan(models.Model):
    """A purchasable membership plan (daily, monthly, yearly, custom...)."""

    class PlanType(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"
        QUARTERLY = "quarterly", "Quarterly"
        YEARLY = "yearly", "Yearly"
        CUSTOM = "custom", "Custom"

    # Sensible default durations (in days) per plan type.
    DEFAULT_DURATIONS = {
        PlanType.DAILY: 1,
        PlanType.WEEKLY: 7,
        PlanType.MONTHLY: 30,
        PlanType.QUARTERLY: 90,
        PlanType.YEARLY: 365,
    }

    name = models.CharField(max_length=100)
    plan_type = models.CharField(
        max_length=20, choices=PlanType.choices, default=PlanType.MONTHLY
    )
    duration_days = models.PositiveIntegerField(
        help_text="Length of the plan in days."
    )
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    features = models.TextField(
        blank=True, help_text="One feature per line (shown as a bullet list)."
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price"]

    def __str__(self) -> str:
        return f"{self.name} (${self.price})"

    @property
    def feature_list(self) -> list[str]:
        return [line.strip() for line in self.features.splitlines() if line.strip()]


class Membership(models.Model):
    """A member's active/expired subscription to a plan."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        CANCELLED = "cancelled", "Cancelled"
        PENDING = "pending", "Pending"

    member = models.ForeignKey(
        "members.Member", on_delete=models.CASCADE, related_name="memberships"
    )
    plan = models.ForeignKey(
        MembershipPlan, on_delete=models.PROTECT, related_name="memberships"
    )
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self) -> str:
        return f"{self.member} - {self.plan.name}"

    def save(self, *args, **kwargs):
        # Auto-calculate the end date from the plan duration.
        if self.start_date and not self.end_date and self.plan_id:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    @property
    def is_expired(self) -> bool:
        return bool(self.end_date and self.end_date < timezone.localdate())

    @property
    def days_remaining(self) -> int:
        if not self.end_date:
            return 0
        return (self.end_date - timezone.localdate()).days

    def refresh_status(self):
        """Recompute the status based on the end date."""
        if self.status == self.Status.CANCELLED:
            return
        self.status = self.Status.EXPIRED if self.is_expired else self.Status.ACTIVE
