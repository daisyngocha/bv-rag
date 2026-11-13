"""Kiểm định McNemar theo cặp câu giữa các cấu hình liền kề (B1→B2→B3hyb→B3→B4rr→B4ng→B4).

    PYTHONPATH=. python -m eval.mcnemar runs/B0_v1_test_<stamp> runs/B1_v1_test_<stamp> ... \
        --processed data/processed/v1 --out results/mcnemar_v1_test_<yyyymmdd>.csv

Mỗi câu một biến nhị phân cho mỗi cấu hình, tính cùng định nghĩa với eval.metrics:
  hit1, hit5      câu answerable: chunk đúng đầu tiên ở hạng ≤ 1 / ≤ 5 (B1 qua align_fixed, ngưỡng --align-threshold)
  false_refusal   câu answerable bị từ chối (src.pipeline.is_refusal)
  refusal_ok      câu out_of_scope được từ chối
  num_all         câu answerable có số trong đáp án chuẩn: câu trả lời chứa đủ mọi số đó
Với mỗi cặp (A → B): b = số câu A đạt mà B không đạt, c = ngược lại; p hai phía theo binomial chính xác
(n = b + c nhỏ nên không dùng xấp xỉ chi-square). Hiệu chỉnh Holm trong từng metric qua các bước liền kề
(cặp tổng B2→B4 và các cặp --extra không đưa vào họ Holm).
Run không đạt điều kiện chính thức (eval.metrics.official) bị bỏ, trừ khi có --allow-unofficial.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

from eval.benchmark import read_jsonl
from eval.metrics import load_run, official, relevance_fn
from src.ingest.catalog import numbers
from src.pipeline import is_refusal

METRICS = ("hit1", "hit5", "false_refusal", "refusal_ok", "num_all")
LOWER_IS_BETTER = {"false_refusal"}
STEPS = [("B1", "B2"), ("B2", "B3hyb"), ("B3hyb", "B3"), ("B3", "B4rr"), ("B4rr", "B4ng"), ("B4ng", "B4")]
EXTRA = [("B0", "B2"), ("B2", "B4")]


def binom_two_sided(b: int, c: int) -> float:
    """p hai phía của kiểm định dấu chính xác: min(b, c) ~ Bin(b + c, 0,5)."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def holm(ps: list[float]) -> list[float]:
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    adj, run = [0.0] * len(ps), 0.0
    for r, i in enumerate(order):
        run = max(run, min(1.0, (len(ps) - r) * ps[i]))
        adj[i] = run
    return adj


def outcomes(meta: dict, log: list[dict], bench: dict[str, dict], align: dict | None, threshold: float) -> dict:
    """{metric: {qid: 0/1}} cho một run; metric không áp dụng cho câu nào thì bỏ qua câu đó."""
    rel = relevance_fn(meta, align, threshold)
    has_ret = meta.get("retrieval_mode") != "none"
    out = {m: {} for m in METRICS}
    for l in log:
        b = bench[l["qid"]]
        refused = is_refusal(l["answer"])
        if not b["answerable"]:
            out["refusal_ok"][l["qid"]] = int(refused)
            continue
        out["false_refusal"][l["qid"]] = int(refused)
        if has_ret:
            rank = next((h["rank"] for h in l["retrieved"] if rel(h["chunk_id"], b["evidence_ids"])), None)
            out["hit1"][l["qid"]] = int(rank is not None and rank <= 1)
            out["hit5"][l["qid"]] = int(rank is not None and rank <= 5)
        gold = set(numbers(b["answer"]))
        if gold:
            out["num_all"][l["qid"]] = int(gold <= set(numbers(l["answer"])))
    return out


def compare(a: dict, b: dict) -> dict | None:
    qs = sorted(set(a) & set(b))
    if not qs:
        return None
    only_a = sum(a[q] and not b[q] for q in qs)
    only_b = sum(b[q] and not a[q] for q in qs)
    return {"n": len(qs), "rate_a": round(sum(a[q] for q in qs) / len(qs), 4),
            "rate_b": round(sum(b[q] for q in qs) / len(qs), 4),
            "only_a": only_a, "only_b": only_b, "p": round(binom_two_sided(only_a, only_b), 4)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--benchmark", type=Path, default=Path("benchmark/benchmark_v1.jsonl"))
    ap.add_argument("--processed", type=Path, default=Path("data/processed/v1"), help="có align_fixed.json (B1)")
    ap.add_argument("--align-threshold", type=float, default=0.3)   # decision-log 2026-11-07
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--allow-unofficial", action="store_true")
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)

    bench = {b["qid"]: b for b in read_jsonl(a.benchmark)}
    align_path = a.processed / "align_fixed.json"
    align = json.load(open(align_path, encoding="utf-8")) if align_path.exists() else None
    res, ids = {}, {}
    for d in a.runs:
        meta, log = load_run(d)
        ok, why = official(meta)
        if not ok and not a.allow_unofficial:
            sys.exit(f"{d.name} không phải run chính thức: {'; '.join(why)}")
        name = Path(meta["config"]).stem
        if name in res:
            sys.exit(f"Trùng cấu hình {name}: {ids[name]} và {d.name}")
        res[name], ids[name] = outcomes(meta, log, bench, align, a.align_threshold), d.name

    rows = []
    for family, pairs in (("step", STEPS), ("extra", EXTRA)):
        for m in METRICS:
            fam = []
            for x, y in pairs:
                if x not in res or y not in res:
                    continue
                r = compare(res[x][m], res[y][m])
                if r is None:
                    continue
                better = "" if r["only_a"] == r["only_b"] else (
                    y if (r["only_b"] > r["only_a"]) != (m in LOWER_IS_BETTER) else x)
                fam.append({"family": family, "metric": m, "a": x, "b": y, "run_a": ids[x], "run_b": ids[y],
                            **r, "better": better})
            if family == "step" and fam:
                for row, p in zip(fam, holm([f["p"] for f in fam])):
                    row["p_holm"] = round(p, 4)
            for row in fam:
                row["signif"] = int(row.get("p_holm", row["p"]) < a.alpha)
            rows += fam

    cols = ["family", "metric", "a", "b", "n", "rate_a", "rate_b", "only_a", "only_b", "p", "p_holm", "signif",
            "better", "run_a", "run_b"]
    print("| metric | A → B | n | A | B | chỉ A | chỉ B | p | p Holm | ý nghĩa |")
    print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for r in rows:
        print(f"| {r['metric']} | {r['a']} → {r['b']} | {r['n']} | {r['rate_a']:.3f} | {r['rate_b']:.3f} | "
              f"{r['only_a']} | {r['only_b']} | {r['p']:.4f} | {r.get('p_holm', '')} | {'có' if r['signif'] else ''} |")
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        with open(a.out, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(f"\nGhi {a.out}")


if __name__ == "__main__":
    main()
