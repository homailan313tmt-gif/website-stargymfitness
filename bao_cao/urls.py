from django.urls import path
from . import views

app_name = "bao_cao"

urlpatterns = [
    path("khach-hang/", views.bao_cao_khach_hang, name="khach_hang"),
    path("khach-hang.csv", views.bao_cao_khach_hang_csv, name="khach_hang_csv"),
    path("khach-hang/<int:user_id>/", views.khach_hang_chi_tiet, name="khach_hang_chi_tiet"),
]

