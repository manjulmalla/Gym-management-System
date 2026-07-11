"""
Root URL configuration for GymPro.

Each feature lives in its own reusable app and is mounted under a
descriptive prefix. Media files are served during development.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentication & profile
    path("accounts/", include("accounts.urls")),
    # Feature apps
    path("", include("dashboard.urls")),
    path("members/", include("members.urls")),
    path("trainers/", include("trainers.urls")),
    path("memberships/", include("memberships.urls")),
    path("attendance/", include("attendance.urls")),
    path("payments/", include("payments.urls")),
    path("equipment/", include("equipment.urls")),
    path("classes/", include("classes.urls")),
    path("reports/", include("reports.urls")),
    path("notifications/", include("notifications.urls")),
]

# Serve uploaded media (and static during dev) files.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / "static")

# Customise the Django admin branding.
admin.site.site_header = "GymPro Administration"
admin.site.site_title = "GymPro Admin"
admin.site.index_title = "Welcome to GymPro Admin Panel"
