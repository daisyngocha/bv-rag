# Truth lập tay cho từng sản phẩm

Mỗi sản phẩm một file `{product_code}.json`, lập tay từ PDF gốc (mục lục, số định nghĩa, bảng, `cell_checks`),
không lấy từ regex của chunker (decision-log 2026-10-25). `scripts/build_kb.py` đọc file này ở bước `check`.

Khung theo pilot BVP, khóa ngoài là tên file PDF:

```json
{"bvp_quytac.pdf": {
   "sections": [{"chuong": "I", "muc": "II"}, {"chuong": "III", "muc": "I", "bo_sung": [{"so": 5}]}, {"phu_luc": 1}],
   "tables": [{"id": "QLBS5", "cell_checks": [{"row": "...", "col": "...", "value": "..."}]}]},
 "bvp_bangquyenloi.pdf": {"tables": [{"cell_checks": [...]}]}}
```

Pilot BVP: chép `logs/pilot_bvp/truth.json` thành `data/truth/BVP.json`.
