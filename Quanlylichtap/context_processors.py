from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ObjectDoesNotExist
from taikhoan.models import KhachHang


def notification_context(request):
    if not request.user.is_authenticated:
        return {}

    try:
        ThongBao = apps.get_model('Quanlylichtap', 'ThongBao')
    except LookupError:
        return {}

    try:
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'customer':
            return {}

        khach_hang_nhan = request.user.profile.khach_hang

        print(f"DEBUG CP: User {request.user.username} đang tìm KH ID: {khach_hang_nhan.id}")

        base_queryset = ThongBao.objects.filter(
            nguoi_nhan=khach_hang_nhan
        ).order_by('-thoi_gian')

        unread_count = base_queryset.filter(is_read=False).count()
        notifications = base_queryset[:7]

        print(f"DEBUG CP: KH ID {khach_hang_nhan.id} có {unread_count} thông báo chưa đọc.")

        return {
            'notifications': notifications,
            'unread_count': unread_count
        }

    except (AttributeError, ObjectDoesNotExist, KhachHang.DoesNotExist) as e:

        print(f"DEBUG LỖI CP: Lỗi truy xuất dữ liệu KH: {e}")
        return {}
    except Exception as e:
        print(f"DEBUG LỖI CP: Lỗi truy vấn thông báo: {e}")
        return {}