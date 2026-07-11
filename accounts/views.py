"""Authentication, profile and user-management views."""

from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import (
    LoginForm,
    ProfileForm,
    RegisterForm,
    StaffUserForm,
    StyledPasswordChangeForm,
)
from .models import User
from .permissions import ADMIN_ROLES, role_required


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------
class LoginView(auth_views.LoginView):
    """Branded login page."""

    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    """Log the user out and return to the login page."""


def register(request):
    """Public self-registration for new members."""
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to GymPro! Your account has been created.")
            return redirect("dashboard:home")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


# ---------------------------------------------------------------------------
# Profile & password
# ---------------------------------------------------------------------------
@login_required
def profile(request):
    """View and edit your own profile."""
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "accounts/profile.html", {"form": form})


@login_required
def change_password(request):
    """Let a logged-in user change their password."""
    if request.method == "POST":
        form = StyledPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Keep the user logged in after the password change.
            update_session_auth_hash(request, user)
            messages.success(request, "Your password has been changed successfully.")
            return redirect("accounts:profile")
    else:
        form = StyledPasswordChangeForm(request.user)
    return render(request, "accounts/change_password.html", {"form": form})


# ---------------------------------------------------------------------------
# Password reset (forgot password) flow
# ---------------------------------------------------------------------------
class PasswordResetView(auth_views.PasswordResetView):
    template_name = "accounts/password_reset.html"
    email_template_name = "accounts/password_reset_email.html"
    success_url = reverse_lazy("accounts:password_reset_done")


class PasswordResetDoneView(auth_views.PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class PasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("accounts:password_reset_complete")


class PasswordResetCompleteView(auth_views.PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"


# ---------------------------------------------------------------------------
# User management (admin / manager only)
# ---------------------------------------------------------------------------
@login_required
@role_required(*ADMIN_ROLES)
def user_list(request):
    """List all system users."""
    query = request.GET.get("q", "").strip()
    role = request.GET.get("role", "").strip()
    users = User.objects.all()
    if query:
        users = users.filter(username__icontains=query) | users.filter(
            first_name__icontains=query
        ) | users.filter(last_name__icontains=query)
    if role:
        users = users.filter(role=role)
    context = {"users": users.distinct(), "query": query, "role": role}
    return render(request, "accounts/user_list.html", context)


@login_required
@role_required(*ADMIN_ROLES)
def user_create(request):
    """Create a new staff/member user account."""
    if request.method == "POST":
        form = StaffUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User account created successfully.")
            return redirect("accounts:user_list")
    else:
        form = StaffUserForm()
    return render(request, "accounts/user_form.html", {"form": form, "title": "Add User"})


@login_required
@role_required(*ADMIN_ROLES)
def user_edit(request, pk):
    """Edit an existing user account."""
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        form = StaffUserForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "User account updated successfully.")
            return redirect("accounts:user_list")
    else:
        form = StaffUserForm(instance=user_obj)
    return render(
        request, "accounts/user_form.html", {"form": form, "title": "Edit User"}
    )


@login_required
@role_required(*ADMIN_ROLES)
def user_delete(request, pk):
    """Delete a user account."""
    user_obj = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        if user_obj == request.user:
            messages.error(request, "You cannot delete your own account.")
        else:
            user_obj.delete()
            messages.success(request, "User account deleted.")
        return redirect("accounts:user_list")
    return render(request, "accounts/user_confirm_delete.html", {"object": user_obj})
