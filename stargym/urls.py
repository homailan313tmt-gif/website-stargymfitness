from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('danh-sach-hoc-vien/', include('Quanlylichtap.urls')),
    path('lich-su/', include('Quanlylichtap.lichsu_urls')),
    path('danh-gia/', include('danhgia.urls')),
    path('ho-tro/', include('hotro.urls')),
    path('theo-doi-phan-hoi/', include('traloikhachhang.urls')),
    path('tai-khoan/', include('taikhoan.urls')),
    path("", views.home_view, name="trang_chu"),
    path("home-customer/", views.home_customer, name="home_customer"),
    path("home-staff/", views.home_staff, name="home_staff"),
    path("home-trainer/", views.home_trainer, name="home_trainer"),
    path("thong-bao/", views.danh_sach_thong_bao, name="thong_bao"),
    path('bao-cao/', include('bao_cao.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)