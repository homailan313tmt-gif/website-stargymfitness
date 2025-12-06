from django import forms
from .models import PhanHoi

class PhanHoiForm(forms.ModelForm):
    class Meta:
        model = PhanHoi
        fields = ['loai', 'noi_dung']
        labels = {
            'loai': 'Loại phản hồi',
            'noi_dung': 'Nội dung chi tiết'
        }
        widgets = {
            'loai': forms.Select(attrs={
                'class': 'form-select',
                'style': 'width:400px; height:50px;'
            }),
            'noi_dung': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'style': 'width:400px; height:100px;'
            }),
        }
