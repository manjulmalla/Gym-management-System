"""Member attendance (check-in / check-out) tracking."""

from django.db import models
from django.utils import timezone


class Attendance(models.Model):
    """A single check-in/out record for a member on a given day."""

    member = models.ForeignKey(
        "members.Member", on_delete=models.CASCADE, related_name="attendances"
    )
    date = models.DateField(default=timezone.localdate)
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-date", "-check_in"]
        unique_together = ("member", "date")

    def __str__(self) -> str:
        return f"{self.member} - {self.date}"

    @property
    def duration(self):
        """Time spent in the gym, if both timestamps exist."""
        if self.check_in and self.check_out:
            return self.check_out - self.check_in
        return None
