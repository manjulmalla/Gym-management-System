"""Forms for the payments app."""

from django import forms

from accounts.forms import BootstrapMixin

from .models import Payment


class PaymentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Payment
        fields = [
            "member",
            "membership",
            "amount",
            "method",
            "status",
            "date",
            "note",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }
