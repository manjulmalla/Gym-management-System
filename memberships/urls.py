from django.urls import path

from . import views

app_name = "memberships"

urlpatterns = [
    # Plans
    path("plans/", views.plan_list, name="plan_list"),
    path("plans/add/", views.plan_create, name="plan_create"),
    path("plans/<int:pk>/edit/", views.plan_edit, name="plan_edit"),
    path("plans/<int:pk>/delete/", views.plan_delete, name="plan_delete"),
    # Memberships
    path("", views.membership_list, name="membership_list"),
    path("add/", views.membership_create, name="membership_create"),
    path("<int:pk>/edit/", views.membership_edit, name="membership_edit"),
    path("<int:pk>/renew/", views.membership_renew, name="membership_renew"),
    path("<int:pk>/delete/", views.membership_delete, name="membership_delete"),
]
