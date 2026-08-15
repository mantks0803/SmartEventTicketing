# Lệnh chạy test SmartEventTicketing

## 1. Kích hoạt môi trường

Chạy bằng Command Prompt:

```cmd
cd /d D:\SmartEventTicketing
venv\Scripts\activate
cd backend
```

## 2. Chạy toàn bộ backend test

```cmd
python manage.py test -v 2
```

Nếu muốn dùng lại database test cũ:

```cmd
python manage.py test -v 2 --keepdb
```

## 3. Chạy test theo app

```cmd
python manage.py test authentication.tests -v 2
python manage.py test events.tests -v 2
python manage.py test seating.tests -v 2
python manage.py test orders.tests -v 2
```

## 4. Chạy một file test

Không ghi đuôi `.py` và dùng dấu chấm thay cho dấu `/`:

```cmd
python manage.py test orders.tests.test_admin_payout -v 2
python manage.py test orders.tests.test_payos -v 2
python manage.py test seating.tests.test_race_condition -v 2
python manage.py test authentication.tests.test_login -v 2
```

## 5. Chạy một test case cụ thể

```cmd
python manage.py test orders.tests.test_admin_payout.AdminPayoutTests.test_admin_can_complete_payout_only_once -v 2
```

## 6. Kiểm tra cấu hình và migration

```cmd
python manage.py check
python manage.py makemigrations --check --dry-run
```

## 7. Build frontend

```cmd
cd /d D:\SmartEventTicketing\frontend
npm run build
```

> Luôn chạy full backend test từ thư mục `backend` để Django tìm thấy đầy đủ test.
