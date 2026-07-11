"""Forms for the equipment app."""

from django import forms

from accounts.forms import BootstrapMixin

from .models import Equipment, EquipmentCategory, RepairHistory


class EquipmentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Equipment
        fields = [
            "name",
            "category",
            "photo",
            "quantity",
            "purchase_date",
            "cost",
            "status",
            "last_maintenance",
            "next_maintenance",
            "notes",
        ]
        widgets = {
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "last_maintenance": forms.DateInput(attrs={"type": "date"}),
            "next_maintenance": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class EquipmentCategoryForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = EquipmentCategory
        fields = ["name", "description"]


class RepairHistoryForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = RepairHistory
        fields = ["equipment", "date", "description", "cost", "technician"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 2}),
        }
