from django.urls import path
from . import views

urlpatterns = [
    path('', views.danh_sach_tap, name='danh_sach_tap'),

    path('hoc-vien/<int:hv_id>/',
         views.danh_sach_buoi_tap,
         name='danh_sach_buoi_tap'),

    path('hoc-vien/<int:hv_id>/<int:buoi_id>/',
         views.chi_tiet_tap,
         name='chi_tiet_tap'),




    path('xoa-anh/<int:anh_id>/', views.xoa_anh_cam_nhan, name='xoa_anh_cam_nhan'),
]
