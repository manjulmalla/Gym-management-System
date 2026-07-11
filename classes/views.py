"""Workout class scheduling and enrolment views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import ADMIN_ROLES, STAFF_ROLES, role_required

from .forms import ClassEnrollmentForm, WorkoutClassForm
from .models import WorkoutClass


@login_required
@role_required(*STAFF_ROLES)
def class_list(request):
    class_type = request.GET.get("type", "").strip()
    classes = WorkoutClass.objects.select_related("trainer")
    if class_type:
        classes = classes.filter(class_type=class_type)
    context = {
        "classes": classes,
        "type": class_type,
        "type_choices": WorkoutClass.ClassType.choices,
    }
    return render(request, "classes/class_list.html", context)


@login_required
@role_required(*STAFF_ROLES)
def class_detail(request, pk):
    workout_class = get_object_or_404(WorkoutClass, pk=pk)
    return render(
        request,
        "classes/class_detail.html",
        {
            "workout_class": workout_class,
            "enrollments": workout_class.enrollments.select_related("member"),
        },
    )


@login_required
@role_required(*ADMIN_ROLES)
def class_create(request):
    if request.method == "POST":
        form = WorkoutClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Class created.")
            return redirect("classes:list")
    else:
        form = WorkoutClassForm()
    return render(
        request, "classes/class_form.html", {"form": form, "title": "Add Class"}
    )


@login_required
@role_required(*ADMIN_ROLES)
def class_edit(request, pk):
    workout_class = get_object_or_404(WorkoutClass, pk=pk)
    if request.method == "POST":
        form = WorkoutClassForm(request.POST, instance=workout_class)
        if form.is_valid():
            form.save()
            messages.success(request, "Class updated.")
            return redirect("classes:detail", pk=workout_class.pk)
    else:
        form = WorkoutClassForm(instance=workout_class)
    return render(
        request, "classes/class_form.html", {"form": form, "title": "Edit Class"}
    )


@login_required
@role_required(*ADMIN_ROLES)
def class_delete(request, pk):
    workout_class = get_object_or_404(WorkoutClass, pk=pk)
    if request.method == "POST":
        workout_class.delete()
        messages.success(request, "Class deleted.")
        return redirect("classes:list")
    return render(
        request, "classes/class_confirm_delete.html", {"object": workout_class}
    )


@login_required
@role_required(*STAFF_ROLES)
def class_enroll(request, pk):
    """Enroll a member into a class (respecting capacity)."""
    workout_class = get_object_or_404(WorkoutClass, pk=pk)
    if request.method == "POST":
        if workout_class.is_full:
            messages.error(request, "This class is already full.")
            return redirect("classes:detail", pk=pk)
        form = ClassEnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save(commit=False)
            enrollment.workout_class = workout_class
            try:
                enrollment.save()
                messages.success(request, "Member enrolled successfully.")
            except Exception:
                messages.error(request, "Member is already enrolled in this class.")
            return redirect("classes:detail", pk=pk)
    else:
        form = ClassEnrollmentForm()
    return render(
        request,
        "classes/enroll_form.html",
        {"form": form, "workout_class": workout_class},
    )
