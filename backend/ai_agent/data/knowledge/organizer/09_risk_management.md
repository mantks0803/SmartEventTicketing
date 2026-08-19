# Quản lý rủi ro và phương án dự phòng

> Đối tượng: Organizer  
> Danh mục kiến thức: PLANNING  
> Nguồn: Quy trình SmartEventTicketing và hướng dẫn nội bộ phục vụ đồ án  
> Cập nhật: 19/08/2026

## Mục đích

Tài liệu này giúp Ban tổ chức nhận diện rủi ro, xác định mức ưu tiên và chuẩn bị phương án phản ứng. Đây là checklist lập kế hoạch, không thay thế tư vấn pháp lý, an toàn, y tế hoặc kỹ thuật chuyên môn.

## Cách lập danh sách rủi ro

Với mỗi rủi ro, ghi rõ:

- Mô tả.
- Khả năng xảy ra: thấp, trung bình hoặc cao.
- Mức ảnh hưởng: thấp, trung bình hoặc cao.
- Dấu hiệu cảnh báo.
- Cách phòng ngừa.
- Người chịu trách nhiệm.
- Phương án khi xảy ra.
- Thời điểm cần quyết định dừng hoặc thay đổi chương trình.

Ưu tiên xử lý các rủi ro có khả năng và ảnh hưởng đều cao.

## Rủi ro thời tiết

Đối với sự kiện ngoài trời:

- Theo dõi dự báo từ nguồn tin cậy.
- Xác định khu vực trú, mái che hoặc địa điểm thay thế.
- Bảo vệ thiết bị điện và đường dây.
- Quy định thời điểm quyết định chuyển hoặc hoãn.
- Chuẩn bị cách thông báo cho khách.

Chatbot không được tự quyết định điều kiện thời tiết có đủ an toàn để tiếp tục chương trình.

## Rủi ro địa điểm và sức chứa

- Địa điểm không sẵn sàng đúng giờ.
- Bố trí thực tế giảm số ghế.
- Ùn tắc tại lối vào.
- Thiếu chỗ đỗ xe hoặc khu chờ.
- Mất điện, nước hoặc Internet.

Phòng ngừa bằng khảo sát, xác nhận bằng văn bản, sơ đồ luồng khách và phương án nguồn dự phòng.

## Rủi ro kỹ thuật

- Micro hoặc loa hỏng.
- Máy tính trình chiếu gặp lỗi.
- Mất file nội dung.
- Mạng không ổn định.
- Thiết bị quét QR không hoạt động.

Nên có thiết bị thay thế cho hạng mục quan trọng, sao lưu file cục bộ và chạy tổng duyệt trước khi mở cửa.

## Rủi ro nội dung và nhân sự

- Nghệ sĩ hoặc diễn giả đến trễ hay vắng mặt.
- Nhân sự thiếu hoặc không hiểu nhiệm vụ.
- Chương trình kéo dài quá thời gian.
- Thay đổi nội dung sát giờ.

Phương án gồm người thay thế, nội dung dự phòng, timeline rút gọn và quy định ai có quyền phê duyệt thay đổi.

## Rủi ro ngân sách

- Giá dịch vụ thay đổi.
- Phát sinh giờ làm hoặc vận chuyển.
- Bán vé thấp hơn dự kiến.
- Hỏng vật tư hoặc thiết bị.

Ngân sách nên có khoảng thấp–cao và khoản dự phòng mặc định 10% cho bản demo. Tỷ lệ này không bảo đảm đủ cho mọi trường hợp; các hợp đồng và báo giá thật phải được xác minh riêng.

## Rủi ro bán vé và giữ ghế

SmartEventTicketing đã xử lý một số rủi ro:

- Ghế được khóa khi tạo đơn để chống hai khách cùng mua.
- Mỗi đơn giữ ghế 10 phút.
- Đơn hết hạn giải phóng ghế khi luồng dọn đơn được gọi.
- Một Customer chọn tối đa 5 ghế mỗi đơn.
- Event phải `PUBLISHED` và chưa bắt đầu mới được giữ ghế.

Organizer vẫn cần theo dõi ghế đã bán, ghế đang giữ và sức chứa thực tế. Ghế `LOCKED` không được tính là đã bán.

Project demo không có worker dọn đơn chạy nền liên tục. Việc hết hạn được xử lý khi có request liên quan hoặc khi chạy lệnh `python manage.py release_expired_orders`; khi triển khai thật cần đặt lịch cho lệnh này.

## Rủi ro thanh toán

Các tình huống gồm:

- PayOS báo thành công nhưng backend chưa cập nhật.
- Sai mã đơn hoặc số tiền.
- Webhook gửi lặp.
- Giao dịch đến sau khi đơn hết hạn.
- Ghế đã được cấp cho đơn khác trước khi giao dịch muộn được xử lý.

Backend đối soát mã đơn, số tiền, số tiền còn lại và mã tham chiếu. Logic phát hành vé có chống lặp. Nếu PayOS đã nhận tiền nhưng ghế không còn an toàn, API trả cảnh báo cần kiểm tra thủ công và khách không nên thanh toán lại. Project hiện chưa có field `manual_review`, hàng đợi xử lý thủ công hoặc quy trình hoàn tiền thật trong database.

## Rủi ro check-in

- Khách chia sẻ QR.
- QR bị quét trước.
- Hai thiết bị cùng quét một vé.
- Organizer khác cố quét vé.
- Mất kết nối tại cổng.

Hệ thống chỉ cho Organizer sở hữu Event check-in, khóa Ticket khi cập nhật và từ chối vé đã sử dụng. Ban tổ chức cần chuẩn bị mạng dự phòng và quầy xử lý trường hợp bất thường.

## Rủi ro dữ liệu và quyền truy cập

- Chia sẻ tài khoản Organizer.
- Lộ QR của khách.
- Dùng dữ liệu khách cho mục đích ngoài phạm vi.
- Tin vào nội dung do chatbot suy đoán.

Không chia sẻ mật khẩu, token hoặc dữ liệu thanh toán. Chatbot không có quyền tự sửa Event, Order, Payment, Ticket hoặc Seat.

## Quy trình phản ứng khi có sự cố

1. Xác định sự cố và mức ảnh hưởng.
2. Bảo đảm an toàn cho người tham dự trước.
3. Báo người chịu trách nhiệm.
4. Kích hoạt phương án đã chuẩn bị.
5. Ghi lại thời gian, quyết định và kết quả.
6. Thông báo cho khách bằng nội dung đã được duyệt nếu cần.
7. Sau sự kiện, phân tích nguyên nhân và cập nhật checklist.

## Khi chatbot phải dừng tư vấn

Chatbot phải yêu cầu xác minh chuyên môn khi câu hỏi liên quan trực tiếp đến:

- Quyết định an toàn đám đông.
- Kết cấu sân khấu và tải trọng.
- Phòng cháy chữa cháy.
- Y tế khẩn cấp.
- Điều kiện pháp lý hoặc giấy phép.
- Cam kết hợp đồng và bảo hiểm.

Chatbot có thể đưa checklist nhưng không được khẳng định sự kiện đã đáp ứng đầy đủ quy định.
