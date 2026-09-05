# Thanh toán đơn hàng qua PayOS

> Đối tượng: Customer  
> Danh mục kiến thức: POLICY  
> Nguồn: Luồng thanh toán PayOS của SmartEventTicketing  
> Cập nhật: 05/09/2026

## Mục đích

Tài liệu này mô tả quá trình thanh toán qua PayOS, cách hệ thống xác nhận giao dịch và cách xử lý khi trạng thái thanh toán chưa cập nhật ngay.

## Điều kiện để tạo liên kết thanh toán

Hệ thống chỉ tạo liên kết PayOS khi:

- Người yêu cầu là Customer sở hữu đơn hàng.
- Đơn đang ở trạng thái `PENDING`.
- Đơn chưa hết 10 phút giữ ghế.
- Sự kiện vẫn ở trạng thái `PUBLISHED`.
- Sự kiện chưa bắt đầu.

Nếu một trong các điều kiện trên không còn đúng, khách hàng phải làm theo thông báo trên màn hình và không nên cố thanh toán lại đơn cũ.

## Các bước thanh toán

1. Khách hàng giữ ghế thành công và được chuyển đến trang thanh toán.
2. Trang thanh toán hiển thị mã đơn, các ghế, tổng tiền và thời gian còn lại.
3. Khách hàng chọn thanh toán qua PayOS.
4. Backend tạo liên kết thanh toán bằng đúng mã đơn và tổng tiền.
5. Trình duyệt chuyển sang trang PayOS.
6. Khách hàng thực hiện thanh toán theo hướng dẫn của PayOS.
7. PayOS chuyển khách hàng về trang kết quả thanh toán.
8. Trang kết quả yêu cầu backend đối soát giao dịch cho đến khi có kết quả cuối cùng hoặc hết số lần kiểm tra tự động.

Trạng thái hoặc chữ hiển thị trên đường dẫn trả về không được dùng làm bằng chứng thanh toán. Backend phải kiểm tra dữ liệu trực tiếp từ PayOS.

## Backend kiểm tra những gì?

Khi PayOS báo giao dịch đã thanh toán, backend kiểm tra:

- Mã đơn PayOS có khớp với mã đơn trên hệ thống không.
- Tổng tiền yêu cầu có bằng tổng tiền đơn hàng không.
- Số tiền PayOS ghi nhận đã thanh toán có bằng chính xác tổng tiền đơn hàng không.
- Số tiền còn thiếu có bằng 0 không.
- PayOS có cung cấp mã tham chiếu giao dịch ngân hàng không.
- Mã giao dịch có bị sử dụng cho đơn khác không.
- Ghế của đơn có còn đủ điều kiện phát hành vé không.

Nếu dữ liệu không khớp, backend không tự chuyển đơn thành `PAID`.

## Khi thanh toán thành công

Sau khi xác nhận hợp lệ, hệ thống thực hiện trong một transaction:

- Chuyển đơn hàng sang `PAID`.
- Chuyển các ghế của đơn sang `SOLD`.
- Tạo một bản ghi Payment thành công.
- Lưu mã giao dịch PayOS nếu được cung cấp.
- Phát hành một Ticket cho mỗi ghế trong đơn.
- Tạo mã QR riêng cho từng Ticket.
- Sau khi dữ liệu được lưu an toàn, hệ thống thực hiện gửi email thanh toán thành công, kèm thông tin từng vé, ảnh QR và mã vé dùng để check-in thủ công.

Email chỉ là kênh thông báo. Trạng thái đơn và vé trong hệ thống mới là căn cứ chính. Việc email đến chậm hoặc bị chuyển vào thư mục spam không làm mất vé đã phát hành.

Để xem vé, chọn nút xem vé trên trang kết quả hoặc mở **Vé của tôi** bằng đúng tài khoản đã đặt. Một đơn mua nhiều ghế sẽ có nhiều vé, mỗi vé có mã riêng. Email chứa vé giúp khách chuẩn bị mã trước khi đến sự kiện; không cần đăng nhập chỉ để đọc mã đã có trong email.

## Chống xử lý giao dịch lặp

PayOS có thể gửi webhook nhiều lần hoặc khách hàng có thể bấm kiểm tra lại nhiều lần. Hệ thống kiểm tra trạng thái đơn và mã giao dịch để tránh:

- Tạo Payment trùng.
- Tạo Ticket trùng.
- Đánh dấu ghế bán nhiều lần.
- Gửi email thành công nhiều lần cho cùng một lần xử lý.

Nếu đơn đã `PAID`, yêu cầu đối soát lại chỉ trả về trạng thái thành công hiện có.

## Khi trang kết quả vẫn đang chờ

Việc PayOS hiển thị thanh toán thành công không có nghĩa frontend được tự chuyển đơn thành `PAID`. Có thể webhook hoặc yêu cầu đối soát đang đến chậm.

Khách hàng nên:

1. Giữ nguyên mã đơn.
2. Chọn **Kiểm tra lại** trên trang kết quả.
3. Mở “Vé của tôi” để xem vé đã được phát hành chưa.
4. Không thanh toán lại cùng đơn khi PayOS đã ghi nhận giao dịch.
5. Liên hệ hỗ trợ nếu trạng thái không cập nhật sau một khoảng thời gian hợp lý.

Khi liên hệ, cần cung cấp mã đơn, email tài khoản, thời gian thanh toán, số tiền và mã tham chiếu giao dịch nếu có. Không gửi mật khẩu hoặc mã QR vé.

## Không nhận được email sau thanh toán

1. Mở **Vé của tôi** và chọn **Làm mới** để kiểm tra vé đã phát hành.
2. Kiểm tra hộp thư của email gắn với tài khoản đã mua vé, bao gồm thư rác hoặc spam.
3. Nếu đã có vé trên website, dùng mã vé tại đó; không thanh toán lại để yêu cầu một email khác.
4. Nếu cả email lẫn website đều chưa có vé, giữ mã đơn và yêu cầu hỗ trợ kiểm tra trạng thái giao dịch.

Chatbot không có chức năng tự gửi lại email, truy cập giao dịch cá nhân hoặc tự chuyển đơn thành đã thanh toán. Không cung cấp mật khẩu, OTP ngân hàng hoặc mã vé đầy đủ trong cuộc trò chuyện.

## Thanh toán đến sau khi đơn hết hạn

Trong một số trường hợp hiếm, PayOS có thể xác nhận giao dịch sau thời điểm giữ ghế kết thúc. Backend chỉ phát hành vé nếu các ghế cũ vẫn còn an toàn, chưa được bán và chưa bị đơn khác giữ.

Nếu ghế đã được cấp cho đơn khác, hệ thống không tự phát hành vé và đánh dấu tình huống cần Admin kiểm tra. Khách hàng không nên thanh toán thêm lần nữa; hãy liên hệ hỗ trợ và cung cấp mã đơn.

Thông báo cần kiểm tra không phải xác nhận hoàn tiền. Project chưa có luồng tự hoàn tiền thật về ngân hàng; không được hứa rằng tiền sẽ tự được hoàn sau một khoảng thời gian cố định.

## Khi người dùng hủy trên PayOS

Nếu giao dịch không thành công hoặc bị hủy, đơn không được phát hành vé. Tùy thời điểm xử lý, đơn có thể chuyển sang `CANCELLED` hoặc `EXPIRED`, và các ghế được giải phóng nếu vẫn do đơn đó giữ.

Muốn mua lại, khách hàng cần kiểm tra trạng thái ghế và tạo đơn mới.

## Những điều không nên làm

- Không chuyển sai số tiền hoặc sửa nội dung giao dịch do PayOS cung cấp.
- Không dùng liên kết của đơn hàng khác.
- Không thanh toán lại chỉ vì trang kết quả cập nhật chậm.
- Không coi ảnh chụp màn hình chuyển khoản là bằng chứng để frontend tự phát hành vé.
- Không chia sẻ mật khẩu, access token hoặc mã QR vé khi yêu cầu hỗ trợ.
