# Cài đặt và chạy SmartEventTicketing

Dùng **Windows Command Prompt (CMD)**. Hướng dẫn clone vào `%USERPROFILE%\SmartEventTicketing`; nếu lưu nơi khác, thay đường dẫn tương ứng. Dữ liệu/tài khoản local độc lập với website online.

## 1. Cài công cụ

| Công cụ | Phiên bản/mục đích |
|---|---|
| [Git](https://git-scm.com/downloads) | Tải source từ GitHub |
| [Python](https://www.python.org/downloads/) | 3.12, cùng phiên bản CI |
| [Node.js](https://nodejs.org/en/download) | Node 22 từ 22.18.0, hoặc từ 24.12.0 theo package.json |
| [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) | Chạy PostgreSQL có sẵn pgvector; bỏ qua nếu đã có PostgreSQL với pgvector |

Mở CMD mới sau khi cài, kiểm tra:

```cmd
git --version
py -3.12 --version
node --version
npm --version
```

Các lệnh phải hiện phiên bản. Nếu dùng Docker, mở Docker Desktop và hoàn tất yêu cầu WSL 2/khởi động lại của bộ cài trước bước 3. **pgAdmin là công cụ quản lý, không thay thế dịch vụ PostgreSQL.**

## 2. Clone và cài thư viện backend

Nếu đã clone, dùng thư mục hiện có; không tạo lại `venv` nếu đã có môi trường phù hợp.

```cmd
cd /d "%USERPROFILE%"
git clone https://github.com/mantks0803/SmartEventTicketing.git
cd SmartEventTicketing
py -3.12 -m venv venv
venv\Scripts\activate.bat
set PYTHONUTF8=1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

Đầu dòng thường có `(venv)`. Chờ cài thư viện xong, không có lỗi, rồi tiếp tục từ **thư mục gốc project**.

## 3. Chuẩn bị database — chọn một cách

**Cài mới bằng Docker:** khi Docker Desktop đã chạy và chưa có container cùng tên, chạy một lần:

```cmd
docker run --name smartticket-postgres -e POSTGRES_DB=smart_booking_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 127.0.0.1:5433:5432 -v smartticket_pgdata:/var/lib/postgresql/data -d pgvector/pgvector:0.8.6-pg16
docker exec smartticket-postgres pg_isready -U postgres -d smart_booking_db
```

Thấy `accepting connections` là sẵn sàng. Backend kết nối cổng **5433**; tài khoản `postgres/postgres` chỉ dùng local. Nếu đã tạo container, dùng `docker start smartticket-postgres`, không chạy lại `docker run`.

Volume `smartticket_pgdata` lưu dữ liệu qua các lần tắt/bật, không phải backup. **Không xóa container/volume để sửa lỗi trùng tên; volume có sẵn có thể chứa dữ liệu cần giữ.**

**Đã có PostgreSQL trực tiếp:** bật dịch vụ, tạo database `smart_booking_db` bằng pgAdmin nếu chưa có. Ghi lại user/password/host/port (thường **5432**). Server phải được cài pgvector; `pip install pgvector` không thay thế extension trên server. Migration cần quyền tạo extension `vector`.

## 4. Điền cấu hình

Tại **thư mục gốc**, tạo file từ mẫu nếu chưa có:

```cmd
if not exist backend\.env copy backend\.env.example backend\.env
if not exist frontend\.env copy frontend\.env.example frontend\.env
notepad backend\.env
```

Với Docker ở bước 3, sửa các dòng sau, giữ các biến còn lại từ file mẫu rồi lưu:

```dotenv
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=smart_booking_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5433
FRONTEND_URL=http://localhost:5173
```

Nếu dùng PostgreSQL trực tiếp, thay bằng thông tin kết nối của bạn. Trong `frontend/.env`, giữ:

```dotenv
VITE_API_URL=http://127.0.0.1:8000/api/
```

Khóa dịch vụ có thể để trống để chạy phần cơ bản; xem mục cuối. **Không commit `.env` hoặc đặt secret trong `VITE_*` vì trình duyệt đọc được.** Secret/tài khoản mẫu chỉ dành cho local.

## 5. Tạo bảng và tài khoản

Trong CMD đã kích hoạt `venv`, chuyển vào **backend** và kiểm tra cấu hình database:

```cmd
cd backend
python manage.py shell -c "from django.db import connection; c=connection.settings_dict; print(c['NAME'], c['HOST'], c['PORT'])"
```

Với Docker ở trên, kết quả phải là `smart_booking_db 127.0.0.1 5433`. Nếu khác, kiểm tra `.env` và biến môi trường CMD/Windows có thể ghi đè nó. Khi đã đúng database local muốn dùng:

```cmd
python manage.py migrate
python manage.py createsuperuser
```

`migrate` tạo/cập nhật bảng; không cần chạy `makemigrations` khi cài project. `createsuperuser` tạo Admin, bỏ qua nếu đã có. Nhập mật khẩu không hiện ký tự trong CMD là bình thường.

**Dữ liệu mẫu là tùy chọn:** làm theo [hướng dẫn database](../database/README.md) nếu muốn có sự kiện hoặc biểu đồ báo cáo. `seed_data.py` xóa toàn bộ sự kiện cũ và dữ liệu liên quan, chỉ chạy trên database mới không có dữ liệu cần giữ. Không cần file SQL backup để cài lần đầu; chỉ migrate thì chưa có sự kiện mẫu.

## 6. Mở website

Tại **backend**, chạy và giữ cửa sổ này mở:

```cmd
python manage.py runserver
```

Django Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

Mở **CMD thứ hai** để cài và chạy frontend:

```cmd
cd /d "%USERPROFILE%\SmartEventTicketing\frontend"
npm ci
npm run dev
```

Mở địa chỉ Vite hiển thị, thường là [http://localhost:5173](http://localhost:5173). Có thể đăng nhập bằng tài khoản Admin vừa tạo hoặc đăng ký Customer/Organizer. Chưa nạp dữ liệu thì danh sách sự kiện có thể trống.

**Những lần sau:** bật PostgreSQL, kích hoạt `venv`, chạy hai server theo [README chính](../README.md#cài-và-chạy). Không seed/rebuild RAG mỗi lần; chỉ migrate khi database mới hoặc có migration mới. Cài lại thư viện khi requirements/lockfile thay đổi. Dừng server bằng `Ctrl + C`; đổi `.env` thì khởi động lại server, đổi database thì đăng nhập lại.

## Dịch vụ tùy chọn

Điền khóa riêng trong `backend/.env`, theo [file mẫu](../backend/.env.example). Không dùng hoặc chia sẻ key của website online.

| Dịch vụ | Cấu hình | Khi chưa có |
|---|---|---|
| PayOS | `PAYOS_CLIENT_ID`, `PAYOS_API_KEY`, `PAYOS_CHECKSUM_KEY` | Không tạo link thanh toán thật |
| Cloudinary | `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` | Chưa upload ảnh mới |
| Email | Đổi `EMAIL_BACKEND` sang `django.core.mail.backends.smtp.EmailBackend`, điền các biến SMTP `EMAIL_*` và `DEFAULT_FROM_EMAIL` | Mặc định chỉ in email vào terminal |
| Gemini | `GOOGLE_API_KEY`, model được tài khoản hỗ trợ, nạp dữ liệu theo [AI Agent](../backend/ai_agent/README.md) | Hỏi đáp/diễn giải chưa đầy đủ; tìm sự kiện từ DB không gọi Google |

Email Gmail dùng mật khẩu ứng dụng nếu tài khoản hỗ trợ, không dùng mật khẩu đăng nhập chính.

PayOS thật cần webhook backend HTTPS công khai: `https://<ten-mien-backend>/api/orders/webhook/payos/`, không phải localhost hoặc URL frontend. Giữ `PAYOS_SKIP_SIGNATURE_CHECK=False` trên server public. Thử không dùng tiền thật theo [hướng dẫn thanh toán local](PAYMENT_TEST.md).

## Nếu chưa chạy được

| Lỗi | Kiểm tra |
|---|---|
| Không nhận lệnh / không tìm thấy Django | Cài công cụ, mở CMD mới; kích hoạt `venv` và cài requirements |
| Docker chưa chạy hoặc trùng tên | Mở Docker Desktop, dùng container đã tạo; không xóa dữ liệu |
| Không kết nối database | Dịch vụ PostgreSQL, DB/user/password/host/port và biến môi trường ghi đè |
| `vector is not available` | Server PostgreSQL thiếu pgvector; dùng Docker ở bước 3 hoặc cài extension đúng server |
| Trang trống | Backend có chạy, API URL đúng, database đã có sự kiện PUBLISHED chưa |
| Vite dùng cổng khác 5173 | Dùng cổng Vite hiển thị và cập nhật `FRONTEND_URL` backend khi thử thanh toán |
| Upload/thanh toán/email lỗi | Cấu hình dịch vụ phía trên và log backend; không tắt chữ ký PayOS để né lỗi |
| Chatbot không hiện hoặc AI lỗi | Vai trò Customer/Organizer, dữ liệu RAG, key/model/quota; xem [AI Agent](../backend/ai_agent/README.md) |

Cần kiểm thử: xem [lệnh test](TEST_COMMANDS.md) hoặc [danh mục tài liệu](README.md). Đây là hướng dẫn chạy local, chưa có script cài đặt tự động.
