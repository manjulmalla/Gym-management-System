from django.contrib import admin

from .models import Trainer, TrainerAttendance


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ("full_name", "specialization", "phone", "salary", "status")
    list_filter = ("status", "specialization")
    search_fields = ("full_name", "email", "phone", "specialization")


@admin.register(TrainerAttendance)
class TrainerAttendanceAdmin(admin.ModelAdmin):
    list_display = ("trainer", "date", "check_in", "check_out", "present")
    list_filter = ("present", "date")
    search_fields = ("trainer__full_name",)
