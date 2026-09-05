# HỆ THỐNG BÁN VÉ SỰ KIỆN TRỰC TUYẾN TÍCH HỢP CHATBOT THÔNG MINH

> Có thể truy cập tại: [https://smartticket-web.vercel.app/](https://smartticket-web.vercel.app/)

SmartEventTicketing là đồ án quản lý bán vé sự kiện, từ tìm sự kiện, đặt ghế và thanh toán đến phát hành vé, check-in và báo cáo doanh thu. Chatbot hỗ trợ hỏi đáp, tìm sự kiện và tư vấn chi phí tổ chức.

## Chức năng chính

| Người dùng | Chức năng |
|---|---|
| Khách hàng | Đăng ký/đăng nhập, tìm sự kiện, chọn ghế, thanh toán PayOS, nhận email QR/mã vé và xem vé đã mua |
| Ban tổ chức | Tạo sự kiện và loại vé, tải ảnh, gửi duyệt, xem doanh thu, check-in bằng mã vé |
| Admin | Duyệt sự kiện, quản lý tài khoản, xem doanh thu, quản lý thanh toán và quyết toán mô phỏng |
| Chatbot | Hỏi đáp bằng RAG, tìm sự kiện/ghế từ database, dự toán chi phí và giá vé |

Mỗi đơn tối đa **5 ghế**, giữ **10 phút**. Vé chỉ phát hành khi thanh toán được xác nhận; BTC chỉ check-in vé sự kiện của mình.

**Công nghệ:** Django REST Framework, PostgreSQL/pgvector; Vue 3, Bootstrap, SweetAlert2; PayOS, Cloudinary, SMTP; LangChain và Gemini.

## Cài và chạy

- **Chỉ muốn trải nghiệm:** mở website phía trên, không cần cài đặt.
- **Cài trên máy lần đầu:** làm theo [hướng dẫn cài đặt từng bước](documents/SETUP.md), dùng Windows CMD và PostgreSQL quản lý bằng pgAdmin. Nếu đã cài PostgreSQL/pgAdmin thì dùng lại, không cần cài Docker. Docker là [lựa chọn riêng](documents/SETUP.md#dùng-docker-thay-cho-postgresql-cài-trực-tiếp); không cần bản sao database của chủ dự án.
- **Đã cài xong:** bật PostgreSQL. Nếu dùng Docker theo hướng dẫn, mở Docker Desktop rồi chạy `docker start smartticket-postgres`. Mở hai cửa sổ CMD:

Backend:

```cmd
cd /d "%USERPROFILE%\SmartEventTicketing"
venv\Scripts\activate.bat
set PYTHONUTF8=1
cd backend
python manage.py runserver
```

Frontend:

```cmd
cd /d "%USERPROFILE%\SmartEventTicketing\frontend"
npm run dev
```

Thay đường dẫn nếu lưu project ở nơi khác. Mở địa chỉ Vite hiển thị, thường là [http://localhost:5173](http://localhost:5173). Không cần nạp dữ liệu mẫu mỗi lần chạy; chỉ migrate khi database mới hoặc có migration mới.

## Thư mục và hướng dẫn

| Thư mục/tài liệu | Nội dung |
|---|---|
| `backend/` | Django API, models, migrations, test trong từng app |
| [frontend/](frontend/README.md) | Vue 3, cách chạy và build |
| [database/](database/README.md) | Hai script dữ liệu mẫu, tài khoản demo và chuyển database |
| [documents/](documents/README.md) | [Cài đặt](documents/SETUP.md), [chạy test](documents/TEST_COMMANDS.md), [thử thanh toán](documents/PAYMENT_TEST.md) |
| [backend/ai_agent/](backend/ai_agent/README.md) | Chatbot, Markdown kiến thức và JSON dịch vụ |
| [docs/](docs/RAG_EVALUATION.md) | Hướng dẫn/kết quả đánh giá RAG |
| `.github/workflows/` | CI chạy test backend và build frontend, chưa tự deploy |

## Lưu ý trước khi dùng

- `seed_data.py` **xóa sự kiện cũ và dữ liệu liên quan**. Chỉ chạy trên database mới không có dữ liệu cần giữ; xem [hướng dẫn database](database/README.md).
- Database local độc lập với website online. Tài khoản và dữ liệu mẫu chỉ dùng cho demo.
- Thanh toán thật, upload ảnh, gửi email thật và hỏi đáp AI cần cấu hình dịch vụ riêng. Không chia sẻ API key, commit `.env` hoặc đặt secret trong `VITE_*`.
- Quyết toán chỉ mô phỏng, không chuyển/hoàn tiền thật. BTC chưa có luồng sửa/xóa sự kiện hoàn chỉnh; check-in hiện nhập mã, chưa quét bằng camera.
- Chatbot tìm sự kiện/tư vấn dùng thông tin từ form, chưa tự suy ra đầy đủ từ câu chat. Build thành công không thay thế kiểm thử giao diện.
