# Benchmark: schema và quy trình

`benchmark_v1.jsonl`: mỗi dòng một câu hỏi. Kiểm tra: `PYTHONPATH=. python -m eval.benchmark benchmark/benchmark_v1.jsonl` (thêm `--final` khi chốt v1).

## Trường

| Trường | Kiểu | Ý nghĩa |
| --- | --- | --- |
| `qid` | str | `v1-0001`…; không đổi khi build lại, không dùng lại qid đã xóa |
| `question` | str | Câu hỏi tự nhiên, nêu tên sản phẩm |
| `answer` | str | Đáp án chuẩn; mọi số phải có trong text của `evidence_ids` (lookup, table, compare: lỗi; scenario: cảnh báo) |
| `evidence_ids` | list[str] | `chunk_id` chunk cấu trúc trong `data/processed/v1` chứa căn cứ; B1 chấm qua `align_fixed.json` |
| `products` | list[str] | Mã sản phẩm câu hỏi nhắc tới; chứa mọi sản phẩm của evidence |
| `group` | str | `lookup`, `table`, `compare`, `scenario`, `out_of_scope` |
| `difficulty` | str | `easy`, `medium`, `hard` |
| `answerable` | bool | `false` ⇔ `out_of_scope`: `evidence_ids = []`, `answer` = câu từ chối chuẩn |
| `split` | str | `dev` (tinh chỉnh ngưỡng, prompt) hoặc `test` (chỉ để báo cáo) |
| `created_by` | str | `llm_draft+human` |
| `version` | str | `v1` |
| `source_draft` | str | `task_id` bản nháp (truy vết về `drafts/*_review.csv`) |

Câu từ chối chuẩn: "Tài liệu sản phẩm hiện có không có thông tin để trả lời câu hỏi này." (`draft_config.yaml: refusal`).

## Phân bố v1

150 câu, 30 câu mỗi nhóm; dev 30 (6/nhóm), test 120. Rải đủ 5 sản phẩm; có câu trên chunk OCR (BTB quy tắc, FLX BQL) để tách khi phân tích RQ1.

## Quy trình (`eval/bench_draft.py`)

1. `sample`: code chọn chunk phân tầng theo sản phẩm (lookup: quy tắc, có 20% định nghĩa; table: chunk bảng; scenario: quy tắc có thời gian chờ/loại trừ/đồng chi trả/giới hạn); compare ghép cặp theo trường Product Catalog và thuật ngữ glossary có định nghĩa khác nhau; out_of_scope theo 4 loại (brochure, luật, sản phẩm khác, chi tiết không nêu).
2. `draft`: Gemini (model, `prompt_version` trong `draft_config.yaml`) viết câu hỏi, đáp án, độ khó. Evidence do code chọn, không do LLM.
3. `review`: xuất `drafts/{tag}_review.csv` kèm text evidence và cờ: số không có trong evidence, ô cần tránh (truth `data_quality`), evidence OCR, câu hỏi chép ≥ 8 từ, gần trùng câu khác. Người duyệt điền `decision` (`keep`, `edit` + `edited_question`/`edited_answer`, `drop`), chỉnh `split`, `difficulty`.
4. `build`: gộp mọi `*_review.csv` → `benchmark_v1.jsonl`, kiểm lại; có lỗi thì không ghi file.

Checklist duyệt: đáp án kiểm được 100% từ evidence; câu hỏi có một đáp án rõ ràng; không chép nguyên văn; đúng nhóm, độ khó; không trùng ý; out_of_scope chắc chắn tài liệu không có.

Sau khi chốt v1 (tuần 5), mọi sửa đổi ghi vào `CHANGELOG.md`.
