from django.urls import path

from . import views

app_name = "equipment"

urlpatterns = [
    path("", views.equipment_list, name="list"),
    path("add/", views.equipment_create, name="create"),
    path("categories/", views.category_manage, name="categories"),
    path("<int:pk>/", views.equipment_detail, name="detail"),
    path("<int:pk>/edit/", views.equipment_edit, name="edit"),
    path("<int:pk>/delete/", views.equipment_delete, name="delete"),
    path("<int:pk>/repair/", views.repair_add, name="repair_add"),
]
