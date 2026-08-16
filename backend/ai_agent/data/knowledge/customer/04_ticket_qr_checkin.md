# Vé điện tử, mã QR và quy trình check-in

> Đối tượng: Customer  
> Danh mục kiến thức: POLICY  
> Nguồn: Quy trình phát hành và soát vé của SmartEventTicketing  
> Cập nhật: 17/08/2026

## Mục đích

Tài liệu này giải thích khi nào khách hàng nhận được vé điện tử, thông tin trên vé, cách sử dụng mã QR và các quy tắc check-in.

## Khi nào vé được phát hành?

Vé chỉ được phát hành sau khi backend xác nhận đơn hàng ở trạng thái `PAID`. Mỗi ghế đã thanh toán tạo ra một Ticket riêng và một mã QR riêng.

Các đơn `PENDING`, `CANCELLED`, `EXPIRED` hoặc `REFUNDED` không được hiển thị như vé hợp lệ trong “Vé của tôi”. Việc có OrderItem hoặc từng giữ ghế không đồng nghĩa với việc đã có vé.

## Xem vé ở đâu?

Khách hàng đăng nhập bằng đúng tài khoản đã mua vé và mở mục **Vé của tôi**. Trang này lấy danh sách Ticket thuộc đơn `PAID` của chính khách hàng.

Sau khi thanh toán thành công, khách hàng có thể:

- Chọn nút xem vé từ trang kết quả thanh toán.
- Mở “Vé của tôi” từ thanh điều hướng.
- Chọn **Làm mới** nếu vé vừa được phát hành nhưng danh sách chưa cập nhật.

Nếu đăng nhập bằng tài khoản khác, vé sẽ không xuất hiện.

## Thông tin trên vé

Một vé điện tử có thể hiển thị:

- Mã đơn hàng.
- Tên và hình ảnh sự kiện.
- Thời gian bắt đầu.
- Địa điểm.
- Loại vé.
- Tên ghế.
- Giá của ghế tại thời điểm tạo đơn.
- Trạng thái đã check-in hay chưa.
- Mã QR riêng của vé.

## Sử dụng mã QR

Khách hàng mở vé và chọn **Xem mã QR**. Khi vé chưa được sử dụng, hệ thống hiển thị QR để Ban tổ chức quét tại khu vực check-in.

Khách hàng nên:

- Chuẩn bị sẵn mã QR trước khi đến lượt check-in.
- Tăng độ sáng màn hình nếu máy quét khó nhận diện.
- Sử dụng đúng QR của đúng người và đúng ghế.
- Giữ thiết bị có đủ pin trong ngày diễn ra sự kiện.

## Bảo mật mã QR

Mã QR là thông tin xác nhận vé và không nên chia sẻ công khai. Không đăng ảnh QR lên mạng xã hội hoặc gửi cho người không liên quan.

Nếu người khác sử dụng mã QR trước, vé sẽ được đánh dấu đã check-in và không thể quét lần thứ hai. Hệ thống không thể phân biệt người quét đầu tiên có phải chủ tài khoản hay không chỉ dựa trên QR.

Khi liên hệ hỗ trợ, khách hàng nên cung cấp mã đơn nhưng không gửi toàn bộ QR nếu chưa được yêu cầu qua kênh hỗ trợ tin cậy.

## Ai được quyền soát vé?

Chỉ tài khoản Organizer sở hữu sự kiện của vé mới được phép check-in vé đó. Organizer của sự kiện khác và Customer không có quyền sử dụng API soát vé.

Backend kiểm tra:

- Mã QR có tồn tại không.
- Đơn của vé có đang `PAID` không.
- Vé có thuộc sự kiện của Organizer đang quét không.
- Vé đã được check-in trước đó chưa.

## Check-in thành công

Khi QR hợp lệ:

- Vé được đánh dấu `is_checked_in = true`.
- Hệ thống lưu thời gian check-in.
- Màn hình Organizer nhận thông báo soát vé thành công.
- Trang “Vé của tôi” hiển thị trạng thái **Đã soát vé** sau khi tải lại.
- QR không còn được hiển thị như một vé chưa sử dụng.

Quá trình kiểm tra và cập nhật vé được khóa trong transaction để hạn chế hai thiết bị quét cùng một QR tại cùng thời điểm.

## Check-in không thành công

Các trường hợp thường gặp:

- **QR không tồn tại:** mã sai, thiếu ký tự hoặc không thuộc hệ thống.
- **Vé chưa được thanh toán:** Order chưa ở trạng thái `PAID`.
- **Sai Ban tổ chức:** người quét không sở hữu sự kiện của vé.
- **Vé đã sử dụng:** QR đã được check-in trước đó.
- **Vé không còn hiệu lực:** trạng thái đơn không còn cho phép sử dụng vé.

Khách hàng không nên tự tạo hoặc chỉnh sửa chuỗi QR. Nếu vé hợp lệ nhưng không quét được, hãy cung cấp mã đơn và thông tin vé cho nhân viên sự kiện để kiểm tra.

## Email và vé trên hệ thống

Sau khi thanh toán được xử lý thành công, hệ thống có thể gửi email thông báo kèm thông tin vé. Tuy nhiên, “Vé của tôi” là nơi lấy trạng thái vé mới nhất từ database.

Không nhận được email không đồng nghĩa với việc chưa có vé. Khách hàng nên kiểm tra đúng tài khoản, thư mục spam và trang “Vé của tôi” trước khi liên hệ hỗ trợ.

