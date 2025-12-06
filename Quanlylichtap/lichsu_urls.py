from django.urls import path
from . import views

urlpatterns = [
    path('', views.lich_su_tap_luyen, name='lich_su_tap_luyen'),       # /lich-su/
    path('<int:buoi_id>/', views.thong_tin_buoi_tap, name='thongtin_buoi_tap'),  # /lich-su/<id>/
    path('<int:buoi_id>/ghi-chu/', views.them_ghi_chu, name='them_ghi_chu'),
    path('<int:buoi_id>/ghi-chu/xoa/', views.xoa_ghi_chu, name='xoa_ghi_chu_ls'),

]