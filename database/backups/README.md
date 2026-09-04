# Bản sao lưu riêng tư

Thư mục này dành cho bản dump/backup PostgreSQL do chủ sở hữu chủ động tạo hoặc cung cấp. **Không cần có backup để cài project mới**: sử dụng migration và dữ liệu mẫu theo [hướng dẫn database](../README.md). Không có bước bắt buộc lấy file từ Desktop, đường dẫn cá nhân hoặc máy của tác giả.

Backup có thể chứa email, số điện thoại, mật khẩu đã băm, tài khoản ngân hàng, lịch sử đơn hàng/thanh toán, vé QR và hội thoại. Không commit, đính kèm issue hay chia sẻ công khai các file này. Quy tắc ignore của repository giữ nội dung backup ngoài Git, chỉ README hướng dẫn được theo dõi; luôn kiểm tra danh sách file trước khi commit. Ignore không bảo vệ những file đã được theo dõi từ trước.

Trước khi khôi phục:

1. Xác nhận nguồn file, quyền sử dụng và nội dung cần khôi phục; không chạy SQL từ nguồn không tin cậy.
2. Xác định định dạng backup, phiên bản PostgreSQL và yêu cầu extension pgvector. File SQL văn bản và archive tùy chỉnh không dùng cùng cách restore.
3. Chọn một database mới dành riêng cho việc khôi phục. Không ghi đè `smart_booking_db` hoặc database đang có dữ liệu cần giữ.
4. Giữ bản sao an toàn trước khi thay đổi; bảo vệ backup bằng quyền truy cập phù hợp và phương thức lưu trữ riêng tư.
5. Sau khi kiểm tra dữ liệu khôi phục, trỏ `backend/.env` tới database đó, khởi động lại backend và đăng xuất/đăng nhập lại frontend.

Không chạy `seed_data.py` lên database đã khôi phục: script xóa toàn bộ sự kiện cùng dữ liệu liên quan. Không xóa Docker volume `smartticket_pgdata` để xử lý sự cố restore; volume là dữ liệu đang lưu, không phải bản backup độc lập.
