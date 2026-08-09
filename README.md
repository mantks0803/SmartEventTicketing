# SmartEventTicketing

//.\\venv\\Scripts\\activate.bat



\##pagination -> undd
##hoạt ảnh banner chính!!\\



\##hoạt ảnh banner chính -> smooth transaction
##Hồ sơ -- arrow updown for user interact (nhớ kèm sweetarlet nếu cần)
\##update avatar - cloudinary

##!!!!tạo lại seed data tên event ? -> giống nhau toàn bộ ?



##user threads -> payment -> mail sending ?


Hoàn thiện PayOS webhook: chữ ký, số tiền, transaction ID, chống webhook lặp.
Hoàn thiện QR và check-in: chỉ vé PAID, chống check-in hai lần.
Sửa permission: organizer chỉ quản lý sự kiện của mình, khóa user phải chặn đăng nhập.
Đồng bộ frontend: payment cancel/return, countdown, trạng thái đơn và ghế.
Dashboard và báo cáo lấy dữ liệu API thật.
Thêm test race condition, IDOR và permission.

Những vấn đề quan trọng còn lại
Permission sự kiện vẫn sai
EventCreateView và danh sách sự kiện của BTC chỉ yêu cầu đăng nhập. Customer gọi vào có thể gây lỗi do code truy cập request.user.organizer, thay vì trả 403. API chi tiết cũng công khai cả sự kiện PENDING/CANCELLED. Xem [events/views.py (line 33)](/D:/SmartEventTicketing/events/views.py:33).
Khóa tài khoản vẫn không hoạt động đúng
Model có cả status và is_active, nhưng đăng nhập chỉ kiểm tra is_active. Trong khi Django Admin đang hiển thị/quản lý status, nên đặt status=False vẫn có thể đăng nhập. Xem [authentication/models.py (line 20)](/D:/SmartEventTicketing/authentication/models.py:20) và [authentication/serializers.py (line 74)](/D:/SmartEventTicketing/authentication/serializers.py:74).
Tạo sự kiện có nguy cơ lỗi và dữ liệu dở dang
Quá trình tạo Event → TicketType → Seat chưa nằm trong một transaction. Ngoài ra mọi loại vé mặc định dùng row_prefix='A'; nếu tạo nhiều loại vé không truyền prefix khác nhau, chúng có thể đụng unique constraint (event, row, number). Xem [events/serializers.py (line 27)](/D:/SmartEventTicketing/events/serializers.py:27) và [seating/models.py (line 27)](/D:/SmartEventTicketing/seating/models.py:27).
Thanh toán đến trễ chưa có luồng đối soát
Nếu PayOS xác nhận thành công sau khi đơn hết hạn, webhook trả ignored_expired nhưng chưa lưu bản ghi để hoàn tiền hoặc xử lý thủ công. Xem [orders/views.py (line 403)](/D:/SmartEventTicketing/orders/views.py:403).
Frontend thanh toán còn thiếu route
Backend mock tạo URL /payment-mock/:id, nhưng router frontend không có route này. PayOS cũng trả thẳng về /my-tickets, chưa có trang kết quả thành công, thất bại hoặc hủy riêng. Xem [orders/views.py (line 195)](/D:/SmartEventTicketing/orders/views.py:195).
QR và Dashboard vẫn chỉ là demo
Trang vé chỉ hiển thị icon và chuỗi qr_code, chưa render QR thật dù đã cài qrcode.vue. Dashboard vẫn hard-code 128.500.000 ₫, 450/500, 3 sự kiện. Xem [MyTicketsView.vue (line 43)](/D:/SmartEventTicketing/frontend/src/views/MyTicketsView.vue:43) và [OrganizerDashboardView.vue (line 25)](/D:/SmartEventTicketing/frontend/src/views/OrganizerDashboardView.vue:25).
Auth frontend chưa đồng bộ hoàn chỉnh
Router có meta.role nhưng guard không kiểm tra role. Khi API trả 401, interceptor xóa access token và user nhưng không xóa refresh token hay cập nhật Pinia state. Refresh token được lưu nhưng không có endpoint/flow refresh. API URL vẫn hard-code localhost. Xem [router/index.js (line 85)](/D:/SmartEventTicketing/frontend/src/router/index.js:85) và [api.js (line 5)](/D:/SmartEventTicketing/frontend/src/services/api.js:5).
AI, CRUD BTC và báo cáo chưa triển khai
ai_agent mới có model; serializer/view trống và URL không có endpoint. Organizer chưa có frontend tạo–sửa–xóa sự kiện, chưa có báo cáo doanh thu thật, payout và quản trị riêng. Xem [ai_agent/urls.py (line 3)](/D:/SmartEventTicketing/ai_agent/urls.py:3).



mà từ giờ nếu có fix lỗi thì chỉnh sửa ít nhất (ít làm thay đổi cả 1 nguyên khối refactor lớn) có thể và code sao cho đơn giản ,nhìn giống 1 sinh viên nhất có thể nha