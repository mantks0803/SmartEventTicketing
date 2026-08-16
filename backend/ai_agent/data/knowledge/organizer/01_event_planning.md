# Quy trình lập kế hoạch và tạo một sự kiện

> Đối tượng: Organizer  
> Danh mục kiến thức: PLANNING  
> Nguồn: Quy trình nghiệp vụ SmartEventTicketing và hướng dẫn nội bộ phục vụ đồ án  
> Cập nhật: 17/08/2026

## Mục đích

Tài liệu này hướng dẫn Ban tổ chức chuyển một ý tưởng thành kế hoạch có thể thực hiện và tạo sự kiện đúng cấu trúc trên SmartEventTicketing.

## Thông tin cần xác định trước

Trước khi lập ngân sách hoặc chọn nhà cung cấp, Ban tổ chức cần trả lời:

1. Mục tiêu của sự kiện là bán vé, xây dựng thương hiệu, đào tạo hay kết nối cộng đồng?
2. Loại sự kiện là âm nhạc, workshop, giải trí hay thể thao?
3. Nhóm khách tham dự chính là ai?
4. Số khách tối thiểu, dự kiến và tối đa là bao nhiêu?
5. Thời gian và khu vực tổ chức mong muốn?
6. Ngân sách tối đa có thể chi?
7. Sự kiện có bán vé không và dự kiến bán bao nhiêu phần trăm sức chứa?
8. Những dịch vụ bắt buộc gồm địa điểm, ăn uống, kỹ thuật, trang trí, nhân sự hay truyền thông?

Nếu thiếu các thông tin quan trọng, chatbot nên hỏi lại thay vì tự giả định toàn bộ kế hoạch.

## Các giai đoạn lập kế hoạch

### 1. Xác định mục tiêu và phạm vi

Mục tiêu phải có thể kiểm tra được, ví dụ số người tham dự, số vé bán, mức ngân sách hoặc mức độ hài lòng. Phạm vi cần ghi rõ phần nào do Ban tổ chức tự thực hiện và phần nào thuê nhà cung cấp.

### 2. Xác định khách tham dự

Thông tin về độ tuổi, sở thích, khu vực, khả năng chi trả và thời gian thuận tiện ảnh hưởng trực tiếp đến nội dung, địa điểm, kênh truyền thông và giá vé.

### 3. Chọn thời gian và địa điểm

Thời gian phải đủ xa để chuẩn bị, truyền thông và bán vé. Địa điểm phải đáp ứng sức chứa, giao thông, khu vực check-in, nguồn điện, thiết bị, lối thoát và điều kiện thời tiết.

### 4. Lập ngân sách

Ngân sách nên chia theo nhóm chi phí, dùng khoảng thấp nhất và cao nhất, sau đó cộng khoản dự phòng. Không dùng một con số do LLM tự đoán làm báo giá chính thức.

### 5. Thiết kế vé và ghế

Ban tổ chức xác định các loại vé, giá, số hàng, số ghế mỗi hàng và tiền tố hàng. Mỗi loại vé nên có quyền lợi rõ ràng để khách hiểu sự khác biệt.

### 6. Lập timeline và phân công

Mỗi công việc phải có người phụ trách, hạn hoàn thành và kết quả cần bàn giao. Các mốc quan trọng gồm chốt địa điểm, mở bán vé, chạy truyền thông, kiểm tra kỹ thuật và tổng duyệt.

### 7. Vận hành và tổng kết

Ngày diễn ra cần có quy trình check-in, xử lý sự cố và liên lạc nội bộ. Sau sự kiện, Ban tổ chức đối chiếu số vé, check-in, doanh thu và chi phí để đánh giá kết quả.

## Tạo sự kiện trên SmartEventTicketing

Ban tổ chức đăng nhập bằng tài khoản Organizer và nhập:

- Tên sự kiện.
- Ảnh đại diện.
- Nội dung mô tả.
- Địa điểm.
- Thời gian bắt đầu.
- Danh mục.
- Một hoặc nhiều loại vé.
- Giá, số hàng, số ghế mỗi hàng và tiền tố hàng của từng loại vé.

Ảnh chấp nhận định dạng JPG, JPEG, PNG hoặc WEBP và có dung lượng tối đa 5 MB. Ảnh được tải lên Cloudinary trước, sau đó URL được lưu vào Event.

## Quy tắc tạo loại vé và ghế

- Mỗi loại vé phải có tên riêng, không trùng tên trong cùng sự kiện.
- Giá vé tối thiểu là 1.000 đồng.
- Mỗi loại vé có từ 1 đến 50 hàng.
- Mỗi hàng có từ 1 đến 100 ghế.
- Tiền tố hàng chỉ gồm chữ cái và chữ số, tối đa 10 ký tự.
- Tên hàng tạo ra giữa các loại vé không được trùng nhau.
- Tổng số ghế của một sự kiện không vượt quá 5.000.

Ví dụ, loại vé VIP có `row_prefix = VIP`, 2 hàng và 5 ghế mỗi hàng sẽ tạo các hàng `VIP1`, `VIP2` với tổng cộng 10 ghế.

Event, TicketType và Seat được tạo trong một transaction. Nếu một phần bị lỗi, quá trình tạo không để lại một sự kiện dở dang.

## Quy trình duyệt sự kiện

Sự kiện Organizer tạo luôn bắt đầu ở trạng thái `PENDING`. Organizer không thể tự gửi trạng thái `PUBLISHED` từ frontend.

Luồng xử lý:

1. Organizer gửi sự kiện.
2. Backend tạo Event, TicketType và Seat ở trạng thái chờ duyệt.
3. Admin xem thông tin sự kiện.
4. Nếu hợp lệ và chưa qua giờ bắt đầu, Admin chuyển sự kiện sang `PUBLISHED`.
5. Nếu từ chối, hệ thống hiện chuyển sự kiện sang `CANCELLED`.
6. Chỉ sự kiện `PUBLISHED` mới xuất hiện công khai và cho phép giữ ghế.

Ban tổ chức nên gửi sự kiện đủ sớm để Admin có thời gian kiểm tra trước ngày mở bán.

## Theo dõi sau khi mở bán

Organizer có thể theo dõi:

- Tổng số ghế, ghế trống, ghế đang giữ và ghế đã bán.
- Số vé đã check-in.
- Doanh thu chỉ từ Order `PAID`.
- Doanh thu theo loại vé.
- Danh sách giao dịch của sự kiện.

Các đơn `PENDING`, `CANCELLED`, `EXPIRED` và `REFUNDED` không được tính vào doanh thu đã thanh toán.

## Kết quả chatbot nên trả về

Khi tư vấn lập kế hoạch, chatbot nên trình bày:

- Tóm tắt yêu cầu và các giả định.
- Checklist công việc.
- Timeline đề xuất.
- Khoảng chi phí tham khảo nếu có đủ dữ liệu.
- Rủi ro chính và phương án dự phòng.
- Thông tin còn thiếu cần Ban tổ chức xác nhận.

Chatbot không được tự tạo Event, tự duyệt sự kiện, tự ký hợp đồng hoặc cam kết doanh thu.

