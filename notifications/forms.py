"""Forms for the notifications app."""

from django import forms

from accounts.forms import BootstrapMixin

from .models import Notification


class NotificationForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Notification
        fields = ["recipient", "notification_type", "title", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "recipient": "Leave blank to broadcast to everyone.",
        }
