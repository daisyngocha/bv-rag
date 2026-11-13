# Việc còn lại tuần 8 (giao cho Claude Code, 13/11)

Đọc trước: `CLAUDE.md`, `docs/results_w8.md`, `docs/results_summary.md`, `benchmark/CHANGELOG.md`.
Làm từng việc theo thứ tự. Sau mỗi việc: tóm tắt kết quả, đề xuất commit (liệt kê file), **dừng chờ tôi duyệt**.
Gặp lỗi hoặc số bất thường thì dừng và hỏi, không tự sửa dữ liệu hay benchmark.

1. Kiểm tra `results/ragas/*__j1.csv` và `*__c2.csv` của 8 run trong `configs/test_runs_official.txt`: số câu so với số câu
   answerable không bị từ chối của run, cột `error`, NaN (B0 không có faithfulness là đúng). Báo bảng kết quả.
2. `PYTHONPATH=. python -m eval.ragas_summary --judge j1 --bench benchmark/benchmark_v1.1.jsonl $(ls results/*_v1.1_test_*.csv)`,
   tương tự `--judge c2`; rồi `PYTHONPATH=. python scripts/build_results_summary.py`. Tính Kendall tau giữa thứ hạng các cấu hình
   theo j1 và theo c2 (faithfulness, answer_correctness, dòng all).
3. `PYTHONPATH=. .venv-judge/bin/python -m eval.paired_tests results/review/per_question_v1.1_test.csv B1:B2 B2:B3 B3:B4rr B4rr:B4ng B4ng:B4 B3:B4 --ragas-judge j1 > results/review/paired_tests_v1.1_test.txt`
4. Điền mục 5 của `docs/results_w8.md`: Ragas theo cấu hình và nhóm (dẫn bảng trong results_summary), độ vững j1/c2,
   Wilcoxon cho Ragas, chi phí judge (token từ `results/ragas/*.usage.jsonl`, chỉ báo token nếu chưa có đơn giá).
5. `results/review/rag_v3_num_drop.md` (8 câu B4rr đủ số mà B4ng rơi số): mỗi câu soạn nhận xét theo 6 bước
   (1) đáp án chuẩn khớp evidence? (2) rank evidence ở 3 cấu hình; (3) số trong B4ng/B4 so với evidence: đúng khác định dạng /
   thiếu / sai / từ chối; (4) nếu sai, số đó nằm ở chunk nào trong `data/processed/v1/chunks.jsonl` và có thuộc top-5 không;
   (5) `[n]` trỏ chunk nào (thứ tự top-5); (6) B4 có giống B4ng không. Gán mã chính G1/G2/F1/không lỗi, mã phụ nếu có.
   Kiểm giả thuyết: rag_v3 đưa ngữ cảnh dạng `<doc so="n">` (`src/generate/prompts.py`, `format_context`) nên mất mã chunk
   phân biệt bảng cá nhân (S1) / gia đình (S2). Ví dụ v1-0032: B4ng = B4 = 2.464.000 (nghi lấy từ biểu phí cá nhân).
   Thêm bảng tổng hợp cuối file, ghi "nháp, chờ HA duyệt". Viết lại đoạn "Đánh đổi của prompt rag_v3" ở mục 4 results_w8.md.
6. `PYTHONPATH=. python -m eval.error_sheet runs/B4_v1_test_20261107-1335 --ng-run runs/B4ng_v1_test_20261107-1335 --bench benchmark/benchmark_v1.1.jsonl --ragas results/ragas/B4_v1_test_20261107-1335__j1.csv --per-question results/review/per_question_v1.1_test.csv --manual results/review/manual30_B4_v1_test_20261107-1335.csv --include $(cat results/review/error_include_qids.txt) --out results/review/error_analysis_B4_v1.1_test.xlsx`
   Với câu chưa có `code`: đọc câu trả lời, evidence, chunk được trích; điền `code` nháp và `note`. Giữ nguyên `code` lấy từ
   manual30. Tóm tắt phân bố mã lỗi theo nhóm câu, 3–5 ví dụ mỗi loại lớn, đề xuất khắc phục cho ĐA2 vào mục 6 results_w8.md.
   Mục "Ca từ demo" để riêng, không tính vào phân bố.
7. Dashboard: `web/lib/data.js` (`getEvalQuality`) và `web/views.jsx` đổi biểu đồ từ `cite_rate` sang `faithfulness_j1`,
   chú thích "Faithfulness (Ragas, j1)"; B0 để trống. Rồi `PYTHONPATH=. python scripts/sync_supabase.py evals --benchmark benchmark/benchmark_v1.1.jsonl --dry-run`;
   báo kết quả, **không chạy bản thật**.
8. Sửa đường dẫn CSV v1 trong `docs/results_w4_baseline.md`, `docs/results_w5_b3.md`, `docs/results_w6_b4.md`
   (`grep -rn "results/B[0-9]\|results/mcnemar" docs/`) sang `results/archive_v1/` (tên file có đuôi giờ của run).
9. Cập nhật dòng tuần 8 trong `docs/progress.md`; thêm vào `docs/decision-log.md` các quyết định 12–13/11 có trong
   `docs/results_w8.md` (judge j1/c2, bỏ c1, benchmark v1.1, run chính thức, kiểm định, rơi số rag_v3).
