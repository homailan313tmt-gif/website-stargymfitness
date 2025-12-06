from collections import Counter

from django.shortcuts import render, get_object_or_404, redirect
from hotro.models import PhanHoi


# =============================
#   TRANG THEO DÕI PHẢN HỒI
# =============================
def theo_doi(request):
    # Lấy toàn bộ phản hồi, mới nhất trước
    ds = PhanHoi.objects.all().order_by('-ngay_gui')

    # ===== TÍNH SỐ LẦN MỖI USER ĐÃ PHẢN HỒI =====
    # Lấy danh sách user_id của những phản hồi có gắn user
    user_id_list = ds.values_list('user_id', flat=True)
    user_id_list = [uid for uid in user_id_list if uid is not None]

    # Đếm số lần mỗi user đã phản hồi
    counts = Counter(user_id_list)   # {user_id: số_lần_phan_hoi}

    # Gắn thêm thuộc tính cho từng phản hồi để dùng trong template
    for ph in ds:
        if ph.user_id is None:
            # Khách lẻ (không đăng nhập): mỗi phản hồi xem như 1 lần, luôn là khách mới
            ph.so_lan_phan_hoi = 1
            ph.la_khach_moi = True
        else:
            ph.so_lan_phan_hoi = counts.get(ph.user_id, 0)
            ph.la_khach_moi = (ph.so_lan_phan_hoi == 1)
    # ============================================

    return render(request, 'traloikhachhang/theo-doi.html', {'ds': ds})


# ==================================
#   TRANG TRẢ LỜI 1 PHẢN HỒI
# ==================================
def tra_loi(request, pk):
    ph = get_object_or_404(PhanHoi, pk=pk)

    # ===== LỊCH SỬ PHẢN HỒI CỦA CÙNG USER =====
    if ph.user_id is not None:
        history = (
            PhanHoi.objects
            .filter(user_id=ph.user_id)
            .exclude(pk=ph.pk)
            .order_by('-ngay_gui')
        )
    else:
        # Nếu phản hồi không gắn user (ẩn danh) thì không có lịch sử
        history = PhanHoi.objects.none()

    first_time = not history.exists()
    # ==========================================

    if request.method == 'POST':
        ph.trang_thai = request.POST.get('trang_thai')
        ph.tra_loi = request.POST.get('tra_loi')
        ph.save()

        # ⭐ KHÔNG redirect nữa → trả về lại trang tra-loi cùng thông báo
        return render(request, 'traloikhachhang/tra-loi.html', {
            'ph': ph,
            'history': history,
            'first_time': first_time,
            'updated': True  # ⭐ biến báo lưu thành công
        })

    context = {
        'ph': ph,
        'history': history,
        'first_time': first_time,
    }
    return render(request, 'traloikhachhang/tra-loi.html', context)


# ==================================
#   TRANG SAU KHI TRẢ LỜI THÀNH CÔNG
# ==================================
def tra_loi_thanh_cong(request, pk):
    ph = get_object_or_404(PhanHoi, pk=pk)
    return render(request, 'traloikhachhang/thanh-cong.html', {'ph': ph})
