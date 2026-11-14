# bv-rag – ghi chú cho Claude Code

Đồ án chuyên ngành 1 (HUST, GenAI): hệ thống hỏi đáp RAG có trích dẫn về sản phẩm bảo hiểm cá nhân Bảo Việt.
Đồ án 1/3 (ĐA1 → ĐA2 → ĐATN): code, schema, benchmark, harness phải dùng lại được cho ĐA2/ĐATN.
Người làm: Lê Thị Ngọc Hà (Data/Business Analyst bảo hiểm). Trả lời và viết tài liệu bằng tiếng Việt, mức practitioner, ngắn gọn.

## Dữ liệu và ràng buộc

- Chỉ tài liệu công khai và dữ liệu giả; không xử lý dữ liệu cá nhân thật.
- `runs/`, `data/processed/`, `.env` không có trong git (xem `.gitignore`); không commit chúng.
- Mọi lần chạy chính thức (sinh câu trả lời) trên Colab L4; laptop WSL chỉ CPU, chỉ để phát triển và tính metric từ log.
- Không chạy lại GPU, không gọi API judge (Gemini/Anthropic) nếu chưa được yêu cầu rõ.

## Đánh giá (tuần 8)

- Benchmark hiện hành: `benchmark/benchmark_v1.1.jsonl` (sửa từ v1, xem `benchmark/CHANGELOG.md`). Log chạy với v1; metric tính
  lại bằng `eval.metrics --bench benchmark/benchmark_v1.1.jsonl`. Số v1 ở `results/archive_v1/`.
- Run test chính thức: `configs/test_runs_official.txt` (8 run). Không dùng glob `runs/*_v1_test_*` (khớp cả run thử).
- Judge Ragas: j1 = Gemini (chính), c2 = Claude Haiku 5.5 (phụ); điểm từng câu `results/ragas/{run_id}__{judge}.csv`.
  `results/ragas/_unofficial/` là điểm của run không chính thức, bỏ qua.
- Ragas bổ sung (results_w8 mục 7): j1x = LLM của j1 + embedding Gemini (`configs/judge_j1x.yaml`, `eval/ragas_extra.py`):
  answer relevancy (prompt `rr_vi_v1`, chỉ tham khảo), context precision/recall (B4ng/B4 chép từ B4rr);
  điểm `results/ragas/{run_id}__j1x.csv`, gộp bằng `eval/ragas_summary.py --judge j1x`.
- Bảng tổng `docs/results_summary.md` sinh bằng `scripts/build_results_summary.py`; không sửa số bằng tay.
- Kết quả tuần 8: `docs/results_w8.md`. Tiến độ: `docs/progress.md`. Quyết định: `docs/decision-log.md`.
- Chỉ tinh chỉnh trên split dev, không bao giờ trên test. Kết luận "cải thiện" chỉ khi kiểm định theo cặp có ý nghĩa
  (`eval/mcnemar.py`, `eval/paired_tests.py`).

## Lệnh

- Python dự án: `.venv/bin/python`; judge Ragas: `.venv-judge/bin/python`. Luôn `PYTHONPATH=.`.
- Test harness: `PYTHONPATH=. python -m pytest tests/test_eval_harness.py -q`.

## Không được

- Sửa `benchmark/benchmark_v1.1.jsonl`, `eval/ragas_eval.py`, `eval/ragas_extra.py` (gồm prompt `rr_vi_v1`),
  `configs/judge_*.yaml`, prompt đã dùng cho run chính thức
  (`src/generate/prompts.py`: thêm tên mới thay vì sửa).
- `git add -A` hoặc `git add .`; luôn add đúng file. Không push nếu chưa được bảo.
- Ghi đè nhận xét/mã lỗi người dùng đã chốt. Nhận định của Claude ghi rõ "nháp, chờ HA duyệt".
