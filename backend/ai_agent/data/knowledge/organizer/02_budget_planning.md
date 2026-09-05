# Lập ngân sách, tính hòa vốn và gợi ý giá vé

> Đối tượng: Organizer  
> Danh mục kiến thức: PLANNING  
> Nguồn: Phương pháp dự toán nội bộ phục vụ đồ án SmartEventTicketing  
> Cập nhật: 05/09/2026

## Mục đích

Tài liệu này quy định cách thu thập đầu vào, chia nhóm chi phí, tính khoảng ngân sách và gợi ý giá vé. Phép tính phải do Python thực hiện từ dữ liệu có cấu trúc; LLM chỉ giải thích kết quả.

## Đầu vào cần thiết

- Loại sự kiện.
- Khu vực tổ chức.
- Số khách dự kiến.
- Thời lượng tổ chức nếu dịch vụ tính theo giờ.
- Các nhóm dịch vụ cần dùng.
- Mức chất lượng: Tiết kiệm (`ECONOMY`), Tiêu chuẩn (`STANDARD`) hoặc Cao cấp (`PREMIUM`).

Trong chatbot, chọn **Tổ chức** rồi điền loại sự kiện, số khách, chất lượng, địa điểm và tích các dịch vụ cần dùng. Có thể nhập thời lượng theo giờ. Các ô này là dữ liệu tính toán; backend chưa tự trích đầy đủ yêu cầu từ câu chat.

Ví dụ, muốn tổ chức âm nhạc 600 người không cần trang trí: chọn Âm nhạc, nhập 600 khách, chọn chất lượng, địa điểm và bỏ chọn Trang trí. Chỉ gõ “không cần trang trí” mà vẫn tích ô Trang trí thì dịch vụ đó vẫn được đưa vào phép tính.

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

Dữ liệu dịch vụ mẫu được nạp từ `event_services.json` vào database. Khi tư vấn, hệ thống đọc các bản ghi trong database, không đọc lại JSON mỗi câu hỏi và không đi lấy báo giá trực tiếp trên Internet. Tên nhà cung cấp và giá trong bộ mẫu phục vụ demo, không phải báo giá thương mại đã xác minh.

Các đơn vị có thể gồm:

- `PACKAGE`: tính theo gói.
- `PER_PERSON`: tính theo số người.
- `PER_HOUR`: tính theo thời lượng.

Nếu một nhóm dịch vụ không có dữ liệu phù hợp, hệ thống phải báo thiếu dữ liệu thay vì tự bịa giá.

## Cách chọn dịch vụ và xử lý thiếu dữ liệu

Mỗi dịch vụ phải đang hoạt động, đúng mức chất lượng, khớp địa điểm tìm kiếm và có khoảng sức chứa bao gồm số khách đã nhập. Trong từng nhóm được chọn, hệ thống ưu tiên dịch vụ có giá cao nhất của khoảng giá nhỏ nhất, rồi xét giá thấp nhất và mã định danh nếu bằng nhau. Đây không phải mô hình dự đoán giá bằng học máy.

Nếu báo “Không tìm thấy dịch vụ phù hợp cho: VENUE, SOUND_LIGHT”, nghĩa là thiếu Địa điểm hoặc Âm thanh ánh sáng thỏa điều kiện. Hãy kiểm tra địa điểm, chất lượng và quy mô thực tế. Có thể thử mức chất lượng khác nếu chấp nhận thay đổi yêu cầu, hoặc đề nghị người quản lý bổ sung dữ liệu dịch vụ phù hợp.

Ví dụ minh họa: gói Cao cấp nhận từ 300 khách sẽ không phù hợp yêu cầu 100 khách. Không tăng giả số khách chỉ để vượt kiểm tra. Lỗi này xảy ra ở bước chọn dữ liệu để tính, không phải do câu hỏi dài hoặc hết hạn mức Gemini. Thêm tài liệu Markdown không tự tạo thêm dịch vụ trong database.

## Công thức dự toán

Với mỗi dịch vụ:

```text
Chi phí dịch vụ = đơn giá × số lượng áp dụng
```

Số lượng áp dụng là 1 đối với gói, số khách đối với dịch vụ theo người, và số giờ đối với dịch vụ theo giờ. Nếu chưa nhập số giờ, hệ thống dùng thời lượng có sẵn của dịch vụ nếu có; nếu vẫn thiếu thì yêu cầu bổ sung. Gói không tự nhân thêm theo số khách.

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

Đây là trung bình theo loại vé, không tính trọng số theo số vé đã bán. Phép đối chiếu hiện chưa lọc theo địa điểm, số khách hoặc thời gian bắt đầu. Không gọi kết quả này là giá trung bình của riêng những sự kiện sắp diễn ra tại địa điểm đã nhập.

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
