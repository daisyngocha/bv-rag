"""Chunking theo cấu trúc cho tài liệu sản phẩm bảo hiểm (ĐA1).

Đầu vào : DoclingDocument đã parse (split_2up + pypdfium2 + drop_offpage_items) và cấu hình file.
Đầu ra  : list[dict] theo schema chunk (skill quy ước, mục 6) + báo cáo đối chiếu mục lục.

Luồng: linearize (item → Rec, bỏ trang skip, làm sạch) → toc_from_pdf + reconcile (chèn tiêu đề
bị mất, ví dụ CHƯƠNG IV trong khung màu) → build_units (đơn vị = mục/định nghĩa/QL bổ sung/phần A-B)
→ unit_to_chunks (≤ max_tokens; quá thì tách theo khoản, bảng tách theo nhóm dòng).
"""
from __future__ import annotations

import re
import subprocess
import unicodedata
from dataclasses import dataclass, field
from typing import Callable, Iterable

# ---------------------------------------------------------------- làm sạch
FIX_CHARS = str.maketrans({"Ð": "Đ", "ð": "đ"})            # BVP: font WinAnsi map sai Đ/đ
SPACE_FIXES = [(re.compile(r"\b(đến|từ)(\d)"), r"\1 \2")]   # BVP BQL: "đến1tỷ", "đến500triệu"
INVISIBLE = re.compile(r"[\u00ad\u200b\u200c\u200d\u2060\ufeff\ufffe\x01-\x08\x0b\x0c\x0e-\x1f\x7f]")   # pdfium chèn ở chỗ xuống dòng


def clean_text(s: str) -> str:
    s = unicodedata.normalize("NFC", s or "").translate(FIX_CHARS)
    s = INVISIBLE.sub("", s)
    for pat, rep in SPACE_FIXES:
        s = pat.sub(rep, s)
    return re.sub(r"\s+", " ", s).strip()


WORD = re.compile(r"[^\W\d_]+")


def build_vocab(pdf_path: str) -> set[str]:
    """Từ vựng lấy bằng pdftotext (poppler tách từ đúng) để sửa từ bị dính khi pypdfium2 nối dòng."""
    out = subprocess.run(["pdftotext", pdf_path, "-"], capture_output=True, text=True, check=True).stdout
    return {w.lower() for w in WORD.findall(clean_text(out))}


def repair_glued(text: str, vocab: set[str]) -> str:
    """'điềutrị' → 'điều trị' nếu cả hai nửa đều có trong từ vựng và từ dính thì không có."""
    def fix(m):
        w = m.group(0)
        lw = w.lower()
        if len(w) < 4 or lw in vocab:
            return w
        for i in range(2, len(w) - 1):
            if lw[:i] in vocab and lw[i:] in vocab:
                return f"{w[:i]} {w[i:]}"
        return w
    return WORD.sub(fix, text) if vocab else text


# ---------------------------------------------------------------- nhận diện cấu trúc
ROMAN = r"(?=[IVX])X{0,3}(?:IX|IV|V?I{0,3})"
PAT = {
    "chuong": re.compile(rf"^CHƯƠNG\s+({ROMAN})\b\s*[-:–]?\s*(.*)$"),
    "phuluc": re.compile(r"^PHỤ LỤC\s+(\d+)\b\s*[-:.–]?\s*(.*)$"),
    "bosung": re.compile(r"^QUYỀN LỢI BỔ SUNG\s+(\d+)\s*:\s*(.+)$", re.I),
    "muc":    re.compile(rf"^({ROMAN})\.\s*(\S.*)$"),           # \s* vì có 'VII.Kết thúc'
    "part":   re.compile(r"^([A-D])\.\s+(\S.*)$"),
    "khoan":  re.compile(r"^(\d+)\.\s+(\S.*)$"),
}
TOC_LINE = re.compile(r"^(?P<title>.+?)\s*\.{3,}\s*(?P<page>\d+)$")
LVL1_ROW = re.compile(r"^[IVX]+\s*[–-]")                       # dòng nhóm cấp 1 trong bảng (I – TỬ VONG)
DT_ABBR = {"quy_tac": "QT", "dieu_khoan": "DK", "bang_phi": "BP",
           "bang_quyen_loi": "BQL", "brochure": "BR", "faq": "FAQ"}
SKIP_LABELS = {"picture", "chart", "page_header", "page_footer", "caption", "document_index", "marker"}
BULLETS = {"-", "•", "*", "·", "–", "+"}


def roman_to_int(s: str) -> int:
    vals, total, prev = {"I": 1, "V": 5, "X": 10}, 0, 0
    for ch in reversed(s.upper()):
        v = vals[ch]
        total += -v if v < prev else v
        prev = max(prev, v)
    return total


# ---------------------------------------------------------------- linearize
@dataclass
class Rec:
    kind: str                              # header | text | list | table
    text: str = ""
    page: int = 0                          # trang của file đã parse (file tách nếu split_2up)
    rows: list[list[str]] | None = None    # bảng: danh sách hàng, mỗi hàng là danh sách ô
    synthetic: bool = False                # tiêu đề chèn từ mục lục
    row_pages: list[int] | None = None     # trang của từng hàng (bảng ghép nhiều trang)


def table_rows(item, vocab: set[str] | None = None) -> list[list[str]]:
    rows = []
    for row in item.data.grid:
        cells = [repair_glued(clean_text(c.text), vocab) for c in row]
        if any(cells):
            rows.append(cells)
    return rows


def linearize(doc, skip_pages: set[int] = frozenset(), vocab: set[str] | None = None) -> list[Rec]:
    recs: list[Rec] = []
    for it, _ in doc.iterate_items():
        lab = it.label.value
        if lab in SKIP_LABELS or not getattr(it, "prov", None):
            continue
        page = it.prov[0].page_no
        if page in skip_pages:
            continue
        if lab == "table":
            rows = table_rows(it, vocab)
            if rows:
                recs.append(Rec("table", page=page, rows=rows, row_pages=[page] * len(rows)))
            continue
        text = getattr(it, "text", "") or ""
        if lab == "list_item":
            marker = (getattr(it, "marker", "") or "").strip()
            if marker and not text.lstrip().startswith(marker):
                text = f"- {text}" if marker in BULLETS else f"{marker} {text}"
        text = repair_glued(clean_text(text), vocab)
        if not text:
            continue
        kind = "header" if lab in ("section_header", "title") else "list" if lab == "list_item" else "text"
        recs.append(Rec(kind, text, page))
    return recs


# ---------------------------------------------------------------- ngữ cảnh cấu trúc
@dataclass
class Ctx:
    chuong: tuple | None = None    # (số, tiêu đề)
    muc: tuple | None = None
    bosung: tuple | None = None
    part: tuple | None = None
    dn: tuple | None = None        # định nghĩa
    phuluc: tuple | None = None
    last_def: int = 0

    @property
    def in_definitions(self) -> bool:
        return self.muc is not None and self.bosung is None and "ĐỊNH NGHĨA" in self.muc[1].upper()

    def apply(self, key: tuple) -> None:
        lv, n, title = key
        if lv == "chuong":
            self.chuong, self.muc, self.bosung, self.part, self.dn, self.phuluc = (n, title), None, None, None, None, None
        elif lv == "phuluc":
            self.chuong = self.muc = self.bosung = self.part = self.dn = None
            self.phuluc = (n, title)
        elif lv == "muc":
            self.muc, self.bosung, self.part, self.dn, self.last_def = (n, title), None, None, None, 0
        elif lv == "bosung":
            self.bosung, self.part, self.dn = (n, title), None, None
        elif lv == "part":
            self.part = (n, title)
        elif lv == "dn":
            self.dn, self.last_def = (n, title), n

    def toc_key(self, lv: str) -> tuple:
        c = self.chuong[0] if self.chuong else None
        return {"chuong": ("chuong", c),
                "phuluc": ("phuluc", self.phuluc[0] if self.phuluc else None),
                "muc": ("muc", c, self.muc[0] if self.muc else None),
                "bosung": ("bosung", c, self.bosung[0] if self.bosung else None)}.get(lv, (lv,))

    def id_parts(self) -> list[str]:
        if self.phuluc:
            return [f"PL{self.phuluc[0]}"]
        parts = []
        if self.chuong:
            parts.append(f"C{self.chuong[0]}")
        if self.muc:
            parts.append(f"M{self.muc[0]}")
        if self.bosung:
            parts.append(f"B{self.bosung[0]}")
        if self.part:
            parts.append(self.part[0])
        if self.dn:
            parts.append(f"K{self.dn[0]}")
        return parts

    def path(self) -> list[str]:
        if self.phuluc:
            return [self.phuluc[1][:100]]
        return [x[1][:100] for x in (self.chuong, self.muc, self.bosung, self.part, self.dn) if x]


def struct_key(rec: Rec, ctx: Ctx) -> tuple | None:
    """Trả về (cấp, số, tiêu đề) nếu rec là tiêu đề cấu trúc. Chỉ tin regex, không tin nhãn Docling."""
    if rec.kind == "table":
        return None
    t = rec.text
    if m := PAT["chuong"].match(t):
        return ("chuong", roman_to_int(m[1]), t)
    if m := PAT["phuluc"].match(t):
        return ("phuluc", int(m[1]), t)
    if not (rec.kind == "header" or len(t) <= 150):
        return None
    if m := PAT["bosung"].match(t):
        return ("bosung", int(m[1]), t)
    if m := PAT["muc"].match(t):
        return ("muc", roman_to_int(m[1]), t)
    if ctx.in_definitions:
        m = PAT["khoan"].match(t)
        if rec.kind == "header" and m and int(m[1]) == ctx.last_def + 1:   # số tăng liên tục → không nhầm danh sách lồng
            return ("dn", int(m[1]), t)
        return None
    if (ctx.muc or ctx.bosung) and (rec.kind == "header" or len(t) <= 60):
        if m := PAT["part"].match(t):
            return ("part", m[1], t)
    return None


# ---------------------------------------------------------------- mục lục
def classify_title(title: str, chuong: int | None) -> tuple | None:
    if m := PAT["chuong"].match(title):
        return ("chuong", roman_to_int(m[1]))
    if m := PAT["phuluc"].match(title):
        return ("phuluc", int(m[1]))
    if m := PAT["bosung"].match(title):
        return ("bosung", chuong, int(m[1]))
    if m := PAT["muc"].match(title):
        return ("muc", chuong, roman_to_int(m[1]))
    return None


def toc_from_pdf(pdf_path: str, pages: Iterable[int]) -> list[dict]:
    """Đọc mục lục bằng pdftotext (ổn định hơn bảng document_index của Docling)."""
    entries, chuong = [], None
    for p in pages:
        out = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), pdf_path, "-"],
                             capture_output=True, text=True, check=True).stdout
        for line in out.splitlines():
            m = TOC_LINE.match(clean_text(line))
            if not m:
                continue
            title = m["title"].strip()
            key = classify_title(title, chuong)
            if key is None:
                continue
            if key[0] == "chuong":
                chuong = key[1]
            entries.append({"key": key, "title": title, "page": int(m["page"])})
    return entries


def detected_keys(recs: list[Rec]) -> set[tuple]:
    ctx, keys = Ctx(), set()
    for r in recs:
        if k := struct_key(r, ctx):
            ctx.apply(k)
            keys.add(ctx.toc_key(k[0]))
    return keys


def reconcile(recs: list[Rec], toc: list[dict], page_offset: int = 0,
              insert_levels: tuple = ("chuong", "phuluc")) -> tuple[list[Rec], dict]:
    """So mục lục với tiêu đề tìm được. Chỉ chèn cấp luôn bắt đầu trang mới (chương, phụ lục);
    cấp thấp hơn thiếu thì chỉ báo cáo để tránh chèn sai chỗ giữa trang."""
    recs, inserted = list(recs), []
    found = detected_keys(recs)
    for e in toc:
        if e["key"] not in found and e["key"][0] in insert_levels:
            page = e["page"] + page_offset
            idx = next((i for i, r in enumerate(recs) if r.page >= page), len(recs))
            recs.insert(idx, Rec("header", e["title"], page, synthetic=True))
            inserted.append(e["title"])
    found = detected_keys(recs)                      # tính lại sau khi chèn (số chương của mục con đổi)
    missing = [f'{e["title"]} (tr.{e["page"]})' for e in toc if e["key"] not in found]
    return recs, {"toc_entries": len(toc), "matched": len(toc) - len(missing),
                  "missing": missing, "inserted": inserted}


# ---------------------------------------------------------------- đơn vị
@dataclass
class Unit:
    ids: list[str]
    path: list[str]
    recs: list[Rec] = field(default_factory=list)


def build_units(recs: list[Rec], structure: str = "legal") -> list[Unit]:
    units, ctx, sec = [], Ctx(), 0
    cur = Unit(ids=[], path=[])
    for r in recs:
        if structure == "legal":
            if key := struct_key(r, ctx):
                if cur.recs:
                    units.append(cur)
                ctx.apply(key)
                cur = Unit(ids=ctx.id_parts(), path=ctx.path())
                continue
        elif r.kind == "header":                       # flat: BQL, tờ rơi → mỗi tiêu đề một đơn vị
            if cur.recs:
                units.append(cur)
            sec += 1
            cur = Unit(ids=[f"S{sec}"], path=[r.text[:100]])
            continue
        cur.recs.append(r)
    if cur.recs:
        units.append(cur)
    return units


# ---------------------------------------------------------------- render + đóng gói
@dataclass
class Piece:
    text: str
    page: int
    knum: int | None = None
    is_table: bool = False


def is_group_row(row: list[str]) -> bool:
    vals = {c for c in row if c}
    return len(vals) == 1 and not re.fullmatch(r"[\d.,%/ ]+", next(iter(vals)))


def rows_to_md(rows: list[list[str]]) -> str:
    ncol = max(len(r) for r in rows)
    out = []
    for i, r in enumerate(rows):
        r = r + [""] * (ncol - len(r))
        if i > 0 and is_group_row(r):                  # ô gộp ngang bị Docling lặp ở mọi cột → thu về 1 ô
            r = [next(c for c in r if c)] + [""] * (ncol - 1)
        out.append("| " + " | ".join(c.replace("|", "/") for c in r) + " |")
        if i == 0:
            out.append("|" + "---|" * ncol)
    return "\n".join(out)


def merge_tables(recs: list[Rec]) -> list[Rec]:
    """Ghép các mảnh bảng liền nhau cùng số cột (bảng trải nhiều trang, ví dụ Phụ lục 1)."""
    out: list[Rec] = []
    for r in recs:
        prev = out[-1] if out else None
        if (r.kind == "table" and prev is not None and prev.kind == "table"
                and len(prev.rows[0]) == len(r.rows[0])):
            skip = 1 if r.rows[0] == prev.rows[0] else 0
            prev.rows = prev.rows + r.rows[skip:]
            prev.row_pages = prev.row_pages + r.row_pages[skip:]
            continue
        out.append(Rec(r.kind, r.text, r.page, [list(x) for x in r.rows] if r.rows else None, r.synthetic,
                       list(r.row_pages) if r.row_pages else None))
    return out


def table_parts(rows, budget, count) -> list[list[list[str]]]:
    """Tách bảng lớn: theo dòng nhóm (CHI TRÊN, II. QUYỀN LỢI BỔ SUNG…), nhóm quá lớn thì theo số dòng.
    Mỗi phần lặp lại dòng tiêu đề (+ dòng nhóm cấp 1 nếu có)."""
    header, body = rows[0], rows[1:]
    groups, cur, lvl1 = [], [], None
    for r in body:
        if is_group_row(r) and cur:
            groups.append(cur)
            cur = []
        cur.append(r)
    if cur:
        groups.append(cur)
    parts = []
    for g in groups:
        first = next(c for c in g[0] if c)
        ctx_rows = [header]
        if is_group_row(g[0]) and LVL1_ROW.match(first):
            lvl1 = g[0]
        elif lvl1 is not None:
            ctx_rows.append(lvl1)
        cand = ctx_rows + g
        if count(rows_to_md(cand)) <= budget:
            parts.append(cand)
            continue
        keep = ctx_rows + ([g[0]] if is_group_row(g[0]) else [])
        data = g[1:] if is_group_row(g[0]) else g
        k = -(-count(rows_to_md(keep + data)) // budget)          # số phần tối thiểu
        while True:                                            # chia đều để không còn phần lẻ quá nhỏ
            size = -(-len(data) // k)
            slices = [keep + data[j:j + size] for j in range(0, len(data), size)]
            if all(count(rows_to_md(s)) <= budget for s in slices) or size == 1:
                break
            k += 1
        parts += slices
    # gộp các phần nhỏ liền nhau nếu còn vừa ngân sách
    merged: list[list[list[str]]] = []
    for p in parts:
        if merged:
            cand = merged[-1] + [r for r in p[1:] if r not in merged[-1]]
            if count(rows_to_md(cand)) <= budget:
                merged[-1] = cand
                continue
        merged.append(p)
    return merged


def split_text(text: str, budget: int, count) -> list[str]:
    sents = re.split(r"(?<=[.;:])\s+", text)
    out, cur = [], ""
    for s in sents:
        cand = f"{cur} {s}".strip()
        if cur and count(cand) > budget:
            out.append(cur)
            cand = s
        cur = cand
    if cur:
        out.append(cur)
    return out


def unit_pieces(recs: list[Rec], budget: int, count) -> list[Piece]:
    """Biến đơn vị thành các mẩu nhỏ nhất có thể đóng gói, gắn số khoản (1., 2., …) nếu tăng liên tục."""
    pieces, expect, knum, caption = [], 1, None, ""
    for i, r in enumerate(recs):
        if r.kind == "table":
            md, cap = rows_to_md(r.rows), (caption + "\n" if caption else "")
            if count(cap + md) <= budget:
                pieces.append(Piece(cap + md, r.page, knum, True))
            else:
                parts = table_parts(r.rows, budget - count(cap), count)
                pg = {id(row): rp for row, rp in zip(r.rows, r.row_pages or [r.page] * len(r.rows))}
                def part_page(part):
                    data = [pg[id(x)] for x in part[1:] if id(x) in pg and not is_group_row(x)]
                    return min(data) if data else r.page
                pieces += [Piece((cap if j == 0 else "") + rows_to_md(p), part_page(p), knum, True)
                           for j, p in enumerate(parts)]
            caption = ""
            continue
        nxt = recs[i + 1] if i + 1 < len(recs) else None
        if nxt is not None and nxt.kind == "table" and len(r.text) <= 150 and not PAT["khoan"].match(r.text):
            caption = r.text                           # dòng ngắn ngay trước bảng = tiêu đề bảng
            continue
        m = PAT["khoan"].match(r.text)
        if m and int(m[1]) == expect:
            knum, expect = expect, expect + 1
        if count(r.text) <= budget:
            pieces.append(Piece(r.text, r.page, knum))
        else:
            pieces += [Piece(t, r.page, knum) for t in split_text(r.text, budget, count)]
    return pieces


def pack(pieces: list[Piece], budget: int, count) -> list[tuple[str, list[Piece]]]:
    """Đóng gói theo khoản: giữ nguyên khoản nếu vừa; khoản quá dài mới tách bên trong (K{n}_P{j}).
    Trả về [(nhãn, mẩu)]; nhãn: K{a} | K{a}-{b} | TB{i} (chỉ bảng) | P{i}."""
    segs: list[list[Piece]] = []
    for p in pieces:                                   # nhóm các mẩu liền nhau cùng số khoản
        if segs and segs[-1][-1].knum == p.knum:
            segs[-1].append(p)
        else:
            segs.append([p])
    tok = lambda ps: sum(count(x.text) + 1 for x in ps)
    raw: list[tuple[bool, list[Piece]]] = []           # (là phần tách bên trong 1 khoản, mẩu)
    cur: list[Piece] = []
    for seg in segs:
        if tok(seg) > budget:
            if cur:
                raw.append((False, cur))
                cur = []
            sub: list[Piece] = []
            for p in seg:
                if sub and tok(sub + [p]) > budget:
                    raw.append((True, sub))
                    sub = []
                sub.append(p)
            if sub:
                raw.append((True, sub))
        elif cur and tok(cur + seg) > budget:
            raw.append((False, cur))
            cur = list(seg)
        else:
            cur += seg
    if cur:
        raw.append((False, cur))
    out, tb, sub_idx = [], 0, {}
    for i, (inner, pk) in enumerate(raw, 1):
        ks = sorted({p.knum for p in pk if p.knum is not None})
        if all(p.is_table for p in pk):
            tb += 1
            label = f"TB{tb}"
        elif inner and ks:
            sub_idx[ks[0]] = sub_idx.get(ks[0], 0) + 1
            label = f"K{ks[0]}_P{sub_idx[ks[0]]}"
        elif ks:
            label = f"K{ks[0]}" if len(ks) == 1 else f"K{ks[0]}-{ks[-1]}"
        else:
            label = f"P{i}"
        out.append((label, pk))
    return out


def unit_to_chunks(u: Unit, cfg: dict, count, max_tokens: int, page_map: list[int] | None) -> list[dict]:
    abbr = DT_ABBR[cfg["doc_type"]]
    base = f'{cfg["product_code"]}_{abbr}_' + "_".join(u.ids or ["S0"])
    tail = " > ".join(u.path[-2:]) if u.path else cfg["doc_label"]
    header = f'[{cfg["product_name"]} | {cfg["doc_label"]} | {tail}]'
    budget = max_tokens - count(header) - 2
    pieces = unit_pieces(merge_tables(u.recs), budget, count)
    whole = "\n".join(p.text for p in pieces)
    packs = [("", pieces)] if count(whole) <= budget else pack(pieces, budget, count)
    orig = (lambda p: page_map[p - 1]) if page_map else (lambda p: p)
    out = []
    for label, pk in packs:
        body = "\n".join(p.text for p in pk)
        if len(body) < cfg.get("min_chars", 20):
            continue
        out.append({
            "chunk_id": f"{base}_{label}" if label else base, "text": f"{header}\n{body}",
            "company": cfg["company"], "product_code": cfg["product_code"], "line": cfg["line"],
            "doc_type": cfg["doc_type"], "section_path": " > ".join(u.path) or cfg["doc_label"],
            "is_table": all(p.is_table for p in pk), "effective_date": cfg["effective_date"],
            "source_file": cfg["source_file"], "page": orig(pk[0].page),
        })
    return out


# ---------------------------------------------------------------- API chính
def make_token_counter(model_name: str = "BAAI/bge-m3") -> Callable[[str], int]:
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_name)
    return lambda s: len(tok(s, add_special_tokens=False)["input_ids"])


def chunk_document(doc, cfg: dict, count: Callable[[str], int], page_map: list[int] | None = None,
                   toc_pdf: str | None = None, max_tokens: int = 512,
                   vocab_pdf: str | None = None) -> tuple[list[dict], dict]:
    vocab = build_vocab(vocab_pdf) if vocab_pdf else set()
    recs = linearize(doc, set(cfg.get("skip_pages", [])), vocab)
    if cfg.get("drop_tables"):
        recs = [r for r in recs if r.kind != "table"]
    report: dict = {}
    structure = cfg.get("structure", "legal")
    if structure == "legal" and cfg.get("toc_pages") and toc_pdf:
        recs, report = reconcile(recs, toc_from_pdf(toc_pdf, cfg["toc_pages"]), cfg.get("toc_page_offset", 0))
    units = build_units(recs, structure)
    chunks, seen = [], set()
    for u in units:
        for ch in unit_to_chunks(u, cfg, count, max_tokens, page_map):
            cid, k = ch["chunk_id"], 2
            while ch["chunk_id"] in seen:
                ch["chunk_id"] = f"{cid}_{k}"
                k += 1
            seen.add(ch["chunk_id"])
            chunks.append(ch)
    report.update(units=len(units), chunks=len(chunks))
    return chunks, report
