# bao_cao/views.py
from datetime import date, timedelta, datetime
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from functools import wraps
from taikhoan.models import Profile

def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("taikhoan:dang_nhap")

        p = Profile.ensure_for(request.user)
        if p.role != "staff":
            messages.error(request, "Bạn không có quyền truy cập trang này.")
            return redirect("taikhoan:ho_so")

        return view_func(request, *args, **kwargs)
    return wrapper

def _require_staff(request):
    return request.user.is_authenticated and Profile.ensure_for(request.user).role == "staff"

def _base_for(role):
    return {"customer": "base-customer.html", "trainer": "base-trainer.html", "staff": "base-staff.html"}.get(role,
                                                                                                              "base-staff.html")
def fmt_dt(dt):
    if not dt:
        return "—"
    if isinstance(dt, datetime):
        return dt.strftime("%d/%m/%Y %H:%M")
    if isinstance(dt, date):
        return dt.strftime("%d/%m/%Y")
    return str(dt)


def _get_customers_by_type(loai):
    """Lấy queryset khách hàng theo loại"""
    customers = User.objects.filter(profile__role="customer").select_related("profile", "profile__khach_hang")

    if loai == "moi":
        return customers.filter(date_joined__date__gte=date.today() - timedelta(days=29))
    elif loai == "duy_tri":
        return customers.filter(is_active=True)
    else:  # da_khoa
        return customers.filter(is_active=False)


def _get_customer_counts():
    """Đếm số lượng khách hàng theo loại"""
    base = User.objects.filter(profile__role="customer")
    return {
        "tong_moi": base.filter(date_joined__date__gte=date.today() - timedelta(days=29)).count(),
        "tong_duy_tri": base.filter(is_active=True).count(),
        "tong_da_khoa": base.filter(is_active=False).count(),
    }


@login_required
@staff_required
def bao_cao_khach_hang(request):
    p = Profile.ensure_for(request.user)
    loai = request.GET.get("loai", "moi")
    search = request.GET.get("search", "").strip()

    customers = _get_customers_by_type(loai)
    if search:
        customers = customers.filter(
            Q(username__icontains=search) |
            Q(profile__ho_ten__icontains=search) |
            Q(email__icontains=search)
        )

    customers = customers.order_by("-profile__khoa_luc" if loai == "da_khoa" else "-date_joined")

    ds_khach = []
    for u in customers[:100]:
        p_u = u.profile
        ds_khach.append({
            "id": u.id,
            "username": u.username,
            "ho_ten": p_u.ho_ten or u.get_full_name() or u.username,
            "email": u.email or "—",
            "ngay_dang_ky": fmt_dt(u.date_joined.date()),
            "khoa_luc": fmt_dt(p_u.khoa_luc) if p_u.khoa_luc else "—",
            "ly_do_khoa": p_u.ly_do_khoa or "—",
        })

    titles = {"moi": "Khách hàng mới", "duy_tri": "Khách hàng đang hoạt động", "da_khoa": "Khách hàng đã khóa"}

    return render(request, "bao_cao/bao_cao_khach_hang.html", {
        "base": _base_for(p.role),
        "loai": loai,
        "search": search,
        "title": titles.get(loai, "Báo cáo khách hàng"),
        "ds_khach": ds_khach,
        **_get_customer_counts(),
    })

@login_required
@staff_required
def bao_cao_khach_hang_csv(request):
    loai = request.GET.get("loai", "moi")
    customers = _get_customers_by_type(loai)

    import csv, io
    buf = io.StringIO()
    w = csv.writer(buf)

    headers = ["STT", "Username", "Ho ten", "Email", "Ngay dang ky"]
    if loai == "da_khoa":
        headers.extend(["Ngay khoa", "Ly do khoa"])
    w.writerow(headers)

    for idx, u in enumerate(customers, 1):
        p = u.profile
        row = [
            idx, u.username,
            p.ho_ten or u.get_full_name() or u.username,
            u.email or "",
            fmt_dt(u.date_joined.date())
        ]
        if loai == "da_khoa":
            row.extend([
                fmt_dt(p.khoa_luc) if p.khoa_luc else "",
                p.ly_do_khoa or ""
            ])
        w.writerow(row)

    csv_data = '\ufeff' + buf.getvalue()
    resp = HttpResponse(csv_data.encode('utf-8'), content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename=khach_hang_{loai}.csv'
    return resp
@login_required
@staff_required
def khach_hang_chi_tiet(request, user_id: int):
    p_staff = Profile.ensure_for(request.user)
    u = get_object_or_404(User.objects.select_related("profile", "profile__khach_hang"), pk=user_id,
                          profile__role="customer")
    p = u.profile
    kh = getattr(p, "khach_hang", None)

    return render(request, "bao_cao/khach_hang_chi_tiet.html", {
        "base": _base_for(p_staff.role),
        "u": u,
        "p": {
            "username": u.username,
            "ho_ten": p.ho_ten or u.get_full_name() or u.username,
            "email": u.email or "",
            "so_dien_thoai": p.so_dien_thoai or "",
            "avatar_url": p.anh_dai_dien.url if p.anh_dai_dien else "",
            "is_active": u.is_active,
            "date_joined_txt": fmt_dt(u.date_joined),
            "last_login_txt": fmt_dt(u.last_login),
            "khoa_luc_txt": fmt_dt(p.khoa_luc),
            "ly_do_khoa": p.ly_do_khoa or "",
            "muc_tieu": kh.muc_tieu if kh else "",
            "chieu_cao_cm": kh.chieu_cao_cm if kh else "",
            "can_nang_kg": kh.can_nang_kg if kh else "",
        },
    })