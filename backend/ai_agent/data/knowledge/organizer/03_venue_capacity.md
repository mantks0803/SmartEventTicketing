# Chọn địa điểm và xác định sức chứa

> Đối tượng: Organizer  
> Danh mục kiến thức: PLANNING  
> Nguồn: Hướng dẫn nội bộ phục vụ đồ án SmartEventTicketing  
> Cập nhật: 17/08/2026

## Mục đích

Tài liệu này giúp Ban tổ chức chọn địa điểm phù hợp với loại sự kiện, số khách, cách bố trí ghế và yêu cầu vận hành.

## Thông tin cần thu thập

- Loại sự kiện và nội dung chính.
- Khu vực mong muốn.
- Số khách tối thiểu, dự kiến và tối đa.
- Hình thức ngồi, đứng hoặc kết hợp.
- Số loại vé và khu vực vé.
- Nhu cầu sân khấu, màn hình, gian hàng hoặc khu trải nghiệm.
- Nhu cầu ăn uống.
- Số lượng nhân sự và thiết bị.
- Yêu cầu tiếp cận cho người khuyết tật.
- Phương án trong nhà, ngoài trời và thời tiết dự phòng.

## Sức chứa không chỉ là số người tham dự

Sức chứa công bố của địa điểm không nên được dùng toàn bộ làm số vé bán. Cần chừa diện tích cho:

- Sân khấu và thiết bị kỹ thuật.
- Lối đi và lối thoát.
- Khu check-in.
- Bàn ghế, gian hàng hoặc khu ăn uống.
- Nhân sự vận hành.
- Khu vực dự phòng và xử lý sự cố.

Sức chứa bán vé phải lấy theo phương án bố trí đã được địa điểm chấp thuận, không tự suy ra chỉ từ diện tích.

## Gợi ý theo loại sự kiện

### Workshop và hội thảo

Ưu tiên không gian yên tĩnh, màn hình dễ nhìn, âm thanh rõ, bàn ghế phù hợp và khu vực giải lao. Cần kiểm tra Wi-Fi nếu chương trình có thực hành trực tuyến.

### Âm nhạc và biểu diễn

Ưu tiên khả năng cách âm, sân khấu, tải điện, khu điều khiển kỹ thuật, tầm nhìn và phương án kiểm soát đám đông.

### Thể thao

Cần không gian cho khu thi đấu, khán giả, vận động viên, y tế, thiết bị và phân luồng vào ra.

### Giải trí và triển lãm

Cần xem xét luồng di chuyển giữa các khu vực, điểm chụp ảnh, gian hàng, kho thiết bị và thời gian lắp đặt.

## Tiêu chí đánh giá địa điểm

### Vị trí và di chuyển

- Khoảng cách với nhóm khách chính.
- Khả năng tiếp cận bằng phương tiện công cộng.
- Bãi đỗ xe hoặc điểm đón trả khách.
- Biển chỉ dẫn và khả năng tìm kiếm địa điểm.

### Cơ sở vật chất

- Nguồn điện và phương án điện dự phòng.
- Hệ thống âm thanh, ánh sáng có sẵn.
- Internet và Wi-Fi.
- Nhà vệ sinh.
- Điều hòa hoặc thông gió.
- Khu chuẩn bị, kho và phòng chờ.

### Vận hành và an toàn

- Lối vào, lối ra và lối thoát.
- Khả năng phân luồng khách.
- Quy định tải trọng, tiếng ồn và thời gian hoạt động.
- Phương án y tế, phòng cháy và xử lý khẩn cấp của địa điểm.

Ban tổ chức phải xác minh trực tiếp các yêu cầu pháp lý và an toàn với địa điểm và cơ quan có thẩm quyền. Chatbot chỉ cung cấp checklist, không thay thế việc kiểm tra chuyên môn.

## Khảo sát địa điểm

Khi khảo sát, nên ghi lại:

1. Kích thước và sơ đồ không gian.
2. Vị trí sân khấu, check-in và kỹ thuật.
3. Số và vị trí ổ điện.
4. Lối vận chuyển thiết bị.
5. Khu vực dành cho nhà cung cấp.
6. Điểm có nguy cơ ùn tắc.
7. Thời gian được phép lắp đặt và tháo dỡ.
8. Các khoản phụ thu ngoài giá thuê.

Nên chụp ảnh và xác nhận bằng văn bản những hạng mục địa điểm cung cấp.

## Thể hiện sức chứa trên SmartEventTicketing

Khi tạo sự kiện, tổng số ghế được tính từ:

```text
Tổng ghế = tổng của (số hàng × số ghế mỗi hàng) ở từng loại vé
```

Hệ thống hiện giới hạn tối đa 5.000 ghế cho một sự kiện. Mỗi hàng từ 1 đến 100 ghế và mỗi loại vé từ 1 đến 50 hàng.

Sơ đồ hiện tại nhóm ghế theo loại vé và hàng, không lưu tọa độ không gian thực của địa điểm. Ban tổ chức cần thiết kế tiền tố hàng rõ ràng như `VIP`, `A`, `B` để khách dễ nhận biết.

Không nên tạo số ghế trên hệ thống lớn hơn số ghế thực tế đã được địa điểm xác nhận.

## Quyết định cuối cùng

Một địa điểm phù hợp phải đồng thời đáp ứng:

- Sức chứa và bố trí.
- Ngân sách.
- Thời gian còn trống.
- Yêu cầu kỹ thuật.
- Khả năng tiếp cận.
- Điều kiện vận hành và an toàn.

Nếu chưa có đủ dữ liệu, chatbot nên đưa danh sách câu hỏi cần xác minh thay vì khẳng định một địa điểm chắc chắn phù hợp.

