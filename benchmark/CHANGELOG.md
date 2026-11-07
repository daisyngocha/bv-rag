# Benchmark changelog

| Ngày | Phiên bản | qid | Thay đổi | Lý do |
| --- | --- | --- | --- | --- |
| 2026-11-07 | v1 | v1-0001 – v1-0150 | Tạo benchmark v1: 150 câu (lookup, table, compare, scenario, out_of_scope mỗi nhóm 30), dev 30 (6/nhóm), test 120; easy 62, medium 64, hard 24; BTB 31, BVP 34, C37 24, FLX 32, ITC 29 câu. Soạn nháp Gemini gemini-3.8-flash (lô w3 prompt p1, w3b p2, w4/w4b/w4c p3), duyệt tay theo drafts/*_review.csv; câu table đối chiếu ô, câu out_of_scope kiểm từ khóa trên data/processed/v1 | Chốt v1 sớm (kế hoạch tuần 5); evidence_ids theo processed/v1 (manifest data/manifests/v1.json) |
| 2026-11-07 | v1 | v1-0006, 0041, 0046, 0048, 0049, 0087, 0089, 0092, 0100, 0106, 0114, 0115, 0126, 0129 | Rà tay 14 câu bị `eval.per_question` gắn cờ trên test (B1/B2/B3hyb/B3): đáp án và evidence đúng, không sửa | Kết quả rà ở docs/results_w5_b3.md; nguyên nhân là lỗi hệ thống (từ chối nhầm, truy xuất trượt, đọc nhầm bảng), benchmark_v1.jsonl giữ nguyên sha256 |
