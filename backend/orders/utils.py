import logging

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.html import escape

from orders.models import Order, OrderStatusEnum


logger = logging.getLogger(__name__)


def format_vnd(value):
    return f'{value:,.0f}'.replace(',', '.')


def send_payment_success_email(order_id):
    try:
        order = (
            Order.objects
            .select_related(
                'customer__user',
                'event',
            )
            .prefetch_related(
                'tickets__seat',
                'tickets__ticket_type',
            )
            .get(id=order_id)
        )

        if order.status != OrderStatusEnum.PAID:
            logger.warning(
                'Không gửi email vì đơn hàng #%s chưa PAID.',
                order.id,
            )
            return False

        customer = order.customer.user

        if not customer.email:
            logger.warning(
                'Không gửi email vì tài khoản của đơn #%s không có email.',
                order.id,
            )
            return False

        tickets = list(order.tickets.all())

        if not tickets:
            logger.warning(
                'Không gửi email vì đơn hàng #%s chưa có vé.',
                order.id,
            )
            return False

        frontend_url = settings.FRONTEND_URL.rstrip('/')
        ticket_url = f'{frontend_url}/my-tickets?order={order.id}'

        event_title = order.event.title if order.event else 'Sự kiện'
        event_location = order.event.location if order.event else ''

        event_time = ''
        if order.event and order.event.start_time:
            event_time = timezone.localtime(
                order.event.start_time
            ).strftime('%H:%M - %d/%m/%Y')

        ticket_text_lines = []
        ticket_html_rows = []

        for ticket in tickets:
            seat_name = ticket.seat.seat_name
            ticket_type_name = ticket.ticket_type.name

            ticket_text_lines.append(
                f'- {ticket_type_name} - Ghế {seat_name}'
            )

            ticket_html_rows.append(
                f'''
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">
                        {escape(ticket_type_name)}
                    </td>
                    <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">
                        {escape(seat_name)}
                    </td>
                </tr>
                '''
            )

        subject = (
            f'SmartTicket - Thanh toán thành công đơn hàng #{order.id}'
        )

        text_message = (
            f'Xin chào {customer.name},\n\n'
            f'Đơn hàng #{order.id} của bạn đã được thanh toán thành công.\n\n'
            f'Sự kiện: {event_title}\n'
            f'Thời gian: {event_time}\n'
            f'Địa điểm: {event_location}\n'
            f'Tổng tiền: {format_vnd(order.total_amount)} VNĐ\n\n'
            f'Danh sách vé:\n'
            f'{"\n".join(ticket_text_lines)}\n\n'
            f'Xem mã QR vé tại: {ticket_url}\n\n'
            f'Vui lòng không chia sẻ mã QR vé cho người khác.\n\n'
            f'Cảm ơn bạn đã sử dụng SmartTicket!'
        )

        html_message = f'''
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
        </head>

        <body style="
            margin: 0;
            padding: 0;
            background: #f8fafc;
            font-family: Arial, sans-serif;
            color: #0f172a;
        ">
            <div style="
                max-width: 620px;
                margin: 30px auto;
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 18px;
                overflow: hidden;
            ">
                <div style="
                    padding: 28px;
                    background: linear-gradient(135deg, #0f172a, #1d4ed8);
                    color: #ffffff;
                ">
                    <div style="
                        font-size: 23px;
                        font-weight: bold;
                    ">
                        SmartTicket
                    </div>

                    <div style="
                        margin-top: 8px;
                        color: #bfdbfe;
                    ">
                        Xác nhận thanh toán thành công
                    </div>
                </div>

                <div style="padding: 28px;">
                    <h2 style="
                        margin-top: 0;
                        color: #059669;
                    ">
                        Thanh toán thành công!
                    </h2>

                    <p>
                        Xin chào <strong>{escape(customer.name)}</strong>,
                    </p>

                    <p>
                        Đơn hàng <strong>#{order.id}</strong> của bạn đã
                        được thanh toán và vé điện tử đã được phát hành.
                    </p>

                    <div style="
                        padding: 18px;
                        margin: 22px 0;
                        border-radius: 14px;
                        background: #eff6ff;
                    ">
                        <div style="margin-bottom: 8px;">
                            <strong>Sự kiện:</strong>
                            {escape(event_title)}
                        </div>

                        <div style="margin-bottom: 8px;">
                            <strong>Thời gian:</strong>
                            {escape(event_time)}
                        </div>

                        <div style="margin-bottom: 8px;">
                            <strong>Địa điểm:</strong>
                            {escape(event_location)}
                        </div>

                        <div>
                            <strong>Tổng tiền:</strong>
                            <span style="
                                color: #2563eb;
                                font-size: 18px;
                                font-weight: bold;
                            ">
                                {format_vnd(order.total_amount)} VNĐ
                            </span>
                        </div>
                    </div>

                    <h3>Danh sách vé</h3>

                    <table style="
                        width: 100%;
                        border-collapse: collapse;
                        margin-bottom: 24px;
                    ">
                        <thead>
                            <tr style="
                                background: #f1f5f9;
                                text-align: left;
                            ">
                                <th style="padding: 10px;">Loại vé</th>
                                <th style="padding: 10px;">Ghế</th>
                            </tr>
                        </thead>

                        <tbody>
                            {''.join(ticket_html_rows)}
                        </tbody>
                    </table>

                    <div style="text-align: center; margin: 30px 0;">
                        <a
                            href="{escape(ticket_url)}"
                            style="
                                display: inline-block;
                                padding: 14px 26px;
                                border-radius: 999px;
                                background: #2563eb;
                                color: #ffffff;
                                text-decoration: none;
                                font-weight: bold;
                            "
                        >
                            Xem vé và mã QR
                        </a>
                    </div>

                    <p style="
                        color: #64748b;
                        font-size: 13px;
                        line-height: 1.6;
                    ">
                        Mã QR là mã dùng để check-in. Vui lòng không chia sẻ
                        mã QR hoặc ảnh chụp vé cho người khác.
                    </p>
                </div>
            </div>
        </body>
        </html>
        '''

        sent_count = send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[customer.email],
            fail_silently=False,
            html_message=html_message,
        )

        if sent_count == 1:
            logger.info(
                'Đã gửi email xác nhận cho đơn hàng #%s đến %s.',
                order.id,
                customer.email,
            )
            return True

        logger.warning(
            'Email đơn hàng #%s không được gửi.',
            order.id,
        )
        return False

    except Order.DoesNotExist:
        logger.error(
            'Không tìm thấy đơn hàng #%s để gửi email.',
            order_id,
        )
        return False

    except Exception:
        logger.exception(
            'Lỗi gửi email xác nhận đơn hàng #%s.',
            order_id,
        )
        return False
