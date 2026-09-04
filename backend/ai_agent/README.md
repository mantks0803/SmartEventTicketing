# AI Agent: chatbot và dữ liệu RAG

Chatbot dành cho Customer/Organizer đã đăng nhập và có tài khoản hoạt động. Admin, staff và superuser không được dùng các API chatbot. Frontend nằm tại `frontend/src/components/chat/ChatWidget.vue`; backend cung cấp `POST /api/ai/chat/`, danh sách phiên tại `GET /api/ai/sessions/` và tin nhắn tại `GET /api/ai/sessions/<id>/messages/`. Mỗi người chỉ truy cập được phiên chat của mình.

## Ba chế độ hiện có

| Chế độ | Nguồn dữ liệu và cách dùng | Cần Google API? |
|---|---|---|
| `GENERAL` — Hỏi hệ thống | Tìm tài liệu phù hợp theo vai trò, rồi tạo câu trả lời về quy trình/chính sách có trong tài liệu. Không tra trạng thái đơn hàng hay ghế cụ thể. | Có: embedding và chat |
| `RECOMMEND_EVENT` — Tìm sự kiện | Form lọc truy vấn PostgreSQL trực tiếp; hoặc nhập tên sự kiện để kiểm tra ghế. Tối đa 5 sự kiện đã xuất bản, chưa diễn ra và phù hợp điều kiện. | Không |
| `PLAN_EVENT` — Tư vấn tổ chức | Form cung cấp tham số; Python tính dự toán từ `EventService` và giá vé tham khảo trong database. RAG/Gemini diễn giải số liệu đó. | Có cho phần diễn giải; phép tính dùng database/Python |

Đây không phải chatbot tự suy ra mọi bộ lọc từ câu gõ tự do. Ở chế độ tìm sự kiện, hãy điền danh mục, địa điểm, giá tối đa hoặc tên sự kiện vào **form**. API có thêm `date_from`/`date_to`, nhưng form hiện tại chưa có hai ô ngày. Ở chế độ tư vấn, thay thông tin trong **form tổ chức** để thay dự toán; câu nhắn không tự ghi đè số khách, chất lượng hoặc dịch vụ đã chọn.

Form tổ chức bắt buộc: loại sự kiện, số khách nguyên dương, chất lượng, địa điểm và ít nhất một loại dịch vụ. Thời lượng là tùy chọn nhưng phải dương nếu nhập; dịch vụ tính theo giờ cần thời lượng nhập vào hoặc thời lượng mặc định của dịch vụ. Nếu không có dịch vụ phù hợp địa điểm/chất lượng/sức chứa, hệ thống báo thiếu dữ liệu, không tạo báo giá tùy ý. Số liệu là tham khảo cho demo, không phải báo giá hoặc cam kết đặt dịch vụ.

Tin nhắn tối đa 1.000 ký tự. Backend đưa tối đa 8 tin nhắn gần nhất vào ngữ cảnh và ghép câu người dùng trước đó với câu hiện tại để tìm tài liệu. Tìm sự kiện/kiểm tra ghế không đặt vé, giữ ghế hay thanh toán; số ghế còn là trạng thái tại thời điểm truy vấn.

## Các file dữ liệu phải giữ nguyên vị trí

```text
backend/ai_agent/
├── README.md                    # Hướng dẫn vận hành, không phải tài liệu RAG
├── data/
│   ├── event_services.json      # Danh mục dịch vụ mẫu để dự toán
│   ├── knowledge/
│   │   ├── customer/            # Markdown kiến thức dành cho khách hàng
│   │   └── organizer/           # Markdown kiến thức dành cho ban tổ chức
│   └── evaluation/
│       └── rag_questions.json   # Bộ câu hỏi đánh giá
├── management/commands/        # Seed, rebuild, evaluation
└── rag_engine/                  # Retrieval, trả lời và phép tính nghiệp vụ
```

Code đọc các thư mục trên tương đối từ `settings.BASE_DIR` (`backend/`). Không chuyển `data/` sang `database/`. Bộ nạp duyệt mọi file `*.md` bên dưới `knowledge/customer/` và `knowledge/organizer/`; vì vậy không đặt README cài đặt, thông tin bí mật hoặc hướng dẫn phát triển trong hai thư mục đó. README này cố ý nằm ngoài vùng nạp kiến thức.

## Chuẩn bị và nạp dữ liệu

Hoàn tất PostgreSQL + pgvector, Python 3.12, requirements và migration trong [README gốc](../../README.md). Trong `backend/.env`, cấu hình các biến đã có tại [`.env.example`](../.env.example):

```dotenv
GOOGLE_API_KEY=your-google-api-key
AI_CHAT_MODEL=gemini-3.6-flash
AI_EMBEDDING_MODEL=gemini-embedding-2
AI_EMBEDDING_DIMENSIONS=768
AI_MAX_CONTEXT_CHUNKS=4
```

Các tên model trên là cấu hình mặc định của repository, không đảm bảo tài khoản Google của bạn có quyền truy cập hoặc còn quota. Đặt API key thật chỉ trong file local, không commit. Khởi động lại backend sau khi đổi cấu hình. Kích thước embedding bắt buộc là `768` để khớp cột vector hiện tại; không đổi riêng biến môi trường sang số chiều khác.

Từ Windows CMD:

```cmd
cd /d "%USERPROFILE%\SmartEventTicketing"
call venv\Scripts\activate.bat
cd backend
chcp 65001
set PYTHONUTF8=1
python manage.py seed_ai_data
python manage.py rebuild_rag_index
```

Hai lệnh có mục đích khác nhau:

- `seed_ai_data` đọc `data/event_services.json`, tạo hoặc cập nhật `EventService` theo `code`. Không gọi Google và không seed sự kiện bán vé. Chạy lại sẽ cập nhật các mã có trong JSON bằng dữ liệu mẫu.
- `rebuild_rag_index` đọc Markdown, chia đoạn, gọi Google Embedding rồi lưu `KnowledgeBase`/`KnowledgeChunk` vào database đang chọn. Nó thay thế chunk của tài liệu đã xử lý và xóa tài liệu cũ thuộc nguồn `customer/`/`organizer/` không còn trên đĩa. Đây là thao tác ghi dữ liệu và dùng quota, không phải bước chạy mỗi lần khởi động server.

Cần rebuild sau khi sửa tài liệu hoặc thay model embedding để truy vấn và chỉ mục dùng cùng model. Việc chỉ thêm câu hỏi evaluation không yêu cầu rebuild. Dữ liệu dịch vụ/chỉ mục nằm riêng trong mỗi database: nếu chuyển sang database mới thì cần chuẩn bị lại ở database đó. Để có sự kiện cho chế độ tìm kiếm, dùng dữ liệu đã tạo trên ứng dụng hoặc xem [hướng dẫn seed sự kiện](../../database/README.md) và đọc cảnh báo xóa dữ liệu trước.

## Đánh giá và kiểm thử

Từ thư mục `backend`, với môi trường ảo đã kích hoạt:

```cmd
python manage.py evaluate_rag
python manage.py evaluate_rag --with-generation --generation-limit 5
```

Lệnh đầu đánh giá retrieval trên 30 câu hỏi hiện có: không gọi Gemini Chat nhưng vẫn gọi embedding cho các câu hỏi và tiêu tốn quota embedding. Lệnh thứ hai chạy lại retrieval và thêm generation cho tối đa 5 case được đánh dấu. Không cần chạy cả hai liên tiếp nếu chỉ muốn một lần đánh giá có generation. Lỗi quota/rate limit không đồng nghĩa code hoặc migration bị hỏng; ngừng gọi lặp lại, kiểm tra cấu hình và đợi quota phù hợp.

Có thể lưu kết quả vào một file riêng để không ghi đè báo cáo đã commit:

```cmd
python manage.py evaluate_rag --report ..\docs\RAG_EVALUATION_LOCAL.md
```

Đọc kết quả trước khi chia sẻ hoặc commit. Xem [hướng dẫn đánh giá RAG](../../docs/RAG_EVALUATION.md) để hiểu Hit@K, nguồn đúng, từ chối câu ngoài phạm vi và giới hạn phép đo. Evaluation độc lập không kiểm tra toàn bộ form, memory hội thoại, tìm sự kiện hay dự toán; nó cũng không tự làm CI thất bại chỉ vì tỷ lệ chất lượng thấp.

Kiểm thử AI dùng mock cho các lời gọi Google:

```cmd
python manage.py test ai_agent -v 2
```

Các test vẫn cần PostgreSQL/pgvector và quyền tạo database test. Không dùng database sản xuất cho cấu hình phát triển/kiểm thử. Không đưa các lệnh rebuild hoặc evaluation gọi Google thật vào CI.

## Khi chatbot không trả lời như mong đợi

- Không thấy widget: đăng nhập bằng Customer/Organizer hoạt động; Admin không có chatbot.
- `GENERAL` nói chưa đủ thông tin: kiểm tra tài liệu đúng vai trò và chỉ mục đã tạo. Chỉ các đoạn có cosine distance không lớn hơn `0.40` được dùng; hệ thống không có dữ liệu web mở để trả lời mọi chủ đề.
- AI tạm gián đoạn: kiểm tra key, quyền truy cập model, quota và log backend. `RECOMMEND_EVENT` không cần Google; ở `PLAN_EVENT`, số liệu dự toán có thể vẫn được trả về dù phần diễn giải AI lỗi.
- Không tìm thấy sự kiện: kiểm tra form lọc, trạng thái xuất bản, thời gian diễn ra và ghế còn. Sự kiện seed báo cáo là sự kiện đã diễn ra nên không được tìm ở chế độ này.
- Dự toán báo thiếu dịch vụ: kiểm tra đã chạy `seed_ai_data` ở đúng database và bộ lọc form khớp dữ liệu mẫu.
- Lỗi vector/embedding: xác nhận pgvector ở server, migration hoàn tất và số chiều vẫn là `768`.

Nội dung tài liệu, câu hỏi, phần lịch sử gần nhất và dữ liệu cấu trúc dùng để tạo câu trả lời có thể được gửi tới Google. Không đưa bí mật hoặc dữ liệu khách hàng thật vào bộ demo; tài liệu nguồn và output model không phải chỉ dẫn để thay đổi quyền truy cập hay thực thi hành động.
