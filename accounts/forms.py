"""Forms for authentication, registration and profile management."""

from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm,
    UserCreationForm,
)

from .models import Role, User

# Common Bootstrap widget attributes.
TEXT_INPUT = {"class": "form-control"}
SELECT_INPUT = {"class": "form-select"}


class BootstrapMixin:
    """Apply Bootstrap classes to every field automatically."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", "form-select")
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.ClearableFileInput):
                widget.attrs.setdefault("class", "form-control")
            else:
                widget.attrs.setdefault("class", "form-control")


class LoginForm(BootstrapMixin, AuthenticationForm):
    """Styled login form."""

    username = forms.CharField(
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": "Username"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )


class RegisterForm(BootstrapMixin, UserCreationForm):
    """Public self registration form (creates a Member account)."""

    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "phone"]

    def save(self, commit=True):
        user = super().save(commit=False)
        # Self registered accounts are always plain members.
        user.role = Role.MEMBER
        if commit:
            user.save()
        return user


class ProfileForm(BootstrapMixin, forms.ModelForm):
    """Allow users to update their own profile details."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "gender",
            "date_of_birth",
            "address",
            "avatar",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 2}),
        }


class StyledPasswordChangeForm(BootstrapMixin, PasswordChangeForm):
    """Bootstrap styled change password form."""


class StaffUserForm(BootstrapMixin, forms.ModelForm):
    """Admin form to create/manage staff users with any role."""

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Leave blank to keep unchanged"}),
        required=False,
        help_text="Set a password for new users. Leave blank when editing to keep it.",
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "is_active",
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        # Grant Django admin access to privileged roles.
        user.is_staff = user.role in {Role.SUPER_ADMIN, Role.MANAGER}
        user.is_superuser = user.role == Role.SUPER_ADMIN
        if commit:
            user.save()
        return user
