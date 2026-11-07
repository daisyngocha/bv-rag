# Tiến độ ĐA1

| Tuần | Việc chính | Trạng thái | Ghi chú |
| --- | --- | --- | --- |
| 0 | Gửi thầy đề cương + lộ trình; smoke test hạ tầng; dựng repo | Xong | Repo, smoke test, chọn GPU L4, đồng bộ tài liệu (README mục Colab L4, pin version theo smoke v3); đã gửi thầy đề cương + lộ trình |
| 1 | Lý thuyết, chốt sản phẩm, làm thử 1 sản phẩm | Xong | Pilot BVP xong (PR #5); chốt 5 sản phẩm BHBV, bỏ R26 và brochure (decision-log 2026-11-05, chờ GVHD); `scripts/build_kb.py` + config/truth theo sản phẩm; chunk cố định cho B1 và bảng căn chỉnh `align_fixed.json`. Chạy lại BVP bằng `build_kb.py` trên WSL: 127 chunk cấu trúc (trùng id với pilot), 56 chunk cố định, 12/12 kiểm tra, căn chỉnh 127/127 phủ ≥ 0,5. Còn: chương tổng quan |
| 2 | Thu thập, parse tài liệu | Xong (06/11) | `scripts/colab_batch.ipynb` (cell đầu dừng nếu GPU không phải L4), `scripts/sync.sh` (rclone Drive), embed + index + Retriever: chạy thử BVP trên L4 (commit `4c2af96`): embed cấu trúc 127 chunk 2,69 s (0,021 s/chunk), cố định 56 chunk 0,82 s (0,015 s/chunk); nạp Qdrant :memory: và truy xuất 6 câu thử chạy được, vector ở Drive `vectors/v1/`. 05/11: đã tải tài liệu BTB, C37, FLX, ITC. BVP xây lại: 123/57 chunk, 13/13 kiểm tra, căn chỉnh 123/123. Còn lại: parse + truth 4 sản phẩm, hạn 11/11. ITC xong: 181 chunk cấu trúc, 76 cố định, 13/13 kiểm tra. C37 xong: 84 chunk cấu trúc, 35 cố định, 13/13 kiểm tra. BTB xong (06/11, sau PR #17): 144 chunk cấu trúc (quy tắc 128 + BQL 11 + biểu phí 4 + 1 manual_units), 70 cố định, 13/13 kiểm tra, căn chỉnh 144/144; quy tắc OCR Tesseract 4.1.1 fast, PL III nhập tay (manual: true); BQL có 1 chunk 562 token (> 512). Kho v1 = 4/5 sản phẩm (BTB, BVP, C37, ITC): 532 chunk cấu trúc, 238 cố định; còn FLX. 06/11: giới hạn token embed/rerank nâng 512 → 1024 (PR #18), build --all 4 sản phẩm đạt mọi kiểm tra (thêm kiểm tra chunk ≤ 1024 token); embed lại v1 trên Colab L4: structure 532 chunk (BTB 144, BVP 123, C37 84, ITC 181), fixed 238 (BTB 70, BVP 57, C37 35, ITC 76), max_length 1024, commit a62653c, vector ở Drive `vectors/v1/`. Thời gian embed: cấu trúc 4,55 s (0,0086 s/chunk), cố định 2,58 s (0,0108 s/chunk). FLX xong (06/11): 102 chunk cấu trúc (quy tắc 85 + BQL 8 + biểu phí 9), 48 cố định, 14/14 kiểm tra, căn chỉnh 102/102; BQL OCR Tesseract 4.1.1 + bảng nhập tay (data/manual/FLX_BQL.csv), biểu phí từ docx đã đối chiếu (không OCR). Kho v1 = 5/5 sản phẩm: 634 chunk cấu trúc, 286 cố định. Embed lại v1 trên Colab L4 (commit 6f28917): structure 634 chunk (BTB 144, BVP 123, C37 84, FLX 102, ITC 181) 4,9 s (0,0077 s/chunk), fixed 286 (BTB 70, BVP 57, C37 35, FLX 48, ITC 76) 2,99 s (0,0105 s/chunk), max_length 1024.|
| 3 | Chunking, catalog, từ điển; benchmark nháp | Đang làm | 09/11: đóng băng v1 (data/manifests/v1.json), 634/286 chunk, vector commit 6f28917; `colab_batch.ipynb` kiểm manifest, không embed lại v1. 07/11: từ điển `data/glossary.json` 241 mục = 13 general (10 khoản Điều 4 VBHN 31/VBHN-VPQH + 3 định nghĩa TT 67/2023 Điều 12) + 228 định nghĩa sản phẩm tách bằng code từ chunk v1 (BTB 52, BVP 53, C37 22, FLX 39, ITC 62; 2 thuật ngữ OCR BTB sửa tay, 7 alias từ ngoặc); Product Catalog `data/catalog.json` 5 sản phẩm (trường tự động từ config/truth/sources; trường nội dung từ `data/manual/catalog.csv`, có chunk_id nguồn, số đã đối chiếu text chunk). Còn: benchmark nháp |
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
