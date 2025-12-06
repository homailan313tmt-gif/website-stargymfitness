# taikhoan/admin.py
from django.contrib import admin
from .models import Profile, KhachHang, HuanLuyenVien, NhanVien

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "role", "ho_ten", "so_dien_thoai")
    list_filter = ("role",)
    search_fields = ("user__username", "ho_ten", "so_dien_thoai")

admin.site.register(KhachHang)
admin.site.register(HuanLuyenVien)
admin.site.register(NhanVien)
