from django.db import models
from hotro.models import PhanHoi

class TraLoiKhachHang(models.Model):
    phan_hoi = models.OneToOneField(
        PhanHoi,
        on_delete=models.CASCADE,
        related_name='tra_loi_khachhang'  # đổi tên này để tránh trùng
    )
    noi_dung_tra_loi = models.TextField("Nội dung trả lời")
    ngay_tra_loi = models.DateTimeField(auto_now_add=True)
    nguoi_tra_loi = models.CharField(max_length=100)

    def __str__(self):
        return f"Trả lời cho phản hồi #{self.phan_hoi.id}"
