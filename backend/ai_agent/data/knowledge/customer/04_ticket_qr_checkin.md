# Vé điện tử, mã QR và quy trình check-in

> Đối tượng: Customer  
> Danh mục kiến thức: POLICY  
> Nguồn: Quy trình phát hành và soát vé của SmartEventTicketing  
> Cập nhật: 05/09/2026

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

## Lấy mã vé và check-in thủ công

1. Mở email thanh toán thành công hoặc đăng nhập và vào **Vé của tôi**.
2. Chọn đúng sự kiện, loại vé và ghế. Trên website, bấm **Xem mã QR** để xem QR cùng chuỗi mã vé phía dưới.
3. Đưa mã vé đầy đủ cho Ban tổ chức. Mã cần nhập là chuỗi mã vé, không phải mã đơn hàng, số ghế hay mã giao dịch ngân hàng.
4. Ban tổ chức nhập hoặc dán mã vào mục **Soát vé** bằng tài khoản sở hữu sự kiện.
5. Chờ hệ thống báo soát vé thành công trước khi vào.

QR mã hóa chính chuỗi mã vé dùng để check-in thủ công. Giao diện BTC hiện chưa có chức năng mở camera để quét QR. Thiết bị quét ngoài có thể dùng nếu thiết bị đưa được chuỗi mã vào ô nhập; không bắt buộc có thiết bị này để soát vé.

Một đơn mua nhiều ghế có nhiều mã vé riêng. Cần kiểm tra từng vé, không dùng một mã cho cả đơn. Có thể chuẩn bị email trước khi đến sự kiện; BTC vẫn cần kết nối hệ thống để xác nhận trạng thái vé mới nhất.

## Bảo mật mã QR

Mã QR là thông tin xác nhận vé và không nên chia sẻ công khai. Không đăng ảnh QR lên mạng xã hội hoặc gửi cho người không liên quan.

Nếu người khác sử dụng mã vé trước, vé sẽ được đánh dấu đã check-in và không thể dùng lần thứ hai. Hệ thống không thể xác minh người cầm mã có phải chủ tài khoản chỉ dựa trên QR hoặc chuỗi mã vé. Cần bảo mật cả hai, không chỉ ảnh QR.

Khi liên hệ hỗ trợ, khách hàng nên cung cấp mã đơn nhưng không gửi toàn bộ QR nếu chưa được yêu cầu qua kênh hỗ trợ tin cậy.

## Ai được quyền soát vé?

Chỉ tài khoản Organizer sở hữu sự kiện của vé mới được phép check-in vé đó. Organizer của sự kiện khác và Customer không có quyền sử dụng API soát vé.

Backend kiểm tra:

- Mã vé có tồn tại không.
- Đơn của vé có đang `PAID` không.
- Vé có thuộc sự kiện của Organizer đang soát vé không.
- Vé đã được check-in trước đó chưa.

## Check-in thành công

Khi mã vé hợp lệ:

- Vé được đánh dấu `is_checked_in = true`.
- Hệ thống lưu thời gian check-in.
- Màn hình Organizer nhận thông báo soát vé thành công.
- Trang “Vé của tôi” hiển thị trạng thái **Đã soát vé** sau khi tải lại.
- QR không còn được hiển thị như một vé chưa sử dụng.

Quá trình kiểm tra và cập nhật vé được khóa trong transaction để hạn chế hai yêu cầu cùng xác nhận một vé tại cùng thời điểm.

## Check-in không thành công

Các trường hợp thường gặp:

- **Mã vé không tồn tại:** mã sai, thiếu ký tự hoặc không thuộc hệ thống. Kiểm tra có nhập nhầm mã đơn hay tên ghế không.
- **Vé chưa được thanh toán:** Order chưa ở trạng thái `PAID`.
- **Sai Ban tổ chức:** tài khoản soát vé không sở hữu sự kiện của vé.
- **Vé đã sử dụng:** QR đã được check-in trước đó.
- **Vé không còn hiệu lực:** trạng thái đơn không còn cho phép sử dụng vé.

Khách hàng không nên tự tạo hoặc chỉnh sửa mã vé. Nếu vé không được chấp nhận, hãy cung cấp mã đơn và thông tin vé cho người phụ trách sự kiện để kiểm tra qua kênh tin cậy, không đăng mã vé công khai.

## Email và vé trên hệ thống

Sau khi thanh toán được xử lý thành công, hệ thống thực hiện gửi email có thông tin từng vé, ảnh QR và mã vé để check-in thủ công. Không cần đăng nhập website chỉ để đọc mã đã nhận trong email. Nếu ứng dụng email không hiện ảnh QR, có thể dùng chuỗi mã vé bằng chữ.

Email là thông tin tại thời điểm gửi, không tự đổi sau khi vé đã check-in. “Vé của tôi” và kết quả soát vé của BTC lấy trạng thái mới nhất từ database. Không coi ảnh QR còn trong email là bằng chứng vé vẫn chưa được dùng.

Không nhận được email không đồng nghĩa với việc chưa có vé. Khách hàng nên kiểm tra đúng tài khoản, thư mục spam và trang “Vé của tôi” trước khi liên hệ hỗ trợ.

**Có thể tự check-in bằng chatbot không?** Không. Chatbot chỉ hướng dẫn cách lấy và sử dụng vé; thao tác xác nhận do BTC thực hiện ở mục “Soát vé”.

