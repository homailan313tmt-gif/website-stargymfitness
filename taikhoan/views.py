# taikhoan/views.py
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import FormDangKy, FormDangNhap, FormHoSo, FormKhoaTaiKhoan
from .models import Profile

BASE_TEMPLATES = {
    "customer": "base-customer.html",
    "trainer": "base-trainer.html",
    "staff": "base-staff.html"
}


def dang_nhap(request):
    if request.user.is_authenticated:
        return redirect("taikhoan:ho_so")

    if request.method == "POST":
        form = FormDangNhap(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.is_active:
                messages.error(request, "Tài khoản đã bị khóa.")
                return redirect("taikhoan:dang_nhap")

            login(request, user)
            p = Profile.ensure_for(user)
            request.session["role"] = p.role
            return redirect("taikhoan:ho_so")
    else:
        form = FormDangNhap()

    return render(request, "nguoidung/dang_nhap.html", {"form": form})


def dang_ky(request):
    if request.user.is_authenticated:
        return redirect("taikhoan:ho_so")

    if request.method == "POST":
        form = FormDangKy(request.POST)
        if form.is_valid():
            user = form.save()
            p = Profile.ensure_for(user)
            login(request, user)
            request.session["role"] = p.role
            messages.success(request, "Đăng ký thành công.")
            return redirect("taikhoan:ho_so")
    else:
        form = FormDangKy()

    return render(request, "taikhoan/dang_ky.html", {"form": form})


@login_required
def dang_xuat(request):
    logout(request)
    return redirect("taikhoan:dang_nhap")


@login_required
def ho_so_xem(request):
    p = Profile.ensure_for(request.user)
    return render(request, "taikhoan/ho_so_xem.html", {
        "p": type('obj', (), p.to_dict())(),
        "base": BASE_TEMPLATES.get(p.role, "base-customer.html")
    })


@login_required
def ho_so_sua(request):
    p = Profile.ensure_for(request.user)

    if request.method == "POST":
        form = FormHoSo(role=p.role, data=request.POST)
        if form.is_valid():
            p.update_info(form.cleaned_data, request.FILES)
            p.update_role_data(p.role, form.cleaned_data)
            messages.success(request, "Đã lưu thay đổi hồ sơ.")
            return redirect("taikhoan:ho_so")
        messages.error(request, "Dữ liệu không hợp lệ.")
    else:
        form = FormHoSo(role=p.role, initial=p.to_dict())

    return render(request, "taikhoan/ho_so_sua.html", {
        "p": type('obj', (), p.to_dict())(),
        "base": BASE_TEMPLATES.get(p.role, "base-customer.html"),
        "form": form
    })


@login_required
def khoa_tai_khoan(request):
    p = Profile.ensure_for(request.user)

    if request.method == "POST":
        form = FormKhoaTaiKhoan(request.POST)
        if form.is_valid():
            request.user.is_active = False
            request.user.save(update_fields=["is_active"])

            p.ly_do_khoa = form.cleaned_data["ly_do"]
            p.khoa_luc = timezone.now()
            p.save(update_fields=["ly_do_khoa", "khoa_luc"])

            logout(request)
            messages.success(request, "Khóa tài khoản thành công.")
            return redirect("taikhoan:dang_nhap")
        messages.error(request, "Vui lòng nhập lý do hợp lệ.")
    else:
        form = FormKhoaTaiKhoan()

    return render(request, "taikhoan/khoa_tai_khoan.html", {
        "form": form,
        "base": BASE_TEMPLATES.get(p.role, "base-customer.html")
    })


@login_required
def tai_anh_dai_dien(request):
    if request.method == "POST":
        p = Profile.ensure_for(request.user)
        if f := request.FILES.get("anh_dai_dien") or request.FILES.get("avatar"):
            p.anh_dai_dien = f
            p.save(update_fields=["anh_dai_dien"])
            messages.success(request, "Đã cập nhật ảnh đại diện.")
            return redirect("taikhoan:ho_so")
        messages.error(request, "Vui lòng chọn tệp ảnh hợp lệ.")
    return redirect("taikhoan:ho_so_sua")