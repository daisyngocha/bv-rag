"""Trích điều "Giải thích từ ngữ" trong văn bản pháp luật KDBH ra CSV ứng viên cho glossary general (bản nháp để duyệt tay).

Chạy ở gốc repo, trên WSL (cần pdftotext):
    python scripts/legal_terms.py data/raw/legal/vbhn_31_2026_luat_kdbh.pdf \
        --source "Luật Kinh doanh bảo hiểm (VBHN 31/VBHN-VPQH)" >> data/manual/glossary_general_candidates.csv
    python scripts/legal_terms.py data/raw/legal/tt_67_2023.pdf --source "TT 67/2023/TT-BTC" --header-off >> ...

Mỗi khoản một dòng: term, definition, source ("<văn bản>, Điều N, khoản K"), amended_by, keep, review.
- term: phần trước " là " hoặc ":" đầu tiên; không tách được thì để trống, review ghi lý do.
- Dòng chú thích của VBHN ("được sửa đổi, bổ sung/bãi bỏ theo…") bị gỡ khỏi definition và đưa vào amended_by
  để đối chiếu; vị trí chú thích trong PDF không chắc chắn nên mọi dòng có amended_by đều đánh dấu review.
- Script không quyết định giữ mục nào: cột keep để trống, người duyệt điền 1.
Đọc lại từng dòng với PDF trước khi dùng: pdftotext có thể ngắt sai dòng, dính số chú thích vào chữ.
"""
import argparse, csv, re, subprocess, sys

ARTICLE = re.compile(r"^\s*Điều\s+(\d+)\s*[.:]\s*(.*)$")
KHOAN = re.compile(r"^\s*(\d+)\s*\.\s*(\S.*)$")
KHOAN_ALONE = re.compile(r"^\s*(\d+)\s*\.\s*$")          # số khoản nằm riêng một dòng
NUM_START = re.compile(r"^\s*\d+\s*[.)]?\s*\S")
FOOTNOTE = re.compile(r"(được|bị)\s+(sửa đổi|bổ sung|bãi bỏ|thay thế)|theo quy định tại .*(Luật|Thông tư|Nghị định) số", re.I)
PAGE_NO = re.compile(r"^\s*\d{1,3}\s*$")
COLS = ["term", "definition", "source", "amended_by", "keep", "review"]


def pdf_lines(path: str) -> list[str]:
    txt = subprocess.run(["pdftotext", path, "-"], capture_output=True, text=True, check=True).stdout
    return [l.replace("\f", "").rstrip() for l in txt.splitlines()]


def find_article(lines: list[str], title: str) -> tuple[str, list[str]]:
    """Trả về (số Điều, các dòng thân) của điều đầu tiên có tiêu đề chứa title."""
    for i, l in enumerate(lines):
        m = ARTICLE.match(l)
        if m and title.lower() in m.group(2).lower():
            body = []
            for l2 in lines[i + 1:]:
                if ARTICLE.match(l2):
                    break
                body.append(l2)
            return m.group(1), body
    hits = [f"   dòng {i + 1}: {l.strip()[:90]}" for i, l in enumerate(lines) if title.lower() in l.lower()]
    sys.exit(f"Không thấy dòng 'Điều N. {title}'" + (":\n" + "\n".join(hits) if hits else f"; không dòng nào chứa '{title}'"))


def split_khoan(body: list[str]) -> list[dict]:
    items, notes = [], []
    for i, l in enumerate(body):
        if not l.strip() or PAGE_NO.match(l):
            continue
        if FOOTNOTE.search(l):
            notes.append(l.strip())
            if items:
                items[-1]["notes"].append(l.strip())
            continue
        m = KHOAN.match(l) or KHOAN_ALONE.match(l)
        expected = items[-1]["no"] + 1 if items else 1
        if m and int(m.group(1)) == expected:
            items.append({"no": expected, "text": (m.group(2) if m.re is KHOAN else "").strip(), "notes": []})
            continue
        if m or NUM_START.match(l):
            print(f"   ! dòng {i + 1} bắt đầu bằng số nhưng không phải khoản {expected}: {l.strip()[:90]}", file=sys.stderr)
        if items:
            items[-1]["text"] += " " + l.strip()
    return items


def to_row(item: dict, source: str, dieu: str) -> dict:
    text = re.sub(r"\s+", " ", item["text"]).strip()
    m = re.match(r"(.+?)\s+là\s+(.+)", text) or re.match(r"(.+?)\s*:\s*(.+)", text)
    review = []
    if not m or len(m.group(1).split()) > 12:
        term, definition = "", text
        review.append("không tách được thuật ngữ")
    else:
        term, definition = m.group(1).strip(), m.group(2).strip()
        if re.search(r"\d$", term):
            review.append("thuật ngữ có số ở cuối (số chú thích?)")
    if item["notes"]:
        review.append("có chú thích sửa đổi: kiểm tra với PDF")
    return {"term": term, "definition": definition, "source": f"{source}, Điều {dieu}, khoản {item['no']}",
            "amended_by": " | ".join(item["notes"]), "keep": "", "review": "; ".join(review)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--source", required=True, help='tên văn bản ghi vào cột source, ví dụ "TT 67/2023/TT-BTC"')
    ap.add_argument("--title", default="Giải thích từ ngữ")
    ap.add_argument("--header-off", action="store_true", help="không in dòng tiêu đề (khi nối thêm vào file đã có)")
    a = ap.parse_args()

    lines = pdf_lines(a.pdf)
    if not any(l.strip() for l in lines):
        sys.exit("pdftotext không ra chữ: PDF không có lớp chữ (bản scan), cần OCR")
    dieu, body = find_article(lines, a.title)
    items = split_khoan(body)
    w = csv.DictWriter(sys.stdout, fieldnames=COLS, lineterminator="\n")
    if not a.header_off:
        w.writeheader()
    for it in items:
        w.writerow(to_row(it, a.source, dieu))
    flagged = sum(bool(to_row(it, a.source, dieu)["review"]) for it in items)
    print(f"Điều {dieu}: {len(items)} khoản, {flagged} dòng cần xem (cột review)", file=sys.stderr)


if __name__ == "__main__":
    main()
