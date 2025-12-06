from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from . import views
from .forms import FormDangNhap

app_name = 'taikhoan'
urlpatterns = [
    path('dang-ky/', views.dang_ky, name='dang_ky'),
    path('dang-nhap/', auth_views.LoginView.as_view(
        authentication_form=FormDangNhap,
        template_name='nguoidung/dang_nhap.html'
    ), name='dang_nhap'),
    path('dang-xuat/', auth_views.LogoutView.as_view(), name='dang_xuat'),

    path('ho-so/', views.ho_so_xem, name='ho_so'),
    path('ho-so/chinh-sua/', views.ho_so_sua, name='ho_so_sua'),
    path('ho-so/tai-anh/', views.tai_anh_dai_dien, name='tai_anh'),
    path('tai-khoan/khoa-tai-khoan/', views.khoa_tai_khoan, name="khoa_tai_khoan"),
]