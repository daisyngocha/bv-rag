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
- Đánh đổi của prompt rag_v3 (HA duyệt 13/11): B4rr → B4ng giảm từ chối nhầm 0,167 → 0,104 (p 0,11), khớp đủ số giảm
  0,635 → 0,508 (9 vs 1 câu, p 0,022, Holm 0,11); cả chặng B2→B4 Hit@1 tăng (p 0,0002), khớp đủ số giảm 0,587 → 0,508 (p 0,23).
  Rà tay 8 câu B4rr đủ số mà B4ng rơi số (`results/review/rag_v3_num_drop.md`): chỉ 3 câu rơi số thật do rag_v3. Hai câu
  compare từ chối nhầm một phần: nói một sản phẩm "không có thông tin" dù đoạn chứa số ở hạng 1 (v1-0133) hoặc hạng 4
  (v1-0149). Câu còn lại (v1-0032) lấy số từ bảng cá nhân thay vì bảng gia đình. Thêm 1 câu đúng nội dung nhưng trích dẫn
  sai (v1-0045). Câu v1-0107 sai kết luận ở cả B4rr nên không do rag_v3. 3 câu còn lại không lỗi: đáp án chuẩn chứa số lấy từ
  câu hỏi hoặc tên sản phẩm, còn câu trả lời ngắn của rag_v3 không nhắc lại. Mức giảm khớp số vì vậy phóng đại phần mất mát
  thật. Giả thuyết ngữ cảnh `<doc so="n">` làm mất mã phân biệt bảng S1/S2 không đủ căn cứ: text chunk luôn có tiêu đề "dành
  cho cá nhân / gia đình", còn mã S1/S2 tự nó không mang nghĩa. Kiểm chắc cần chạy lại trên dev (ĐA2).

## 5. Ragas theo cấu hình

HA duyệt 13/11. Chấm toàn bộ 8 run bằng j1 và c2: điểm từng câu `results/ragas/{run_id}__{j1,c2}.csv`, gộp vào
`results/*_v1.1_test_*.csv` bằng `eval/ragas_summary.py` (cột `faithfulness_{j}`, `answer_correctness_{j}`, `n_ragas_{j}`;
bỏ NaN và câu lỗi; qid chấm lại giữ bản sau). Chỉ chấm câu answerable không bị từ chối, nên n khác nhau giữa các cấu hình.
Đóng góp từng bước theo j1: bảng 2 và ý 8 của `docs/results_summary.md`.

Theo nhóm (j1 / c2; n = số câu chấm, giống nhau ở hai judge):

| Cấu hình | n | Faith. all | lookup | table | compare | scenario | Ans. corr. all | lookup | table | compare | scenario |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| B0 | 17 | – | – | – | – | – | 0,113 / 0,088 | 0,225 / 0,292 | 0,052 / 0,000 | 0,444 / 0,333 | 0,000 / 0,000 |
| B1 | 65 | 0,596 / 0,507 | 0,867 / 0,740 | 0,450 / 0,354 | 0,691 / 0,492 | 0,356 / 0,423 | 0,550 / 0,481 | 0,820 / 0,703 | 0,398 / 0,362 | 0,495 / 0,394 | 0,448 / 0,427 |
| B2 | 76 | 0,722 / 0,642 | 0,897 / 0,754 | 0,729 / 0,547 | 0,750 / 0,746 | 0,359 / 0,473 | 0,705 / 0,615 | 0,876 / 0,770 | 0,715 / 0,616 | 0,641 / 0,545 | 0,485 / 0,449 |
| B3hyb | 77 | 0,710 / 0,648 | 0,947 / 0,787 | 0,717 / 0,568 | 0,661 / 0,689 | 0,386 / 0,509 | 0,665 / 0,565 | 0,877 / 0,739 | 0,667 / 0,567 | 0,527 / 0,453 | 0,505 / 0,431 |
| B3 | 81 | 0,738 / 0,680 | 0,970 / 0,759 | 0,757 / 0,643 | 0,740 / 0,768 | 0,335 / 0,485 | 0,649 / 0,580 | 0,848 / 0,769 | 0,669 / 0,575 | 0,530 / 0,523 | 0,482 / 0,376 |
| B4rr | 80 | 0,711 / 0,632 | 0,921 / 0,732 | 0,667 / 0,530 | 0,700 / 0,755 | 0,389 / 0,397 | 0,678 / 0,575 | 0,849 / 0,676 | 0,604 / 0,555 | 0,589 / 0,517 | 0,661 / 0,525 |
| B4ng | 86 | 0,738 / 0,736 | 0,983 / 0,927 | 0,694 / 0,688 | 0,794 / 0,802 | 0,372 / 0,438 | 0,702 / 0,684 | 0,891 / 0,828 | 0,628 / 0,663 | 0,658 / 0,639 | 0,606 / 0,571 |
| B4 | 83 | 0,741 / 0,749 | 0,948 / 0,971 | 0,708 / 0,677 | 0,850 / 0,793 | 0,385 / 0,500 | 0,688 / 0,654 | 0,889 / 0,858 | 0,647 / 0,625 | 0,599 / 0,576 | 0,572 / 0,504 |

n theo nhóm (lookup/table/compare/scenario): B0 4/11/1/1, B1 19/20/12/14, B2 21/24/19/12, B3hyb 22/23/18/14,
B3 22/24/21/14, B4rr 23/24/22/11, B4ng 23/24/23/16, B4 23/24/19/17. Ô của B0 và nhóm có n nhỏ chỉ để tham khảo.

- Scenario có faithfulness thấp nhất ở mọi cấu hình (j1 0,34–0,39), khớp lệch đã thấy khi hiệu chỉnh (mục 2, ý 1):
  judge không nhận mệnh đề áp điều khoản vào tình huống. Không đọc con số này là tỉ lệ bịa.
- B0 trả lời 17 câu, answer correctness 0,11 (j1): không có RAG thì model gần như không trả lời đúng sản phẩm Bảo Việt.

**Độ vững theo judge.** Kendall tau-b giữa thứ hạng cấu hình theo j1 và theo c2 (dòng all): faithfulness 0,810
(7 cấu hình, không có B0; p 0,011), answer correctness 0,714 (8 cấu hình; p 0,014). Faithfulness: hai judge cùng xếp
B4 > B4ng > B3 ở đầu và B1 cuối, chỉ đổi chỗ B2/B3hyb/B4rr. Answer correctness: j1 xếp B2 đầu (0,705), c2 xếp B4ng >
B4 > B2. c2 chấm thấp hơn j1 ở hầu hết ô (B1–B4rr thấp hơn 0,06–0,10), trừ B4ng/B4 gần bằng. Từ B2 trở đi các cấu hình
chỉ cách nhau 0,01–0,06 nên thứ hạng ở khúc này không ổn định.

**Wilcoxon theo cặp câu** (`eval/paired_tests.py --ragas-judge`, chỉ câu cả hai cấu hình cùng có điểm; j1:
`results/review/paired_tests_v1.1_test.txt`, c2: `results/review/paired_tests_v1.1_test_c2.txt`). Holm tính tay trong từng
metric qua 6 cặp dưới đây (bổ sung, script chưa có).

| Cặp | n | Faith. j1 (A → B; p; Holm) | Ans. corr. j1 | Faith. c2 | Ans. corr. c2 |
| --- | --- | --- | --- | --- | --- |
| B1 → B2 | 60 | 0,610 → 0,718; 0,080; 0,46 | 0,561 → 0,695; 0,032; 0,19 | 0,528 → 0,616; 0,058; 0,23 | 0,488 → 0,605; 0,064; 0,26 |
| B2 → B3 | 74 | 0,722 → 0,754; 0,36; 0,84 | 0,701 → 0,654; 0,098; 0,49 | 0,643 → 0,695; 0,062; 0,23 | 0,614 → 0,582; 0,43; 0,86 |
| B3 → B4rr | 77 | 0,752 → 0,712; 0,28; 0,84 | 0,671 → 0,685; 0,58; 0,75 | 0,692 → 0,630; 0,11; 0,23 | 0,600 → 0,582; 0,51; 0,86 |
| B4rr → B4ng | 78 | 0,717 → 0,766; 0,076; 0,46 | 0,673 → 0,702; 0,19; 0,75 | 0,637 → 0,765; **0,0001; 0,0006** | 0,574 → 0,685; **0,0001; 0,0006** |
| B4ng → B4 | 82 | 0,728 → 0,746; 0,16; 0,64 | 0,700 → 0,688; 0,24; 0,75 | 0,726 → 0,752; 0,16; 0,23 | 0,679 → 0,655; 0,20; 0,59 |
| B3 → B4 | 73 | 0,746 → 0,766; 0,54; 0,84 | 0,671 → 0,699; 0,37; 0,75 | 0,683 → 0,766; 0,044; 0,22 | 0,598 → 0,670; 0,036; 0,18 |

- Theo j1 (judge chính) không bước nào có ý nghĩa sau Holm; B1 → B2 answer correctness p 0,032 cùng chiều với RQ1 nhưng
  không qua Holm (0,19).
- Hai judge bất đồng ở bước prompt rag_v3 (B4rr → B4ng): c2 thấy tăng mạnh ở cả hai metric (16 vs 44 câu, 17 vs 49 câu,
  Holm 0,0006), j1 chỉ tăng nhẹ (p 0,076 / 0,19). Kết luận về rag_v3 vì vậy phụ thuộc judge; theo quy ước j1 là chính,
  ghi "không phân biệt được". Nghi c2 nhạy với văn phong rag_v3 (câu ngắn, bám ngữ cảnh), cần xem ở mục 6 trước khi viết
  vào báo cáo.
- Rerank cải thiện MRR có ý nghĩa (mục 4) nhưng Ragas không tăng ở cả hai judge: đưa chunk đúng lên đầu không làm câu trả
  lời tốt hơn khi chunk đó đã nằm trong top-5.

**Chi phí judge** (báo riêng, không tính vào chi phí hệ thống; chưa có đơn giá trong repo nên chỉ báo token, từ
`results/ragas/{run_id}__{j1,c2}.usage.jsonl` của 8 run chính thức):

| Judge | Câu có điểm | Câu có log token | Token vào | Token ra | Trung bình/câu (vào / ra) |
| --- | --- | --- | --- | --- | --- |
| j1 (`gemini-3.8-flash`) | 565 | 494 | 2.877.143 | 2.139.465 | 5.824 / 4.331 |
| c2 (`claude-haiku-5-5`) | 566 lượt (565 câu + 1 chấm lại) | 566 | 5.408.188 | 1.248.635 | 9.555 / 2.206 |

- j1 thiếu log token 71 câu: 34 câu hiệu chỉnh (B4 30, B4ng 4) đã báo ở mục 2 (190,7K vào, 162,7K ra); 37 câu của B2
  (CSV 76 câu, log 39) không có log, nghi do lần chấm đầu bị ngắt (`eval/ragas_eval.py` ghi điểm từng câu nhưng chỉ ghi
  token khi chạy xong). Cộng mục 2: j1 ≈ 3,07M vào, 2,30M ra cho 528/565 câu.
- Token ra của j1 cao hơn c2 vì đã gồm thought tokens của Gemini; c2 tốn token vào nhiều hơn (5 lượt gọi/câu).

## 6. Phân tích lỗi B4 **[CHỜ]**

`eval/error_sheet.py` → `results/review/error_analysis_B4_v1.1_test.xlsx` (tối đa 40 câu, 1 mã chính mỗi câu: R1, R2, P1,
G1, G2, F1, F2, D1). Đưa thêm: 9 câu nghi lỗi tuần 6, 3 câu scenario tụt do rerank (0050, 0108, 0112), 4 câu compare bị
ngưỡng chặn, các câu rơi số ở rag_v3.

- Phân bố mã lỗi theo nhóm: **[CHỜ]**
- Ví dụ điển hình 3–5 câu mỗi loại lớn: **[CHỜ]**
- Ca từ demo (không tính vào phân bố test): v1-0053 G1, v1-0022 G2, v1-0075 vượt ngưỡng, ca BTB "635 ngày", phản hồi 👎.
- Đề xuất cho ĐA2: **[CHỜ]**
