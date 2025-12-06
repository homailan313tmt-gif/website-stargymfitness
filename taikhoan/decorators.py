from django.shortcuts import redirect
from functools import wraps
from django.urls import reverse

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                return redirect("taikhoan:dang_nhap")

            try:
                role = user.profile.role
            except Exception:
                return redirect("taikhoan:ho_so")

            if role not in roles:
                role_redirects = {
                    "customer": "home_customer",
                    "trainer": "home_trainer",
                    "staff": "home_staff",
                }
                return redirect(reverse(role_redirects.get(role, "taikhoan:ho_so")))

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator