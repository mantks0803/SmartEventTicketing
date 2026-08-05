import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def send_payment_success_email(order):
    try:
        subject = f"SmartTicket - Xác nhận thanh toán thành công đơn hàng #{order.id}"
        message = (
            f"Xin chào {order.customer.user.name},\n\n"
            f"Đơn hàng #{order.id} cho sự kiện '{order.event.title}' đã được thanh toán thành công.\n"
            f"Tổng tiền: {order.total_amount:,.0f} VNĐ\n\n"
            f"Cảm ơn bạn đã sử dụng dịch vụ của SmartTicket!"
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [order.customer.user.email],
            fail_silently=False
        )
    except Exception as e:
        logger.error(f"Lỗi gửi email xác nhận cho đơn hàng #{order.id}: {str(e)}", exc_info=True)