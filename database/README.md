# Database và dữ liệu mẫu

Hoàn tất [SETUP](../documents/SETUP.md) trước. Thư mục này chứa script, không chứa database đang chạy; PostgreSQL quản lý dữ liệu. Các lệnh dưới đây dùng **Windows CMD**.

## 1. Chọn script

| Script | Dữ liệu tạo ra | Lưu ý |
|---|---|---|
| [seed_data.py](seed_data.py) | 32 sự kiện tương lai, mỗi sự kiện 25 ghế và một BTC mẫu | **Xóa toàn bộ sự kiện cũ và dữ liệu liên quan**; đặt lại mật khẩu `demo_organizer` thành `123456` |
| [seed_admin_report_demo.py](seed_admin_report_demo.py) | Thêm 8 sự kiện quá khứ riêng, 60 đơn PAID, 120 vé (72 đã check-in), Payment và tài khoản | Chỉ chạy trên `smart_booking_report_demo`; từ chối nạp trùng |

Hai script độc lập. Seed báo cáo không thêm vé vào 32 sự kiện cơ bản; giao dịch `PAYOS-DEMO` là mô phỏng, không gọi PayOS hoặc chuyển tiền.

## 2. Chuẩn bị database demo riêng

Nếu dùng Docker theo SETUP và database **chưa tồn tại**:

```cmd
docker exec smartticket-postgres psql -U postgres -d postgres -c "CREATE DATABASE smart_booking_report_demo;"
```

Nếu dùng PostgreSQL cài trực tiếp, tạo database cùng tên bằng pgAdmin; server cần pgvector. Database đã tồn tại thì kiểm tra dữ liệu, không xóa để làm lại.

Dừng backend, sửa `backend/.env`:

```dotenv
DB_NAME=smart_booking_report_demo
```

Giữ user/password/host/port nếu cùng server. Docker theo SETUP dùng cổng **5433**, PostgreSQL trực tiếp thường là **5432**. Đổi tên database không sao chép dữ liệu.

Mở CMD, thay đường dẫn nếu cần, rồi kiểm tra database trước khi nạp:

```cmd
cd /d "%USERPROFILE%\SmartEventTicketing"
venv\Scripts\activate.bat
set PYTHONUTF8=1
cd backend
python manage.py shell -c "from django.db import connection; c=connection.settings_dict; print(c['NAME'], c['HOST'], c['PORT'])"
```

Tên phải là **`smart_booking_report_demo`**, host/cổng phải đúng server. Nếu khác, dừng và kiểm tra `.env` cùng biến môi trường CMD/Windows có thể ghi đè nó.

## 3. Nạp dữ liệu — chọn đúng trường hợp

Các lệnh chạy tại `backend/`, sau bước kiểm tra trên.

**Database demo mới, chưa có dữ liệu cần giữ:**

```cmd
python manage.py migrate
python ..\database\seed_data.py
python ..\database\seed_admin_report_demo.py
```

Kết quả: 32 sự kiện tương lai + 8 sự kiện quá khứ. **Seed cơ bản xóa sự kiện, ghế, đơn, vé và thanh toán liên quan: không chạy nó sau seed báo cáo hoặc trên dữ liệu cần giữ.** Nếu chỉ cần báo cáo, bỏ qua lệnh `seed_data.py`.

**Đã có sự kiện, chưa có bộ báo cáo:** áp dụng migration mới nếu cần, rồi chỉ chạy:

```cmd
python ..\database\seed_admin_report_demo.py
```

**Đã có bộ báo cáo:** không nạp lại mỗi lần mở web. Script chặn nạp trùng khi có user `report_demo_` hoặc sự kiện `[DEMO REPORT]`.

## 4. Đăng nhập và xem kết quả

| Vai trò | Email | Mật khẩu |
|---|---|---|
| BTC cơ bản | `organizer@smartevent.vn` | `123456` |
| Admin báo cáo | `report.demo.admin@smartticket.test` | `DemoAdmin@123` |
| BTC báo cáo số 1 | `report.demo.organizer1@smartticket.test` | `DemoOrganizer@123` |
| Customer số 1 | `report.demo.customer1@smartticket.test` | `DemoCustomer@123` |

Bộ báo cáo có 4 BTC và 12 Customer; thay số trong email để dùng tài khoản khác, mật khẩu giữ theo vai trò. **Chỉ dùng tài khoản mẫu ở local.**

Khởi động hai server theo [README chính](../README.md#cài-và-chạy), đăng xuất và đăng nhập lại. Báo cáo dùng giao dịch trong **6 tháng trước tháng chạy script**; chọn bộ lọc thời gian tương ứng. Sự kiện quá khứ không được chatbot gợi ý như sự kiện sắp diễn ra.

## 5. Chuyển database hoặc xóa bộ báo cáo

- Chuyển về database chính: dừng backend → đổi `DB_NAME=smart_booking_db` và kiểm tra biến môi trường ghi đè → khởi động lại → đăng nhập lại. Chỉ migrate nếu database thiếu migration; không seed lại.
- **Xóa bộ báo cáo là tùy chọn, không thuộc bước cài đặt.** Kiểm tra đúng database ở bước 2 trước khi chạy lệnh dưới:

```cmd
python ..\database\seed_admin_report_demo.py --clear
```

Lệnh xóa user/sự kiện theo hai tiền tố trên **và dữ liệu liên quan, kể cả dữ liệu bạn thêm dưới chúng**. Không hoàn tác bằng script, không tự nạp lại. Muốn tạo bộ mới, chạy lại riêng seed báo cáo. Lệnh cũ `python manage.py seed_admin_report_demo` không còn dùng.

Hai script không nạp dữ liệu chatbot; xem [AI Agent](../backend/ai_agent/README.md). Clone mới không cần SQL backup; nếu khôi phục dữ liệu riêng, đọc [hướng dẫn backup](backups/README.md).
