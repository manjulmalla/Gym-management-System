"""Payment views: history, invoices and receipts (PDF)."""

from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import get_template

from accounts.permissions import ADMIN_ROLES, STAFF_ROLES, role_required

from .forms import PaymentForm
from .models import Payment


@login_required
@role_required(*STAFF_ROLES)
def payment_list(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()

    payments = Payment.objects.select_related("member")
    if query:
        payments = payments.filter(
            Q(member__full_name__icontains=query)
            | Q(invoice_number__icontains=query)
        )
    if status:
        payments = payments.filter(status=status)

    paginator = Paginator(payments, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    totals = Payment.objects.filter(status=Payment.Status.PAID).aggregate(
        total=Sum("amount")
    )
    pending = Payment.objects.filter(status=Payment.Status.PENDING).aggregate(
        total=Sum("amount")
    )
    context = {
        "page_obj": page_obj,
        "query": query,
        "status": status,
        "status_choices": Payment.Status.choices,
        "total_paid": totals["total"] or 0,
        "total_pending": pending["total"] or 0,
    }
    return render(request, "payments/payment_list.html", context)


@login_required
@role_required(*STAFF_ROLES)
def payment_create(request):
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, "Payment recorded successfully.")
            return redirect("payments:receipt", pk=payment.pk)
    else:
        form = PaymentForm()
    return render(
        request, "payments/payment_form.html", {"form": form, "title": "Record Payment"}
    )


@login_required
@role_required(*STAFF_ROLES)
def payment_edit(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == "POST":
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            form.save()
            messages.success(request, "Payment updated successfully.")
            return redirect("payments:list")
    else:
        form = PaymentForm(instance=payment)
    return render(
        request, "payments/payment_form.html", {"form": form, "title": "Edit Payment"}
    )


@login_required
@role_required(*ADMIN_ROLES)
def payment_delete(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if request.method == "POST":
        payment.delete()
        messages.success(request, "Payment deleted.")
        return redirect("payments:list")
    return render(request, "payments/payment_confirm_delete.html", {"object": payment})


@login_required
@role_required(*STAFF_ROLES)
def receipt(request, pk):
    """HTML receipt / invoice preview (printable)."""
    payment = get_object_or_404(Payment.objects.select_related("member"), pk=pk)
    return render(request, "payments/receipt.html", {"payment": payment})


@login_required
@role_required(*STAFF_ROLES)
def invoice_pdf(request, pk):
    """Generate a PDF invoice with ReportLab."""
    payment = get_object_or_404(Payment.objects.select_related("member"), pk=pk)

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
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
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=f"Invoice {payment.invoice_number}")
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("GymPro", styles["Title"]))
    elements.append(Paragraph("Payment Invoice", styles["Heading2"]))
    elements.append(Spacer(1, 8 * mm))

    info = [
        ["Invoice #", payment.invoice_number],
        ["Date", payment.date.strftime("%Y-%m-%d")],
        ["Member", payment.member.full_name],
        ["Membership ID", payment.member.membership_id],
        ["Method", payment.get_method_display()],
        ["Status", payment.get_status_display()],
    ]
    table = Table(info, colWidths=[50 * mm, 100 * mm])
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(table)
    elements.append(Spacer(1, 8 * mm))

    amount_table = Table(
        [["Description", "Amount"], ["Membership Fee", f"${payment.amount}"],
         ["Total", f"${payment.amount}"]],
        colWidths=[100 * mm, 50 * mm],
    )
    amount_table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563eb")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(amount_table)
    elements.append(Spacer(1, 12 * mm))
    elements.append(Paragraph("Thank you for choosing GymPro!", styles["Italic"]))

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="invoice_{payment.invoice_number}.pdf"'
    )
    return response
