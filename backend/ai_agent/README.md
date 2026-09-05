# AI Agent: chatbot và dữ liệu RAG

Chỉ Customer/Organizer đã đăng nhập, còn hoạt động được dùng chatbot; Admin, staff và superuser bị chặn. API chính: `POST /api/ai/chat/`. API đọc lịch sử: `GET /api/ai/sessions/`, `GET /api/ai/sessions/<id>/messages/`; người dùng chỉ xem phiên của mình. Widget hiện chỉ dùng phiên đang mở, chưa có danh sách lịch sử cũ.

## Ba chế độ

| Chế độ | Cách xử lý | Google API |
|---|---|---|
| `GENERAL` — Hỏi hệ thống | Tìm tài liệu theo vai trò rồi trả lời quy trình/chính sách; không tra đơn hay ghế cụ thể | Embedding + chat |
| `RECOMMEND_EVENT` — Tìm sự kiện | Query PostgreSQL theo form, tối đa 5 sự kiện đã xuất bản/chưa diễn ra; hoặc kiểm tra ghế theo tên | Không |
| `PLAN_EVENT` — Tư vấn tổ chức | Python tính từ `EventService` và giá vé trong database; RAG/Gemini diễn giải | Có cho diễn giải |

**Điều kiện tìm kiếm/dự toán phải nhập ở form, không tự suy ra toàn bộ từ câu chat.** Form tìm kiếm có danh mục, địa điểm, giá tối đa hoặc tên sự kiện; API hỗ trợ thêm ngày nhưng UI chưa có ô ngày. Form tổ chức cần loại sự kiện, số khách nguyên dương, chất lượng, địa điểm và ít nhất một nhóm dịch vụ. Thời lượng tùy chọn nhưng phải dương nếu nhập; dịch vụ theo giờ dùng thời lượng nhập hoặc mặc định của dịch vụ.

Tin nhắn tối đa 1.000 ký tự; ngữ cảnh lấy tối đa 8 tin gần nhất. Câu người dùng trước đó được ghép với câu hiện tại khi tìm tài liệu. Tìm/kiểm tra ghế không giữ ghế hay đặt vé; số ghế là trạng thái tại lúc truy vấn. Giá dịch vụ là mẫu demo, giá vé tham khảo chỉ từ hệ thống, không phải báo giá thị trường hay cam kết đặt dịch vụ.

## Vị trí dữ liệu và code

| Đường dẫn trong `backend/ai_agent/` | Vai trò |
|---|---|
| `data/knowledge/customer/`, `data/knowledge/organizer/` | Markdown kiến thức theo vai trò |
| `data/event_services.json` | Nguồn nạp dịch vụ mẫu vào `EventService` |
| `data/evaluation/rag_questions.json` | Câu hỏi đánh giá, không phải nguồn trả lời |
| `rag_engine/` | Tạo/tìm vector, trả lời RAG và tính toán nghiệp vụ |
| `management/commands/` | Các lệnh seed, rebuild và đánh giá |
| `models.py`, `serializers.py`, `views.py`, `urls.py` | Lưu dữ liệu, kiểm tra request, xử lý và định tuyến API |

Giữ nguyên vị trí `data/`: code đọc từ `settings.BASE_DIR` (`backend/`). Bộ nạp đọc mọi `*.md` dưới hai thư mục `knowledge/` trên; **không thêm README cài đặt hoặc bí mật vào đó**. README này nằm ngoài vùng nạp.

## Chuẩn bị và nạp lần đầu

Hoàn tất PostgreSQL + pgvector, môi trường Python, requirements và migration theo [SETUP](../../documents/SETUP.md). Điền các biến có sẵn trong [backend/.env.example](../.env.example) vào `backend/.env`:

```dotenv
GOOGLE_API_KEY=your-google-api-key
AI_CHAT_MODEL=gemini-3.6-flash
AI_EMBEDDING_MODEL=gemini-embedding-2
AI_EMBEDDING_DIMENSIONS=768
AI_MAX_CONTEXT_CHUNKS=4
```

Đây là model mặc định của repository, không đảm bảo tài khoản Google có quyền truy cập/còn quota. Không commit key; khởi động lại backend sau khi đổi cấu hình. Giữ số chiều `768` để khớp cột vector hiện tại.

Trong CMD tại `backend`, sau khi kích hoạt môi trường và kiểm tra đúng database:

```cmd
chcp 65001
set PYTHONUTF8=1
python manage.py seed_ai_data
python manage.py rebuild_rag_index
```

- `seed_ai_data`: tạo/cập nhật dịch vụ theo `code` từ JSON, không gọi Google và không tạo sự kiện. Chạy lại ghi đè các mã tương ứng bằng dữ liệu mẫu.
- `rebuild_rag_index`: chia Markdown, gọi embedding và ghi database; thay chunk, xóa tài liệu cũ thuộc nguồn customer/organizer không còn trên đĩa. Lệnh dùng quota Google.

**Không chạy lại khi chỉ khởi động server.** Rebuild khi đổi tài liệu/model embedding; không cần rebuild khi chỉ thêm câu hỏi đánh giá. Database mới cần nạp dữ liệu riêng. Chế độ tìm sự kiện cần Event có sẵn; xem [seed sự kiện](../../database/README.md) và cảnh báo xóa dữ liệu trước khi chạy.

## Đánh giá và kiểm thử

Tại `backend`, chạy một lần đánh giá và lưu file riêng, tránh ghi đè báo cáo đã commit:

```cmd
python manage.py evaluate_rag --report ..\docs\RAG_EVALUATION_LOCAL.md
```

Lệnh mặc định đo retrieval (tìm tài liệu) trên 30 câu hỏi, **dùng quota embedding nhưng không gọi chat**. Nếu cần đo cả câu trả lời, thêm `--with-generation --generation-limit 5` vào cùng lệnh; lượt đó chạy cả retrieval và tối đa 5 case generation. Xem [hướng dẫn evaluation](../../docs/RAG_EVALUATION.md) về chỉ số, phạm vi và cách đọc kết quả; không coi nó là kiểm thử đầy đủ form, memory hoặc công cụ nghiệp vụ.

Test không dùng Google thật: `python manage.py test ai_agent -v 2` (dùng mock, vẫn cần PostgreSQL/pgvector và quyền tạo database test). Không đưa rebuild/evaluation gọi Google thật vào CI, không dùng cấu hình database sản xuất để test.

## Giới hạn và xử lý nhanh

- Không thấy widget: kiểm tra vai trò và trạng thái tài khoản.
- Không đủ thông tin: kiểm tra tài liệu đúng vai trò/index; chỉ dùng đoạn có cosine distance ≤ `0.40`, không tự tìm web mở.
- AI gián đoạn: kiểm tra key, quyền model, quota và log; ngừng gọi lặp khi hết quota. Tìm sự kiện không cần Google; dự toán có thể vẫn trả số liệu khi diễn giải lỗi.
- Không tìm thấy sự kiện/dịch vụ: kiểm tra đúng database và điều kiện form. Sự kiện báo cáo đã diễn ra không được gợi ý; thiếu dịch vụ phù hợp thì báo thiếu dữ liệu.
- Lỗi vector: kiểm tra pgvector trên server, migration và số chiều `768`.

Tài liệu, câu hỏi, lịch sử gần nhất và dữ liệu dùng để diễn giải có thể được gửi tới Google. Không đưa bí mật/dữ liệu khách hàng thật vào demo; nội dung tài liệu và output AI không phải lệnh để thay đổi quyền hay thực thi hành động.
