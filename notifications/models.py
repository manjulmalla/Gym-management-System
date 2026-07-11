"""Notifications & announcements."""

from django.conf import settings
from django.db import models


class Notification(models.Model):
    """A notification, optionally targeted at a specific user.

    When ``recipient`` is null the notification is treated as a global
    announcement visible to everyone.
    """

    class Type(models.TextChoices):
        EXPIRY = "expiry", "Membership Expiry"
        PAYMENT = "payment", "Payment Reminder"
        BIRTHDAY = "birthday", "Birthday Wish"
        CLASS = "class", "Class Reminder"
        ANNOUNCEMENT = "announcement", "Admin Announcement"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="Leave blank for a global announcement.",
    )
    notification_type = models.CharField(
        max_length=20, choices=Type.choices, default=Type.ANNOUNCEMENT
    )
    title = models.CharField(max_length=150)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
