from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.landing, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("search/", views.global_search, name="search"),
    path("settings/", views.settings_view, name="settings"),
]
