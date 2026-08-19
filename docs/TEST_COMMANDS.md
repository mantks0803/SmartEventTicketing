# Lệnh kiểm thử SmartEventTicketing

## 1. Chuẩn bị trên Windows Command Prompt

```bat
cd /d <duong-dan-project>
venv\Scripts\activate.bat
cd backend
```

Backend tests sử dụng PostgreSQL. Database server phải đang chạy và extension pgvector phải có sẵn.

## 2. Kiểm tra cấu hình

```bat
python manage.py check
python manage.py makemigrations --check --dry-run
```

## 3. Chạy toàn bộ backend tests

```bat
python manage.py test -v 2
```

Dùng lại test database để chạy những lần sau nhanh hơn:

```bat
python manage.py test --keepdb -v 2
```

Nếu Django hỏi xóa `test_smart_booking_db` cũ, có thể nhập `yes` khi chắc chắn đó là database test. Cách không tương tác:

```bat
python manage.py test --keepdb --noinput -v 2
```

## 4. Chạy theo app

```bat
python manage.py test authentication.tests -v 2
python manage.py test events.tests -v 2
python manage.py test seating.tests -v 2
python manage.py test orders.tests -v 2
python manage.py test ai_agent.tests -v 2
```

## 5. Chạy một file test

Không ghi đuôi `.py`; dùng dấu chấm thay cho dấu `/`:

```bat
python manage.py test authentication.tests.test_admin_user_management -v 2
python manage.py test orders.tests.test_payos -v 2
python manage.py test orders.tests.test_admin_payout -v 2
python manage.py test seating.tests.test_race_condition -v 2
python manage.py test ai_agent.tests.test_chat_api -v 2
python manage.py test ai_agent.tests.test_event_tools -v 2
```

## 6. Chạy một test method

```bat
python manage.py test orders.tests.test_admin_payout.AdminPayoutTests.test_admin_can_complete_payout_only_once -v 2
```

## 7. RAG evaluation

Chỉ đánh giá retrieval; có gọi Gemini Embedding nhưng không gọi Gemini Chat:

```bat
python manage.py evaluate_rag
```

Đánh giá thêm một số câu trả lời Gemini:

```bat
python manage.py evaluate_rag --with-generation --generation-limit 5
```

Các unit test AI dùng mock, không tiêu tốn quota Google:

```bat
python manage.py test ai_agent.tests.test_rag_evaluation -v 2
```

## 8. Build frontend

```bat
cd /d <duong-dan-project>\frontend
npm ci
npm run build
```

> Race-condition test cần PostgreSQL vì SQLite không mô phỏng đúng khóa dòng `select_for_update()`.
