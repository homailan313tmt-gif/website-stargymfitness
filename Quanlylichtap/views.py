from django.shortcuts import render, get_object_or_404, redirect
from .models import BuoiTap, NhanXet, ThongBao, HinhAnhCamNhan, HinhAnhNhanXet, \
    KhachHang  # Đảm bảo KhachHang đã được import
from django.contrib.auth.decorators import login_required
from taikhoan.decorators import role_required
from taikhoan.models import HuanLuyenVien, KhachHang
from django.db.models import Q
from django.urls import reverse
# Nếu bạn cần dùng ngày tháng, hãy giữ các import này (tôi sẽ giữ lại chúng)
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_POST


# from django.db.models import Q # Đã đưa Q lên đầu

@login_required
@role_required('trainer')
def danh_sach_tap(request):
    # Lấy tham số GET
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    # Lấy danh sách buổi tập trước (để lọc giống logic cũ)
    ds_buoitap = BuoiTap.objects.select_related('hoc_vien__profile')

    # Lấy đối tượng HLV đang đăng nhập (từ Profile liên kết với request.user)
    try:
        hlv_dang_nhap = request.user.profile.huan_luyen_vien
    except HuanLuyenVien.DoesNotExist:
        # Nếu user là trainer nhưng chưa có đối tượng HLV (lỗi dữ liệu)
        hlv_dang_nhap = None

    if hlv_dang_nhap:
        # Chỉ lấy buổi tập của học viên có 'huan_luyen_vien' là HLV đang đăng nhập
        ds_buoitap = ds_buoitap.filter(hoc_vien__huan_luyen_vien=hlv_dang_nhap)
    else:
        # Ngăn không cho xem bất cứ buổi tập nào nếu không xác định được HLV
        ds_buoitap = BuoiTap.objects.none()

    # --- Lọc theo từ khóa ---
    if q:
        ds_buoitap = ds_buoitap.filter(
            Q(hoc_vien__profile__ho_ten__icontains=q) |
            Q(bai_tap__icontains=q)
        )

    # --- Lọc theo trạng thái ---
    if status:
        ds_buoitap = ds_buoitap.filter(trang_thai=status)

    # --- Lấy danh sách học viên DISTINCT (mỗi người 1 dòng) ---
    hoc_viens = (
        ds_buoitap
        .values('hoc_vien', 'hoc_vien__profile__ho_ten')
        .distinct()
        .order_by('hoc_vien__profile__ho_ten')
    )

    context = {
        'hoc_viens': hoc_viens,
        'q': q,
        'status': status,
    }
    return render(request, 'danh-sach-tap.html', context)


@login_required
@role_required('trainer')
def danh_sach_buoi_tap(request, hv_id):
    try:
        hlv_dang_nhap = request.user.profile.huan_luyen_vien
    except HuanLuyenVien.DoesNotExist:
        hlv_dang_nhap = None

    khach = get_object_or_404(KhachHang, id=hv_id, huan_luyen_vien=hlv_dang_nhap)

    # Lấy query params
    status = request.GET.get('status', '').strip()
    q = request.GET.get('q', '').strip()

    # Query gốc
    buoi_tap_list = BuoiTap.objects.filter(
        hoc_vien=khach
    ).order_by('-ngay_tap')

    # Lọc theo trạng thái
    if status:
        buoi_tap_list = buoi_tap_list.filter(trang_thai__icontains=status)

    # Lọc theo từ khóa
    if q:
        buoi_tap_list = buoi_tap_list.filter(
            Q(bai_tap__icontains=q) |
            Q(ghi_chu__icontains=q)
        )

    return render(request, 'danh-sach-buoi-tap.html', {
        'khach': khach,
        'buoi_tap_list': buoi_tap_list,
        'hv_id': hv_id,
        'status': status,
        'q': q,
    })


@login_required
@role_required('trainer')
def chi_tiet_tap(request, buoi_id, hv_id):
    try:
        hlv_dang_nhap = request.user.profile.huan_luyen_vien
    except HuanLuyenVien.DoesNotExist:
        hlv_dang_nhap = None

    buoi_tap = get_object_or_404(BuoiTap, id=buoi_id, hoc_vien__id=hv_id, hoc_vien__huan_luyen_vien=hlv_dang_nhap)

    # Lấy nhận xét nếu có
    nhan_xet = NhanXet.objects.filter(buoi_tap=buoi_tap).first()

    # Lịch sử tập luyện
    lich_su = BuoiTap.objects.filter(
        hoc_vien=buoi_tap.hoc_vien
    ).exclude(id=buoi_id).order_by('-ngay_tap')

    for item in lich_su:
        try:
            item.nx = NhanXet.objects.get(buoi_tap=item)
        except NhanXet.DoesNotExist:
            item.nx = None

    # Nhận xét cũ (nếu cần)
    nhan_xet_cu = NhanXet.objects.filter(
        buoi_tap__hoc_vien=buoi_tap.hoc_vien
    ).exclude(buoi_tap=buoi_tap).order_by('-ngay_nhan_xet')

    # === ẢNH CŨ CỦA NHẬN XÉT ===
    danh_sach_anh = HinhAnhNhanXet.objects.filter(nhan_xet=nhan_xet) if nhan_xet else []

    # ========================= POST: LƯU NHẬN XÉT =========================
    if request.method == 'POST':
        noi_dung = (request.POST.get('noi_dung') or '').strip()

        should_send_notification = False

        # Nếu xoá nội dung → xoá luôn nhận xét + ảnh
        if noi_dung == "":
            if nhan_xet:
                HinhAnhNhanXet.objects.filter(nhan_xet=nhan_xet).delete()
                nhan_xet.delete()
            return redirect('chi_tiet_tap', buoi_id=buoi_id, hv_id=hv_id)

        # Lưu hoặc tạo nhận xét
        if nhan_xet:
            if nhan_xet.noi_dung != noi_dung:
                nhan_xet.noi_dung = noi_dung
                nhan_xet.save()
                should_send_notification = True  # Nội dung cũ và mới khác nhau
        else:
            # Tạo mới nhận xét
            nhan_xet = NhanXet.objects.create(buoi_tap=buoi_tap, noi_dung=noi_dung)
            should_send_notification = True  # Luôn thông báo khi tạo mới

        # Thêm ảnh mới
        files = request.FILES.getlist('hinh_anh')
        for f in files:
            HinhAnhNhanXet.objects.create(nhan_xet=nhan_xet, anh=f)

        # Xoá ảnh cũ
        delete_ids = request.POST.get("delete_list", "")
        if delete_ids:
            ids = [x for x in delete_ids.split(",") if x.strip().isdigit()]
            if ids:
                HinhAnhNhanXet.objects.filter(id__in=ids).delete()

        if should_send_notification:
            khach_hang_nhan = buoi_tap.hoc_vien  # KhachHang instance (người nhận)

            # Lấy tên HLV từ profile
            hlv_ten = request.user.profile.display_name

            Tieu_de = f"HLV {hlv_ten} vừa gửi nhận xét mới!"
            Noi_dung = f"Nhận xét về buổi tập ngày {buoi_tap.ngay_tap} đã được cập nhật. Nhấn để xem."

            # BẮT ĐẦU KHỐI DEBUG TRY/EXCEPT TẠI ĐÂY
            try:
                # Tạo thông báo
                ThongBao.objects.create(
                    nguoi_nhan=khach_hang_nhan,
                    tieu_de=Tieu_de,
                    noi_dung=Noi_dung,
                )
                # In ra console để xác nhận thành công (CHỈ DEBUG)
                print(f"DEBUG: TẠO THÔNG BÁO THÀNH CÔNG cho KH: {khach_hang_nhan.id}")

            except Exception as e:
                # In ra console để thấy lỗi ngầm (CHỈ DEBUG)
                print(f"DEBUG LỖI: Không thể tạo thông báo cho KH {khach_hang_nhan.id}. Lỗi: {e}")
                # THÊM MỘT LỆNH THÔNG BÁO LỖI RÕ RÀNG HƠN TRÊN TRANG WEB
                from django.contrib import messages
                messages.error(request, f"Lỗi nội bộ khi gửi thông báo: {e}")
        # ====================================================================

        return redirect('chi_tiet_tap', buoi_id=buoi_id, hv_id=hv_id)

    # ========================= RENDER TEMPLATE =========================
    context = {
        'buoi_tap': buoi_tap,
        'nhan_xet': nhan_xet,
        'lich_su': lich_su,
        'nhan_xet_cu': nhan_xet_cu,

        # truyền đúng biến cho template
        'danh_sach_anh': danh_sach_anh,
        'hinh_anh_list': danh_sach_anh,
    }

    return render(request, 'chi-tiet-tap.html', context)


def lich_su_tap_luyen(request):
    # Lấy tham số từ form GET
    status = (request.GET.get('status') or '').strip()   # 'Đã hoàn thành' | 'Chưa tập' | ''
    q = (request.GET.get('q') or '').strip()             # từ khóa tìm kiếm

    # Lấy toàn bộ buổi tập (mới nhất trước)
    ds_buoitap = BuoiTap.objects.select_related('hoc_vien').order_by('-ngay_tap')

    # (Tùy chọn) Nếu muốn chỉ xem dữ liệu của học viên đang đăng nhập:
    if request.user.is_authenticated:
        # Lọc ds_buoitap theo đối tượng User (request.user)
        ds_buoitap = ds_buoitap.filter(hoc_vien__profile__user=request.user)

    # Chỉ nhận giá trị status hợp lệ theo choices của model
    valid_status = dict(BuoiTap._meta.get_field('trang_thai').choices).keys()
    if status in valid_status:
        ds_buoitap = ds_buoitap.filter(trang_thai=status)

    # Tìm kiếm theo tên bài tập (có thể mở rộng thêm ghi chú nếu có)
    if q:
        ds_buoitap = ds_buoitap.filter(Q(bai_tap__icontains=q))


    return render(request, 'lichsu_tap_luyen.html', {
        'ds_buoitap': ds_buoitap,
        'status': status,
        'q': q,
    })

@login_required
@role_required('customer')
def thong_tin_buoi_tap(request, buoi_id):
    buoi_tap = get_object_or_404(BuoiTap, id=buoi_id, hoc_vien__profile__user=request.user)
    return render(request, 'thongtin_buoi_tap.html', {'buoi_tap': buoi_tap})

from django.views.decorators.http import require_POST

@login_required
@role_required('customer')
def them_ghi_chu(request, buoi_id):
    bt = get_object_or_404(BuoiTap, id=buoi_id, hoc_vien__profile__user=request.user)

    if not bt.ngay_tap:
        from datetime import date
        bt.ngay_tap = date.today()
    # ===== POST: lưu ghi chú + ảnh =====
    if request.method == 'POST':
        bt.muc_ta = (request.POST.get('muc_ta') or '').strip() or None

        sh_raw = (request.POST.get('so_hiep') or '').strip()
        try:
            bt.so_hiep = int(sh_raw) if sh_raw != '' else None
        except ValueError:
            bt.so_hiep = None

        bt.cam_nhan = (request.POST.get('cam_nhan') or '').strip() or None
        bt.save()

        # lưu NHIỀU ảnh (nếu có)
        files = request.FILES.getlist('hinh_anh_cam_nhan')
        for f in files:
            HinhAnhCamNhan.objects.create(buoi_tap=bt, anh=f)

        return redirect(f"{request.path}?saved=1")
    # ===== GET: hiển thị =====
    saved = (request.GET.get('saved') == '1')
    deleted = (request.GET.get('deleted') == '1')
    edit_mode = (request.GET.get('edit') == '1')

    has_data = bool(
        bt.muc_ta or bt.so_hiep or bt.cam_nhan or bt.ds_anh_cam_nhan.exists()
    )
    show_view = (not edit_mode) and (saved or deleted or has_data)

    # 👉 LỊCH SỬ TẬP GẦN ĐÂY (5 buổi gần nhất của cùng học viên, trừ buổi hiện tại)
    lich_su_list = (BuoiTap.objects
                    .filter(hoc_vien=bt.hoc_vien)
                    .exclude(id=bt.id)
                    .order_by('-ngay_tap', '-id')[:5])

    return render(request, 'them_ghi_chu.html', {
        'buoi_tap': bt,
        'saved': saved,
        'deleted': deleted,
        'edit_mode': edit_mode,
        'has_data': has_data,
        'show_view': show_view,
        'lich_su_list': lich_su_list,   #  truyền cho template
    })

#đoạn ni nữa
from django.urls import reverse

@login_required
@role_required('customer')
def xoa_anh_cam_nhan(request, anh_id):
    # Tìm record ảnh, nếu không có thì quay lại trang trước
    anh = HinhAnhCamNhan.objects.filter(id=anh_id).first()
    if not anh:
        return redirect(request.META.get("HTTP_REFERER", reverse('danh_sach_tap')))

    buoi = anh.buoi_tap
    file_name = anh.anh.name  # đường dẫn file trong media (vd: cam_nhan/abc.png)

    # Xoá record trong DB trước
    anh.delete()

    # Kiểm tra còn record nào khác dùng chung file không
    still_used = HinhAnhCamNhan.objects.filter(anh=file_name).exists()

    # Nếu không còn ai dùng file này nữa thì mới xoá file vật lý
    if not still_used:
        from django.core.files.storage import default_storage
        if default_storage.exists(file_name):
            default_storage.delete(file_name)

    # Redirect về lại trang ghi chú ở chế độ edit
    return redirect(f"/lich-su/{buoi.id}/ghi-chu/?edit=1")

@require_POST
def xoa_ghi_chu(request, buoi_id):
    bt = get_object_or_404(BuoiTap, id=buoi_id)
    bt.muc_ta = None
    bt.so_hiep = None
    bt.cam_nhan = None
    bt.save()


from django.core.exceptions import ObjectDoesNotExist  # Import thêm để bắt lỗi truy cập Model


@login_required
def danh_sach_thong_bao(request):
    try:
        # Lấy đối tượng KhachHang liên kết với User đang đăng nhập
        khach_hang_nhan = request.user.profile.khach_hang
    except (AttributeError, ObjectDoesNotExist):
        # Nếu user không có profile hoặc profile không có KhachHang (vd: trainer, staff)
        # Chuyển hướng hoặc trả về danh sách rỗng để tránh lỗi
        return render(request, 'Quanlylichtap/thong-bao.html', {'ds_thong_bao': []})

    # LỌC THÔNG BÁO THEO KhachHang ĐÃ XÁC THỰC
    ds_thong_bao = ThongBao.objects.filter(nguoi_nhan=khach_hang_nhan).order_by('-thoi_gian')

    # === ĐÁNH DẤU ĐÃ ĐỌC (ẨN HUY HIỆU) ===
    # Chạy update trên database để đánh dấu tất cả thông báo chưa đọc là đã đọc
    ds_thong_bao.filter(is_read=False).update(is_read=True)

    # Sau khi update, bạn cần tải lại danh sách nếu bạn muốn hiển thị trạng thái is_read=True ngay lập tức
    # Tuy nhiên, ds_thong_bao đã là một QuerySet nên nó sẽ tự tải lại khi được lặp trong template

    # TRUYỀN DỮ LIỆU ĐÃ SỬA VÀO TEMPLATE
    return render(request, 'Quanlylichtap/thong-bao.html', {'ds_thong_bao': ds_thong_bao})