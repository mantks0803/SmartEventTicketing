# Tìm kiếm và lựa chọn sự kiện trên SmartEventTicketing

> Đối tượng: Customer  
> Danh mục kiến thức: GENERAL  
> Nguồn: Quy trình đang hoạt động của SmartEventTicketing  
> Cập nhật: 19/08/2026

## Mục đích

Tài liệu này hướng dẫn khách hàng tìm sự kiện, đọc thông tin sự kiện và lựa chọn chương trình phù hợp trước khi mua vé.

## Ai có thể xem sự kiện?

Khách chưa đăng nhập vẫn có thể xem danh sách và chi tiết các sự kiện đang được công khai. Khách hàng phải đăng nhập bằng tài khoản Customer trước khi giữ ghế và thanh toán.

Hệ thống công khai những sự kiện có trạng thái `PUBLISHED`. Sự kiện đang chờ duyệt (`PENDING`) hoặc đã bị hủy (`CANCELLED`) không xuất hiện trong danh sách công khai và không thể mở trang chi tiết bằng API công khai.

## Danh mục sự kiện

SmartEventTicketing hiện hỗ trợ bốn danh mục:

- `MUSIC`: âm nhạc, concert và các chương trình biểu diễn âm nhạc.
- `WORKSHOP`: workshop, hội thảo và chương trình chia sẻ kiến thức.
- `ENTERTAINMENT`: giải trí, triển lãm, hài kịch, lễ hội và chương trình biểu diễn.
- `SPORTS`: thể thao, giải đấu và hoạt động vận động cộng đồng.

Khách hàng có thể chọn một danh mục để thu hẹp danh sách hoặc chọn tất cả để xem toàn bộ sự kiện đang công khai.

## Tìm kiếm sự kiện

Chức năng tìm kiếm hiện tại đối chiếu từ khóa với:

- Tên sự kiện.
- Địa điểm tổ chức.

Tìm kiếm không phân biệt chữ hoa và chữ thường. Ví dụ:

- Nhập `Workshop` để tìm các sự kiện có từ Workshop trong tên.
- Nhập `Quận 1` để tìm sự kiện có địa điểm tại Quận 1.
- Nhập một phần tên như `Acoustic` để tìm sự kiện có tên gần khớp.

Nếu tên nghệ sĩ hoặc diễn giả được ghi trong tên sự kiện thì có thể tìm bằng tên đó. Hệ thống hiện chưa có trường nghệ sĩ hoặc diễn giả riêng để tìm kiếm độc lập.

## Phân trang và sự kiện nổi bật

Danh sách sự kiện được phân trang, mặc định 12 sự kiện trên một trang. API có thể nhận `page_size` và giới hạn tối đa 100 sự kiện trên một trang. Giao diện hiện dùng phân trang để người dùng chuyển sang các kết quả tiếp theo.

Khu vực sự kiện nổi bật ưu tiên các sự kiện `PUBLISHED` chưa diễn ra và sắp xếp theo thời gian bắt đầu gần nhất. Đây là danh sách gợi ý nhanh, không phải cam kết rằng sự kiện còn đủ số ghế theo yêu cầu của khách.

## Thông tin cần xem trước khi mua vé

Trang chi tiết sự kiện cung cấp:

- Tên và hình ảnh sự kiện.
- Nội dung giới thiệu.
- Danh mục.
- Thời gian bắt đầu.
- Địa điểm.
- Tên Ban tổ chức.
- Các loại vé.
- Giá và số lượng ghế thiết kế cho từng loại vé.

Số lượng của loại vé thể hiện sức chứa được cấu hình. Tình trạng ghế có thể thay đổi liên tục khi nhiều khách hàng cùng đặt vé. Muốn biết trạng thái mới nhất, khách hàng cần mở sơ đồ ghế.

## Cách lựa chọn sự kiện phù hợp

Khách hàng nên xác định:

1. Loại chương trình muốn tham dự.
2. Khu vực hoặc địa điểm thuận tiện.
3. Ngày giờ có thể tham dự.
4. Ngân sách tối đa cho một vé.
5. Số lượng người đi cùng.

Chatbot có thể dùng các tiêu chí này để tìm tối đa 5 sự kiện trong database. Kết quả chỉ gồm sự kiện `PUBLISHED`, chưa diễn ra và có ít nhất một ghế `AVAILABLE` tại thời điểm truy vấn.

Khi khách nhập ngân sách, tool so sánh ngân sách với mức giá thấp nhất được cấu hình trong các `TicketType` của sự kiện. Điều này không bảo đảm ghế còn trống thuộc đúng loại vé có giá thấp nhất. Khách cần mở sơ đồ ghế để kiểm tra loại vé và ghế còn trống trước khi đặt.

## Khi không tìm thấy kết quả

Khách hàng có thể:

- Rút ngắn từ khóa.
- Tìm theo địa điểm rộng hơn, ví dụ `TP.HCM` thay cho tên một quận.
- Chọn tất cả danh mục.
- Thử ngân sách hoặc thời gian linh hoạt hơn khi hỏi chatbot.

Nếu không có sự kiện phù hợp, chatbot phải thông báo chưa tìm thấy dữ liệu thay vì tự tạo ra một sự kiện không tồn tại.

## Lưu ý về dữ liệu tức thời

Tên, giá vé và trạng thái ghế phải được đọc từ database khi khách hỏi. Không sử dụng tài liệu RAG này để khẳng định một sự kiện cụ thể còn ghế. Khi dữ liệu trên màn hình và dữ liệu giữ ghế khác nhau, kết quả xác nhận từ backend là kết quả cuối cùng.
