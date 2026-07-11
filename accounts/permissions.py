"""
Reusable access-control helpers.

These decorators / mixins let every app enforce role based permissions in
a consistent, declarative way.
"""

from functools import wraps

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect

from .models import Role

# Roles that can manage core gym operations.
STAFF_ROLES = {Role.SUPER_ADMIN, Role.MANAGER, Role.RECEPTIONIST}
# Roles with full administrative control.
ADMIN_ROLES = {Role.SUPER_ADMIN, Role.MANAGER}


def role_required(*roles):
    """Decorator restricting a view to the given roles.

    Super admins (and Django superusers) always pass.
    """

    allowed = set(roles)

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                return redirect("accounts:login")
            if user.is_superuser or user.role == Role.SUPER_ADMIN or user.role in allowed:
                return view_func(request, *args, **kwargs)
            messages.error(request, "You do not have permission to access that page.")
            raise PermissionDenied
        return _wrapped

    return decorator


class RoleRequiredMixin(LoginRequiredMixin):
    """Class based view mixin mirroring :func:`role_required`."""

    allowed_roles: set = set()

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect("accounts:login")
        if (
            user.is_superuser
            or user.role == Role.SUPER_ADMIN
            or user.role in self.allowed_roles
        ):
            return super().dispatch(request, *args, **kwargs)
        messages.error(request, "You do not have permission to access that page.")
        raise PermissionDenied
