from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "member", "amount", "method", "status", "date")
    list_filter = ("status", "method", "date")
    search_fields = ("invoice_number", "member__full_name")
    date_hierarchy = "date"
    readonly_fields = ("invoice_number",)
