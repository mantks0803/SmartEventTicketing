# Kết quả đánh giá RAG

- Bộ dữ liệu: **SmartEventTicketing RAG Evaluation**
- Thời gian chạy: **18/08/2026 22:00:40 SE Asia Standard Time**
- Tổng số câu hỏi: **30**
- Top K: **4**

## Chỉ số tổng hợp

| Chỉ số | Kết quả |
|---|---:|
| Hit@4 | 100.00% |
| Source accuracy sau relevance filter | 100.00% |
| No-answer accuracy | 100.00% |
| Answer decision accuracy | 100.00% |
| Retrieval latency trung bình | 640.59 ms |

## Chi tiết từng câu hỏi

| ID | Vai trò | Nguồn mong đợi | Nguồn đầu tiên | Distance | Kết quả |
|---|---|---|---|---:|---|
| customer_event_visibility | CUSTOMER | customer/01_event_search.md | customer/01_event_search.md | 0.2927 | PASS |
| customer_live_seat_status | CUSTOMER | customer/01_event_search.md | customer/01_event_search.md | 0.2524 | PASS |
| customer_max_seats | CUSTOMER | customer/02_seat_hold.md | customer/02_seat_hold.md | 0.2407 | PASS |
| customer_hold_time | CUSTOMER | customer/02_seat_hold.md | customer/02_seat_hold.md | 0.2237 | PASS |
| customer_expired_order | CUSTOMER | customer/02_seat_hold.md | customer/02_seat_hold.md | 0.2071 | PASS |
| customer_payos_return_url | CUSTOMER | customer/03_payos_payment.md | customer/03_payos_payment.md | 0.1654 | PASS |
| customer_payos_late_confirmation | CUSTOMER | customer/03_payos_payment.md | customer/03_payos_payment.md | 0.1993 | PASS |
| customer_ticket_issued | CUSTOMER | customer/04_ticket_qr_checkin.md | customer/04_ticket_qr_checkin.md | 0.2405 | PASS |
| customer_qr_reuse | CUSTOMER | customer/04_ticket_qr_checkin.md | customer/04_ticket_qr_checkin.md | 0.2343 | PASS |
| customer_missing_email | CUSTOMER | customer/05_order_support.md | customer/05_order_support.md | 0.1758 | PASS |
| organizer_event_plan | ORGANIZER | organizer/01_event_planning.md | organizer/01_event_planning.md | 0.1551 | PASS |
| organizer_event_approval | ORGANIZER | organizer/01_event_planning.md | organizer/08_event_timeline.md | 0.2180 | PASS |
| organizer_budget_range | ORGANIZER | organizer/02_budget_planning.md | organizer/02_budget_planning.md | 0.2341 | PASS |
| organizer_break_even | ORGANIZER | organizer/02_budget_planning.md | organizer/02_budget_planning.md | 0.1717 | PASS |
| organizer_venue_capacity | ORGANIZER | organizer/03_venue_capacity.md | organizer/03_venue_capacity.md | 0.1727 | PASS |
| organizer_venue_survey | ORGANIZER | organizer/03_venue_capacity.md | organizer/03_venue_capacity.md | 0.2058 | PASS |
| organizer_sound_light | ORGANIZER | organizer/04_sound_light_stage.md | organizer/04_sound_light_stage.md | 0.1634 | PASS |
| organizer_decoration_checkin | ORGANIZER | organizer/05_decoration_branding.md | organizer/05_decoration_branding.md | 0.2665 | PASS |
| organizer_checkin_staff | ORGANIZER | organizer/06_staff_checkin.md | organizer/06_staff_checkin.md | 0.2136 | PASS |
| organizer_checkin_permission | ORGANIZER | organizer/06_staff_checkin.md | organizer/06_staff_checkin.md | 0.2227 | PASS |
| organizer_marketing_phases | ORGANIZER | organizer/07_marketing_ticketing.md | organizer/07_marketing_ticketing.md | 0.2074 | PASS |
| organizer_ticket_design | ORGANIZER | organizer/07_marketing_ticketing.md | organizer/07_marketing_ticketing.md | 0.2447 | PASS |
| organizer_timeline | ORGANIZER | organizer/08_event_timeline.md | organizer/08_event_timeline.md | 0.1612 | PASS |
| organizer_payout_demo | ORGANIZER | organizer/08_event_timeline.md | organizer/08_event_timeline.md | 0.2294 | PASS |
| organizer_risk_priority | ORGANIZER | organizer/09_risk_management.md | organizer/09_risk_management.md | 0.2293 | PASS |
| out_of_scope_weather | CUSTOMER | - | customer/05_order_support.md | 0.4865 | PASS |
| out_of_scope_cooking | CUSTOMER | - | customer/01_event_search.md | 0.4811 | PASS |
| out_of_scope_stock | ORGANIZER | - | organizer/01_event_planning.md | 0.4695 | PASS |
| out_of_scope_medical | CUSTOMER | - | customer/05_order_support.md | 0.4620 | PASS |
| out_of_scope_football | ORGANIZER | - | organizer/03_venue_capacity.md | 0.4443 | PASS |

## Cách hiểu kết quả

- `Hit@K`: nguồn đúng xuất hiện trong K kết quả retrieval đầu tiên.
- `Source accuracy`: nguồn đúng vẫn còn sau khi lọc relevance.
- `No-answer accuracy`: câu ngoài phạm vi được từ chối đúng.
- `Generation keyword coverage`: câu trả lời chứa các ý bắt buộc.

> Kết quả phụ thuộc model embedding, tài liệu và cấu hình hiện tại.
