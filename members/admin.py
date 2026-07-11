from django.contrib import admin

from .models import Member


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "membership_id",
        "full_name",
        "phone",
        "trainer",
        "status",
        "join_date",
    )
    list_filter = ("status", "gender", "trainer")
    search_fields = ("full_name", "email", "phone", "membership_id")
    date_hierarchy = "join_date"
    readonly_fields = ("membership_id",)
