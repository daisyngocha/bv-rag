"""Chunking cố định cho B1 (RQ1): cửa sổ trượt max_tokens token, chồng lấn overlap token.

Dùng chung đầu vào và làm sạch với chunker cấu trúc (linearize, clean_text, sửa từ dính, skip_pages,
drop_tables) để so sánh B1 với B2 chỉ khác cách cắt:
- không nhận diện Chương/Mục/Khoản, không chèn tiêu đề từ mục lục, cắt qua ranh giới mục;
- bảng thành văn bản thô: mỗi hàng một dòng, ô nối bằng dấu cách (không Markdown);
- context header chỉ có [tên sản phẩm | loại tài liệu], không có section_path, để tách được
  tác động của cấu trúc khỏi tác động của việc gắn tên sản phẩm.
Cửa sổ cắt theo token bge-m3, mép cửa sổ lùi về đầu từ để không cắt giữa từ.
"""
from __future__ import annotations

import re
from bisect import bisect_right
from typing import Callable

from src.ingest.chunker import DT_ABBR, build_vocab, is_group_row, linearize

Offsets = list[tuple[int, int]]


def make_offset_encoder(model_name: str = "BAAI/bge-m3") -> Callable[[str], Offsets]:
    """Trả về hàm text -> offset (ký tự) của từng token, không gồm token đặc biệt."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(model_name)
    tok.model_max_length = 10 ** 9                  # chỉ tokenize, không đưa vào model → tắt cảnh báo độ dài
    return lambda s: [tuple(o) for o in tok(s, add_special_tokens=False,
                                            return_offsets_mapping=True)["offset_mapping"]]


def regex_offset_encoder(s: str) -> Offsets:
    """Ước lượng thô (từ và dấu câu) khi chưa có tokenizer; KHÔNG dùng cho số liệu chính thức."""
    return [m.span() for m in re.finditer(r"\w+|[^\w\s]", s)]


def segments(recs) -> list[tuple[str, int, bool]]:
    """Rec → các dòng (text, trang, là_bảng). Bảng: mỗi hàng một dòng, trang lấy theo hàng."""
    out = []
    for r in recs:
        if r.kind != "table":
            out.append((r.text, r.page, False))
            continue
        for row, page in zip(r.rows, r.row_pages or [r.page] * len(r.rows)):
            cells = [next(c for c in row if c)] if is_group_row(row) else [c for c in row if c]
            if cells:
                out.append((" ".join(cells), page, True))
    return out


def windows(offsets: Offsets, size: int, overlap: int) -> list[tuple[int, int]]:
    """Chia dãy token thành [s, e) dài ≤ size, chồng lấn ~overlap; mép lùi về đầu từ nếu được."""
    n = len(offsets)
    word_start = [i == 0 or offsets[i][0] > offsets[i - 1][1] for i in range(n)] + [True]
    out, s = [], 0
    while s < n:
        e = min(s + size, n)
        b = e
        while b > s and not word_start[b]:
            b -= 1
        e = b if b > s else e                          # cả cửa sổ là một "từ" dài → cắt cứng
        out.append((s, e))
        if e >= n:
            break
        ns = max(e - overlap, s + 1)
        b = ns
        while b > s + 1 and not word_start[b]:
            b -= 1
        s = b if word_start[b] else ns
    return out


def chunk_fixed(doc, cfg: dict, encode: Callable[[str], Offsets], page_map: list[int] | None = None,
                max_tokens: int = 512, overlap: int = 64,
                vocab_pdf: str | None = None) -> tuple[list[dict], dict]:
    vocab = build_vocab(vocab_pdf) if vocab_pdf else set()
    recs = linearize(doc, set(cfg.get("skip_pages", [])), vocab)
    if cfg.get("drop_tables"):
        recs = [r for r in recs if r.kind != "table"]
    segs = segments(recs)
    text, starts = "", []
    for t, _, _ in segs:
        starts.append(len(text) + (1 if text else 0))
        text = f"{text}\n{t}" if text else t
    seg_at = lambda pos: bisect_right(starts, pos) - 1                       # đoạn chứa ký tự pos

    header = f'[{cfg["product_name"]} | {cfg["doc_label"]}]'
    size = max_tokens - len(encode(header)) - 2
    offs = encode(text)
    orig = (lambda p: page_map[p - 1]) if page_map else (lambda p: p)
    base = f'{cfg["product_code"]}_{DT_ABBR[cfg["doc_type"]]}_F'
    chunks = []
    for i, (s, e) in enumerate(windows(offs, size, overlap), 1):
        a, b = offs[s][0], offs[e - 1][1]
        first, last = seg_at(a), seg_at(b - 1)
        chunks.append({
            "chunk_id": f"{base}{i:03d}", "text": f"{header}\n{text[a:b]}",
            "company": cfg["company"], "product_code": cfg["product_code"], "line": cfg["line"],
            "doc_type": cfg["doc_type"], "section_path": cfg["doc_label"],
            "is_table": all(segs[j][2] for j in range(first, last + 1)),
            "effective_date": cfg["effective_date"], "source_file": cfg["source_file"],
            "page": orig(segs[first][1]),
        })
    return chunks, {"tokens_total": len(offs), "window": size, "overlap": overlap, "chunks": len(chunks)}
