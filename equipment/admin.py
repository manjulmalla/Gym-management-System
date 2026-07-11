from django.contrib import admin

from .models import Equipment, EquipmentCategory, RepairHistory


class RepairHistoryInline(admin.TabularInline):
    model = RepairHistory
    extra = 0


@admin.register(EquipmentCategory)
class EquipmentCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "quantity", "status", "next_maintenance")
    list_filter = ("status", "category")
    search_fields = ("name",)
    inlines = [RepairHistoryInline]


@admin.register(RepairHistory)
class RepairHistoryAdmin(admin.ModelAdmin):
    list_display = ("equipment", "date", "cost", "technician")
    list_filter = ("date",)
    search_fields = ("equipment__name", "technician")
