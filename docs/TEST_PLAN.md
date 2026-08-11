# Kế hoạch kiểm thử Smart Event Ticketing

## 1. Mục tiêu

Kế hoạch này kiểm tra các luồng quan trọng nhất của hệ thống: xác thực và phân quyền, danh sách sự kiện, chọn và giữ ghế, thanh toán PayOS, phát hành vé QR và soát vé.

## 2. Phạm vi

- Backend: Django 6, Django REST Framework và PostgreSQL.
- Frontend: Vue 3 được kiểm tra khả năng biên dịch bằng Vite.
- PayOS, Cloudinary và email được mock hoặc dùng memory backend trong test tự động.
- Không chuyển khoản thật, không upload ảnh thật và không gửi email thật khi chạy test.
- Chưa bao gồm kiểm thử tải lớn, kiểm thử trình duyệt tự động và triển khai production.

## 3. Môi trường và dữ liệu mẫu

- Python 3.12.
- Node.js 22.18.0.
- PostgreSQL 16 trong GitHub Actions.
- Customer A, Customer B, Organizer A, Organizer B và Admin.
- Event ở ba trạng thái `PENDING`, `PUBLISHED`, `CANCELLED`.
- Loại vé VIP giá 100.000 đồng và các ghế A-1 đến A-6.
- Không dùng `sleep()` để chờ 10 phút; test đưa `expires_at` về quá khứ.

## 4. Điều kiện đạt

- Toàn bộ test backend phải pass.
- Chạy trong thư mục `backend/`, lệnh `python manage.py check` không báo lỗi.
- Không có migration chưa tạo.
- `npm run build` hoàn tất mà không có lỗi biên dịch.
- Race condition phải có đúng một đơn giữ ghế thành công.

## 5. Ma trận test case

| STT | Chức năng | Mô tả kịch bản | Các bước thực hiện | Kết quả kỳ vọng |
|---:|---|---|---|---|
| TC-01 | Đăng ký Customer | Đăng ký với dữ liệu hợp lệ | Gửi `POST /api/auth/register/customer/` với họ tên, email, số điện thoại và mật khẩu | Trả 201; tạo `User` loại CUSTOMER và hồ sơ `Customer`; mật khẩu được mã hóa |
| TC-02 | Đăng ký Organizer | Đăng ký ban tổ chức hợp lệ | Gửi `POST /api/auth/register/organizer/` kèm tên công ty và tài khoản ngân hàng | Trả 201; tạo `User` loại ORGANIZER và hồ sơ `Organizer` |
| TC-03 | Đăng ký | Email đã tồn tại | Tạo một tài khoản, sau đó đăng ký tài khoản mới bằng cùng email | Trả 400 và không tạo thêm tài khoản trùng |
| TC-04 | Đăng nhập | Đăng nhập bằng email và mật khẩu đúng | Gửi `POST /api/auth/login/` | Trả access token, refresh token và đúng role |
| TC-05 | Đăng nhập | Sai mật khẩu hoặc tài khoản `is_active=False` | Gửi thông tin đăng nhập không hợp lệ | Trả 400 và không cấp token |
| TC-06 | Phân quyền | Customer gọi API của Organizer hoặc Admin | Xác thực Customer rồi gọi API tạo sự kiện, upload ảnh hoặc duyệt sự kiện | Trả 403; dữ liệu không thay đổi |
| TC-07 | Danh sách sự kiện | Chỉ hiển thị sự kiện đã duyệt | Tạo event PUBLISHED, PENDING và CANCELLED rồi gọi `GET /api/events/` | Chỉ trả event PUBLISHED |
| TC-08 | Phân trang | Danh sách có hơn 12 sự kiện | Gọi lần lượt `?page=1` và `?page=2` | `count`, `next` và số bản ghi từng trang chính xác |
| TC-09 | Tìm kiếm | Tìm theo tiêu đề hoặc địa điểm | Gọi `GET /api/events/?search=...` | Chỉ trả các event có tiêu đề hoặc địa điểm phù hợp |
| TC-10 | Lọc danh mục | Lọc theo MUSIC hoặc WORKSHOP | Gọi `GET /api/events/?category=WORKSHOP` | Chỉ trả đúng danh mục yêu cầu |
| TC-11 | Chi tiết sự kiện | Truy cập event chưa duyệt hoặc bị hủy | Gọi `GET /api/events/{id}/` cho PENDING và CANCELLED | API công khai trả 404 |
| TC-12 | Sự kiện nổi bật | Lọc event tương lai đã duyệt | Gọi `GET /api/events/featured/` với event quá khứ và PENDING | Chỉ trả event PUBLISHED có thời gian tương lai |
| TC-13 | Tạo sự kiện | Organizer tạo event và nhiều loại vé | Gửi `POST /api/events/create/` với hai loại vé và cấu hình hàng ghế | Trả 201; tạo Event, TicketType, Seat; event ở trạng thái PENDING |
| TC-14 | Transaction tạo event | Hai loại vé tạo hàng ghế trùng | Gửi hai `row_prefix` tạo cùng tên hàng | Trả 400; không để lại Event hoặc Seat dở dang |
| TC-15 | Quyền sở hữu event | Organizer xem danh sách của mình | Tạo event cho hai Organizer rồi gọi `GET /api/events/organizer/events/` | Chỉ trả event thuộc Organizer đang đăng nhập |
| TC-16 | Admin duyệt event | Duyệt event PENDING | Admin gọi `POST /api/events/admin/{id}/approve/` | Event thành PUBLISHED và xuất hiện qua API công khai |
| TC-17 | Upload thumbnail | Organizer upload ảnh hợp lệ | Mock Cloudinary rồi gửi JPG qua `POST /api/events/upload-thumbnail/` | Trả URL ảnh; không gọi Cloudinary thật trong test |
| TC-18 | Sơ đồ ghế | Xem ghế của event PUBLISHED | Gọi `GET /api/seats/event/{event_id}/` | Ghế được sắp theo loại vé, hàng và số; có giá và trạng thái đúng |
| TC-19 | Giữ ghế | Customer giữ một ghế còn trống | Gửi `POST /api/orders/hold/` với `seat_ids` | Trả 201; tạo Order PENDING; ghế LOCKED khoảng 10 phút |
| TC-20 | Giữ ghế không hợp lệ | Chọn ghế khác event, ID trùng hoặc hơn 5 ghế | Gửi từng payload không hợp lệ | Trả 400; không tạo đơn sai |
| TC-21 | Khóa ghế tuần tự | Hai Customer lần lượt giữ cùng ghế | Customer A giữ trước, Customer B giữ sau | Customer B nhận lỗi `seat_locked`; chỉ một đơn giữ ghế |
| TC-22 | Race condition | Hai luồng giữ cùng ghế đồng thời | Dùng hai thread, hai kết nối DB và `Barrier` để bắt đầu cùng lúc | Một luồng thành công, một luồng nhận `seat_locked`; chỉ có một Order và OrderItem |
| TC-23 | Hết hạn giữ ghế | Đơn vượt quá 10 phút | Đưa `expires_at` và `locked_until` về quá khứ rồi chạy xử lý hết hạn | Order thành EXPIRED; ghế trở lại AVAILABLE |
| TC-24 | Tạo liên kết thanh toán | Tạo link cho order PENDING hợp lệ | Bật chế độ PayOS test và gọi `POST /api/orders/{id}/payos-link/` | Trả `checkoutUrl` và lưu URL vào order, không gọi ngân hàng thật |
| TC-25 | Xác nhận thanh toán | Thanh toán đúng số tiền | Xác nhận order bằng mã giao dịch giả lập | Order PAID; ghế SOLD; tạo Payment và Ticket |
| TC-26 | Chữ ký webhook | Webhook có chữ ký không hợp lệ | Mock hàm xác minh PayOS trả lỗi rồi gửi webhook | Trả 400; order vẫn PENDING; không tạo Payment hoặc Ticket |
| TC-27 | Webhook lặp | PayOS gửi cùng webhook hai lần | Gửi hai request có cùng transaction reference | Chỉ tạo một Payment, một bộ Ticket và một email |
| TC-28 | Đối soát PayOS | Return URL kiểm tra lại giao dịch PAID | Mock PayOS trả PAID rồi gọi `POST /api/orders/{id}/reconcile-payos/` | Backend kiểm tra orderCode, số tiền và transaction trước khi chuyển PAID |
| TC-29 | IDOR đơn hàng | Customer B truy cập đơn của Customer A | Customer B gọi API chi tiết, hủy và đối soát order A | Trả 404; order A không thay đổi |
| TC-30 | Ví vé | Chỉ lấy vé PAID của chính Customer | Tạo vé paid của hai khách và một vé trong order PENDING rồi gọi `GET /api/orders/my-tickets/` | Chỉ trả vé PAID thuộc Customer hiện tại |
| TC-31 | Soát vé | Organizer chủ event quét QR hợp lệ | Gọi `POST /api/orders/check-in/` với QR của vé PAID | Trả 200; `is_checked_in=True` và có `checked_in_at` |
| TC-32 | Chống check-in lặp | Quét cùng QR lần thứ hai | Gửi lại QR đã check-in | Trả 400; vé không bị cập nhật sai lần nữa |
| TC-33 | Quyền soát vé | Customer hoặc Organizer khác quét QR | Đăng nhập sai vai trò/chủ sở hữu rồi gọi API check-in | Trả 403; vé vẫn chưa check-in |
| TC-34 | QR không hợp lệ | Quét chuỗi QR không tồn tại | Gửi mã bất kỳ vào API check-in | Trả 404 và không thay đổi dữ liệu vé |

## 6. Vị trí test tự động

| Nhóm | Thư mục/file |
|---|---|
| Đăng ký và đăng nhập | `backend/authentication/tests/` |
| Sự kiện công khai, Organizer, thumbnail và Admin | `backend/events/tests/` |
| Sơ đồ ghế và race condition | `backend/seating/tests/` |
| Giữ ghế, PayOS, thanh toán, vé và check-in | `backend/orders/tests/` |

## 7. Cách chạy ở máy cá nhân

Chạy toàn bộ backend test:

```powershell
cd backend
..\venv\Scripts\python.exe manage.py test -v 2
```

Chạy riêng từng app:

```powershell
cd backend
..\venv\Scripts\python.exe manage.py test authentication.tests -v 2
..\venv\Scripts\python.exe manage.py test events.tests -v 2
..\venv\Scripts\python.exe manage.py test seating.tests -v 2
..\venv\Scripts\python.exe manage.py test orders.tests -v 2
```

Chạy một file hoặc một test cụ thể:

```powershell
cd backend
..\venv\Scripts\python.exe manage.py test seating.tests.test_race_condition -v 2
..\venv\Scripts\python.exe manage.py test orders.tests.test_check_in.CheckInTests.test_ticket_cannot_be_checked_in_twice -v 2
```

Kiểm tra frontend:

```powershell
cd frontend
npm ci
npm run build
```

> Test race condition cần PostgreSQL vì SQLite không mô phỏng đúng khóa dòng `select_for_update()`.

## 8. Rủi ro đã biết

- Model tài khoản có cả `status` và `is_active`, nhưng luồng đăng nhập hiện dùng `is_active` để khóa đăng nhập. Test tự động bám theo hành vi này.
- Workflow chưa triển khai website lên server; nó chỉ test backend và build frontend.
- Giao diện trình duyệt và thanh toán ngân hàng thật vẫn cần kiểm thử thủ công trước khi demo.
