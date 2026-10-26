"""Căn chỉnh chunk cố định (B1) với chunk cấu trúc (B2+) để chấm Recall@k/MRR của B1.

Benchmark ghi evidence_ids theo chunk cấu trúc. Chunk cố định có id khác nên không so trực tiếp được;
thay vào đó tính độ phủ: tỷ lệ n-gram từ của chunk cấu trúc S xuất hiện trong chunk cố định F
(cùng source_file). Khi chấm B1, F được tính là trúng evidence S nếu độ phủ ≥ ngưỡng (chọn ở eval).
So khớp trên phần thân (bỏ context header), bỏ ký hiệu Markdown của bảng.
"""
from __future__ import annotations

import re
from collections import defaultdict

TOKEN = re.compile(r"\w+", re.UNICODE)


def body_words(text: str) -> list[str]:
    body = text.split("\n", 1)[1] if text.startswith("[") and "\n" in text else text
    return [w.lower() for w in TOKEN.findall(body)]


def shingles(words: list[str], n: int) -> set[tuple[str, ...]]:
    n = min(n, len(words)) or 1
    return {tuple(words[i:i + n]) for i in range(len(words) - n + 1)}


def align(structure: list[dict], fixed: list[dict], n: int = 5, min_cov: float = 0.1) -> dict:
    """Trả về {chunk_id cấu trúc: [[chunk_id cố định, độ phủ], ...]} sắp giảm dần, chỉ giữ độ phủ ≥ min_cov."""
    by_file, cache = defaultdict(list), {}
    for f in fixed:
        by_file[f["source_file"]].append((f["chunk_id"], body_words(f["text"])))
    out = {}
    for s in structure:
        words = body_words(s["text"])
        sh = shingles(words, n)
        k = min(n, len(words)) or 1                   # chunk rất ngắn: n-gram ngắn hơn
        hits = []
        for fid, fw in by_file.get(s["source_file"], []):
            if (fid, k) not in cache:
                cache[fid, k] = shingles(fw, k)
            cov = len(sh & cache[fid, k]) / len(sh) if sh else 0.0
            if cov >= min_cov:
                hits.append([fid, round(cov, 3)])
        out[s["chunk_id"]] = sorted(hits, key=lambda h: -h[1])
    return out


def align_report(alignment: dict, thresholds: tuple = (0.5, 0.8)) -> dict:
    """Số chunk cấu trúc có ít nhất một chunk cố định phủ ≥ ngưỡng; liệt kê chunk phủ kém."""
    best = {sid: (hits[0][1] if hits else 0.0) for sid, hits in alignment.items()}
    rep = {f"best_cov>={t}": sum(v >= t for v in best.values()) for t in thresholds}
    rep["total"] = len(best)
    rep["low"] = sorted((sid for sid, v in best.items() if v < thresholds[0]), key=best.get)[:20]
    return rep
