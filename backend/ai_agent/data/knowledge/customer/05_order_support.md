# Trạng thái đơn hàng, đơn hết hạn và hướng dẫn hỗ trợ

> Đối tượng: Customer  
> Danh mục kiến thức: POLICY  
> Nguồn: Vòng đời đơn hàng của SmartEventTicketing  
> Cập nhật: 17/08/2026

## Mục đích

Tài liệu này giúp khách hàng hiểu trạng thái đơn hàng, biết khi nào cần tạo đơn mới và chuẩn bị thông tin cần thiết khi liên hệ hỗ trợ.

## Các trạng thái đơn hàng

### PENDING — Chờ thanh toán

Đơn đã được tạo và ghế đang được giữ tạm thời. Khách hàng cần thanh toán trước `expires_at`. Đơn `PENDING` chưa có vé điện tử.

### PAID — Đã thanh toán

Backend đã xác nhận giao dịch hợp lệ. Ghế được chuyển sang `SOLD`, Payment thành công được ghi nhận và Ticket được phát hành. Vé xuất hiện trong “Vé của tôi”.

### CANCELLED — Đã hủy

Đơn chờ thanh toán đã bị hủy hoặc giao dịch không thành công theo luồng xử lý hiện tại. Nếu ghế vẫn do đơn giữ, ghế được giải phóng. Đơn `CANCELLED` không phát hành vé.

### EXPIRED — Hết hạn

Đơn không được thanh toán trong thời gian giữ ghế. Ghế được giải phóng để người khác đặt. Muốn tiếp tục mua, khách hàng cần tạo đơn mới.

### REFUNDED — Đã hoàn tiền

Đây là trạng thái được model dự phòng cho nghiệp vụ hoàn tiền. Project hiện chưa triển khai quy trình hoàn tiền PayOS thật cho Customer. Chatbot không được tự cam kết rằng tiền đã được hoàn chỉ vì trạng thái này tồn tại trong code.

## Vì sao đơn hủy và hết hạn vẫn được lưu?

Đơn `CANCELLED` và `EXPIRED` được giữ trong database để:

- Theo dõi lịch sử giữ và giải phóng ghế.
- Hỗ trợ kiểm tra giao dịch đến trễ.
- Giúp Admin rà soát các trường hợp bất thường.
- Bảo đảm dữ liệu đơn, ghế và thanh toán nhất quán.

Những đơn này không cần xuất hiện trong “Vé của tôi”, vì trang đó chỉ dành cho Ticket thuộc đơn `PAID`.

## Khi nào khách hàng cần tạo đơn mới?

Khách hàng cần tạo đơn mới khi:

- Đơn cũ đã `EXPIRED`.
- Đơn cũ đã `CANCELLED`.
- Khách hàng đã hủy thanh toán và muốn chọn lại ghế.
- Sự kiện vẫn mở bán và ghế mong muốn còn `AVAILABLE`.

Không nên tạo đơn mới nếu PayOS đã trừ tiền nhưng hệ thống đang chờ đối soát. Trường hợp đó cần kiểm tra lại đơn cũ hoặc liên hệ hỗ trợ trước.

## Các trường hợp cần kiểm tra lại

### PayOS báo thành công nhưng chưa thấy vé

Khách hàng nên:

1. Chọn **Kiểm tra lại** trên trang kết quả thanh toán.
2. Mở “Vé của tôi” và chọn **Làm mới**.
3. Kiểm tra email và thư mục spam.
4. Không thanh toán lại đơn đó.
5. Liên hệ hỗ trợ nếu trạng thái vẫn chưa cập nhật.

### Đã hết thời gian giữ ghế nhưng chưa trả tiền

Đơn sẽ hết hạn và ghế được giải phóng. Khách hàng quay lại sự kiện để chọn ghế và tạo đơn mới.

### Đã chuyển tiền sau khi đơn hết hạn

Không tạo thêm giao dịch. Backend sẽ chỉ phát hành vé nếu dữ liệu PayOS hợp lệ và ghế vẫn an toàn. Nếu ghế không còn, giao dịch cần Admin kiểm tra thủ công.

### Có vé nhưng không nhận được email

Vé trên hệ thống vẫn có hiệu lực nếu Order đang `PAID`. Khách hàng kiểm tra địa chỉ email tài khoản, thư mục spam và sử dụng vé trong “Vé của tôi”.

### Không tìm thấy vé trong “Vé của tôi”

Kiểm tra:

- Đang đăng nhập đúng tài khoản Customer đã mua vé.
- Đơn đã thực sự chuyển sang `PAID`.
- Trang vé đã được làm mới.
- Thanh toán không còn ở trạng thái chờ đối soát.

## Thông tin nên cung cấp khi yêu cầu hỗ trợ

Khách hàng nên chuẩn bị:

- Mã đơn hàng.
- Email của tài khoản mua vé.
- Tên sự kiện.
- Số tiền đã thanh toán.
- Thời gian thanh toán.
- Mã tham chiếu giao dịch PayOS hoặc ngân hàng nếu có.
- Mô tả ngắn vấn đề và ảnh chụp trạng thái giao dịch nếu cần.

Khách hàng không được cung cấp:

- Mật khẩu.
- Access token hoặc refresh token.
- Mã OTP ngân hàng.
- Toàn bộ thông tin thẻ hoặc tài khoản ngân hàng.
- Mã QR vé ở nơi công khai.

Kênh email hỗ trợ đang hiển thị trên website là `dephucau@gmail.com`.

## Giới hạn hỗ trợ hiện tại

- Hệ thống chưa tự động hoàn tiền thật qua PayOS.
- Trạng thái `REFUNDED` trong model không phải bằng chứng tiền đã về tài khoản ngân hàng.
- Chatbot không có quyền tự sửa Order, Payment, Ticket hoặc Seat.
- Chatbot không được yêu cầu người dùng thanh toán lần nữa khi giao dịch cũ chưa được xác minh.
- Các trường hợp tiền đã chuyển nhưng vé không thể phát hành phải được Admin kiểm tra.

## Nguyên tắc trả lời của chatbot

Khi không đủ dữ liệu, chatbot phải nói rõ chưa thể kết luận và yêu cầu mã đơn hoặc hướng dẫn liên hệ hỗ trợ. Chatbot không được tự khẳng định giao dịch đã thành công, tự tạo vé, tự hứa hoàn tiền hoặc bịa trạng thái đơn hàng.
