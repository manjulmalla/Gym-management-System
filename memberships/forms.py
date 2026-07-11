"""Forms for the memberships app."""

from django import forms

from accounts.forms import BootstrapMixin

from .models import Membership, MembershipPlan


class MembershipPlanForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = [
            "name",
            "plan_type",
            "duration_days",
            "price",
            "description",
            "features",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "features": forms.Textarea(attrs={"rows": 4}),
        }


class MembershipForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Membership
        fields = ["member", "plan", "start_date", "end_date", "status"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(
                attrs={"type": "date"},
            ),
        }
        help_texts = {
            "end_date": "Leave blank to auto-calculate from the plan duration.",
        }
