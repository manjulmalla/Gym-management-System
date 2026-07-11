"""Payment & invoice models."""

from django.db import models
from django.utils import timezone


class Payment(models.Model):
    """A payment made by a member (membership fees, etc.)."""

    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        UPI = "upi", "UPI"
        BANK = "bank", "Bank Transfer"
        ONLINE = "online", "Online"

    class Status(models.TextChoices):
        PAID = "paid", "Paid"
        PENDING = "pending", "Pending"
        REFUNDED = "refunded", "Refunded"

    member = models.ForeignKey(
        "members.Member", on_delete=models.CASCADE, related_name="payments"
    )
    membership = models.ForeignKey(
        "memberships.Membership",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(
        max_length=20, choices=Method.choices, default=Method.CASH
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PAID
    )
    date = models.DateField(default=timezone.localdate)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self) -> str:
        return f"{self.invoice_number} - {self.member}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.invoice_number:
            self.invoice_number = f"INV{self.pk:06d}"
            super().save(update_fields=["invoice_number"])
