from django.db import models
from django.conf import settings
from pathlib import Path
import uuid


def profile_avatar_path(instance, filename):
    ext = Path(filename).suffix.lower()
    return f"avatars/{instance.user_id}/{uuid.uuid4().hex}{ext}"


class Profile(models.Model):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Khách hàng"
        TRAINER = "trainer", "Huấn luyện viên"
        STAFF = "staff", "Nhân viên"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    ho_ten = models.CharField(max_length=150, blank=True)
    so_dien_thoai = models.CharField(max_length=20, blank=True)
    anh_dai_dien = models.ImageField(upload_to=profile_avatar_path, blank=True, null=True)

    # Thông tin khóa
    ly_do_khoa = models.CharField(max_length=255, blank=True)
    khoa_luc = models.DateTimeField(null=True, blank=True)
    khoa_boi = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                 on_delete=models.SET_NULL, related_name="da_khoa")

    def __str__(self):
        return self.ho_ten or self.user.get_username()

    @classmethod
    def ensure_for(cls, user):
        obj, _ = cls.objects.get_or_create(user=user, defaults={"role": cls.Role.CUSTOMER})
        return obj

    @property
    def display_name(self):
        """Tên hiển thị"""
        return self.ho_ten or self.user.get_full_name() or self.user.username

    @property
    def avatar_url(self):
        """URL avatar"""
        try:
            return self.anh_dai_dien.url if self.anh_dai_dien else ""
        except:
            return ""

    def update_info(self, data, files=None):
        """Cập nhật thông tin profile"""
        self.ho_ten = data.get("ho_ten", self.ho_ten) or ""
        self.so_dien_thoai = data.get("so_dien_thoai", self.so_dien_thoai) or ""

        if email := data.get("email"):
            self.user.email = email
            self.user.save(update_fields=["email"])

        if files and (f := files.get("avatar")):
            self.anh_dai_dien = f

        self.save()

    def update_role_data(self, role, data):
        """Cập nhật dữ liệu theo role"""
        if role == "customer":
            kh, _ = KhachHang.objects.get_or_create(profile=self)
            kh.muc_tieu = data.get("muc_tieu", kh.muc_tieu) or ""
            kh.chieu_cao_cm = data.get("chieu_cao_cm", kh.chieu_cao_cm)
            kh.can_nang_kg = data.get("can_nang_kg", kh.can_nang_kg)
            kh.save()
        elif role == "trainer":
            hlv, _ = HuanLuyenVien.objects.get_or_create(profile=self)
            hlv.chuyen_mon = data.get("chung_chi", hlv.chuyen_mon) or ""
            hlv.nam_kinh_nghiem = data.get("kinh_nghiem_nam", hlv.nam_kinh_nghiem)
            hlv.gioi_thieu = data.get("gioi_thieu", hlv.gioi_thieu) or ""
            hlv.save()
        elif role == "staff":
            nv, _ = NhanVien.objects.get_or_create(profile=self)
            nv.phong_ban = data.get("phong_ban", nv.phong_ban) or ""
            nv.ghi_chu = data.get("ghi_chu", nv.ghi_chu) or ""
            nv.save()

    def to_dict(self):
        """Convert sang dict"""
        kh = getattr(self, "khach_hang", None)
        hlv = getattr(self, "huan_luyen_vien", None)
        nv = getattr(self, "nhan_vien", None)

        return {
            "id": self.id,
            "role": self.role,
            "ho_ten": self.display_name,
            "so_dien_thoai": self.so_dien_thoai or "",
            "email": self.user.email or "",
            "avatar_url": self.avatar_url,
            "muc_tieu": kh.muc_tieu if kh else "",
            "chieu_cao_cm": kh.chieu_cao_cm if kh else None,
            "can_nang_kg": kh.can_nang_kg if kh else None,
            "chung_chi": hlv.chuyen_mon if hlv else "",
            "kinh_nghiem_nam": hlv.nam_kinh_nghiem if hlv else None,
            "gioi_thieu": hlv.gioi_thieu if hlv else "",
            "phong_ban": nv.phong_ban if nv else "",
            "ghi_chu": nv.ghi_chu if nv else "",
        }


class KhachHang(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="khach_hang")
    muc_tieu = models.CharField(max_length=255, blank=True)
    chieu_cao_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    can_nang_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    goi_tap = models.CharField(max_length=100, blank=True)
    ngay_het_han = models.DateField(null=True, blank=True)
    huan_luyen_vien = models.ForeignKey("taikhoan.HuanLuyenVien", on_delete=models.SET_NULL, null=True, blank=True, related_name="hoc_vien_quan_ly")

    def __str__(self):
        return f"Khách hàng: {self.profile}"


class HuanLuyenVien(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="huan_luyen_vien")
    chuyen_mon = models.CharField(max_length=255, blank=True)
    nam_kinh_nghiem = models.PositiveIntegerField(null=True, blank=True)
    gioi_thieu = models.TextField(blank=True)

    def __str__(self):
        return f"HLV: {self.profile}"


class NhanVien(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="nhan_vien")
    phong_ban = models.CharField(max_length=100, blank=True)
    ghi_chu = models.TextField(blank=True)

    def __str__(self):
        return f"Nhân viên: {self.profile}"