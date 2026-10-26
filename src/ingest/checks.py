"""Kiểm tra kho chunk của một sản phẩm với truth lập tay (data/truth/{product}.json) và config sản phẩm.

Truth không lấy từ regex của chunker (decision-log 2026-10-25) nên kiểm tra không tự xác nhận chính nó.
Kiểm tra chung cho mọi sản phẩm + kiểm tra riêng khai báo ở khối `checks` của configs/products/{P}.yaml.
"""
from __future__ import annotations

import re
import unicodedata

from src.ingest.chunker import DT_ABBR, WORD, roman_to_int

norm = lambda s: re.sub(r"\s+", "", s)


def section_prefixes(product: str, doc_type: str, sections: list[dict]) -> list[str]:
    """Mục trong truth (chuong/muc/bo_sung/phu_luc) → tiền tố chunk_id phải có."""
    out = []
    for s in sections:
        base = f"{product}_{DT_ABBR[doc_type]}"
        if "phu_luc" in s:
            pref = f'{base}_PL{s["phu_luc"]}'
        else:
            pref = f'{base}_C{roman_to_int(s["chuong"])}' + (f'_M{roman_to_int(s["muc"])}' if s.get("muc") else "")
        out += [f'{pref}_B{b["so"]}' for b in s.get("bo_sung", [])] or [pref]
    return out


def run_checks(chunks: list[dict], truth: dict, files: dict, spec: dict, vocab: set[str]) -> dict[str, bool]:
    """files: {tên file pdf: cfg file đã gộp meta sản phẩm}; spec: khối checks của config sản phẩm."""
    checks: dict[str, bool] = {}
    ids = [c["chunk_id"] for c in chunks]
    checks["chunk_id không trùng"] = len(ids) == len(set(ids))
    by_file = lambda f: [c for c in chunks if c["source_file"] == f]

    # mục lục / danh sách mục trong truth
    miss = []
    for fname, t in truth.items():
        if t.get("sections") and fname in files:
            cfg = files[fname]
            for pr in section_prefixes(cfg["product_code"], cfg["doc_type"], t["sections"]):
                if not any(i == pr or i.startswith(pr + "_") for i in ids):
                    miss.append(pr)
    checks[f"mỗi mục trong truth có chunk (thiếu: {miss})"] = not miss

    # giá trị ô bảng trong truth còn nguyên trong chunk của đúng file
    for fname, t in truth.items():
        cells = [c for tb in t.get("tables", []) for c in tb.get("cell_checks", [])]
        if cells and fname in files:
            txt = norm(" ".join(c["text"] for c in by_file(fname)))
            bad = [x["value"] for x in cells if norm(x["value"]).replace(";", "") not in txt]
            checks[f"{fname}: giá trị ô trong chunk ({len(cells) - len(bad)}/{len(cells)}, sai: {bad[:5]})"] = not bad

    # nhiễu
    noise = {"Ð": sum("Ð" in c["text"] for c in chunks),
             "footer": sum(bool(re.search(r"^- \d+ -$", c["text"], re.M)) for c in chunks)}
    for dt, words in spec.get("forbidden", {}).items():
        noise.update({w: sum(w in c["text"] for c in chunks if c["doc_type"] == dt) for w in words})
    checks[f"không còn nhiễu {noise}"] = not any(noise.values())
    inv = [c["chunk_id"] for c in chunks
           if any(unicodedata.category(ch) in ("Cf", "Cc", "Co") and ch != "\n" for ch in c["text"])]
    checks[f"không còn ký tự vô hình ({inv[:5]})"] = not inv

    def glued(w):
        lw = w.lower()
        return len(w) >= 4 and lw not in vocab and any(lw[:i] in vocab and lw[i:] in vocab for i in range(2, len(w) - 1))
    gl = sorted({w for c in chunks for w in WORD.findall(c["text"]) if glued(w)}) if vocab else []
    checks[f"không còn từ dính ({gl[:10]})"] = not gl

    # kiểm tra riêng của sản phẩm
    if d := spec.get("definitions"):
        got = {int(m[1]) for i in ids if (m := re.match(rf'{re.escape(d["prefix"])}(\d+)', i))}
        checks[f'định nghĩa {d["count"]} (thấy {len(got)})'] = got == set(range(1, d["count"] + 1))
    for dt, (lo, hi) in spec.get("page_range", {}).items():
        checks[f"{dt}: page trong {lo}–{hi} (trang gốc)"] = all(lo <= c["page"] <= hi
                                                                 for c in chunks if c["doc_type"] == dt)
    for sp in spec.get("table_pages", []):
        pages = sorted({c["page"] for c in chunks if c["chunk_id"].startswith(sp["prefix"])})
        checks[f'{sp["prefix"]} trải trang gốc {sp["first"]}–{sp["last"]} (thấy {pages})'] = \
            pages[:1] == [sp["first"]] and pages[-1:] == [sp["last"]]
    for dt, words in spec.get("required", {}).items():
        txt = norm(" ".join(c["text"] for c in chunks if c["doc_type"] == dt))
        checks[f"{dt} có {words}"] = all(norm(w) in txt for w in words)
    for dt in spec.get("no_table_chunks", []):
        checks[f"{dt} không có chunk bảng"] = not any(c["is_table"] for c in chunks if c["doc_type"] == dt)
    return checks
