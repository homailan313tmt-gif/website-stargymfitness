from django.shortcuts import redirect
from functools import wraps
from django.urls import reverse

def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            # Nếu chưa đăng nhập → chuyển về trang đăng nhập
            if not user.is_authenticated:
                return redirect("taikhoan:dang_nhap")

            # Lấy role từ Profile
            try:
                role = user.profile.role
            except Exception:
                return redirect("taikhoan:ho_so")

            # Nếu user không có đúng role được yêu cầu
            if role not in roles:
                # Tự điều hướng đến home đúng với vai trò
                role_redirects = {
                    "customer": "home_customer",
                    "trainer": "home_trainer",
                    "staff": "home_staff",
                }
                return redirect(reverse(role_redirects.get(role, "taikhoan:ho_so")))

            # :white_check_mark: Nếu hợp lệ → cho phép truy cập
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator