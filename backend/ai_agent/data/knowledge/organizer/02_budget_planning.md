# Lập ngân sách, tính hòa vốn và gợi ý giá vé

> Đối tượng: Organizer  
> Danh mục kiến thức: PLANNING  
> Nguồn: Phương pháp dự toán nội bộ phục vụ đồ án SmartEventTicketing  
> Cập nhật: 17/08/2026

## Mục đích

Tài liệu này quy định cách thu thập đầu vào, chia nhóm chi phí, tính khoảng ngân sách và gợi ý giá vé. Phép tính phải do Python thực hiện từ dữ liệu có cấu trúc; LLM chỉ giải thích kết quả.

## Đầu vào cần thiết

- Loại sự kiện.
- Khu vực tổ chức.
- Sức chứa tối đa.
- Số khách dự kiến.
- Tỷ lệ vé dự kiến bán.
- Ngày và thời lượng tổ chức.
- Các nhóm dịch vụ cần dùng.
- Mức chất lượng: tiết kiệm, tiêu chuẩn hoặc nâng cao.
- Ngân sách tối đa nếu đã có.
- Số loại vé dự kiến.

Nếu Ban tổ chức chưa biết tỷ lệ bán vé, hệ thống có thể dùng giả định demo 80% nhưng phải công khai giả định này trong câu trả lời.

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

Sau đó:

```text
Tổng chi phí cơ bản = tổng các nhóm chi phí

Chi phí dự phòng = tổng chi phí cơ bản × tỷ lệ dự phòng

Tổng chi phí dự kiến = tổng chi phí cơ bản + chi phí dự phòng
```

MVP sử dụng tỷ lệ dự phòng mặc định 10%. Đây là giả định phục vụ dự toán, không phải quy định bắt buộc cho mọi sự kiện.

Kết quả phải trả theo khoảng `min` và `max`, không chỉ trả một con số duy nhất.

## Tính số vé dự kiến bán

Không nên giả định bán hết 100% sức chứa.

```text
Số vé dự kiến bán = sức chứa × tỷ lệ bán vé dự kiến
```

Ví dụ, sự kiện có 500 ghế và tỷ lệ bán dự kiến 80%:

```text
500 × 80% = 400 vé dự kiến bán
```

Nếu có vé mời hoặc vé miễn phí, cần trừ chúng khỏi số vé có thể tạo doanh thu trước khi tính hòa vốn.

## Tính giá vé hòa vốn

```text
Giá hòa vốn thấp = tổng chi phí dự kiến thấp ÷ số vé dự kiến bán

Giá hòa vốn cao = tổng chi phí dự kiến cao ÷ số vé dự kiến bán
```

Ví dụ minh họa:

- Sức chứa: 500.
- Tỷ lệ bán dự kiến: 80%.
- Số vé dự kiến bán: 400.
- Chi phí sau dự phòng: 200–300 triệu đồng.

Kết quả:

```text
200.000.000 ÷ 400 = 500.000 đồng/vé
300.000.000 ÷ 400 = 750.000 đồng/vé
```

Khoảng 500.000–750.000 đồng là mức hòa vốn theo giả định, chưa phải mức giá bảo đảm bán được vé.

## Đối chiếu giá vé trên hệ thống

Backend có thể query `TicketType.price` của các Event:

- Cùng danh mục.
- Đang `PUBLISHED`.
- Có dữ liệu vé hợp lệ.

Kết quả tham khảo nên gồm giá thấp nhất, trung vị, cao nhất và số mẫu. Giá trung vị hữu ích hơn giá trung bình khi có một số loại vé quá cao hoặc quá thấp.

Dữ liệu seed là dữ liệu demo, vì vậy chatbot phải nói “giá các sự kiện tương tự trên hệ thống”, không gọi đây là giá thị trường thực tế.

Nếu không có sự kiện tương tự, chatbot chỉ đưa giá theo công thức hòa vốn.

## Gợi ý nhiều hạng vé

MVP có thể đề xuất hai hạng:

- Vé phổ thông gần mức hòa vốn mục tiêu.
- Vé VIP cao hơn vé phổ thông dựa trên quyền lợi và vị trí ghế.

Không nên áp dụng một tỷ lệ VIP cố định cho mọi sự kiện. Nếu dùng tỷ lệ minh họa, chatbot phải ghi đây là giả định và mô tả quyền lợi đi kèm.

Tổng doanh thu dự kiến cần tính theo số vé dự kiến bán của từng hạng, không lấy toàn bộ sức chứa nhân với giá cao nhất.

## Câu trả lời mẫu

Một câu trả lời tốt gồm:

1. Các giả định đầu vào.
2. Bảng chi phí thấp–cao theo nhóm.
3. Chi phí dự phòng.
4. Tổng dự kiến.
5. Số vé dự kiến bán.
6. Khoảng giá hòa vốn.
7. Giá các sự kiện tương tự trên hệ thống nếu có.
8. Cảnh báo đây là dự toán tham khảo.

## Giới hạn

- Không xem dữ liệu demo là báo giá nhà cung cấp thật.
- Không cam kết bán được tỷ lệ vé đã giả định.
- Không để LLM tự cộng tiền hoặc tự sửa kết quả Python.
- Không tự thêm phí nền tảng, thuế hoặc khoản pháp lý nếu database chưa có dữ liệu.
- Không cam kết lợi nhuận.

