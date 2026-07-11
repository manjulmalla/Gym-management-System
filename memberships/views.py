"""Views for membership plans, subscriptions and renewals."""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.permissions import ADMIN_ROLES, STAFF_ROLES, role_required

from .forms import MembershipForm, MembershipPlanForm
from .models import Membership, MembershipPlan


# ---------------------------------------------------------------------------
# Membership plans
# ---------------------------------------------------------------------------
@login_required
@role_required(*STAFF_ROLES)
def plan_list(request):
    plans = MembershipPlan.objects.all()
    return render(request, "memberships/plan_list.html", {"plans": plans})


@login_required
@role_required(*ADMIN_ROLES)
def plan_create(request):
    if request.method == "POST":
        form = MembershipPlanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Membership plan created.")
            return redirect("memberships:plan_list")
    else:
        form = MembershipPlanForm()
    return render(
        request, "memberships/plan_form.html", {"form": form, "title": "Add Plan"}
    )


@login_required
@role_required(*ADMIN_ROLES)
def plan_edit(request, pk):
    plan = get_object_or_404(MembershipPlan, pk=pk)
    if request.method == "POST":
        form = MembershipPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, "Membership plan updated.")
            return redirect("memberships:plan_list")
    else:
        form = MembershipPlanForm(instance=plan)
    return render(
        request, "memberships/plan_form.html", {"form": form, "title": "Edit Plan"}
    )


@login_required
@role_required(*ADMIN_ROLES)
def plan_delete(request, pk):
    plan = get_object_or_404(MembershipPlan, pk=pk)
    if request.method == "POST":
        plan.delete()
        messages.success(request, "Membership plan deleted.")
        return redirect("memberships:plan_list")
    return render(request, "memberships/plan_confirm_delete.html", {"object": plan})


# ---------------------------------------------------------------------------
# Memberships (subscriptions)
# ---------------------------------------------------------------------------
@login_required
@role_required(*STAFF_ROLES)
def membership_list(request):
    status = request.GET.get("status", "").strip()
    memberships = Membership.objects.select_related("member", "plan")
    if status:
        memberships = memberships.filter(status=status)

    paginator = Paginator(memberships, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    # Memberships expiring within the next 7 days.
    today = timezone.localdate()
    expiring = Membership.objects.select_related("member", "plan").filter(
        status=Membership.Status.ACTIVE,
        end_date__gte=today,
        end_date__lte=today + timedelta(days=7),
    )
    context = {
        "page_obj": page_obj,
        "status": status,
        "status_choices": Membership.Status.choices,
        "expiring": expiring,
    }
    return render(request, "memberships/membership_list.html", context)


@login_required
@role_required(*STAFF_ROLES)
def membership_create(request):
    if request.method == "POST":
        form = MembershipForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Membership assigned successfully.")
            return redirect("memberships:membership_list")
    else:
        form = MembershipForm()
    return render(
        request,
        "memberships/membership_form.html",
        {"form": form, "title": "Add Membership"},
    )


@login_required
@role_required(*STAFF_ROLES)
def membership_edit(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    if request.method == "POST":
        form = MembershipForm(request.POST, instance=membership)
        if form.is_valid():
            form.save()
            messages.success(request, "Membership updated.")
            return redirect("memberships:membership_list")
    else:
        form = MembershipForm(instance=membership)
    return render(
        request,
        "memberships/membership_form.html",
        {"form": form, "title": "Edit Membership"},
    )


@login_required
@role_required(*STAFF_ROLES)
def membership_renew(request, pk):
    """Renew a membership by extending it for another plan duration."""
    membership = get_object_or_404(Membership, pk=pk)
    if request.method == "POST":
        today = timezone.localdate()
        base = max(membership.end_date or today, today)
        membership.start_date = base
        membership.end_date = base + timedelta(days=membership.plan.duration_days)
        membership.status = Membership.Status.ACTIVE
        membership.save()
        messages.success(request, "Membership renewed successfully.")
        return redirect("memberships:membership_list")
    return render(
        request, "memberships/membership_renew.html", {"membership": membership}
    )


@login_required
@role_required(*ADMIN_ROLES)
def membership_delete(request, pk):
    membership = get_object_or_404(Membership, pk=pk)
    if request.method == "POST":
        membership.delete()
        messages.success(request, "Membership deleted.")
        return redirect("memberships:membership_list")
    return render(
        request, "memberships/membership_confirm_delete.html", {"object": membership}
    )
