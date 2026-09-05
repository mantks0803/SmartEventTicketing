# Cài đặt và chạy SmartEventTicketing

Hướng dẫn cho **Windows Command Prompt (CMD)**, không phải PowerShell. Ví dụ dùng `%USERPROFILE%\SmartEventTicketing`; nếu project ở `D:\SmartEventTicketing`, thay đường dẫn tương ứng. Database và tài khoản trên máy độc lập với website online.

## 1. Chuẩn bị công cụ

| Công cụ | Yêu cầu |
|---|---|
| [Git](https://git-scm.com/downloads) | Để clone source |
| [Python](https://www.python.org/downloads/) | 3.12, cùng phiên bản dùng trong CI |
| [Node.js](https://nodejs.org/en/download) | `^22.18.0 \|\| >=24.12.0` theo package.json; có thể chọn Node 22 từ 22.18.0 |
| [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) | Chạy PostgreSQL có sẵn pgvector; không bắt buộc nếu server PostgreSQL hiện có đã cài pgvector |

Mở CMD mới sau khi cài, kiểm tra:

~~~bat
git --version
py -3.12 --version
node --version
npm --version
docker --version
~~~

Nếu dùng Docker, mở Docker Desktop và hoàn tất yêu cầu WSL 2/khởi động lại máy của bộ cài. **pgAdmin chỉ là công cụ quản lý; dịch vụ PostgreSQL mới là thành phần backend cần kết nối.**

## 2. Clone và cài backend

Nếu đã có project, dùng thư mục đó, không clone đè. Chỉ tạo môi trường `venv` khi chưa có:

~~~bat
cd /d "%USERPROFILE%"
git clone https://github.com/mantks0803/SmartEventTicketing.git
cd SmartEventTicketing
py -3.12 -m venv venv
venv\Scripts\activate.bat
set PYTHONUTF8=1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
~~~

Đầu dòng thường xuất hiện `(venv)` khi kích hoạt thành công. Các bước 3–4 bên dưới vẫn thực hiện từ thư mục gốc project.

## 3. Chuẩn bị PostgreSQL — chọn một cách

### Cách A: Docker có sẵn pgvector

Chờ Docker Desktop sẵn sàng. Chỉ chạy lệnh tạo container **một lần**, khi chưa có container cùng tên:

~~~bat
docker run --name smartticket-postgres -e POSTGRES_DB=smart_booking_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 127.0.0.1:5433:5432 -v smartticket_pgdata:/var/lib/postgresql/data -d pgvector/pgvector:0.8.6-pg16
docker exec smartticket-postgres pg_isready -U postgres -d smart_booking_db
~~~

Thấy `accepting connections` là server sẵn sàng. Backend trên máy kết nối cổng **5433**; cổng bên trong container là 5432. Tài khoản `postgres/postgres` chỉ dùng local.

Nếu đã tạo container theo hướng dẫn, chỉ cần `docker start smartticket-postgres`. Không xóa container/volume để xử lý lỗi trùng tên. Volume `smartticket_pgdata` giữ dữ liệu qua những lần tắt/bật, nhưng không thay thế backup. Nếu volume đã có dữ liệu, không coi đây là database mới rỗng.

### Cách B: PostgreSQL cài trực tiếp

Bật dịch vụ PostgreSQL, dùng pgAdmin hoặc công cụ quản trị của bạn để tạo database mới tên `smart_booking_db` nếu chưa tồn tại. Giữ nguyên database có dữ liệu; ghi lại host, port, username và password để cấu hình bước 4. Port thường là **5432**, tùy máy.

Server phải có extension **pgvector** tương thích. Migration sẽ tạo extension `vector`, nên tài khoản chạy migrate cần quyền phù hợp. Chỉ `pip install pgvector` không cài extension cho server; nếu chưa có, dùng cách Docker hoặc cài pgvector trên đúng server.

## 4. Tạo cấu hình local

Từ thư mục gốc, copy mẫu **chỉ khi chưa có** `.env`:

~~~bat
if not exist backend\.env copy backend\.env.example backend\.env
if not exist frontend\.env copy frontend\.env.example frontend\.env
notepad backend\.env
~~~

Với Docker ở bước 3, điền:

~~~dotenv
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=smart_booking_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5433
FRONTEND_URL=http://localhost:5173
~~~

Nếu dùng PostgreSQL cài trực tiếp, thay thông tin kết nối bằng cấu hình của bạn, không dùng nhầm cổng Docker. Giữ các biến khác từ [mẫu backend](../backend/.env.example); khóa dịch vụ có thể để trống để chạy phần cơ bản. `SECRET_KEY` mẫu chỉ dành cho local.

File `frontend/.env` cần:

~~~dotenv
VITE_API_URL=http://127.0.0.1:8000/api/
~~~

**Không commit `.env` thật và không đặt secret trong `VITE_*`** vì trình duyệt đọc được các biến này. Biến môi trường đã đặt trong Windows/CMD có thể ghi đè `.env`.

## 5. Tạo bảng, tài khoản và dữ liệu tùy chọn

Tại CMD đã kích hoạt `venv`, kiểm tra đúng database trước:

~~~bat
cd backend
python manage.py shell -c "from django.db import connection; c=connection.settings_dict; print(c['NAME'], c['HOST'], c['PORT'])"
~~~

Với Docker mặc định, kết quả là `smart_booking_db 127.0.0.1 5433`. Nếu sai, dừng và sửa cấu hình. Nếu đúng database local dự định sử dụng:

~~~bat
python manage.py migrate
python manage.py createsuperuser
~~~

`migrate` tạo/cập nhật bảng; lần cài đầu không cần `makemigrations`. `createsuperuser` tạo Admin dùng được trên website và Django Admin; bỏ qua nếu đã có tài khoản. Khi nhập mật khẩu, CMD không hiện ký tự là bình thường.

Nạp dữ liệu là **tùy chọn**, xem [hướng dẫn database](../database/README.md):

- Muốn có sự kiện và ghế mẫu: seed cơ bản tạo 32 sự kiện nhưng **xóa toàn bộ sự kiện cũ cùng dữ liệu liên quan**, chỉ chạy trên database mới không có dữ liệu cần giữ.
- Muốn có đơn PAID/vé để xem biểu đồ: dùng database riêng `smart_booking_report_demo`. Seed báo cáo thêm 8 sự kiện riêng và từ chối nạp trùng.
- Nếu đã có dữ liệu, không chạy lại seed chỉ vì vừa mở server hoặc cập nhật tài liệu. Không cần file SQL backup để cài demo mới.

## 6. Chạy hai server

Trong CMD backend:

~~~bat
python manage.py runserver
~~~

Giữ cửa sổ này mở. Django Admin ở [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

Mở **CMD thứ hai**:

~~~bat
cd /d "%USERPROFILE%\SmartEventTicketing\frontend"
npm ci
npm run dev
~~~

Mở địa chỉ Vite hiển thị, thường là [http://localhost:5173](http://localhost:5173). Nếu Vite đổi cổng do 5173 đang bận, giải phóng cổng hoặc cập nhật `FRONTEND_URL` ở backend trước khi thử chuyển hướng thanh toán.

## 7. Chạy lại những lần sau

Bật dịch vụ PostgreSQL; nếu dùng Docker, mở Docker Desktop rồi chạy:

~~~bat
docker start smartticket-postgres
~~~

CMD thứ nhất:

~~~bat
cd /d "%USERPROFILE%\SmartEventTicketing"
venv\Scripts\activate.bat
set PYTHONUTF8=1
cd backend
python manage.py runserver
~~~

CMD thứ hai:

~~~bat
cd /d "%USERPROFILE%\SmartEventTicketing\frontend"
npm run dev
~~~

Dừng server bằng `Ctrl + C`. Không cần seed/rebuild RAG mỗi lần. Chỉ migrate khi database mới hoặc có migration mới; cài lại thư viện khi requirements/lockfile thay đổi. Sau khi sửa `.env`, khởi động lại server tương ứng. Khi chuyển database, đăng xuất rồi đăng nhập lại.

## 8. Cấu hình dịch vụ — tùy chọn

Điền khóa riêng vào `backend/.env`, không chia sẻ key của website online.

| Dịch vụ | Biến cần điền | Nếu chưa cấu hình |
|---|---|---|
| PayOS | `PAYOS_CLIENT_ID`, `PAYOS_API_KEY`, `PAYOS_CHECKSUM_KEY` | Không tạo link thanh toán thật |
| Cloudinary | `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` | Xem ảnh URL có sẵn, chưa upload ảnh mới |
| Email | `EMAIL_BACKEND`, các biến `EMAIL_*` và `DEFAULT_FROM_EMAIL` | Console backend chỉ in email vào terminal, không gửi Gmail |
| Gemini | `GOOGLE_API_KEY` và cấu hình model | Hỏi đáp/diễn giải AI chưa đầy đủ; tìm sự kiện từ database không gọi Google |

**Email thật:** đổi `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`; cấu hình host, port, TLS, user, password và địa chỉ gửi theo nhà cung cấp. Với Gmail, dùng mật khẩu ứng dụng nếu tài khoản hỗ trợ, không nhập mật khẩu đăng nhập chính. Xem các tên biến trong [mẫu cấu hình](../backend/.env.example).

**PayOS thật:** cấu hình webhook trỏ tới backend HTTPS công khai, dạng `https://<ten-mien-backend>/api/orders/webhook/payos/`, không phải địa chỉ frontend hoặc localhost. Giữ `PAYOS_SKIP_SIGNATURE_CHECK=False` trên server public. Thử không dùng tiền thật theo [hướng dẫn thanh toán local](PAYMENT_TEST.md).

**Chatbot:** chọn model tài khoản Google hỗ trợ, giữ số chiều embedding 768, rồi nạp dịch vụ và tạo chỉ mục theo [hướng dẫn AI Agent](../backend/ai_agent/README.md). Rebuild/evaluation thật dùng quota Google, không chạy liên tục để thử.

## 9. Lỗi thường gặp

| Hiện tượng | Kiểm tra |
|---|---|
| Không nhận lệnh Git/Python/npm | Đã cài, thêm PATH và mở CMD mới chưa |
| Không tìm thấy Django | Đã kích hoạt `venv` và cài requirements chưa |
| Docker chưa chạy/trùng tên container | Mở Docker Desktop; dùng container có sẵn đúng cấu hình, không xóa dữ liệu |
| Không kết nối database | Dịch vụ PostgreSQL, host/cổng, tên DB, user/password và biến môi trường ghi đè |
| `vector is not available` | Server PostgreSQL thiếu pgvector; pip không thay thế extension |
| Trang chủ trống | API URL/backend, database đang chọn và sự kiện PUBLISHED |
| Upload ảnh/thanh toán lỗi | Khóa Cloudinary/PayOS và log backend; không tắt chữ ký PayOS để né lỗi |
| Không nhận email | Đang dùng console hay SMTP, thông tin gửi, thư mục spam |
| Không thấy chatbot | Đăng nhập bằng Customer/Organizer hoạt động, không phải Admin |
| AI thiếu thông tin/tạm gián đoạn | Đúng database, đã tạo chỉ mục, key/model/quota; xem hướng dẫn chatbot |

Tiếp theo: [dữ liệu mẫu](../database/README.md), [lệnh kiểm thử](TEST_COMMANDS.md) hoặc [danh mục tài liệu](README.md). Các lệnh trong tài liệu là hướng dẫn để bạn tự chạy; không có script cài đặt tự động đi kèm.
