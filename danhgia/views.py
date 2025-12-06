from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from taikhoan.decorators import role_required
from .models import DanhGia, DanhGiaImage
from .forms import DanhGiaForm
from taikhoan.models import KhachHang


@login_required
@role_required('customer')
def review(request):
    da_gui = False

    # Lấy hoặc tạo khách hàng từ profile
    kh, _ = KhachHang.objects.get_or_create(profile=request.user.profile)

    if request.method == "POST":
        form = DanhGiaForm(request.POST)

        if form.is_valid():
            # Lưu đánh giá trước
            dg = form.save(commit=False)
            dg.khach_hang = kh
            dg.user = request.user
            dg.nguoi_tao = request.user.profile
            dg.save()

            # ----- LƯU NHIỀU ẢNH -----
            images = request.FILES.getlist("anh_minh_chung")
            for img in images:
                DanhGiaImage.objects.create(danh_gia=dg, image=img)

            request.session["da_gui"] = True
            return redirect("danh_gia")

    else:
        form = DanhGiaForm()

    if request.session.pop("da_gui", False):
        da_gui = True

    danhgias = DanhGia.objects.all().order_by("-ngay_tao")

    return render(request, "danhgia/review.html", {
        "form": form,
        "danhgias": danhgias,
        "da_gui": da_gui,
    })
