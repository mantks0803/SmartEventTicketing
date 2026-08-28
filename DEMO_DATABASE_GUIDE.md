# Hướng dẫn database demo cho SmartEventTicketing

Database demo được tách hoàn toàn khỏi database chính:

```text
Database chính: smart_booking_db
Database demo:  smart_booking_report_demo
```

Management command chỉ chấp nhận chạy khi database hiện tại có đúng tên
`smart_booking_report_demo`. Vì vậy nếu quên chuyển database, command sẽ dừng và
không ghi dữ liệu vào `smart_booking_db`.

## 1. Dữ liệu demo được tạo

Lệnh seed tạo:

- 1 tài khoản Admin.
- 4 tài khoản Organizer.
- 12 tài khoản Customer.
- 8 sự kiện, phủ đủ MUSIC, WORKSHOP, ENTERTAINMENT và SPORTS.
- 2 loại vé và 50 ghế cho mỗi sự kiện.
- 60 đơn PAID trải đều trong 6 tháng.
- 120 OrderItem, Ticket và ghế SOLD.
- 60 Payment SUCCESS có số tiền khớp đơn hàng.
- 72 vé đã check-in.
- 3 sự kiện đã quyết toán và 5 sự kiện chờ quyết toán.

Tất cả Order, Payment, Ticket, Seat và thời gian check-in được tạo đồng bộ theo
đúng ràng buộc nghiệp vụ hiện tại.

## 2. Kiểm tra PostgreSQL trên Windows

Mở Command Prompt và chạy:

```cmd
"C:\Program Files\PostgreSQL\18\bin\psql.exe" --version
"C:\Program Files\PostgreSQL\18\bin\pg_isready.exe" -h localhost -p 5432
```

Nếu PostgreSQL được cài ở phiên bản khác, thay số `18` trong đường dẫn bằng
phiên bản đang có trên máy.

Nếu máy chưa có PostgreSQL:

1. Tải bộ cài PostgreSQL dành cho Windows.
2. Khi cài, chọn PostgreSQL Server, pgAdmin 4 và Command Line Tools.
3. Giữ port mặc định `5432` nếu port này chưa bị ứng dụng khác sử dụng.
4. Đặt mật khẩu cho user `postgres` và ghi nhớ mật khẩu.
5. Cài xong, chạy lại hai lệnh kiểm tra phía trên.

File backup có extension `vector`. Có thể kiểm tra PostgreSQL hiện tại bằng:

```cmd
"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d smart_booking_db -c "SELECT extversion FROM pg_extension WHERE extname = 'vector';"
```

Nếu lệnh trả về phiên bản thì pgvector đã sẵn sàng. Nếu báo extension không tồn
tại khi restore trên máy mới, cần cài pgvector cho đúng phiên bản PostgreSQL
trước khi tiếp tục.

## 3. Tạo backup mới cho database chính

File `data_27_8.sql` là backup ngày 27/08/2026. Nên tạo thêm một backup mới
trước khi thao tác:

```cmd
if not exist "D:\SmartEventTicketing\backups" mkdir "D:\SmartEventTicketing\backups"

"C:\Program Files\PostgreSQL\18\bin\pg_dump.exe" -U postgres -h localhost -p 5432 -F c -d smart_booking_db -f "D:\SmartEventTicketing\backups\smart_booking_before_demo.dump"
```

Lệnh chỉ đọc database chính và tạo file backup, không xóa dữ liệu.

## 4. Tạo database demo

Kiểm tra tên database demo đã tồn tại chưa:

```cmd
"C:\Program Files\PostgreSQL\18\bin\psql.exe" -U postgres -d postgres -c "SELECT datname FROM pg_database WHERE datname = 'smart_booking_report_demo';"
```

Nếu chưa có kết quả, tạo database:

```cmd
"C:\Program Files\PostgreSQL\18\bin\createdb.exe" -U postgres -h localhost -p 5432 smart_booking_report_demo
```

## 5. Khôi phục file data_27_8.sql vào database demo

`data_27_8.sql` là PostgreSQL custom dump, không phải SQL text. Phải dùng
`pg_restore`:

```cmd
"C:\Program Files\PostgreSQL\18\bin\pg_restore.exe" -U postgres -h localhost -p 5432 -d smart_booking_report_demo --no-owner --no-privileges "C:\Users\nguye\OneDrive\Desktop\data_27_8.sql"
```

Không dùng lệnh `psql -f data_27_8.sql`.

## 6. Chuyển tạm backend sang database demo

Mở một Command Prompt mới:

```cmd
cd /d D:\SmartEventTicketing
venv\Scripts\activate.bat
cd backend
set DB_NAME=smart_booking_report_demo
```

Biến `DB_NAME` chỉ có hiệu lực trong cửa sổ CMD hiện tại. File `.env` không bị
thay đổi.

Kiểm tra backend đang trỏ đến database nào:

```cmd
python manage.py shell -c "from django.db import connection; print(connection.settings_dict['NAME'])"
```

Kết quả bắt buộc phải là:

```text
smart_booking_report_demo
```

Sau đó cập nhật migration còn thiếu trong bản backup:

```cmd
python manage.py migrate
```

## 7. Tạo dữ liệu báo cáo demo

Vẫn trong cửa sổ CMD đang có `DB_NAME=smart_booking_report_demo`, chạy:

```cmd
python seed_admin_report_demo.py
```

Nếu seed thành công, command in số lượng bản ghi và các tài khoản demo.

Nếu chạy lần thứ hai, command sẽ từ chối để tránh nhân đôi dữ liệu. Muốn dựng
lại từ đầu:

```cmd
python seed_admin_report_demo.py --clear
python seed_admin_report_demo.py
```

`--clear` chỉ xóa User có username bắt đầu bằng `report_demo_` và Event có tên
bắt đầu bằng `[DEMO REPORT]`.

## 8. Chạy website bằng database demo

Chạy backend trong đúng cửa sổ CMD đã đặt `DB_NAME`:

```cmd
python manage.py runserver
```

Mở một Command Prompt khác để chạy frontend:

```cmd
cd /d D:\SmartEventTicketing\frontend
npm install
npm run dev
```

Frontend không cần đổi cấu hình database. Frontend gọi backend và backend quyết
định database được sử dụng.

## 9. Tài khoản demo

### Admin

```text
Email: report.demo.admin@smartticket.test
Username: report_demo_admin
Password: DemoAdmin@123
```

Admin này có `type=ADMIN`, `is_staff=True`, `is_superuser=True`, `status=True`
và `is_active=True`. Không cần chạy `createsuperuser`.

### Organizer

```text
report.demo.organizer1@smartticket.test
report.demo.organizer2@smartticket.test
report.demo.organizer3@smartticket.test
report.demo.organizer4@smartticket.test

Password chung: DemoOrganizer@123
```

### Customer

```text
report.demo.customer1@smartticket.test
...
report.demo.customer12@smartticket.test

Password chung: DemoCustomer@123
```

Trang đăng nhập chấp nhận cả email và username.

## 10. Chuyển từ database demo về database thật

Nhấn `Ctrl + C` để dừng backend.

Trong cùng cửa sổ CMD, chạy:

```cmd
set DB_NAME=smart_booking_db
python manage.py shell -c "from django.db import connection; print(connection.settings_dict['NAME'])"
python manage.py runserver
```

Kết quả kiểm tra phải là `smart_booking_db`.

Cách đơn giản hơn là đóng cửa sổ CMD đang chạy database demo, mở CMD mới rồi
khởi động backend bình thường. Khi đó Django đọc lại `DB_NAME=smart_booking_db`
từ file `backend/.env`.

## 11. Chuyển từ database thật sang database demo

Dừng backend, sau đó trong CMD:

```cmd
cd /d D:\SmartEventTicketing
venv\Scripts\activate.bat
cd backend
set DB_NAME=smart_booking_report_demo
python manage.py shell -c "from django.db import connection; print(connection.settings_dict['NAME'])"
python manage.py runserver
```

Luôn chạy lệnh kiểm tra tên database trước khi seed hoặc xóa dữ liệu demo.

## 12. Xóa hoàn toàn database demo khi không cần nữa

Trước tiên dừng backend đang kết nối database demo. Sau đó chạy:

```cmd
"C:\Program Files\PostgreSQL\18\bin\dropdb.exe" -U postgres -h localhost -p 5432 smart_booking_report_demo
```

Lệnh này xóa toàn bộ database demo nhưng không tác động `smart_booking_db`.
Chỉ chạy khi chắc chắn tên cuối lệnh là `smart_booking_report_demo`.

## 13. Lỗi thường gặp

### Command báo đang dùng sai database

Chạy lại:

```cmd
set DB_NAME=smart_booking_report_demo
```

Sau đó kiểm tra tên database bằng Django shell trước khi seed.

### `pg_restore` báo database không tồn tại

Chạy `createdb` ở bước 4 trước.

### `pg_restore` báo object đã tồn tại

Database demo không còn trống. Có thể tiếp tục dùng dữ liệu đã restore hoặc xóa
đúng database demo rồi tạo lại. Không chạy restore đè lên database chính.

### `extension "vector" is not available`

PostgreSQL server trên máy chưa có pgvector. Cần cài pgvector đúng phiên bản
PostgreSQL rồi tạo lại database demo.

### Giao diện vẫn hiện dữ liệu database chính

Backend có thể đang chạy trong một cửa sổ CMD khác. Dừng backend, đặt lại
`DB_NAME`, kiểm tra tên database rồi chạy server lại.

### Không nên chạy file seed_data.py cũ

`backend/seed_data.py` có thao tác xóa toàn bộ Event. Bộ dữ liệu báo cáo chỉ
được tạo bằng:

```cmd
python seed_admin_report_demo.py
```
