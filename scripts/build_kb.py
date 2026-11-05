"""Xây kho chunk cho từng sản phẩm: parse → chunk (cấu trúc + cố định) → check → gộp + căn chỉnh.

Chạy ở gốc repo, trên WSL (parse cần requirements/ingest.txt):
    PYTHONPATH=. python scripts/build_kb.py --product BVP
    PYTHONPATH=. python scripts/build_kb.py --all                 # mọi configs/products/*.yaml
    PYTHONPATH=. python scripts/build_kb.py --product BVP --force-parse

Tham số chunk lấy từ configs/B1.yaml (cố định) và configs/B2.yaml (cấu trúc); phiên bản dữ liệu
lấy từ data_version của B2.yaml. Đầu ra:
    data/parsed/{P}/                         docling.json, md, bảng, file đã cắt 2-up, page_map (cache parse)
    data/processed/{ver}/{P}/                chunks.jsonl, chunks_fixed.jsonl, report.json
    data/processed/{ver}/chunks.jsonl        gộp các sản phẩm đạt mọi kiểm tra (B2+)
    data/processed/{ver}/chunks_fixed.jsonl  gộp, cho B1
    data/processed/{ver}/align_fixed.json    chunk cấu trúc → chunk cố định phủ nó (chấm B1)
"""
import argparse, json, re, statistics, sys, subprocess, time, warnings
from pathlib import Path

import yaml

warnings.filterwarnings("ignore", message="Provenance bbox")
from src.ingest.align import align, align_report
from src.ingest.checks import run_checks
from src.ingest.chunker import build_vocab, chunk_document, apply_text_fixes, toc_from_cfg, toc_from_pdf
from src.ingest.fixed_chunker import chunk_fixed, make_offset_encoder, regex_offset_encoder

RAW, PARSED, PROCESSED = Path("data/raw/products"), Path("data/parsed"), Path("data/processed")
META_KEYS = ("product_code", "product_name", "company", "line", "effective_date")


def load_yaml(path):
    return yaml.safe_load(open(path, encoding="utf-8"))


def file_cfgs(pc: dict) -> dict:
    """{stem: cfg} với meta sản phẩm gộp vào; khóa của file ghi đè meta."""
    return {stem: {**{k: pc[k] for k in META_KEYS}, **c, "source_file": f"{stem}.pdf"}
            for stem, c in pc["files"].items()}


def get_tesseract_metadata(tessdata_dir: str | None = None) -> dict:
    """Lấy thông tin version Tesseract và đường dẫn/loại traineddata phục vụ audit/report."""
    try:
        ver_res = subprocess.run(["tesseract", "--version"], capture_output=True, text=True, check=True)
        version_line = ver_res.stdout.splitlines()[0] if ver_res.stdout else "unknown"
    except Exception:
        version_line = "tesseract not found or error"

    traineddata_path = Path(tessdata_dir) / "vie.traineddata" if tessdata_dir else Path("/usr/share/tessdata/vie.traineddata")
    file_size_mb = round(traineddata_path.stat().st_size / (1024 * 1024), 2) if traineddata_path.exists() else 0.0
    data_type = "fast" if file_size_mb < 5.0 else "best"

    return {
        "engine": "tesseract",
        "version": version_line,
        "traineddata_lang": "vie",
        "traineddata_type": data_type,
        "traineddata_size_mb": file_size_mb,
        "path": str(traineddata_path)
    }


def parse_product(pc: dict, force: bool) -> None:
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
    from src.ingest.parser import build_converter, parse_pdf, split_2up

    P, out = pc["product_code"], PARSED / pc["product_code"]
    out.mkdir(parents=True, exist_ok=True)
    opt = pc.get("parse", {})
    
    # Duyệt qua các file để xem có file nào bật OCR riêng hay không
    has_ocr = any(c.get("ocr") for c in pc["files"].values()) or opt.get("ocr", False)
    ocr_opts = next((c.get("ocr") for c in pc["files"].values() if c.get("ocr")), opt.get("ocr", None))

    conv = build_converter(ocr=ocr_opts, num_threads=opt.get("num_threads", 8),
                           backend=PyPdfiumDocumentBackend if opt.get("backend", "pdfium") == "pdfium" else None)
    
    for stem, c in pc["files"].items():
        if (out / f"{stem}.docling.json").exists() and not force:
            print(f"   parse {stem}: dùng cache {out}")
            continue
        src = RAW / P / f"{stem}.pdf"
        if c.get("split_2up"):
            page_map = split_2up(str(src), str(out / f"{stem}_split.pdf"))
            (out / f"{stem}_page_map.json").write_text(json.dumps(page_map), encoding="utf-8")
            src = out / f"{stem}_split.pdf"
        t0 = time.time()
        doc, tables, dropped = parse_pdf(str(src), conv)
        (out / f"{stem}.docling.json").write_text(json.dumps(doc.export_to_dict(), ensure_ascii=False), encoding="utf-8")
        (out / f"{stem}.md").write_text(doc.export_to_markdown(), encoding="utf-8")
        for i, md in enumerate(tables, 1):
            (out / f"{stem}_TB{i}.md").write_text(md, encoding="utf-8")
        print(f"   parse {stem}: {len(doc.pages)} trang, {len(tables)} bảng, bỏ {dropped} item ngoài trang, "
              f"{time.time() - t0:.0f} s")


def file_inputs(P: str, stem: str, c: dict):
    """Đường dẫn PDF dùng cho mục lục/từ vựng và page_map: file đã cắt nếu split_2up, không thì file gốc."""
    d = PARSED / P
    pdf = d / f"{stem}_split.pdf" if c.get("split_2up") else RAW / P / f"{stem}.pdf"
    page_map = json.load(open(d / f"{stem}_page_map.json")) if c.get("split_2up") else None
    return str(pdf), page_map


def chunk_product(pc: dict, struct_cfg: dict, fixed_cfg: dict, encode, tokenizer: str, ver: str) -> bool:
    from docling_core.types.doc import DoclingDocument

    P = pc["product_code"]
    count = lambda s: len(encode(s))
    files = file_cfgs(pc)
    structure, fixed, report = [], [], {"tokenizer": tokenizer, "files": {}}
    vocab: set[str] = set()
    
    # Lấy thông tin cấu hình OCR nếu có dùng cho báo cáo report.json
    ocr_meta_captured = None

    for stem, cfg in files.items():
        doc = DoclingDocument.load_from_json(PARSED / P / f"{stem}.docling.json")
        pdf, page_map = file_inputs(P, stem, cfg)
        
        # Nếu file bật OCR, không dùng lớp chữ rác sẵn có để quét vocab/toc tự động
        txt_pdf = None if cfg.get("ocr") else pdf
        if txt_pdf:
            vocab |= build_vocab(txt_pdf)
            
        if cfg.get("ocr") and not ocr_meta_captured:
            ocr_cfg_val = cfg.get("ocr")
            tessdata_path = ocr_cfg_val.get("tessdata") if isinstance(ocr_cfg_val, dict) else None
            ocr_meta_captured = get_tesseract_metadata(tessdata_path)

        # Xử lý Mục lục: Ưu tiên đọc từ YAML (`toc`), nếu không có mới dùng `toc_pages`
        toc_items = toc_from_cfg(cfg["toc"]) if cfg.get("toc") else (toc_from_pdf(txt_pdf, cfg["toc_pages"]) if cfg.get("toc_pages") and txt_pdf else None)

        ch, rep = chunk_document(doc, cfg, count, page_map, toc_items=toc_items,
                                 max_tokens=struct_cfg["max_tokens"], vocab_pdf=txt_pdf)
        fx, frep = chunk_fixed(doc, cfg, encode, page_map, max_tokens=fixed_cfg["max_tokens"],
                               overlap=fixed_cfg["overlap"], vocab_pdf=txt_pdf)

        # Áp dụng các bản vá văn bản định nghĩa trước (text_fixes)
        if cfg.get("text_fixes"):
            ch, _ = apply_text_fixes(ch, cfg["text_fixes"])
            fx, _ = apply_text_fixes(fx, cfg["text_fixes"])

        # Bổ sung các manual_units nếu có khai báo trong YAML (ví dụ trang 47 biểu phí BTB)
        if cfg.get("manual_units"):
            for m in cfg["manual_units"]:
                manual_chunk = {
                    "chunk_id": f"{P}_{stem}_manual_{len(ch)+1}",
                    "product_code": P,
                    "doc_type": m.get("doc_type", cfg.get("doc_type")),
                    "doc_label": m.get("doc_label", cfg.get("doc_label")),
                    "source_file": m.get("source_file", f"{stem}.pdf"),
                    "page": m.get("page"),
                    "section_path": m.get("section_path"),
                    "text": m.get("text"),
                    "manual": True
                }
                ch.append(manual_chunk)
                fx.append(manual_chunk)

        toks = [count(c["text"]) for c in ch]
        rep.update(tokens_max=max(toks) if toks else 0, 
                   tokens_median=int(statistics.median(toks)) if toks else 0,
                   over_max=sum(t > struct_cfg["max_tokens"] for t in toks), 
                   tables=sum(c.get("is_table", False) for c in ch))
        report["files"][stem] = {"structure": rep, "fixed": frep}
        structure += ch
        fixed += fx
        print(f"   {stem}: cấu trúc {len(ch)} chunk (token max {rep['tokens_max']}, trung vị {rep['tokens_median']}, "
              f"vượt {rep['over_max']}, bảng {rep['tables']}) | cố định {len(fx)} chunk")
        if "toc_entries" in rep:
            print(f"      mục lục: khớp {rep['matched']}/{rep['toc_entries']} | chèn: {rep['inserted']}")
            for m in rep.get("toc_titles_fixed", []):
                print("      SỬA TIÊU ĐỀ:", m)
            for m in rep.get("toc_titles_unmatched", []):
                print("      TIÊU ĐỀ KHÔNG KHỚP MỤC LỤC:", m)
            for m in rep["missing"]:
                print("      THIẾU:", m)

    truth_path = Path(pc["truth"])
    if truth_path.exists():
        truth = json.load(open(truth_path, encoding="utf-8"))
        checks = run_checks(structure, truth, {c["source_file"]: c for c in files.values()}, pc.get("checks", {}), vocab)
    else:
        checks = {f"có truth {truth_path}": False}
        
    report["checks"] = checks
    report["align"] = align_report(align(structure, fixed))
    if ocr_meta_captured:
        report["ocr_config"] = ocr_meta_captured

    print("   == Kiểm tra")
    for k, v in checks.items():
        print(("   OK   " if v else "   SAI  ") + k)
    print(f"   == Căn chỉnh cố định: {report['align']}")

    out = PROCESSED / ver / P
    out.mkdir(parents=True, exist_ok=True)
    write_jsonl(out / "chunks.jsonl", structure)
    write_jsonl(out / "chunks_fixed.jsonl", fixed)
    json.dump(report, open(out / "report.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return all(checks.values())


def write_jsonl(path: Path, rows: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def merge(ver: str, allow_fail: bool) -> None:
    """Gộp mọi sản phẩm đã chunk trong processed/{ver}; bỏ sản phẩm chưa đạt kiểm tra trừ khi --allow-fail."""
    root, structure, fixed, used = PROCESSED / ver, [], [], []
    for d in sorted(p for p in root.iterdir() if (p / "report.json").exists()):
        rep = json.load(open(d / "report.json", encoding="utf-8"))
        ok = all(rep["checks"].values()) and rep["tokenizer"] == "bge-m3"
        if not ok and not allow_fail:
            print(f"   bỏ {d.name}: chưa đạt kiểm tra hoặc không dùng tokenizer bge-m3")
            continue
        structure += read_jsonl(d / "chunks.jsonl")
        fixed += read_jsonl(d / "chunks_fixed.jsonl")
        used.append(d.name)
    write_jsonl(root / "chunks.jsonl", structure)
    write_jsonl(root / "chunks_fixed.jsonl", fixed)
    json.dump(align(structure, fixed), open(root / "align_fixed.json", "w", encoding="utf-8"), ensure_ascii=False)
    print(f"== Gộp {used}: {len(structure)} chunk cấu trúc, {len(fixed)} chunk cố định → {root}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--product", action="append", default=[])
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--steps", default="parse,chunk,merge")
    ap.add_argument("--force-parse", action="store_true")
    ap.add_argument("--allow-fail", action="store_true", help="vẫn gộp sản phẩm chưa đạt kiểm tra (chỉ để thử)")
    a = ap.parse_args()

    b1, b2 = load_yaml("configs/B1.yaml"), load_yaml("configs/B2.yaml")
    assert b1["data_version"] == b2["data_version"], "B1 và B2 phải cùng data_version"
    ver, steps = b2["data_version"], set(a.steps.split(","))
    products = sorted(p.stem for p in Path("configs/products").glob("*.yaml")) if a.all else a.product
    if not products and "merge" not in steps:
        sys.exit("Cần --product hoặc --all")

    encode, tokenizer = None, None
    if "chunk" in steps:
        try:
            encode, tokenizer = make_offset_encoder("BAAI/bge-m3"), "bge-m3"
        except Exception as e:
            print(f"!!! Không nạp được tokenizer bge-m3 ({e}); dùng ước lượng regex — KHÔNG dùng kết quả này")
            encode, tokenizer = regex_offset_encoder, "regex"

    failed = []
    for P in products:
        pc = load_yaml(f"configs/products/{P}.yaml")
        print(f"== {P}")
        if "parse" in steps:
            parse_product(pc, a.force_parse)
        if "chunk" in steps and not chunk_product(pc, b2["chunk"], b1["chunk"], encode, tokenizer, ver):
            failed.append(P)
    if "merge" in steps and (PROCESSED / ver).exists():
        merge(ver, a.allow_fail)
    if failed:
        sys.exit(f"Chưa đạt kiểm tra: {failed}")


if __name__ == "__main__":
    main()
