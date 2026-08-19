# SmartEventTicketing

SmartEventTicketing là đồ án nền tảng đặt vé sự kiện xây dựng bằng Django REST Framework, Vue 3 và PostgreSQL. Hệ thống hỗ trợ toàn bộ luồng từ tạo sự kiện, duyệt sự kiện, giữ ghế, thanh toán PayOS, phát hành vé QR, soát vé đến báo cáo doanh thu. Project còn có trợ lý AI sử dụng RAG, LangChain, Gemini và pgvector để giải đáp nghiệp vụ, tìm sự kiện và tư vấn chi phí tổ chức.

## Chức năng chính

### Khách hàng

- Đăng ký, đăng nhập JWT, cập nhật hồ sơ và ảnh đại diện.
- Xem sự kiện đã được duyệt, phân trang, tìm kiếm và lọc danh mục.
- Xem loại vé, ghế và trạng thái ghế.
- Chọn tối đa 5 ghế và giữ ghế trong 10 phút.
- Thanh toán PayOS, đối soát trạng thái khi quay lại website.
- Nhận email xác nhận sau khi thanh toán thành công.
- Xem vé đã thanh toán và mã QR của từng vé.

### Ban tổ chức

- Tạo sự kiện, loại vé, số hàng và số ghế trong một transaction.
- Upload thumbnail lên Cloudinary.
- Gửi sự kiện cho Admin duyệt trước khi mở bán.
- Xem dashboard và báo cáo doanh thu theo từng sự kiện.
- Soát QR đúng sự kiện thuộc quyền quản lý và chống check-in hai lần.

### Quản trị viên

- Duyệt hoặc từ chối sự kiện đang chờ.
- Xem, tìm kiếm, lọc, khóa và mở khóa tài khoản.
- Xem báo cáo doanh thu toàn hệ thống.
- Quản lý giao dịch, xem cảnh báo bất thường và đối soát lại với PayOS.
- Xác nhận quyết toán cho Organizer ở mức mô phỏng; hệ thống không chuyển tiền thật.

### Trợ lý AI

- `GENERAL`: hỏi đáp chính sách và nghiệp vụ bằng RAG Markdown, pgvector và Gemini.
- `RECOMMEND_EVENT`: tìm sự kiện hoặc kiểm tra ghế trực tiếp từ PostgreSQL, không gọi Gemini.
- `PLAN_EVENT`: tính chi phí từ dữ liệu dịch vụ, tính giá vé hòa vốn, tham khảo giá vé trong hệ thống và dùng RAG/Gemini để diễn giải.
- Lưu phiên chat, kiểm tra quyền sở hữu session và sử dụng tối đa 8 tin nhắn gần nhất làm memory.
- Có bộ evaluation đo Hit@4, source accuracy, no-answer accuracy và thời gian retrieval.

## Công nghệ

| Phần | Công nghệ |
|---|---|
| Backend | Python 3.12+, Django 6, Django REST Framework, SimpleJWT |
| Database | PostgreSQL, pgvector |
| Frontend | Vue 3, Vite, Pinia, Vue Router, Bootstrap 5, SweetAlert2 |
| Thanh toán | PayOS |
| Lưu ảnh | Cloudinary |
| AI | LangChain Core, Gemini, Gemini Embedding, PostgreSQL pgvector |
| Kiểm thử | Django TestCase/APITestCase, PostgreSQL race-condition tests, Vite build |
| CI | GitHub Actions |

## Cấu trúc thư mục

```text
SmartEventTicketing/
├── backend/
│   ├── manage.py
│   ├── config/                  # Cấu hình Django và URL gốc
│   ├── authentication/          # Tài khoản và phân quyền
│   ├── events/                  # Sự kiện và loại vé
│   ├── seating/                 # Ghế và sơ đồ ghế
│   ├── orders/                  # Đơn hàng, PayOS, vé, báo cáo
│   ├── ai_agent/                # RAG, event tools và chat API
│   ├── seed_data.py             # Dữ liệu sự kiện demo
│   └── requirements.txt
├── frontend/
│   ├── src/components/          # Component dùng chung và ChatWidget
│   ├── src/views/               # View theo nhóm role/chức năng
│   ├── src/services/            # Axios API client
│   └── src/stores/              # Pinia stores
├── docs/                        # Test plan, report và RAG evaluation
└── .github/workflows/ci-cd.yml
```

## Yêu cầu môi trường

- Git.
- Python 3.12 trở lên; khuyến nghị Python 3.12 giống môi trường CI.
- Node.js `^22.18.0` hoặc `>=24.12.0` và npm, đúng theo `frontend/package.json`.
- PostgreSQL có extension `pgvector`.
- Tùy chọn: tài khoản PayOS, Cloudinary, Gmail SMTP và Google AI Studio.

Frontend hiện gọi API tại `http://127.0.0.1:8000/api/`, vì vậy backend local nên chạy đúng port `8000`.

## Cài đặt từ GitHub trên Windows CMD

### 1. Clone project và tạo virtual environment

```bat
git clone <repository-url>
cd SmartEventTicketing

py -3.12 -m venv venv
venv\Scripts\activate.bat

python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

Nếu máy không có lệnh `py -3.12`, có thể dùng `python -m venv venv` với Python 3.12+.

### 2. Chuẩn bị PostgreSQL và pgvector

Cách nhanh bằng Docker, chỉ dùng Docker cho database:

```bat
docker run --name smartticket-postgres -e POSTGRES_DB=smart_booking_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d pgvector/pgvector:0.8.6-pg16
```

Hoặc dùng PostgreSQL cài trực tiếp. Tạo database và bật extension:

```sql
CREATE DATABASE smart_booking_db;
```

Sau đó kết nối vào `smart_booking_db` và chạy:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Migration của project cũng có lệnh bật extension, nhưng PostgreSQL phải được cài pgvector phía server và tài khoản database phải có quyền tạo extension.

### 3. Tạo file môi trường

Từ thư mục gốc:

```bat
copy backend\.env.example backend\.env
```

Mở `backend\.env` và sửa ít nhất thông tin database. Các khóa PayOS, Cloudinary, email và Gemini có thể để trống nếu chưa kiểm thử những chức năng tương ứng.

Không commit `backend/.env` hoặc bất kỳ API key thật nào lên GitHub.

### 4. Migration và tài khoản Admin

```bat
cd backend
python manage.py migrate
python manage.py createsuperuser
```

### 5. Dữ liệu demo tùy chọn

```bat
python seed_data.py
python manage.py seed_ai_data
```

> `python seed_data.py` xóa toàn bộ Event hiện có trước khi tạo dữ liệu mẫu. Do quan hệ cascade, dữ liệu loại vé, ghế, đơn hàng, thanh toán và vé liên quan cũng có thể bị xóa. Chỉ chạy trên database mới hoặc database demo.

Script sự kiện tạo tài khoản Organizer demo:

```text
Username: demo_organizer
Email: organizer@smartevent.vn
Password: 123456
```

`seed_ai_data` nạp dữ liệu chi phí dịch vụ từ JSON vào bảng `EventService` và có thể chạy lại an toàn bằng `update_or_create`.

Nếu đã cấu hình `GOOGLE_API_KEY`, tạo vector index cho RAG:

```bat
python manage.py rebuild_rag_index
```

Lệnh này dùng quota Gemini Embedding. Chỉ cần chạy lại khi tài liệu Markdown hoặc model embedding thay đổi.

### 6. Chạy backend

```bat
cd /d <duong-dan-project>\backend
..\venv\Scripts\activate.bat
python manage.py runserver
```

Backend chạy tại `http://127.0.0.1:8000`.

### 7. Chạy frontend

Mở một cửa sổ CMD khác:

```bat
cd /d <duong-dan-project>\frontend
npm ci
npm run dev
```

Frontend chạy tại `http://localhost:5173`.

## Cấu hình dịch vụ ngoài

### PayOS

Thanh toán thật cần đủ `PAYOS_CLIENT_ID`, `PAYOS_API_KEY` và `PAYOS_CHECKSUM_KEY`. Khi chạy thật phải giữ:

```env
PAYOS_SKIP_SIGNATURE_CHECK=False
```

PayOS không gọi được webhook vào localhost. Khi kiểm thử webhook thật cần public HTTPS tunnel và cấu hình URL:

```text
https://<public-domain>/api/orders/webhook/payos/
```

`PAYOS_SKIP_SIGNATURE_CHECK=True` chỉ dùng trong môi trường local có kiểm soát, không dùng trên server public. Xem hướng dẫn mock chi tiết trong `payment_test.txt`.

### Email

`.env.example` dùng console email backend để project chạy ngay mà không cần Gmail. Muốn gửi email thật, đổi sang SMTP backend và điền tài khoản/mật khẩu ứng dụng.

### Cloudinary

Cần ba biến `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` để Organizer upload thumbnail và người dùng upload avatar.

### Gemini và RAG

`GENERAL` và `PLAN_EVENT` cần `GOOGLE_API_KEY`. `RECOMMEND_EVENT` query database trực tiếp nên vẫn sử dụng được khi không có Gemini.

Không đổi `AI_EMBEDDING_DIMENSIONS` nếu chưa tạo migration mới và rebuild toàn bộ index, vì kích thước phải khớp cột vector trong PostgreSQL.

## Kiểm thử

Chạy kiểm tra cấu hình, migration và toàn bộ backend tests:

```bat
cd /d <duong-dan-project>\backend
..\venv\Scripts\activate.bat
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test -v 2
```

Chạy một file test:

```bat
python manage.py test orders.tests.test_payos -v 2
python manage.py test ai_agent.tests.test_chat_api -v 2
```

Build frontend:

```bat
cd /d <duong-dan-project>\frontend
npm ci
npm run build
```

Test AI sử dụng mock nên không gọi Google API. RAG evaluation thật có dùng quota embedding:

```bat
cd /d <duong-dan-project>\backend
python manage.py evaluate_rag
python manage.py evaluate_rag --with-generation --generation-limit 5
```

GitHub Actions tự chạy Django check, migration, toàn bộ backend tests và Vue production build khi push hoặc tạo pull request vào `main`.

## API chính

| Nhóm | Base URL |
|---|---|
| Authentication | `/api/auth/` |
| Events | `/api/events/` |
| Seats | `/api/seats/` |
| Orders, tickets và reports | `/api/orders/` |
| AI chatbot | `/api/ai/` |
| Django Admin | `/admin/` |

## Tài liệu

- [Lệnh chạy test](docs/TEST_COMMANDS.md)
- [Kế hoạch kiểm thử](docs/TEST_PLAN.md)
- [Báo cáo kiểm thử gần nhất](docs/TEST_REPORT.md)
- [Hướng dẫn RAG evaluation](docs/RAG_EVALUATION.md)
- [Kết quả RAG evaluation](docs/RAG_EVALUATION_RESULT.md)
- [Frontend](frontend/README.md)

## Giới hạn hiện tại

- Organizer chưa có luồng sửa và xóa sự kiện hoàn chỉnh.
- Admin payout chỉ là mô phỏng đánh dấu đã quyết toán, không chuyển tiền thật.
- Project chưa thực hiện hoàn tiền PayOS thật.
- ChatWidget chỉ giữ session hiện tại trên giao diện; reload trang không khôi phục card kết quả cũ.
- CI chỉ kiểm thử và build, chưa tự động deploy production.
- Thanh toán ngân hàng, SMTP thật, webhook public và giao diện trình duyệt vẫn cần kiểm thử thủ công trước khi demo.
