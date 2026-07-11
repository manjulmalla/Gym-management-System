# GymPro — Gym Management System

A modern, production-ready **Gym Management System** built with **Django 5** and **SQLite**.
GymPro provides a premium dashboard for managing members, trainers, memberships,
attendance, payments, workout classes, equipment, reports and notifications —
with role-based access control and a responsive Bootstrap 5 UI.

---

## Features

- **Authentication** — register, login, logout, forgot/change password, profile update
- **Role-based access** — Super Admin, Gym Manager, Trainer, Receptionist, Member
- **Dashboard** — KPI cards + Chart.js charts (revenue, attendance, equipment status)
- **Members** — CRUD, photo upload, medical info, emergency contact, BMI, search & filters
- **Trainers** — profiles, assigned members, schedule, salary, trainer attendance
- **Memberships** — daily/weekly/monthly/quarterly/yearly/custom plans, renewals, expiry reminders
- **Attendance** — check-in / check-out, daily & monthly reports
- **Payments** — record payments, invoices, printable receipts, **PDF invoices** (ReportLab)
- **Workout Classes** — Yoga, Cardio, Strength, Zumba, CrossFit, HIIT, capacity & enrolment
- **Equipment** — inventory, categories, maintenance schedule, repair history
- **Reports** — Member, Attendance, Revenue, Trainer, Membership & Equipment PDF exports
- **Notifications** — expiry, payment, birthday, class reminders & admin announcements
- **Global search**, pagination, image upload, form validation, toast messages, loading spinner
- **Security** — CSRF, XSS & SQL-injection protection, login-required & permission-based views

---

## Tech Stack

| Layer     | Technology                       |
|-----------|----------------------------------|
| Backend   | Django 5+ (Python)               |
| Database  | SQLite                           |
| Frontend  | Django Templates, Bootstrap 5    |
| Charts    | Chart.js                         |
| PDF       | ReportLab                        |
| Images    | Pillow                           |

---

## Project Structure

```
gymms/
├── gympro/            # Project settings, URLs, WSGI/ASGI
├── accounts/          # Custom User, roles, auth, permissions
├── members/           # Member management
├── trainers/          # Trainer management & attendance
├── memberships/       # Plans, subscriptions, renewals
├── attendance/        # Member check-in / check-out
├── payments/          # Payments, invoices, receipts (PDF)
├── equipment/         # Equipment, categories, repairs
├── classes/           # Workout classes & enrolment
├── dashboard/         # KPIs, charts, search, settings, seed_demo command
├── reports/           # PDF report exports
├── notifications/     # Notifications & announcements
├── templates/         # HTML templates (base, partials, per-app)
├── static/            # CSS & JS
├── media/             # Uploaded files (created at runtime)
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Installation Guide

### 1. Prerequisites
- Python 3.11+ installed

### 2. Create and activate a virtual environment

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment (optional)
```bash
# Windows:  copy .env.example .env
# macOS/Linux:
cp .env.example .env
```
Edit `.env` and set your own `SECRET_KEY` for production.
If you skip this step, sensible development defaults are used.

### 5. Apply database migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a super admin
```bash
python manage.py createsuperuser
```

### 7. (Optional) Load demo data
```bash
python manage.py seed_demo
```
This creates trainers, plans, ~40 members, payments, attendance, classes,
equipment and demo staff logins:
- `manager` / `manager12345`
- `reception` / `reception12345`

> After running `createsuperuser`, open the Django admin (`/admin/`) and set the
> new user's **role** to *Super Admin* to unlock all administration menus.

### 8. Run the development server
```bash
python manage.py runserver
```

Visit **http://127.0.0.1:8000/**

- Landing page: `/`
- Dashboard: `/dashboard/`
- Admin panel: `/admin/`

---

## User Roles & Permissions

| Role          | Access                                                       |
|---------------|-------------------------------------------------------------|
| Super Admin   | Everything, including Django admin & user management        |
| Gym Manager   | Everything except superuser-only admin operations           |
| Receptionist  | Members, memberships, attendance, payments, classes (view)  |
| Trainer       | Staff-level read access to operational pages                |
| Member        | Personal profile & self-service pages                       |

Access is enforced with the reusable `role_required` decorator and
`RoleRequiredMixin` in `accounts/permissions.py`.

---

## Database Backup & Restore

GymPro uses SQLite, so backups are simple:

**Backup (JSON dump):**
```bash
python manage.py dumpdata --natural-primary --natural-foreign -o backup.json
```

**Restore:**
```bash
python manage.py loaddata backup.json
```

You can also copy the `db.sqlite3` file directly for a full binary backup.

---

## Security Notes

- Set `DEBUG=False` and a strong `SECRET_KEY` in production.
- Configure `ALLOWED_HOSTS` in `.env`.
- When `DEBUG=False`, secure cookies, HSTS and SSL redirect are enabled.
- Serve static files with `python manage.py collectstatic` behind a real web server.

---

## License

Provided as-is for educational and commercial use. Customize freely.
