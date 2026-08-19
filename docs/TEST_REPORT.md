# Báo cáo kiểm thử SmartEventTicketing

## 1. Thông tin lần chạy gần nhất

| Nội dung | Giá trị |
|---|---|
| Ngày chạy | 19/08/2026 |
| Nhánh tại thời điểm chạy | `chatbox-6` |
| HEAD trước khi cập nhật tài liệu | `8d3ee00` |
| Môi trường local | Windows |
| Backend local | Python 3.14.6, Django 6.0.7 |
| Frontend local | Node.js 24.14.1, Vue 3, Vite 8.2.0 |
| Database local | PostgreSQL 18.4 với pgvector |
| CI dự kiến | Python 3.12, Node.js 22.18.0, PostgreSQL 16 với pgvector |

## 2. Kết quả tổng hợp

| Hạng mục | Tổng | Passed | Failed | Kết quả |
|---|---:|---:|---:|---|
| Authentication và Admin user | 20 | 20 | 0 | PASS |
| Events | 23 | 23 | 0 | PASS |
| Seating | 5 | 5 | 0 | PASS |
| Orders, PayOS, reports và payout | 55 | 55 | 0 | PASS |
| AI Agent, RAG và chat API | 36 | 36 | 0 | PASS |
| **Tổng backend** | **139** | **139** | **0** | **PASS** |
| Django system check | 1 | 1 | 0 | PASS |
| Migration check | 1 | 1 | 0 | PASS |
| Python dependency check | 1 | 1 | 0 | PASS |
| Vue production build | 1 | 1 | 0 | PASS |

Tỷ lệ pass backend: **100%**.

## 3. Lệnh đã chạy

```bat
cd /d <duong-dan-project>\backend
..\venv\Scripts\python.exe manage.py check
..\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
..\venv\Scripts\python.exe manage.py test --keepdb --noinput -v 1
..\venv\Scripts\python.exe -m pip check

cd /d <duong-dan-project>\frontend
npm.cmd run build
```

## 4. Output chính

### Backend

```text
System check identified no issues (0 silenced).
No changes detected
Found 139 test(s).
Ran 139 tests in 127.612s
OK
```

Test database được giữ lại bằng `--keepdb` để chạy các lần sau nhanh hơn.

### Dependencies

```text
No broken requirements found.
```

### Frontend

```text
vite v8.2.0 building client environment for production...
193 modules transformed.
build completed successfully.
```

Vite có cảnh báo bundle chính lớn hơn 500 kB. Đây là cảnh báo tối ưu hiệu năng, không phải lỗi build và không chặn bản demo.

## 5. Phạm vi đã xác nhận

- Đăng ký, đăng nhập, JWT, khóa tài khoản bằng cả `status` và `is_active`.
- Phân quyền và ownership của Customer, Organizer và Admin.
- Admin quản lý người dùng, thống kê và khóa/mở khóa tài khoản.
- Event công khai, tìm kiếm, lọc, phân trang, tạo event trong transaction và moderation.
- Upload Cloudinary bằng mock.
- Ghế, giới hạn 5 ghế, giữ 10 phút, giải phóng hết hạn và race condition.
- PayOS link, webhook signature, idempotency, reconcile và IDOR.
- Email xác nhận bằng memory backend, phát hành vé và QR check-in một lần.
- Báo cáo Organizer, báo cáo Admin, quản lý thanh toán và payout mô phỏng.
- Seed dữ liệu AI, chunking, pgvector retrieval, audience filter và RAG evaluation.
- Ba mode chat, session ownership, memory 8 tin nhắn và event tools.
- Vue ChatWidget và toàn bộ frontend biên dịch thành công.

## 6. Dịch vụ ngoài trong test tự động

| Dịch vụ | Cách test |
|---|---|
| PayOS | Mock SDK và response xác minh |
| Cloudinary | Mock hàm upload |
| Email | `locmem.EmailBackend` |
| Gemini Chat/Embedding | Fake model hoặc mock tại nơi sử dụng |
| Ngân hàng | Không kết nối và không chuyển tiền |

Do dùng mock, full backend test không tiêu tốn quota PayOS, Cloudinary, Gmail hoặc Google AI.

## 7. RAG evaluation gần nhất

Báo cáo ngày 18/08/2026 ghi nhận 30 câu hỏi với Hit@4, source accuracy, no-answer accuracy và answer decision accuracy đều đạt 100%. Đây là snapshot trước khi một số knowledge Markdown được đồng bộ ngày 19/08/2026; cần rebuild index và chạy lại evaluation để có kết quả mới. Xem [RAG_EVALUATION_RESULT.md](RAG_EVALUATION_RESULT.md).

## 8. GitHub Actions

Workflow `.github/workflows/ci-cd.yml` gồm:

- Backend job: PostgreSQL pgvector, cài requirements, check, migration và full test.
- Frontend job: `npm ci` và `npm run build`.

Workflow chạy khi push hoặc pull request vào `main`. Báo cáo này chỉ xác nhận local; trạng thái run trên GitHub cần xem trực tiếp trong tab Actions sau khi push.

## 9. Giới hạn

- Chưa có Selenium/E2E browser test trong CI.
- PayOS thật, webhook HTTPS, SMTP, Cloudinary và camera QR vẫn cần test thủ công.
- RAG evaluation thật dùng quota Gemini và không chạy trong CI.
- Payout chỉ cập nhật trạng thái mô phỏng, không chuyển tiền thật.
- Project chưa có deploy production tự động.
