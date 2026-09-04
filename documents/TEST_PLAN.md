# Kế hoạch kiểm thử SmartEventTicketing

Các phiên bản môi trường và kết quả đã ghi nhận thuộc lần kiểm thử trước; xem [báo cáo kiểm thử lịch sử](TEST_REPORT.md). Việc sắp xếp tài liệu không xác nhận lại trạng thái kiểm thử hiện tại.

## 1. Mục tiêu

Kế hoạch kiểm tra các luồng cốt lõi của Customer, Organizer, Admin và AI Agent: xác thực, phân quyền, sự kiện, ghế, thanh toán, vé QR, báo cáo, quản trị và chatbot RAG.

## 2. Phạm vi

- Backend Django REST Framework và PostgreSQL/pgvector.
- Frontend Vue 3 được kiểm tra khả năng build production bằng Vite.
- PayOS, Cloudinary, email và Gemini được mock trong test tự động.
- Race condition dùng PostgreSQL thật để kiểm tra `select_for_update()`.
- RAG evaluation thật tách khỏi CI vì sử dụng quota Gemini.
- Chưa bao gồm load test, Selenium/E2E trình duyệt, deploy production và chuyển tiền thật.

## 3. Môi trường chuẩn

- CI: Python 3.12, Node.js 22.18.0, PostgreSQL 16 với pgvector.
- Local gần nhất: Python 3.14.6, Node.js 24.14.1, PostgreSQL 18.4.
- Event ở các trạng thái `PENDING`, `PUBLISHED`, `CANCELLED`.
- Order ở các trạng thái `PENDING`, `PAID`, `CANCELLED`, `EXPIRED`, `REFUNDED`.
- Customer A/B, Organizer A/B và Admin để kiểm tra ownership/IDOR.
- Test không dùng `sleep()`; thời gian giữ ghế được đưa trực tiếp về quá khứ.

## 4. Điều kiện đạt

- `python manage.py check` không có lỗi.
- `python manage.py makemigrations --check --dry-run` báo không có thay đổi.
- Toàn bộ backend tests pass.
- `npm run build` hoàn tất không có lỗi biên dịch.
- Không có request test nào gọi PayOS, Cloudinary, SMTP hoặc Gemini thật.
- Race condition chỉ cho đúng một Customer giữ được cùng một ghế.

## 5. Ma trận test case

| STT | Chức năng | Kịch bản | Kết quả kỳ vọng |
|---:|---|---|---|
| TC-01 | Đăng ký | Customer đăng ký hợp lệ | Tạo User/Customer, mật khẩu được hash, trả 201 |
| TC-02 | Đăng ký | Organizer đăng ký hợp lệ | Tạo User/Organizer, trả 201 |
| TC-03 | Đăng ký | Trùng username, email hoặc số điện thoại | Trả 400, không tạo dữ liệu trùng |
| TC-04 | Đăng nhập | Email/username và mật khẩu đúng | Trả access, refresh token và role đúng |
| TC-05 | Khóa tài khoản | `status=False` hoặc `is_active=False` | Không đăng nhập và token cũ không dùng được ở API bảo vệ |
| TC-06 | Phân quyền | Customer gọi API Organizer/Admin | Trả 403, dữ liệu không thay đổi |
| TC-07 | Admin user | Danh sách, tìm kiếm, lọc role/status và phân trang | Trả đúng tài khoản và thống kê |
| TC-08 | Admin user | Xem chi tiết Customer/Organizer | Trả profile và statistics đúng, không lộ password |
| TC-09 | Admin user | Khóa/mở khóa tài khoản | Đồng bộ `status` và `is_active`; chặn tự khóa/superuser |
| TC-10 | Event công khai | Danh sách có PUBLISHED/PENDING/CANCELLED | Chỉ PUBLISHED được công khai |
| TC-11 | Event công khai | Phân trang, tìm kiếm và lọc category | `count`, `next` và kết quả đúng điều kiện |
| TC-12 | Event chi tiết | Truy cập event chưa duyệt | Trả 404 để không lộ dữ liệu |
| TC-13 | Event nổi bật | Event quá khứ hoặc chưa duyệt | Chỉ trả event PUBLISHED trong tương lai |
| TC-14 | Organizer create | Tạo event, nhiều loại vé và ghế | Event PENDING; TicketType/Seat được tạo đầy đủ |
| TC-15 | Transaction event | Cấu hình hàng ghế bị trùng | Trả 400 và rollback toàn bộ dữ liệu dở dang |
| TC-16 | Ownership event | Organizer xem event của mình | Không trả event của Organizer khác |
| TC-17 | Thumbnail | Upload JPG/PNG/WEBP hợp lệ | Mock Cloudinary; trả secure URL |
| TC-18 | Admin moderation | Approve/reject event PENDING | Chuyển đúng trạng thái; xử lý lặp trả conflict |
| TC-19 | Sơ đồ ghế | Xem ghế event PUBLISHED | Đúng loại vé, hàng, số, giá và trạng thái |
| TC-20 | Sơ đồ ghế | Event chưa duyệt hoặc bị hủy | API công khai trả 404 |
| TC-21 | Giữ ghế | Customer giữ ghế AVAILABLE | Tạo Order PENDING và khóa ghế khoảng 10 phút |
| TC-22 | Giữ ghế | ID trùng, khác event hoặc hơn 5 ghế | Trả 400, không tạo đơn sai |
| TC-23 | Race condition | Hai Customer đồng thời giữ cùng ghế | Một thành công, một `seat_locked`; chỉ một OrderItem |
| TC-24 | Hết hạn | Order vượt quá 10 phút | Order EXPIRED và ghế trở lại AVAILABLE |
| TC-25 | Hủy đơn | Customer hủy Order PENDING | Order CANCELLED và giải phóng đúng ghế |
| TC-26 | PayOS link | Order PENDING hợp lệ | Mock SDK; trả checkout URL đúng order |
| TC-27 | PayOS webhook | Chữ ký hoặc số tiền sai | Trả lỗi; không tạo Payment/Ticket |
| TC-28 | PayOS webhook | Gửi cùng webhook hai lần | Chỉ một Payment, một bộ Ticket và một email |
| TC-29 | Reconcile | PayOS trả PAID hợp lệ | Kiểm tra orderCode/amount/reference rồi chuyển PAID |
| TC-30 | IDOR order | Customer B truy cập Order A | Trả 404; Order A không thay đổi |
| TC-31 | Vé của tôi | Hai khách và một Order PENDING | Chỉ trả Ticket thuộc Order PAID của đúng Customer |
| TC-32 | Check-in | Organizer chủ event quét QR PAID | Thành công, lưu `checked_in_at` |
| TC-33 | Check-in | Quét lại cùng QR | Trả 400, không check-in lần hai |
| TC-34 | Check-in permission | Customer hoặc Organizer khác quét | Trả 403; Ticket không thay đổi |
| TC-35 | Organizer report | Báo cáo event thuộc Organizer | Chỉ tính Order PAID, ghế và check-in đúng |
| TC-36 | Organizer report | Xem báo cáo event người khác | Trả 404 để tránh lộ event |
| TC-37 | Admin revenue | Lọc ngày/category/event/Organizer | Tất cả KPI và series dùng cùng bộ Order PAID |
| TC-38 | Admin payment | Danh sách/detail và cảnh báo bất thường | Phân trang đúng, cảnh báo được tính từ dữ liệu hiện có |
| TC-39 | Admin reconcile | Admin đối soát Order bất kỳ | Tái sử dụng luồng xác nhận; chống Payment/Ticket trùng |
| TC-40 | Payout demo | Event đã diễn ra và có Order PAID | Admin đánh dấu `is_payout_completed=True` |
| TC-41 | Payout demo | Xác nhận lần hai/event chưa bắt đầu | Trả conflict; không thay đổi dữ liệu khác |
| TC-42 | AI seed | Chạy seed dịch vụ nhiều lần | `update_or_create`, không tạo code trùng |
| TC-43 | RAG index | Chunk tài liệu và embedding đúng dimension | Tạo index hợp lệ; lỗi không phá index cũ |
| TC-44 | RAG retrieval | Customer/Organizer hỏi đúng tài liệu | Chỉ lấy tài liệu đúng audience hoặc ALL |
| TC-45 | AI GENERAL | Gửi câu hỏi có tài liệu | Trả answer/sources và lưu session/messages |
| TC-46 | AI RECOMMEND | Tìm event hoặc kiểm tra ghế | Query DB đúng filter, không gọi Gemini |
| TC-47 | AI PLAN | Dự toán và giá vé | Tính bằng Python/DB; Gemini chỉ diễn giải structured data |
| TC-48 | AI session | User khác đọc hoặc tiếp tục session | Trả 404 chống IDOR |
| TC-49 | AI memory | Hội thoại nhiều tin nhắn | Chỉ gửi tối đa 8 tin gần nhất theo đúng thứ tự |
| TC-50 | RAG evaluation | Dataset có câu đúng nguồn và ngoài phạm vi | Tính đúng Hit@4/source/no-answer và report |

## 6. Vị trí test tự động

| Nhóm | Thư mục |
|---|---|
| Authentication và Admin user | `backend/authentication/tests/` |
| Event công khai, Organizer, upload và moderation | `backend/events/tests/` |
| Ghế và race condition | `backend/seating/tests/` |
| Order, PayOS, ticket, reports, payment và payout | `backend/orders/tests/` |
| RAG, tools, chat API và evaluation | `backend/ai_agent/tests/` |

## 7. Cách chạy

```bat
cd /d <duong-dan-project>\backend
..\venv\Scripts\activate.bat
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test -v 2
```

Frontend:

```bat
cd /d <duong-dan-project>\frontend
npm ci
npm run build
```

Chi tiết lệnh theo app/file xem [TEST_COMMANDS.md](TEST_COMMANDS.md).

## 8. Kiểm thử thủ công còn cần

- Thanh toán ngân hàng và webhook PayOS qua public HTTPS.
- Email SMTP thật và kiểm tra spam.
- Upload Cloudinary bằng tài khoản thật.
- Chatbot Gemini thật, quota và chất lượng câu trả lời.
- Camera QR trên thiết bị thật.
- Responsive và luồng end-to-end trên trình duyệt.
- Payout hiện chỉ mô phỏng; không kiểm tra chuyển tiền ngân hàng.
