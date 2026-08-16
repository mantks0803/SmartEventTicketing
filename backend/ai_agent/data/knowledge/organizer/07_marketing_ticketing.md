# Marketing, mở bán và thiết kế giá vé

> Đối tượng: Organizer  
> Danh mục kiến thức: PLANNING  
> Nguồn: Quy trình SmartEventTicketing và hướng dẫn nội bộ phục vụ đồ án  
> Cập nhật: 17/08/2026

## Mục đích

Tài liệu này hướng dẫn xác định khách hàng mục tiêu, xây dựng kế hoạch truyền thông và cấu trúc các loại vé phù hợp với sức chứa và ngân sách.

## Xác định khách hàng mục tiêu

Ban tổ chức nên mô tả:

- Nhóm tuổi và sở thích.
- Khu vực sinh sống hoặc làm việc.
- Lý do họ muốn tham dự.
- Khả năng chi trả.
- Kênh thông tin họ thường sử dụng.
- Thời điểm thuận tiện để mua vé và tham dự.

Không cần thu thập dữ liệu cá nhân nhạy cảm nếu không phục vụ trực tiếp cho việc tổ chức.

## Thông điệp truyền thông

Thông điệp cần trả lời ngắn gọn:

- Sự kiện là gì?
- Dành cho ai?
- Khách nhận được trải nghiệm hoặc giá trị gì?
- Diễn ra khi nào và ở đâu?
- Giá vé và cách mua?

Tên, thời gian, địa điểm và quyền lợi vé trong nội dung truyền thông phải thống nhất với Event trên SmartEventTicketing.

## Các giai đoạn truyền thông

### Giai đoạn giới thiệu

Công bố chủ đề, hình ảnh chính và thời gian dự kiến. Mục tiêu là tạo nhận biết, chưa cần đưa quá nhiều thông tin chưa chốt.

### Giai đoạn mở bán

Công bố trang sự kiện, các loại vé, giá, số lượng và hướng dẫn mua. Sự kiện phải được Admin duyệt thành `PUBLISHED` trước khi khách có thể giữ ghế.

### Giai đoạn duy trì

Giới thiệu nội dung, diễn giả, nghệ sĩ, quyền lợi và các mốc chuẩn bị. Theo dõi tốc độ bán vé để điều chỉnh nội dung truyền thông.

### Giai đoạn gần ngày diễn ra

Nhắc thời gian, địa điểm, cách di chuyển, quy định tham dự và chuẩn bị QR. Không tiếp tục quảng bá như còn nhiều vé nếu dữ liệu ghế không còn phù hợp.

### Sau sự kiện

Đăng nội dung tổng kết, cảm ơn và thu thập phản hồi theo phạm vi đã thông báo với người tham dự.

## Thiết kế loại vé

Mỗi loại vé cần có:

- Tên dễ hiểu.
- Giá cụ thể.
- Khu vực ghế.
- Quyền lợi khác biệt nếu có.
- Số hàng và số ghế phù hợp địa điểm.

Ví dụ hai mức đơn giản:

- Phổ thông: quyền tham dự cơ bản.
- VIP: vị trí tốt hơn hoặc quyền lợi bổ sung đã được Ban tổ chức cam kết.

Không nên tạo quá nhiều hạng vé nếu sự khác biệt không rõ, vì làm khách khó lựa chọn và tăng độ phức tạp khi vận hành.

## Quy tắc trên hệ thống

- Tên loại vé trong một sự kiện không được trùng.
- Giá tối thiểu là 1.000 đồng.
- Tiền tố hàng của các loại vé phải tạo ra tên hàng không trùng nhau.
- Tổng ghế của sự kiện không vượt quá 5.000.
- Mỗi Customer chọn tối đa 5 ghế trong một đơn.
- Giá và ghế chỉ mở bán sau khi Event là `PUBLISHED` và chưa bắt đầu.

Hệ thống hiện chưa có mã giảm giá hoặc chương trình khuyến mãi riêng. Chatbot không nên tư vấn như thể chức năng coupon đã tồn tại.

## Gợi ý giá vé

Giá vé nên dựa trên:

1. Tổng chi phí dự kiến sau dự phòng.
2. Số vé thực tế dự kiến bán, không phải toàn bộ sức chứa.
3. Số vé mời hoặc ghế không bán.
4. Quyền lợi của từng hạng vé.
5. Giá các sự kiện cùng danh mục đang có trên hệ thống.

Phép tính hòa vốn và đối chiếu giá nằm trong tool dự toán, không để LLM tự cộng.

Dữ liệu từ các sự kiện seed chỉ là tham khảo nội bộ của hệ thống, không được gọi là khảo sát thị trường chính thức.

## Theo dõi hiệu quả

Organizer có thể dùng báo cáo theo sự kiện để xem:

- Ghế đã bán và ghế còn trống.
- Số đơn `PAID`.
- Doanh thu từ đơn `PAID`.
- Doanh thu theo loại vé.
- Số vé đã check-in.

Các chỉ số nên theo dõi thêm trong kế hoạch truyền thông:

- Lượng truy cập trang sự kiện nếu hệ thống đo được.
- Số vé bán theo từng giai đoạn.
- Chi phí truyền thông.
- Tỷ lệ doanh thu trên chi phí truyền thông.

Không được bịa chỉ số nếu project chưa thu thập dữ liệu đó.

## Điều chỉnh khi bán vé chậm

Trước khi thay đổi chiến dịch, cần kiểm tra:

- Thông tin sự kiện đã rõ chưa.
- Giá vé có phù hợp nhóm khách không.
- Ngày giờ và địa điểm có thuận tiện không.
- Nội dung truyền thông có đến đúng nhóm khách không.
- Còn đủ thời gian để thay đổi không.

Project hiện chưa có chức năng sửa hoặc giảm giá hàng loạt cho vé đã phát hành. Mọi thay đổi phải tránh làm sai quyền lợi của khách đã thanh toán.

## Nguyên tắc an toàn

- Không cam kết chắc chắn bán hết vé.
- Không dùng số ghế đang `LOCKED` như vé đã bán.
- Chỉ Order `PAID` được tính là doanh thu.
- Không quảng cáo quyền lợi chưa được chuẩn bị.
- Không hiển thị dữ liệu cá nhân của người mua trong nội dung marketing.

