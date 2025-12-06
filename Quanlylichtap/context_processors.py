from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
# Không cần import logging hay settings

def notification_context(request):
    """
    Tải thông báo chưa đọc và các thông báo gần nhất cho Khách hàng.
    """
    # 0. Điều kiện thoát sớm nếu chưa đăng nhập
    if not request.user.is_authenticated:
        return {}

    # 1. Tải Model động (Tránh lỗi AppRegistryNotReady)
    try:
        # Giả sử ThongBao nằm trong ứng dụng Quanlylichtap
        ThongBao = apps.get_model('Quanlylichtap', 'ThongBao')
    except LookupError:
        # Nếu model không tồn tại (ví dụ: đang chạy migrate)
        return {}

    # 2. Kiểm tra vai trò và truy xuất KhachHang an toàn
    try:
        # Nếu không có profile hoặc vai trò không phải 'customer', thoát
        if not hasattr(request.user, 'profile') or request.user.profile.role != 'customer':
            return {}

        # Lấy KhachHang instance an toàn (có thể gây ObjectDoesNotExist)
        khach_hang_nhan = request.user.profile.khach_hang

        # === DÒNG DEBUG ĐỂ XÁC NHẬN ===
        print(f"DEBUG CP: User {request.user.username} đang tìm KH ID: {khach_hang_nhan.id}")
        # =============================

    except (AttributeError, ObjectDoesNotExist) as e:
        # Bắt lỗi nếu user không có profile/khach_hang
        print(f"DEBUG LỖI CP: Lỗi truy xuất KhachHang: {e}")
        return {}

    # 3. Thực hiện truy vấn cuối cùng
    try:
        # Truy vấn chính: đã lọc theo người nhận và sắp xếp
        base_queryset = ThongBao.objects.filter(
            nguoi_nhan=khach_hang_nhan
        ).order_by('-thoi_gian')

        # Lấy số lượng chưa đọc (cho huy hiệu)
        unread_count = base_queryset.filter(is_read=False).count()

        # Lấy tối đa 7 thông báo gần nhất (cho dropdown)
        notifications = base_queryset[:7]

        # In ra số lượng chưa đọc để xác nhận
        print(f"DEBUG CP: KH ID {khach_hang_nhan.id} có {unread_count} thông báo chưa đọc.")

        return {
            'notifications': notifications,
            'unread_count': unread_count
        }
    except Exception as e:
        # Bắt lỗi trong quá trình truy vấn (ví dụ: lỗi database)
        print(f"DEBUG LỖI CP: Lỗi truy vấn thông báo: {e}")
        return {}