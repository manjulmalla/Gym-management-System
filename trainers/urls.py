from django.urls import path

from . import views

app_name = "trainers"

urlpatterns = [
    path("", views.trainer_list, name="list"),
    path("add/", views.trainer_create, name="create"),
    path("attendance/", views.trainer_attendance, name="attendance"),
    path("<int:pk>/", views.trainer_detail, name="detail"),
    path("<int:pk>/edit/", views.trainer_edit, name="edit"),
    path("<int:pk>/delete/", views.trainer_delete, name="delete"),
]
