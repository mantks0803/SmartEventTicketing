# Database và dữ liệu mẫu

Project dùng PostgreSQL và extension `vector` (pgvector), không dùng SQLite. Thiết lập Python 3.12, môi trường `venv`, Docker và backend theo [README gốc](../README.md) trước khi chạy các lệnh dưới đây. Các ví dụ dùng **Windows Command Prompt (CMD)**, với project tại `%USERPROFILE%\SmartEventTicketing`.

## Cấu trúc và kết nối

- `seed_data.py`: dữ liệu sự kiện, loại vé, ghế và tài khoản Organizer cơ bản.
- `seed_admin_report_demo.py`: điểm chạy tiện dụng cho dữ liệu báo cáo. Logic Django vẫn nằm tại `backend/orders/management/commands/seed_admin_report_demo.py`.
- `backups/`: chỗ lưu bản sao lưu riêng tư; xem [quy tắc backup](backups/README.md).
- Migration vẫn nằm trong từng app của `backend/`; thư mục này không thay thế migration.

Cấu hình local thống nhất với README gốc:

| Thành phần | Giá trị |
|---|---|
| Docker container | `smartticket-postgres` |
| Image | `pgvector/pgvector:0.8.6-pg16` |
| Volume lưu dữ liệu | `smartticket_pgdata` |
| PostgreSQL trong container | Cổng `5432` |
| Kết nối từ backend trên Windows | `127.0.0.1:5433` |
| Database chính | `smart_booking_db` |
| User / password demo local | `postgres` / `postgres` |

Backend đọc `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` từ `backend/.env`. Tài khoản trên chỉ phục vụ máy local, không dùng trên hệ thống public. Volume giữ dữ liệu khi container dừng; volume không phải bản sao lưu. Không xóa volume nếu cần giữ dữ liệu.

## Seed cơ bản: chỉ chạy trên database mới, có thể bỏ đi

**Cảnh báo mất dữ liệu:** `seed_data.py` gọi `Event.objects.all().delete()` trước khi nạp mẫu. Nó xóa **toàn bộ sự kiện trong database đang kết nối**, không chỉ sự kiện demo; các loại vé, ghế, đơn hàng, vé phát hành và thanh toán liên quan có thể bị xóa theo quan hệ cascade. Script còn đặt lại mật khẩu tài khoản `demo_organizer` thành `123456`, kể cả khi tài khoản đã tồn tại. Script này không có chốt bảo vệ tên database.

Chỉ dùng trên database mới, dành riêng cho demo và không có dữ liệu cần giữ. Nếu database đã có dữ liệu thật hoặc dữ liệu demo cần bảo toàn, bỏ qua bước này; không coi seed là lệnh cập nhật an toàn.

Sau khi tạo database và hoàn tất migration theo README gốc, kiểm tra `backend/.env` đang trỏ đúng database rồi chạy:

```cmd
cd /d "%USERPROFILE%\SmartEventTicketing"
call venv\Scripts\activate.bat
cd backend
chcp 65001
set PYTHONUTF8=1
python ..\database\seed_data.py
```

Kết quả: 32 sự kiện đã xuất bản, mỗi sự kiện có 10 ghế VIP và 15 ghế phổ thông. Ngày diễn ra được tính tương đối từ ngày chạy script. Đăng nhập Organizer bằng `demo_organizer` hoặc `organizer@smartevent.vn`, mật khẩu `123456`. Seed này không tạo tài khoản Admin hay Customer.

## Demo báo cáo Admin trên database riêng

Command báo cáo chỉ chấp nhận database tên `smart_booking_report_demo`; nó sẽ từ chối database chính `smart_booking_db`. Không bỏ chốt bảo vệ này. Dữ liệu thanh toán `PAYOS-DEMO` do script tạo chỉ là mô phỏng, không phải giao dịch PayOS thật.

### 1. Tạo database demo mới

Nếu container theo README gốc đang chạy và database này **chưa tồn tại**, mở CMD:

```cmd
docker exec smartticket-postgres psql -U postgres -d postgres -c "CREATE DATABASE smart_booking_report_demo;"
```

Nếu tên này đã tồn tại, không xóa hoặc ghi đè database để chạy tiếp. Kiểm tra dữ liệu đang có trước; không chạy seed cơ bản trên database cần giữ.

### 2. Chuyển backend sang database demo

Dừng backend. Sửa `backend/.env`:

```dotenv
DB_NAME=smart_booking_report_demo
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5433
```

Nếu đã đặt các biến `DB_*` trong Windows hoặc phiên CMD, cần đồng bộ chúng với `.env`: biến môi trường có sẵn được ưu tiên hơn file `.env`. Chỉ tên database thay đổi khi dùng cùng container; database chính vẫn được giữ nguyên.

### 3. Migration, rồi seed đúng thứ tự

Chỉ thực hiện chuỗi dưới đây trên **database demo vừa tạo, chưa có dữ liệu cần giữ**. Trước tiên kiểm tra cấu hình kết nối mà backend thực sự nạp; lệnh kiểm tra chỉ đọc tên, host và cổng, không in mật khẩu:

```cmd
cd /d "%USERPROFILE%\SmartEventTicketing"
call venv\Scripts\activate.bat
cd backend
chcp 65001
set PYTHONUTF8=1
python manage.py shell -c "from django.db import connection; c=connection.settings_dict; print(c['NAME'], c['HOST'], c['PORT'])"
```

Với ví dụ Docker này, kết quả kiểm tra **phải là**:

```text
smart_booking_report_demo 127.0.0.1 5433
```

Nếu khác, dừng tại đây và sửa `.env` hoặc biến môi trường đang ghi đè; không chạy seed. Chỉ khi đã xác nhận đúng database mới, tiếp tục trong cùng cửa sổ CMD tại `backend`:

```cmd
python manage.py migrate
python ..\database\seed_data.py
python ..\database\seed_admin_report_demo.py
```

Thứ tự bắt buộc khi muốn cả danh sách sự kiện tương lai và báo cáo: **seed cơ bản trước, seed báo cáo sau**. Chạy seed cơ bản sau seed báo cáo sẽ xóa các sự kiện báo cáo và dữ liệu liên quan. Nếu chỉ cần báo cáo, có thể bỏ qua seed cơ bản.

Seed báo cáo tạo 1 Admin, 4 Organizer, 12 Customer, 8 sự kiện đã diễn ra, 60 đơn `PAID` và 120 vé. Giao dịch trải qua 6 tháng trước tháng chạy script; chọn khoảng thời gian tương ứng trên màn hình báo cáo nếu bộ lọc mặc định chưa hiển thị dữ liệu. Các sự kiện báo cáo đã diễn ra nên không xuất hiện trong kết quả chatbot tìm sự kiện tương lai.

| Vai trò | Email đăng nhập | Mật khẩu demo |
|---|---|---|
| Admin | `report.demo.admin@smartticket.test` | `DemoAdmin@123` |
| Organizer 1 | `report.demo.organizer1@smartticket.test` | `DemoOrganizer@123` |
| Customer 1 | `report.demo.customer1@smartticket.test` | `DemoCustomer@123` |

Admin cũng có thể đăng nhập bằng username `report_demo_admin`. Organizer còn lại dùng số `2` đến `4`; Customer còn lại dùng số `2` đến `12`, với mật khẩu tương ứng trong bảng. Đây là tài khoản mẫu công khai, không dùng cho dữ liệu thật.

Command từ chối nạp lại nếu phát hiện user có tiền tố `report_demo_` hoặc sự kiện có tiền tố `[DEMO REPORT]`. Nếu chủ động muốn thay bộ báo cáo demo hiện tại, từ `backend` chạy:

```cmd
python ..\database\seed_admin_report_demo.py --clear
python ..\database\seed_admin_report_demo.py
```

`--clear` xóa các sự kiện/user theo những tiền tố trên cùng dữ liệu cascade của chúng. Nó không hoàn tác được và có thể xóa dữ liệu bạn đã bổ sung dưới các tài khoản/sự kiện đó. Không cần chạy lại seed cơ bản. Cách gọi Django tương đương vẫn hoạt động: `python manage.py seed_admin_report_demo` (hoặc thêm `--clear`).

### 4. Chạy ứng dụng hoặc quay lại database chính

Khởi động lại backend sau khi đổi `.env`. Trên frontend, **đăng xuất rồi đăng nhập lại** bằng tài khoản thuộc database đang chọn; không tái sử dụng token hay phiên chat của database trước.

Muốn quay lại database chính: dừng backend, đổi `DB_NAME=smart_booking_db` trong `backend/.env` và các biến môi trường có ghi đè, khởi động backend lại, rồi đăng xuất/đăng nhập lại trên trình duyệt. Không cần seed lại và không cần xóa database demo.

## Tùy chọn: PostgreSQL cài trực tiếp trên Windows

Có thể dùng PostgreSQL native thay Docker nếu server đã cài pgvector tương thích với phiên bản PostgreSQL đó. Gói Python `pgvector` trong requirements không tự cài extension trên server PostgreSQL. Migration `ai_agent/0003_enable_pgvector.py` tạo extension `vector`; user chạy migration cần quyền tạo extension và server phải có sẵn các file extension.

Tạo database riêng bằng công cụ quản trị PostgreSQL của bạn, rồi đặt đúng `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` trong `backend/.env`. PostgreSQL native thường được cấu hình cổng `5432`, còn hướng dẫn Docker ở trên dùng cổng host `5433`: không hoán đổi hai cổng. Nếu migration báo `extension "vector" is not available`, cần cài pgvector trên đúng server PostgreSQL hoặc dùng image Docker đã nêu; cài lại thư viện Python không giải quyết lỗi này.

## Backup và dữ liệu AI

Clone mới không cần file dump từ Desktop hoặc máy của người khác. Migration cùng seed tùy chọn đủ để tạo môi trường demo. Backup chỉ dùng khi chủ sở hữu chủ động muốn khôi phục một bộ dữ liệu cụ thể; xem [database/backups](backups/README.md).

Dữ liệu dịch vụ, tài liệu RAG và bộ câu hỏi đánh giá vẫn nằm tại `backend/ai_agent/data/` vì code tải chúng theo đường dẫn đó. Xem [hướng dẫn AI Agent](../backend/ai_agent/README.md) để seed dịch vụ hoặc tạo chỉ mục; các thao tác này không nằm trong hai script sự kiện ở trên.
