"""Template context processor exposing notifications globally."""

from django.db.models import Q

from .models import Notification


def notifications(request):
    """Expose unread notification count and latest items to all templates."""
    if not request.user.is_authenticated:
        return {"unread_notifications": 0, "recent_notifications": []}

    qs = Notification.objects.filter(
        Q(recipient=request.user) | Q(recipient__isnull=True)
    )
    return {
        "unread_notifications": qs.filter(is_read=False).count(),
        "recent_notifications": qs[:5],
    }
