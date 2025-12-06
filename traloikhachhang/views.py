from collections import Counter

from django.shortcuts import render, get_object_or_404, redirect
from hotro.models import PhanHoi



def theo_doi(request):
    ds = PhanHoi.objects.all().order_by('-ngay_gui')

    user_id_list = ds.values_list('user_id', flat=True)
    user_id_list = [uid for uid in user_id_list if uid is not None]

    counts = Counter(user_id_list)
    for ph in ds:
        if ph.user_id is None:
            ph.so_lan_phan_hoi = 1
            ph.la_khach_moi = True
        else:
            ph.so_lan_phan_hoi = counts.get(ph.user_id, 0)
            ph.la_khach_moi = (ph.so_lan_phan_hoi == 1)

    return render(request, 'traloikhachhang/theo-doi.html', {'ds': ds})


def tra_loi(request, pk):
    ph = get_object_or_404(PhanHoi, pk=pk)

    if ph.user_id is not None:
        history = (
            PhanHoi.objects
            .filter(user_id=ph.user_id)
            .exclude(pk=ph.pk)
            .order_by('-ngay_gui')
        )
    else:
        history = PhanHoi.objects.none()

    first_time = not history.exists()


    if request.method == 'POST':
        ph.trang_thai = request.POST.get('trang_thai')
        ph.tra_loi = request.POST.get('tra_loi')
        ph.save()

        return render(request, 'traloikhachhang/tra-loi.html', {
            'ph': ph,
            'history': history,
            'first_time': first_time,
            'updated': True
        })

    context = {
        'ph': ph,
        'history': history,
        'first_time': first_time,
    }
    return render(request, 'traloikhachhang/tra-loi.html', context)


def tra_loi_thanh_cong(request, pk):
    ph = get_object_or_404(PhanHoi, pk=pk)
    return render(request, 'traloikhachhang/thanh-cong.html', {'ph': ph})
