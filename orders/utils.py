from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_payment_success_email(order):
    try:
        recipient_email = order.customer.user.email
        customer_name = order.customer.user.name
        tickets = order.tickets.select_related('seat__event', 'ticket_type').all()
        
        if not tickets.exists():
            return

        event = tickets.first().seat.event
        subject = f"[Smart Event Ticketing] Xác nhận thanh toán thành công đơn hàng #{order.id}"
        
        ticket_details_html = ""
        for t in tickets:
            ticket_details_html += f"<li>Ghế: <b>{t.seat.row}{t.seat.number}</b> - Loại: {t.ticket_type.name} ({int(t.ticket_type.price):,} VNĐ)</li>"

        html_content = f"""
        <h2>Cảm ơn {customer_name} đã đặt vé!</h2>
        <p>Đơn hàng <b>#{order.id}</b> của bạn đã được thanh toán thành công qua PayOS.</p>
        <hr>
        <h3>Thông tin sự kiện:</h3>
        <p><b>Sự kiện:</b> {event.title}</p>
        <p><b>Địa điểm:</b> {event.location}</p>
        <p><b>Thời gian:</b> {event.start_time.strftime('%H:%M %d/%m/%Y')}</p>
        <hr>
        <h3>Chi tiết vé:</h3>
        <ul>{ticket_details_html}</ul>
        <p><b>Tổng tiền:</b> {int(order.total_amount):,} VNĐ</p>
        <hr>
        <p>Vui lòng xuất trình mã QR Code trong mục <b>Ví vé của tôi</b> trên ứng dụng khi đến tham dự sự kiện.</p>
        """

        text_content = f"Xác nhận thanh toán đơn hàng #{order.id} cho sự kiện {event.title} thành công."

        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [recipient_email])
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=True)
    except Exception:
        pass