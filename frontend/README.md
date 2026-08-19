# SmartEventTicketing Frontend

Frontend Vue 3 cho hệ thống SmartEventTicketing. Giao diện sử dụng Vite, Pinia, Vue Router, Axios, Bootstrap 5, Bootstrap Icons và SweetAlert2.

## Chức năng giao diện

- Trang chủ, banner nổi bật, tìm kiếm, lọc và phân trang sự kiện.
- Chi tiết sự kiện, chọn ghế và giữ ghế.
- Checkout PayOS, trang kết quả thanh toán và ví vé QR.
- Dashboard Organizer, tạo sự kiện, báo cáo doanh thu và soát vé.
- Trang Admin duyệt sự kiện, quản lý tài khoản, doanh thu, giao dịch và quyết toán mô phỏng.
- ChatWidget AI với ba mode hỏi đáp, tìm sự kiện và tư vấn tổ chức.

## Cấu trúc chính

```text
src/
├── components/          # Navbar, footer, seat map, admin, organizer, chat
├── views/
│   ├── account/
│   ├── admin/
│   ├── auth/
│   ├── customer/
│   ├── organizer/
│   └── public/
├── router/              # Route và role guard
├── services/api.js      # Axios client và Bearer token
├── stores/auth.js       # Pinia authentication state
└── assets/main.css      # CSS dùng chung
```

Mỗi view/component có CSS riêng đặt cạnh file `.vue` và được nhúng bằng `<style scoped src="./TenFile.css"></style>`.

## Yêu cầu

- Node.js `^22.18.0` hoặc `>=24.12.0`, đúng theo `engines` trong `package.json`.
- Backend chạy tại `http://127.0.0.1:8000`.

## Cài đặt và chạy

Mở Command Prompt:

```bat
cd /d <duong-dan-project>\frontend
npm ci
npm run dev
```

Truy cập `http://localhost:5173`.

Nếu chưa có `package-lock.json` thì dùng `npm install`; project hiện đã có lockfile nên `npm ci` được khuyến nghị để cài đúng phiên bản.

## Build production

```bat
npm run build
```

Kết quả build nằm trong `frontend/dist/` và thư mục này không được commit.

Xem hướng dẫn cài toàn bộ backend, database, dịch vụ ngoài và test tại [README gốc](../README.md).
