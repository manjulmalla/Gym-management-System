"""Dashboard views: KPIs, charts, home page, settings and global search."""

import json
from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import render
from django.utils import timezone

from accounts.permissions import ADMIN_ROLES, role_required
from attendance.models import Attendance
from classes.models import WorkoutClass
from equipment.models import Equipment
from members.models import Member
from memberships.models import Membership
from payments.models import Payment
from trainers.models import Trainer


def landing(request):
    """Public landing / home page."""
    if request.user.is_authenticated:
        return dashboard(request)
    plans = None
    try:
        from memberships.models import MembershipPlan

        plans = MembershipPlan.objects.filter(is_active=True)[:3]
    except Exception:
        plans = []
    return render(request, "home.html", {"plans": plans})


@login_required
def dashboard(request):
    """Main dashboard with KPI cards and charts."""
    today = timezone.localdate()
    month_start = today.replace(day=1)

    # KPI numbers
    total_members = Member.objects.count()
    active_members = Member.objects.filter(status=Member.Status.ACTIVE).count()
    total_trainers = Trainer.objects.filter(status=Trainer.Status.ACTIVE).count()
    attendance_today = Attendance.objects.filter(date=today).count()

    monthly_revenue = (
        Payment.objects.filter(status=Payment.Status.PAID, date__gte=month_start)
        .aggregate(total=Sum("amount"))
        .get("total")
        or 0
    )

    # Expiring memberships (next 7 days)
    expiring = Membership.objects.select_related("member", "plan").filter(
        status=Membership.Status.ACTIVE,
        end_date__gte=today,
        end_date__lte=today + timedelta(days=7),
    )[:5]

    recent_payments = Payment.objects.select_related("member")[:5]
    upcoming_classes = WorkoutClass.objects.select_related("trainer").filter(
        is_active=True
    )[:5]

    # Equipment status breakdown
    equipment_status = {
        "working": Equipment.objects.filter(status=Equipment.Status.WORKING).count(),
        "maintenance": Equipment.objects.filter(
            status=Equipment.Status.MAINTENANCE
        ).count(),
        "repair": Equipment.objects.filter(status=Equipment.Status.REPAIR).count(),
        "out_of_order": Equipment.objects.filter(
            status=Equipment.Status.OUT_OF_ORDER
        ).count(),
    }

    # Revenue chart: last 6 months
    revenue_labels = []
    revenue_data = []
    for i in range(5, -1, -1):
        # Walk back `i` months from the current month start.
        target = month_start
        for _ in range(i):
            target = (target - timedelta(days=1)).replace(day=1)
        next_month = (target + timedelta(days=32)).replace(day=1)
        total = (
            Payment.objects.filter(
                status=Payment.Status.PAID,
                date__gte=target,
                date__lt=next_month,
            )
            .aggregate(total=Sum("amount"))
            .get("total")
            or 0
        )
        revenue_labels.append(target.strftime("%b %Y"))
        revenue_data.append(float(total))

    # Attendance chart: last 7 days
    attendance_labels = []
    attendance_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        attendance_labels.append(day.strftime("%a"))
        attendance_data.append(Attendance.objects.filter(date=day).count())

    context = {
        "total_members": total_members,
        "active_members": active_members,
        "total_trainers": total_trainers,
        "attendance_today": attendance_today,
        "monthly_revenue": monthly_revenue,
        "expiring": expiring,
        "recent_payments": recent_payments,
        "upcoming_classes": upcoming_classes,
        "equipment_status": equipment_status,
        "revenue_labels": json.dumps(revenue_labels),
        "revenue_data": json.dumps(revenue_data),
        "attendance_labels": json.dumps(attendance_labels),
        "attendance_data": json.dumps(attendance_data),
        "equipment_chart": json.dumps(list(equipment_status.values())),
    }
    return render(request, "dashboard/dashboard.html", context)


@login_required
def global_search(request):
    """Search across members, trainers and payments."""
    query = request.GET.get("q", "").strip()
    members = trainers = payments = []
    if query:
        members = Member.objects.filter(
            Q(full_name__icontains=query)
            | Q(email__icontains=query)
            | Q(phone__icontains=query)
            | Q(membership_id__icontains=query)
        )[:20]
        trainers = Trainer.objects.filter(
            Q(full_name__icontains=query) | Q(specialization__icontains=query)
        )[:20]
        payments = Payment.objects.filter(
            Q(invoice_number__icontains=query)
            | Q(member__full_name__icontains=query)
        )[:20]
    context = {
        "query": query,
        "members": members,
        "trainers": trainers,
        "payments": payments,
    }
    return render(request, "dashboard/search.html", context)


@login_required
@role_required(*ADMIN_ROLES)
def settings_view(request):
    """System settings / admin tools landing page."""
    return render(request, "dashboard/settings.html")
