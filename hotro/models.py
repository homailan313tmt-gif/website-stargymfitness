
from django.db import models
from django.contrib.auth.models import User

class PhanHoi(models.Model):
    LOAI_PHAN_HOI = [
        ('Khiếu nại', 'Khiếu nại'),
        ('Góp ý', 'Góp ý'),
        ('Thắc mắc', 'Thắc mắc'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    loai = models.CharField(max_length=50, choices=LOAI_PHAN_HOI)
    noi_dung = models.TextField()
    trang_thai = models.CharField(max_length=20, default='Chưa xử lý')
    tra_loi = models.TextField(blank=True, null=True)
    ngay_gui = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.loai}"
