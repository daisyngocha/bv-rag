"""Chép tài liệu sản phẩm từ ổ Windows vào data/raw/products/{product}/ và thêm dòng vào sources.csv."""
import argparse, csv, shutil, unicodedata, re
from datetime import datetime
from pathlib import Path

COLS = ["product_code", "company", "doc_type", "url", "downloaded_at", "effective_date", "file"]
RULES = [(r"quy.?tac", "quy_tac"), (r"dieu.?khoan", "dieu_khoan"), (r"bieu.?phi|bang.?phi", "bang_phi"),
         (r"quyen.?loi", "bang_quyen_loi"), (r"brochure|to.?roi|leaflet", "brochure"), (r"faq|hoi.?dap", "faq")]

def ascii_lower(s: str) -> str:
    s = unicodedata.normalize("NFD", s).replace("đ", "d").replace("Đ", "D")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()

def doc_type(name: str) -> str:
    n = ascii_lower(name)
    return next((dt for pat, dt in RULES if re.search(pat, n)), "CHECK")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("--product", required=True)
    ap.add_argument("--company", required=True); ap.add_argument("--effective-date", default="")
    a = ap.parse_args()

    raw = Path("data/raw"); dst = raw / "products" / a.product; dst.mkdir(parents=True, exist_ok=True)
    csv_path = raw / "sources.csv"
    existing = set()
    if csv_path.exists():
        with csv_path.open(encoding="utf-8") as f:
            existing = {r["file"] for r in csv.DictReader(f)}

    rows = []
    for p in sorted(Path(a.src).iterdir()):
        if not p.is_file() or p.name.endswith(":Zone.Identifier"):
            continue
        rel = f"products/{a.product}/{p.name}"
        if rel in existing:
            print("bỏ qua (đã có):", rel); continue
        shutil.copy2(p, dst / p.name)                      # copy2 giữ mtime gốc
        rows.append({"product_code": a.product, "company": a.company, "doc_type": doc_type(p.name),
                     "url": "", "downloaded_at": datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d"),
                     "effective_date": a.effective_date, "file": rel})

    new_file = not csv_path.exists()
    with csv_path.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        if new_file: w.writeheader()
        w.writerows(rows)
    for r in rows: print(r["doc_type"], "|", r["downloaded_at"], "|", r["file"])
    print(f"Đã thêm {len(rows)} dòng vào {csv_path}. Còn phải điền tay: url, các dòng CHECK.")

if __name__ == "__main__":
    main()
