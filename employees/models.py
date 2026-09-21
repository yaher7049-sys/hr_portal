from datetime import date

from django.conf import settings
from django.db import models


class Employee(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
        ("Payroll", "Payroll"),
        ("Contract", "Contract"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employee_profile",
        null=True,
        blank=True,
        help_text="Login account linked to this employee record.",
    )

    # --- Identity & role ---
    employee_id = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=150)
    department = models.CharField(max_length=100, blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    employment_type = models.CharField(
        max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, blank=True, null=True
    )
    reporting_manager_name = models.CharField(max_length=150, blank=True, null=True)
    reporting_manager_email = models.EmailField(blank=True, null=True)
    work_location = models.CharField(max_length=100, blank=True, null=True)

    # --- Personal ---
    gender = models.CharField(max_length=10, blank=True, null=True)
    marital_status = models.CharField(max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    education = models.CharField(max_length=50, blank=True, null=True)
    college_university_name = models.CharField(max_length=150, blank=True, null=True)

    # --- Employment ---
    date_of_joining = models.DateField(blank=True, null=True)
    notice_period_months = models.PositiveIntegerField(blank=True, null=True)
    years_of_experience = models.FloatField(blank=True, null=True)
    experience_note = models.CharField(
        max_length=120, blank=True, null=True,
        help_text="Original free-text experience value, kept for reference.",
    )

    # --- Contact ---
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    personal_email = models.EmailField(blank=True, null=True)
    office_email = models.EmailField(blank=True, null=True)
    current_address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)

    # --- Emergency contact ---
    emergency_contact_name = models.CharField(max_length=150, blank=True, null=True)
    emergency_contact_relationship = models.CharField(max_length=50, blank=True, null=True)
    emergency_contact_number = models.CharField(max_length=20, blank=True, null=True)

    # --- Statutory / bank (sensitive — see README on access control) ---
    aadhaar_no = models.CharField(max_length=20, blank=True, null=True)
    pan_card_no = models.CharField(max_length=20, blank=True, null=True)
    uan_no = models.CharField(max_length=20, blank=True, null=True)
    pf_number = models.CharField(max_length=30, blank=True, null=True)
    esic_no = models.CharField(max_length=30, blank=True, null=True)
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    bank_account_number = models.CharField(max_length=30, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)

    # --- Account state ---
    must_change_password = models.BooleanField(
        default=True,
        help_text="Forces a password change on first login. Cleared automatically once they set a new one.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return f"{self.employee_id} — {self.full_name}"

    @property
    def tenure_years(self):
        if not self.date_of_joining:
            return None
        delta_days = (date.today() - self.date_of_joining).days
        return round(delta_days / 365.25, 1)

    @property
    def is_hr(self):
        return bool(self.user and self.user.is_staff)


class SalarySlip(models.Model):
    MONTH_CHOICES = [(i, date(2000, i, 1).strftime("%B")) for i in range(1, 13)]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="salary_slips")
    month = models.PositiveSmallIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveSmallIntegerField()

    basic = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)

    slip_pdf = models.FileField(upload_to="salary_slips/%Y/%m/", blank=True, null=True)
    generated_on = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ("employee", "month", "year")
        ordering = ["-year", "-month"]

    def __str__(self):
        return f"{self.employee.employee_id} — {self.get_month_display()} {self.year}"

    def save(self, *args, **kwargs):
        self.net_pay = (self.basic or 0) + (self.hra or 0) + (self.allowances or 0) - (self.deductions or 0)
        super().save(*args, **kwargs)
