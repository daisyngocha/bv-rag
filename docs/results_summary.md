# Bảng tổng kết quả B0–B4 (test)

Benchmark v1 test (120 câu: 96 answerable, 24 out_of_scope, 24 câu/nhóm), dữ liệu `processed/v1`, Colab L4,
Qwen2.5 7B q4 (num_ctx 8192, seed 42). Mọi run là run chính thức của `eval.metrics`; một lần chạy test cho mỗi cấu hình.
Bảng sinh từ `results/*.csv` bằng `PYTHONPATH=. python -m eval.summary` (danh sách run trong `eval/summary.py`).
Chi tiết từng bước: `docs/results_w4_baseline.md` (B0–B2), `docs/results_w5_b3.md` (B3), `docs/results_w6_b4.md` (B4).

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
| B1 | dense, chunk cố định 512 | 0,406 | 0,740 | 0,625 | 0,564 | 1,000 | 0,323 | 0,108 | 0,400 | 0,628 | 0,472 | 4,64 | 0,76 |
| B2 | chunk cấu trúc + bảng Markdown | 0,604 | 0,865 | 0,792 | 0,709 | 1,000 | 0,208 | 0,132 | 0,579 | 0,761 | 0,675 | 4,65 | 0,66 |
| B3hyb | + hybrid RRF (ablation) | 0,615 | 0,885 | 0,823 | 0,731 | 1,000 | 0,198 | 0,104 | 0,429 | 0,677 | 0,682 | 4,41 | 0,65 |
| B3 | + query processor | 0,635 | 0,896 | 0,854 | 0,746 | 1,000 | 0,156 | 0,123 | 0,407 | 0,793 | 0,710 | 4,35 | 0,67 |
| B4rr | + rerank (ablation, rag_v1) | 0,771 | 0,906 | 0,875 | 0,835 | 1,000 | 0,167 | 0,062 | 0,400 | 0,732 | 0,739 | 6,15 | 0,96 |
| B4ng | + prompt rag_v3 (ablation, không chặn) | 0,771 | 0,906 | 0,875 | 0,835 | 1,000 | 0,104 | 0,046 | 0,977 | 0,680 | 0,669 | 6,05 | 0,89 |
| B4 | + ngưỡng từ chối 0,90 | 0,771 | 0,906 | 0,875 | 0,835 | 1,000 | 0,135 | 0,012 | 0,988 | 0,709 | 0,661 | 5,74 | 0,80 |
| Mục tiêu B4 |  |  | ≥ 0,92 |  | ≥ 0,80 | ≥ 0,90 | ≤ 0,10 | ≤ 0,05 | ≥ 0,90 | ≥ 0,85** |  | ≤ 6 |  |

## Bảng 1'. Recall@5 theo nhóm (24 câu/nhóm)

| Cấu hình | lookup | table | compare | scenario |
| --- | --- | --- | --- | --- |
| B0 | – | – | – | – |
| B1 | 0,833 | 0,833 | 0,708 | 0,583 |
| B2 | 0,833 | 1,000 | 0,917 | 0,708 |
| B3hyb | 0,875 | 0,917 | 0,917 | 0,833 |
| B3 | 0,875 | 0,958 | 0,917 | 0,833 |
| B4rr | 1,000 | 1,000 | 0,917 | 0,708 |
| B4ng | 1,000 | 1,000 | 0,917 | 0,708 |
| B4 | 1,000 | 1,000 | 0,917 | 0,708 |

## Bảng 1'. full_recall@5 theo nhóm (24 câu/nhóm)

| Cấu hình | lookup | table | compare | scenario |
| --- | --- | --- | --- | --- |
| B0 | – | – | – | – |
| B1 | 0,833 | 0,833 | 0,250 | 0,583 |
| B2 | 0,833 | 1,000 | 0,625 | 0,708 |
| B3hyb | 0,875 | 0,917 | 0,667 | 0,833 |
| B3 | 0,875 | 0,958 | 0,750 | 0,833 |
| B4rr | 1,000 | 1,000 | 0,792 | 0,708 |
| B4ng | 1,000 | 1,000 | 0,792 | 0,708 |
| B4 | 1,000 | 1,000 | 0,792 | 0,708 |

## Bảng 1'. MRR theo nhóm (24 câu/nhóm)

| Cấu hình | lookup | table | compare | scenario |
| --- | --- | --- | --- | --- |
| B0 | – | – | – | – |
| B1 | 0,636 | 0,562 | 0,623 | 0,437 |
| B2 | 0,664 | 0,774 | 0,761 | 0,637 |
| B3hyb | 0,703 | 0,755 | 0,789 | 0,675 |
| B3 | 0,711 | 0,756 | 0,833 | 0,683 |
| B4rr | 0,931 | 0,866 | 0,834 | 0,707 |
| B4ng | 0,931 | 0,866 | 0,834 | 0,707 |
| B4 | 0,931 | 0,866 | 0,834 | 0,707 |

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

## Từ chối đúng (out_of_scope, 24 câu)

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

\* Cận dưới tự động: chỉ tính trích dẫn trỏ đúng `evidence_ids`. \*\* Mục tiêu đo bằng kiểm tay 30 câu (chưa làm).
Mục tiêu B4 là bản đề xuất 07/11, chờ GVHD (decision-log).

## Bảng 2. Đóng góp từng bước (test, dòng all; Recall@5 trên 96 câu answerable: 0,010 ≈ 1 câu)

| Bước | So sánh | R@1 | R@5 | MRR | Từ chối nhầm | Có trích dẫn | Khớp số | p95 (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Chunk cấu trúc (RQ1) | B1 → B2 | +0,198 | +0,125 | +0,144 | −0,115 | +0,179 | +0,204 | +0,01 |
| Hybrid | B2 → B3hyb | +0,010 | +0,021 | +0,022 | −0,010 | −0,150 | +0,007 | −0,24 |
| Query processor | B3hyb → B3 | +0,021 | +0,010 | +0,015 | −0,042 | −0,021 | +0,028 | −0,06 |
| Rerank | B3 → B4rr | +0,135 | +0,010 | +0,089 | +0,010 | −0,007 | +0,028 | +1,80 |
| Prompt rag_v3 | B4rr → B4ng | 0 | 0 | 0 | −0,062 | +0,577 | −0,070 | −0,10 |
| Ngưỡng 0,90 | B4ng → B4 | 0 | 0 | 0 | +0,031 | +0,011 | −0,008 | −0,31 |
| Tổng | B2 → B4 | +0,167 | +0,042 | +0,126 | −0,073 | +0,409 | −0,015 | +1,09 |

## Bảng 2'. Kiểm định McNemar theo cặp câu (test; exact binomial, Holm trong từng metric qua 6 bước liền kề)

`eval/mcnemar.py`, CSV `results/mcnemar_v1_test_20261109.csv`. "Chỉ A / chỉ B": số câu chỉ cấu hình A / chỉ B đạt.
Hit@k và từ chối nhầm trên 96 câu answerable; khớp đủ số trên 63 câu answerable có số trong đáp án chuẩn.

| Bước | Metric | A → B | Chỉ A / chỉ B | p | p Holm |
| --- | --- | --- | --- | --- | --- |
| Chunk cấu trúc B1 → B2 | Hit@1 | 0,406 → 0,604 | 9 / 28 | 0,003 | **0,016** |
| | Hit@5 | 0,740 → 0,865 | 4 / 16 | 0,012 | 0,071 |
| | Từ chối nhầm | 0,323 → 0,208 | 16 / 5 | 0,027 | 0,160 |
| | Khớp đủ số | 0,381 → 0,587 | 3 / 16 | 0,004 | **0,026** |
| Hybrid B2 → B3hyb | Hit@1 / Hit@5 | +0,010 / +0,021 | 4/5, 2/4 | 1,000 / 0,688 | 1,0 |
| Query processor B3hyb → B3 | Hit@5 / từ chối nhầm | +0,010 / −0,042 | 0/1, 4/0 | 1,000 / 0,125 | 1,0 / 0,547 |
| Rerank B3 → B4rr | Hit@1 | 0,635 → 0,771 | 3 / 16 | 0,004 | **0,022** |
| | Hit@5 | 0,896 → 0,906 | 4 / 5 | 1,000 | 1,0 |
| Prompt rag_v3 B4rr → B4ng | Từ chối nhầm | 0,167 → 0,104 | 8 / 2 | 0,109 | 0,547 |
| | Khớp đủ số | 0,635 → 0,508 | 9 / 1 | 0,022 | 0,108 |
| Ngưỡng 0,90 B4ng → B4 | Từ chối nhầm | 0,104 → 0,135 | 1 / 4 | 0,375 | 1,0 |
| Tổng B2 → B4 (ngoài họ Holm) | Hit@1 | 0,604 → 0,771 | 3 / 19 | **< 0,001** | |
| | Hit@5 / từ chối nhầm / khớp đủ số | | 2/6, 13/6, 8/3 | 0,289 / 0,167 / 0,227 | |

Có ý nghĩa ở mức 0,05 sau hiệu chỉnh: chunk cấu trúc (Hit@1, khớp đủ số) và rerank (Hit@1); B2 → B4 về Hit@1.
Không phân biệt được với n = 96: hybrid, query processor, rerank với Hit@5, prompt rag_v3 và ngưỡng 0,90 với từ chối nhầm;
từ chối đúng không khác nhau (1,000 từ B1, chỉ B0 0,917). Prompt rag_v3 làm giảm khớp đủ số (9 / 1, p = 0,022) nhưng
không còn ý nghĩa sau Holm (0,108). Hit@5 B1 → B2 có ý nghĩa nếu kiểm riêng (p = 0,012) nhưng không sau Holm.

## Đọc nhanh

1. Bước lớn nhất về truy xuất là chunk theo cấu trúc (RQ1: Recall@5 +0,125, MRR +0,144); rerank đóng góp nhiều nhất cho
   thứ hạng (Recall@1 +0,135, MRR +0,089) nhưng làm scenario tụt (Recall@5 0,833 → 0,708) nên Recall@5 tổng chỉ +0,010.
2. Bước lớn nhất về sinh là prompt rag_v3 (trích dẫn [n]): có trích dẫn 0,400 → 0,977, từ chối nhầm −0,062; đổi lại
   khớp số giảm 0,070.
3. Ngưỡng 0,90 không thêm từ chối đúng trên test (đã 1,000 từ B1) mà chặn nhầm 4 câu compare; lợi ích chỉ ở độ trễ và
   giờ GPU.
4. Nhóm khó nhất xuyên suốt là scenario: Recall@5 tối đa 0,833 (B3), từ chối nhầm thấp nhất 0,292 (B4), khớp số ≤ 0,679.
5. B4 đạt 5/9 mục tiêu đo tự động được (MRR, từ chối đúng, có trích dẫn, hedge, p95; trích dẫn đúng chưa kiểm tay);
   chưa đạt Recall@5 tổng và scenario, compare full_recall@5 (0,792, thiếu 1 câu), từ chối nhầm (0,135).
