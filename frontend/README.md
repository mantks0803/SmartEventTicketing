# SmartEventTicketing Frontend

Giao diện Vue 3 + Vite, dùng Pinia, Vue Router, Axios, Bootstrap, SweetAlert2 và Chart.js. Xem [tổng quan hệ thống](../README.md) và [cài đặt lần đầu](../documents/SETUP.md); frontend không tự tạo database hay tài khoản.

## Chạy bằng Windows CMD

Cần Node.js thỏa `^22.18.0 || >=24.12.0` theo [package.json](package.json), npm và backend đã cấu hình. Ví dụ clone tại `%USERPROFILE%\SmartEventTicketing`:

```cmd
cd /d "%USERPROFILE%\SmartEventTicketing\frontend"
if not exist .env copy .env.example .env
npm ci
npm run dev
```

Mở địa chỉ Vite in ra, thường là `http://localhost:5173`; giữ backend và frontend cùng chạy. Lần sau chỉ cần `npm run dev`, không phải cài lại. Nếu Vite đổi cổng, đồng bộ `FRONTEND_URL` ở backend khi thử chuyển hướng thanh toán.

## Địa chỉ API

Trong `frontend/.env`:

```dotenv
VITE_API_URL=http://127.0.0.1:8000/api/
```

[api.js](src/services/api.js) đọc biến này và tự gắn Bearer token từ `localStorage`. Giữ `/api/` và dấu `/` cuối; không thêm `/api/` lần nữa vào API con. Sau khi đổi `.env`, khởi động lại Vite hoặc build lại.

**Biến `VITE_*` hiển thị trong mã trình duyệt. Không đặt API key, secret hay mật khẩu database trong frontend.** Các khóa dịch vụ thuộc `backend/.env`. Sau khi đổi database, đăng xuất và đăng nhập lại bằng tài khoản của database mới.

## Các vị trí chính trong `src/`

| Vị trí | Vai trò |
|---|---|
| `main.js`, `App.vue` | Khởi tạo ứng dụng và khung giao diện chung |
| `views/` | Trang theo nhóm public, auth, account, customer, organizer, admin |
| `components/` | Navbar, footer, banner, ghế, phân trang và khối admin/organizer/chat |
| `router/`, `stores/auth.js` | Route, kiểm tra vai trò giao diện và trạng thái đăng nhập |
| `services/api.js`, `assets/main.css` | Gọi API và CSS dùng chung |

CSS riêng đặt cạnh file `.vue` cùng tên. Quyền trên giao diện không thay thế permission backend. Chatbot chỉ hiện cho Customer/Organizer; xem [hướng dẫn AI](../backend/ai_agent/README.md).

## Build và kiểm tra

```cmd
npm run build
npm run preview
```

Build tạo `dist/`; `preview` chỉ xem thử bản build local, backend vẫn phải truy cập được. Không commit `dist/` hoặc `node_modules/`.

Hiện chưa có script `test`/`lint`; build thành công không thay thế kiểm thử thao tác. `npm run format` sửa định dạng code, không phải test. Xem [kế hoạch kiểm thử](../documents/TEST_PLAN.md) và [lệnh test backend](../documents/TEST_COMMANDS.md). Nếu trang không tải dữ liệu, kiểm tra backend, địa chỉ API và database đã migrate/nạp dữ liệu.
