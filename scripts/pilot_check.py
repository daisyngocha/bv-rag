import json, re
from pathlib import Path
from docling_core.types.doc import DoclingDocument
import sys

P = Path(sys.argv[1] if len(sys.argv) > 1 else "logs/pilot_bvp/parsed")
truth = json.load(open("logs/pilot_bvp/truth.json", encoding="utf-8"))
load = lambda stem: DoclingDocument.load_from_json(P / f"{stem}.docling.json")
pg = lambda it: it.prov[0].page_no if it.prov else None
norm = lambda s: re.sub(r"\s+", "", s)

# 1. Danh sách bảng: trang, kích thước, ô đầu
for stem in ["bvp_quytac", "bvp_bangquyenloi", "bvp_brochure"]:
    doc = load(stem)
    print(f"== {stem}: {len(doc.tables)} bảng")
    for i, t in enumerate(doc.tables, 1):
        first = t.data.table_cells[0].text[:40] if t.data.table_cells else ""
        print(f"  TB{i}: trang {pg(t)}, {t.data.num_rows}x{t.data.num_cols}, ô đầu: {first!r}")

# 2. Tiêu đề và nhãn của quy tắc
doc = load("bvp_quytac")
print("== Tiêu đề quy tắc")
labels = {}
for it, _ in doc.iterate_items():
    lab = it.label.value
    labels[lab] = labels.get(lab, 0) + 1
    if lab in ("section_header", "title"):
        print(f"  p{pg(it)}: {it.text[:70]}")
print("== Số item theo nhãn:", labels)

# 3. Nhiễu và lỗi ký tự
md = (P / "bvp_quytac.md").read_text(encoding="utf-8")
body = md.split("## CHƯƠNG I - Quy Định Chung")[-1]
print("Ð:", md.count("Ð"), "| footer '- n -':", len(re.findall(r"^- \d+ -$", md, re.M)),
      "| caption ảnh:", sum(s in md for s in ["Chi trả khám chữa bệnh", "Quyền lợi ngoại trú"]),
      "| 'CHƯƠNG IV' trong thân:", "CHƯƠNG IV" in body,
      "| 'HỒ SƠ YÊU CẦU BỒI THƯỜNG':", "HỒ SƠ YÊU CẦU BỒI THƯỜNG" in body)

# 4. cell_checks bảng quyền lợi
rows = [r for r in (P / "bvp_bangquyenloi_TB1.md").read_text(encoding="utf-8").splitlines() if r.startswith("|")]
cells = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
hdr, ok = cells(rows[0]), 0
checks = truth["bvp_bangquyenloi.pdf"]["tables"][0]["cell_checks"]
for c in checks:
    j, key = hdr.index(c["col"]), norm(c["row"].replace(" (ô gộp)", ""))[:25]
    vals = [norm(cells(r)[j]) for r in rows[2:] if key in norm(cells(r)[0])]
    hit = any(norm(c["value"]).replace(";", "") in v for v in vals)
    ok += hit
    print(("OK  " if hit else "SAI ") + f"{c['row'][:40]} | {c['col']} | {c['value']}")
print(f"cell_checks: {ok}/{len(checks)}")

# 5. Ghi chú dưới bảng quyền lợi
bmd = (P / "bvp_bangquyenloi.md").read_text(encoding="utf-8")
print("Ghi chú BQL:", {k: k in bmd for k in ["ĐIỀU CHỈNH BỔ SUNG", "70/30", "1,5 lần"]})

# 6. Bảng Thai sản (QL bổ sung 5, trang 33)
doc = load("bvp_quytac")
qlbs5 = next((t for t in doc.tables if pg(t) == 33), None)
if qlbs5 is None:
    print("QLBS5: KHÔNG thấy bảng ở trang 33")
else:
    md5 = norm(qlbs5.export_to_markdown(doc=doc))
    qt = next((t for t in truth["bvp_quytac.pdf"].get("tables", []) if t.get("id") == "QLBS5"), None)
    for c in (qt or {}).get("cell_checks", []):
        print(("OK  " if norm(c["value"]) in md5 else "SAI ") + f"QLBS5 | {c['col']} | {c['value']}")
