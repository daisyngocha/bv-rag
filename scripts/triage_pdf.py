"""Triage cấu trúc PDF quy tắc: mục lục, tiêu đề cấp 1, thống kê đánh số cấp dưới.
Chỉ để định hướng; truth.json vẫn lập tay.
"""
import argparse
import collections
import re
import subprocess
import unicodedata

ap = argparse.ArgumentParser()
ap.add_argument("pdf")
ap.add_argument("--toc", type=int, default=0, help="trang mục lục (0 = bỏ qua)")
ap.add_argument("--start", type=int, default=1)
ap.add_argument("--2up", dest="two_up", action="store_true", help="tách đôi trang PDF 2-up")
ap.add_argument("--dump", default="", help="regex trên nhãn phần, vd 'PHẦN (I|II|V|VI)@'")
args = ap.parse_args()

info = subprocess.run(["pdfinfo", args.pdf], capture_output=True, text=True).stdout
n = int(re.search(r"Pages:\s+(\d+)", info).group(1))

# Đọc kích thước (width, height) của từng trang từ pdfinfo
info_all = subprocess.run(["pdfinfo", "-f", "1", "-l", str(n), args.pdf], capture_output=True, text=True).stdout
sizes = {}
for m in re.finditer(r"Page\s+(\d+)\s+size:\s+([\d.]+)\s+x\s+([\d.]+)", info_all):
    sizes[int(m.group(1))] = (float(m.group(2)), float(m.group(3)))

def extract_text(p, x=0, y=0, width=None, height=None):
    cmd = ["pdftotext", "-f", str(p), "-l", str(p), "-layout"]
    if width is not None and height is not None:
        cmd += ["-x", str(int(x)), "-y", str(int(y)), "-W", str(int(width)), "-H", str(int(height))]
    cmd += [args.pdf, "-"]
    res = subprocess.run(cmd, capture_output=True, text=True).stdout
    return unicodedata.normalize("NFC", res).replace("Ð", "Đ")

def pages():
    for p in range(args.start, n + 1):
        w, h = sizes[p]
        # Nếu trang là khổ đơn (ví dụ trang bìa width nhỏ hơn đáng kể), không tách đôi
        is_single_page = w < 500  # Ngưỡng nhận diện trang đơn/bìa
        halves = [(0, w / 2), (w / 2, w / 2)] if (args.two_up and not is_single_page) else [(0, w)]
        for j, (x, ww) in enumerate(halves):
            t = extract_text(p, x=x, y=0, width=ww, height=h)
            lab = f"g{2 * p - 2 + j}" if (args.two_up and not is_single_page) else f"p{p}"
            yield lab, t

if args.toc:
    print(f"=== p{args.toc} (mục lục) ===\n{extract_text(args.toc)}")

print("=== Cấp 1 (không neo đầu dòng) ===")
TOP_ANY = re.compile(r"(PHẦN\s+[IVX]+|CHƯƠNG\s+[IVX\d]+|PHỤ LỤC\s*\d*)")
for lab, txt in pages():
    for i, line in enumerate(txt.splitlines()):
        for m in TOP_ANY.finditer(line):
            print(f"  {lab} L{i} col{m.start()}: {line.strip()[:90]}")

TOP = re.compile(r"^\s*(PHẦN\s+[IVX]+|CHƯƠNG\s+[IVX\d]+|PHỤ LỤC)")
LVL = re.compile(
    r"^\s*(\d+\.\d+\.\d+\.?|\d+\.\d+\.?|\d+\.|\d+\)|[a-zđ]\)|[A-Z]\.|"
    r"(?:Mục|MỤC|Phần|PHẦN|Điều|ĐIỀU)\s+[A-Z\d]+|-|•|\+)\s"
)
cur, cnt, ex = "pre", collections.defaultdict(collections.Counter), {}
for lab, txt in pages():
    for line in txt.splitlines():
        if m := TOP.match(line):
            cur = f"{m.group(1)}@{lab}"
            continue
        if m := LVL.match(line):
            k = re.sub(r"\d+", "N", m.group(1))
            cnt[cur][k] += 1
            ex.setdefault((cur, k), f"{lab}: {line.strip()[:70]}")
            if args.dump and re.search(args.dump, cur) and k in {"N.", "N.N.", "N.N.N.", "A.", "B.", "a)"}:
                print(f"  [{cur.split('@')[0]}] {lab}: {line.strip()[:90]}")

print("\n=== Đánh số cấp dưới theo từng phần ===")
for sec, c in cnt.items():
    print(f"\n{sec}")
    for k, v in c.most_common(8):
        print(f"  {k:12} {v:4}  {ex[(sec, k)]}")
