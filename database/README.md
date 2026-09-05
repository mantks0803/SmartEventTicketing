# Database và dữ liệu mẫu

Hoàn tất [cài đặt project](../documents/SETUP.md) trước. Các lệnh dưới đây dùng **Windows CMD**; thay `%USERPROFILE%\SmartEventTicketing` bằng nơi bạn lưu project nếu khác. Database thật được PostgreSQL quản lý, không nằm trong thư mục này.

## 1. Chọn đúng script

| Script | Dữ liệu và tác động |
|---|---|
| [seed_data.py](seed_data.py) | Tạo 32 sự kiện tương lai, mỗi sự kiện có 10 ghế VIP và 15 ghế phổ thông, cùng một Organizer. **Xóa toàn bộ sự kiện cũ và dữ liệu liên quan**, đặt lại mật khẩu `demo_organizer` thành `123456`. Không có chốt tên database |
| [seed_admin_report_demo.py](seed_admin_report_demo.py) | Thêm **8 sự kiện quá khứ riêng**, 60 đơn PAID, 120 vé (72 đã check-in), Payment và tài khoản mẫu. Chỉ chạy trên `smart_booking_report_demo`; từ chối nạp trùng nếu đã có bộ báo cáo |

Hai script độc lập dùng model và cấu hình `backend/.env` hiện có. Migration vẫn nằm trong từng app backend. Các giao dịch `PAYOS-DEMO` là mô phỏng, không chuyển tiền hoặc gọi thanh toán thật. Seed báo cáo không thêm đơn/vé vào 32 sự kiện của seed cơ bản.

## 2. Tạo và chọn database demo riêng

Nếu dùng Docker theo SETUP và database này **chưa tồn tại**, chạy:

```cmd
docker exec smartticket-postgres psql -U postgres -d postgres -c "CREATE DATABASE smart_booking_report_demo;"
```

Nếu đã tồn tại, kiểm tra dữ liệu bên trong; **không xóa database để chạy lại từ đầu**. Với PostgreSQL cài trực tiếp, tạo database cùng tên bằng pgAdmin. Server phải có pgvector; xem SETUP nếu báo `extension "vector" is not available`.

Dừng backend, đổi trong `backend/.env`:

```dotenv
DB_NAME=smart_booking_report_demo
```

Nếu cùng server, giữ các biến kết nối còn lại. Docker theo SETUP dùng `127.0.0.1:5433`, PostgreSQL cài trực tiếp thường dùng `5432`. **Đổi `DB_NAME` chỉ đổi nơi kết nối, không sao chép dữ liệu từ database khác.**

Trước mọi lần chạy seed hoặc `--clear`, kích hoạt môi trường và kiểm tra kết nối thực tế:

```cmd
cd /d "%USERPROFILE%\SmartEventTicketing"
call venv\Scripts\activate.bat
cd backend
chcp 65001
set PYTHONUTF8=1
python manage.py shell -c "from django.db import connection; c=connection.settings_dict; print(c['NAME'], c['HOST'], c['PORT'])"
```

Tên phải là **`smart_booking_report_demo`**, host/cổng phải đúng server bạn chọn. Nếu khác, dừng và sửa cấu hình. Biến môi trường đã đặt trong CMD/Windows có thể ghi đè `.env`; lệnh kiểm tra không in mật khẩu.

## 3. Nạp lần đầu hay thêm báo cáo?

Các lệnh tiếp theo đều chạy tại `backend`. Chỉ chọn trường hợp phù hợp, không chạy lần lượt cả ba.

### A. Database mới, chưa có dữ liệu cần giữ

**Cảnh báo:** lệnh seed cơ bản dưới đây xóa mọi sự kiện đang có và các loại vé, ghế, đơn, vé phát hành, thanh toán liên quan theo quan hệ cascade. Chỉ dùng trên database demo mới, có thể bỏ đi.

```cmd
python manage.py migrate
python ..\database\seed_data.py
python ..\database\seed_admin_report_demo.py
```

Thứ tự: **migrate → seed cơ bản → seed báo cáo**. Không chạy seed cơ bản sau cùng vì nó xóa cả dữ liệu báo cáo. Nếu chỉ cần báo cáo, bỏ qua lệnh seed cơ bản.

### B. Đã có sự kiện, chưa có bộ báo cáo demo

Nếu database demo đã áp dụng đủ migration và có dữ liệu cần giữ, **chỉ chạy**:

```cmd
python ..\database\seed_admin_report_demo.py
```

Script giữ nguyên sự kiện đang có. Nếu trước đó có đúng 32 sự kiện cơ bản, kết quả là **40 sự kiện: 32 tương lai + 8 quá khứ**. Không chạy lại `seed_data.py`.

### C. Đã có bộ báo cáo

Không cần nạp lại khi mở website. Script từ chối nạp trùng khi phát hiện user tiền tố `report_demo_` hoặc sự kiện tiền tố `[DEMO REPORT]`.

**Chỉ khi chủ động muốn xóa bộ báo cáo**, sau khi đã kiểm tra database ở bước 2, mới chạy lệnh dưới. Nó xóa các sự kiện/user theo tiền tố trên và dữ liệu liên quan, kể cả dữ liệu bạn bổ sung dưới những tài khoản/sự kiện đó. Không hoàn tác được bằng script:

```cmd
python ..\database\seed_admin_report_demo.py --clear
```

`--clear` **chỉ xóa, không tự nạp lại**. Muốn tạo bộ mới, chạy lại lệnh ở trường hợp B; không cần seed cơ bản. Xem tham số bằng `python ..\database\seed_admin_report_demo.py --help` mà không tạo/xóa dữ liệu. Lệnh `python manage.py seed_admin_report_demo` không còn được hỗ trợ.

## 4. Tài khoản và xem kết quả

| Vai trò | Email | Mật khẩu |
|---|---|---|
| BTC của seed cơ bản | `organizer@smartevent.vn` | `123456` |
| Admin báo cáo | `report.demo.admin@smartticket.test` | `DemoAdmin@123` |
| BTC báo cáo số 1 | `report.demo.organizer1@smartticket.test` | `DemoOrganizer@123` |
| Customer số 1 | `report.demo.customer1@smartticket.test` | `DemoCustomer@123` |

Bộ báo cáo có 1 Admin, 4 BTC (số 1–4), 12 Customer (số 1–12); đổi số trong email để dùng tài khoản khác, mật khẩu giữ theo vai trò. Đây là tài khoản công khai **chỉ dùng local**, không dùng cho dữ liệu thật.

Khởi động backend/frontend theo SETUP, đăng xuất rồi đăng nhập lại. Giao dịch mẫu trải qua **6 tháng trước tháng chạy script**; chọn khoảng thời gian đó trên báo cáo. Các sự kiện quá khứ không xuất hiện trong chatbot tìm sự kiện tương lai.

## 5. Chuyển database, kiểm thử và dữ liệu khác

- Quay về database chính: dừng backend → đổi `DB_NAME=smart_booking_db` và biến môi trường ghi đè nếu có → khởi động lại → đăng xuất/đăng nhập lại. Không cần seed lại; chỉ migrate khi database chưa áp dụng các migration mới.
- Từ thư mục gốc, có thể gọi cùng script bằng `python database\seed_admin_report_demo.py`; đây không phải một bước nạp bổ sung.
- Test của script: [test_seed_admin_report_demo.py](../backend/orders/tests/test_seed_admin_report_demo.py). Từ `backend`, chạy `python manage.py test orders.tests.test_seed_admin_report_demo -v 2 --keepdb`. Test tích hợp dùng database test riêng, cần PostgreSQL/pgvector và quyền tạo database; không dùng database chứa dữ liệu cần giữ làm database test. Xem [hướng dẫn test](../documents/TEST_COMMANDS.md).
- Clone mới không cần bản dump cá nhân; xem [quy tắc backup](backups/README.md) nếu cần khôi phục dữ liệu riêng. Không xóa Docker volume để làm sạch dữ liệu: volume không phải bản sao lưu.
- Hai script trên không nạp dịch vụ/kiến thức chatbot. Markdown, JSON vẫn ở `backend/ai_agent/data/`; xem [hướng dẫn AI Agent](../backend/ai_agent/README.md).
