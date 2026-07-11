from django.contrib import admin

from .models import ClassEnrollment, WorkoutClass


class ClassEnrollmentInline(admin.TabularInline):
    model = ClassEnrollment
    extra = 0


@admin.register(WorkoutClass)
class WorkoutClassAdmin(admin.ModelAdmin):
    list_display = ("name", "class_type", "trainer", "day", "start_time", "capacity")
    list_filter = ("class_type", "day", "is_active")
    search_fields = ("name",)
    inlines = [ClassEnrollmentInline]


@admin.register(ClassEnrollment)
class ClassEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("member", "workout_class", "enrolled_at")
    search_fields = ("member__full_name", "workout_class__name")
