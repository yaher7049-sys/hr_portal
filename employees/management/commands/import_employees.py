import json
from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from employees.models import Employee

User = get_user_model()

FIELD_MAP = [
    "department", "designation", "employment_type", "reporting_manager_name",
    "reporting_manager_email", "work_location", "gender", "marital_status",
    "blood_group", "education", "college_university_name", "notice_period_months",
    "years_of_experience", "experience_note", "contact_number", "personal_email",
    "office_email", "current_address", "permanent_address", "emergency_contact_name",
    "emergency_contact_relationship", "emergency_contact_number", "aadhaar_no",
    "pan_card_no", "uan_no", "pf_number", "esic_no", "bank_name",
    "bank_account_number", "ifsc_code",
]
DATE_FIELDS = ["date_of_joining", "date_of_birth"]


def parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


class Command(BaseCommand):
    help = "Import employees from a JSON file and create matching login accounts."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_path",
            nargs="?",
            default="data/employees_full.json",
            help="Path to the employees JSON file (default: data/employees_full.json)",
        )
        parser.add_argument(
            "--hr",
            nargs="*",
            default=[],
            help="Employee IDs to mark as HR (staff) accounts, e.g. --hr AAPL100 AAPL105",
        )

    def handle(self, *args, **options):
        path = options["json_path"]
        try:
            with open(path, encoding="utf-8") as f:
                records = json.load(f)
        except FileNotFoundError as exc:
            raise CommandError(f"Could not find {path}") from exc

        hr_ids = set(options["hr"])
        created, updated = 0, 0

        for rec in records:
            employee_id = rec.get("employee_id")
            full_name = rec.get("full_name")
            if not employee_id or not full_name:
                self.stderr.write(f"Skipping record with missing employee_id/full_name: {rec}")
                continue

            is_hr = employee_id in hr_ids
            user, user_created = User.objects.get_or_create(
                username=employee_id,
                defaults={
                    "first_name": full_name.split(" ")[0],
                    "email": rec.get("office_email") or "",
                    "is_staff": is_hr,
                },
            )
            if user_created:
                # Default password = employee ID. They are forced to change it on first login.
                user.set_password(employee_id)
                user.save()
            elif user.is_staff != is_hr:
                user.is_staff = is_hr
                user.save(update_fields=["is_staff"])

            defaults = {"full_name": full_name, "user": user}
            for field in FIELD_MAP:
                defaults[field] = rec.get(field)
            for field in DATE_FIELDS:
                defaults[field] = parse_date(rec.get(field))

            obj, was_created = Employee.objects.update_or_create(
                employee_id=employee_id, defaults=defaults
            )
            created += int(was_created)
            updated += int(not was_created)

        self.stdout.write(self.style.SUCCESS(
            f"Done. Created {created} new employee record(s), updated {updated} existing one(s)."
        ))
        self.stdout.write(
            "Default login password for new accounts is the Employee ID itself — "
            "they'll be required to change it on first login."
        )
