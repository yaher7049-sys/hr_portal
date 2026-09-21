from django.contrib import admin

from .models import Employee, SalarySlip


class SalarySlipInline(admin.TabularInline):
    model = SalarySlip
    extra = 1
    fields = ("month", "year", "basic", "hra", "allowances", "deductions", "net_pay", "slip_pdf")
    readonly_fields = ("net_pay",)


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "full_name", "department", "designation", "employment_type", "is_hr")
    list_filter = ("department", "employment_type", "gender", "work_location")
    search_fields = ("employee_id", "full_name", "office_email", "personal_email")
    inlines = [SalarySlipInline]
    fieldsets = (
        ("Account", {"fields": ("user", "employee_id", "full_name", "must_change_password")}),
        ("Role", {"fields": ("department", "designation", "employment_type", "reporting_manager_name",
                              "reporting_manager_email", "work_location")}),
        ("Personal", {"fields": ("gender", "marital_status", "date_of_birth", "blood_group",
                                  "education", "college_university_name")}),
        ("Employment", {"fields": ("date_of_joining", "notice_period_months", "years_of_experience",
                                    "experience_note")}),
        ("Contact", {"fields": ("contact_number", "personal_email", "office_email",
                                 "current_address", "permanent_address")}),
        ("Emergency contact", {"fields": ("emergency_contact_name", "emergency_contact_relationship",
                                           "emergency_contact_number")}),
        ("Statutory & bank (sensitive)", {"fields": ("aadhaar_no", "pan_card_no", "uan_no", "pf_number",
                                                       "esic_no", "bank_name", "bank_account_number",
                                                       "ifsc_code")}),
    )

    def is_hr(self, obj):
        return obj.is_hr
    is_hr.boolean = True


@admin.register(SalarySlip)
class SalarySlipAdmin(admin.ModelAdmin):
    list_display = ("employee", "month", "year", "net_pay", "generated_on")
    list_filter = ("year", "month")
    search_fields = ("employee__employee_id", "employee__full_name")
    readonly_fields = ("net_pay", "generated_on")
