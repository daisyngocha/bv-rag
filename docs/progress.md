# Tiến độ ĐA1

| Tuần | Việc chính | Trạng thái | Ghi chú |
| --- | --- | --- | --- |
| 0 | Gửi thầy đề cương + lộ trình; smoke test hạ tầng; dựng repo | Đang làm | |
| 1 | Lý thuyết, chốt sản phẩm, làm thử 1 sản phẩm | | |
| 2 | Thu thập, parse tài liệu | | |
| 3 | Chunking, catalog, từ điển; benchmark nháp | | |
| 4 | Baseline B0–B2; chốt mục tiêu số | | |
| 5 | B3; chốt benchmark v1 | | |
| 6 | B4 hoàn chỉnh | | |
| 7 | Demo; chạy test B0–B4 | | |
| 8 | Hiệu chỉnh Ragas, phân tích lỗi | | |
| 9–10 | Báo cáo, slide, bảo vệ | | |

## Kết quả smoke test hạ tầng

Dán phần tóm tắt của `scripts/smoke_test.py` vào đây (máy, GPU/CPU, tok/s, thời gian embed, ước tính thời gian chạy test).
| Thành phần	| Kết quả	| Đánh giá |
| --- | --- | --- |
| Máy |	8 nhân CPU, 12,3 GB RAM, không có GPU	|Tự quyết định mọi thứ bên dưới |
| bge-m3 |	1,39 giây/chunk, top-1 đúng 3/3	| Dùng được: 4.000 chunk mất khoảng 1,5 giờ, chỉ chạy 1 lần cho mỗi phiên bản dữ liệu |
| Qdrant | 1.20.0 hybrid	24 ms/truy vấn, đáp án đúng nằm hạng 1 cả 3 câu	| Tốt |
| Reranker | 88 giây cho 30 cặp, top-1 đúng 3/3	| Chất lượng ổn nhưng quá chậm |
| Qwen 7B |	prefill 19 tok/s, decode 4,7 tok/s, 89 giây cho một câu trả lời ngắn	| Trả lời đúng và có trích dẫn, nhưng chậm |
