from django.urls import path
from . import views

urlpatterns = [
    path('', views.theo_doi, name='quan-ly'),
    path('<int:pk>/', views.tra_loi, name='tra_loi_chi_tiet'),
    path('thanh-cong/<int:pk>/', views.tra_loi_thanh_cong, name='tra_loi_thanh_cong'),
    path('home/', views.staff_home, name='staff-home'),
]
