"""Equipment inventory, categories and repair history."""

from django.db import models


class EquipmentCategory(models.Model):
    """A category of equipment (Cardio, Strength, Free Weights...)."""

    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name_plural = "Equipment categories"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Equipment(models.Model):
    """A piece of gym equipment."""

    class Status(models.TextChoices):
        WORKING = "working", "Working"
        MAINTENANCE = "maintenance", "Under Maintenance"
        REPAIR = "repair", "Needs Repair"
        OUT_OF_ORDER = "out_of_order", "Out of Order"

    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        EquipmentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="equipment",
    )
    photo = models.ImageField(upload_to="equipment/", blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    purchase_date = models.DateField(null=True, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.WORKING
    )
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Equipment"

    def __str__(self) -> str:
        return self.name


class RepairHistory(models.Model):
    """A repair / maintenance log entry for a piece of equipment."""

    equipment = models.ForeignKey(
        Equipment, on_delete=models.CASCADE, related_name="repairs"
    )
    date = models.DateField()
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    technician = models.CharField(max_length=120, blank=True)

    class Meta:
        ordering = ["-date"]
        verbose_name_plural = "Repair history"

    def __str__(self) -> str:
        return f"{self.equipment} - {self.date}"
