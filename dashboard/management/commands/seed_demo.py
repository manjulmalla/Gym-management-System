"""
Seed the database with realistic demo data for GymPro.

Usage::

    python manage.py seed_demo

Creates staff users, trainers, membership plans, members, memberships,
payments, attendance, workout classes, equipment and notifications so the
dashboard and every page has meaningful content out of the box.
"""

import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from attendance.models import Attendance
from classes.models import WorkoutClass
from equipment.models import Equipment, EquipmentCategory
from members.models import Member
from memberships.models import Membership, MembershipPlan
from notifications.models import Notification
from payments.models import Payment
from trainers.models import Trainer

User = get_user_model()

FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Chris", "Karen",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
]


class Command(BaseCommand):
    help = "Populate the database with demo data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--members", type=int, default=40, help="Number of members to create."
        )

    def handle(self, *args, **options):
        random.seed(42)
        today = timezone.localdate()

        self.stdout.write("Creating staff users...")
        self._create_user("manager", "Gym", "Manager", "manager")
        self._create_user("reception", "Front", "Desk", "receptionist")

        self.stdout.write("Creating membership plans...")
        plans = self._create_plans()

        self.stdout.write("Creating trainers...")
        trainers = self._create_trainers()

        self.stdout.write("Creating members, memberships & payments...")
        members = []
        for _ in range(options["members"]):
            member = self._create_member(trainers)
            members.append(member)

            plan = random.choice(plans)
            start = today - timedelta(days=random.randint(0, 60))
            membership = Membership.objects.create(
                member=member, plan=plan, start_date=start
            )
            membership.refresh_status()
            membership.save()

            Payment.objects.create(
                member=member,
                membership=membership,
                amount=plan.price,
                method=random.choice([m[0] for m in Payment.Method.choices]),
                status=Payment.Status.PAID,
                date=start,
            )

        self.stdout.write("Creating attendance records...")
        for _ in range(120):
            member = random.choice(members)
            day = today - timedelta(days=random.randint(0, 6))
            check_in = timezone.now() - timedelta(
                days=random.randint(0, 6), hours=random.randint(1, 5)
            )
            Attendance.objects.get_or_create(
                member=member,
                date=day,
                defaults={"check_in": check_in},
            )

        self.stdout.write("Creating equipment...")
        self._create_equipment()

        self.stdout.write("Creating workout classes...")
        self._create_classes(trainers)

        self.stdout.write("Creating notifications...")
        Notification.objects.get_or_create(
            title="Welcome to GymPro!",
            defaults={
                "message": "Explore your new gym management dashboard.",
                "notification_type": Notification.Type.ANNOUNCEMENT,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data created successfully!"))
        self.stdout.write(
            "Staff logins -> manager/manager12345, reception/reception12345"
        )

    # -- helpers -----------------------------------------------------------
    def _create_user(self, username, first, last, role):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "first_name": first,
                "last_name": last,
                "email": f"{username}@gympro.local",
                "role": role,
            },
        )
        if created:
            user.set_password(f"{username}12345")
            user.is_staff = role in {"manager", "super_admin"}
            user.save()
        return user

    def _create_plans(self):
        data = [
            ("Day Pass", "daily", 1, 10, "Gym access for a day\nLocker access"),
            ("Weekly", "weekly", 7, 40, "7 days access\nGroup classes"),
            ("Monthly Basic", "monthly", 30, 45, "Full gym access\n1 free class/week"),
            ("Quarterly Pro", "quarterly", 90, 120, "Full access\nPersonal trainer\nNutrition plan"),
            ("Yearly Elite", "yearly", 365, 400, "All access\nPersonal trainer\nSpa & sauna\nPriority booking"),
        ]
        plans = []
        for name, ptype, days, price, features in data:
            plan, _ = MembershipPlan.objects.get_or_create(
                name=name,
                defaults={
                    "plan_type": ptype,
                    "duration_days": days,
                    "price": price,
                    "features": features,
                },
            )
            plans.append(plan)
        return plans

    def _create_trainers(self):
        specs = ["Yoga", "Strength Training", "Cardio", "CrossFit", "HIIT", "Zumba"]
        trainers = []
        for i, spec in enumerate(specs):
            name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
            trainer, _ = Trainer.objects.get_or_create(
                full_name=name,
                defaults={
                    "email": f"trainer{i}@gympro.local",
                    "phone": f"555-01{i:02d}",
                    "specialization": spec,
                    "salary": random.randint(2000, 5000),
                    "hire_date": timezone.localdate() - timedelta(days=random.randint(30, 900)),
                    "schedule": "Mon-Fri 6am-2pm",
                },
            )
            trainers.append(trainer)
        return trainers

    def _create_member(self, trainers):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        return Member.objects.create(
            full_name=name,
            email=f"{name.replace(' ', '.').lower()}{random.randint(1, 999)}@example.com",
            phone=f"555-{random.randint(1000, 9999)}",
            gender=random.choice(["male", "female"]),
            date_of_birth=timezone.localdate() - timedelta(days=random.randint(6500, 18000)),
            trainer=random.choice(trainers),
            height_cm=random.randint(150, 195),
            weight_kg=random.randint(50, 110),
            status="active",
            join_date=timezone.localdate() - timedelta(days=random.randint(0, 365)),
        )

    def _create_equipment(self):
        categories = {}
        for cname in ["Cardio", "Strength", "Free Weights", "Functional"]:
            categories[cname], _ = EquipmentCategory.objects.get_or_create(name=cname)

        items = [
            ("Treadmill", "Cardio", 8),
            ("Elliptical", "Cardio", 4),
            ("Leg Press", "Strength", 2),
            ("Bench Press", "Strength", 3),
            ("Dumbbell Set", "Free Weights", 20),
            ("Kettlebell Set", "Free Weights", 15),
            ("Rowing Machine", "Cardio", 5),
            ("Cable Machine", "Functional", 2),
        ]
        statuses = ["working", "working", "working", "maintenance", "repair"]
        for name, cat, qty in items:
            Equipment.objects.get_or_create(
                name=name,
                defaults={
                    "category": categories[cat],
                    "quantity": qty,
                    "status": random.choice(statuses),
                    "cost": random.randint(500, 5000),
                    "purchase_date": timezone.localdate() - timedelta(days=random.randint(100, 1000)),
                    "next_maintenance": timezone.localdate() + timedelta(days=random.randint(10, 90)),
                },
            )

    def _create_classes(self, trainers):
        classes = [
            ("Morning Yoga", "yoga", "monday", "06:00", "07:00"),
            ("Cardio Blast", "cardio", "tuesday", "18:00", "19:00"),
            ("Strength 101", "strength", "wednesday", "17:00", "18:30"),
            ("Zumba Party", "zumba", "thursday", "19:00", "20:00"),
            ("CrossFit WOD", "crossfit", "friday", "06:30", "07:30"),
            ("HIIT Express", "hiit", "saturday", "09:00", "09:45"),
        ]
        for name, ctype, day, start, end in classes:
            WorkoutClass.objects.get_or_create(
                name=name,
                defaults={
                    "class_type": ctype,
                    "trainer": random.choice(trainers),
                    "day": day,
                    "start_time": start,
                    "end_time": end,
                    "capacity": random.randint(15, 30),
                },
            )
