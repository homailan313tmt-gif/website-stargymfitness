from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from taikhoan.models import *



class BuoiTap(models.Model):
    hoc_vien = models.ForeignKey(KhachHang, on_delete=models.CASCADE)
    ngay_tap = models.DateField()
    bai_tap = models.CharField(max_length=100)
    trang_thai = models.CharField(
        max_length=50,
        choices=[('Đã hoàn thành', 'Đã hoàn thành'),
                 ('Chưa hoàn thành', 'Chưa hoàn thành')],
        default='Chưa hoàn thành'
    )
    muc_ta = models.CharField(max_length=100, null=True, blank=True)
    so_hiep = models.IntegerField(null=True, blank=True)
    cam_nhan = models.TextField(null=True, blank=True)

    def __str__(self):
        # Kiểm tra profile tồn tại trước khi dùng ho_ten
        if self.hoc_vien.profile:
            ten_hoc_vien = self.hoc_vien.profile.ho_ten or "Chưa đặt tên"
        else:
            ten_hoc_vien = "Chưa có profile"
        return f"{ten_hoc_vien} - {self.ngay_tap}"



class NhanXet(models.Model):
    buoi_tap = models.OneToOneField(BuoiTap, on_delete=models.CASCADE)
    noi_dung = models.TextField(blank=True, null=True)
    ngay_nhan_xet = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Nhận xét cho {self.buoi_tap}"

class HinhAnhCamNhan(models.Model):
    buoi_tap = models.ForeignKey(
        BuoiTap,
        on_delete=models.CASCADE,
        related_name='ds_anh_cam_nhan'  # để dễ gọi trong template
    )
    anh = models.ImageField(upload_to='cam_nhan/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ảnh cảm nhận - {self.buoi_tap.id}"


class HinhAnhNhanXet(models.Model):
    nhan_xet = models.ForeignKey(NhanXet, on_delete=models.CASCADE, related_name='hinh_anh')
    anh = models.ImageField(upload_to='nhan_xet_hlv/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Hình nhận xét {self.id}"

class ThongBao(models.Model):
    nguoi_nhan = models.ForeignKey(KhachHang, on_delete=models.CASCADE)
    tieu_de = models.CharField(max_length=255)
    noi_dung = models.TextField()
    thoi_gian = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-thoi_gian']
        verbose_name = "Thông báo"
        verbose_name_plural = "Thông báo"

    def __str__(self):
        ten_khach_hang = self.nguoi_nhan.profile.ho_ten or "Khách hàng ẩn danh"
        return f"{self.tieu_de} - {ten_khach_hang}"
