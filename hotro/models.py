
from django.db import models
from django.conf import settings
from taikhoan.models import KhachHang, NhanVien

class PhanHoi(models.Model):
    LOAI_PHAN_HOI = [
        ('Khiếu nại', 'Khiếu nại'),
        ('Góp ý', 'Góp ý'),
        ('Thắc mắc', 'Thắc mắc'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    loai = models.CharField(max_length=50, choices=LOAI_PHAN_HOI)
    noi_dung = models.TextField()
    trang_thai = models.CharField(max_length=20, default='Chưa xử lý')
    tra_loi = models.TextField(blank=True, null=True)
    ngay_gui = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.loai}"

class AnhPhanHoi(models.Model):
    phan_hoi = models.ForeignKey(PhanHoi, on_delete=models.CASCADE, related_name="ds_anh")
    anh = models.ImageField(upload_to='phanhoi/', blank=True, null=True)



