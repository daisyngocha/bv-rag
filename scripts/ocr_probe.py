"""Probe OCR toàn văn: so tessdata fast (apt) với best trên cùng dải trang; đếm cặp thuật ngữ đúng/sai.

    PYTHONPATH=. python scripts/ocr_probe.py data/raw/products/BTB/btb_quytac.pdf --pages 4-45
    PYTHONPATH=. python scripts/ocr_probe.py data/raw/products/BTB/btb_quytac.pdf --pages 41-45 --psm 6

Kết quả: bảng in ra màn hình + logs/ocr_probe/{stem}_{pages}_{fast|best}_psm{n}.txt (mỗi trang ngăn bằng \\f)
và logs/ocr_probe/{stem}_{pages}_psm{n}.json để ghi vào docs/ocr_probe_*.md.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from src.ingest.chunker import clean_text
from src.ingest.ocr import ocr_lines

# (đúng, [chuỗi sai do OCR]) — chuỗi sai không bao giờ hợp lệ trong văn bản bảo hiểm
PAIRS = [("chi phí", ["chỉ phí"]), ("chi trả", ["chỉ chỉ trả", "đồng chỉ trả", "đã chỉ trả"]),
         ("tổ chức", ["tô chức"]), ("bảo hiểm", ["bảo hiêm", "bảo hiếm", "bảo hiềm"]), ("tổn thất", ["tôn thất"]),
         ("ốm đau", ["óm đau"]), ("bác sĩ", ["bácsĩ"]), ("tai nạn", ["tainạn"])]
# "chỉ trả" còn lại có thể đúng ("chỉ trả" = chỉ chi trả) hoặc là OCR sai của "chi trả" → không sửa tự động, đọc tay
AMBIG = re.compile(r"(?<!chỉ )(?<!đồng )(?<!đã )chỉ trả", re.I)
PCT = re.compile(r"\d+(?:,\d+)?\s?%")


def tess_info(tessdata: str | None) -> str:
    ver = subprocess.run(["tesseract", "--version"], capture_output=True, text=True)
    return f'{(ver.stdout or ver.stderr).splitlines()[0]} | {tessdata or "tessdata hệ thống (apt)"}'


def score(text: str) -> dict:
    low = text.lower()
    return {ok: {"ok": low.count(ok), "bad": sum(low.count(b) for b in bads)} for ok, bads in PAIRS}


def ambiguous(texts: list[str], pages: list[int]) -> list[str]:
    """Ngữ cảnh "chỉ trả" chưa phân định, kèm trang scan, để so với ảnh trang."""
    return [f"tr.{p}: …{clean_text(t[max(m.start() - 40, 0):m.end() + 30])}…"
            for p, t in zip(pages, texts) for m in AMBIG.finditer(t)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--pages", default="4-45", help="dải trang scan, ví dụ 4-45")
    ap.add_argument("--psm", type=int)
    ap.add_argument("--dpi", type=int, default=216)
    ap.add_argument("--best", default=str(Path.home() / "tessdata_best"))
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="logs/ocr_probe")
    a = ap.parse_args()

    lo, hi = map(int, a.pages.split("-"))
    pages, stem = list(range(lo, hi + 1)), Path(a.pdf).stem
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    td = Path(a.best, "vie.traineddata")
    if not td.exists() or td.stat().st_size < 100_000:            # tải lỗi thường ra file HTML/JSON vài trăm byte
        raise SystemExit(f"{td} không có hoặc hỏng ({td.stat().st_size if td.exists() else 0} byte); tải lại tessdata_best")

    res = {}
    for name, td in (("fast", None), ("best", a.best)):
        t = time.time()
        with ThreadPoolExecutor(a.workers) as ex:
            texts = list(ex.map(lambda p: "\n".join(ocr_lines(a.pdf, p, dpi=a.dpi, psm=a.psm, tessdata=td)), pages))
        sec = (time.time() - t) * a.workers / len(pages)          # giây CPU/trang ≈ thời gian khi chạy tuần tự
        raw = "\n\f".join(texts)
        (out / f"{stem}_{a.pages}_{name}_psm{a.psm or 3}.txt").write_text(raw, encoding="utf-8")
        txt = clean_text(raw)
        amb = ambiguous(texts, pages)
        (out / f"{stem}_{a.pages}_{name}_psm{a.psm or 3}_chitra.txt").write_text("\n".join(amb), encoding="utf-8")
        res[name] = {"engine": tess_info(td), "s_per_page": round(sec, 1), "chars": len(txt),
                     "pct": len(PCT.findall(txt)), "pairs": score(txt), "chi_tra_ambiguous": len(amb)}

    print(f"\n{stem} trang {a.pages}, {a.dpi} dpi, psm {a.psm or 3}")
    for n, r in res.items():
        print(f"  {n}: {r['engine']}")
    print(f"\n  {'thuật ngữ':12} {'fast đúng/sai':>14} {'best đúng/sai':>14}")
    for ok, _ in PAIRS:
        f, b = res["fast"]["pairs"][ok], res["best"]["pairs"][ok]
        print(f"  {ok:12} {f['ok']:>8}/{f['bad']:<5} {b['ok']:>8}/{b['bad']:<5}")
    for k, lab in (("chi_tra_ambiguous", "'chỉ trả' cần đọc tay"), ("chars", "số ký tự"),
                   ("pct", "số giá trị %"), ("s_per_page", "giây/trang (1 luồng)")):
        print(f"  {lab:20} {res['fast'][k]:>6} {res['best'][k]:>14}")
    for n in res:
        bad = sum(v["bad"] for v in res[n]["pairs"].values())
        tot = bad + sum(v["ok"] for v in res[n]["pairs"].values())
        print(f"  {n}: tổng lỗi đã biết {bad}/{tot} ({bad / max(tot, 1):.1%})")
    json.dump({"pdf": a.pdf, "pages": a.pages, "dpi": a.dpi, "psm": a.psm or 3, **res},
              open(out / f"{stem}_{a.pages}_psm{a.psm or 3}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
