"""Forms for the trainers app."""

from django import forms

from accounts.forms import BootstrapMixin

from .models import Trainer, TrainerAttendance


class TrainerForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Trainer
        fields = [
            "full_name",
            "email",
            "phone",
            "photo",
            "specialization",
            "bio",
            "salary",
            "hire_date",
            "schedule",
            "status",
            "user",
        ]
        widgets = {
            "hire_date": forms.DateInput(attrs={"type": "date"}),
            "bio": forms.Textarea(attrs={"rows": 3}),
        }


class TrainerAttendanceForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = TrainerAttendance
        fields = ["trainer", "date", "check_in", "check_out", "present", "note"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "check_in": forms.TimeInput(attrs={"type": "time"}),
            "check_out": forms.TimeInput(attrs={"type": "time"}),
        }
