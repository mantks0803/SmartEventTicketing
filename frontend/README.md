# SmartEventTicketing Frontend

Giao diện Vue 3 dùng Vite, Pinia, Vue Router, Axios, Bootstrap 5, Bootstrap Icons, SweetAlert2 và Chart.js. Thiết lập backend/database trước theo [README gốc](../README.md); frontend không tự tạo database hoặc tài khoản.

## Yêu cầu

- Node.js đúng `engines` trong [package.json](package.json): `^22.18.0 || >=24.12.0`. Node 22 phải từ `22.18.0` trong nhánh 22; Node 24 phải từ `24.12.0`. Node 20 hoặc 23 không thỏa điều kiện này.
- npm và lockfile `package-lock.json` đã có trong repository.
- Backend đang chạy tại `http://127.0.0.1:8000` theo cấu hình mặc định.

## Cài đặt và chạy bằng Windows CMD

Các ví dụ giả định project đã clone vào `%USERPROFILE%\SmartEventTicketing`:

```cmd
cd /d "%USERPROFILE%\SmartEventTicketing\frontend"
node --version
npm --version
if not exist .env copy .env.example .env
npm ci
npm run dev
```

Mở địa chỉ Vite in ra, thường là `http://localhost:5173`. Giữ cửa sổ backend và frontend cùng chạy. Nếu cổng 5173 bận, kiểm tra địa chỉ thực tế và đồng bộ `FRONTEND_URL` của backend khi thử luồng chuyển hướng thanh toán.

### Cấu hình API

File `frontend/.env` chỉ cần:

```dotenv
VITE_API_URL=http://127.0.0.1:8000/api/
```

Đây là tên biến mà [src/services/api.js](src/services/api.js) thực sự đọc. Giữ phần `/api/` và dấu `/` cuối vì các API con được gọi như `auth/...`, `events/...`, `ai/chat/`. Nếu bỏ biến này, client dùng cùng địa chỉ mặc định ở trên. Không thêm `/api/` lần thứ hai vào URL.

Vite nạp biến môi trường khi khởi động/build: sau khi sửa `.env`, dừng và chạy lại `npm run dev`; với bản build, cần build lại. Các biến `VITE_*` được đưa vào mã phía trình duyệt, vì vậy không đặt Google API key, PayOS secret, Cloudinary secret hay mật khẩu database trong frontend. Các khóa dịch vụ nằm trong `backend/.env`.

Client gửi Bearer token từ `localStorage`. Khi backend đổi sang database khác, hãy đăng xuất rồi đăng nhập lại bằng tài khoản của database mới, tránh dùng token và trạng thái người dùng cũ.

## Chức năng hiện có

- Trang chủ, banner, tìm kiếm/lọc/phân trang và chi tiết sự kiện.
- Chọn/giữ ghế, checkout PayOS, kết quả thanh toán và ví vé QR.
- Organizer: tạo sự kiện, dashboard, báo cáo doanh thu và soát vé bằng mã vé.
- Admin: duyệt sự kiện, quản lý tài khoản, báo cáo, giao dịch và quyết toán mô phỏng.
- ChatWidget: hỏi hệ thống, tìm sự kiện/kiểm tra ghế và form dự toán tổ chức.

Luồng thanh toán cần cấu hình PayOS ở backend; tải ảnh cần Cloudinary. Tính năng AI cần chuẩn bị dữ liệu và quyền truy cập Google theo [hướng dẫn AI Agent](../backend/ai_agent/README.md). Riêng tìm sự kiện/kiểm tra ghế của chatbot truy vấn database trực tiếp, không gọi Google. Widget chỉ dành cho Customer/Organizer đã đăng nhập; không hiển thị cho Admin. Dự toán và lọc sự kiện lấy tham số từ form, không tự trích xuất toàn bộ điều kiện từ câu gõ tự do.

## Cấu trúc chính

```text
src/
├── components/          # Navbar, footer, ghế, admin, organizer, chat
├── views/
│   ├── account/
│   ├── admin/
│   ├── auth/
│   ├── customer/
│   ├── organizer/
│   └── public/
├── router/              # Route và kiểm tra vai trò phía giao diện
├── services/api.js      # Axios client và Bearer token
├── stores/auth.js       # Trạng thái đăng nhập Pinia
└── assets/main.css      # CSS dùng chung
```

Các view/component có CSS riêng đặt cạnh file `.vue`. Kiểm tra route ở frontend không thay thế kiểm tra quyền tại API backend.

## Build và kiểm tra

Từ thư mục `frontend`:

```cmd
npm run build
npm run preview
```

Build tạo `frontend/dist/`; không commit `dist/` hoặc `node_modules/`. `preview` chỉ xem thử bản build trên máy local, không phải cấu hình triển khai production. Backend vẫn phải chạy và địa chỉ API phải truy cập được từ trình duyệt.

Hiện `package.json` **không có script `test` hoặc `lint`**. `npm run build` kiểm tra khả năng build, không thay thế kiểm thử tương tác trên trình duyệt. `npm run format` chỉnh định dạng các file trong `src/`, không phải lệnh kiểm thử. Xem [kế hoạch kiểm thử](../documents/TEST_PLAN.md) và [lệnh kiểm thử backend](../documents/TEST_COMMANDS.md) để kiểm tra luồng nghiệp vụ.

## Xử lý lỗi nhanh

- `npm ci` báo Node không hỗ trợ: kiểm tra phiên bản theo `engines`, sau đó cài lại dependency bằng `npm ci`.
- Trang hiện nhưng không tải sự kiện: kiểm tra backend, `VITE_API_URL`, database đã migration và dữ liệu đang có. Xem lỗi request trong công cụ phát triển của trình duyệt.
- Đăng nhập lỗi sau khi chuyển database: đăng xuất/đăng nhập lại; tài khoản ở database này không tự tồn tại trong database khác.
- Không có chatbot với tài khoản Admin: đây là giới hạn chủ động của ứng dụng, không phải lỗi cài đặt frontend.
