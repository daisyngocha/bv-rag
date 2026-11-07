# Kết quả baseline B0–B2 (tuần 4)

Benchmark v1 (`benchmark/benchmark_v1.jsonl`), dữ liệu `processed/v1` (manifest `data/manifests/v1.json`), Colab L4,
Qwen2.5 7B q4 (num_ctx 8192, seed 42), code commit `1110315`, metric tính bằng `eval/metrics.py` (commit `9115a9b`).
Mọi run dưới đây được `eval.metrics` đánh dấu "chính thức". Định nghĩa metric: docstring `eval/metrics.py`.

| Run | Split | n |
| --- | --- | --- |
| `B0_v1_test_20261107-0904`, `B1_v1_test_20261107-0904`, `B2_v1_test_20261107-0904` | test | 120 (96 answerable, 24 out_of_scope) |
| `B{0,1,2}_v1_dev_20261107-0832_r{0,1,2}` | dev | 30 (24 answerable), 3 lần, seed 42/43/44 |

CSV: `results/B{0,1,2}_v1_test_20261107.csv`, `results/B{0,1,2}_v1_dev_20261107_r{0,1,2}.csv`,
độ nhạy ngưỡng căn chỉnh B1: `results/sens_0.5/B1_v1_test_20261107.csv`.
Các run `*_20261107-0814_*` bị loại (num_ctx 4096, tràn ngữ cảnh; decision-log 07/11).

## Bảng 1. Test, dòng all

| Cấu hình | Recall@1 | Recall@5 | full_R@5 | MRR | Từ chối đúng | Từ chối nhầm | Hedge | Có trích dẫn | Trích dẫn đúng* | Khớp số | p95 (s) | Giờ GPU/1.000 câu |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B0 | – | – | – | – | 0,917 | 0,823 | 0,059 | – | – | 0,034 | 1,12 | 0,14 |
| B1 (ngưỡng 0,3) | 0,406 | 0,740 | 0,625 | 0,564 | 1,000 | 0,323 | 0,108 | 0,400 | 0,628 | 0,472 | 4,64 | 0,76 |
| B1 (ngưỡng 0,5) | 0,375 | 0,719 | 0,615 | 0,527 | 1,000 | 0,323 | 0,108 | 0,400 | 0,609 | 0,472 | 4,64 | 0,76 |
| B2 | 0,604 | 0,865 | 0,792 | 0,709 | 1,000 | 0,208 | 0,132 | 0,579 | 0,761 | 0,675 | 4,65 | 0,66 |

\* Cận dưới: chỉ tính trích dẫn trỏ đúng `evidence_ids`, không tính chunk khác có chứa đáp án.

## Bảng 2. Test, Recall@5 và từ chối nhầm theo nhóm

| Nhóm (24 câu) | B1 R@5 | B2 R@5 | B1 full_R@5 | B2 full_R@5 | B0 từ chối nhầm | B1 từ chối nhầm | B2 từ chối nhầm | B2 khớp số |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| lookup | 0,833 | 0,833 | 0,833 | 0,833 | 0,833 | 0,208 | 0,125 | 0,900 |
| table | 0,833 | 1,000 | 0,833 | 1,000 | 0,542 | 0,167 | 0,000 | 0,729 |
| compare | 0,708 | 0,917 | 0,250 | 0,625 | 0,958 | 0,500 | 0,208 | 0,660 |
| scenario | 0,583 | 0,708 | 0,583 | 0,708 | 0,958 | 0,417 | 0,500 | 0,423 |
| out_of_scope | – | – | – | – | từ chối đúng 0,917 | 1,000 | 1,000 | – |

## Bảng 3. Dev, dao động giữa 3 lần chạy (mean ± sd)

| Cấu hình | Recall@5 | MRR | Từ chối đúng | Từ chối nhầm | Hedge | Có trích dẫn | Khớp số |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B0 | – | – | 1,000 ± 0,000 | 0,806 ± 0,024 | 0,217 ± 0,029 | – | 0,038 ± 0,000 |
| B1 | 0,958 ± 0,000 | 0,798 ± 0,000 | 1,000 ± 0,000 | 0,417 ± 0,042 | 0,022 ± 0,039 | 0,307 ± 0,067 | 0,487 ± 0,044 |
| B2 | 0,958 ± 0,000 | 0,813 ± 0,000 | 0,944 ± 0,096 | 0,208 ± 0,000 | 0,158 ± 0,000 | 0,386 ± 0,030 | 0,703 ± 0,044 |

p95 dev không dùng: lần lặp r1, r2 dùng lại KV cache của prompt r0.

## Nhận định

1. RQ1 (chunk cấu trúc + bảng Markdown so với chunk cố định 512): trên test, B2 hơn B1 ở Recall@5 +0,125
   (0,740 → 0,865), Recall@1 +0,198, MRR +0,145, full_recall@5 +0,167. Chênh lệch giữ nguyên chiều khi chấm B1 ở
   ngưỡng căn chỉnh 0,5 (B1 Recall@5 0,719); ngưỡng chính 0,3 đã dễ dãi với B1. Không cải thiện ở lookup (0,833 cả hai);
   cải thiện ở table (+0,167, B2 đạt 1,000), compare (+0,209; full_recall +0,375) và scenario (+0,125).
   Chưa kiểm định thống kê (McNemar theo cặp câu): làm ở tuần 8 cùng phân tích lỗi.
2. Phía sinh: B2 giảm từ chối nhầm 0,323 → 0,208, tăng khớp số 0,472 → 0,675, tỷ lệ có trích dẫn 0,400 → 0,579.
   Một phần do prompt B2 ngắn hơn (trung vị 2.121 so với 3.143 token Qwen) chứ không chỉ do truy xuất tốt hơn;
   báo cáo nêu yếu tố này.
3. Dev không đại diện tốt cho test ở truy xuất: dev B1 = B2 = 0,958 Recall@5, test 0,740 / 0,865. Dev chỉ 24 câu
   answerable; tinh chỉnh ngưỡng trên dev ở tuần 5–6 phải xem cả chiều chênh lệch, không chỉ số tuyệt đối.
4. Điểm yếu lớn nhất sau truy xuất: từ chối nhầm (B2 0,208; scenario 0,500), câu đã trả lời nhưng chèn câu từ chối
   (compare 0,421), trích dẫn thiếu (42% câu trả lời không có trích dẫn). Đây là việc của prompt và ngưỡng ở B4.
5. Từ chối đúng của B1, B2 = 1,000 vì prompt rag_v1 dễ từ chối; cần đọc cùng từ chối nhầm. Trên dev có ca
   không từ chối câu hỏi luật (v1-0066, B2 r0): model trả lời bằng chunk sản phẩm cùng chủ đề.
6. Chi phí: B2 0,66 giờ L4 cho 1.000 câu, p95 4,65 s; B4 thêm rerank 30 cặp (~0,56 s theo smoke test).
