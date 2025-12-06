from django.shortcuts import render
from Quanlylichtap.models import *
from django.contrib.auth.decorators import login_required
from taikhoan.decorators import role_required
from taikhoan.models import HuanLuyenVien, KhachHang
from django.db.models import Q
# Create your views here.
def home(request):
    return render(request, 'home.html')

@login_required
def danh_sach_thong_bao(request):
    ds_thong_bao = ThongBao.objects.none()
    if request.user.is_authenticated:
        try:
            khach_hang_nhan = request.user.profile.khach_hang

            ds_thong_bao = ThongBao.objects.filter(
                nguoi_nhan=khach_hang_nhan
            ).order_by('-thoi_gian')

        except Exception:
            pass
    return render(request, 'thong-bao.html', {'ds_thong_bao': ds_thong_bao})