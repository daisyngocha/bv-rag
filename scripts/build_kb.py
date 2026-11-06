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
import argparse, json, re, statistics, sys, time, warnings
from pathlib import Path

import yaml

warnings.filterwarnings("ignore", message="Provenance bbox")
from src.ingest.align import align, align_report
from src.ingest.checks import run_checks
from src.ingest.chunker import DT_ABBR, build_vocab, chunk_document
from src.ingest.fixed_chunker import chunk_fixed, make_offset_encoder, regex_offset_encoder
from src.retrieve.encoder import CHUNK_MAX_LENGTH

RAW, PARSED, PROCESSED = Path("data/raw/products"), Path("data/parsed"), Path("data/processed")
META_KEYS = ("product_code", "product_name", "company", "line", "effective_date")


def load_yaml(path):
    return yaml.safe_load(open(path, encoding="utf-8"))


def file_cfgs(pc: dict) -> dict:
    """{stem: cfg} với meta sản phẩm gộp vào; khóa của file ghi đè meta."""
    return {stem: {**{k: pc[k] for k in META_KEYS}, **c, "source_file": f"{stem}.pdf"}
            for stem, c in pc["files"].items()}


def parse_product(pc: dict, force: bool) -> None:
    from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend
    from src.ingest.parser import build_converter, ocr_provenance, parse_pdf, split_2up

    P, out = pc["product_code"], PARSED / pc["product_code"]
    out.mkdir(parents=True, exist_ok=True)
    opt = pc.get("parse", {})
    convs: dict[str, object] = {}                      # một converter cho mỗi cấu hình OCR (file không OCR dùng chung)

    def converter(ocr):
        key = json.dumps(ocr, sort_keys=True)
        if key not in convs:
            convs[key] = build_converter(ocr=ocr, num_threads=opt.get("num_threads", 8),
                                         backend=PyPdfiumDocumentBackend if opt.get("backend", "pdfium") == "pdfium" else None)
        return convs[key]

    for stem, c in pc["files"].items():
        ocr = c.get("ocr") or opt.get("ocr") or None   # khóa ocr của file ghi đè parse.ocr của sản phẩm
        prov_path = out / f"{stem}.ocr.json"
        prov = ocr_provenance(ocr) if ocr else None
        cached = (out / f"{stem}.docling.json").exists()
        old = json.load(open(prov_path, encoding="utf-8")) if prov_path.exists() else None
        if cached and not force and old == prov:
            print(f"   parse {stem}: dùng cache {out}")
            continue
        if cached and not force:
            print(f"   parse {stem}: cấu hình OCR đổi → parse lại")
        src = RAW / P / f"{stem}.pdf"
        if c.get("split_2up"):
            page_map = split_2up(str(src), str(out / f"{stem}_split.pdf"))
            (out / f"{stem}_page_map.json").write_text(json.dumps(page_map), encoding="utf-8")
            src = out / f"{stem}_split.pdf"
        t0 = time.time()
        doc, tables, dropped = parse_pdf(str(src), converter(ocr))
        (out / f"{stem}.docling.json").write_text(json.dumps(doc.export_to_dict(), ensure_ascii=False), encoding="utf-8")
        (out / f"{stem}.md").write_text(doc.export_to_markdown(), encoding="utf-8")
        for i, md in enumerate(tables, 1):
            (out / f"{stem}_TB{i}.md").write_text(md, encoding="utf-8")
        if prov:
            prov_path.write_text(json.dumps(prov, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            prov_path.unlink(missing_ok=True)
        print(f"   parse {stem}: {len(doc.pages)} trang, {len(tables)} bảng, bỏ {dropped} item ngoài trang, "
              f"{time.time() - t0:.0f} s")


def file_inputs(P: str, stem: str, c: dict):
    """Đường dẫn PDF dùng cho mục lục/từ vựng và page_map: file đã cắt nếu split_2up, không thì file gốc."""
    d = PARSED / P
    pdf = d / f"{stem}_split.pdf" if c.get("split_2up") else RAW / P / f"{stem}.pdf"
    page_map = json.load(open(d / f"{stem}_page_map.json")) if c.get("split_2up") else None
    return str(pdf), page_map


def manual_chunks(pc: dict, structure: list[dict], fixed: list[dict], count, max_tokens: int):
    """Đơn vị nhập tay (config manual_units): nội dung chỉ có ở trang scan không đưa vào kho, hoặc bảng OCR không đạt.
    Mỗi đơn vị → 1 chunk cấu trúc ({sp}_{dt}_S{i}) + 1 chunk cố định ({sp}_{dt}_F{nnn}) cùng nội dung, manual: true;
    số thứ tự đánh tiếp sau chunk đã có cùng tiền tố để không trùng id."""
    def next_no(chunks, prefix):
        nums = [int(m[1]) for c in chunks if (m := re.fullmatch(rf"{re.escape(prefix)}(\d+)(?:_.*)?", c["chunk_id"]))]
        return max(nums, default=0) + 1

    ms, mf = [], []
    for i, u in enumerate(pc["manual_units"], 1):
        miss = [k for k in ("doc_type", "doc_label", "source_file", "page", "section_path", "text") if k not in u]
        if miss:
            raise ValueError(f"manual_units[{i}] thiếu {miss}")
        meta = {k: pc[k] for k in META_KEYS} | {k: u[k] for k in META_KEYS if k in u}
        base = f'{pc["product_code"]}_{DT_ABBR[u["doc_type"]]}_'
        common = {"company": meta["company"], "product_code": meta["product_code"], "line": meta["line"],
                  "doc_type": u["doc_type"], "section_path": u["section_path"],
                  "is_table": u.get("is_table", u["text"].lstrip().startswith("|")),
                  "effective_date": meta["effective_date"], "source_file": u["source_file"], "page": u["page"],
                  "ocr": False, "manual": True}
        tail = " > ".join(u["section_path"].split(" > ")[-2:])
        s_text = f'[{meta["product_name"]} | {u["doc_label"]} | {tail}]\n{u["text"]}'
        if count(s_text) > max_tokens:
            raise ValueError(f"manual_units[{i}] dài {count(s_text)} token > {max_tokens}; tách thành nhiều đơn vị")
        ms.append({"chunk_id": f"{base}S{next_no(structure + ms, base + 'S')}", "text": s_text, **common})
        mf.append({"chunk_id": f"{base}F{next_no(fixed + mf, base + 'F'):03d}",
                   "text": f'[{meta["product_name"]} | {u["doc_label"]}]\n{u["text"]}', **common,
                   "section_path": u["doc_label"]})
    return ms, mf


def chunk_product(pc: dict, struct_cfg: dict, fixed_cfg: dict, encode, tokenizer: str, ver: str) -> bool:
    from docling_core.types.doc import DoclingDocument

    P = pc["product_code"]
    count = lambda s: len(encode(s))
    files = file_cfgs(pc)
    structure, fixed, report = [], [], {"tokenizer": tokenizer, "files": {}}
    vocab: set[str] = set()

    for stem, cfg in files.items():
        doc = DoclingDocument.load_from_json(PARSED / P / f"{stem}.docling.json")
        pdf, page_map = file_inputs(P, stem, cfg)
        txt_pdf = None if cfg.get("ocr") else pdf        # file OCR: lớp chữ có sẵn (nếu có) không tin được → không dùng pdftotext
        if txt_pdf:
            vocab |= build_vocab(txt_pdf)
        ch, rep = chunk_document(doc, cfg, count, page_map, txt_pdf if cfg.get("toc_pages") else None,
                                 max_tokens=struct_cfg["max_tokens"], vocab_pdf=txt_pdf)
        fx, frep = chunk_fixed(doc, cfg, encode, page_map, max_tokens=fixed_cfg["max_tokens"],
                               overlap=fixed_cfg["overlap"], vocab_pdf=txt_pdf)
        if (prov := PARSED / P / f"{stem}.ocr.json").exists():
            rep["ocr"] = json.load(open(prov, encoding="utf-8"))
        toks = [count(c["text"]) for c in ch]
        rep.update(tokens_max=max(toks), tokens_median=int(statistics.median(toks)),
                   over_max=sum(t > struct_cfg["max_tokens"] for t in toks), tables=sum(c["is_table"] for c in ch))
        report["files"][stem] = {"structure": rep, "fixed": frep}
        structure += ch
        fixed += fx
        print(f"   {stem}: cấu trúc {len(ch)} chunk (token max {rep['tokens_max']}, trung vị {rep['tokens_median']}, "
              f"vượt {rep['over_max']}, bảng {rep['tables']}) | cố định {len(fx)} chunk")
        if "text_fixes" in rep:
            print(f"      text_fixes: {rep['text_fixes']} lần thay")
        if "ocr" in rep:
            print(f"      OCR: {rep['ocr']['engine']}, {rep['ocr']['tessdata_dir']} {rep['ocr']['traineddata_sha256']}")
        if "toc_entries" in rep:
            print(f"      mục lục: khớp {rep['matched']}/{rep['toc_entries']} | chèn: {rep['inserted']}")
            for m in rep["missing"]:
                print("      THIẾU:", m)
        for m in rep.get("toc_titles_fixed", []):
            print("      SỬA TIÊU ĐỀ:", m)
        for m in rep.get("toc_titles_unmatched", []):
            print("      TIÊU ĐỀ KHÔNG KHỚP MỤC LỤC:", m)
        for key, lab in (("table_overrides", "BẢNG NHẬP TAY"), ("merged_heads_split", "TÁCH TIÊU ĐỀ GỘP"),
                         ("numbering_fixed", "SỬA SỐ MỤC"), ("numbering_gaps", "KHOẢNG HỞ SỐ MỤC")):
            for m in rep.get(key, []):
                print(f"      {lab}:", m)

    if pc.get("manual_units"):
        ms, mf = manual_chunks(pc, structure, fixed, count, struct_cfg["max_tokens"])
        structure += ms
        fixed += mf
        report["manual_units"] = [c["chunk_id"] for c in ms]
        print(f"   manual_units: {report['manual_units']} (cố định: {[c['chunk_id'] for c in mf]})")

    truth_path = Path(pc["truth"])
    if truth_path.exists():
        truth = json.load(open(truth_path, encoding="utf-8"))
        checks = run_checks(structure, truth, {c["source_file"]: c for c in files.values()}, pc.get("checks", {}), vocab)
    else:
        checks = {f"có truth {truth_path}": False}
    long = [c["chunk_id"] for c in structure + fixed if count(c["text"]) > CHUNK_MAX_LENGTH]
    checks[f"chunk ≤ {CHUNK_MAX_LENGTH} token, giới hạn embed/rerank (vượt: {long[:5]})"] = not long
    report["checks"] = checks
    report["align"] = align_report(align(structure, fixed))

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
