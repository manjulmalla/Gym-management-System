"""Forms for the members app."""

from django import forms

from accounts.forms import BootstrapMixin

from .models import Member


class MemberForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            "full_name",
            "email",
            "phone",
            "photo",
            "gender",
            "date_of_birth",
            "address",
            "trainer",
            "height_cm",
            "weight_kg",
            "medical_info",
            "emergency_contact_name",
            "emergency_contact_phone",
            "status",
            "join_date",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "join_date": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 2}),
            "medical_info": forms.Textarea(attrs={"rows": 3}),
        }
