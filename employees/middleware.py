from django.shortcuts import redirect
from django.urls import reverse

# Paths a logged-in user must still reach even if they're forced to change their password.
EXEMPT_PATH_NAMES = {"password_change", "password_change_done", "logout"}


class ForcePasswordChangeMiddleware:
    """
    Employee accounts are created by HR with a default password (their employee ID).
    This middleware blocks access to everything else until they set a real password.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            profile = getattr(user, "employee_profile", None)
            if profile and profile.must_change_password:
                exempt_paths = {reverse(name) for name in EXEMPT_PATH_NAMES}
                if request.path not in exempt_paths and not request.path.startswith("/admin/"):
                    return redirect("password_change")
        return self.get_response(request)
