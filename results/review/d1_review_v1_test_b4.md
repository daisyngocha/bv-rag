# Rà lỗi benchmark (D1) trước tuần 8: 9 câu nghi lỗi của B4 + 2 ca từ demo (09/11)

Đầu vào: `benchmark/benchmark_v1.jsonl`, text chunk `processed/v1/chunks.jsonl` (Drive, khớp manifest v1, 634 chunk),
log `runs/{B4,B4rr,B4ng}_v1_test_20261107-1335/log.jsonl` (Drive, 120 câu), cờ nghi lỗi từ
`results/review/per_question_v1_test_b4.csv`, log demo `docs/demo/B4_demo_20261109-0843_log.jsonl`.

Tiêu chí D1: đáp án chuẩn không suy ra được 100% từ text evidence, hoặc evidence_ids thiếu/sai chunk chứa đáp án.

## Kết luận

**0/11 ca là D1.** Đáp án và evidence đúng ở cả 11 ca; `benchmark_v1.jsonl` giữ nguyên, không chạy lại B0–B4.
Toàn bộ lỗi thuộc hệ thống, nhãn chính dùng cho phân tích lỗi (bước 5):

| qid | Nhóm | Cờ | Evidence trong top-5 B4? | Hành vi B4 | Nhãn | Ghi chú |
| --- | --- | --- | --- | --- | --- | --- |
| v1-0006 | lookup | num0_all | có, hạng 1 | trả lời đúng ý chính | G1 (thiếu ý) | Thiếu câu "tổng không vượt quá 100% số tiền bảo hiểm" nên không khớp số 100; chunk có rác OCR ("I¬il 4 /¬*Ỷ 2#") nhưng không ảnh hưởng |
| v1-0046 | scenario | miss_all, refuse_all | không | từ chối | R1 | Đáp án ở khoản 10 của chunk danh sách loại trừ C37_QT_C3_K9 (9 khoản); top-5 là bảng quyền lợi, định nghĩa |
| v1-0049 | scenario | miss_all, refuse_all | không | từ chối | R1 | Câu đáp án là gạch đầu dòng cuối của chunk nghĩa vụ dài (BTB_QT_C4_M14_K2_P1); chunk tiếp P2 ở hạng 24 không chứa đáp án |
| v1-0089 | lookup | refuse_all | có, hạng 1 | từ chối | F1 | Evidence nêu nguyên văn cả xử lý lẫn ngoại lệ ("trừ khi… có lý do chính đáng và được pháp luật cho phép"); lỗi thuần ở sinh |
| v1-0092 | table | num0_all | có, hạng 1 | trả lời 30.000.000 (sai) | P1 → G1 | Bảng quyền lợi BTB gộp 2 mục (nằm viện + phẫu thuật đặc biệt) trong một ô; cột Nâng cao = 50.000.000, model lấy cột Mở rộng. Đã đối chiếu `btb_bangquyenloi.pdf` trang 1 (09/11): cột Nâng cao, phẫu thuật đặc biệt = 50.000.000/năm, đáp án chuẩn đúng |
| v1-0101 | table | num0_all | có, hạng 3 | trả lời 8.500.000 (sai) | G1 | 300 ngày thuộc dòng 295–301 ngày (8.900.000); model lấy dòng đầu bảng 281–287. Lỗi suy luận khoảng, bảng parse đúng |
| v1-0106 | scenario | miss_all | không | từ chối | R1 | Cả 2 điểm loại trừ (khoản 11 dịch bệnh nhóm A/B, khoản 16 suy thận/chạy thận) nằm trong BTB_QT_C3_K1_P2; chunk OCR nhiễu ("L2,", "l5:") |
| v1-0108 | scenario | refuse_all | không | từ chối | R1 | FLX_QT_C3_K13 (khủng bố NCB, gồm cả hành động ngăn chặn/đàn áp) không vào top-5; top-5 là quyền lợi chương II và loại trừ K2–9 |
| v1-0129 | compare | refuse_all | có, hạng 1 và 2 | từ chối | F1 | Đủ evidence 2 sản phẩm; model từ chối câu so sánh cần suy luận từ chỗ không có (An Gia không có vợ/chồng, bố/mẹ) |
| v1-0053 (dev, demo) | compare | – | có, hạng 1 và 2 | trả lời sai một phần | G1 | ITC_QT_C4_M1_P1 ghi rõ "đến 69 tuổi nếu mới tham gia lần đầu hoặc đến 75 tuổi nếu tham gia tái tục"; model gán sai 69/75. `nums_unsupported` không bắt được vì cả hai số có trong nguồn |
| "635 ngày" (demo 08/11, BTB) | – | – | – | – | không lỗi | "635 ngày đối với (trường hợp) sinh con" có nguyên văn trong BTB_QT_C4_M3_K1, BVP_QT_C2_M2_B5_B, ITC_QT_C4_M10_K1 (BVP, ITC không qua OCR); hệ thống trung thành với nguồn. Ghi chú như decision-log 05/11: không dùng làm đáp án benchmark |

Phân bố nhãn (11 ca): R1 4, G1 4 (0006, 0092, 0101, 0053), F1 2, không lỗi 1, D1 0.

## Nhận xét cho phân tích lỗi

1. R1 tập trung ở câu scenario hỏi về điểm loại trừ/nghĩa vụ (0046, 0049, 0106, 0108): đáp án là một khoản trong chunk
   danh sách dài nhiều khoản, embedding của cả chunk loãng so với câu hỏi tình huống. Hướng ĐA2: tách chunk theo từng khoản
   của chương loại trừ, hoặc query rewriting tình huống → điều khoản.
2. F1 xảy ra khi evidence đã ở hạng 1–2 (0089, 0129): prompt rag_v3 nghiêng về từ chối với câu cần suy luận
   (ngoại lệ, so sánh "không có").
3. G1 ở bảng (0092, 0101) và gán sai thuộc tính (0053): cờ `nums_unsupported` chỉ kiểm số có trong nguồn,
   không kiểm số đúng ô/đúng thuộc tính.
