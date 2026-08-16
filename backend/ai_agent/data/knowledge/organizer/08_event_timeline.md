# Timeline chuẩn bị và vận hành sự kiện

> Đối tượng: Organizer  
> Danh mục kiến thức: PLANNING  
> Nguồn: Hướng dẫn nội bộ phục vụ đồ án SmartEventTicketing  
> Cập nhật: 17/08/2026

## Mục đích

Tài liệu này cung cấp timeline tham khảo cho một sự kiện quy mô vừa. Ban tổ chức có thể rút gọn hoặc kéo dài theo quy mô, nhưng phải giữ đủ thời gian cho duyệt sự kiện, bán vé, kỹ thuật và tổng duyệt.

## Trước 8 tuần

- Xác định mục tiêu, loại sự kiện và khách tham dự.
- Dự kiến số khách, ngân sách và nguồn doanh thu.
- Lập danh sách địa điểm có thể sử dụng.
- Xác định người ra quyết định và nhóm phụ trách.
- Ghi nhận các yêu cầu pháp lý hoặc chuyên môn cần xác minh.

Kết quả cần có: bản mô tả sự kiện, phạm vi, ngân sách sơ bộ và người phụ trách chính.

## Trước 6–7 tuần

- Khảo sát và chốt địa điểm.
- Xác nhận ngày giờ và thời gian lắp đặt.
- Thu thập báo giá dịch vụ chính.
- Chốt hình thức sân khấu và bố trí khách.
- Lập ngân sách thấp–cao và khoản dự phòng.

Kết quả cần có: địa điểm dự kiến, phương án bố trí và ngân sách đã được duyệt nội bộ.

## Trước 4–5 tuần

- Chốt nhà cung cấp quan trọng.
- Xác định loại vé, giá, số hàng và số ghế.
- Chuẩn bị hình ảnh, mô tả, địa điểm và thời gian.
- Tạo sự kiện trên SmartEventTicketing.
- Gửi sự kiện ở trạng thái `PENDING` để Admin duyệt.
- Chuẩn bị nội dung mở bán.

Không nên chờ sát ngày mới gửi duyệt. Admin không thể duyệt một sự kiện đã qua giờ bắt đầu.

## Trước 3–4 tuần

- Kiểm tra Event đã `PUBLISHED`.
- Công bố trang sự kiện và mở bán.
- Chạy kế hoạch truyền thông.
- Xác nhận diễn giả, nghệ sĩ hoặc nội dung chính.
- Lập danh sách thiết bị.
- Xây dựng sơ đồ nhân sự và luồng check-in.

Kết quả cần có: trang sự kiện hoạt động, khách có thể giữ ghế và các đầu việc chính có người phụ trách.

## Trước 2 tuần

- Theo dõi vé đã bán và ghế còn trống.
- Kiểm tra nội dung truyền thông so với Event.
- Chốt kịch bản chương trình.
- Chốt danh sách thiết bị, vật liệu và nhân sự.
- Xác nhận thời gian giao nhận, thi công và tháo dỡ.
- Chuẩn bị kế hoạch rủi ro.

Chỉ tính Order `PAID` khi đánh giá số vé đã bán và doanh thu.

## Trước 1 tuần

- Họp toàn bộ đầu mối.
- Chốt timeline theo phút cho ngày diễn ra.
- Kiểm tra danh sách liên hệ khẩn cấp.
- Xác nhận tài khoản Organizer dùng check-in.
- Chuẩn bị mạng và thiết bị dự phòng.
- Gửi hướng dẫn tham dự cho khách nếu có kênh phù hợp.

## Trước 1 ngày

- Lắp đặt theo thỏa thuận với địa điểm.
- Kiểm tra âm thanh, ánh sáng, màn hình và nguồn điện.
- Kiểm tra biển chỉ dẫn và khu check-in.
- Chạy thử QR trên dữ liệu thử nghiệm.
- Tổng duyệt chương trình.
- Xác nhận phương án khi một hạng mục quan trọng gặp lỗi.

Không sử dụng QR thật của khách để thử nếu việc đó có thể đánh dấu vé đã check-in.

## Ngày diễn ra

### Trước khi mở cửa

- Điểm danh nhân sự.
- Kiểm tra thiết bị và tài khoản.
- Kiểm tra lối đi, biển chỉ dẫn và khu chờ.
- Nhắc lại quy trình xử lý QR lỗi và sự cố thanh toán.

### Khi đón khách

- Hướng dẫn khách mở sẵn vé.
- Quét từng QR.
- Chuyển trường hợp bất thường sang quầy hỗ trợ.
- Theo dõi hàng chờ và mở thêm quầy nếu cần.

### Trong chương trình

- Bám timeline.
- Ghi nhận thay đổi và sự cố.
- Duy trì liên lạc giữa điều phối, kỹ thuật và an ninh.

### Kết thúc

- Hướng dẫn khách ra về theo luồng.
- Kiểm kê thiết bị.
- Bàn giao và tháo dỡ theo quy định địa điểm.

## Sau sự kiện

Trong 1–3 ngày:

- Kiểm tra vé bán, vé check-in và doanh thu.
- Tổng hợp chi phí thực tế.
- Ghi nhận sự cố và phản hồi.
- Đối chiếu công việc với nhà cung cấp.
- Lập báo cáo tổng kết.

Admin có thể thực hiện quyết toán mô phỏng khi Event đã bắt đầu, vẫn `PUBLISHED`, có ít nhất một Order `PAID` và chưa được quyết toán. Chức năng này chỉ đặt `is_payout_completed = true`, không chuyển tiền thật và không làm Event biến mất khỏi trang công khai.

## Lưu ý về thời gian bán vé

Backend không cho tạo đơn hoặc liên kết thanh toán mới khi thời gian bắt đầu của Event đã đến. Tuy nhiên, trạng thái `PUBLISHED` là một field riêng; việc xác nhận quyết toán không tự chuyển Event sang `CANCELLED` và không tự thay đổi nội dung sự kiện.

## Cách chatbot điều chỉnh timeline

Khi ngày tổ chức gần, chatbot nên:

- Nêu những việc không thể bỏ.
- Đánh dấu việc cần quyết định ngay.
- Giảm hạng mục tùy chọn.
- Không khẳng định một timeline quá ngắn chắc chắn khả thi.
- Yêu cầu Ban tổ chức xác nhận khả năng của địa điểm và nhà cung cấp.

