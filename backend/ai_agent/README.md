# Chatbot và dữ liệu RAG

Dành cho Customer/Organizer đã đăng nhập, còn hoạt động; Admin, staff và superuser bị chặn. API chính: `POST /api/ai/chat/`.

## Chức năng

| Chế độ | Cách hoạt động |
|---|---|
| `GENERAL` — Hỏi đáp | Tìm tài liệu theo vai trò bằng embedding/pgvector, gọi Gemini trả lời |
| `RECOMMEND_EVENT` — Sự kiện | Tìm tối đa 5 sự kiện sắp diễn ra hoặc kiểm tra ghế từ database; không gọi Google |
| `PLAN_EVENT` — Tổ chức | Python tính chi phí/giá vé từ database, kết hợp RAG/Gemini để diễn giải |

**Điều kiện tìm kiếm/tổ chức phải nhập trên form**, không tự suy ra đầy đủ từ câu chat. Giá dịch vụ là dữ liệu demo; giá vé tham khảo lấy từ hệ thống, không phải khảo sát thị trường. Kiểm tra ghế không giữ ghế hoặc đặt vé.

Mỗi tin tối đa 1.000 ký tự; dùng 8 tin gần nhất làm ngữ cảnh. Widget giữ phiên hiện tại, chưa tải lại lịch sử cũ khi refresh. API lịch sử `GET /api/ai/sessions/` và `GET /api/ai/sessions/<id>/messages/` chỉ cho xem phiên của chính người dùng.

## Chuẩn bị lần đầu

Hoàn tất [SETUP](../../documents/SETUP.md): PostgreSQL/pgvector, thư viện và migration. Điền `GOOGLE_API_KEY` riêng vào `backend/.env`; giữ các biến model từ [mẫu cấu hình](../.env.example).

Model phải được tài khoản Google hỗ trợ, còn quota; số chiều embedding giữ **768**. Khởi động lại backend sau khi đổi cấu hình. Không commit key.

Trong CMD tại `backend/`, đã kích hoạt môi trường và chọn đúng database:

```cmd
set PYTHONUTF8=1
python manage.py seed_ai_data
python manage.py rebuild_rag_index
```

| Lệnh | Tác dụng | Khi chạy lại |
|---|---|---|
| `seed_ai_data` | Tạo/cập nhật `EventService` từ JSON theo mã dịch vụ, không gọi Google | Khi đổi JSON hoặc dùng database mới; ghi đè dữ liệu các mã tương ứng |
| `rebuild_rag_index` | Chia Markdown, tạo embedding và thay dữ liệu tra cứu trong database; dùng quota Google | Khi đổi tài liệu/model embedding hoặc dùng database mới |

Rebuild cũng xóa tài liệu thuộc nguồn customer/organizer không còn trên đĩa. **Không chạy hai lệnh mỗi lần mở server.** Tìm sự kiện cần Event có sẵn; xem [dữ liệu mẫu](../../database/README.md) và cảnh báo trước khi seed.

## File cần biết

| Trong `backend/ai_agent/` | Vai trò |
|---|---|
| `data/knowledge/customer/`, `data/knowledge/organizer/` | Tài liệu Markdown dùng để trả lời |
| `data/event_services.json` | Giá dịch vụ mẫu để nạp database |
| `rag_engine/` | Nạp/tìm vector, trả lời RAG và tính toán |
| `models.py`, `serializers.py`, `views.py`, `urls.py` | Database, kiểm tra đầu vào, xử lý API |
| `management/commands/` | Các lệnh nạp và đánh giá |
| `data/evaluation/rag_questions.json` | Câu hỏi đánh giá, không dùng làm tài liệu trả lời |

Giữ nguyên đường dẫn dữ liệu. Bộ nạp đọc mọi `*.md` trong hai thư mục knowledge trên; không đặt README cài đặt hoặc bí mật vào đó.

## Kiểm tra và lỗi thường gặp

Test không gọi Google thật, chạy tại `backend/`: `python manage.py test ai_agent -v 2 --keepdb`. Vẫn cần PostgreSQL/pgvector và quyền tạo database test.

Đánh giá tìm tài liệu trên 30 câu hỏi:

```cmd
python manage.py evaluate_rag --report ..\docs\RAG_EVALUATION_LOCAL.md
```

Lệnh dùng quota embedding, chưa gọi chat. Thêm `--with-generation --generation-limit 5` nếu cần đánh giá cả câu trả lời. Xem [hướng dẫn evaluation](../../docs/RAG_EVALUATION.md); không chạy đánh giá thật trong CI hoặc ghi đè báo cáo muốn giữ.

- Không thấy widget: kiểm tra vai trò/trạng thái tài khoản.
- Thiếu thông tin: kiểm tra đúng database, tài liệu theo vai trò và đã rebuild chưa.
- AI lỗi/chậm: kiểm tra key, model, quota và log; không gửi liên tục khi hết quota. Tìm sự kiện vẫn không cần Google; dự toán có thể trả số liệu khi diễn giải lỗi.
- Thiếu sự kiện/dịch vụ: kiểm tra dữ liệu và điều kiện form; hệ thống không tự tìm dịch vụ trên Internet.
- Lỗi vector: kiểm tra pgvector phía PostgreSQL, migration và số chiều 768.

Tài liệu, câu hỏi, lịch sử gần nhất và số liệu tư vấn có thể gửi tới Google. Không đưa bí mật hoặc dữ liệu khách hàng thật vào demo.
