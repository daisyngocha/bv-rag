# Benchmark changelog

| Ngày | Phiên bản | qid | Thay đổi | Lý do |
| --- | --- | --- | --- | --- |
| 2026-11-07 | v1 | v1-0001 – v1-0150 | Tạo benchmark v1: 150 câu (lookup, table, compare, scenario, out_of_scope mỗi nhóm 30), dev 30 (6/nhóm), test 120; easy 62, medium 64, hard 24; BTB 31, BVP 34, C37 24, FLX 32, ITC 29 câu. Soạn nháp Gemini gemini-3.8-flash (lô w3 prompt p1, w3b p2, w4/w4b/w4c p3), duyệt tay theo drafts/*_review.csv; câu table đối chiếu ô, câu out_of_scope kiểm từ khóa trên data/processed/v1 | Chốt v1 sớm (kế hoạch tuần 5); evidence_ids theo processed/v1 (manifest data/manifests/v1.json) |
