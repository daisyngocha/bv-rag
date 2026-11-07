"""Bảng tổng B0–B4 (test) từ results/*.csv: dòng all và theo nhóm, kèm mục tiêu B4. In Markdown.

    PYTHONPATH=. python -m eval.summary > docs/results_summary.md.tmp   # rồi chép bảng vào docs/results_summary.md

RUNS: một CSV test chính thức cho mỗi cấu hình (B1 ở ngưỡng căn chỉnh 0,3). Thêm cấu hình mới thì thêm dòng.
"""
from __future__ import annotations

import csv
from pathlib import Path

RUNS = [  # (cấu hình, bước so với dòng trên, CSV, giờ L4/1.000 câu từ eval.metrics)
    ("B0", "không RAG", "results/B0_v1_test_20261107.csv", 0.14),
    ("B1", "dense, chunk cố định 512", "results/B1_v1_test_20261107.csv", 0.76),
    ("B2", "chunk cấu trúc + bảng Markdown", "results/B2_v1_test_20261107.csv", 0.66),
    ("B3hyb", "+ hybrid RRF (ablation)", "results/B3hyb_v1_test_20261107.csv", 0.65),
    ("B3", "+ query processor", "results/B3_v1_test_20261107.csv", 0.67),
    ("B4rr", "+ rerank (ablation, rag_v1)", "results/B4rr_v1_test_20261107-1335.csv", 0.96),
    ("B4ng", "+ prompt rag_v3 (ablation, không chặn)", "results/B4ng_v1_test_20261107-1335.csv", 0.89),
    ("B4", "+ ngưỡng từ chối 0,90", "results/B4_v1_test_20261107-1335.csv", 0.80),
]
ALL_COLS = [("recall@1", "R@1"), ("recall@5", "R@5"), ("full_recall@5", "full_R@5"), ("mrr", "MRR"),
            ("refusal_ok", "Từ chối đúng"), ("false_refusal", "Từ chối nhầm"), ("hedge_rate", "Hedge"),
            ("cite_rate", "Có trích dẫn"), ("cite_prec", "Trích dẫn đúng*"), ("num_recall", "Khớp số"), ("p95_s", "p95 (s)")]
TARGET = {"recall@5": "≥ 0,92", "mrr": "≥ 0,80", "refusal_ok": "≥ 0,90", "false_refusal": "≤ 0,10", "hedge_rate": "≤ 0,05",
          "cite_rate": "≥ 0,90", "cite_prec": "≥ 0,85**", "p95_s": "≤ 6"}
GROUPS = ("lookup", "table", "compare", "scenario")


def vn(v: str, digits=3) -> str:
    return "–" if v in ("", None) else f"{float(v):.{digits}f}".replace(".", ",")


def load(path) -> dict[str, dict]:
    return {r["group"]: r for r in csv.DictReader(open(path, encoding="utf-8"))}


def table(header, rows):
    out = ["| " + " | ".join(header) + " |", "|" + " --- |" * len(header)]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def main():
    data = [(n, step, load(p), gpu, p) for n, step, p, gpu in RUNS]
    for _, _, d, _, p in data:
        assert d["all"].get("official") == "True", f"{p} không phải run chính thức"
    print("## Bảng A. Test, dòng all (120 câu: 96 answerable, 24 out_of_scope)\n")
    rows = [[n, step] + [vn(d["all"][c], 2 if c == "p95_s" else 3) for c, _ in ALL_COLS] + [vn(gpu, 2)]
            for n, step, d, gpu, _ in data]
    rows.append(["Mục tiêu B4", ""] + [TARGET.get(c, "") for c, _ in ALL_COLS] + [""])
    print(table(["Cấu hình", "Bước"] + [h for _, h in ALL_COLS] + ["Giờ L4/1.000 câu"], rows))
    for metric, title in (("recall@5", "Recall@5"), ("full_recall@5", "full_recall@5"), ("mrr", "MRR"),
                          ("false_refusal", "Từ chối nhầm"), ("cite_rate", "Có trích dẫn"), ("num_recall", "Khớp số")):
        print(f"\n## Bảng {title} theo nhóm (24 câu/nhóm)\n")
        rows = [[n] + [vn(d[g][metric]) if g in d else "–" for g in GROUPS] for n, _, d, _, _ in data]
        print(table(["Cấu hình", *GROUPS], rows))
    print("\n## Từ chối đúng (out_of_scope, 24 câu)\n")
    print(table(["Cấu hình", "Từ chối đúng"], [[n, vn(d["out_of_scope"]["refusal_ok"])] for n, _, d, _, _ in data]))


if __name__ == "__main__":
    main()
