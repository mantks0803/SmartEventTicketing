# Bản sao lưu riêng tư

Thư mục dành cho backup PostgreSQL của chủ sở hữu. **Clone mới không cần backup**; dùng migration và seed theo [hướng dẫn database](../README.md).

Backup có thể chứa thông tin cá nhân, mật khẩu đã băm, tài khoản ngân hàng, giao dịch, QR vé và hội thoại. Không chia sẻ công khai hoặc commit. Repository chỉ theo dõi README trong thư mục này; quy tắc ignore không bảo vệ file đã được Git theo dõi từ trước, nên luôn kiểm tra trước khi commit.

Trước khi khôi phục:

1. Xác nhận nguồn và quyền sử dụng; không chạy SQL từ nguồn không tin cậy.
2. Kiểm tra định dạng backup, phiên bản PostgreSQL và pgvector. SQL văn bản và archive tùy chỉnh dùng cách restore khác nhau.
3. Chọn **database mới riêng biệt**, không ghi đè database đang có dữ liệu cần giữ. Bảo quản bản sao gốc an toàn.
4. Sau khi kiểm tra dữ liệu, đổi `backend/.env` sang database đó, khởi động lại backend và đăng xuất/đăng nhập lại frontend.

**Không chạy `seed_data.py` trên database đã khôi phục:** script xóa toàn bộ sự kiện và dữ liệu liên quan. Không xóa Docker volume `smartticket_pgdata` để sửa lỗi restore; volume chứa dữ liệu đang dùng, không phải backup độc lập.
