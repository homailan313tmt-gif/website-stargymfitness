from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.files.storage import default_storage

from taikhoan.decorators import role_required
from .models import PhanHoi, AnhPhanHoi
from .forms import PhanHoiForm


# =======================
# GỬI PHẢN HỒI
# =======================
@login_required
@role_required('customer')
def gui_phan_hoi(request):
    da_gui = False

    if request.method == 'POST':
        form = PhanHoiForm(request.POST, request.FILES)

        if form.is_valid():
            ph = form.save(commit=False)
            ph.user = request.user
            ph.save()

            # Lưu nhiều ảnh
            for f in request.FILES.getlist('anh'):
                AnhPhanHoi.objects.create(phan_hoi=ph, anh=f)

            request.session['da_gui'] = True
            return redirect('gui_phan_hoi')

    else:
        form = PhanHoiForm()

    if request.session.pop('da_gui', False):
        da_gui = True

    return render(request, 'hotro/gui.html', {
        'form': form,
        'da_gui': da_gui
    })



# =======================
# THEO DÕI
# =======================
@login_required
@role_required('customer')
def theo_doi(request):
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    ds = PhanHoi.objects.filter(user=request.user)

    if q:
        ds = ds.filter(Q(noi_dung__icontains=q) | Q(tra_loi__icontains=q))

    if status == 'Đã xử lý':
        ds = ds.exclude(tra_loi__isnull=True).exclude(tra_loi__exact='')
    elif status == 'Chưa xử lý':
        ds = ds.filter(Q(tra_loi__isnull=True) | Q(tra_loi__exact=''))

    ds = ds.order_by('-ngay_gui')

    return render(request, 'hotro/theodoi.html', {
        'ds': ds,
        'q': q,
        'status': status,
    })


# =======================
# CHI TIẾT PHẢN HỒI
# =======================
@login_required
@role_required('customer')
def chi_tiet(request, pk):
    ph = get_object_or_404(PhanHoi, pk=pk)
    return render(request, 'hotro/chitiet.html', {'ph': ph})


# =======================
# CHỈNH SỬA PHẢN HỒI
# =======================
@login_required
@role_required('customer')
def chinh_sua(request, pk):
    ph = get_object_or_404(PhanHoi, pk=pk)

    # Không cho sửa phản hồi của người khác
    if ph.user != request.user:
        return redirect("theo_doi")

    if request.method == "POST":
        form = PhanHoiForm(request.POST, request.FILES, instance=ph)

        if form.is_valid():
            form.save()

            # =============================
            # 🔥 XÓA ẢNH CŨ
            # =============================
            delete_str = request.POST.get("delete_list", "")
            delete_ids = [x for x in delete_str.split(",") if x.strip().isdigit()]

            for img_id in delete_ids:
                try:
                    img = AnhPhanHoi.objects.get(id=img_id)

                    # Xóa file thật trong media
                    if img.anh and default_storage.exists(img.anh.name):
                        default_storage.delete(img.anh.name)

                    img.delete()

                except AnhPhanHoi.DoesNotExist:
                    pass

            # =============================
            # 🔥 LƯU ẢNH MỚI
            # =============================
            for f in request.FILES.getlist("anh"):
                AnhPhanHoi.objects.create(phan_hoi=ph, anh=f)

            return redirect("chi_tiet", ph.id)

    else:
        form = PhanHoiForm(instance=ph)

    return render(request, "hotro/chinhsua.html", {
        "form": form,
        "ph": ph,
    })
