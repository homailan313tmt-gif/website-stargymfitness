from django.urls import path
from . import views

urlpatterns = [
    path('', views.theo_doi, name='theo-doi-phan-hoi'),
    path('<int:pk>/', views.tra_loi, name='tra_loi_chi_tiet'),
    path('thanh-cong/<int:pk>/', views.tra_loi_thanh_cong, name='tra_loi_thanh_cong'),
]
