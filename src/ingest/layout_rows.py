"""Dựng lại bảng 2 cột (tên | nội dung) trải nhiều trang từ toạ độ dòng của pdftotext, thay bảng Docling.

Dùng khi TableFormer đặt sai ranh giới dòng (C37 Chương II: bullet cuối của bệnh 1 rơi vào dòng bệnh 2).
Mốc dòng = dòng cột trái khớp "N." ; mọi dòng cột phải có yMin ≥ yMin(mốc) − tol thuộc mục N cho tới mốc kế tiếp,
kể cả khi sang trang. Đầu ra là Rec "N. Tên" + Rec nội dung, để build_units nhận mục M{n} như numbered_units.

Cấu hình file (YAML):
    layout_rows: {pages: [9, 22], split_x: 95, stop: "^Ghi chú"}
"""
from __future__ import annotations

import html
import re
import subprocess
import unicodedata

LINE = re.compile(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="[\d.]+" yMax="[\d.]+">(.*?)</line>', re.S)
WORDTXT = re.compile(r">([^<]*)</word>")
PAGE = re.compile(r"<page [^>]*>(.*?)</page>", re.S)
MARK = re.compile(r"^(\d+)\.\s*(.*)$")
FOOTER = re.compile(r"^-\s*\d+\s*-$")
NEWLINE_BEFORE = re.compile(r"^(?:[•◦\-–+]|[ivx]+\.|[a-zđ][.)]|[A-Z]\)|Loại [IVX]+:)\s*")
LIGATURES = str.maketrans({"ﬁ": "fi", "ﬂ": "fl", "ﬀ": "ff"})


def page_lines(pdf: str, first: int, last: int) -> list[tuple[int, float, float, str]]:
    """(trang, x, y, text) của từng dòng, toạ độ tính trong trang đã cắt."""
    out = subprocess.run(["pdftotext", "-bbox-layout", "-f", str(first), "-l", str(last), pdf, "-"],
                         capture_output=True, text=True, check=True).stdout
    lines = []
    for p, body in enumerate(PAGE.findall(out), first):
        for m in LINE.finditer(body):
            txt = " ".join(html.unescape(w) for w in WORDTXT.findall(m[3]))
            txt = unicodedata.normalize("NFC", txt).translate(LIGATURES).strip()
            if txt and not FOOTER.match(txt):
                lines.append((p, float(m[1]), float(m[2]), txt))
    return sorted(lines, key=lambda t: (t[0], t[2], t[1]))


def join_lines(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Nối dòng thành đoạn [(trang của dòng đầu, đoạn)]: đoạn mới trước bullet/đánh số;
    nối từ bị ngắt bằng '-' ở cuối dòng ("mela-" + "noma")."""
    paras: list[list] = []
    for page, ln in lines:
        if not paras or NEWLINE_BEFORE.match(ln):
            paras.append([page, ln])
        elif paras[-1][1].endswith("-") and ln[:1].islower():
            paras[-1][1] = paras[-1][1][:-1] + ln
        else:
            paras[-1][1] += " " + ln
    return [(p, t) for p, t in paras]


def layout_rows(pdf: str, pages: tuple[int, int], split_x: float, stop: str | None = None,
                tol: float = 3.0) -> list[dict]:
    """[{n, name, body: [(trang, đoạn)], page}] theo thứ tự đọc; page = trang (đã cắt) của mốc.

    Hai lượt: (1) tìm mốc "N." ở cột trái (số tăng liên tục); (2) gán mỗi dòng cho mốc cuối cùng có
    (trang, y − tol) ≤ (trang, y) của dòng, nên dòng đầu cột phải lệch baseline vài pt vẫn đúng mục.
    """
    lines = page_lines(pdf, *pages)
    if stop:
        stop_re = re.compile(stop)
        cut = next((i for i, t in enumerate(lines) if stop_re.match(t[3])), len(lines))
        lines = lines[:cut]
    marks = []
    for p, x, y, txt in lines:
        if x < split_x and (m := MARK.match(txt)) and int(m[1]) == (marks[-1]["n"] + 1 if marks else 1):
            marks.append({"n": int(m[1]), "page": p, "y": y, "name": [m[2]] if m[2] else [], "body": []})
    for p, x, y, txt in lines:
        owner = None
        for mk in marks:
            if (mk["page"], mk["y"] - tol) <= (p, y):
                owner = mk
            else:
                break
        if owner is None or (x < split_x and MARK.match(txt) and (p, y) == (owner["page"], owner["y"])):
            continue                                       # header bảng trước mốc đầu, hoặc chính dòng mốc
        if x < split_x:                                    # tên có thể sang trang (C37 bệnh 34)
            owner["name"].append(txt)
        else:
            owner["body"].append((p, txt))
    return [{"n": r["n"], "name": re.sub(r"\s*/\s*", "/", " ".join(r["name"])), "body": join_lines(r["body"]), "page": r["page"]}
            for r in marks]
