from django import forms
from .models import DanhGia

class DanhGiaForm(forms.ModelForm):
    class Meta:
        model = DanhGia
        fields = ['danh_gia_chung', 'thai_do_phuc_vu', 'chat_luong_dich_vu', 'nhan_xet']
        widgets = {
            'nhan_xet': forms.Textarea(attrs={
                'class': 'form-control bg-dark text-light',
                'rows': 4,
                'placeholder': 'Thêm nhận xét...',
            }),
        }
