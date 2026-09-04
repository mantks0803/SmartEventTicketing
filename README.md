# HỆ THỐNG BÁN VÉ SỰ KIỆN TRỰC TUYẾN TÍCH HỢP CHATBOT THÔNG MINH

> Có thể truy cập tại: [https://smartticket-web.vercel.app/](https://smartticket-web.vercel.app/)

## 1. Giới thiệu

SmartEventTicketing hỗ trợ tìm kiếm, đặt vé và quản lý sự kiện trực tuyến. Hệ thống phục vụ ba nhóm người dùng: Khách hàng, Ban tổ chức và Quản trị viên.

Khách hàng tìm sự kiện, chọn ghế, thanh toán và nhận vé điện tử. Ban tổ chức tạo sự kiện, thiết lập loại vé, soát vé và theo dõi doanh thu. Quản trị viên duyệt sự kiện, quản lý tài khoản, giám sát giao dịch và xem báo cáo toàn hệ thống.

Chatbot kết hợp tài liệu Markdown, dữ liệu PostgreSQL, LangChain và Gemini để giải đáp nghiệp vụ, tìm sự kiện và tư vấn chi phí tổ chức.

### Chọn cách sử dụng

- **Chỉ muốn trải nghiệm:** mở website phía trên, không cần cài đặt hay tự nhập API key.
- **Muốn chạy source trên máy:** làm theo hướng dẫn Windows CMD bên dưới. Database và tài khoản local độc lập với website online.
- **Muốn thử đầy đủ tích hợp:** tự cấu hình PayOS, Gemini, Cloudinary và email. Không có key vẫn khởi động được các phần cơ bản, nhưng không đồng nghĩa tất cả chức năng đều hoạt động.

Repository không cung cấp key bí mật hoặc thông tin đăng nhập của hệ thống online.

## 2. Chức năng chính

| Vai trò | Chức năng |
|---|---|
| Khách hàng | Đăng ký, đăng nhập, cập nhật hồ sơ, tìm kiếm và lọc sự kiện, chọn ghế, giữ ghế, thanh toán PayOS, nhận email có QR và mã vé, xem vé đã thanh toán |
| Ban tổ chức | Tạo sự kiện, upload ảnh Cloudinary, thiết lập loại vé và ghế, gửi Admin duyệt, xem báo cáo doanh thu, check-in bằng mã vé |
| Quản trị viên | Duyệt/từ chối sự kiện, quản lý và khóa tài khoản, xem doanh thu, quản lý giao dịch, đối soát PayOS, xác nhận quyết toán mô phỏng |
| Chatbot | Hỏi đáp hệ thống, tìm sự kiện, kiểm tra ghế, tư vấn chi phí và giá vé hòa vốn |

Quy tắc nghiệp vụ:

- Mỗi đơn được chọn tối đa 5 ghế và giữ ghế trong 10 phút.
- Sự kiện do Ban tổ chức tạo cần Admin duyệt trước khi công khai.
- Vé chỉ được phát hành sau khi đơn được xác nhận PAID.
- Mỗi vé chỉ được check-in thành công một lần.
- Ban tổ chức chỉ soát vé thuộc sự kiện của mình.
- Doanh thu chỉ tính các đơn PAID.

## 3. Công nghệ

| Thành phần | Công nghệ |
|---|---|
| Backend | Python, Django REST Framework, SimpleJWT |
| Frontend | Vue 3, Vite, Pinia, Vue Router, Axios |
| Giao diện và biểu đồ | Bootstrap, Bootstrap Icons, SweetAlert2, Chart.js |
| Database | PostgreSQL, pgvector |
| Tích hợp | PayOS, Cloudinary, Django Email/SMTP |
| Chatbot | LangChain, Gemini Chat, Gemini Embedding |
| Kiểm thử và CI | Django TestCase/APITestCase/TransactionTestCase, GitHub Actions |

## 4. Cấu trúc dự án

~~~text
SmartEventTicketing/
├── backend/                 Django, API, models, migrations và tests theo từng app
│   └── ai_agent/
│       ├── README.md        Hướng dẫn chatbot
│       ├── data/            Markdown, JSON dịch vụ và câu hỏi evaluation
│       └── rag_engine/      Truy xuất kiến thức, chat và công cụ nghiệp vụ
├── frontend/                Vue, CSS, component, router và store
├── database/                Hai script seed và hướng dẫn database mẫu
├── documents/               Hướng dẫn thanh toán, kiểm thử và tài liệu lưu trữ
├── docs/                    Tài liệu RAG evaluation giữ tại vị trí cũ
├── .github/workflows/       CI kiểm thử backend và build frontend
└── README.md
~~~

Test vẫn nằm trong backend/<app>/tests/. Dữ liệu chatbot không được chuyển sang database/ hoặc documents/.

## 5. Chuẩn bị

Hướng dẫn sử dụng **Windows và Command Prompt (CMD)**. Những lệnh dưới đây không dành cho PowerShell.

Cài đặt:

1. [Git](https://git-scm.com/downloads).
2. [Python 3.12](https://www.python.org/downloads/) giống môi trường CI.
3. [Node.js](https://nodejs.org/en/download): dòng 22 từ 22.18.0 hoặc phiên bản từ 24.12.0 trở lên, theo package.json.
4. [Docker Desktop](https://docs.docker.com/desktop/setup/install/windows-install/) để chạy PostgreSQL có sẵn pgvector.

Mở Docker Desktop sau khi cài. Nếu bộ cài yêu cầu WSL 2 hoặc khởi động lại máy, hoàn thành bước đó trước.

Kiểm tra trong CMD:

~~~bat
git --version
py -3.12 --version
node --version
npm --version
docker --version
~~~

Nếu đã có PostgreSQL được cài pgvector, không bắt buộc dùng Docker. Xem [cách dùng PostgreSQL cài trực tiếp](database/README.md).

pgvector phải có ở PostgreSQL server; chỉ cài thư viện pgvector bằng pip chưa đủ.

## 6. Cài đặt lần đầu

### Bước 1: Clone mã nguồn

~~~bat
cd /d "%USERPROFILE%"
git clone https://github.com/mantks0803/SmartEventTicketing.git
cd SmartEventTicketing
~~~

Các ví dụ sau giả định project nằm trong thư mục SmartEventTicketing của tài khoản Windows hiện tại. Nếu chọn vị trí khác, thay đường dẫn tương ứng.

Nếu máy đã có project, không cần clone đè hoặc tạo lại. Dùng thư mục hiện có và kiểm tra cấu hình của bạn trước khi tiếp tục.

### Bước 2: Tạo môi trường Python và cài thư viện

~~~bat
py -3.12 -m venv venv
venv\Scripts\activate.bat
set PYTHONUTF8=1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
~~~

Khi kích hoạt thành công, đầu dòng CMD thường xuất hiện (venv). PYTHONUTF8 giúp hiển thị tiếng Việt trong các script.

### Bước 3: Tạo database local mới

Chờ Docker Desktop sẵn sàng, rồi chạy **một lần**:

~~~bat
docker run --name smartticket-postgres -e POSTGRES_DB=smart_booking_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 127.0.0.1:5433:5432 -v smartticket_pgdata:/var/lib/postgresql/data -d pgvector/pgvector:0.8.6-pg16
~~~

Kiểm tra:

~~~bat
docker exec smartticket-postgres pg_isready -U postgres -d smart_booking_db
~~~

Khi thấy accepting connections, database đã sẵn sàng.

Cấu hình dùng cổng 5433 trên máy để hạn chế trùng PostgreSQL cài trực tiếp ở cổng 5432. Volume smartticket_pgdata giữ dữ liệu qua những lần tắt/bật container. Không xóa volume nếu muốn giữ dữ liệu.

Mật khẩu postgres trong ví dụ **chỉ dùng local**, không dùng nguyên trạng cho môi trường online.

Nếu container đã tồn tại, không chạy lại docker run hoặc xóa container để xử lý lỗi tên trùng. Kiểm tra cấu hình đang có; nếu đúng container đã tạo theo hướng dẫn, dùng:

~~~bat
docker start smartticket-postgres
~~~

### Bước 4: Tạo file cấu hình

Tại thư mục gốc project, chỉ copy khi chưa có file .env:

~~~bat
if not exist backend\.env copy backend\.env.example backend\.env
if not exist frontend\.env copy frontend\.env.example frontend\.env
notepad backend\.env
~~~

Với Docker vừa tạo, sửa các dòng sau trong backend/.env:

~~~env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=smart_booking_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=127.0.0.1
DB_PORT=5433
FRONTEND_URL=http://localhost:5173
~~~

Các khóa dịch vụ còn lại có thể để trống để chạy phần cơ bản. Giữ console email backend của file mẫu nếu chưa cần email thật. Giá trị SECRET_KEY mẫu chỉ dành cho local; hệ thống online phải có khóa riêng.

Frontend/.env cần:

~~~env
VITE_API_URL=http://127.0.0.1:8000/api/
~~~

Đường dẫn API phải có phần /api/. Không đặt mật khẩu database hoặc key bí mật vào biến VITE_: chúng xuất hiện trong mã frontend mà trình duyệt tải về.

Không commit .env thật lên GitHub.

### Bước 5: Tạo bảng và Admin

~~~bat
cd backend
python manage.py migrate
python manage.py createsuperuser
~~~

Điền username, email, tên, số điện thoại và mật khẩu theo yêu cầu. Khi nhập mật khẩu, CMD có thể không hiện ký tự; đây là bình thường.

Tài khoản superuser dùng được cho Admin trên website và Django Admin. Người cài lần đầu cần migrate, không cần tự chạy makemigrations.

### Bước 6: Nạp sự kiện mẫu — tùy chọn

**Cảnh báo: script dưới đây xóa toàn bộ sự kiện cũ và dữ liệu liên quan, đồng thời đặt mật khẩu demo_organizer về 123456. Chỉ chạy trên database local mới, không có dữ liệu cần giữ. Không chạy trên database online.**

Trước tiên kiểm tra backend đang trỏ đến đâu:

~~~bat
python manage.py shell -c "from django.conf import settings; db=settings.DATABASES['default']; print(db['NAME'], db['HOST'], db['PORT'])"
~~~

Nếu dùng cấu hình phía trên, kết quả phải là:

~~~text
smart_booking_db 127.0.0.1 5433
~~~

Tên database đúng chưa đủ để đảm bảo dữ liệu đang trống. Chỉ tiếp tục nếu đây là database mới bạn vừa tạo:

~~~bat
python ..\database\seed_data.py
~~~

Kết quả là 32 sự kiện PUBLISHED có ghế để chạy thử. Ban tổ chức mẫu:

~~~text
Email: organizer@smartevent.vn
Username: demo_organizer
Password: 123456
~~~

Đây không phải tài khoản website online. Khách hàng có thể đăng ký trên giao diện.

Muốn có đơn PAID, vé và dữ liệu doanh thu mà không chuyển tiền thật, xem [database demo báo cáo](database/README.md). Không cần file backup riêng trên Desktop để tạo dữ liệu này.

### Bước 7: Chạy backend

Vẫn trong thư mục backend:

~~~bat
python manage.py runserver
~~~

Giữ cửa sổ CMD mở. Django Admin: http://127.0.0.1:8000/admin/

### Bước 8: Chạy frontend

Mở một CMD khác:

~~~bat
cd /d "%USERPROFILE%\SmartEventTicketing\frontend"
npm ci
npm run dev
~~~

Mở địa chỉ Vite hiển thị, thông thường là http://localhost:5173.

Nếu Vite chọn cổng khác vì 5173 đang bận, nên giải phóng cổng hoặc cập nhật FRONTEND_URL tương ứng trước khi thử luồng thanh toán.

## 7. Chạy lại trong các lần sau

Không cần nạp lại dữ liệu mẫu. Mở Docker Desktop và bật database:

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

Dừng server bằng Ctrl + C. Chỉ migrate khi database mới hoặc có migration mới. Chỉ cài lại thư viện khi requirements.txt hoặc package-lock.json thay đổi.

Nếu dùng PostgreSQL cài trực tiếp, bật dịch vụ PostgreSQL thay cho bước docker start.

## 8. Cấu hình để sử dụng đầy đủ

| Dịch vụ | Cấu hình backend | Nếu chưa cấu hình |
|---|---|---|
| PayOS | PAYOS_CLIENT_ID, PAYOS_API_KEY, PAYOS_CHECKSUM_KEY | Không tạo liên kết thanh toán thật |
| Cloudinary | CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET | Xem ảnh URL có sẵn được, nhưng không upload ảnh mới |
| Email | EMAIL_BACKEND cùng tài khoản SMTP và các biến EMAIL_* | Console backend chỉ in email ở terminal |
| Gemini | GOOGLE_API_KEY, AI_CHAT_MODEL, AI_EMBEDDING_MODEL | Hỏi đáp/tư vấn chưa đầy đủ; tìm sự kiện từ database vẫn hoạt động |

Để gửi email thật, đổi EMAIL_BACKEND sang django.core.mail.backends.smtp.EmailBackend và cấu hình EMAIL_HOST_USER, EMAIL_HOST_PASSWORD cùng các thông số SMTP của nhà cung cấp. Không dùng mật khẩu email chính thay cho thông tin SMTP được nhà cung cấp cho phép.

PayOS webhook thật cần URL backend public HTTPS:

~~~text
https://<ten-mien-backend>/api/orders/webhook/payos/
~~~

Không thể đưa địa chỉ localhost cho PayOS gọi từ Internet. Bản local có hướng dẫn giả lập riêng tại [PAYMENT_TEST.md](documents/PAYMENT_TEST.md).

**Trên server public phải giữ PAYOS_SKIP_SIGNATURE_CHECK=False.** Không chia sẻ bộ key production để người khác chạy demo. Người dùng website online không cần biết key vì backend xử lý dịch vụ.

## 9. Chuẩn bị chatbot

Điền GOOGLE_API_KEY và chọn model được tài khoản Google của bạn hỗ trợ trong backend/.env. Giữ AI_EMBEDDING_DIMENSIONS=768 để khớp database hiện tại.

Tại backend:

~~~bat
python manage.py seed_ai_data
python manage.py rebuild_rag_index
~~~

Lệnh thứ nhất nạp giá dịch vụ mẫu; lệnh thứ hai tạo chỉ mục từ Markdown và sử dụng quota Gemini Embedding. Không chạy rebuild mỗi lần khởi động website.

Chatbot chỉ hiển thị khi đăng nhập bằng Customer hoặc Organizer. Chế độ tìm sự kiện dùng PostgreSQL trực tiếp, không gọi Gemini. Hai chế độ tìm sự kiện/tư vấn nhận bộ lọc từ form, chưa tự hiểu đầy đủ mọi yêu cầu trong câu chat.

Xem [hướng dẫn chatbot](backend/ai_agent/README.md) để cập nhật dữ liệu và chạy evaluation.

## 10. Kiểm thử và CI

Tại backend đã kích hoạt venv:

~~~bat
python manage.py check
python manage.py test -v 2
~~~

Tại frontend:

~~~bat
npm run build
~~~

Test backend dùng database test và giả lập dịch vụ ngoài. RAG evaluation thật được chạy riêng vì sử dụng quota Google.

GitHub Actions kiểm tra backend và build frontend khi push hoặc mở pull request vào main. Workflow hiện không có job deploy; cấu hình triển khai website online được quản lý riêng.

Xem [TEST_COMMANDS.md](documents/TEST_COMMANDS.md) để chạy theo app/file. Kết quả trong [TEST_REPORT.md](documents/TEST_REPORT.md) là kết quả theo ngày ghi nhận, không phải cam kết source mới nhất đã được kiểm thử lại.

## 11. Lỗi thường gặp

| Hiện tượng | Kiểm tra |
|---|---|
| Không nhận lệnh py, npm hoặc git | Cài công cụ, kiểm tra PATH, mở CMD mới |
| Không tìm thấy Django/thư viện | Kích hoạt venv và cài requirements.txt |
| Không kết nối database | PostgreSQL/Docker đã chạy chưa, đúng DB_HOST/DB_PORT/mật khẩu chưa |
| vector is not available | PostgreSQL server chưa có pgvector; pip install không thay thế extension |
| Trang chủ không có dữ liệu | Database chưa có sự kiện PUBLISHED hoặc backend/API URL chưa đúng |
| Upload ảnh lỗi | Kiểm tra ba khóa Cloudinary |
| Thanh toán trả 503 | Kiểm tra khóa PayOS; không tự bật bỏ qua chữ ký trên server public |
| Không nhận email trong Gmail | Kiểm tra console backend hay SMTP, cấu hình tài khoản gửi |
| Không thấy chatbot | Dùng tài khoản Customer/Organizer, không dùng Admin |
| RAG chưa có dữ liệu | Kiểm tra đúng database, API key và đã rebuild index chưa |
| Google báo hết hạn mức | Kiểm tra quota của đúng model, không rebuild/test API thật liên tục |

Sau khi sửa backend/.env phải khởi động lại backend. Sau khi sửa frontend/.env phải khởi động lại Vite. Khi chuyển database, đăng xuất và đăng nhập lại bằng tài khoản của database đang dùng.

## 12. Tài liệu

- [Dữ liệu mẫu và database demo](database/README.md)
- [Danh mục tài liệu](documents/README.md)
- [Lệnh kiểm thử](documents/TEST_COMMANDS.md)
- [Kế hoạch kiểm thử](documents/TEST_PLAN.md)
- [Báo cáo kiểm thử theo lần chạy](documents/TEST_REPORT.md)
- [Giả lập thanh toán local](documents/PAYMENT_TEST.md)
- [Chatbot và dữ liệu RAG](backend/ai_agent/README.md)
- [Hướng dẫn RAG evaluation](docs/RAG_EVALUATION.md)
- [Kết quả RAG evaluation](docs/RAG_EVALUATION_RESULT.md)
- [Frontend](frontend/README.md)

## 13. Giới hạn hiện tại

- Quyết toán Organizer là mô phỏng, không chuyển tiền thật; chưa hoàn tiền PayOS thật.
- Chưa có luồng sửa và xóa sự kiện hoàn chỉnh cho Organizer.
- Giao diện check-in nhận mã vé; chưa tích hợp camera quét QR.
- ChatWidget chưa khôi phục toàn bộ lịch sử/card kết quả cũ sau khi tải lại trang.
- Chưa có kiểm thử giao diện tự động bằng Selenium/Playwright; build không thay thế thao tác thử trên trình duyệt.
- Dữ liệu, giá dịch vụ, mật khẩu mẫu chỉ dùng để minh họa; không sử dụng nguyên trạng cho môi trường thật.
