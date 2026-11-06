"""Đánh giá OCR bằng trang "song sinh": trang scan có bản gốc lớp chữ (BTB: quy tắc trang 48–50 = btb_bangquyenloi.pdf).
Đo precision/recall/F1 theo túi từ (có dấu, không phụ thuộc thứ tự dòng/bảng) cho tessdata fast/best,
trước và sau text_fixes ứng viên. Sửa nào làm GIẢM precision là sửa sai → bỏ.

    PYTHONPATH=. python scripts/ocr_twin_eval.py data/raw/products/BTB/btb_quytac.pdf --pages 48-50 \\
        --gt data/raw/products/BTB/btb_bangquyenloi.pdf
"""
from __future__ import annotations

import argparse
import re
import subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from src.ingest.chunker import clean_text
from src.ingest.ocr import WORD, ocr_lines

# Ứng viên text_fixes. Nguyên tắc: từ không tồn tại → sửa độc lập; nhầm sang từ có thật → chỉ sửa trong ngữ cảnh.
FIXES = [
    [r"\b([Cc])h[ỉí] phí\b", r"\1hi phí"],
    [r"\bChỉ trả\b", "Chi trả"],                       # đầu câu/ô bảng: "Chi trả theo chi phí thực tế"
    [r"\b(chỉ|đồng|đã|tự|Đồng) chỉ trả\b", r"\1 chi trả"],
    [r"\b([Bb]ảo|[Nn]guy) hi[êếềệ]m\b", r"\1 hiểm"],
    [r"\b([Tt])ô chức\b", r"\1ổ chức"],
    [r"\b([Tt])ôn thất\b", r"\1ổn thất"],
    [r"\b[Óó]m đau\b", "ốm đau"],
    [r"\b([Tt])uôi\b", r"\1uổi"],
    [r"\b([Tt])hưc\b", r"\1hực"],
    [r"\b([Cc])âp\b", r"\1ấp"],
    [r"\b([Bb])[ỗồ] sung\b", r"\1ổ sung"],
    [r"\b([Đđ])iêu (trị|kiện|khoản)\b", r"\1iều \2"],
    [r"\b([Qq])uyên (lợi|hạn)\b", r"\1uyền \2"],
    [r"\b([Cc]ó|[Cc]ơ) thê\b", r"\1 thể"],
    [r"\b([Cc])h[âầấ]n đoán\b", r"\1hẩn đoán"],
    [r"\b([Tt])ôi (đa|thiểu)\b", r"\1ối \2"],
    [r"\b([Nn])ghĩ (điều|việc|ốm)\b", r"\1ghỉ \2"],
    [r"\b([Tt])hai sẵn\b", r"\1hai sản"],
]


def bag(t: str) -> Counter:
    return Counter(w.lower() for w in WORD.findall(clean_text(t)))


def prf(o: Counter, r: Counter) -> tuple[float, float, float]:
    hit = sum((o & r).values())
    p, rc = hit / max(sum(o.values()), 1), hit / max(sum(r.values()), 1)
    return p, rc, 2 * p * rc / max(p + rc, 1e-9)


def apply(t: str, fixes) -> tuple[str, Counter]:
    n = Counter()
    for pat, rep in fixes:
        t, k = re.subn(pat, rep, t)
        n[pat] += k
    return t, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf"); ap.add_argument("--pages", default="48-50"); ap.add_argument("--gt", required=True)
    ap.add_argument("--dpi", type=int, default=216); ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--best", default=str(Path.home() / "tessdata_best"))
    a = ap.parse_args()
    lo, hi = map(int, a.pages.split("-"))
    R = bag(subprocess.run(["pdftotext", a.gt, "-"], capture_output=True, text=True, check=True).stdout)
    print(f"{Path(a.pdf).stem} trang {a.pages} ↔ {Path(a.gt).name} ({sum(R.values())} từ), {a.dpi} dpi\n")
    print(f"  {'':5} {'P':>6} {'R':>6} {'F1':>6} | sau text_fixes: {'P':>6} {'R':>6} {'F1':>6} | sai nhiều nhất còn lại")
    for name, td in (("fast", None), ("best", a.best)):
        with ThreadPoolExecutor(a.workers) as ex:
            raw = "\n".join(ex.map(lambda p: "\n".join(ocr_lines(a.pdf, p, dpi=a.dpi, tessdata=td)), range(lo, hi + 1)))
        fixed, n = apply(raw, FIXES)
        b0, b1 = bag(raw), bag(fixed)
        p0, r0, f0 = prf(b0, R)
        p1, r1, f1 = prf(b1, R)
        print(f"  {name:5} {p0:6.1%} {r0:6.1%} {f0:6.1%} |                 {p1:6.1%} {r1:6.1%} {f1:6.1%} | "
              + ", ".join(f"{w}×{c}" for w, c in (b1 - R).most_common(10)))
        # sửa nào làm tăng từ sai (precision giảm): đo riêng từng sửa
        for pat, rep in FIXES:
            if n[pat]:
                d = prf(bag(apply(raw, [[pat, rep]])[0]), R)[0] - p0
                if d < 0:
                    print(f"        !! {pat} ({n[pat]} lần) làm giảm precision {d:+.2%} → bỏ")


if __name__ == "__main__":
    main()
