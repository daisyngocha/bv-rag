# Kết quả B3 và ablation B3hyb (tuần 5)

Benchmark v1, dữ liệu `processed/v1` (manifest `data/manifests/v1.json`), Colab L4, Qwen2.5 7B q4 (num_ctx 8192),
prompt rag_v1, context_n 5, code nhánh `feat/week5` (commit `e282620`). Mọi run được `eval.metrics` đánh dấu "chính thức".
B2 lấy từ `docs/results_w4_baseline.md` (run `B2_v1_test_20261107-0904`, cùng prompt, cùng khối llm).

| Cấu hình | Khác cấu hình trước | Run test | Run dev (seed 42/43/44) |
| --- | --- | --- | --- |
| B2 | dense, chunk cấu trúc | `B2_v1_test_20261107-0904` | `B2_v1_dev_20261107-0832_r{0,1,2}` |
| B3hyb | + hybrid dense + sparse (RRF), không lọc | `B3hyb_v1_test_20261107-1020` | `B3hyb_v1_dev_20261107-1012_r{0,1,2}` |
| B3 | + query processor: lọc product_code, tách câu ≥ 2 sản phẩm | `B3_v1_test_20261107-1020` | `B3_v1_dev_20261107-1012_r{0,1,2}` |

CSV: `results/B3_v1_{test,dev}_20261107*.csv`, `results/B3hyb_v1_{test,dev}_20261107*.csv` (ghi trên WSL).

## Bảng 1. Test, dòng all (120 câu: 96 answerable, 24 out_of_scope)

| Cấu hình | Recall@1 | Recall@5 | full_R@5 | MRR | Từ chối đúng | Từ chối nhầm | Hedge | Có trích dẫn | Trích dẫn đúng* | Khớp số | p95 (s) | Giờ GPU/1.000 câu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B2 | 0,604 | 0,865 | 0,792 | 0,709 | 1,000 | 0,208 | 0,132 | 0,579 | 0,761 | 0,675 | 4,65 | 0,66 |
| B3hyb | 0,615 | 0,885 | 0,823 | 0,731 | 1,000 | 0,198 | 0,104 | 0,429 | 0,677 | 0,682 | 4,41 | 0,65 |
| B3 | 0,635 | 0,896 | 0,854 | 0,746 | 1,000 | 0,156 | 0,123 | 0,407 | 0,793 | 0,710 | 4,35 | 0,67 |

\* Cận dưới: chỉ tính trích dẫn trỏ đúng `evidence_ids`.

## Bảng 2. Test theo nhóm (24 câu/nhóm)

| Nhóm | R@5 B2 | R@5 B3hyb | R@5 B3 | full_R@5 B2 | full_R@5 B3hyb | full_R@5 B3 | Từ chối nhầm B2 | B3hyb | B3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lookup | 0,833 | 0,875 | 0,875 | 0,833 | 0,875 | 0,875 | 0,125 | 0,083 | 0,083 |
| table | 1,000 | 0,917 | 0,958 | 1,000 | 0,917 | 0,958 | 0,000 | 0,042 | 0,000 |
| compare | 0,917 | 0,917 | 0,917 | 0,625 | 0,667 | 0,750 | 0,208 | 0,250 | 0,125 |
| scenario | 0,708 | 0,833 | 0,833 | 0,708 | 0,833 | 0,833 | 0,500 | 0,417 | 0,417 |
| out_of_scope (từ chối đúng) | 1,000 | 1,000 | 1,000 | | | | | | |

## Bảng 3. Dev, dao động giữa 3 lần chạy (mean ± sd)

| Cấu hình | Recall@5 | MRR | Từ chối đúng | Từ chối nhầm | Hedge | Có trích dẫn | Khớp số |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B2 | 0,958 ± 0,000 | 0,813 ± 0,000 | 0,944 ± 0,096 | 0,208 ± 0,000 | 0,158 ± 0,000 | 0,386 ± 0,030 | 0,703 ± 0,044 |
| B3hyb | 0,958 ± 0,000 | 0,837 ± 0,000 | 1,000 ± 0,000 | 0,194 ± 0,024 | 0,258 ± 0,045 | 0,501 ± 0,069 | 0,846 ± 0,000 |
| B3 | 0,958 ± 0,000 | 0,856 ± 0,000 | 1,000 ± 0,000 | 0,153 ± 0,024 | 0,131 ± 0,027 | 0,459 ± 0,052 | 0,836 ± 0,009 |

p95 dev không dùng (r1, r2 dùng lại KV cache của r0).

## Nhận định

1. RQ2, phần truy xuất (test): B2 → B3 tăng Recall@5 +0,031 (0,865 → 0,896), Recall@1 +0,031, MRR +0,037,
   full_recall@5 +0,062. Hybrid (B2 → B3hyb) đóng góp Recall@5 +0,020, MRR +0,022; query processor
   (B3hyb → B3) thêm Recall@5 +0,011, MRR +0,015, full_recall@5 +0,031. Chênh lệch nhỏ: +0,031 Recall@5 là
   3/96 câu; phải kiểm McNemar theo cặp câu ở tuần 8 trước khi kết luận.
2. Tách câu theo sản phẩm có tác dụng đúng chỗ dự kiến: compare full_recall@5 0,625 (B2) → 0,667 (B3hyb) → 0,750 (B3),
   Recall@5 compare không đổi (0,917). Vẫn dưới mục tiêu 0,80 đề xuất cho B4.
3. Hybrid giúp scenario (Recall@5 0,708 → 0,833) và lookup (0,833 → 0,875) nhưng làm giảm table (1,000 → 0,917 ở B3hyb,
   0,958 ở B3): sparse kéo chunk quy tắc có cùng từ khóa lên trên chunk bảng. Cần xem 2 câu table bị trượt trong
   bảng per_question.
4. Phía sinh: từ chối nhầm 0,208 → 0,156 (compare 0,208 → 0,125), khớp số 0,675 → 0,710, trích dẫn đúng (cận dưới)
   0,761 → 0,793. Nhưng tỷ lệ có trích dẫn GIẢM: 0,579 (B2) → 0,429 (B3hyb) → 0,407 (B3), giảm ở cả table
   (0,208) và scenario (0,214). Ngữ cảnh hybrid khác ngữ cảnh dense nên cùng prompt rag_v1 cho kết quả trích dẫn khác;
   đây là việc chính của prompt trích dẫn B4.
5. Trên dev, B3 giảm hedge so với B3hyb (0,131 so với 0,258), chủ yếu ở compare (B3hyb hedge 1,000 cả 3 lần):
   khi top-5 chỉ có một sản phẩm, model trả lời phần có rồi chèn câu từ chối cho phần thiếu.
6. Từ chối đúng giữ 1,000; lọc theo sản phẩm (câu out_of_scope nêu tên sản phẩm cũng bị lọc) không làm model trả lời
   bừa trên test.
7. So với mục tiêu B4 đề xuất (decision-log 07/11): Recall@5 0,896 < 0,92; scenario 0,833 < 0,85 mỗi nhóm;
   MRR 0,746 < 0,80; từ chối nhầm 0,156 > 0,10; có trích dẫn 0,407 < 0,90. Phần còn lại giao cho rerank,
   ngưỡng và prompt B4. Chi phí không đổi: 0,67 giờ L4/1.000 câu, p95 4,35 s.
8. Giới hạn: câu hỏi benchmark v1 luôn nêu tên sản phẩm (nhận diện đúng 120/120 câu answerable), nên phần đóng góp
   của bộ lọc là cận trên so với câu hỏi thật.
