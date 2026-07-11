"""Reports hub and PDF export using ReportLab."""

from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from accounts.permissions import ADMIN_ROLES, STAFF_ROLES, role_required
from attendance.models import Attendance
from equipment.models import Equipment
from members.models import Member
from memberships.models import Membership
from payments.models import Payment
from trainers.models import Trainer


@login_required
@role_required(*STAFF_ROLES)
def reports_home(request):
    """Reports landing page with links to each PDF export."""
    return render(request, "reports/reports_home.html")


def _build_pdf(title, columns, rows, summary=None):
    """Helper that renders a titled table into a PDF byte stream."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), title=title)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph("GymPro", styles["Title"]),
        Paragraph(title, styles["Heading2"]),
        Paragraph(
            f"Generated on {timezone.localdate().strftime('%Y-%m-%d')}",
            styles["Normal"],
        ),
        Spacer(1, 6 * mm),
    ]

    data = [columns] + rows if rows else [columns, ["No records found."]]
    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("PADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    elements.append(table)

    if summary:
        elements.append(Spacer(1, 6 * mm))
        elements.append(Paragraph(summary, styles["Heading3"]))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def _pdf_response(buffer, filename):
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@login_required
@role_required(*STAFF_ROLES)
def member_report(request):
    rows = [
        [
            m.membership_id,
            m.full_name,
            m.phone or "-",
            m.get_status_display(),
            m.trainer.full_name if m.trainer else "-",
            m.join_date.strftime("%Y-%m-%d"),
        ]
        for m in Member.objects.select_related("trainer")
    ]
    buffer = _build_pdf(
        "Member Report",
        ["Member ID", "Name", "Phone", "Status", "Trainer", "Joined"],
        rows,
        summary=f"Total members: {len(rows)}",
    )
    return _pdf_response(buffer, "member_report.pdf")


@login_required
@role_required(*STAFF_ROLES)
def attendance_report(request):
    rows = [
        [
            a.member.full_name,
            a.date.strftime("%Y-%m-%d"),
            a.check_in.strftime("%H:%M") if a.check_in else "-",
            a.check_out.strftime("%H:%M") if a.check_out else "-",
        ]
        for a in Attendance.objects.select_related("member")[:500]
    ]
    buffer = _build_pdf(
        "Attendance Report",
        ["Member", "Date", "Check In", "Check Out"],
        rows,
        summary=f"Records shown: {len(rows)}",
    )
    return _pdf_response(buffer, "attendance_report.pdf")


@login_required
@role_required(*STAFF_ROLES)
def revenue_report(request):
    payments = Payment.objects.select_related("member")
    rows = [
        [
            p.invoice_number,
            p.member.full_name,
            f"${p.amount}",
            p.get_method_display(),
            p.get_status_display(),
            p.date.strftime("%Y-%m-%d"),
        ]
        for p in payments[:500]
    ]
    total = payments.filter(status=Payment.Status.PAID).aggregate(t=Sum("amount"))["t"] or 0
    buffer = _build_pdf(
        "Revenue Report",
        ["Invoice", "Member", "Amount", "Method", "Status", "Date"],
        rows,
        summary=f"Total collected: ${total}",
    )
    return _pdf_response(buffer, "revenue_report.pdf")


@login_required
@role_required(*STAFF_ROLES)
def trainer_report(request):
    rows = [
        [
            t.full_name,
            t.specialization or "-",
            t.phone or "-",
            f"${t.salary}",
            t.get_status_display(),
            str(t.assigned_members_count),
        ]
        for t in Trainer.objects.all()
    ]
    buffer = _build_pdf(
        "Trainer Report",
        ["Name", "Specialization", "Phone", "Salary", "Status", "Members"],
        rows,
        summary=f"Total trainers: {len(rows)}",
    )
    return _pdf_response(buffer, "trainer_report.pdf")


@login_required
@role_required(*STAFF_ROLES)
def membership_report(request):
    rows = [
        [
            m.member.full_name,
            m.plan.name,
            m.start_date.strftime("%Y-%m-%d"),
            m.end_date.strftime("%Y-%m-%d") if m.end_date else "-",
            m.get_status_display(),
        ]
        for m in Membership.objects.select_related("member", "plan")
    ]
    buffer = _build_pdf(
        "Membership Report",
        ["Member", "Plan", "Start", "End", "Status"],
        rows,
        summary=f"Total memberships: {len(rows)}",
    )
    return _pdf_response(buffer, "membership_report.pdf")


@login_required
@role_required(*STAFF_ROLES)
def equipment_report(request):
    rows = [
        [
            e.name,
            e.category.name if e.category else "-",
            str(e.quantity),
            e.get_status_display(),
            e.next_maintenance.strftime("%Y-%m-%d") if e.next_maintenance else "-",
        ]
        for e in Equipment.objects.select_related("category")
    ]
    buffer = _build_pdf(
        "Equipment Report",
        ["Name", "Category", "Qty", "Status", "Next Maintenance"],
        rows,
        summary=f"Total equipment items: {len(rows)}",
    )
    return _pdf_response(buffer, "equipment_report.pdf")
