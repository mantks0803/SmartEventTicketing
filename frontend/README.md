# Frontend SmartEventTicketing

Giao diện Vue 3 + Vite. Nếu mới clone project, làm theo [SETUP](../documents/SETUP.md) để chuẩn bị cả backend và database.

## Cài và chạy

Cần Node.js `^22.18.0 || >=24.12.0` theo [package.json](package.json). Các lệnh dùng Windows CMD; thay đường dẫn nếu lưu project ở nơi khác.

```cmd
cd /d "%USERPROFILE%\SmartEventTicketing\frontend"
if not exist .env copy .env.example .env
npm ci
npm run dev
```

Lần sau chỉ cần `npm run dev`. Giữ backend cùng chạy và mở địa chỉ Vite hiển thị, thường là `http://localhost:5173`.

## Địa chỉ backend

Trong `frontend/.env`:

```dotenv
VITE_API_URL=http://127.0.0.1:8000/api/
```

Giữ `/api/` và dấu `/` cuối. [api.js](src/services/api.js) tự gắn token đăng nhập; đổi `.env` thì khởi động lại Vite hoặc build lại. Nếu cổng frontend thay đổi, cập nhật `FRONTEND_URL` ở backend khi thử thanh toán.

**Không đặt API key hoặc mật khẩu trong `VITE_*`: trình duyệt đọc được các biến này.** Sau khi chuyển database, đăng xuất và đăng nhập lại.

## Code và build

- `views/`: các trang theo chức năng; `components/`: các khối dùng chung.
- `router/`, `stores/auth.js`: điều hướng và trạng thái đăng nhập.
- `services/api.js`: gọi API. CSS riêng đặt cạnh file `.vue` cùng tên.
- Chatbot chỉ hiện cho Customer/Organizer đủ điều kiện; quyền thực sự vẫn được kiểm tra ở backend.

Chạy `npm run build` để tạo `dist/`; `npm run preview` để xem bản build local, vẫn cần backend. Không commit `dist/` hoặc `node_modules/`.

Chưa có script test giao diện tự động. Nếu trang không có dữ liệu, kiểm tra backend, API URL và database; xem [hướng dẫn kiểm thử](../documents/TEST_COMMANDS.md).
