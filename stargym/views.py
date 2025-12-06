from django.shortcuts import render
from django.contrib.auth.decorators import login_required

def home_view(request):
    return render(request, 'home.html')

def home_customer(request):
    return render(request, 'home-customer.html')

def home_staff(request):
    return render(request, 'home-staff.html')

def home_trainer(request):
    return render(request, 'home-trainer.html')

from taikhoan.decorators import role_required

@role_required("customer")
def home_customer(request):
    ...
    return render(request, "home-customer.html")

@role_required("trainer")
def home_trainer(request):
    ...
    return render(request, "home-trainer.html")

@role_required("staff")
def home_staff(request):
    ...
    return render(request, "home-staff.html")

def danh_sach_thong_bao(request):
    ...
    return render(request, "thong-bao.html")