"""Attendance views: check-in/out and reports."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.permissions import STAFF_ROLES, role_required
from members.models import Member

from .models import Attendance


@login_required
@role_required(*STAFF_ROLES)
def attendance_list(request):
    """List attendance records with optional date filter."""
    date_str = request.GET.get("date", "").strip()
    records = Attendance.objects.select_related("member")
    if date_str:
        records = records.filter(date=date_str)

    paginator = Paginator(records, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    today = timezone.localdate()
    context = {
        "page_obj": page_obj,
        "date": date_str,
        "today_count": Attendance.objects.filter(date=today).count(),
    }
    return render(request, "attendance/attendance_list.html", context)


@login_required
@role_required(*STAFF_ROLES)
def check_in(request):
    """Check a member in for today."""
    if request.method == "POST":
        member = get_object_or_404(Member, pk=request.POST.get("member"))
        today = timezone.localdate()
        record, created = Attendance.objects.get_or_create(member=member, date=today)
        if record.check_in:
            messages.info(request, f"{member} is already checked in today.")
        else:
            record.check_in = timezone.now()
            record.save()
            messages.success(request, f"{member} checked in successfully.")
        return redirect("attendance:list")

    members = Member.objects.filter(status=Member.Status.ACTIVE)
    return render(request, "attendance/check_in.html", {"members": members})


@login_required
@role_required(*STAFF_ROLES)
def check_out(request, pk):
    """Check a member out."""
    record = get_object_or_404(Attendance, pk=pk)
    if record.check_out:
        messages.info(request, "Member already checked out.")
    else:
        record.check_out = timezone.now()
        record.save()
        messages.success(request, f"{record.member} checked out successfully.")
    return redirect("attendance:list")


@login_required
@role_required(*STAFF_ROLES)
def monthly_report(request):
    """Monthly attendance summary grouped by day."""
    today = timezone.localdate()
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    records = Attendance.objects.filter(date__year=year, date__month=month)
    # Count attendances per day for a chart.
    daily = {}
    for rec in records:
        daily[rec.date.day] = daily.get(rec.date.day, 0) + 1

    context = {
        "year": year,
        "month": month,
        "total": records.count(),
        "labels": sorted(daily.keys()),
        "data": [daily[d] for d in sorted(daily.keys())],
    }
    return render(request, "attendance/monthly_report.html", context)
