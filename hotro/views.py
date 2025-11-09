from django.shortcuts import render, redirect, get_object_or_404
from .models import PhanHoi
from .forms import PhanHoiForm
from django.contrib.auth.decorators import login_required

def gui_phan_hoi(request):
    da_gui = False

    if request.method == 'POST':
        form = PhanHoiForm(request.POST)
        if form.is_valid():
            ph = form.save(commit=False)
            if request.user.is_authenticated:
                ph.user = request.user
            else:
                ph.user = None
            ph.save()
            # 👉 Lưu cờ vào session rồi redirect (tránh lặp khi F5)
            request.session['da_gui'] = True
            return redirect('ho_tro_gui')  # tên URL tới trang form phản hồi
    else:
        form = PhanHoiForm()

    # 👉 Kiểm tra nếu vừa gửi thành công
    if request.session.pop('da_gui', False):
        da_gui = True

    return render(request, 'hotro/gui.html', {'form': form, 'da_gui': da_gui})

def theo_doi(request):
    if request.user.is_authenticated:
        # nếu đã đăng nhập → lọc phản hồi theo user
        ds = PhanHoi.objects.filter(user=request.user)
    else:
        # nếu chưa đăng nhập → hiển thị tất cả (hoặc để trống)
        ds = PhanHoi.objects.all().order_by('-ngay_gui')

    return render(request, 'hotro/theodoi.html', {'ds': ds})


def chi_tiet(request, pk):
    ph = get_object_or_404(PhanHoi, pk=pk)
    return render(request, 'hotro/chitiet.html', {'ph': ph})
