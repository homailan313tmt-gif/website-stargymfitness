from django import forms
from datetime import date, timedelta

class FormKhoangNgay(forms.Form):
    tu_ngay = forms.DateField(
        label="Từ ngày",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    den_ngay = forms.DateField(
        label="Đến ngày",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            today = date.today()
            self.initial.setdefault("den_ngay", today)
            self.initial.setdefault("tu_ngay", today - timedelta(days=29))

    def clean(self):
        cd = super().clean()
        s, e = cd.get("tu_ngay"), cd.get("den_ngay")
        if s and e and s > e:
            cd["tu_ngay"], cd["den_ngay"] = e, s
        return cd