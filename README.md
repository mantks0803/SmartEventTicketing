# SmartEventTicketing

Đồ án đặt vé sự kiện gồm Django REST Framework, Vue 3 và module AI dự kiến phát triển bằng LangChain.

## Cấu trúc dự án

```text
SmartEventTicketing/
├── backend/                  # Django REST Framework
│   ├── manage.py
│   ├── config/
│   ├── authentication/
│   ├── events/
│   ├── seating/
│   ├── orders/
│   ├── ai_agent/
│   │   └── rag_engine/       # Chưa triển khai logic RAG
│   ├── seed_data.py
│   ├── requirements.txt
│   └── .env
├── frontend/                 # Vue 3 + Vite
├── docs/                     # Test plan và test report
└── .github/workflows/        # GitHub Actions
```

## Chạy Backend

Mở PowerShell tại thư mục gốc dự án, sau đó chuyển vào backend:

```powershell
cd backend
..\venv\Scripts\python.exe -m pip install -r requirements.txt
..\venv\Scripts\python.exe manage.py migrate
..\venv\Scripts\python.exe manage.py runserver
```

File cấu hình môi trường của Django nằm tại `backend/.env`.

Nạp dữ liệu mẫu khi cần:

```powershell
cd backend
..\venv\Scripts\python.exe seed_data.py
```

## Chạy Frontend

```powershell
cd frontend
npm install
npm run dev
```

## Chạy kiểm thử

```powershell
cd backend
..\venv\Scripts\python.exe manage.py test -v 2
cd ..\frontend
npm run build
```

Hoặc nếu đang ở thư mục gốc, build frontend riêng:

```powershell
cd frontend
npm run build
```

Xem kế hoạch và kết quả kiểm thử trong thư mục `docs/`.
