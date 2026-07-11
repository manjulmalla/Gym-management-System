"""Workout classes with scheduling, capacity and enrolment."""

from django.db import models


class WorkoutClass(models.Model):
    """A scheduled workout class (Yoga, Cardio, Zumba, ...)."""

    class ClassType(models.TextChoices):
        YOGA = "yoga", "Yoga"
        CARDIO = "cardio", "Cardio"
        STRENGTH = "strength", "Strength Training"
        ZUMBA = "zumba", "Zumba"
        CROSSFIT = "crossfit", "CrossFit"
        HIIT = "hiit", "HIIT"
        PERSONAL = "personal", "Personal Training"

    class Day(models.TextChoices):
        MON = "monday", "Monday"
        TUE = "tuesday", "Tuesday"
        WED = "wednesday", "Wednesday"
        THU = "thursday", "Thursday"
        FRI = "friday", "Friday"
        SAT = "saturday", "Saturday"
        SUN = "sunday", "Sunday"

    name = models.CharField(max_length=120)
    class_type = models.CharField(
        max_length=20, choices=ClassType.choices, default=ClassType.CARDIO
    )
    trainer = models.ForeignKey(
        "trainers.Trainer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classes",
    )
    day = models.CharField(max_length=10, choices=Day.choices, default=Day.MON)
    start_time = models.TimeField()
    end_time = models.TimeField()
    capacity = models.PositiveIntegerField(default=20)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["day", "start_time"]
        verbose_name_plural = "Workout classes"

    def __str__(self) -> str:
        return f"{self.name} ({self.get_day_display()})"

    @property
    def enrolled_count(self) -> int:
        return self.enrollments.count()

    @property
    def seats_left(self) -> int:
        return max(self.capacity - self.enrolled_count, 0)

    @property
    def is_full(self) -> bool:
        return self.enrolled_count >= self.capacity


class ClassEnrollment(models.Model):
    """A member enrolled in a workout class."""

    workout_class = models.ForeignKey(
        WorkoutClass, on_delete=models.CASCADE, related_name="enrollments"
    )
    member = models.ForeignKey(
        "members.Member", on_delete=models.CASCADE, related_name="class_enrollments"
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("workout_class", "member")

    def __str__(self) -> str:
        return f"{self.member} -> {self.workout_class}"
