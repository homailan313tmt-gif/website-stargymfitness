from django.db import models
from taikhoan.models import *
from django.contrib.auth.models import User


class DanhGia(models.Model):
    khach_hang = models.ForeignKey(KhachHang, on_delete=models.CASCADE)
    nguoi_tao = models.ForeignKey(Profile, on_delete=models.SET_NULL, null=True)
    danh_gia_chung = models.IntegerField(default=0)
    thai_do_phuc_vu = models.IntegerField(default=0)
    chat_luong_dich_vu = models.IntegerField(default=0)
    nhan_xet = models.TextField(blank=True, null=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return f"Đánh giá {self.id} - {self.ngay_tao.strftime('%d/%m/%Y')}"


class DanhGiaImage(models.Model):
    danh_gia = models.ForeignKey(
        DanhGia,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='danhgia/')

    def __str__(self):
        return f"Ảnh đánh giá {self.id}"