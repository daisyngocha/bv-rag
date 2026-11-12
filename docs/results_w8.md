# Tuần 8: hiệu chỉnh judge Ragas, benchmark v1.1, kiểm định, phân tích lỗi

Tập test, benchmark v1.1 (`benchmark/CHANGELOG.md`), 8 run chính thức trong `configs/test_runs_official.txt`
(B0–B2 `-0904`, B3/B3hyb `-1020`, B4rr/B4ng/B4 `-1335`, ngày 07/11, Colab L4). Bảng tổng: `docs/results_summary.md`.
Mục đánh dấu **[CHỜ]** điền sau khi chấm Ragas toàn bộ test xong.

## 1. Bộ chấm tay manual30

- Nguồn: `results/review/manual30_B4_v1_test_20261107-1335.{xlsx,csv}`. Gồm 30 câu trả lời của
  `B4_v1_test_20261107-1335` (lookup 7, table 7, compare 8, scenario 8; chọn bằng `scripts/make_manual30.py`, seed 42),
  cộng 4 câu compare bị ngưỡng chặn ở B4, chấm câu trả lời của `B4ng_v1_test_20261107-1335` (v1-0054, 0119, 0120, 0125).
  Tất cả thuộc split test, không có câu out_of_scope.
- Thang 1–5 cho đúng (correct) và trung thực với ngữ cảnh (faithful), kèm cờ trích dẫn đúng (cite_ok) và mã lỗi chính.
  Điểm correct chấm theo đáp án chuẩn đã sửa ở v1.1.
- Phân bố điểm (30 câu chính): faithful {1: 2, 3: 3, 4: 5, 5: 20}; correct {1: 4, 2: 2, 3: 2, 4: 5, 5: 17}.
  Faithful dồn về 4–5 (83%) nên tương quan faithfulness kém tin cậy hơn correctness.
- Quy trình: bảng chấm có cột đề xuất điểm (`dx_*`) do Claude soạn; điểm chốt trùng 100% với đề xuất. Judge Claude không
  tương quan với điểm tay cao hơn Gemini (mục 2), nên không thấy dấu hiệu thiên lệch cùng họ model.
  **[Tùy chọn]** chấm mù lại 10 câu, báo weighted kappa.
- Trích dẫn đúng kiểm tay: 24/30 = 0,800 (cả 34 câu: 0,794). Mục tiêu 0,85 chưa đạt.

## 2. Hiệu chỉnh judge Ragas

Cấu hình chung: Ragas 0.4.3 (LangChain pin 0.3 trong `requirements/judge.txt`), Faithfulness và AnswerCorrectness với
`weights=[1, 0]` (chỉ phần factual, không cần embedding), bỏ ký hiệu `[n]` khỏi câu trả lời trước khi chấm, bỏ câu
out_of_scope và câu bị từ chối. Mã: `eval/ragas_eval.py`, `eval/claude_llm.py`, `eval/calibrate_judge.py`; config
`configs/judge_{j1,j1b,c1,c1b,c2,c2b}.yaml`; điểm từng câu `results/ragas/*__{judge}.csv`.

| Judge | Model | ρ faithfulness (n = 30) | ρ correctness (n = 30) | Chấm lặp lại (ρ faith / corr) | Chi phí 34 câu |
| --- | --- | --- | --- | --- | --- |
| j1 | Gemini `gemini-3.8-flash`, temperature 0 | 0,665 [0,38; 0,88] | 0,816 [0,63; 0,92] | 0,902 / 0,969 | 190,7K vào, 162,7K ra |
| c2 | `claude-haiku-5-5`, effort low, không suy nghĩ trước | 0,546 [0,24; 0,80] | 0,751 [0,50; 0,90] | 0,945 / 0,902 | ~$0,07 |
| c1 | `claude-sonnet-5-5`, effort low, between_tools | 0,575 [0,28; 0,82] | 0,684 [0,39; 0,87] | 0,873 / 0,838 | ~$1,37 |

Spearman, CI95 bootstrap 2.000 lần; Kendall tau-b: j1 0,595 / 0,720, c2 0,469 / 0,655, c1 0,504 / 0,591. Thêm 4 câu
B4ng (n = 34): j1 0,670 / 0,764, c2 0,560 / 0,717, c1 0,578 / 0,673. Claude Sonnet/Haiku 5.5 không nhận temperature nên
độ ổn định được đo bằng cách chấm lại lần 2 (MAD c2 0,052 / 0,077; c1 0,053 / 0,101).

Quyết định: j1 là judge chính (ρ cao nhất ở cả hai metric, cận dưới CI trên 0,35, rẻ, khác họ với model sinh Qwen);
c2 là judge phụ để kiểm tra độ vững; bỏ c1 (đắt gấp ~20 lần c2, ρ correctness thấp nhất, chấm lặp kém ổn định hơn).
Các CI chồng lấn nhau: chỉ kết luận j1 cao hơn về điểm ước lượng, không kết luận có ý nghĩa thống kê.

Lệch có hệ thống, lặp lại ở cả ba judge (không tinh chỉnh judge trên test):

1. Faithfulness bị đánh giá thấp ở nhóm scenario (v1-0041, 0110, 0118, 0113, 0048): câu trả lời áp điều khoản vào tình
   huống cụ thể, mệnh đề suy luận không có nguyên văn trong ngữ cảnh.
2. AnswerCorrectness phạt câu trả lời dài hơn đáp án chuẩn (v1-0051, 0119, 0008, 0056, 0125): mệnh đề đúng nhưng thừa
   bị tính FP. Riêng c2 cho v1-0097 (table) faithfulness 0 dù điểm tay 5, nghi đọc sai ngữ cảnh bảng Markdown.

## 3. Benchmark v1.1

Sửa từ manual30 (chi tiết `benchmark/CHANGELOG.md`): đáp án chuẩn v1-0126 (D1) và v1-0113 (bổ sung), evidence 7 câu
(0056, 0113, 0119, 0120, 0124, 0125, 0126). Câu hỏi giữ nguyên nên không chạy lại GPU: metric tính lại từ log bằng
`eval.metrics --bench benchmark/benchmark_v1.1.jsonl`; số v1 lưu ở `results/archive_v1/`.

| Cấu hình | Recall@1 | Recall@5 | full_R@5 | MRR | Trích dẫn đúng* |
| --- | --- | --- | --- | --- | --- |
| B1 | 0,406 → 0,427 (+2 câu) | 0,740 → 0,771 (+3) | 0,625 → 0,646 (+2) | 0,564 → 0,584 | 0,628 |
| B2 | 0,604 | 0,865 → 0,875 (+1) | 0,792 | 0,709 → 0,713 | 0,761 → 0,750 |
| B3hyb | 0,615 | 0,885 → 0,896 (+1) | 0,823 | 0,731 → 0,733 | 0,677 |
| B3 | 0,635 → 0,625 (−1) | 0,896 → 0,906 (+1) | 0,854 → 0,833 (−2) | 0,746 → 0,740 | 0,793 |
| B4rr / B4ng / B4 | 0,771 → 0,781 (+1) | 0,906 → 0,896 (−1) | 0,875 | 0,835 → 0,838 | B4 0,709 → 0,728 |

Khớp số không đổi: tập số trong đáp án chuẩn của 0113 và 0126 giữ nguyên. Theo v1.1, Recall@5 của B4 thấp hơn B3 một
câu (theo v1 là cao hơn một câu), do evidence 0119/0120/0124/0125 chuyển sang chunk bảng quyền lợi.

## 4. Kiểm định theo cặp câu

Bảng 2' trong `docs/results_summary.md` (`eval/mcnemar.py`, McNemar chính xác, Holm trong từng metric qua 6 bước B1→B4,
n = 96 câu answerable; num_all n = 63). MRR kiểm bằng Wilcoxon theo cặp (`eval/paired_tests.py`).

| Bước | Có ý nghĩa sau Holm | Ghi chú |
| --- | --- | --- |
| Chunk cấu trúc B1→B2 (RQ1) | Hit@1 (9 vs 26 câu, Holm 0,030); khớp đủ số (3 vs 16, Holm 0,026) | Hit@5 p 0,031 → Holm 0,19; từ chối nhầm p 0,027 → Holm 0,16; MRR Wilcoxon p 0,0024 |
| Hybrid B2→B3hyb, query processor B3hyb→B3 (RQ2) | không | mọi p ≥ 0,125 |
| Rerank B3→B4rr (RQ2) | Hit@1 (2 vs 17, Holm 0,004) | Hit@5 5 vs 4 (p 1,0); MRR Wilcoxon p 0,0017 |
| Prompt rag_v3 B4rr→B4ng | không | từ chối nhầm 0,167 → 0,104 (p 0,11); khớp đủ số 0,635 → 0,508 (9 vs 1, p 0,022, Holm 0,11) |
| Ngưỡng 0,90 B4ng→B4 (RQ3) | không | từ chối nhầm 0,104 → 0,135 (1 vs 4, p 0,38); từ chối đúng 1,000 ở mọi cấu hình có RAG |

Kết luận:

- RQ1: chunk theo cấu trúc cải thiện thứ hạng và độ đầy đủ số liệu có ý nghĩa; Recall@5 tăng 10 câu nhưng không qua Holm.
- RQ2: reranker cải thiện có ý nghĩa việc đưa chunk đúng lên đầu (Recall@1 +15 câu), không tìm thêm evidence (Recall@5 −1
  câu). Hybrid và query processor không phân biệt được với n = 96.
- RQ3: chưa phân biệt được. Câu out_of_scope đã được từ chối đúng 100% khi chưa có ngưỡng; ngưỡng 0,90 thêm 3 câu từ chối
  nhầm (không có ý nghĩa). Đầu vào ĐA2: bổ sung câu out_of_scope khó hơn (hỏi chi tiết tài liệu không nêu).
- Đánh đổi của prompt rag_v3: giảm từ chối nhầm nhưng làm rơi số liệu; cả chặng B2→B4 Hit@1 tăng (p 0,0002) còn khớp đủ số
  giảm 0,587 → 0,508 (p 0,23). Các câu rơi số: `results/review/rag_v3_num_drop.txt`, đưa vào phân tích lỗi.

## 5. Ragas theo cấu hình **[CHỜ]**

- Chấm toàn bộ 8 run bằng j1 và c2: `results/ragas/*__{j1,c2}.csv`, token ở `*.usage.jsonl`.
- Bảng faithfulness / answer correctness (j1) theo cấu hình và nhóm: `docs/results_summary.md` (bảng 1, bảng 2, ý 8).
- Độ vững theo judge: Kendall tau giữa thứ hạng B0–B4 theo j1 và theo c2: **[CHỜ]**.
- Wilcoxon theo cặp cho Ragas (`eval/paired_tests.py --ragas-judge j1`): **[CHỜ]**.
- Chi phí judge (báo riêng, không tính vào chi phí hệ thống): **[CHỜ]**.

## 6. Phân tích lỗi B4 **[CHỜ]**

`eval/error_sheet.py` → `results/review/error_analysis_B4_v1.1_test.xlsx` (tối đa 40 câu, 1 mã chính mỗi câu: R1, R2, P1,
G1, G2, F1, F2, D1). Đưa thêm: 9 câu nghi lỗi tuần 6, 3 câu scenario tụt do rerank (0050, 0108, 0112), 4 câu compare bị
ngưỡng chặn, các câu rơi số ở rag_v3.

- Phân bố mã lỗi theo nhóm: **[CHỜ]**
- Ví dụ điển hình 3–5 câu mỗi loại lớn: **[CHỜ]**
- Ca từ demo (không tính vào phân bố test): v1-0053 G1, v1-0022 G2, v1-0075 vượt ngưỡng, ca BTB "635 ngày", phản hồi 👎.
- Đề xuất cho ĐA2: **[CHỜ]**
