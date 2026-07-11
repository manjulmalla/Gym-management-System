from django.urls import path

from . import views

app_name = "classes"

urlpatterns = [
    path("", views.class_list, name="list"),
    path("add/", views.class_create, name="create"),
    path("<int:pk>/", views.class_detail, name="detail"),
    path("<int:pk>/edit/", views.class_edit, name="edit"),
    path("<int:pk>/delete/", views.class_delete, name="delete"),
    path("<int:pk>/enroll/", views.class_enroll, name="enroll"),
]
