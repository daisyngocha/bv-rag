"""Pilot BVP bước 5: chunk 3 file đã parse (pypdfium2) và kiểm tra với truth.json.

Chạy ở gốc repo:  PYTHONPATH=. python scripts/pilot_chunk.py [thư_mục_parse]
Ghi: logs/pilot_bvp/chunks.jsonl, logs/pilot_bvp/chunk_report.json
"""
import json, re, statistics, sys, warnings
from pathlib import Path

warnings.filterwarnings("ignore", message="Provenance bbox")
from docling_core.types.doc import DoclingDocument
from src.ingest.chunker import chunk_document, make_token_counter, roman_to_int

P = Path(sys.argv[1] if len(sys.argv) > 1 else "logs/pilot_bvp/parsed_pdfium")
OUT = Path("logs/pilot_bvp")
RAW = Path("data/raw/products/BVP")
TRUTH = json.load(open(OUT / "truth.json", encoding="utf-8"))
META = dict(company="BHBV", product_code="BVP", product_name="Bảo Việt An Gia",
            line="phi_nhan_tho", effective_date="2025-06-27")
FILES = {   # cấu hình chunk từng file, lấy theo truth.json
    "bvp_quytac": dict(doc_type="quy_tac", doc_label="Quy tắc", structure="legal",
                       skip_pages=[1, 2, 3, 4, 5, 51, 52], toc_pages=[5],
                       toc_pdf="bvp_quytac_split.pdf", page_map="bvp_quytac_page_map.json",
                       vocab_pdf="bvp_quytac_split.pdf"),
    "bvp_bangquyenloi": dict(doc_type="bang_quyen_loi", doc_label="Bảng quyền lợi", structure="flat"),
    "bvp_brochure": dict(doc_type="brochure", doc_label="Tờ rơi", structure="flat",
                         drop_tables=True, min_chars=8),    # bảng tờ rơi trùng BQL → bỏ; giữ "Việt Nam."
}

try:
    count = make_token_counter("BAAI/bge-m3")
except Exception as e:                                       # chỉ để chạy thử khi chưa có tokenizer
    print(f"!!! Không nạp được tokenizer bge-m3 ({e}); dùng ước lượng len/3 — KHÔNG dùng số token này")
    count = lambda s: max(1, len(s) // 3)

all_chunks, report = [], {}
for stem, c in FILES.items():
    cfg = {**META, **c, "source_file": f"{stem}.pdf"}
    doc = DoclingDocument.load_from_json(P / f"{stem}.docling.json")
    page_map = json.load(open(P / c["page_map"])) if c.get("page_map") else None
    toc_pdf = str(P / c["toc_pdf"]) if c.get("toc_pdf") else None
    vocab_pdf = str(P / c["vocab_pdf"]) if c.get("vocab_pdf") else str(RAW / f"{stem}.pdf")
    chunks, rep = chunk_document(doc, cfg, count, page_map, toc_pdf, vocab_pdf=vocab_pdf)
    toks = [count(ch["text"]) for ch in chunks]
    rep.update(tokens_max=max(toks), tokens_median=int(statistics.median(toks)),
               over_512=sum(t > 512 for t in toks), tables=sum(ch["is_table"] for ch in chunks))
    report[stem] = rep
    all_chunks += chunks
    print(f"\n== {stem}: {len(chunks)} chunk | token max {rep['tokens_max']}, trung vị {rep['tokens_median']}, "
          f">512: {rep['over_512']} | chunk bảng: {rep['tables']}")
    if "toc_entries" in rep:
        print(f"   mục lục: khớp {rep['matched']}/{rep['toc_entries']} | chèn: {rep['inserted']}")
        for m in rep["missing"]:
            print("   THIẾU:", m)

# ---------------- kiểm tra với truth
ids = [c["chunk_id"] for c in all_chunks]
qt = [c for c in all_chunks if c["doc_type"] == "quy_tac"]
checks = {}
checks["chunk_id không trùng"] = len(ids) == len(set(ids))
defs = {int(m[1]) for c in qt if (m := re.match(r"BVP_QT_C1_M1_K(\d+)", c["chunk_id"]))}
checks[f"định nghĩa 53 (thấy {len(defs)})"] = defs == set(range(1, 54))
miss = []
for s in TRUTH["bvp_quytac.pdf"]["sections"]:
    if "phu_luc" in s:
        pref = f'BVP_QT_PL{s["phu_luc"]}'
    else:
        pref = f'BVP_QT_C{roman_to_int(s["chuong"])}' + (f'_M{roman_to_int(s["muc"])}' if s.get("muc") else "")
    prefs = [f'{pref}_B{b["so"]}' for b in s.get("bo_sung", [])] or [pref]
    for pr in prefs:
        if not any(i == pr or i.startswith(pr + "_") for i in ids):
            miss.append(pr)
checks[f"mỗi mục trong truth có chunk (thiếu: {miss})"] = not miss
noise = {"Ð": sum("Ð" in c["text"] for c in all_chunks),
         "footer": sum(bool(re.search(r"^- \d+ -$", c["text"], re.M)) for c in all_chunks),
         "caption ảnh": sum(any(x in c["text"] for x in ("Chi trả khám chữa bệnh", "Quyền lợi ngoại trú"))
                            for c in qt)}
checks[f"không còn nhiễu {noise}"] = not any(noise.values())
checks["page trong 1–27 (trang gốc)"] = all(1 <= c["page"] <= 27 for c in qt)
pl_pages = sorted({c["page"] for c in qt if c["chunk_id"].startswith("BVP_QT_PL1")})
checks[f"Phụ lục 1 trải trang gốc 23–26 (thấy {pl_pages})"] = pl_pages[:1] == [23] and pl_pages[-1:] == [26]
glued = sorted({w for c in all_chunks for w in re.findall(r"\b\w*(?:điềutrị|việnphí|THAISẢN|bảohiểm)\w*", c["text"])})
checks[f"không còn từ dính mẫu ({glued})"] = not glued
norm = lambda s: re.sub(r"\s+", "", s)
bql_txt = norm(" ".join(c["text"] for c in all_chunks if c["doc_type"] == "bang_quyen_loi"))
cells = TRUTH["bvp_bangquyenloi.pdf"]["tables"][0]["cell_checks"]
hit = sum(norm(x["value"]).replace(";", "") in bql_txt for x in cells)
checks[f"giá trị BQL còn trong chunk ({hit}/{len(cells)})"] = hit == len(cells)
checks["ghi chú dưới BQL có chunk"] = "70/30" in bql_txt and "1,5lần" in bql_txt
checks["tờ rơi không có chunk bảng"] = not any(c["is_table"] for c in all_chunks if c["doc_type"] == "brochure")

import unicodedata
from src.ingest.chunker import build_vocab, WORD
inv = [c["chunk_id"] for c in all_chunks
       if any(unicodedata.category(ch) in ("Cf", "Cc", "Co") and ch != "\n" for ch in c["text"])]
checks[f"không còn ký tự vô hình ({inv[:5]})"] = not inv
vocab = build_vocab(str(P / "bvp_quytac_split.pdf")) | build_vocab(str(RAW / "bvp_bangquyenloi.pdf")) \
        | build_vocab(str(RAW / "bvp_brochure.pdf"))
def glued(w):
    lw = w.lower()
    return len(w) >= 4 and lw not in vocab and any(lw[:i] in vocab and lw[i:] in vocab for i in range(2, len(w) - 1))
gl = sorted({w for c in all_chunks for w in WORD.findall(c["text"]) if glued(w)})
checks[f"không còn từ dính ({gl[:10]})"] = not gl

print("\n== Kiểm tra")
for k, v in checks.items():
    print(("OK   " if v else "SAI  ") + k)

with open(OUT / "chunks.jsonl", "w", encoding="utf-8") as f:
    for c in all_chunks:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
json.dump({"files": report, "checks": checks}, open(OUT / "chunk_report.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

print("\n== Danh sách chunk (id | trang | token | section_path)")
for c in all_chunks:
    print(f'{c["chunk_id"]:28s} {c["page"]:>3} {count(c["text"]):>4} | {c["section_path"][-70:]}')
print(f"\nĐã ghi {len(all_chunks)} chunk → {OUT / 'chunks.jsonl'}")
