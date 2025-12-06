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



@login_required
@role_required('trainer')
def danh_sach_tap(request):
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()

    ds_buoitap = BuoiTap.objects.select_related('hoc_vien__profile')

    try:
        hlv_dang_nhap = request.user.profile.huan_luyen_vien
    except HuanLuyenVien.DoesNotExist:
        hlv_dang_nhap = None

    if hlv_dang_nhap:
        ds_buoitap = ds_buoitap.filter(hoc_vien__huan_luyen_vien=hlv_dang_nhap)
    else:
        ds_buoitap = BuoiTap.objects.none()

    if q:
        ds_buoitap = ds_buoitap.filter(
            Q(hoc_vien__profile__ho_ten__icontains=q) |
            Q(bai_tap__icontains=q)
        )

    if status:
        ds_buoitap = ds_buoitap.filter(trang_thai=status)

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

    status = request.GET.get('status', '').strip()
    q = request.GET.get('q', '').strip()

    buoi_tap_list = BuoiTap.objects.filter(
        hoc_vien=khach
    ).order_by('-ngay_tap')

    if status:
        buoi_tap_list = buoi_tap_list.filter(trang_thai__icontains=status)

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

    nhan_xet = NhanXet.objects.filter(buoi_tap=buoi_tap).first()

    lich_su = BuoiTap.objects.filter(
        hoc_vien=buoi_tap.hoc_vien
    ).exclude(id=buoi_id).order_by('-ngay_tap')

    for item in lich_su:
        try:
            item.nx = NhanXet.objects.get(buoi_tap=item)
        except NhanXet.DoesNotExist:
            item.nx = None

    nhan_xet_cu = NhanXet.objects.filter(
        buoi_tap__hoc_vien=buoi_tap.hoc_vien
    ).exclude(buoi_tap=buoi_tap).order_by('-ngay_nhan_xet')

    danh_sach_anh = HinhAnhNhanXet.objects.filter(nhan_xet=nhan_xet) if nhan_xet else []

    if request.method == 'POST':
        noi_dung = (request.POST.get('noi_dung') or '').strip()

        should_send_notification = False

        if noi_dung == "":
            if nhan_xet:
                HinhAnhNhanXet.objects.filter(nhan_xet=nhan_xet).delete()
                nhan_xet.delete()
            return redirect('chi_tiet_tap', buoi_id=buoi_id, hv_id=hv_id)

        if nhan_xet:
            if nhan_xet.noi_dung != noi_dung:
                nhan_xet.noi_dung = noi_dung
                nhan_xet.save()
                should_send_notification = True
        else:
            nhan_xet = NhanXet.objects.create(buoi_tap=buoi_tap, noi_dung=noi_dung)
            should_send_notification = True

        files = request.FILES.getlist('hinh_anh')
        for f in files:
            HinhAnhNhanXet.objects.create(nhan_xet=nhan_xet, anh=f)

        delete_ids = request.POST.get("delete_list", "")
        if delete_ids:
            ids = [x for x in delete_ids.split(",") if x.strip().isdigit()]
            if ids:
                HinhAnhNhanXet.objects.filter(id__in=ids).delete()

        if should_send_notification:
            khach_hang_nhan = buoi_tap.hoc_vien

            hlv_ten = request.user.profile.display_name

            Tieu_de = f"HLV {hlv_ten} vừa gửi nhận xét mới!"
            Noi_dung = f"Nhận xét về buổi tập ngày {buoi_tap.ngay_tap} đã được cập nhật. Nhấn để xem."

            try:
                ThongBao.objects.create(
                    nguoi_nhan=khach_hang_nhan,
                    tieu_de=Tieu_de,
                    noi_dung=Noi_dung,
                )

                print(f"DEBUG: TẠO THÔNG BÁO THÀNH CÔNG cho KH: {khach_hang_nhan.id}")

            except Exception as e:
                print(f"DEBUG LỖI: Không thể tạo thông báo cho KH {khach_hang_nhan.id}. Lỗi: {e}")
                from django.contrib import messages
                messages.error(request, f"Lỗi nội bộ khi gửi thông báo: {e}")

        return redirect('chi_tiet_tap', buoi_id=buoi_id, hv_id=hv_id)

    context = {
        'buoi_tap': buoi_tap,
        'nhan_xet': nhan_xet,
        'lich_su': lich_su,
        'nhan_xet_cu': nhan_xet_cu,

        'danh_sach_anh': danh_sach_anh,
        'hinh_anh_list': danh_sach_anh,
    }

    return render(request, 'chi-tiet-tap.html', context)


def lich_su_tap_luyen(request):
    status = (request.GET.get('status') or '').strip()
    q = (request.GET.get('q') or '').strip()

    ds_buoitap = BuoiTap.objects.select_related('hoc_vien').order_by('-ngay_tap')

    if request.user.is_authenticated:
        ds_buoitap = ds_buoitap.filter(hoc_vien__profile__user=request.user)

    valid_status = dict(BuoiTap._meta.get_field('trang_thai').choices).keys()
    if status in valid_status:
        ds_buoitap = ds_buoitap.filter(trang_thai=status)

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

    if request.method == 'POST':
        bt.muc_ta = (request.POST.get('muc_ta') or '').strip() or None

        sh_raw = (request.POST.get('so_hiep') or '').strip()
        try:
            bt.so_hiep = int(sh_raw) if sh_raw != '' else None
        except ValueError:
            bt.so_hiep = None

        bt.cam_nhan = (request.POST.get('cam_nhan') or '').strip() or None
        bt.save()


        files = request.FILES.getlist('hinh_anh_cam_nhan')
        for f in files:
            HinhAnhCamNhan.objects.create(buoi_tap=bt, anh=f)

        return redirect(f"{request.path}?saved=1")

    saved = (request.GET.get('saved') == '1')
    deleted = (request.GET.get('deleted') == '1')
    edit_mode = (request.GET.get('edit') == '1')

    has_data = bool(
        bt.muc_ta or bt.so_hiep or bt.cam_nhan or bt.ds_anh_cam_nhan.exists()
    )
    show_view = (not edit_mode) and (saved or deleted or has_data)

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
        'lich_su_list': lich_su_list,
    })

from django.urls import reverse

@login_required
@role_required('customer')
def xoa_anh_cam_nhan(request, anh_id):
    anh = HinhAnhCamNhan.objects.filter(id=anh_id).first()
    if not anh:
        return redirect(request.META.get("HTTP_REFERER", reverse('danh_sach_tap')))

    buoi = anh.buoi_tap
    file_name = anh.anh.name
    anh.delete()

    still_used = HinhAnhCamNhan.objects.filter(anh=file_name).exists()

    if not still_used:
        from django.core.files.storage import default_storage
        if default_storage.exists(file_name):
            default_storage.delete(file_name)

    return redirect(f"/lich-su/{buoi.id}/ghi-chu/?edit=1")

@require_POST
def xoa_ghi_chu(request, buoi_id):
    bt = get_object_or_404(BuoiTap, id=buoi_id)
    bt.muc_ta = None
    bt.so_hiep = None
    bt.cam_nhan = None
    bt.save()


from django.core.exceptions import ObjectDoesNotExist


@login_required
def danh_sach_thong_bao(request):
    try:

        khach_hang_nhan = request.user.profile.khach_hang
    except (AttributeError, ObjectDoesNotExist):

        return render(request, 'Quanlylichtap/thong-bao.html', {'ds_thong_bao': []})

    ds_thong_bao = ThongBao.objects.filter(nguoi_nhan=khach_hang_nhan).order_by('-thoi_gian')

    ds_thong_bao.filter(is_read=False).update(is_read=True)
    return render(request, 'Quanlylichtap/thong-bao.html', {'ds_thong_bao': ds_thong_bao})