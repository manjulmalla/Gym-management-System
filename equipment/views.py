"""Equipment management views."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import ADMIN_ROLES, STAFF_ROLES, role_required

from .forms import EquipmentCategoryForm, EquipmentForm, RepairHistoryForm
from .models import Equipment, EquipmentCategory


@login_required
@role_required(*STAFF_ROLES)
def equipment_list(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    items = Equipment.objects.select_related("category")
    if query:
        items = items.filter(Q(name__icontains=query) | Q(category__name__icontains=query))
    if status:
        items = items.filter(status=status)

    paginator = Paginator(items, 12)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "page_obj": page_obj,
        "query": query,
        "status": status,
        "status_choices": Equipment.Status.choices,
        "categories": EquipmentCategory.objects.all(),
    }
    return render(request, "equipment/equipment_list.html", context)


@login_required
@role_required(*STAFF_ROLES)
def equipment_detail(request, pk):
    item = get_object_or_404(Equipment, pk=pk)
    return render(
        request,
        "equipment/equipment_detail.html",
        {"item": item, "repairs": item.repairs.all()},
    )


@login_required
@role_required(*ADMIN_ROLES)
def equipment_create(request):
    if request.method == "POST":
        form = EquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipment added.")
            return redirect("equipment:list")
    else:
        form = EquipmentForm()
    return render(
        request,
        "equipment/equipment_form.html",
        {"form": form, "title": "Add Equipment"},
    )


@login_required
@role_required(*ADMIN_ROLES)
def equipment_edit(request, pk):
    item = get_object_or_404(Equipment, pk=pk)
    if request.method == "POST":
        form = EquipmentForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "Equipment updated.")
            return redirect("equipment:detail", pk=item.pk)
    else:
        form = EquipmentForm(instance=item)
    return render(
        request,
        "equipment/equipment_form.html",
        {"form": form, "title": "Edit Equipment"},
    )


@login_required
@role_required(*ADMIN_ROLES)
def equipment_delete(request, pk):
    item = get_object_or_404(Equipment, pk=pk)
    if request.method == "POST":
        item.delete()
        messages.success(request, "Equipment deleted.")
        return redirect("equipment:list")
    return render(request, "equipment/equipment_confirm_delete.html", {"object": item})


@login_required
@role_required(*ADMIN_ROLES)
def category_manage(request):
    """List and create equipment categories on one page."""
    if request.method == "POST":
        form = EquipmentCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added.")
            return redirect("equipment:categories")
    else:
        form = EquipmentCategoryForm()
    categories = EquipmentCategory.objects.all()
    return render(
        request,
        "equipment/category_list.html",
        {"form": form, "categories": categories},
    )


@login_required
@role_required(*ADMIN_ROLES)
def repair_add(request, pk):
    """Log a repair for a piece of equipment."""
    item = get_object_or_404(Equipment, pk=pk)
    if request.method == "POST":
        form = RepairHistoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Repair record added.")
            return redirect("equipment:detail", pk=item.pk)
    else:
        form = RepairHistoryForm(initial={"equipment": item})
    return render(
        request,
        "equipment/repair_form.html",
        {"form": form, "item": item},
    )
