"""Tính metric từ runs/{run_id}/ (log.jsonl + meta.json) trên WSL, ghi results/*.csv.

    PYTHONPATH=. python -m eval.metrics runs/B2_v1_test_20261110-2000 [runs/...] [--align-threshold 0.3]
    PYTHONPATH=. python -m eval.metrics runs/B1_v1_dev_*_r0 --align-sweep      # chọn ngưỡng căn chỉnh B1 trên dev

Định nghĩa (skill conventions mục 10), tính theo từng group và "all":
  recall@k       câu answerable có ≥ 1 evidence trong top-k truy xuất
  full_recall@5  câu answerable có MỌI evidence trong top-5 (compare/scenario nhiều đoạn)
  mrr            1/rank của chunk đúng đầu tiên trong top_k (0 nếu không có)
  refusal_ok     câu answerable=false bị từ chối
  false_refusal  câu answerable=true bị từ chối (từ chối = câu trả lời MỞ ĐẦU bằng câu từ chối, src/pipeline.is_refusal)
  hedge_rate     câu answerable, không từ chối, nhưng có chèn câu từ chối (thường ở cuối)
  cite_rate      câu answerable, không từ chối, có ≥ 1 trích dẫn hợp lệ (mã nằm trong ngữ cảnh)
  cite_prec      trung bình tỷ lệ trích dẫn trỏ đúng evidence (cận dưới: không tính chunk khác có chứa đáp án)
  num_recall     câu answerable có số trong đáp án chuẩn: tỷ lệ số đó xuất hiện trong câu trả lời (xấp xỉ đúng/sai,
                 không thay Answer Correctness của Ragas)
  p50_s, p95_s   độ trễ toàn câu (truy xuất + sinh), không gồm nạp model/warmup
Chunk cố định (B1): chunk F tính là trúng evidence S nếu độ phủ cov(S, F) ≥ ngưỡng (align_fixed.json), hoặc F
là chunk cố định phủ S nhiều nhất (để S dài hơn 1 cửa sổ 512 token vẫn có chunk trúng). Ngưỡng chọn trên dev.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from eval.benchmark import read_jsonl
from src.ingest.catalog import numbers
from src.pipeline import is_hedged, is_refusal

GROUPS = ("lookup", "table", "compare", "scenario", "out_of_scope")
KS = (1, 3, 5, 10)
COLUMNS = ["run_id", "config", "split", "group", "n", "n_answerable",
           *[f"recall@{k}" for k in KS], "full_recall@5", "mrr", "refusal_ok", "false_refusal", "hedge_rate",
           "cite_rate", "cite_prec", "num_recall", "p50_s", "p95_s", "tokens_out_mean", "ctx_overflow", "official"]


# ------------------------------------------------------------------ đọc run
def load_run(run_dir) -> tuple[dict, list[dict]]:
    d = Path(run_dir)
    return json.load(open(d / "meta.json", encoding="utf-8")), read_jsonl(d / "log.jsonl")


def official(meta: dict) -> tuple[bool, list[str]]:
    """Điều kiện đưa vào bảng báo cáo: Colab L4, LLM 100% GPU, đủ câu, không debug, code đã commit."""
    why = []
    if meta.get("runtime") != "colab" or meta.get("gpu") != "L4":
        why.append(f"runtime={meta.get('runtime')} gpu={meta.get('gpu')}")
    if meta.get("llm_gpu_pct") != 100:
        why.append(f"llm_gpu_pct={meta.get('llm_gpu_pct')}")
    if meta.get("n_logged") != meta.get("n"):
        why.append(f"thiếu câu {meta.get('n_logged')}/{meta.get('n')}")
    if meta.get("debug"):
        why.append("debug (--qids/--limit)")
    if meta.get("repo_dirty"):
        why.append("code chưa commit")
    if not meta.get("ctx_check"):
        why.append("không kiểm độ dài prompt (--skip-ctx-check)")
    if meta.get("ctx_overflow"):
        why.append(f"{meta['ctx_overflow']} câu prompt vượt num_ctx")
    return not why, why


# ------------------------------------------------------------------ chunk đúng
def relevance_fn(meta: dict, align: dict | None, threshold: float):
    """Trả f(chunk_id, evidence_ids) -> set evidence mà chunk đó trúng."""
    if meta.get("chunking") != "fixed" or meta.get("retrieval_mode") == "none":
        return lambda cid, ev: {cid} & set(ev)
    if align is None:
        raise ValueError("run chunk cố định cần align_fixed.json (--processed)")
    rel = {}
    for s, hits in align.items():
        rel[s] = {f for f, cov in hits if cov >= threshold}
        if hits:
            rel[s].add(hits[0][0])                     # chunk phủ nhiều nhất luôn tính
    return lambda cid, ev: {e for e in ev if cid in rel.get(e, ())}


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return round(sum(xs) / len(xs), 4) if xs else None


def _pct(xs, q):
    xs = sorted(xs)
    if not xs:
        return None
    i = max(0, math.ceil(q * len(xs)) - 1)             # nearest-rank
    return round(xs[i] / 1000, 2)


def score_rows(pairs: list[tuple[dict, dict]], rel) -> dict:
    """pairs = [(câu benchmark, dòng log)]; trả dict metric (None khi không áp dụng)."""
    ans = [(b, l) for b, l in pairs if b["answerable"]]
    neg = [(b, l) for b, l in pairs if not b["answerable"]]
    has_ret = any(l["retrieved"] for _, l in pairs)
    m = {"n": len(pairs), "n_answerable": len(ans)}

    def first_rank(b, l):
        for h in l["retrieved"]:
            if rel(h["chunk_id"], b["evidence_ids"]):
                return h["rank"]
        return None

    for k in KS:
        m[f"recall@{k}"] = _mean([float((r := first_rank(b, l)) is not None and r <= k) for b, l in ans]) if has_ret else None
    if has_ret:
        full = []
        for b, l in ans:
            got = set()
            for h in l["retrieved"][:5]:
                got |= rel(h["chunk_id"], b["evidence_ids"])
            full.append(float(got >= set(b["evidence_ids"])))
        m["full_recall@5"] = _mean(full)
        m["mrr"] = _mean([1 / r if (r := first_rank(b, l)) else 0.0 for b, l in ans])
    else:
        m["full_recall@5"] = m["mrr"] = None
    m["refusal_ok"] = _mean([float(is_refusal(l["answer"])) for _, l in neg])
    m["false_refusal"] = _mean([float(is_refusal(l["answer"])) for _, l in ans])
    answered = [(b, l) for b, l in ans if not is_refusal(l["answer"])]
    m["hedge_rate"] = _mean([float(is_hedged(l["answer"])) for _, l in answered])
    if has_ret:
        m["cite_rate"] = _mean([float(bool(l["citations"])) for _, l in answered])
        m["cite_prec"] = _mean([sum(bool(rel(c, b["evidence_ids"])) for c in l["citations"]) / len(l["citations"])
                                for b, l in answered if l["citations"]])
    else:
        m["cite_rate"] = m["cite_prec"] = None
    nr = []
    for b, l in ans:
        gold = set(numbers(b["answer"]))
        if gold:
            nr.append(len(gold & set(numbers(l["answer"]))) / len(gold))
    m["num_recall"] = _mean(nr)
    lat = [l["latency_ms"] for _, l in pairs]
    m["p50_s"], m["p95_s"] = _pct(lat, 0.5), _pct(lat, 0.95)
    m["tokens_out_mean"] = _mean([l.get("tokens_out") for _, l in pairs])
    m["ctx_overflow"] = sum(bool(l.get("ctx_overflow")) for _, l in pairs)
    return m


def evaluate(meta: dict, log: list[dict], bench: dict[str, dict], align: dict | None, threshold: float) -> list[dict]:
    rel = relevance_fn(meta, align, threshold)
    missing = [l["qid"] for l in log if l["qid"] not in bench]
    if missing:
        raise ValueError(f"qid không có trong benchmark: {missing[:5]}")
    pairs = [(bench[l["qid"]], l) for l in log]
    by = defaultdict(list)
    for b, l in pairs:
        by[b["group"]].append((b, l))
    out = []
    for g in ("all", *GROUPS):
        ps = pairs if g == "all" else by.get(g, [])
        if ps:
            out.append({"run_id": meta["run_id"], "config": Path(meta["config"]).stem, "split": meta["split"],
                        "group": g, **score_rows(ps, rel)})
    return out


# ------------------------------------------------------------------ in và ghi
def fmt(v):
    return "" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))


def print_table(rows: list[dict], cols: list[str]):
    print("| " + " | ".join(cols) + " |")
    print("|" + " --- |" * len(cols))
    for r in rows:
        print("| " + " | ".join(fmt(r.get(c)) for c in cols) + " |")


def result_path(meta: dict, out_dir: Path) -> Path:
    """results/{config}_{benchmark_ver}_{split}_{yyyymmdd}[_rN].csv"""
    date = (meta.get("started_at") or "")[:10].replace("-", "")
    rep = meta["run_id"].rsplit("_", 1)[-1] if meta["run_id"].rsplit("_", 1)[-1].startswith("r") else None
    name = f"{Path(meta['config']).stem}_{meta.get('benchmark_version', 'v1')}_{meta['split']}_{date}"
    return out_dir / (name + (f"_{rep}" if rep else "") + ".csv")


def write_csv(rows: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def repeat_summary(results: dict[str, list[dict]]) -> list[dict]:
    """Gộp các lần lặp cùng config + split (dev × 3): mean ± sd của dòng "all"."""
    by = defaultdict(list)
    for rows in results.values():
        a = next(r for r in rows if r["group"] == "all")
        by[a["config"], a["split"]].append(a)
    out = []
    for (cfg, split), alls in sorted(by.items()):
        if len(alls) < 2:
            continue
        row = {"config": cfg, "split": split, "runs": len(alls)}
        for c in ("recall@5", "mrr", "refusal_ok", "false_refusal", "hedge_rate", "cite_rate", "num_recall", "p95_s"):
            xs = [a[c] for a in alls if a.get(c) is not None]
            row[c] = f"{statistics.mean(xs):.3f} ± {statistics.stdev(xs):.3f}" if len(xs) > 1 else None
        out.append(row)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--processed", type=Path, help="processed/{ver} có align_fixed.json; mặc định data/processed/{ver}")
    ap.add_argument("--align-threshold", type=float, default=0.3)   # decision-log 2026-11-07
    ap.add_argument("--align-sweep", action="store_true", help="in recall@5/MRR theo ngưỡng căn chỉnh (run B1, split dev)")
    ap.add_argument("--out", type=Path, default=Path("results"))
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)

    results, bench_cache = {}, {}
    for run_dir in a.runs:
        meta, log = load_run(run_dir)
        bpath = meta["benchmark"]
        if bpath not in bench_cache:
            bench_cache[bpath] = {r["qid"]: r for r in read_jsonl(bpath)}
            from eval.run_eval import sha256
            if meta.get("benchmark_sha256") and sha256(bpath) != meta["benchmark_sha256"]:
                print(f"!!! {bpath} khác bản lúc chạy {meta['run_id']} (sha256): kiểm CHANGELOG trước khi dùng số liệu")
        align = None
        if meta.get("chunking") == "fixed" and meta.get("retrieval_mode") != "none":
            proc = a.processed or Path(f"data/processed/{meta['data_version']}")
            align = json.load(open(proc / "align_fixed.json", encoding="utf-8"))
        ok, why = official(meta)
        print(f"\n## {meta['run_id']}  ({'chính thức' if ok else 'KHÔNG chính thức: ' + '; '.join(why)})")
        if a.align_sweep:
            if align is None:
                sys.exit("--align-sweep chỉ dùng cho run chunk cố định (B1)")
            if meta["split"] != "dev":
                print("!!! chọn ngưỡng căn chỉnh phải trên dev")
            sweep = []
            for t in (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8):
                r = evaluate(meta, log, bench_cache[bpath], align, t)[0]
                sweep.append({"threshold": t, **{c: r[c] for c in ("recall@1", "recall@5", "recall@10", "mrr")}})
            print_table(sweep, ["threshold", "recall@1", "recall@5", "recall@10", "mrr"])
            continue
        rows = evaluate(meta, log, bench_cache[bpath], align, a.align_threshold)
        for r in rows:
            r["official"] = ok
        results[meta["run_id"]] = rows
        print_table(rows, ["group", "n", "recall@1", "recall@5", "full_recall@5", "mrr", "refusal_ok",
                           "false_refusal", "hedge_rate", "cite_rate", "cite_prec", "num_recall", "p95_s"])
        wall, n = meta.get("wall_s"), meta.get("n_logged")
        if wall and n:
            print(f"giờ GPU / 1.000 câu: {wall / n * 1000 / 3600:.2f} h (wall {wall} s, gồm cả truy xuất)")
        if not a.no_write:
            path = result_path(meta, a.out)
            write_csv(rows, path)
            print(f"→ {path}")
    summ = repeat_summary(results)
    if summ:
        print("\n## Dao động giữa các lần lặp (dòng all)")
        print_table(summ, list(summ[0]))


if __name__ == "__main__":
    main()
