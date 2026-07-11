from django.urls import path

from . import views

app_name = "attendance"

urlpatterns = [
    path("", views.attendance_list, name="list"),
    path("check-in/", views.check_in, name="check_in"),
    path("check-out/<int:pk>/", views.check_out, name="check_out"),
    path("report/", views.monthly_report, name="monthly_report"),
]
