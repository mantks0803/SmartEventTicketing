# Hướng dẫn xem báo cáo doanh thu của Ban tổ chức

> Đối tượng: Organizer  
> Danh mục kiến thức: POLICY  
> Nguồn: Giao diện Báo cáo doanh thu và API báo cáo sự kiện SmartEventTicketing  
> Cập nhật: 05/09/2026

## Điều kiện và cách mở báo cáo

1. Đăng nhập bằng tài khoản Organizer còn hoạt động.
2. Vào trang **Quản lý**, chọn tab **Báo cáo doanh thu**.
3. Trong ô **Chọn sự kiện**, chọn sự kiện muốn xem. Danh sách chỉ gồm sự kiện của BTC đang đăng nhập.
4. Chờ hệ thống tải số liệu, xem các thẻ tổng quan và hai bảng phía dưới.
5. Muốn lấy số liệu mới sau khi có người mua vé hoặc check-in, bấm nút có biểu tượng làm mới cạnh ô chọn sự kiện.

Nếu chưa có sự kiện, trang báo chưa có sự kiện để lập báo cáo. BTC không xem được báo cáo của người khác, kể cả khi tự đổi mã sự kiện trên đường dẫn API; backend trả không tìm thấy thay vì tiết lộ dữ liệu sự kiện khác.

## Ý nghĩa các số liệu tổng quan

| Chỉ số | Cách hiểu |
|---|---|
| Tổng ghế | Tổng số ghế của sự kiện |
| Đã bán | Số ghế đang ở trạng thái SOLD |
| Còn trống | Số ghế đang AVAILABLE |
| Đang giữ | Số ghế đang LOCKED, chưa được coi là đã bán |
| Đã check-in | Số vé thuộc đơn PAID đã được BTC soát vé thành công |
| Doanh thu | Tổng total_amount của các đơn PAID thuộc sự kiện |

Trước khi tổng hợp, hệ thống xử lý các đơn giữ ghế đã hết hạn để cập nhật trạng thái ghế. Số ghế đang giữ có thể giảm sau khi làm mới nếu đã hết 10 phút.

Doanh thu không tính các đơn PENDING, EXPIRED, CANCELLED hoặc REFUNDED. Doanh thu bán vé không phải lợi nhuận, vì báo cáo chưa trừ chi phí tổ chức, thuế hoặc mọi khoản phí thực tế.

## Bảng doanh thu theo loại vé

Mỗi dòng gồm tên loại vé, số vé đã bán và doanh thu của loại vé đó. Hệ thống chỉ lấy các dòng mua vé thuộc đơn PAID và cộng giá đã lưu khi khách mua (`OrderItem.unit_price`), không lấy giá hiện tại nhân lại cho đơn cũ.

Ví dụ minh họa: hai ghế được mua với giá 100.000 đồng mỗi ghế đóng góp 200.000 đồng cho loại vé tương ứng. Đây là ví dụ giải thích phép tính, không phải doanh thu thực tế của một sự kiện đang có.

## Bảng danh sách giao dịch

Danh sách chỉ gồm đơn PAID của sự kiện đã chọn. Mỗi dòng hiển thị mã đơn, tên khách, số ghế đã mua, tổng tiền và thời gian tạo đơn. Thời gian tạo không nhất thiết là thời điểm ngân hàng ghi nhận tiền.

Một đơn có thể mua nhiều ghế, nên số dòng giao dịch không bằng số vé. Đơn mới giữ ghế chưa thanh toán không xuất hiện trong bảng này.

## Nhãn Đã đối soát và Chưa đối soát

Nhãn này trên báo cáo BTC lấy từ `Event.is_payout_completed`, phản ánh trạng thái quyết toán được ghi nhận cho sự kiện. Nó khác thao tác kiểm tra giao dịch với PayOS của từng đơn hàng.

Trong bản demo, quyết toán do Admin xác nhận mang tính mô phỏng, không gọi API chuyển tiền thật. Nhãn “Đã đối soát” không phải bằng chứng tiền đã chuyển vào ngân hàng của BTC và không biến doanh thu thành số tiền thực nhận. BTC xem trạng thái tại báo cáo, không tự xác nhận quyết toán bằng chatbot.

## Câu hỏi thường gặp

**Có người chọn ghế mà doanh thu vẫn bằng 0?** Chọn hoặc giữ ghế chưa phải thanh toán. Kiểm tra sau khi đơn đã được hệ thống xác nhận PAID và làm mới báo cáo.

**PayOS báo thành công nhưng chưa tăng doanh thu?** Đơn trong hệ thống có thể chưa được xác nhận PAID. Nhờ Admin kiểm tra giao dịch, không tự cộng tiền hoặc sửa báo cáo chỉ dựa trên ảnh chuyển khoản.

**Vé đã bán nhiều hơn vé đã check-in có sai không?** Không nhất thiết. Khách đã trả tiền có thể chưa tới sự kiện hoặc chưa được soát vé.

**Chatbot cho biết doanh thu hiện tại của tôi được không?** Chatbot hiện hướng dẫn cách xem báo cáo, chưa có công cụ đọc báo cáo doanh thu riêng tư của BTC. Muốn biết số liệu thực tế, mở tab báo cáo; không dùng con số minh họa trong tài liệu thay dữ liệu trên trang.
