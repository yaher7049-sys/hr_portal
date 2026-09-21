from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView

from .models import Employee


def is_hr(user):
    return user.is_authenticated and user.is_staff


@login_required
def home_redirect(request):
    """Send HR to the dashboard, everyone else to their own profile."""
    if is_hr(request.user):
        return redirect("hr-dashboard")
    return redirect("my-profile")


class MyProfileView(LoginRequiredMixin, TemplateView):
    """An employee's view of their own record — never anyone else's."""
    template_name = "employees/my_profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee = get_object_or_404(Employee, user=self.request.user)
        context["employee"] = employee
        context["salary_slips"] = employee.salary_slips.all()
        return context


class HRDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """HR's roster view — searchable and filterable, links out to full detail."""
    model = Employee
    template_name = "employees/hr_dashboard.html"
    context_object_name = "employees"
    paginate_by = 25

    def test_func(self):
        return is_hr(self.request.user)

    def get_queryset(self):
        qs = Employee.objects.all()
        q = self.request.GET.get("q", "").strip()
        department = self.request.GET.get("department", "").strip()
        employment_type = self.request.GET.get("type", "").strip()

        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(full_name__icontains=q)
                | Q(employee_id__icontains=q)
                | Q(designation__icontains=q)
            )
        if department:
            qs = qs.filter(department=department)
        if employment_type:
            qs = qs.filter(employment_type=employment_type)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["departments"] = (
            Employee.objects.exclude(department__isnull=True)
            .values_list("department", flat=True)
            .distinct()
            .order_by("department")
        )
        context["query"] = self.request.GET.get("q", "")
        context["selected_department"] = self.request.GET.get("department", "")
        context["selected_type"] = self.request.GET.get("type", "")
        context["total_count"] = Employee.objects.count()
        return context


class EmployeeDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """HR's full-detail view of one employee — every field, plus salary slips."""
    model = Employee
    template_name = "employees/employee_detail.html"
    context_object_name = "employee"

    def test_func(self):
        return is_hr(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["salary_slips"] = self.object.salary_slips.all()
        return context


class ForcedPasswordChangeView(PasswordChangeView):
    """Same as Django's built-in view, but also clears the must_change_password flag."""
    template_name = "registration/password_change.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        response = super().form_valid(form)
        profile = getattr(self.request.user, "employee_profile", None)
        if profile:
            profile.must_change_password = False
            profile.save(update_fields=["must_change_password"])
        return response
