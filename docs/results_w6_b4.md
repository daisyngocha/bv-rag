# Kết quả B4 và ablation B4rr, B4ng (tuần 6)

Benchmark v1, dữ liệu `processed/v1` (manifest `data/manifests/v1.json`), Colab L4, Qwen2.5 7B q4 (num_ctx 8192),
context_n 5, top_k 30, reranker `BAAI/bge-reranker-v2-m3` (max_length 1024, điểm sigmoid). Mọi run được `eval.metrics`
đánh dấu "chính thức". B3 lấy từ `docs/results_w5_b3.md` (run `B3_v1_test_20261107-1020`).
Cấu hình B4 (prompt rag_v3, `rerank.min_score` 0,90) chốt trên dev trước khi chạy test (decision-log 07/11); không chỉnh
gì theo kết quả test.

| Cấu hình | Khác cấu hình trước | Run test | Run dev (seed 42/43/44) |
| --- | --- | --- | --- |
| B3 | hybrid + query processor, rag_v1 | `B3_v1_test_20261107-1020` | `B3_v1_dev_20261107-1012_r*` |
| B4rr | + rerank (rerank riêng từng sản phẩm rồi ghép), rag_v1, không chặn | `B4rr_v1_test_20261107-1335` | `B4rr_v1_dev_20261107-1131_r*` |
| B4ng | + prompt rag_v3 (trích dẫn [n]), không chặn | `B4ng_v1_test_20261107-1335` | (không chạy dev) |
| B4 | + ngưỡng từ chối min_score 0,90 | `B4_v1_test_20261107-1335` | `B4_v1_dev_20261107-1259_r*` |

Dev rag_v2 (`B4_v1_dev_20261107-1131_r*`, không chặn) chỉ dùng để chọn ngưỡng và prompt, không chạy test.
`B4_v1_dev_20261107-1325_r*` chạy lại đúng cấu hình 1259 trong phiên test: mọi metric trùng khớp 1259 trừ p95
(cùng seed cho cùng câu trả lời trên L4), không dùng thêm.

CSV: `results/archive_v1/B4*_v1_test_20261107-1335.csv`, `results/B4*_v1_dev_20261107-{1131,1259,1325}_r*.csv`;
theo câu: `results/review/per_question_v1_test_b4.csv`.

## Bảng 1. Test, dòng all (120 câu: 96 answerable, 24 out_of_scope)

| Cấu hình | R@1 | R@5 | full_R@5 | MRR | Từ chối đúng | Từ chối nhầm | Hedge | Có trích dẫn | Trích dẫn đúng* | Khớp số | Số lạ** | Bị chặn | p95 (s) | Giờ L4/1.000 câu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B3 | 0,635 | 0,896 | 0,854 | 0,746 | 1,000 | 0,156 | 0,123 | 0,407 | 0,793 | 0,710 | | | 4,35 | 0,67 |
| B4rr | 0,771 | 0,906 | 0,875 | 0,835 | 1,000 | 0,167 | 0,062 | 0,400 | 0,732 | 0,739 | 0,013 | 0 | 6,15 | 0,96 |
| B4ng | 0,771 | 0,906 | 0,875 | 0,835 | 1,000 | 0,104 | 0,046 | 0,977 | 0,680 | 0,669 | 0,012 | 0 | 6,05 | 0,89 |
| B4 | 0,771 | 0,906 | 0,875 | 0,835 | 1,000 | 0,135 | 0,012 | 0,988 | 0,709 | 0,661 | 0,000 | 0,225 | 5,74 | 0,80 |

\* Cận dưới tự động: chỉ tính trích dẫn trỏ đúng `evidence_ids`. \*\* `num_unsup`: câu trả lời có số không có trong
ngữ cảnh lẫn câu hỏi.

## Bảng 2. Test theo nhóm (24 câu/nhóm)

| Nhóm | R@5 B3 | R@5 B4 | MRR B4 | Từ chối nhầm B3 | B4rr | B4ng | B4 | Bị chặn B4 | Trích dẫn đúng* B4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lookup | 0,875 | 1,000 | 0,931 | 0,083 | 0,042 | 0,042 | 0,042 | 0,000 | 0,870 |
| table | 0,958 | 1,000 | 0,866 | 0,000 | 0,000 | 0,000 | 0,000 | 0,000 | 0,542 |
| compare | 0,917 | 0,917 | 0,834 | 0,125 | 0,083 | 0,042 | 0,208 | 0,167 | 0,746 |
| scenario | 0,833 | 0,708 | 0,707 | 0,417 | 0,542 | 0,333 | 0,292 | 0,000 | 0,688 |
| out_of_scope (từ chối đúng) | 1,000 | 1,000 | | | | | | 0,958 | |

compare full_recall@5: B3 0,750 → B4 0,792.
B4rr, B4ng, B4 cùng truy xuất nên cột truy xuất giống nhau.

## Bảng 3. Dev, dao động giữa 3 lần chạy (mean ± sd)

| Đợt | Recall@5 | MRR | Từ chối đúng | Từ chối nhầm | Hedge | Có trích dẫn | Khớp số | p95 (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B4rr 1131 (rag_v1) | 1,000 ± 0,000 | 0,903 ± 0,000 | 0,833 ± 0,000 | 0,167 ± 0,000 | 0,067 ± 0,058 | 0,467 ± 0,058 | 0,882 ± 0,044 | 5,68 ± 0,30 |
| B4 1131 (rag_v2, không chặn) | 1,000 ± 0,000 | 0,903 ± 0,000 | 0,667 ± 0,000 | 0,000 ± 0,000 | 0,028 ± 0,024 | 0,972 ± 0,024 | 0,864 ± 0,004 | 5,70 ± 0,26 |
| B4 1259 (rag_v3, 0,90) | 1,000 ± 0,000 | 0,903 ± 0,000 | 0,833 ± 0,000 | 0,042 ± 0,000 | 0,145 ± 0,066 | 0,942 ± 0,025 | 0,854 ± 0,077 | 5,56 ± 0,57 |

## So với mục tiêu B4 (đề xuất 07/11, GVHD xác nhận 14/11)

| Mục tiêu (test) | B4 | Đạt |
| --- | --- | --- |
| Recall@5 ≥ 0,92 | 0,906 | Không |
| Recall@5 mỗi nhóm ≥ 0,85 | scenario 0,708 | Không (lookup, table 1,000; compare 0,917) |
| full_recall@5 compare ≥ 0,80 | 0,792 | Không (19/24, thiếu 1 câu) |
| MRR ≥ 0,80 | 0,835 | Đạt |
| Từ chối đúng ≥ 0,90 | 1,000 | Đạt |
| Từ chối nhầm ≤ 0,10 | 0,135 (B4ng 0,104) | Không |
| Có trích dẫn ≥ 0,90 | 0,988 | Đạt |
| Trích dẫn đúng ≥ 0,85 (kiểm tay 30 câu) | cận dưới 0,709 | Chưa kiểm tay |
| Hedge ≤ 0,05 | 0,012 | Đạt |
| p95 ≤ 6 s | 5,74 | Đạt (compare 6,24, scenario 6,28) |

## Nhận định

1. Rerank (B3 → B4rr) đẩy chunk đúng lên đầu: Recall@1 +0,136 (0,635 → 0,771), MRR +0,089 (0,746 → 0,835), đạt
   mục tiêu MRR. Recall@5 chỉ +0,010 (0,896 → 0,906) vì lợi và hại bù nhau: lookup 0,875 → 1,000, table 0,958 → 1,000,
   compare full_recall@5 0,750 → 0,792, nhưng scenario GIẢM 0,833 → 0,708 (3/24 câu). Giả thuyết (chưa kiểm): câu
   scenario dài, kể tình huống; reranker chấm cao chunk khớp từ ngữ tình huống hơn chunk điểm loại trừ chứa đáp án.
   Cần xem 3 câu tụt trong `per_question_v1_test_b4.csv` (cột rank_B3 so với rank_B4).
2. Prompt (B4rr → B4ng, rag_v1 → rag_v3): có trích dẫn 0,400 → 0,977, từ chối nhầm 0,167 → 0,104 (scenario 0,542 → 0,333,
   compare 0,083 → 0,042), hedge 0,062 → 0,046, từ chối đúng giữ 1,000. Trích dẫn [n] loại hẳn lỗi chép mã SPMAU_.
   Cái giá: khớp số 0,739 → 0,669 (table 0,701 → 0,688, compare 0,741 → 0,654, scenario 0,679 → 0,474): câu trả lời
   ngắn và dè dặt hơn; xem thêm trong phân tích lỗi tuần 8.
3. Ngưỡng (B4ng → B4): trên test model đã tự từ chối đúng 24/24 câu out_of_scope ở B4ng, nên ngưỡng không tăng từ chối
   đúng. Ngưỡng chặn 23/24 câu out_of_scope trước LLM (p95 nhóm out_of_scope 2,69 → 1,67 s, giờ L4 0,89 → 0,80/1.000 câu)
   nhưng chặn nhầm 4/24 câu compare (từ chối nhầm compare 0,042 → 0,208), tổng từ chối nhầm 0,104 → 0,135. Trên dev
   không câu compare nào bị chặn. Nghi nguyên nhân: câu compare rerank từng sản phẩm bằng nguyên câu hỏi so sánh, nên điểm
   cao nhất của từng chunk thấp hơn câu hỏi một sản phẩm. Không chỉnh ngưỡng theo test; ghi cho phân tích lỗi.
4. Từ chối nhầm còn lại tập trung ở scenario (0,292) và gắn với truy xuất trượt (Recall@5 scenario 0,708): khi
   evidence không vào top-5, từ chối là hành vi đúng của prompt. Phần còn lại giao cho tuần 8 (xem 3 câu tụt ở mục 1).
5. Trích dẫn đúng (cận dưới) 0,709, thấp nhất ở table 0,542: cần kiểm tay 30 câu để biết bao nhiêu là trích chunk khác
   cũng chứa đáp án (chunk quy tắc nhắc lại số trong biểu phí).
6. Chi phí: 0,80 giờ L4/1.000 câu (B3 0,67), p95 5,74 s; rerank làm tăng độ trễ, ngưỡng bù lại một phần nhờ không gọi
   LLM cho câu bị chặn.
7. RQ2: B2 → B4 Recall@5 0,865 → 0,906, MRR 0,709 → 0,835, từ chối nhầm 0,208 → 0,135, có trích dẫn 0,579 → 0,988.
   Chênh lệch Recall@5 giữa các bước nhỏ (B3 → B4: 1/96 câu); kiểm McNemar theo cặp câu ở tuần 8.

## Rà câu nghi lỗi (test, B3/B4rr/B4ng/B4)

`eval.per_question` gắn cờ 9/120 câu (tuần 5 trên B1/B2/B3hyb/B3: 14 câu).

| Cờ | Câu | So với tuần 5 |
| --- | --- | --- |
| miss_all | v1-0046, 0049, 0106 | Vẫn trượt. 0087 (tuần 5 hạng 12) không còn miss_all: rerank kéo được lên |
| refuse_all | v1-0046, 0049, 0089, 0108, 0129 | 0041, 0048, 0114, 0115, 0126 hết refuse_all (B4ng/B4 trả lời được câu điểm loại trừ); 0108 mới |
| num0_all | v1-0006, 0092, 0101 | 0092 vẫn đọc nhầm ô bảng gộp (lỗi parse P1); 0101 mới (biểu phí FLX) |

Việc tuần 8: dump chi tiết 9 câu (`--dump-md`), 3 câu scenario tụt hạng do rerank, 4 câu compare bị chặn, kiểm tay
trích dẫn 30 câu, McNemar B2/B3/B4.
