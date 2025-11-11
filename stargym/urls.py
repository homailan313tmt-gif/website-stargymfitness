from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('', include('Quanlylichtap.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('danh-gia/', include('danhgia.urls')),
    path('ho-tro/', include('hotro.urls')),
    path('quan-ly/', include('traloikhachhang.urls')),
    path('tai-khoan/', include('taikhoan.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)