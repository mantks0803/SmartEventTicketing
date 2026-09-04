# Kiểm thử thanh toán giả lập (local)

> Chỉ sử dụng trên môi trường local và dữ liệu test. Tài liệu được chuyển từ `payment_test.txt`; các hướng dẫn và kết quả mong đợi được giữ lại, không thực hiện lại kiểm thử khi sắp xếp tài liệu. Các con số 55/139 tests là số liệu lịch sử; xem [báo cáo kiểm thử](TEST_REPORT.md) và [lệnh kiểm thử](TEST_COMMANDS.md).

Các đường dẫn ví dụ dùng `D:\SmartEventTicketing`; thay bằng vị trí project của bạn nếu khác. Cần chuẩn bị backend, frontend và database theo [README dự án](../README.md) và [hướng dẫn database](../database/README.md) trước khi thực hiện.

## 1. Chế độ này test được gì?

Chế độ giả lập test được phần nghiệp vụ của website:

- Giữ ghế trong 10 phút.
- Tạo Order và OrderItem.
- Nhận webhook thanh toán thành công.
- Kiểm tra số tiền.
- Chống webhook lặp.
- Chuyển Order sang PAID.
- Chuyển Seat sang SOLD.
- Tạo Payment SUCCESS.
- Tạo Ticket và mã QR.
- Hiển thị trang "Thanh toán thành công".
- Hiển thị vé trong "Vé của tôi".
- Gửi email thật hoặc in email trong terminal.
- Check-in QR và chống check-in hai lần.

Chế độ này KHÔNG tạo giao dịch thật trên PayOS, không tạo QR ngân hàng thật,
không trừ tiền và không xuất hiện trong lịch sử giao dịch PayOS thật.

Webhook được gửi thủ công từ PowerShell hoặc Postman để giả lập việc PayOS
gọi về backend sau khi khách hàng đã thanh toán.

## 2. Cảnh báo an toàn

PAYOS_SKIP_SIGNATURE_CHECK=True chỉ được dùng khi test local.

Khi bật True, endpoint webhook chấp nhận payload không có chữ ký PayOS thật.
Nếu bật trên website public, người khác có thể tự gửi webhook giả để biến đơn
hàng thành PAID.

Sau khi test xong bắt buộc đổi lại:

```dotenv
PAYOS_SKIP_SIGNATURE_CHECK=False
```

Không commit file .env hoặc mật khẩu email lên GitHub.

## 3. Chuẩn bị file .env

Bước 1. Mở PowerShell tại thư mục project:

`D:\SmartEventTicketing`

Bước 2. Mở file:

`D:\SmartEventTicketing\backend\.env`

Bước 3. Đổi cấu hình PayOS mock thành:

```dotenv
PAYOS_SKIP_SIGNATURE_CHECK=True
```

Giá trị phải đúng chữ hoa/chữ thường như trên vì settings đang so sánh với
chuỗi "True".

Bước 4. Chọn một trong hai cách test email.

### Cách A — Không gửi email thật, in email trong terminal

Khuyên dùng khi test nhiều lần:

```dotenv
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Kết quả:

- Không gửi thư ra internet.
- Tiêu đề, text và HTML email được in trong terminal chạy Django.
- Vẫn test được việc hàm email được gọi sau khi phát hành vé.

### Cách B — Gửi email thật

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_TIMEOUT=10
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
DEFAULT_FROM_EMAIL="SmartTicket <your_email@gmail.com>"
```

Lưu ý:

- EMAIL_HOST_PASSWORD phải là Gmail App Password.
- Không dùng mật khẩu Gmail đăng nhập thông thường.
- Email trong tài khoản Customer phải là email có thể nhận thư.
- Kiểm tra Inbox, Spam và Promotions sau khi test.

## 4. Khởi động lại backend và frontend

Thay đổi .env chỉ chắc chắn có hiệu lực sau khi tắt và chạy lại backend.

Bước 1. Chạy backend:

```powershell
cd D:\SmartEventTicketing\backend
..\venv\Scripts\python.exe manage.py runserver
```

Kết quả mong đợi:

```text
Starting development server at http://127.0.0.1:8000/
```

Bước 2. Mở PowerShell khác và chạy frontend:

```powershell
cd D:\SmartEventTicketing\frontend
npm.cmd run dev
```

Kết quả mong đợi:

```text
Local: http://localhost:5173/
```

Bước 3. Có thể kiểm tra backend đã đọc đúng chế độ mock bằng lệnh:

```powershell
cd D:\SmartEventTicketing\backend
..\venv\Scripts\python.exe manage.py shell -c "from django.conf import settings; print('PAYOS mock =', settings.PAYOS_SKIP_SIGNATURE_CHECK); print('Email backend =', settings.EMAIL_BACKEND)"
```

Kết quả đúng phải có:

```text
PAYOS mock = True
```

Nếu vẫn là False, hãy tắt hẳn terminal runserver và khởi động lại backend.

## 5. Tạo đơn hàng test

Bước 1. Truy cập:

`http://localhost:5173/`

Bước 2. Đăng nhập bằng tài khoản có role/type CUSTOMER.

Không dùng tài khoản ORGANIZER vì API giữ ghế và thanh toán chỉ cho CUSTOMER.

Bước 3. Mở một Event đang PUBLISHED.

Bước 4. Nhấn "Mở sơ đồ chọn ghế".

Bước 5. Chọn từ 1 đến 5 ghế AVAILABLE.

Không chọn ghế LOCKED hoặc SOLD.

Bước 6. Nhấn "Giữ ghế ngay".

Kết quả mong đợi:

- Backend trả POST /api/orders/hold/ HTTP 201.
- Order được tạo với status PENDING.
- Ghế chuyển từ AVAILABLE sang LOCKED.
- locked_by_order trỏ về Order vừa tạo.
- expires_at cách thời điểm tạo khoảng 10 phút.
- Chưa có Payment.
- Chưa có Ticket.
- Trình duyệt chuyển sang /checkout/{orderId}.

Bước 7. Ghi lại hai giá trị trên trang checkout:

- Mã đơn hàng.
- Tổng tiền chính xác.

Ví dụ:

```text
Mã đơn hàng: 25
Tổng tiền: 300.000 VNĐ
```

Khi tạo webhook phải dùng:

```text
orderCode = 25
amount = 300000
```

Không dùng:

```text
amount = 300.000
amount = "300000 VNĐ"
amount = ID ghế
amount = ID sự kiện
```

## 6. Mở trang thanh toán giả lập

Bước 1. Tại checkout, nhấn "Thanh toán qua PayOS".

Frontend gọi:

```text
POST /api/orders/{orderId}/payos-link/
```

Bước 2. Vì PAYOS_SKIP_SIGNATURE_CHECK=True, backend không tạo Payment Link
PayOS thật. Backend trả URL local dạng:

`http://localhost:5173/payment/result?orderId=25`

Bước 3. Trang hiển thị:

"Đang xác nhận thanh toán"

Điều này là bình thường. Đơn vẫn đang PENDING vì chưa gửi webhook giả.

Trang mới sẽ gọi:

```text
POST /api/orders/25/reconcile-payos/
```

Trong chế độ mock, PayOS thật không có giao dịch mới này. Vì vậy reconcile có
thể tạm trả lỗi/waiting. Sau khi webhook giả chuyển Order local thành PAID,
lần kiểm tra tiếp theo sẽ trả success ngay mà không cần hỏi PayOS.

Nên gửi webhook giả trong vòng 10 phút để kết quả dễ dự đoán nhất.

## 7. Giả lập thanh toán thành công bằng PowerShell

Đây là cách khuyên dùng.

Bước 1. Mở PowerShell thứ ba.

Bước 2. Khai báo đúng ID đơn và tổng tiền.

Ví dụ đơn #25, tổng tiền 300000:

```powershell
$testOrderId = 25
$testAmount = 300000
$testReference = "MOCK-$testOrderId-$(Get-Date -Format 'yyyyMMddHHmmssfff')"
```

Bước 3. Tạo payload webhook giả:

```powershell
$testPayload = @{
    success = $true
    code = "00"
    desc = "success"
    data = @{
        orderCode = $testOrderId
        amount = $testAmount
        reference = $testReference
    }
} | ConvertTo-Json -Depth 5
```

Bước 4. Gửi webhook:

```powershell
Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/orders/webhook/payos/" `
    -Method Post `
    -ContentType "application/json" `
    -Body $testPayload
```

Bước 5. Kiểm tra kết quả PowerShell.

Kết quả đúng:

```text
status
------
success
```

Tương đương JSON:

```json
{
    "status": "success"
}
```

Nếu nhận amount_mismatch thì số tiền trong $testAmount chưa đúng với tổng
tiền của Order.

## 8. Giả lập bằng Postman

Bước 1. Tạo request mới.

Method:

```text
POST
```

URL:

`http://127.0.0.1:8000/api/orders/webhook/payos/`

Bước 2. Chọn:

Body -> raw -> JSON

Bước 3. Nhập payload và sửa orderCode, amount cho đúng:

```json
{
    "success": true,
    "code": "00",
    "desc": "success",
    "data": {
        "orderCode": 25,
        "amount": 300000,
        "reference": "MOCK-ORDER-25-001"
    }
}
```

Bước 4. Nhấn Send.

Kết quả mong đợi:

HTTP 200 OK

```json
{
    "status": "success"
}
```

Lưu ý về reference:

- Mỗi giao dịch test mới nên có reference mới.
- Không dùng reference của Order trước cho Order khác.
- PowerShell ở phần trên tự tạo reference theo thời gian.
- Nếu dùng Postman, đổi 001 thành 002, 003... cho các đơn tiếp theo.

## 9. Kết quả sau khi webhook thành công

Backend chạy confirm_order_payment() trong transaction và thực hiện:

```text
Order.status = PAID
Seat.status = SOLD
Seat.locked_until = null
Seat.locked_by_order = null
Payment.status = SUCCESS
Payment.provider = PAYOS
Payment.transaction_id = reference vừa gửi
Ticket được tạo cho từng ghế
Ticket.qr_code được tạo duy nhất
```

Trang payment/result:

- Thường cập nhật trong khoảng 2 giây.
- Hiển thị "Thanh toán thành công!".
- Hiển thị mã đơn, sự kiện và tổng tiền.
- Hiện SweetAlert toast thành công.
- Có nút "Xem vé của tôi".

Nếu trang đã chuyển sang trạng thái waiting trước khi gửi webhook:

- Nhấn "Kiểm tra lại"; hoặc
- Tải lại /payment/result?orderId={id}.

Không cần gửi webhook lần thứ hai.

## 10. Kiểm tra database

Chạy tại thư mục `D:\SmartEventTicketing\backend` và thay số 25 thành Order ID của bạn:

```powershell
..\venv\Scripts\python.exe manage.py shell -c "from orders.models import Order; o=Order.objects.get(id=25); print('Order =', o.status); print('Payments =', o.payments.count()); print('Tickets =', o.tickets.count()); print('Seats =', [(i.seat.seat_name, i.seat.status) for i in o.items.select_related('seat')])"
```

Ví dụ mua 2 ghế, kết quả đúng:

```text
Order = PAID
Payments = 1
Tickets = 2
Seats = [('VIP1-1', 'SOLD'), ('VIP1-2', 'SOLD')]
```

## 11. Kiểm tra email

### Nếu dùng console email backend

Xem terminal đang chạy Django.

Email phải có:

- Subject chứa mã Order.
- Tên khách hàng.
- Tên Event.
- Thời gian và địa điểm.
- Tổng tiền.
- Danh sách loại vé và ghế.
- Link /my-tickets?order={orderId}.

Không có email thật trong Inbox vì console backend chỉ in email.

### Nếu dùng SMTP email backend

Kiểm tra email của tài khoản Customer:

- Inbox.
- Spam.
- Promotions.

Email hiện không nhúng ảnh QR trực tiếp. Email có nút dẫn về trang "Vé của
tôi", nơi frontend render QR từ ticket.qr_code.

Nếu SMTP lỗi thì Payment và Ticket vẫn giữ trạng thái thành công. Lỗi email
được ghi trong terminal backend.

## 12. Kiểm tra vé và QR

Bước 1. Nhấn "Xem vé của tôi" hoặc truy cập:

`http://localhost:5173/my-tickets`

Bước 2. Kết quả mong đợi:

- Vé của Order vừa thanh toán xuất hiện.
- Card đúng Order được highlight khi đi từ trang kết quả.
- Có tên Event, thời gian, địa điểm.
- Có loại vé, tên ghế và giá lúc mua.
- Trạng thái là "Vé hợp lệ".

Bước 3. Nhấn "Xem mã QR".

Kết quả mong đợi:

- QR SVG được render từ ticket.qr_code.
- Mỗi ghế có Ticket và QR riêng.
- Chuỗi qr_code xuất hiện phía dưới QR.

## 13. Kiểm tra check-in

Bước 1. Sao chép chuỗi qr_code phía dưới QR.

Bước 2. Đăng xuất tài khoản Customer.

Bước 3. Đăng nhập tài khoản Organizer sở hữu Event của vé.

Bước 4. Mở Dashboard BTC, phần soát vé.

Bước 5. Dán qr_code và nhấn soát vé.

Lần đầu mong đợi:

```text
Soát vé thành công
Ticket.is_checked_in = True
Ticket.checked_in_at có thời gian
```

Gửi lại cùng QR lần thứ hai mong đợi:

Vé này đã được soát vé trước đó!

Organizer khác Event phải nhận lỗi không có quyền soát vé.

## 14. Test webhook lặp

Gửi lại chính xác $testPayload cũ, gồm cùng orderCode, amount và reference:

```powershell
Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/api/orders/webhook/payos/" `
    -Method Post `
    -ContentType "application/json" `
    -Body $testPayload
```

Kết quả mong đợi:

```json
{
    "status": "already_processed"
}
```

Database vẫn phải có:

- Chỉ một Payment SUCCESS.
- Chỉ một Ticket cho mỗi ghế.
- Không đổi QR.
- Không gửi email lần hai.

## 15. Test thanh toán thất bại/hủy

Phải tạo một Order PENDING mới để test nhánh này.

Payload ví dụ:

```json
{
    "success": false,
    "code": "01",
    "desc": "cancelled",
    "data": {
        "orderCode": 26,
        "amount": 300000,
        "reference": "MOCK-FAILED-26-001"
    }
}
```

Kết quả mong đợi:

```json
{
    "status": "payment_failed"
}
```

Database:

```text
Order.status = CANCELLED hoặc EXPIRED
Seat.status = AVAILABLE
Payment.status = FAILED
Ticket không được tạo
Email thành công không được gửi
```

Nếu gửi webhook success sau đó cho Order đã CANCELLED, hệ thống không phục
hồi Order và trả status ignored với code invalid_payment_state.

## 16. Các lỗi và kết quả mong đợi

### Lỗi 1 — Sai amount

Response:

```text
HTTP 400
```

```json
{
    "error": "Số tiền thanh toán không khớp với đơn hàng.",
    "code": "amount_mismatch"
}
```

Order vẫn PENDING, ghế vẫn LOCKED, không có Ticket.

### Lỗi 2 — Order không tồn tại

Response mong đợi:

```text
HTTP 200
```

```json
{
    "status": "ignored_unknown_order"
}
```

Backend trả 200 để PayOS không gửi lặp mãi một webhook hợp lệ nhưng không
khớp dữ liệu local.

### Lỗi 3 — Dùng reference của giao dịch khác

Response:

```text
HTTP 400
```

```json
{
    "error": "Mã giao dịch PayOS đã được sử dụng cho giao dịch khác.",
    "code": "duplicate_transaction"
}
```

Hãy tạo reference mới.

### Lỗi 4 — Order đã hết hạn

Theo luồng được ghi nhận trong tài liệu gốc, webhook PAID đến trễ có thể phục hồi Order EXPIRED nếu:

- Ghế vẫn AVAILABLE và không thuộc Order nào; hoặc
- Ghế vẫn LOCKED bởi chính Order cũ.

Khi đó webhook vẫn có thể trả success, tạo vé và chuyển ghế SOLD.

Nếu ghế đã được Order khác giữ/bán, webhook không giành lại ghế và trả:

```json
{
    "status": "manual_review",
    "code": "seat_unavailable_after_payment"
}
```

Để test cơ bản ổn định, hãy gửi webhook trong thời gian giữ ghế 10 phút.

### Lỗi 5 — Webhook báo chữ ký không hợp lệ

Nguyên nhân:

- PAYOS_SKIP_SIGNATURE_CHECK vẫn là False.
- Backend chưa restart sau khi sửa .env.

Kiểm tra lại bằng lệnh settings ở Phần 4.

### Lỗi 6 — Trang kết quả vẫn đang kiểm tra

Kiểm tra:

- Đã gửi webhook giả chưa?
- Webhook có trả status=success không?
- orderCode có đúng ID Order không?
- amount có đúng tổng tiền không?
- Backend có đang chạy không?
- Có đăng nhập đúng Customer sở hữu Order không?

Sau khi webhook thành công, nhấn "Kiểm tra lại" hoặc tải lại trang result.

### Lỗi 7 — Response 401

Webhook không cần JWT, nhưng các API hold, checkout, reconcile và my-tickets
cần đăng nhập Customer.

Hãy đăng nhập lại bằng đúng tài khoản đã tạo Order.

### Lỗi 8 — Vé không xuất hiện

Kiểm tra:

- Order phải PAID.
- Ticket count phải lớn hơn 0.
- Đăng nhập đúng Customer đã mua.
- Nhấn "Làm mới" trong trang Vé của tôi.
- Xem lệnh kiểm tra database ở Phần 10.

### Lỗi 9 — Không có email

Nếu console backend:

- Xem terminal Django, không xem Inbox.

Nếu SMTP backend:

- Kiểm tra EMAIL_HOST_USER.
- Kiểm tra Gmail App Password.
- Kiểm tra email của Customer.
- Kiểm tra Spam và Promotions.
- Xem log SMTP trong terminal.

## 17. Chạy automated test

Chạy riêng test orders:

```powershell
cd D:\SmartEventTicketing\backend
..\venv\Scripts\python.exe manage.py test orders.tests --verbosity 2
```

Kết quả lịch sử trong tài liệu gốc (không phải số lượng kiểm thử được xác nhận lại hiện tại):

```text
Found 55 test(s)
OK
```

Chạy toàn bộ backend test:

```powershell
..\venv\Scripts\python.exe manage.py test
```

Kết quả lịch sử trong tài liệu gốc (không phải số lượng kiểm thử được xác nhận lại hiện tại):

```text
Found 139 test(s)
OK
```

Các test liên quan bao gồm:

- Giữ ghế.
- Giới hạn tối đa 5 ghế.
- Chặn ghế khác Event.
- Hủy và hết hạn Order.
- Sai số tiền.
- Thanh toán và tạo Ticket đúng một lần.
- Webhook lặp.
- Email không gửi lặp.
- Phục hồi thanh toán đến trễ khi ghế an toàn.
- Không lấy ghế từ Order khác.
- Reconcile PayOS.
- Chống IDOR khi đối soát Order người khác.
- PayOS PENDING không tạo vé.
- Sai dữ liệu PayOS không tạo vé.
- Vé chưa PAID không được check-in.

## 18. Tắt chế độ giả lập sau khi test

Bước 1. Mở lại:

`D:\SmartEventTicketing\backend\.env`

Bước 2. Đổi:

```dotenv
PAYOS_SKIP_SIGNATURE_CHECK=True
```

thành:

```dotenv
PAYOS_SKIP_SIGNATURE_CHECK=False
```

Bước 3. Nếu muốn dùng email thật, đặt:

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

Bước 4. Tắt và chạy lại backend:

```powershell
cd D:\SmartEventTicketing\backend
..\venv\Scripts\python.exe manage.py runserver
```

Bước 5. Kiểm tra:

```powershell
..\venv\Scripts\python.exe manage.py shell -c "from django.conf import settings; print(settings.PAYOS_SKIP_SIGNATURE_CHECK)"
```

Kết quả phải là:

```text
False
```

Sau đó hệ thống trở lại chế độ thật:

- Tạo Payment Link/QR PayOS thật.
- Kiểm tra chữ ký webhook thật.
- Đối soát giao dịch thật với PayOS.
- Không chấp nhận webhook giả không có chữ ký.

## 19. Tóm tắt nhanh

1. Đặt PAYOS_SKIP_SIGNATURE_CHECK=True trong .env.
2. Chọn console email hoặc SMTP email.
3. Restart backend.
4. Chạy frontend.
5. Đăng nhập Customer.
6. Chọn ghế và tạo Order PENDING.
7. Ghi lại Order ID và tổng tiền.
8. Nhấn "Thanh toán qua PayOS" để mở payment/result local.
9. Gửi webhook success giả bằng PowerShell hoặc Postman.
10. Kiểm tra trang báo thành công.
11. Kiểm tra Order PAID, Payment SUCCESS, Seat SOLD và Ticket.
12. Kiểm tra email.
13. Mở Vé của tôi và kiểm tra QR.
14. Gửi webhook lặp để kiểm tra idempotent.
15. Test check-in nếu cần.
16. Đổi PAYOS_SKIP_SIGNATURE_CHECK=False và restart backend sau khi test.
