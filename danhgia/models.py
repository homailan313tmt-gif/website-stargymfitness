from django.db import models
from django.utils import timezone

class DanhGia(models.Model):
    danh_gia_chung = models.IntegerField(default=0)
    thai_do_phuc_vu = models.IntegerField(default=0)
    chat_luong_dich_vu = models.IntegerField(default=0)
    nhan_xet = models.TextField(blank=True, null=True)
    ngay_tao = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"Đánh giá {self.id} - {self.ngay_tao.strftime('%d/%m/%Y')}"
