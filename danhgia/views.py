from django.shortcuts import render, redirect
from django.contrib import messages
from .models import DanhGia
from .forms import DanhGiaForm

def review(request):
    da_gui = False  # cờ hiển thị "Đánh giá thành công!"

    if request.method == "POST":
        form = DanhGiaForm(request.POST)
        if form.is_valid():
            form.save()
            # dùng session để giữ trạng thái hiển thị
            request.session["da_gui"] = True
            return redirect("danh_gia")  # redirect để ngắt POST (chống F5 lặp)
    else:
        form = DanhGiaForm()

    # kiểm tra nếu vừa redirect sau khi gửi
    if request.session.pop("da_gui", False):
        da_gui = True

    danhgias = DanhGia.objects.all().order_by("-ngay_tao")

    context = {
        "form": form,
        "danhgias": danhgias,
        "da_gui": da_gui,
    }
    return render(request, "danhgia/review.html", context)
