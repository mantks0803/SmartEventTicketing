# Đánh giá chất lượng RAG

## 1. Mục tiêu

Evaluation dùng để kiểm tra chatbot có:

- Tìm đúng tài liệu liên quan đến câu hỏi.
- Giữ đúng nguồn sau khi lọc relevance.
- Từ chối câu hỏi nằm ngoài phạm vi SmartEventTicketing.
- Tạo câu trả lời có các ý nghiệp vụ bắt buộc.
- Phản hồi retrieval trong thời gian hợp lý.

Evaluation không thay thế unit test. Unit test kiểm tra code hoạt động đúng,
còn evaluation đo chất lượng kết quả tìm kiếm và câu trả lời.

Evaluation áp dụng trực tiếp cho retrieval của mode `GENERAL` và phần tư vấn
RAG trong `PLAN_EVENT`. Mode `RECOMMEND_EVENT` query PostgreSQL trực tiếp nên
được kiểm tra bằng test event tools, không dùng các chỉ số retrieval này.

## 2. Các file liên quan

- `backend/ai_agent/data/evaluation/rag_questions.json`: 30 câu hỏi chuẩn.
- `backend/ai_agent/management/commands/evaluate_rag.py`: lệnh chạy evaluation.
- `backend/ai_agent/tests/test_rag_evaluation.py`: test validation và công thức đo.

## 3. Các chỉ số

### Hit@K

Nguồn mong đợi có xuất hiện trong K kết quả retrieval đầu tiên hay không.

```text
Hit@K = số câu tìm thấy nguồn đúng / số câu có thể trả lời
```

Mặc định project dùng `K = 4`, bằng số chunk context tối đa hiện tại.

### Source accuracy

Kiểm tra nguồn đúng có còn lại sau khi áp dụng ngưỡng relevance `0.40`.

Một nguồn có thể nằm trong top 4 nhưng bị loại nếu cosine distance quá cao.

### No-answer accuracy

Đo tỷ lệ câu ngoài phạm vi không có chunk nào vượt qua relevance filter.

Ví dụ: thời tiết, chứng khoán, nấu ăn hoặc tư vấn thuốc.

### Answer decision accuracy

Đo quyết định tổng quát:

- Câu có tài liệu thì hệ thống cho phép trả lời.
- Câu ngoài phạm vi thì hệ thống từ chối.

### Generation keyword coverage

Kiểm tra câu trả lời có chứa các ý bắt buộc được khai báo trong dataset.
Chỉ số này chỉ chạy khi có tùy chọn `--with-generation`.

Đây là phép kiểm tra đơn giản phục vụ đồ án, không thay thế đánh giá ngữ nghĩa
chuyên sâu hoặc đánh giá thủ công.

## 4. Chạy retrieval evaluation

Mở Command Prompt:

```cmd
cd /d <duong-dan-project>
.\venv\Scripts\activate.bat
cd backend
chcp 65001
set PYTHONUTF8=1
python manage.py evaluate_rag
```

Lệnh này chạy toàn bộ 30 câu hỏi và mỗi câu tạo một embedding query. Nó không
gọi Gemini Chat nên không dùng quota generation, nhưng vẫn dùng quota Gemini
Embedding.

Với dataset hiện tại, một lần chạy đầy đủ dùng khoảng 30 request embedding.
Nếu quota Embedding hoặc RPM/RPD đã gần giới hạn, nên chờ quota được làm mới
thay vì chạy liên tục.

## 5. Lưu báo cáo Markdown

Từ thư mục `backend`:

```cmd
python manage.py evaluate_rag --report ..\docs\RAG_EVALUATION_RESULT.md
```

File kết quả gồm chỉ số tổng hợp và kết quả PASS/FAIL của từng câu hỏi.

## 6. Chạy generation evaluation

Chỉ chạy một số case được đánh dấu `run_generation=true`:

```cmd
python manage.py evaluate_rag --with-generation --generation-limit 5
```

Hoặc lưu báo cáo:

```cmd
python manage.py evaluate_rag --with-generation --generation-limit 5 --report ..\docs\RAG_EVALUATION_RESULT.md
```

Không nên chạy generation cho toàn bộ dataset liên tục vì ngoài embedding,
mỗi case generation còn dùng một lần gọi Gemini Chat và có thể chạm giới hạn
request trong ngày.

## 7. Chạy test tự động

```cmd
python manage.py test ai_agent.tests.test_rag_evaluation -v 2
```

Test sử dụng mock cho retrieval và chat model, vì vậy không gọi Google API và
không tiêu tốn quota.

Chạy toàn bộ test AI Agent:

```cmd
python manage.py test ai_agent -v 2
```

## 8. Cách sử dụng kết quả

1. Chạy evaluation với cấu hình hiện tại để lấy baseline.
2. Lưu lại báo cáo.
3. Chỉ thay chunk size, overlap hoặc relevance threshold khi có case thất bại.
4. Chạy lại cùng dataset sau khi thay đổi.
5. So sánh kết quả trước và sau.

Không nên thêm reranker hoặc hybrid search nếu `Hit@4`, source accuracy và
no-answer accuracy hiện tại đã tốt.

## 9. Cấu hình RAG hiện tại

- Embedding model: `gemini-embedding-2`.
- Kích thước vector: 768 chiều.
- Chia đoạn: 1.000 ký tự, overlap 120 ký tự.
- Số chunk context tối đa: 4.
- Ngưỡng cosine distance: `0.40`; số càng nhỏ càng gần câu hỏi.

Command evaluation in các chỉ số để người phát triển đọc và so sánh. Hiện tại
nó không tự làm CI thất bại chỉ vì một tỷ lệ chất lượng thấp. GitHub Actions
chỉ chạy các test có mock và không gọi Gemini thật.

## 10. Giới hạn và lưu ý

- Kết quả retrieval phụ thuộc model embedding và dữ liệu index hiện tại.
- Phải chạy `python manage.py rebuild_rag_index` sau khi sửa tài liệu Markdown.
- Không cần rebuild index khi chỉ thêm câu hỏi evaluation.
- Không đưa lệnh gọi Gemini thật vào GitHub Actions.
- Keyword coverage có thể thất bại khi Gemini diễn đạt đúng ý bằng từ đồng nghĩa;
  trường hợp đó cần đọc câu trả lời và đánh giá thủ công.
- Generation evaluation chỉ kiểm tra RAG độc lập. Nó không đo memory hội thoại,
  tool tìm sự kiện hoặc tool dự toán chi phí.
