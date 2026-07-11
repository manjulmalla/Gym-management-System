from django.urls import path

from . import views

app_name = "reports"

urlpatterns = [
    path("", views.reports_home, name="home"),
    path("members.pdf", views.member_report, name="member_report"),
    path("attendance.pdf", views.attendance_report, name="attendance_report"),
    path("revenue.pdf", views.revenue_report, name="revenue_report"),
    path("trainers.pdf", views.trainer_report, name="trainer_report"),
    path("memberships.pdf", views.membership_report, name="membership_report"),
    path("equipment.pdf", views.equipment_report, name="equipment_report"),
]
