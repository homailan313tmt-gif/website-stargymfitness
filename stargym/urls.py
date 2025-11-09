from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('danh-gia/', include('danhgia.urls')),
    path('ho-tro/', include('hotro.urls')),
]
