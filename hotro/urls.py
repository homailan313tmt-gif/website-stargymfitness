from django.urls import path
from . import views

urlpatterns = [
    path('', views.gui_phan_hoi, name='gui_phan_hoi'),
    path('theo-doi/', views.theo_doi, name='theo_doi'),
    path('chi-tiet/<int:pk>/', views.chi_tiet, name='chi_tiet'),
    path('chinh-sua/<int:pk>/', views.chinh_sua, name='chinh_sua'),


]
