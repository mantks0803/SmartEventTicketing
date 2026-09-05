# Tài liệu SmartEventTicketing

| Nhu cầu | Đọc tại |
|---|---|
| Hiểu tổng quan và chức năng | [README chính](../README.md) |
| Cài đặt lần đầu, chạy lại, cấu hình dịch vụ | [SETUP](SETUP.md) |
| Nạp dữ liệu mẫu, thêm báo cáo, chuyển database | [Database](../database/README.md) |
| Cấu hình và chạy giao diện | [Frontend](../frontend/README.md) |
| Chuẩn bị và sử dụng chatbot | [AI Agent](../backend/ai_agent/README.md) |
| Chạy test | [Lệnh kiểm thử](TEST_COMMANDS.md) |
| Xem kịch bản và kết quả test | [Kế hoạch](TEST_PLAN.md) / [Báo cáo](TEST_REPORT.md) |
| Thử thanh toán local không dùng tiền thật | [Hướng dẫn thanh toán](PAYMENT_TEST.md) |
| Đánh giá RAG | [Hướng dẫn](../docs/RAG_EVALUATION.md) / [Kết quả](../docs/RAG_EVALUATION_RESULT.md) |
| Lưu bản sao database riêng tư | [Backup](../database/backups/README.md) |

Báo cáo test/evaluation là kết quả theo lần chạy, không tự cập nhật theo source mới. Chỉ dùng giả lập thanh toán ở local; không tắt kiểm tra chữ ký PayOS trên server public.

Các tài liệu đánh giá vẫn ở `docs/`; dữ liệu chatbot giữ nguyên tại `backend/ai_agent/data/`. Đây là thư mục hướng dẫn người dùng dự án, không phải nguồn kiến thức để nạp vào RAG.
