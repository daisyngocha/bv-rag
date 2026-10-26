import warnings; warnings.filterwarnings("ignore", message="Provenance bbox")
import json, sys, time
from pathlib import Path
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
from src.ingest.parser import build_converter, parse_pdf, split_2up

BACKEND = sys.argv[1] if len(sys.argv) > 1 else "pdfium"          # pdfium | default
SRC = Path("data/raw/products/BVP")
OUT = Path(f"logs/pilot_bvp/parsed_{BACKEND}"); OUT.mkdir(parents=True, exist_ok=True)
FILES = {
    "bvp_quytac.pdf":       {"split_2up": True},
    "bvp_bangquyenloi.pdf": {"split_2up": False},
    "bvp_brochure.pdf":     {"split_2up": False},
}

conv, stats = build_converter(ocr=False, num_threads=8,
                              backend=PyPdfiumDocumentBackend if BACKEND == "pdfium" else None), {}
for name, cfg in FILES.items():
    src, page_map = SRC / name, None
    if cfg["split_2up"]:
        split_path = OUT / f"{src.stem}_split.pdf"
        page_map = split_2up(str(src), str(split_path))
        src = split_path
    t0 = time.time()
    doc, tables, dropped = parse_pdf(str(src), conv)
    sec, n = time.time() - t0, len(doc.pages)
    stem = Path(name).stem
    (OUT / f"{stem}.docling.json").write_text(json.dumps(doc.export_to_dict(), ensure_ascii=False), encoding="utf-8")
    (OUT / f"{stem}.md").write_text(doc.export_to_markdown(), encoding="utf-8")
    for i, md in enumerate(tables, 1):
        (OUT / f"{stem}_TB{i}.md").write_text(md, encoding="utf-8")
    if page_map:
        (OUT / f"{stem}_page_map.json").write_text(json.dumps(page_map), encoding="utf-8")
    stats[name] = {"pages": n, "tables": len(tables), "dropped": dropped,"sec": round(sec, 1), "sec_per_page": round(sec / n, 2)}
    print(name, stats[name], flush=True)

(OUT / "parse_stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
