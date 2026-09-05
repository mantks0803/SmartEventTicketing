# HỆ THỐNG BÁN VÉ SỰ KIỆN TRỰC TUYẾN TÍCH HỢP CHATBOT THÔNG MINH

> Có thể truy cập tại: [https://smartticket-web.vercel.app/](https://smartticket-web.vercel.app/)

SmartEventTicketing hỗ trợ tìm sự kiện, đặt vé, thanh toán và quản lý tổ chức sự kiện. Chatbot kết hợp tài liệu RAG, dữ liệu PostgreSQL và Gemini để hỏi đáp, tìm sự kiện và tư vấn chi phí.

## 1. Chức năng chính

| Vai trò | Chức năng |
|---|---|
| Khách hàng | Đăng ký/đăng nhập, cập nhật hồ sơ, tìm và lọc sự kiện, chọn ghế, thanh toán PayOS, nhận email có QR/mã vé, xem vé đã mua |
| Ban tổ chức | Tạo sự kiện và loại vé, tải ảnh Cloudinary, gửi duyệt, xem doanh thu, check-in bằng mã vé |
| Quản trị viên | Duyệt sự kiện, quản lý/khóa tài khoản, báo cáo doanh thu, quản lý giao dịch, đối soát PayOS, quyết toán mô phỏng |
| Chatbot | Hỏi đáp hệ thống, tìm sự kiện/kiểm tra ghế, dự toán tổ chức và gợi ý giá vé hòa vốn |

Mỗi đơn tối đa **5 ghế**, giữ **10 phút**. Sự kiện cần Admin duyệt; vé chỉ phát hành khi đơn **PAID**. Doanh thu chỉ tính đơn PAID. BTC chỉ soát vé sự kiện của mình và mỗi vé chỉ check-in một lần.

## 2. Công nghệ

- **Backend:** Python, Django REST Framework, SimpleJWT; PostgreSQL và pgvector.
- **Frontend:** Vue 3, Vite, Pinia, Vue Router, Axios; Bootstrap, SweetAlert2, Chart.js.
- **Tích hợp:** PayOS, Cloudinary, SMTP; LangChain và Gemini.
- **Kiểm thử:** Django TestCase/APITestCase/TransactionTestCase; GitHub Actions kiểm tra backend và build frontend khi push/pull request vào `main`. Workflow chưa có bước deploy.

## 3. Cấu trúc dự án

~~~text
SmartEventTicketing/
├── backend/             API, models, migrations, tests và ai_agent
├── frontend/            Giao diện Vue; CSS riêng cạnh từng view/component
├── database/            Hai script tạo dữ liệu mẫu và hướng dẫn
├── documents/           Cài đặt, thanh toán và kiểm thử
├── docs/                Hướng dẫn/kết quả đánh giá RAG
├── .github/workflows/   Kiểm tra tự động trên GitHub
└── README.md
~~~

Test nằm trong `backend/<app>/tests/`. Markdown kiến thức và JSON chatbot giữ tại `backend/ai_agent/data/`, không di chuyển sang thư mục tài liệu.

## 4. Bắt đầu sử dụng

**Chỉ muốn trải nghiệm:** mở website phía trên, không cần cài đặt hoặc nhận API key.

**Cài trên máy lần đầu:** chuẩn bị Git, Python 3.12, Node.js theo [package.json](frontend/package.json) và PostgreSQL có pgvector. Hướng dẫn dùng Windows CMD, với Docker là lựa chọn database mặc định.

~~~bat
cd /d "%USERPROFILE%"
git clone https://github.com/mantks0803/SmartEventTicketing.git
cd SmartEventTicketing
~~~

Tiếp tục theo [hướng dẫn cài đặt từng bước](documents/SETUP.md) để tạo môi trường, cấu hình database, migrate và chạy hai server. Nếu đã có project, không clone đè; thay đường dẫn ví dụ bằng thư mục của bạn.

**Đã cài xong, muốn chạy lại:** bật PostgreSQL (hoặc Docker Desktop và container đã tạo), rồi mở hai cửa sổ CMD.

Backend:

~~~bat
cd /d "%USERPROFILE%\SmartEventTicketing"
venv\Scripts\activate.bat
set PYTHONUTF8=1
cd backend
python manage.py runserver
~~~

Frontend:

~~~bat
cd /d "%USERPROFILE%\SmartEventTicketing\frontend"
npm run dev
~~~

Mở địa chỉ Vite hiển thị, thường là [http://localhost:5173](http://localhost:5173). Không seed lại mỗi lần chạy web. Chỉ migrate khi database mới hoặc có migration mới.

### Dữ liệu mẫu và tích hợp

- [Seed cơ bản](database/seed_data.py) tạo 32 sự kiện nhưng **xóa toàn bộ sự kiện cũ cùng dữ liệu liên quan**. Chỉ dùng trên database mới, không có dữ liệu cần giữ.
- [Seed báo cáo](database/seed_admin_report_demo.py) thêm 8 sự kiện riêng, 60 đơn PAID và 120 vé; chỉ chạy trên `smart_booking_report_demo`. Xem [hướng dẫn nạp dữ liệu](database/README.md) để chọn đúng trường hợp.
- Database/tài khoản local độc lập với website online. Đổi tên database trong cấu hình không sao chép dữ liệu.
- Chưa có key vẫn chạy được phần cơ bản, nhưng thanh toán thật, upload ảnh, email thật và hỏi đáp AI cần [cấu hình dịch vụ](documents/SETUP.md). Không chia sẻ key bí mật, không commit `.env`, không đặt secret trong biến `VITE_*`.

## 5. Tài liệu theo nhu cầu

| Muốn làm gì? | Tài liệu |
|---|---|
| Cài lần đầu, cấu hình dịch vụ, xử lý lỗi | [SETUP](documents/SETUP.md) |
| Nạp sự kiện, thêm báo cáo, chuyển database | [Database](database/README.md) |
| Chạy và chỉnh giao diện | [Frontend](frontend/README.md) |
| Chuẩn bị dữ liệu, sử dụng và đánh giá chatbot | [AI Agent](backend/ai_agent/README.md) |
| Chạy test / thử thanh toán local | [Lệnh test](documents/TEST_COMMANDS.md) / [Thanh toán](documents/PAYMENT_TEST.md) |
| Xem kế hoạch, báo cáo và tài liệu khác | [Danh mục tài liệu](documents/README.md) |

Báo cáo kiểm thử ghi nhận kết quả tại thời điểm chạy, không tự cập nhật khi code thay đổi.

## 6. Giới hạn hiện tại

- Quyết toán BTC chỉ mô phỏng; không chuyển tiền hoặc hoàn tiền PayOS thật.
- Chưa có luồng sửa/xóa sự kiện hoàn chỉnh cho BTC; check-in hiện nhập mã, chưa tích hợp camera quét QR.
- Chatbot tìm sự kiện/tư vấn lấy điều kiện từ form, chưa tự hiểu mọi yêu cầu trong câu chat; widget chưa khôi phục toàn bộ lịch sử/card cũ khi tải lại.
- Chưa có kiểm thử trình duyệt tự động; build thành công không thay thế thao tác thử giao diện.
- Dữ liệu, giá dịch vụ và mật khẩu mẫu chỉ dùng cho demo.
