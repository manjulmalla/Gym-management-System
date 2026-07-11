"""Trainer management views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import ADMIN_ROLES, STAFF_ROLES, role_required

from .forms import TrainerAttendanceForm, TrainerForm
from .models import Trainer, TrainerAttendance


@login_required
@role_required(*STAFF_ROLES)
def trainer_list(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    trainers = Trainer.objects.all()
    if query:
        trainers = trainers.filter(
            Q(full_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
            | Q(specialization__icontains=query)
        )
    if status:
        trainers = trainers.filter(status=status)

    paginator = Paginator(trainers, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "page_obj": page_obj,
        "query": query,
        "status": status,
        "status_choices": Trainer.Status.choices,
    }
    return render(request, "trainers/trainer_list.html", context)


@login_required
@role_required(*STAFF_ROLES)
def trainer_detail(request, pk):
    trainer = get_object_or_404(Trainer, pk=pk)
    context = {
        "trainer": trainer,
        "members": trainer.members.all(),
        "classes": trainer.classes.all(),
        "attendances": trainer.attendances.all()[:15],
    }
    return render(request, "trainers/trainer_detail.html", context)


@login_required
@role_required(*ADMIN_ROLES)
def trainer_create(request):
    if request.method == "POST":
        form = TrainerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Trainer added successfully.")
            return redirect("trainers:list")
    else:
        form = TrainerForm()
    return render(
        request, "trainers/trainer_form.html", {"form": form, "title": "Add Trainer"}
    )


@login_required
@role_required(*ADMIN_ROLES)
def trainer_edit(request, pk):
    trainer = get_object_or_404(Trainer, pk=pk)
    if request.method == "POST":
        form = TrainerForm(request.POST, request.FILES, instance=trainer)
        if form.is_valid():
            form.save()
            messages.success(request, "Trainer updated successfully.")
            return redirect("trainers:detail", pk=trainer.pk)
    else:
        form = TrainerForm(instance=trainer)
    return render(
        request, "trainers/trainer_form.html", {"form": form, "title": "Edit Trainer"}
    )


@login_required
@role_required(*ADMIN_ROLES)
def trainer_delete(request, pk):
    trainer = get_object_or_404(Trainer, pk=pk)
    if request.method == "POST":
        trainer.delete()
        messages.success(request, "Trainer deleted.")
        return redirect("trainers:list")
    return render(request, "trainers/trainer_confirm_delete.html", {"object": trainer})


@login_required
@role_required(*STAFF_ROLES)
def trainer_attendance(request):
    """Record and list trainer attendance."""
    if request.method == "POST":
        form = TrainerAttendanceForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Trainer attendance recorded.")
            except Exception:
                messages.error(request, "Attendance already recorded for that day.")
            return redirect("trainers:attendance")
    else:
        form = TrainerAttendanceForm()

    records = TrainerAttendance.objects.select_related("trainer")
    paginator = Paginator(records, 15)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "trainers/trainer_attendance.html",
        {"form": form, "page_obj": page_obj},
    )
