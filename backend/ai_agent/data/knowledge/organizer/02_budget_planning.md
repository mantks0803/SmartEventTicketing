# Lập ngân sách, tính hòa vốn và gợi ý giá vé

> Đối tượng: Organizer  
> Danh mục kiến thức: PLANNING  
> Nguồn: Phương pháp dự toán nội bộ phục vụ đồ án SmartEventTicketing  
> Cập nhật: 19/08/2026

## Mục đích

Tài liệu này quy định cách thu thập đầu vào, chia nhóm chi phí, tính khoảng ngân sách và gợi ý giá vé. Phép tính phải do Python thực hiện từ dữ liệu có cấu trúc; LLM chỉ giải thích kết quả.

## Đầu vào cần thiết

- Loại sự kiện.
- Khu vực tổ chức.
- Số khách dự kiến.
- Thời lượng tổ chức nếu dịch vụ tính theo giờ.
- Các nhóm dịch vụ cần dùng.
- Mức chất lượng: tiết kiệm, tiêu chuẩn hoặc nâng cao.

## Các nhóm chi phí chính

### Địa điểm

Chi phí thuê không gian, thời gian chuẩn bị, thời gian tổ chức và các khoản phụ thu được nhà cung cấp báo riêng.

### Ăn uống

Thường được tính theo số người. Cần xác định loại suất ăn, nước uống, số khách và tỷ lệ dự phòng.

### Âm thanh, ánh sáng và sân khấu

Phụ thuộc quy mô không gian, loại chương trình, thời lượng, thiết bị và số kỹ thuật viên.

### Trang trí

Gồm backdrop, bảng hướng dẫn, khu check-in, sân khấu, khu chụp ảnh và vật liệu nhận diện.

### Nhân sự

Gồm điều phối, check-in, kỹ thuật, bảo vệ, hỗ trợ khách, y tế hoặc các vai trò khác tùy sự kiện.

### Truyền thông và media

Gồm thiết kế nội dung, quảng cáo, quay phim, chụp ảnh hoặc livestream nếu có.

## Dữ liệu giá sử dụng

Giá dịch vụ phải đọc từ `EventService`, gồm giá thấp nhất, giá cao nhất, đơn vị tính, khu vực, sức chứa và ngày kiểm chứng.

Các đơn vị có thể gồm:

- `PACKAGE`: tính theo gói.
- `PER_PERSON`: tính theo số người.
- `PER_HOUR`: tính theo thời lượng.

Nếu một nhóm dịch vụ không có dữ liệu phù hợp, hệ thống phải báo thiếu dữ liệu thay vì tự bịa giá.

## Công thức dự toán

Với mỗi dịch vụ:

```text
Chi phí dịch vụ = đơn giá × số lượng áp dụng
```

Sau đó, bản demo tính:

```text
Chi phí thấp nhất = tổng min_price × số lượng của từng dịch vụ

Chi phí cao nhất = tổng max_price × số lượng của từng dịch vụ

Chi phí dự phòng = chi phí cao nhất × 10%

Tổng chi phí dự kiến = chi phí cao nhất + chi phí dự phòng
```

MVP sử dụng tỷ lệ dự phòng mặc định 10%. Đây là giả định phục vụ dự toán, không phải quy định bắt buộc cho mọi sự kiện.

Response trả cả chi phí thấp nhất, chi phí cao nhất, dự phòng và tổng dự kiến.

## Tính giá vé hòa vốn

Trong phiên bản demo hiện tại, `guest_count` đồng thời được dùng làm số vé dự kiến bán. Nghĩa là công thức đang giả định bán đủ số vé tương ứng số khách đã nhập.

```text
Giá vé hòa vốn = tổng chi phí dự kiến ÷ số khách dự kiến
```

Ví dụ minh họa:

- Sức chứa: 500.
- Số khách và số vé dự kiến bán: 500.
- Tổng chi phí dự kiến sau dự phòng: 250 triệu đồng.

Kết quả:

```text
250.000.000 ÷ 500 = 500.000 đồng/vé
```

500.000 đồng là mức hòa vốn theo giả định bán đủ 500 vé, chưa phải mức giá bảo đảm bán được vé hoặc có lợi nhuận.

## Đối chiếu giá vé trên hệ thống

Backend có thể query `TicketType.price` của các Event:

- Cùng danh mục.
- Đang `PUBLISHED`.
- Có dữ liệu vé hợp lệ.

Backend hiện tính trung bình cộng `TicketType.price` của tất cả loại vé phù hợp. Kết quả được trả trong field `market_reference_avg_price`.

Dữ liệu seed là dữ liệu demo, vì vậy chatbot phải nói “giá các sự kiện tương tự trên hệ thống”, không gọi đây là giá thị trường thực tế.

Nếu không có sự kiện tương tự, chatbot chỉ đưa giá theo công thức hòa vốn.

## Gợi ý nhiều hạng vé

Ban tổ chức có thể tham khảo hai hạng:

- Vé phổ thông gần mức hòa vốn mục tiêu.
- Vé VIP cao hơn vé phổ thông dựa trên quyền lợi và vị trí ghế.

Không nên áp dụng một tỷ lệ VIP cố định cho mọi sự kiện. Nếu dùng tỷ lệ minh họa, chatbot phải ghi đây là giả định và mô tả quyền lợi đi kèm.

Tool hiện chưa tự chia tỷ lệ ghế hoặc đề xuất giá riêng cho từng hạng vé. Nếu cần nhiều hạng, Ban tổ chức phải tự xác định số lượng và quyền lợi trước khi tạo sự kiện.

## Câu trả lời mẫu

Một câu trả lời tốt gồm:

1. Các giả định đầu vào.
2. Bảng chi phí thấp–cao theo nhóm.
3. Chi phí dự phòng.
4. Tổng dự kiến.
5. Giả định số vé bán bằng số khách đã nhập.
6. Giá vé hòa vốn.
7. Giá vé trung bình của các sự kiện cùng danh mục trên hệ thống nếu có.
8. Cảnh báo đây là dữ liệu demo và dự toán tham khảo.

## Giới hạn

- Không xem dữ liệu demo là báo giá nhà cung cấp thật.
- Giá hòa vốn hiện giả định bán đủ số vé bằng `guest_count`.
- Giá tham khảo chỉ là trung bình dữ liệu nội bộ, không phải giá thị trường bên ngoài.
- Không để LLM tự cộng tiền hoặc tự sửa kết quả Python.
- Không tự thêm phí nền tảng, thuế hoặc khoản pháp lý nếu database chưa có dữ liệu.
- Không cam kết lợi nhuận.
