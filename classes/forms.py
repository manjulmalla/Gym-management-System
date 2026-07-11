"""Forms for the classes app."""

from django import forms

from accounts.forms import BootstrapMixin

from .models import ClassEnrollment, WorkoutClass


class WorkoutClassForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = WorkoutClass
        fields = [
            "name",
            "class_type",
            "trainer",
            "day",
            "start_time",
            "end_time",
            "capacity",
            "description",
            "is_active",
        ]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class ClassEnrollmentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = ClassEnrollment
        fields = ["member"]
