# Báo cáo kết quả kiểm thử Smart Event Ticketing

## 1. Thông tin lần kiểm thử

| Nội dung | Giá trị |
|---|---|
| Ngày kiểm thử | 11/08/2026 |
| Nhánh Git | `folder-refactor` |
| Commit trước khi tái cấu trúc | `7534b34` |
| Môi trường | Máy local Windows |
| Backend | Python 3.14.6, Django 6.0.7 |
| Frontend | Node.js 24.14.1, Vue 3, Vite 8.2.0 |
| Database | PostgreSQL 18.4 |

> GitHub Actions sẽ dùng Python 3.12, Node.js 22.18.0 và PostgreSQL 16 để có môi trường ổn định, dễ lặp lại.

## 2. Kết quả tổng hợp

| Hạng mục | Tổng | Passed | Failed | Kết quả |
|---|---:|---:|---:|---|
| Authentication tests | 7 | 7 | 0 | PASS |
| Event tests | 23 | 23 | 0 | PASS |
| Seating tests | 5 | 5 | 0 | PASS |
| Order, PayOS, ticket và check-in tests | 35 | 35 | 0 | PASS |
| **Tổng backend** | **70** | **70** | **0** | **PASS** |
| Django system check | 1 lần | 1 | 0 | PASS |
| Migration check | 1 lần | 1 | 0 | PASS - No changes detected |
| Vue production build | 1 lần | 1 | 0 | PASS |

Tỷ lệ pass backend: **100%**.

## 3. Lệnh đã chạy

```powershell
cd backend
..\venv\Scripts\python.exe manage.py check
..\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
..\venv\Scripts\python.exe manage.py test -v 1
cd ..\frontend
npm.cmd run build
```

## 4. Kết quả thực tế

### Backend

```text
Found 70 test(s).
System check identified no issues (0 silenced).
Ran 70 tests in 61.810s
OK
```

### Frontend

```text
vite v8.2.0 building client environment for production...
175 modules transformed.
build completed successfully in 0.838s
```

### Workflow YAML

```text
YAML parsed successfully
Jobs: backend, frontend
```

## 5. Phạm vi đã xác nhận

- Đăng ký Customer và Organizer.
- Đăng nhập đúng, sai mật khẩu, tài khoản `is_active=False` và role Admin.
- Phân quyền Customer, Organizer và Admin.
- Danh sách event công khai, phân trang, tìm kiếm và lọc danh mục.
- Tạo event, tạo loại vé và ghế trong transaction.
- Upload ảnh Cloudinary bằng mock và duyệt event bởi Admin.
- Sơ đồ ghế, giữ ghế 10 phút, hủy đơn và giải phóng ghế hết hạn.
- Race condition hai Customer giữ cùng một ghế trên PostgreSQL.
- Tạo link PayOS test, kiểm tra chữ ký webhook, chống webhook lặp và đối soát giao dịch.
- Phát hành vé, danh sách vé của đúng Customer và không trả vé PENDING.
- Check-in QR một lần và quyền soát vé của đúng Organizer.
- Giữ nguyên template/script của 16 SFC và tách nguyên vẹn CSS scoped ra file riêng.

## 6. Dịch vụ ngoài trong test

| Dịch vụ | Cách kiểm thử |
|---|---|
| PayOS | Mock SDK hoặc bật `PAYOS_SKIP_SIGNATURE_CHECK` trong từng test cần thiết |
| Cloudinary | Mock `cloudinary.uploader.upload` |
| Email | Dùng `django.core.mail.backends.locmem.EmailBackend` |
| Ngân hàng | Không kết nối và không chuyển tiền thật |

## 7. GitHub Actions

| Workflow | Backend | Frontend | Trạng thái hiện tại |
|---|---|---|---|
| `.github/workflows/ci-cd.yml` | Chạy check, migration và 70 test | Chạy `npm ci` và `npm run build` | Chưa chạy trên GitHub vì chưa push theo yêu cầu |

## 8. Ghi chú và giới hạn

- Backend được chuyển nguyên khối vào `backend/`; logic model, serializer, view, API, route và Vue component không bị thay đổi.
- Test race condition cần PostgreSQL; không nên thay bằng SQLite.
- Luồng đăng nhập hiện khóa tài khoản bằng field `is_active`. Field `status` trong model chưa phải điều kiện khóa đăng nhập.
- Kiểm thử trình duyệt, email SMTP thật và thanh toán ngân hàng thật vẫn là kiểm thử thủ công ngoài phạm vi CI.
