import logging
from email.message import MIMEPart
from io import BytesIO

import qrcode

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.utils.html import escape

from orders.models import Order, OrderStatusEnum


logger = logging.getLogger(__name__)


def format_vnd(value):
    return f'{value:,.0f}'.replace(',', '.')


def create_ticket_qr_image(ticket_code):
    qr = qrcode.QRCode(
        box_size=8,
        border=3,
    )
    qr.add_data(ticket_code)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color='black',
        back_color='white',
    )
    image_buffer = BytesIO()
    image.save(image_buffer, format='PNG')
    return image_buffer.getvalue()


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
        ticket_html_cards = []
        ticket_qr_images = []

        for ticket in tickets:
            seat_name = ticket.seat.seat_name
            ticket_type_name = ticket.ticket_type.name
            content_id = f'ticket-qr-{ticket.id}'

            ticket_text_lines.append(
                f'- {ticket_type_name} - Ghế {seat_name}\n'
                f'  Mã vé: {ticket.qr_code}'
            )

            qr_image = MIMEPart()
            qr_image.set_content(
                create_ticket_qr_image(ticket.qr_code),
                maintype='image',
                subtype='png',
                disposition='inline',
                cid=f'<{content_id}>',
            )
            ticket_qr_images.append(qr_image)

            ticket_html_cards.append(
                f'''
                <div style="
                    margin-bottom: 18px;
                    padding: 20px;
                    border: 1px solid #f2d7cc;
                    border-radius: 16px;
                    background: #ffffff;
                    text-align: center;
                ">
                    <div style="
                        margin-bottom: 6px;
                        color: #f47c5a;
                        font-size: 18px;
                        font-weight: bold;
                    ">
                        {escape(ticket_type_name)}
                    </div>

                    <div style="margin-bottom: 14px; color: #52605f;">
                        Ghế <strong>{escape(seat_name)}</strong>
                    </div>

                    <img
                        src="cid:{content_id}"
                        width="190"
                        alt="Mã QR vé {escape(seat_name)}"
                        style="
                            display: block;
                            width: 190px;
                            max-width: 100%;
                            height: auto;
                            margin: 0 auto 14px;
                        "
                    >

                    <div style="
                        margin-bottom: 6px;
                        color: #697675;
                        font-size: 12px;
                    ">
                        Mã vé dùng để check-in thủ công
                    </div>

                    <div style="
                        padding: 10px;
                        border-radius: 10px;
                        background: #fff4ee;
                        color: #263238;
                        font-family: Consolas, monospace;
                        font-size: 13px;
                        font-weight: bold;
                        overflow-wrap: anywhere;
                        word-break: break-all;
                    ">
                        {escape(ticket.qr_code)}
                    </div>
                </div>
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
            f'Bạn có thể dùng mã vé phía trên để check-in thủ công.\n'
            f'Xem lại vé tại: {ticket_url}\n\n'
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
            background: #fff9f5;
            font-family: Arial, sans-serif;
            color: #263238;
        ">
            <div style="
                max-width: 620px;
                margin: 30px auto;
                background: #ffffff;
                border: 1px solid #f2d7cc;
                border-radius: 18px;
                overflow: hidden;
            ">
                <div style="
                    padding: 28px;
                    background: linear-gradient(135deg, #f47c5a, #ee9b73);
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
                        color: #fff4ee;
                    ">
                        Xác nhận thanh toán thành công
                    </div>
                </div>

                <div style="padding: 28px;">
                    <h2 style="
                        margin-top: 0;
                        color: #3f9188;
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
                        background: #fff4ee;
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
                                color: #e96343;
                                font-size: 18px;
                                font-weight: bold;
                            ">
                                {format_vnd(order.total_amount)} VNĐ
                            </span>
                        </div>
                    </div>

                    <h3>Vé điện tử và mã check-in</h3>

                    <p style="color: #697675; line-height: 1.6;">
                        Đưa mã QR cho ban tổ chức quét, hoặc đọc mã vé bên
                        dưới QR để ban tổ chức nhập thủ công.
                    </p>

                    {''.join(ticket_html_cards)}

                    <div style="text-align: center; margin: 30px 0;">
                        <a
                            href="{escape(ticket_url)}"
                            style="
                                display: inline-block;
                                padding: 14px 26px;
                                border-radius: 999px;
                                background: #4fa39a;
                                color: #ffffff;
                                text-decoration: none;
                                font-weight: bold;
                            "
                        >
                            Xem vé và mã QR
                        </a>
                    </div>

                    <p style="
                        color: #697675;
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

        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[customer.email],
        )
        email.attach_alternative(html_message, 'text/html')

        for qr_image in ticket_qr_images:
            email.attach(qr_image)

        sent_count = email.send(fail_silently=False)

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
