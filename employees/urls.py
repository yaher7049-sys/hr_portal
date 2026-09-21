from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_redirect, name="home"),

    # Auth
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("accounts/password_change/", views.ForcedPasswordChangeView.as_view(), name="password_change"),
    path(
        "accounts/password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(template_name="registration/password_change_done.html"),
        name="password_change_done",
    ),

    # Employee self-service
    path("me/", views.MyProfileView.as_view(), name="my-profile"),

    # HR
    path("hr/", views.HRDashboardView.as_view(), name="hr-dashboard"),
    path("hr/employee/<int:pk>/", views.EmployeeDetailView.as_view(), name="employee-detail"),
]
