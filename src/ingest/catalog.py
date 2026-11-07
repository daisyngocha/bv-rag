"""Product Catalog (data/catalog.json): mỗi sản phẩm một bản ghi, mỗi trường nội dung có value + source chunk_id.

Hai nguồn:
- Tự động (không cần duyệt): product_code, product_name, company, line (configs/products/{P}.yaml); quyết định ban hành
  và effective_date của quy tắc (data/truth/{P}.json); danh sách tài liệu (data/raw/sources.csv).
- Nhập tay đã duyệt: data/manual/catalog.csv, dạng dài (product_code, field, value, source, note); một trường có thể
  nhiều dòng (ví dụ programs). source = chunk_id trong processed/{ver}. LLM chỉ đề xuất, người duyệt ghi file này.

Kiểm tra bằng code (không để LLM quyết định con số): source phải có trong kho chunk; mọi số trong value phải xuất hiện
trong text của chunk source; tên chương trình phải có nguyên văn; mỗi sản phẩm phải đủ REQUIRED. Có lỗi thì không ghi file.

Chạy ở gốc repo (WSL):
    PYTHONPATH=. python -m src.ingest.catalog candidates --processed data/processed/v1 > data/manual/catalog_candidates.md
    PYTHONPATH=. python -m src.ingest.catalog build --processed data/processed/v1 --out data/catalog.json
"""
import argparse, csv, json, re, sys, unicodedata
from datetime import datetime
from pathlib import Path

import yaml

CFG_DIR, TRUTH_DIR = Path("configs/products"), Path("data/truth")
MANUAL_CSV, SOURCES_CSV = Path("data/manual/catalog.csv"), Path("data/raw/sources.csv")

# Trường nội dung: mô tả, bắt buộc?, từ khóa để lọc đoạn ứng viên
FIELDS = {
    "product_type": ("Loại sản phẩm (sức khỏe, tai nạn, bệnh hiểm nghèo, du lịch…)", True,
                     ["phạm vi bảo hiểm", "quyền lợi bảo hiểm", "bảo hiểm cho"]),
    "insured": ("Đối tượng được bảo hiểm", True, ["đối tượng", "người được bảo hiểm", "điều kiện tham gia"]),
    "age_min": ("Tuổi tham gia nhỏ nhất (giữ đơn vị: 15 ngày tuổi, 18 tuổi…)", True, ["tuổi"]),
    "age_max": ("Tuổi tham gia lớn nhất", True, ["tuổi"]),
    "renewal_age_max": ("Tuổi tái tục tối đa (nếu có)", False, ["tái tục"]),
    "territory": ("Phạm vi lãnh thổ", False, ["lãnh thổ", "phạm vi địa lý", "vùng bảo hiểm", "phạm vi bảo hiểm"]),
    "term": ("Thời hạn bảo hiểm", True, ["thời hạn bảo hiểm"]),
    "programs": ("Chương trình/gói (mỗi chương trình một dòng; tên phải có nguyên văn trong chunk)", False, ["chương trình"]),
    "sum_insured": ("Số tiền bảo hiểm/mức trách nhiệm (khoảng hoặc theo chương trình)", False, ["số tiền bảo hiểm", "mức trách nhiệm"]),
    "waiting_period": ("Thời gian chờ chính (bệnh thông thường)", False, ["thời gian chờ"]),
}
VERBATIM = {"programs"}          # giá trị phải có nguyên văn (không phân biệt hoa thường) trong chunk nguồn
REQUIRED = [f for f, (_, req, _) in FIELDS.items() if req]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", s)).lower()


def numbers(s: str) -> list[str]:
    """Số trong chuỗi, bỏ dấu phân cách nghìn: '1.000.000' → '1000000', '15' → '15'."""
    return [n.replace(".", "").replace(",", "") for n in re.findall(r"\d[\d.,]*\d|\d", s)]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def read_csv(path: Path) -> list[dict]:
    return list(csv.DictReader(open(path, encoding="utf-8-sig"))) if path.exists() else []


def auto_fields(P: str) -> dict:
    pc = yaml.safe_load(open(CFG_DIR / f"{P}.yaml", encoding="utf-8"))
    truth = json.load(open(TRUTH_DIR / f"{P}.json", encoding="utf-8"))
    qt = next((v for k, v in truth.items() if k.endswith("_quytac.pdf")), {})
    iss = qt.get("issuance", {})
    docs = [{"doc_type": s["doc_type"], "file": s["file"], "effective_date": s["effective_date"], "url": s["url"]}
            for s in read_csv(SOURCES_CSV) if s["product_code"] == P]
    return {"product_code": P, "product_name": pc["product_name"], "company": pc["company"], "line": pc["line"],
            "decision": iss.get("decision"), "effective_date": pc["effective_date"], "documents": docs}


def build(processed: Path) -> tuple[dict, list[str]]:
    chunks = {c["chunk_id"]: c for c in read_jsonl(processed / "chunks.jsonl")}
    products = sorted({c["product_code"] for c in chunks.values()})
    rows, errors = read_csv(MANUAL_CSV), []
    out = []
    for P in products:
        rec = auto_fields(P)
        fields: dict[str, list] = {}
        for r in (r for r in rows if r["product_code"] == P):
            f, value, src = r["field"].strip(), r["value"].strip(), r["source"].strip()
            if f not in FIELDS:
                errors.append(f"{P}: trường lạ '{f}'")
                continue
            c = chunks.get(src)
            if not c:
                errors.append(f"{P}.{f}: source {src!r} không có trong kho chunk")
                continue
            if c["product_code"] != P:
                errors.append(f"{P}.{f}: source {src} thuộc sản phẩm {c['product_code']}")
            text_nums = set(numbers(c["text"]))
            missing = [n for n in numbers(value) if n not in text_nums]
            if missing:
                errors.append(f"{P}.{f}: số {missing} trong '{value}' không có trong {src}")
            if f in VERBATIM and norm(value) not in norm(c["text"]):
                errors.append(f"{P}.{f}: '{value}' không có nguyên văn trong {src}")
            item = {"value": value, "source": src}
            if r.get("note", "").strip():
                item["note"] = r["note"].strip()
            fields.setdefault(f, []).append(item)
        errors += [f"{P}: thiếu trường {f}" for f in REQUIRED if f not in fields]
        rec["fields"] = {f: (v if f == "programs" or len(v) > 1 else v[0]) for f, v in fields.items()}
        out.append(rec)
    meta = {"data_version": processed.name, "built_at": datetime.now().isoformat(timespec="seconds"),
            "n_products": len(out), "manual_source": str(MANUAL_CSV),
            "note": "fields.*.source = chunk_id trong processed/{data_version}; số trong value đã đối chiếu với text chunk"}
    return {"_meta": meta, "products": out}, errors


def candidates(processed: Path, per_field: int = 4, width: int = 220) -> str:
    """Đoạn ứng viên cho từng (sản phẩm, trường): chunk quy tắc/BQL/biểu phí có nhiều từ khóa nhất, bỏ chunk định nghĩa."""
    chunks = read_jsonl(processed / "chunks.jsonl")
    defs = {}
    for p in CFG_DIR.glob("*.yaml"):
        pc = yaml.safe_load(open(p, encoding="utf-8"))
        if d := (pc.get("checks") or {}).get("definitions"):
            defs[pc["product_code"]] = d["prefix"]
    lines = ["# Đoạn ứng viên cho Product Catalog (tự sinh, không sửa tay)", ""]
    for P in sorted({c["product_code"] for c in chunks}):
        lines += [f"## {P}", ""]
        pool = [c for c in chunks if c["product_code"] == P and not c["chunk_id"].startswith(defs.get(P, "\0"))]
        for f, (desc, _, kws) in FIELDS.items():
            scored = []
            for c in pool:
                t = norm(c["text"])
                hits = sum(t.count(k) for k in kws)
                if hits:
                    scored.append((hits, c))
            scored.sort(key=lambda x: -x[0])
            lines.append(f"### {P}.{f}: {desc}")
            for _, c in scored[:per_field]:
                t = re.sub(r"\s+", " ", c["text"].split("\n", 1)[-1])
                i = min((norm(t).find(k) for k in kws if k in norm(t)), default=0)
                snip = t[max(0, i - width // 3): i + width]
                lines.append(f"- `{c['chunk_id']}` ({c['doc_type']}, tr.{c['page']}): …{snip}…")
            lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "candidates"])
    ap.add_argument("--processed", type=Path, default=Path("data/processed/v1"))
    ap.add_argument("--out", type=Path, default=Path("data/catalog.json"))
    a = ap.parse_args()
    if a.cmd == "candidates":
        print(candidates(a.processed))
        return
    catalog, errors = build(a.processed)
    print(f"{catalog['_meta']['n_products']} sản phẩm")
    if errors:
        sys.exit("Lỗi, chưa ghi file:\n  " + "\n  ".join(errors))
    json.dump(catalog, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"→ {a.out}")


if __name__ == "__main__":
    main()
