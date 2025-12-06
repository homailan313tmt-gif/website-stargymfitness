from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User


class FormDangKy(UserCreationForm):
    ho = forms.CharField(label='Họ', max_length=30, required=True)
    ten = forms.CharField(label='Tên', max_length=30, required=True)
    email = forms.EmailField(label='Email', max_length=254, required=True)

    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["ho"]
        user.last_name = self.cleaned_data["ten"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class FormDangNhap(AuthenticationForm):
    pass


class FormHoSo(forms.Form):
    """Form chung cho tất cả role"""
    # Thông tin chung
    ho_ten = forms.CharField(label='Họ và tên', max_length=150, required=False)
    so_dien_thoai = forms.CharField(label='Số điện thoại', max_length=20, required=False)
    email = forms.EmailField(label='Email', max_length=254, required=False)

    # Khách hàng
    muc_tieu = forms.CharField(label='Mục tiêu tập luyện', max_length=255, required=False)
    chieu_cao_cm = forms.IntegerField(label='Chiều cao (cm)', min_value=80, max_value=250, required=False)
    can_nang_kg = forms.DecimalField(label='Cân nặng (kg)', min_value=20, max_value=350, max_digits=5, decimal_places=2,
                                     required=False)

    # Huấn luyện viên
    chung_chi = forms.CharField(label='Chứng chỉ', max_length=255, required=False)
    kinh_nghiem_nam = forms.IntegerField(label='Kinh nghiệm (năm)', min_value=0, max_value=80, required=False)
    gioi_thieu = forms.CharField(label='Giới thiệu', widget=forms.Textarea(attrs={'rows': 3}), required=False)

    # Nhân viên
    phong_ban = forms.CharField(label='Phòng ban', max_length=100, required=False)
    ghi_chu = forms.CharField(label='Ghi chú', max_length=255, required=False)

    def __init__(self, role=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Thêm class form-control cho tất cả field
        for field in self.fields.values():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " form-control").strip()

        # Ẩn field không cần thiết theo role
        if role == "customer":
            self._hide_fields(['chung_chi', 'kinh_nghiem_nam', 'gioi_thieu', 'phong_ban', 'ghi_chu'])
        elif role == "trainer":
            self._hide_fields(['muc_tieu', 'chieu_cao_cm', 'can_nang_kg', 'phong_ban', 'ghi_chu'])
        elif role == "staff":
            self._hide_fields(['muc_tieu', 'chieu_cao_cm', 'can_nang_kg', 'chung_chi', 'kinh_nghiem_nam', 'gioi_thieu'])

    def _hide_fields(self, field_names):
        """Ẩn các field không cần thiết"""
        for name in field_names:
            if name in self.fields:
                self.fields[name].widget = forms.HiddenInput()
                self.fields[name].required = False


class FormKhoaTaiKhoan(forms.Form):
    ly_do = forms.CharField(
        label="Lý do khóa tài khoản",
        max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nhập lý do..."}),
    )