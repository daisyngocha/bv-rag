"""Xử lý câu hỏi cho B3: nhận diện sản phẩm → bộ lọc product_code; câu nhắc ≥ 2 sản phẩm → truy xuất riêng từng
sản phẩm rồi ghép xen kẽ; mở rộng viết tắt theo glossary.

Nhận diện bằng từ điển (không fuzzy, không LLM): tên đầy đủ trong data/catalog.json + alias đã duyệt trong
data/manual/product_aliases.csv. So khớp theo ranh giới từ, chữ thường NFC; câu hỏi gõ không dấu thì so trên bản bỏ dấu.
Không nhận diện được sản phẩm nào → không lọc (giữ hành vi B2), log ghi lại để phân tích lỗi.

Đầu ra `plan(query)` là dict thuần, ghi nguyên vào log (`qp`), ĐA2 dùng lại làm bước Router.
"""
from __future__ import annotations

import csv
import json
import re
import unicodedata
from pathlib import Path

CATALOG = Path("data/catalog.json")
ALIASES_CSV = Path("data/manual/product_aliases.csv")
GLOSSARY = Path("data/glossary.json")


def norm(s: str) -> str:
    return " ".join(unicodedata.normalize("NFC", s).lower().split())


def fold(s: str) -> str:
    """Bỏ dấu tiếng Việt (đ → d) trên chuỗi đã norm."""
    s = unicodedata.normalize("NFD", s.replace("đ", "d").replace("Đ", "D"))
    return unicodedata.normalize("NFC", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def has_diacritics(s: str) -> bool:
    return fold(s) != s


def _pattern(term: str) -> re.Pattern:
    return re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.UNICODE)


def load_product_terms(catalog=CATALOG, aliases_csv=ALIASES_CSV) -> dict[str, list[str]]:
    """{product_code: [tên đầy đủ, tên bỏ phần ngoặc, alias...]} (đã norm, bỏ trùng)."""
    cat = json.load(open(catalog, encoding="utf-8"))
    terms: dict[str, list[str]] = {}
    for p in cat["products"]:
        name = norm(p["product_name"])
        terms[p["product_code"]] = [name, norm(re.sub(r"\(.*?\)", " ", name))]
    if Path(aliases_csv).exists():
        for r in csv.DictReader(open(aliases_csv, encoding="utf-8-sig")):
            code = r["product_code"].strip()
            if code not in terms:
                raise ValueError(f"{aliases_csv}: mã sản phẩm {code} không có trong catalog")
            terms[code].append(norm(r["alias"]))
    return {k: list(dict.fromkeys(t for t in v if t)) for k, v in terms.items()}


def load_abbreviations(glossary=GLOSSARY) -> dict[str, str]:
    """Viết tắt → thuật ngữ, lấy từ aliases của glossary: chỉ alias toàn chữ hoa/số dài 2–8 ký tự (HĐBH, NĐBH…)."""
    if not Path(glossary).exists():
        return {}
    out = {}
    for e in json.load(open(glossary, encoding="utf-8"))["entries"]:
        for a in e.get("aliases", []):
            a = a.strip()
            if 2 <= len(a) <= 8 and a.upper() == a and any(c.isalpha() for c in a):
                out.setdefault(a, e["term"])
    return out


class QueryProcessor:
    def __init__(self, product_terms: dict[str, list[str]], abbreviations: dict[str, str] | None = None,
                 split_compare: bool = True, expand_abbr: bool = True):
        self.split_compare, self.expand_abbr = split_compare, expand_abbr
        self.abbr = abbreviations or {}
        # Thuật ngữ dài trước để "bảo hiểm du lịch flexi" ăn trước "flexi"; vị trí khớp đầu tiên quyết định thứ tự SP
        self._pats = sorted(((code, t, _pattern(t), _pattern(fold(t))) for code, ts in product_terms.items() for t in ts),
                            key=lambda x: -len(x[1]))
        self._abbr_pats = {a: _pattern(a) for a in self.abbr}

    @classmethod
    def from_files(cls, catalog=CATALOG, aliases_csv=ALIASES_CSV, glossary=GLOSSARY, **kw) -> "QueryProcessor":
        return cls(load_product_terms(catalog, aliases_csv), load_abbreviations(glossary), **kw)

    def detect_products(self, query: str) -> tuple[list[str], list[str]]:
        """Trả (mã SP theo thứ tự xuất hiện, các cụm đã khớp)."""
        q = norm(query)
        folded = not has_diacritics(q)
        first: dict[str, int] = {}
        matched = []
        for code, term, pat, pat_fold in self._pats:
            m = (pat_fold if folded else pat).search(q)
            if m:
                matched.append(term)
                first[code] = min(first.get(code, m.start()), m.start())
        return sorted(first, key=first.get), matched

    def expand(self, query: str) -> tuple[str, list[str]]:
        """Thêm thuật ngữ đầy đủ sau viết tắt: "HĐBH" → "HĐBH (Hợp đồng bảo hiểm)"."""
        if not self.expand_abbr:
            return query, []
        used = []
        for a, pat in self._abbr_pats.items():
            if pat.search(query) and norm(self.abbr[a]) not in norm(query):
                query = pat.sub(f"{a} ({self.abbr[a]})", query, count=1)
                used.append(a)
        return query, used

    def plan(self, query: str) -> dict:
        """Kế hoạch truy xuất: list sub-query, mỗi sub-query có query (đã mở rộng) và filters."""
        products, matched = self.detect_products(query)
        q, abbr = self.expand(query)
        if len(products) >= 2 and self.split_compare:
            subs = [{"query": q, "filters": {"product_code": [p]}} for p in products]
        elif products:
            subs = [{"query": q, "filters": {"product_code": products}}]
        else:
            subs = [{"query": q, "filters": None}]
        return {"products": products, "matched": matched, "abbr": abbr, "query": q,
                "split": len(subs) > 1, "subqueries": subs}


def interleave(lists: list[list[dict]], k: int) -> list[dict]:
    """Ghép xen kẽ kết quả các sub-query (hạng 1 của mỗi SP, rồi hạng 2…), bỏ trùng chunk, đánh lại rank."""
    out, seen = [], set()
    for i in range(max((len(x) for x in lists), default=0)):
        for x in lists:
            if i < len(x) and x[i]["chunk_id"] not in seen:
                seen.add(x[i]["chunk_id"])
                out.append(dict(x[i]))
    out = out[:k]
    for r, h in enumerate(out, 1):
        h["rank"] = r
    return out
