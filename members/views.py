"""Member management views: CRUD, search and filtering."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import ADMIN_ROLES, STAFF_ROLES, role_required

from .forms import MemberForm
from .models import Member


@login_required
@role_required(*STAFF_ROLES)
def member_list(request):
    """Searchable, filterable, paginated list of members."""
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    members = Member.objects.select_related("trainer")
    if query:
        members = members.filter(
            Q(full_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
            | Q(membership_id__icontains=query)
        )
    if status:
        members = members.filter(status=status)

    paginator = Paginator(members, 10)
    page_obj = paginator.get_page(request.GET.get("page"))
    context = {
        "page_obj": page_obj,
        "query": query,
        "status": status,
        "status_choices": Member.Status.choices,
    }
    return render(request, "members/member_list.html", context)


@login_required
@role_required(*STAFF_ROLES)
def member_detail(request, pk):
    member = get_object_or_404(
        Member.objects.select_related("trainer"), pk=pk
    )
    context = {
        "member": member,
        "memberships": member.memberships.select_related("plan").all(),
        "payments": member.payments.all()[:10],
        "attendances": member.attendances.all()[:10],
    }
    return render(request, "members/member_detail.html", context)


@login_required
@role_required(*STAFF_ROLES)
def member_create(request):
    if request.method == "POST":
        form = MemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save()
            messages.success(request, "Member added successfully.")
            return redirect("members:detail", pk=member.pk)
    else:
        form = MemberForm()
    return render(
        request, "members/member_form.html", {"form": form, "title": "Add Member"}
    )


@login_required
@role_required(*STAFF_ROLES)
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == "POST":
        form = MemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Member updated successfully.")
            return redirect("members:detail", pk=member.pk)
    else:
        form = MemberForm(instance=member)
    return render(
        request, "members/member_form.html", {"form": form, "title": "Edit Member"}
    )


@login_required
@role_required(*ADMIN_ROLES)
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == "POST":
        member.delete()
        messages.success(request, "Member deleted.")
        return redirect("members:list")
    return render(request, "members/member_confirm_delete.html", {"object": member})
