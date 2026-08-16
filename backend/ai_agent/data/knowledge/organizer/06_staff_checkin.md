# Nhân sự vận hành, an ninh và check-in

> Đối tượng: Organizer  
> Danh mục kiến thức: PLANNING  
> Nguồn: Quy trình SmartEventTicketing và hướng dẫn nội bộ phục vụ đồ án  
> Cập nhật: 17/08/2026

## Mục đích

Tài liệu này hướng dẫn xác định vai trò nhân sự, phân công trách nhiệm và tổ chức check-in bằng QR. Số lượng nhân sự cuối cùng phụ thuộc địa điểm, quy mô và yêu cầu an toàn thực tế.

## Các nhóm nhân sự thường gặp

### Trưởng Ban tổ chức

Chịu trách nhiệm quyết định chung, duyệt thay đổi quan trọng và liên hệ với địa điểm hoặc đối tác chính.

### Điều phối chương trình

Theo dõi timeline, phối hợp MC, diễn giả, nghệ sĩ, kỹ thuật và các bộ phận vận hành.

### Nhân sự check-in

Hướng dẫn khách mở QR, quét vé, kiểm tra thông báo và chuyển trường hợp bất thường cho người phụ trách.

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
- Tốc độ quét QR thực tế.
- Số khu vực cần giám sát.
- Mức độ phức tạp của chương trình.

Để mô phỏng, có thể giả định một quầy xử lý khoảng 60–100 khách mỗi giờ trong điều kiện QR đã được chuẩn bị sẵn. Đây chỉ là giả định lập kế hoạch; Ban tổ chức phải chạy thử tại địa điểm trước khi chốt số quầy.

Ví dụ, 400 khách dự kiến đến trong một giờ không nên chỉ bố trí một thiết bị quét. Cần chia luồng, tăng số quầy hoặc mở cửa check-in sớm hơn.

## Chuẩn bị trước sự kiện

1. Lập danh sách vai trò và người phụ trách.
2. Ghi rõ giờ có mặt và khu vực làm việc.
3. Cung cấp số điện thoại hoặc kênh liên lạc nội bộ.
4. Hướng dẫn cách xử lý tình huống thường gặp.
5. Kiểm tra thiết bị và tài khoản Organizer.
6. Chạy thử một QR hợp lệ, QR đã dùng và QR không tồn tại trên môi trường thử nghiệm.
7. Thống nhất người có quyền quyết định khi phát sinh tranh chấp.

Không dùng QR vé thật của khách hàng để thử công khai trước sự kiện.

## Quyền check-in trên SmartEventTicketing

Chỉ tài khoản Organizer sở hữu sự kiện mới được phép soát vé của sự kiện đó. Customer hoặc Organizer khác nhận lỗi permission.

Backend kiểm tra:

- QR tồn tại.
- Order của Ticket đang `PAID`.
- Ticket thuộc sự kiện của Organizer đang đăng nhập.
- Ticket chưa được check-in.

Việc kiểm tra và cập nhật được thực hiện trong transaction để hạn chế hai thiết bị cùng xác nhận một vé.

## Quy trình check-in đề xuất

1. Hướng dẫn khách mở “Vé của tôi”.
2. Chọn đúng sự kiện và đúng vé.
3. Nhân sự quét QR bằng tài khoản Organizer phù hợp hoặc yêu cầy khách hàng xuất trình mã của Vé.
4. Chỉ cho khách vào khi hệ thống báo thành công.
5. Nếu vé đã sử dụng hoặc không hợp lệ, chuyển sang quầy hỗ trợ.
6. Không tự sửa trạng thái vé hoặc cho qua chỉ dựa trên ảnh chuyển khoản.

Mỗi ghế có một Ticket và một QR riêng. Nếu một đơn mua nhiều ghế, từng vé phải được kiểm tra riêng.

## Xử lý tình huống tại quầy

### QR khó quét

Tăng độ sáng màn hình, lau camera, giữ khoảng cách phù hợp và thử mở lại QR từ “Vé của tôi”. Có thể kiểm tra chuỗi QR theo quy trình nội bộ nếu thiết bị hỗ trợ.

### QR không tồn tại

Kiểm tra khách có đăng nhập đúng tài khoản và mở đúng vé không. Không tự tạo QR thay thế.

### Vé đã check-in

Không quét lại. Chuyển trường hợp cho người phụ trách cùng mã đơn và thông tin vé để kiểm tra thời gian check-in đã lưu.

### Khách có bằng chứng chuyển tiền nhưng chưa có vé

Không xác nhận vào cửa chỉ dựa trên ảnh. Kiểm tra trạng thái Order và liên hệ Admin nếu giao dịch cần đối soát.

### Mất kết nối

Thử mạng dự phòng và giữ hàng chờ có trật tự. Không ghi nhận check-in thủ công vào database nếu chưa có quy trình đồng bộ rõ ràng.

## Sau sự kiện

Organizer có thể xem số vé đã check-in trong báo cáo doanh thu sự kiện. Nên so sánh:

- Vé đã bán.
- Vé đã check-in.
- Khách không đến.
- Thời điểm đông nhất tại khu check-in.

Dữ liệu này hỗ trợ cải thiện số quầy và thời gian mở cửa cho lần tổ chức sau.

## An toàn thông tin

- Không chụp hoặc phát tán QR của khách.
- Không chia sẻ tài khoản Organizer cho người không được phân công.
- Không yêu cầu mật khẩu hoặc OTP ngân hàng.
- Khóa thiết bị check-in khi không sử dụng.
- Chỉ truy cập dữ liệu cần thiết cho sự kiện mình quản lý.

