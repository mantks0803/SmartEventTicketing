# Chọn ghế và giữ ghế khi mua vé

> Đối tượng: Customer  
> Danh mục kiến thức: POLICY  
> Nguồn: Quy trình đặt ghế của SmartEventTicketing  
> Cập nhật: 17/08/2026

## Mục đích

Tài liệu này giải thích trạng thái ghế, cách tạo đơn giữ ghế, giới hạn số lượng và điều gì xảy ra khi hết thời gian giữ ghế.

## Điều kiện để giữ ghế

Khách hàng chỉ có thể giữ ghế khi:

- Đã đăng nhập bằng tài khoản Customer còn hoạt động.
- Sự kiện đang ở trạng thái `PUBLISHED`.
- Sự kiện chưa bắt đầu.
- Ghế tồn tại và thuộc đúng sự kiện.
- Ghế chưa được bán hoặc chưa bị đơn hàng khác giữ.

Tất cả ghế trong một đơn phải thuộc cùng một sự kiện.

## Các trạng thái ghế

- `AVAILABLE`: ghế đang trống và có thể chọn.
- `LOCKED`: ghế đang được một đơn hàng giữ tạm thời.
- `SOLD`: ghế đã được thanh toán và bán thành công.

Ghế `LOCKED` hoặc `SOLD` không thể được một đơn mới giữ lại. Trạng thái hiển thị trên sơ đồ là dữ liệu tại thời điểm tải; trạng thái có thể thay đổi trước khi khách bấm giữ ghế.

## Cách chọn và giữ ghế

1. Mở trang chi tiết của sự kiện.
2. Chọn **Mở sơ đồ chọn ghế**.
3. Chọn ít nhất một ghế `AVAILABLE`.
4. Kiểm tra số ghế và tổng tiền tạm tính.
5. Chọn **Giữ ghế ngay**.
6. Backend kiểm tra lại toàn bộ ghế và tạo đơn nếu dữ liệu hợp lệ.
7. Khách hàng được chuyển đến trang thanh toán của đơn vừa tạo.

Giá của từng ghế được lấy từ loại vé gắn với ghế tại thời điểm tạo đơn. Đơn hàng lưu lại giá này để dùng trong quá trình thanh toán.

## Giới hạn số ghế

Mỗi đơn hàng phải có ít nhất một ghế và được chọn tối đa 5 ghế. Danh sách ghế không được chứa cùng một ghế nhiều lần.

Nếu khách cần mua nhiều hơn 5 ghế, khách phải tạo thêm đơn khác. Các đơn khác nhau được xử lý độc lập và không được đảm bảo nằm liền nhau.

## Thời gian giữ ghế

Sau khi tạo đơn thành công, hệ thống giữ ghế trong 10 phút. Thời điểm hết hạn được backend lưu trong `expires_at`; đồng hồ trên trang thanh toán chỉ hiển thị thời gian còn lại dựa trên mốc này.

Trong thời gian giữ ghế:

- Đơn hàng ở trạng thái `PENDING`.
- Ghế ở trạng thái `LOCKED`.
- Khách hàng khác không thể đặt các ghế đó.
- Khách hàng cần hoàn tất thanh toán trước thời điểm hết hạn.

Đóng trình duyệt hoặc rời trang không làm dừng bộ đếm ở server.

## Khi hết 10 phút

Nếu đơn chưa được thanh toán khi hết hạn:

- Đơn được chuyển sang `EXPIRED` khi hệ thống xử lý hết hạn.
- Các ghế đang được đơn giữ được trả về `AVAILABLE`.
- Liên kết thanh toán đã lưu bị xóa khỏi đơn.
- Đơn cũ không thể tiếp tục thanh toán theo luồng thông thường.
- Khách hàng phải mở lại sơ đồ và tạo đơn mới nếu ghế vẫn còn trống.

Đơn hết hạn vẫn được lưu trong database để quản lý lịch sử và bảo đảm tính nhất quán, nhưng không tạo vé và không xuất hiện trong “Vé của tôi”.

## Hủy đơn đang giữ ghế

Khách hàng có thể hủy đơn khi đơn còn ở trạng thái `PENDING`. Khi hủy thành công:

- Đơn chuyển sang `CANCELLED`.
- Ghế được giải phóng về `AVAILABLE`.
- Liên kết thanh toán của đơn bị xóa.

Đơn đã `PAID`, `CANCELLED`, `EXPIRED` hoặc `REFUNDED` không thể hủy lại bằng chức năng hủy đơn chờ thanh toán.

## Khi hai khách cùng chọn một ghế

Hai người có thể nhìn thấy cùng một ghế trống nếu họ mở sơ đồ gần như cùng lúc. Khi cả hai gửi yêu cầu giữ ghế, backend khóa dữ liệu ghế trong transaction và chỉ một yêu cầu được tạo đơn thành công. Yêu cầu còn lại nhận thông báo ghế đã được giữ hoặc đã bán.

Vì vậy, việc ghế có màu trống trên màn hình không bảo đảm tuyệt đối rằng ghế vẫn còn đến lúc bấm giữ. Kết quả từ backend là kết quả cuối cùng.

## Cách xử lý lỗi thường gặp

- **Ghế đã được bán:** chọn ghế khác.
- **Ghế đang được giữ:** đợi ghế được giải phóng hoặc chọn ghế khác.
- **Sự kiện chưa mở bán:** chờ Admin duyệt và công khai sự kiện.
- **Sự kiện đã bắt đầu:** không thể tạo đơn mới.
- **Chọn quá 5 ghế:** giảm số ghế trong đơn.
- **Đơn đã hết hạn:** quay lại sự kiện và tạo đơn mới.

