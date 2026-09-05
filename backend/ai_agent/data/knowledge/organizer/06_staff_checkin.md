# Nhân sự vận hành, an ninh và check-in

> Đối tượng: Organizer  
> Danh mục kiến thức: PLANNING  
> Nguồn: Quy trình SmartEventTicketing và hướng dẫn nội bộ phục vụ đồ án  
> Cập nhật: 05/09/2026

## Mục đích

Tài liệu này hướng dẫn phân công nhân sự và soát vé bằng mã vé trên SmartEventTicketing. Giao diện hiện hỗ trợ nhập mã thủ công, chưa có chức năng mở camera quét QR. Số lượng nhân sự phụ thuộc địa điểm, quy mô và yêu cầu an toàn thực tế.

## Các nhóm nhân sự thường gặp

### Trưởng Ban tổ chức

Chịu trách nhiệm quyết định chung, duyệt thay đổi quan trọng và liên hệ với địa điểm hoặc đối tác chính.

### Điều phối chương trình

Theo dõi timeline, phối hợp MC, diễn giả, nghệ sĩ, kỹ thuật và các bộ phận vận hành.

### Nhân sự check-in

Hướng dẫn khách mở vé, chuẩn bị mã, kiểm tra thông báo và chuyển trường hợp bất thường cho người phụ trách. Việc phân công nhân sự ngoài thực tế không tự cấp cho họ quyền truy cập phần mềm; hệ thống chưa có tài khoản nhân viên soát vé riêng.

### Nhân sự hỗ trợ khách

Giải đáp vị trí, chỗ ngồi, lịch trình và tiếp nhận các vấn đề không xử lý được tại quầy check-in.

### Nhân sự kỹ thuật

Vận hành âm thanh, ánh sáng, màn hình, mạng hoặc thiết bị quét theo phạm vi đã phân công.

### An ninh và kiểm soát luồng

Phối hợp với địa điểm để quản lý lối vào, khu vực hạn chế, hàng chờ và tình huống khẩn cấp.

### Y tế và ứng phó sự cố

Tùy quy mô và yêu cầu của địa điểm, cần xác định người hoặc đơn vị chịu trách nhiệm sơ cứu và liên hệ hỗ trợ khẩn cấp.

## Cách ước lượng nhân sự

Ban tổ chức cần dựa trên:

- Số khách dự kiến.
- Khoảng thời gian khách tập trung đến.
- Số cổng vào.
- Tốc độ nhập hoặc đọc mã vé thực tế.
- Số khu vực cần giám sát.
- Mức độ phức tạp của chương trình.

Ban tổ chức cần đo thử thời gian xử lý một vé, gồm lấy mã, gửi yêu cầu và xem kết quả, rồi mới ước lượng số quầy. Không coi tốc độ xử lý giả định là số liệu đo được của website. Với nhiều khách đến cùng lúc, có thể chia hàng chờ và bố trí người hướng dẫn chuẩn bị mã trước.

## Chuẩn bị trước sự kiện

1. Lập danh sách vai trò và người phụ trách.
2. Ghi rõ giờ có mặt và khu vực làm việc.
3. Cung cấp số điện thoại hoặc kênh liên lạc nội bộ.
4. Hướng dẫn cách xử lý tình huống thường gặp.
5. Kiểm tra thiết bị và tài khoản Organizer.
6. Chạy thử mã vé hợp lệ, mã đã dùng và mã không tồn tại trên môi trường thử nghiệm.
7. Thống nhất người có quyền quyết định khi phát sinh tranh chấp.

Không dùng vé thật của khách để thử, vì check-in thành công sẽ đánh dấu vé đã sử dụng. Chỉ dùng vé thử trong môi trường demo.

## Quyền check-in trên SmartEventTicketing

Chỉ tài khoản Organizer sở hữu sự kiện mới được phép soát vé của sự kiện đó. Customer hoặc Organizer khác nhận lỗi permission.

Backend kiểm tra:

- Mã vé tồn tại, khớp với `Ticket.qr_code`.
- Order của Ticket đang `PAID`.
- Ticket thuộc sự kiện của Organizer đang đăng nhập.
- Ticket chưa được check-in.

Việc kiểm tra và cập nhật được thực hiện trong transaction để hạn chế hai thiết bị cùng xác nhận một vé.

## Các bước soát vé trên website

1. Đăng nhập bằng tài khoản Organizer sở hữu sự kiện, vào trang **Quản lý**.
2. Chọn tab **Soát vé**.
3. Yêu cầu khách mở email chứa vé hoặc vào **Vé của tôi**, chọn **Xem mã QR** để lấy chuỗi mã vé.
4. Nhập hoặc dán đầy đủ chuỗi mã vào ô soát vé. Không nhập mã đơn, tên ghế hoặc mã giao dịch PayOS thay cho mã vé.
5. Bấm **Soát vé ngay** hoặc nhấn Enter và chờ kết quả. Thiết bị quét ngoài chỉ dùng được nếu nó đưa chuỗi mã vào ô nhập; không cần thiết bị này để dùng chức năng.
6. Nếu thành công, hệ thống đánh dấu vé đã check-in và lưu thời gian. Nếu báo lỗi, kiểm tra nguyên nhân trước khi cho khách vào.

Khách không tự check-in bằng chatbot. BTC cũng không được bỏ qua kiểm tra bằng cách tự sửa dữ liệu hoặc chấp nhận ảnh chuyển khoản thay vé.

Mỗi ghế có một Ticket và một QR riêng. Nếu một đơn mua nhiều ghế, từng vé phải được kiểm tra riêng.

## Xử lý tình huống tại quầy

### Không thấy ảnh QR hoặc không có máy quét

Dùng chuỗi mã vé trong email hoặc bên dưới QR trên website để nhập thủ công. Không cần tìm nút mở camera trong giao diện hiện tại.

### Mã vé không tồn tại

Kiểm tra chuỗi có đủ ký tự, đúng vé và không bị nhầm với mã đơn. Khách cần mở vé bằng đúng tài khoản đã mua hoặc email chứa vé. Không tự tạo mã thay thế.

### Vé đã check-in

Không xác nhận lần hai. Chuyển trường hợp cho người phụ trách cùng mã đơn và thông tin vé để kiểm tra thời gian check-in đã lưu.

### Không có quyền soát vé

Kiểm tra tài khoản đang đăng nhập có phải Organizer của chính sự kiện không. Không chuyển sang tài khoản BTC bất kỳ hoặc chia sẻ mật khẩu để vượt giới hạn quyền.

### Khách có bằng chứng chuyển tiền nhưng chưa có vé

Không xác nhận vào cửa chỉ dựa trên ảnh. Kiểm tra trạng thái Order và liên hệ Admin nếu giao dịch cần đối soát.

### Mất kết nối

Thử mạng dự phòng và giữ hàng chờ có trật tự. Nhập mã thủ công vẫn cần kết nối server, không phải chế độ check-in ngoại tuyến. Nếu mất mạng ngay sau khi gửi, hệ thống có thể đã ghi nhận; kiểm tra kết quả trước khi gửi lại và xử lý thông báo vé đã dùng qua người phụ trách.

## Sau sự kiện

Organizer có thể xem tổng số vé đã check-in trong báo cáo doanh thu sự kiện. Nên so sánh:

- Vé đã bán.
- Vé đã check-in.
- Khách không đến.

Phiên bản hiện tại chưa thống kê thời điểm check-in đông nhất; muốn có chỉ số này cần bổ sung báo cáo theo mốc thời gian.

Dữ liệu này hỗ trợ cải thiện số quầy và thời gian mở cửa cho lần tổ chức sau.

## An toàn thông tin

- Không chụp hoặc phát tán QR của khách.
- Không chia sẻ mật khẩu tài khoản Organizer; người hỗ trợ chuẩn bị mã không tự có quyền soát vé trong hệ thống.
- Không yêu cầu mật khẩu hoặc OTP ngân hàng.
- Khóa thiết bị check-in khi không sử dụng.
- Chỉ truy cập dữ liệu cần thiết cho sự kiện mình quản lý.
