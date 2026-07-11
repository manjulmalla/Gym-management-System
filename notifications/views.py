"""Notification views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import ADMIN_ROLES, role_required

from .forms import NotificationForm
from .models import Notification


@login_required
def notification_list(request):
    """Show notifications for the current user + global announcements."""
    qs = Notification.objects.filter(
        Q(recipient=request.user) | Q(recipient__isnull=True)
    )
    return render(request, "notifications/notification_list.html", {"notifications": qs})


@login_required
def mark_read(request, pk):
    notification = get_object_or_404(
        Notification.objects.filter(
            Q(recipient=request.user) | Q(recipient__isnull=True)
        ),
        pk=pk,
    )
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    return redirect("notifications:list")


@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(
        is_read=True
    )
    messages.success(request, "All notifications marked as read.")
    return redirect("notifications:list")


@login_required
@role_required(*ADMIN_ROLES)
def notification_create(request):
    """Create a targeted notification or a broadcast announcement."""
    if request.method == "POST":
        form = NotificationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Notification sent.")
            return redirect("notifications:list")
    else:
        form = NotificationForm()
    return render(
        request,
        "notifications/notification_form.html",
        {"form": form, "title": "Send Notification"},
    )
