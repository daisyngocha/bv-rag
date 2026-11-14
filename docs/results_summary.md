# Bảng tổng kết quả B0–B4 (test)

Benchmark **v1.1** test (120 câu: 96 answerable, 24 out_of_scope, 24 câu/nhóm), dữ liệu `processed/v1`, Colab L4,
Qwen2.5 7B q4 (num_ctx 8192, seed 42). Log là các run chính thức chạy với v1 (07/11); metric tính lại theo v1.1
(`eval.metrics --bench benchmark/benchmark_v1.1.jsonl`): 7 câu sửa evidence, 2 câu sửa đáp án chuẩn, câu hỏi giữ
nguyên (`benchmark/CHANGELOG.md`). Số theo v1: `results/archive_v1/`. Danh sách run: `configs/test_runs_official.txt`.
File này sinh bằng `PYTHONPATH=. python scripts/build_results_summary.py`; đừng sửa số bằng tay.
Chi tiết từng bước: `docs/results_w4_baseline.md` (B0–B2), `docs/results_w5_b3.md` (B3), `docs/results_w6_b4.md` (B4),
`docs/results_w8.md` (judge Ragas, kiểm định, phân tích lỗi).

| Cấu hình | Run test | Truy xuất | Prompt | Rerank / ngưỡng |
| --- | --- | --- | --- | --- |
| B0 | `B0_v1_test_20261107-0904` | không | norag_v1 | – |
| B1 | `B1_v1_test_20261107-0904` | dense, chunk cố định 512 (chấm qua căn chỉnh, ngưỡng 0,3) | rag_v1 | – |
| B2 | `B2_v1_test_20261107-0904` | dense, chunk cấu trúc | rag_v1 | – |
| B3hyb (ablation) | `B3hyb_v1_test_20261107-1020` | hybrid RRF, không lọc | rag_v1 | – |
| B3 | `B3_v1_test_20261107-1020` | hybrid + query processor | rag_v1 | – |
| B4rr (ablation) | `B4rr_v1_test_20261107-1335` | như B3 | rag_v1 | rerank, không chặn |
| B4ng (ablation) | `B4ng_v1_test_20261107-1335` | như B3 | rag_v3 | rerank, không chặn |
| B4 | `B4_v1_test_20261107-1335` | như B3 | rag_v3 | rerank, min_score 0,90 |

## Bảng 1. Test, dòng all (120 câu: 96 answerable, 24 out_of_scope)

| Cấu hình | Bước | R@1 | R@5 | full_R@5 | MRR | Từ chối đúng | Từ chối nhầm | Hedge | Có trích dẫn | Trích dẫn đúng* | Khớp số | p95 (s) | Giờ L4/1.000 câu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B0 | không RAG | – | – | – | – | 0,917 | 0,823 | 0,059 | – | – | 0,034 | 1,12 | 0,14 |
| B1 | dense, chunk cố định 512 | 0,427 | 0,771 | 0,646 | 0,584 | 1,000 | 0,323 | 0,108 | 0,400 | 0,628 | 0,472 | 4,64 | 0,76 |
| B2 | chunk cấu trúc + bảng Markdown | 0,604 | 0,875 | 0,792 | 0,713 | 1,000 | 0,208 | 0,132 | 0,579 | 0,750 | 0,675 | 4,65 | 0,66 |
| B3hyb | + hybrid RRF (ablation) | 0,615 | 0,896 | 0,823 | 0,733 | 1,000 | 0,198 | 0,104 | 0,429 | 0,677 | 0,682 | 4,41 | 0,65 |
| B3 | + query processor | 0,625 | 0,906 | 0,833 | 0,740 | 1,000 | 0,156 | 0,123 | 0,407 | 0,793 | 0,710 | 4,35 | 0,67 |
| B4rr | + rerank (ablation, rag_v1) | 0,781 | 0,896 | 0,875 | 0,838 | 1,000 | 0,167 | 0,062 | 0,400 | 0,763 | 0,739 | 6,15 | 0,96 |
| B4ng | + prompt rag_v3 (ablation, không chặn) | 0,781 | 0,896 | 0,875 | 0,838 | 1,000 | 0,104 | 0,046 | 0,977 | 0,697 | 0,669 | 6,05 | 0,89 |
| B4 | + ngưỡng từ chối 0,90 | 0,781 | 0,896 | 0,875 | 0,838 | 1,000 | 0,135 | 0,012 | 0,988 | 0,728 | 0,661 | 5,74 | 0,80 |
| Mục tiêu B4 |  |  | ≥ 0,92 |  | ≥ 0,80 | ≥ 0,90 | ≤ 0,10 | ≤ 0,05 | ≥ 0,90 | ≥ 0,85** |  | ≤ 6 |  |

## Bảng 1'. Recall@5 theo nhóm (24 câu/nhóm)

| Cấu hình | lookup | table | compare | scenario |
| --- | --- | --- | --- | --- |
| B0 | – | – | – | – |
| B1 | 0,833 | 0,833 | 0,833 | 0,583 |
| B2 | 0,833 | 1,000 | 0,958 | 0,708 |
| B3hyb | 0,875 | 0,917 | 0,958 | 0,833 |
| B3 | 0,875 | 0,958 | 0,958 | 0,833 |
| B4rr | 1,000 | 1,000 | 0,875 | 0,708 |
| B4ng | 1,000 | 1,000 | 0,875 | 0,708 |
| B4 | 1,000 | 1,000 | 0,875 | 0,708 |

## Bảng 1'. full_recall@5 theo nhóm (24 câu/nhóm)

| Cấu hình | lookup | table | compare | scenario |
| --- | --- | --- | --- | --- |
| B0 | – | – | – | – |
| B1 | 0,833 | 0,833 | 0,333 | 0,583 |
| B2 | 0,833 | 1,000 | 0,667 | 0,667 |
| B3hyb | 0,875 | 0,917 | 0,708 | 0,792 |
| B3 | 0,875 | 0,958 | 0,708 | 0,792 |
| B4rr | 1,000 | 1,000 | 0,792 | 0,708 |
| B4ng | 1,000 | 1,000 | 0,792 | 0,708 |
| B4 | 1,000 | 1,000 | 0,792 | 0,708 |

## Bảng 1'. MRR theo nhóm (24 câu/nhóm)

| Cấu hình | lookup | table | compare | scenario |
| --- | --- | --- | --- | --- |
| B0 | – | – | – | – |
| B1 | 0,636 | 0,562 | 0,702 | 0,437 |
| B2 | 0,664 | 0,774 | 0,779 | 0,637 |
| B3hyb | 0,703 | 0,755 | 0,800 | 0,675 |
| B3 | 0,711 | 0,756 | 0,812 | 0,683 |
| B4rr | 0,931 | 0,866 | 0,847 | 0,707 |
| B4ng | 0,931 | 0,866 | 0,847 | 0,707 |
| B4 | 0,931 | 0,866 | 0,847 | 0,707 |

## Bảng 1'. Từ chối nhầm theo nhóm (24 câu/nhóm)

| Cấu hình | lookup | table | compare | scenario |
| --- | --- | --- | --- | --- |
| B0 | 0,833 | 0,542 | 0,958 | 0,958 |
| B1 | 0,208 | 0,167 | 0,500 | 0,417 |
| B2 | 0,125 | 0,000 | 0,208 | 0,500 |
| B3hyb | 0,083 | 0,042 | 0,250 | 0,417 |
| B3 | 0,083 | 0,000 | 0,125 | 0,417 |
| B4rr | 0,042 | 0,000 | 0,083 | 0,542 |
| B4ng | 0,042 | 0,000 | 0,042 | 0,333 |
| B4 | 0,042 | 0,000 | 0,208 | 0,292 |

## Bảng 1'. Có trích dẫn theo nhóm (24 câu/nhóm)

| Cấu hình | lookup | table | compare | scenario |
| --- | --- | --- | --- | --- |
| B0 | – | – | – | – |
| B1 | 0,421 | 0,200 | 0,750 | 0,357 |
| B2 | 0,524 | 0,375 | 0,842 | 0,667 |
| B3hyb | 0,500 | 0,217 | 0,778 | 0,214 |
| B3 | 0,364 | 0,208 | 0,809 | 0,214 |
| B4rr | 0,348 | 0,167 | 0,818 | 0,182 |
| B4ng | 1,000 | 1,000 | 0,957 | 0,938 |
| B4 | 1,000 | 1,000 | 1,000 | 0,941 |

## Bảng 1'. Khớp số theo nhóm (24 câu/nhóm)

| Cấu hình | lookup | table | compare | scenario |
| --- | --- | --- | --- | --- |
| B0 | 0,000 | 0,069 | 0,000 | 0,038 |
| B1 | 0,800 | 0,396 | 0,347 | 0,513 |
| B2 | 0,900 | 0,729 | 0,660 | 0,423 |
| B3hyb | 0,900 | 0,708 | 0,688 | 0,462 |
| B3 | 0,900 | 0,729 | 0,703 | 0,538 |
| B4rr | 0,900 | 0,701 | 0,741 | 0,679 |
| B4ng | 0,900 | 0,688 | 0,654 | 0,474 |
| B4 | 0,900 | 0,688 | 0,571 | 0,538 |

## Bảng 1'. Từ chối đúng (out_of_scope, 24 câu)

| Cấu hình | Từ chối đúng |
| --- | --- |
| B0 | 0,917 |
| B1 | 1,000 |
| B2 | 1,000 |
| B3hyb | 1,000 |
| B3 | 1,000 |
| B4rr | 1,000 |
| B4ng | 1,000 |
| B4 | 1,000 |

\* Cận dưới tự động: chỉ tính trích dẫn trỏ đúng `evidence_ids`. \*\* Kiểm tay 30 câu B4 (manual30): trích dẫn đúng 24/30 = 0,800.
Mục tiêu B4 đề xuất 07/11, GVHD xác nhận 14/11 (decision-log).
Ragas (judge j1, `results/ragas/`): chỉ chấm câu answerable không bị từ chối (số câu: cột `n_ragas_j1` trong CSV);
B0 không có ngữ cảnh nên không có faithfulness. Hiệu chỉnh judge với 30 câu chấm tay: `docs/results_w8.md`.
Ragas bổ sung (judge j1x = j1 + embedding `gemini-embedding-001`, `eval/ragas_extra.py`): answer relevancy trên câu
answerable không bị từ chối (cột `n_rel_j1x`); context precision/recall trên mọi câu answerable (96, kể cả bị từ
chối). B4rr/B4ng/B4 cùng contexts từng câu nên chung một điểm context. Chưa hiệu chỉnh bằng nhãn tay.

## Bảng 2. Đóng góp từng bước (test, dòng all; trên 96 câu answerable: 0,010 ≈ 1 câu)

| Bước | So sánh | R@1 | R@5 | MRR | Từ chối nhầm | Có trích dẫn | Khớp số | Faithfulness (j1) | Ans. corr. (j1) | Ans. rel. (j1x) | Ctx prec. (j1x) | Ctx recall (j1x) | p95 (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Chunk cấu trúc (RQ1) | B1 → B2 | +0,177 | +0,104 | +0,129 | −0,115 | +0,179 | +0,204 | +0,126 | +0,155 | +0,012 | +0,222 | +0,198 | +0,01 |
| Hybrid | B2 → B3hyb | +0,010 | +0,021 | +0,020 | −0,010 | −0,150 | +0,007 | −0,013 | −0,040 | +0,008 | +0,008 | +0,017 | −0,24 |
| Query processor | B3hyb → B3 | +0,010 | +0,010 | +0,007 | −0,042 | −0,021 | +0,028 | +0,028 | −0,016 | −0,004 | +0,011 | +0,031 | −0,06 |
| Rerank | B3 → B4rr | +0,156 | −0,010 | +0,097 | +0,010 | −0,007 | +0,028 | −0,027 | +0,029 | +0,063 | +0,065 | −0,002 | +1,80 |
| Prompt rag_v3 | B4rr → B4ng | 0 | 0 | 0 | −0,062 | +0,577 | −0,070 | +0,027 | +0,024 | −0,013 | 0 | 0 | −0,10 |
| Ngưỡng 0,90 | B4ng → B4 | 0 | 0 | 0 | +0,031 | +0,011 | −0,008 | +0,003 | −0,015 | +0,030 | 0 | 0 | −0,31 |
| Tổng | B2 → B4 | +0,177 | +0,021 | +0,124 | −0,073 | +0,409 | −0,015 | +0,019 | −0,017 | +0,084 | +0,084 | +0,047 | +1,09 |

Bảng 2' cho biết bước nào có ý nghĩa thống kê; chênh lệch 1–2 câu không đủ để kết luận.

## Bảng 2'. Kiểm định McNemar theo cặp câu (v1.1; Holm hiệu chỉnh trong từng metric qua 6 bước; dòng B2 → B4 không hiệu chỉnh)

| metric | A → B | n | A | B | chỉ A | chỉ B | p | p Holm | ý nghĩa |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hit1 | B1 → B2 | 96 | 0,427 | 0,604 | 9 | 26 | 0,0060 | 0,03 | có |
| hit1 | B2 → B3hyb | 96 | 0,604 | 0,615 | 4 | 5 | 1,0000 | 1,0 |  |
| hit1 | B3hyb → B3 | 96 | 0,615 | 0,625 | 2 | 3 | 1,0000 | 1,0 |  |
| hit1 | B3 → B4rr | 96 | 0,625 | 0,781 | 2 | 17 | 0,0007 | 0,0042 | có |
| hit1 | B4rr → B4ng | 96 | 0,781 | 0,781 | 0 | 0 | 1,0000 | 1,0 |  |
| hit1 | B4ng → B4 | 96 | 0,781 | 0,781 | 0 | 0 | 1,0000 | 1,0 |  |
| hit5 | B1 → B2 | 96 | 0,771 | 0,875 | 4 | 14 | 0,0309 | 0,1854 |  |
| hit5 | B2 → B3hyb | 96 | 0,875 | 0,896 | 2 | 4 | 0,6875 | 1,0 |  |
| hit5 | B3hyb → B3 | 96 | 0,896 | 0,906 | 0 | 1 | 1,0000 | 1,0 |  |
| hit5 | B3 → B4rr | 96 | 0,906 | 0,896 | 5 | 4 | 1,0000 | 1,0 |  |
| hit5 | B4rr → B4ng | 96 | 0,896 | 0,896 | 0 | 0 | 1,0000 | 1,0 |  |
| hit5 | B4ng → B4 | 96 | 0,896 | 0,896 | 0 | 0 | 1,0000 | 1,0 |  |
| false_refusal | B1 → B2 | 96 | 0,323 | 0,208 | 16 | 5 | 0,0266 | 0,1596 |  |
| false_refusal | B2 → B3hyb | 96 | 0,208 | 0,198 | 6 | 5 | 1,0000 | 1,0 |  |
| false_refusal | B3hyb → B3 | 96 | 0,198 | 0,156 | 4 | 0 | 0,1250 | 0,547 |  |
| false_refusal | B3 → B4rr | 96 | 0,156 | 0,167 | 3 | 4 | 1,0000 | 1,0 |  |
| false_refusal | B4rr → B4ng | 96 | 0,167 | 0,104 | 8 | 2 | 0,1094 | 0,547 |  |
| false_refusal | B4ng → B4 | 96 | 0,104 | 0,135 | 1 | 4 | 0,3750 | 1,0 |  |
| refusal_ok | B1 → B2 | 24 | 1,000 | 1,000 | 0 | 0 | 1,0000 | 1,0 |  |
| refusal_ok | B2 → B3hyb | 24 | 1,000 | 1,000 | 0 | 0 | 1,0000 | 1,0 |  |
| refusal_ok | B3hyb → B3 | 24 | 1,000 | 1,000 | 0 | 0 | 1,0000 | 1,0 |  |
| refusal_ok | B3 → B4rr | 24 | 1,000 | 1,000 | 0 | 0 | 1,0000 | 1,0 |  |
| refusal_ok | B4rr → B4ng | 24 | 1,000 | 1,000 | 0 | 0 | 1,0000 | 1,0 |  |
| refusal_ok | B4ng → B4 | 24 | 1,000 | 1,000 | 0 | 0 | 1,0000 | 1,0 |  |
| num_all | B1 → B2 | 63 | 0,381 | 0,587 | 3 | 16 | 0,0044 | 0,0264 | có |
| num_all | B2 → B3hyb | 63 | 0,587 | 0,587 | 7 | 7 | 1,0000 | 1,0 |  |
| num_all | B3hyb → B3 | 63 | 0,587 | 0,619 | 1 | 3 | 0,6250 | 1,0 |  |
| num_all | B3 → B4rr | 63 | 0,619 | 0,635 | 4 | 5 | 1,0000 | 1,0 |  |
| num_all | B4rr → B4ng | 63 | 0,635 | 0,508 | 9 | 1 | 0,0215 | 0,1075 |  |
| num_all | B4ng → B4 | 63 | 0,508 | 0,508 | 3 | 3 | 1,0000 | 1,0 |  |
| hit1 | B2 → B4 | 96 | 0,604 | 0,781 | 2 | 19 | 0,0002 |  | có |
| hit5 | B2 → B4 | 96 | 0,875 | 0,896 | 3 | 5 | 0,7266 |  |  |
| false_refusal | B2 → B4 | 96 | 0,208 | 0,135 | 13 | 6 | 0,1671 |  |  |
| refusal_ok | B2 → B4 | 24 | 1,000 | 1,000 | 0 | 0 | 1,0000 |  |  |
| num_all | B2 → B4 | 63 | 0,587 | 0,508 | 8 | 3 | 0,2266 |  |  |

Nguồn: `eval/mcnemar.py --benchmark benchmark/benchmark_v1.1.jsonl` (`results/review/mcnemar_v1.1_test.csv`); bản v1: `results/archive_v1/mcnemar_v1_test_20261109.csv`. "Chỉ A / chỉ B": số câu chỉ cấu hình A / chỉ B đạt; num_all: câu có số trong đáp án chuẩn (n = 63) và nêu đủ số.
MRR, Wilcoxon theo cặp câu (`eval/paired_tests.py`): B1 → B2 p 0,0024; B3 → B4rr p 0,0017.

## Đọc nhanh

1. Bước lớn nhất về truy xuất là chunk theo cấu trúc (RQ1: Recall@5 +0,104, MRR +0,129); sau Holm có ý nghĩa ở Hit@1 (p Holm 0,03) và khớp đủ số (0,0264), Recall@5 thì không (0,1854).
2. Rerank đóng góp cho thứ hạng (Recall@1 +0,156, p Holm 0,0042; MRR +0,097) nhưng không tìm thêm evidence: Recall@5 −0,010, scenario 0,833 → 0,708.
3. Prompt rag_v3 (trích dẫn [n]): có trích dẫn 0,400 → 0,977, từ chối nhầm −0,062; đổi lại khớp đủ số giảm (chỉ B4rr 9 câu, chỉ B4ng 1 câu; p 0,0215, Holm 0,1075).
4. Ngưỡng 0,90 không thêm từ chối đúng trên test (đã 1,000 từ B1) mà tăng từ chối nhầm 3 câu (p Holm 1,0); lợi ích chỉ ở độ trễ, giờ GPU và hedge (0,046 → 0,012, chưa kiểm định).
5. Hybrid, query processor, prompt rag_v3 và ngưỡng 0,90 không phân biệt được với n = 96 (bảng 2'); câu out_of_scope được từ chối đúng 100% ở mọi cấu hình có RAG nên RQ3 chưa phân biệt được.
6. Nhóm khó nhất xuyên suốt là scenario: Recall@5 tối đa 0,833, từ chối nhầm B4 0,292, khớp số B4 0,538.
7. B4 đạt 5/8 mục tiêu (MRR 0,838; Từ chối đúng 1,000; Hedge 0,012; Có trích dẫn 0,988; p95 (s) 5,74); chưa đạt: R@5 0,896; Từ chối nhầm 0,135; trích dẫn đúng (kiểm tay) 0,800.
8. Ragas (j1): B4 faithfulness 0,741, answer correctness 0,688; B0 answer correctness 0,113.
9. Ragas bổ sung (j1x): context recall B1 0,684 → B2 0,882 → B4 0,929 (cùng chiều Recall@5); answer relevancy B4 0,930, tỷ lệ noncommittal 0,036. Kiểm định: `docs/results_w8.md` mục 7.
