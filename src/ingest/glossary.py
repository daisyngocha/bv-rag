"""Từ điển thuật ngữ 2 cấp (data/glossary.json): general từ văn bản pháp luật đã duyệt, sản phẩm từ chunk định nghĩa.

- general: các dòng keep=1 của data/manual/glossary_general_candidates.csv (đã duyệt tay); source = điều/khoản văn bản,
  effective_date lấy từ data/raw/sources.csv theo văn bản.
- sản phẩm: mỗi định nghĩa trong quy tắc là một đơn vị chunk riêng; id có tiền tố checks.definitions.prefix của
  configs/products/{P}.yaml (ví dụ BVP_QT_C1_M1_K12). Thuật ngữ = cấp cuối của section_path (chunker coi
  "12. Bệnh có sẵn" là tiêu đề đơn vị), định nghĩa = text chunk bỏ header và chữ "Là" mở đầu; không dùng LLM; định nghĩa bị tách nhiều chunk (_P1, _P2…) được nối lại; source = chunk_id phần đầu.
- aliases: phần trong ngoặc cuối thuật ngữ do quy tắc ghi ("Hợp đồng bảo hiểm (HĐBH)"), cộng data/manual/glossary_aliases.csv (term, scope, aliases cách nhau bằng ";") sau khi người duyệt.
- data/manual/glossary_term_overrides.csv (chunk_id, term, definition): sửa tay chỗ code không tách được.

glossary.json không nằm trong processed/{ver} (v1 đã đóng băng) mà commit vào repo; _meta.data_version ghi
phiên bản chunk mà các source trỏ tới.

Chạy ở gốc repo (WSL):
    PYTHONPATH=. python -m src.ingest.glossary --processed data/processed/v1 --out data/glossary.json
"""
import argparse, csv, json, re, sys, unicodedata
from datetime import datetime
from pathlib import Path

import yaml

GENERAL_CSV = Path("data/manual/glossary_general_candidates.csv")
ALIASES_CSV = Path("data/manual/glossary_aliases.csv")
OVERRIDES_CSV = Path("data/manual/glossary_term_overrides.csv")
SOURCES_CSV = Path("data/raw/sources.csv")
# Văn bản trong cột source của CSV general → file trong sources.csv (lấy effective_date)
LEGAL_DOCS = {"VBHN 31/VBHN-VPQH": "legal/vbhn_31_2026_luat_kdbh.pdf", "TT 67/2023/TT-BTC": "legal/tt_67_2023.pdf"}

NUM_HEAD = re.compile(r"^\s*\d+(?:\.\d+)*\s*[.)]\s*")
QUOTES = "“”\"'‘’«»"
SEP = re.compile(r"\s*:\s+|\s*:$|\s+là\s+|\s+được hiểu là\s+")


def norm_term(t: str) -> str:
    """Khóa so khớp thuật ngữ: NFC, thường, bỏ ngoặc kép và khoảng trắng thừa."""
    t = unicodedata.normalize("NFC", t).strip(QUOTES + " .:").lower()
    return re.sub(r"\s+", " ", t)


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def read_csv(path: Path) -> list[dict]:
    return list(csv.DictReader(open(path, encoding="utf-8-sig"))) if path.exists() else []


def split_definition(body: str) -> tuple[str, str] | None:
    """'12. Bệnh có sẵn: là …' → ('Bệnh có sẵn', '…'). Thuật ngữ phải ngắn (≤ 15 từ) mới nhận."""
    text = NUM_HEAD.sub("", re.sub(r"\s+", " ", body)).strip()
    m = SEP.search(text[:200])
    if not m:
        return None
    term, definition = text[:m.start()].strip(QUOTES + " "), text[m.end():].strip()
    definition = re.sub(r"^là\s+", "", definition)
    if not term or len(term.split()) > 15 or not definition:
        return None
    return term, definition


def clean_body(body: str) -> str:
    """Bỏ rác OCR đầu đoạn và chữ 'Là' mở đầu định nghĩa; gộp khoảng trắng."""
    text = re.sub(r"\s+", " ", body).strip()
    text = re.sub(r"^[^\wÀ-ỹ]+", "", text)
    return re.sub(r"^là\s*[:,]?\s*", "", text, flags=re.I)


def term_from_heading(chunk: dict) -> tuple[str, str] | None:
    """Chunker coi dòng '12. Bệnh có sẵn' là tiêu đề đơn vị: thuật ngữ = cấp cuối của section_path.
    Tiêu đề có cả định nghĩa ('12. Bệnh có sẵn: là …') thì trả phần sau làm đầu định nghĩa."""
    last = chunk.get("section_path", "").split(" > ")[-1].strip()
    if not NUM_HEAD.match(last):
        return None
    head = NUM_HEAD.sub("", last).strip()
    if got := split_definition(head):
        return got
    term = head.strip(QUOTES + " :.")
    return (term, "") if term and len(term.split()) <= 15 else None


def split_paren(term: str) -> tuple[str, list[str]]:
    """'Hợp đồng bảo hiểm (HĐBH)' → ('Hợp đồng bảo hiểm', ['HĐBH']); ngoặc ở cuối thuật ngữ là tên gọi khác do
    chính quy tắc ghi ('Điều trị nội trú (Nằm viện)'), nên đưa vào aliases không cần duyệt."""
    m = re.match(r"^(.+?)\s*\(([^()]{1,40})\)$", term.strip())
    return (m[1].strip(), [m[2].strip()]) if m else (term, [])


def id_key(cid: str, prefix: str) -> tuple[int, str]:
    rest = cid[len(prefix):]
    n = re.match(r"\d+", rest)
    return int(n[0]), rest[len(n[0]):]


def product_entries(chunks: list[dict], cfg_dir: Path, overrides: dict) -> tuple[list[dict], list[str]]:
    entries, errors = [], []
    for cfg_path in sorted(cfg_dir.glob("*.yaml")):
        pc = yaml.safe_load(open(cfg_path, encoding="utf-8"))
        d = (pc.get("checks") or {}).get("definitions")
        if not d:
            continue
        P, prefix = pc["product_code"], d["prefix"]
        groups: dict[int, list[dict]] = {}
        for c in chunks:
            if c["chunk_id"].startswith(prefix) and re.match(r"\d", c["chunk_id"][len(prefix):]):
                groups.setdefault(id_key(c["chunk_id"], prefix)[0], []).append(c)
        if sorted(groups) != list(range(1, d["count"] + 1)):
            errors.append(f"{P}: thấy {len(groups)} định nghĩa, config ghi {d['count']}")
        for n in sorted(groups):
            parts = sorted(groups[n], key=lambda c: id_key(c["chunk_id"], prefix))
            first = parts[0]
            body = "\n".join(c["text"].split("\n", 1)[1] if c["text"].startswith("[") else c["text"] for c in parts)
            ov = overrides.get(first["chunk_id"])
            if ov:
                got = (ov["term"], ov["definition"] or clean_body(body))
            elif head := term_from_heading(first):
                got = (head[0], clean_body(" ".join(filter(None, [head[1], body]))))
            else:
                got = split_definition(body)
            if not got or not got[1]:
                errors.append(f"{first['chunk_id']}: không tách được thuật ngữ: {body[:80]!r}")
                continue
            term, aliases = split_paren(got[0])
            entries.append({"term": term, "aliases": aliases, "definition": got[1], "scope": P,
                            "source": first["chunk_id"], "effective_date": first["effective_date"],
                            "parts": [c["chunk_id"] for c in parts]})
    return entries, errors


def general_entries(rows: list[dict], sources: list[dict]) -> tuple[list[dict], list[str]]:
    eff = {s["file"]: s["effective_date"] for s in sources}
    entries, errors = [], []
    for r in rows:
        if r.get("keep", "").strip() != "1":
            continue
        doc = next((f for key, f in LEGAL_DOCS.items() if key in r["source"]), None)
        if not doc or doc not in eff:
            errors.append(f"general '{r['term']}': không xác định được văn bản trong sources.csv ({r['source']})")
            continue
        if not r["term"].strip():
            errors.append(f"general: dòng keep=1 thiếu term ({r['source']})")
            continue
        e = {"term": r["term"].strip(), "aliases": [], "definition": r["definition"].strip(), "scope": "general",
             "source": r["source"], "effective_date": eff[doc]}
        if r.get("amended_by", "").strip():
            e["amended_by"] = r["amended_by"].strip()
        entries.append(e)
    return entries, errors


def apply_aliases(entries: list[dict], rows: list[dict]) -> list[str]:
    idx = {(norm_term(e["term"]), e["scope"]): e for e in entries}
    errors = []
    for r in rows:
        e = idx.get((norm_term(r["term"]), r["scope"].strip()))
        if not e:
            errors.append(f"alias: không có mục '{r['term']}' scope {r['scope']}")
            continue
        e["aliases"] = list(dict.fromkeys(e["aliases"] + [a.strip() for a in r["aliases"].split(";") if a.strip()]))
    return errors


def check(entries: list[dict], chunk_ids: set[str]) -> list[str]:
    errors, seen = [], set()
    for e in entries:
        key = (norm_term(e["term"]), e["scope"])
        if key in seen:
            errors.append(f"trùng thuật ngữ '{e['term']}' trong scope {e['scope']}")
        seen.add(key)
        if e["scope"] != "general" and e["source"] not in chunk_ids:
            errors.append(f"{e['term']}: source {e['source']} không có trong kho chunk")
    return errors


def build(processed: Path, cfg_dir: Path = Path("configs/products")) -> tuple[dict, list[str]]:
    chunks = read_jsonl(processed / "chunks.jsonl")
    overrides = {r["chunk_id"]: r for r in read_csv(OVERRIDES_CSV)}
    prod, e1 = product_entries(chunks, cfg_dir, overrides)
    gen, e2 = general_entries(read_csv(GENERAL_CSV), read_csv(SOURCES_CSV))
    entries = gen + prod
    errors = e1 + e2 + apply_aliases(entries, read_csv(ALIASES_CSV)) + check(entries, {c["chunk_id"] for c in chunks})
    counts = {}
    for e in entries:
        counts[e["scope"]] = counts.get(e["scope"], 0) + 1
    meta = {"data_version": processed.name, "built_at": datetime.now().isoformat(timespec="seconds"),
            "counts": counts, "total": len(entries),
            "general_source": str(GENERAL_CSV), "note": "scope sản phẩm: source = chunk_id định nghĩa trong processed/{data_version}"}
    return {"_meta": meta, "entries": entries}, errors


def load(path: str | Path = "data/glossary.json") -> list[dict]:
    return json.load(open(path, encoding="utf-8"))["entries"]


def lookup(entries: list[dict], term: str, products: list[str] | None = None) -> list[dict]:
    """Định nghĩa của term (khớp term hoặc alias): ưu tiên scope thuộc products; không có mới trả general."""
    k = norm_term(term)
    hits = [e for e in entries if k == norm_term(e["term"]) or k in map(norm_term, e["aliases"])]
    own = [e for e in hits if products and e["scope"] in products]
    return own or [e for e in hits if e["scope"] == "general"] or ([] if products else hits)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed", type=Path, default=Path("data/processed/v1"))
    ap.add_argument("--out", type=Path, default=Path("data/glossary.json"))
    a = ap.parse_args()
    glossary, errors = build(a.processed)
    print(f"{glossary['_meta']['total']} mục: {glossary['_meta']['counts']}")
    if errors:
        sys.exit("Lỗi, chưa ghi file:\n  " + "\n  ".join(errors))
    json.dump(glossary, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"→ {a.out}")


if __name__ == "__main__":
    main()
