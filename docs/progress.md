# Tiến độ ĐA1

| Tuần | Việc chính | Trạng thái | Ghi chú |
| --- | --- | --- | --- |
| 0 | Gửi thầy đề cương + lộ trình; smoke test hạ tầng; dựng repo | Đang làm | Repo, smoke test, chọn GPU L4, đồng bộ tài liệu (README mục Colab L4, pin version theo smoke v3): xong. Còn: gửi thầy |
| 1 | Lý thuyết, chốt sản phẩm, làm thử 1 sản phẩm | Đang làm | Pilot BVP xong (PR #5); tạm chốt 6 sản phẩm; `scripts/build_kb.py` + config/truth theo sản phẩm; chunk cố định cho B1 và bảng căn chỉnh `align_fixed.json`. Chạy lại BVP bằng `build_kb.py` trên WSL: 127 chunk cấu trúc (trùng id với pilot), 56 chunk cố định, 12/12 kiểm tra, căn chỉnh 127/127 phủ ≥ 0,5. Còn: chương tổng quan |
| 2 | Thu thập, parse tài liệu | Đang làm | `scripts/colab_batch.ipynb` (cell đầu dừng nếu GPU không phải L4), `scripts/sync.sh` (rclone Drive), embed + index + Retriever: chạy thử BVP trên L4 (commit `4c2af96`): embed cấu trúc 127 chunk 2,69 s (0,021 s/chunk), cố định 56 chunk 0,82 s (0,015 s/chunk); nạp Qdrant :memory: và truy xuất 6 câu thử chạy được, vector ở Drive `vectors/v1/`. Còn: thu thập, parse 5 sản phẩm còn lại |
| 3 | Chunking, catalog, từ điển; benchmark nháp | | |
| 4 | Baseline B0–B2; chốt mục tiêu số | | |
| 5 | B3; chốt benchmark v1 | | |
| 6 | B4 hoàn chỉnh | | |
| 7 | Demo; chạy test B0–B4 | | |
| 8 | Hiệu chỉnh Ragas, phân tích lỗi | | |
| 9–10 | Báo cáo, slide, bảo vệ | | |

## Kết quả smoke test hạ tầng

| Chỉ số | Laptop WSL (CPU) | Colab L4 (v4, chọn) |
| --- | --- | --- |
| Embed bge-m3 | 1,39 s/chunk (4.000 chunk ~92 phút) | 0,026 s/chunk (~1,7 phút) |
| Rerank 30 cặp | 88 s | 0,56 s |
| Qdrant hybrid | 24 ms | 7,7 ms |
| Qwen2.5 7B prefill / decode | 19 / 4,7 tok/s | 3.498 / 51,9 tok/s, 100% GPU |
| Một lần chạy test (600 lượt sinh) | ~20–28 giờ | ~0,62 giờ (~1 unit) |
| Chất lượng (câu thử) | đúng, có trích dẫn | đúng, có trích dẫn |

Quyết định: GPU chạy trên Colab Pay As You Go, loại L4, dùng cho mọi lần chạy chính thức B0–B4 (xem decision-log 2026-10-25).

Số liệu gốc:
- `docs/smoke_20261024_2229.json`: laptop CPU.
- `docs/smoke_colab_L4_20261025_v4.json`: L4, số liệu chính thức. Cài từ `requirements/base.txt` đã pin (commit `c8f4682`); khớp v3 trong sai số đo.
- `docs/smoke_colab_L4_20261025_v3.json`: L4, cùng code nhưng chạy trước khi pin version (commit `abd24f8`).
- `docs/smoke_colab_L4_20261024.json`, `docs/smoke_colab_L4_20261025_v2.json`, `docs/smoke_colab_T4_20261025.json`: tham khảo quá trình sửa (v1: Ollama chia layer sang CPU; v2: lượt đầu gánh chi phí khởi tạo kernel). Số liệu T4 chưa đo lại sau khi sửa.
