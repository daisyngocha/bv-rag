"""Tính metric từ runs/{run_id}/ (log.jsonl + meta.json) trên WSL, ghi results/*.csv.

    PYTHONPATH=. python -m eval.metrics runs/B2_v1_test_20261110-2000 [runs/...] [--align-threshold 0.3]
    PYTHONPATH=. python -m eval.metrics runs/B1_v1_dev_*_r0 --align-sweep      # chọn ngưỡng căn chỉnh B1 trên dev
    PYTHONPATH=. python -m eval.metrics runs/B4_v1_dev_*_r* --gate-sweep         # chọn rerank.min_score trên dev
    PYTHONPATH=. python -m eval.metrics runs/B4_v1_dev_*_r* --gate-sweep --gate-grid 0.90:0.995:0.005 --gate-detail 0.97

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
  num_unsup      câu answerable, không từ chối, có ≥ 1 số không xuất hiện trong ngữ cảnh lẫn câu hỏi (log
                 nums_unsupported, từ tuần 6; cờ nghi bịa số, không phải lỗi chắc chắn)
  gated          (B4) tỷ lệ câu bị chặn bởi ngưỡng rerank, không gọi LLM
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
           "cite_rate", "cite_prec", "num_recall", "num_unsup", "gated", "p50_s", "p95_s", "tokens_out_mean", "ctx_overflow", "official"]


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
    m["num_unsup"] = _mean([float(bool(l["nums_unsupported"])) for _, l in answered if l.get("nums_unsupported") is not None])
    m["gated"] = _mean([float(l["gated"]) for _, l in pairs if "gated" in l])
    lat = [l["latency_ms"] for _, l in pairs]
    m["p50_s"], m["p95_s"] = _pct(lat, 0.5), _pct(lat, 0.95)
    m["tokens_out_mean"] = _mean([l.get("tokens_out") for _, l in pairs])
    m["ctx_overflow"] = sum(bool(l.get("ctx_overflow")) for _, l in pairs)
    return m


def qp_summary(log: list[dict], bench: dict[str, dict]) -> dict | None:
    """B3+: tỷ lệ câu answerable nhận đúng tập sản phẩm, câu tách theo sản phẩm, câu phải fallback."""
    qp = [(bench[l["qid"]], l["qp"]) for l in log if "qp" in l]
    if not qp:
        return None
    ans = [(b, p) for b, p in qp if b["answerable"]]
    return {"products_exact": _mean([float(set(p["products"]) == set(b["products"])) for b, p in ans]),
            "filtered": _mean([float(bool(p["products"])) for _, p in qp]),
            "split": sum(bool(p.get("split")) for _, p in qp), "fallback": sum(bool(p.get("fallback")) for _, p in qp)}


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
SWEEP = tuple(round(0.05 * i, 2) for i in range(13))   # 0,00 … 0,60


def gate_sweep(logs: list[list[dict]], bench: dict[str, dict], thresholds=SWEEP) -> list[dict]:
    """Quét ngưỡng rerank.min_score trên log chạy KHÔNG chặn (min_score null). Ngưỡng t: câu có rerank_max < t
    coi như từ chối (pipeline trả câu từ chối, không gọi LLM), còn lại giữ câu trả lời của LLM. Nhiều log (dev × 3)
    thì lấy trung bình. Tính lại được chính xác vì cổng chỉ thay câu trả lời, không đổi ngữ cảnh."""
    out = []
    for t in thresholds:
        acc = defaultdict(list)
        for log in logs:
            if any("rerank_max" not in l for l in log):
                raise ValueError("log không có rerank_max: --gate-sweep chỉ dùng cho run có rerank")
            if any(l.get("gated") for l in log):
                raise ValueError("log đã chặn theo ngưỡng: quét trên run min_score null")
            ref = {l["qid"]: l["rerank_max"] < t or is_refusal(l["answer"]) for l in log}
            ans = [q for q in ref if bench[q]["answerable"]]
            neg = [q for q in ref if not bench[q]["answerable"]]
            acc["refusal_ok"].append(sum(ref[q] for q in neg) / len(neg) if neg else None)
            acc["false_refusal"].append(sum(ref[q] for q in ans) / len(ans) if ans else None)
            acc["gated"].append(sum(l["rerank_max"] < t for l in log) / len(log))
            acc["gated_answerable"].append(sum(next(l["rerank_max"] for l in log if l["qid"] == q) < t for q in ans)
                                           / len(ans) if ans else None)
            for g in ("lookup", "table", "compare", "scenario"):
                qs = [q for q in ans if bench[q]["group"] == g]
                acc[f"fr_{g}"].append(sum(ref[q] for q in qs) / len(qs) if qs else None)
        row = {"min_score": t, **{k: _mean(v) for k, v in acc.items()}}
        row["balanced"] = (round(row["refusal_ok"] - row["false_refusal"], 4)
                           if row["refusal_ok"] is not None and row["false_refusal"] is not None else None)
        out.append(row)
    return out


def parse_grid(spec: str) -> tuple[float, ...]:
    """"a:b:step" → (a, a+step, …, b), làm tròn 4 chữ số."""
    a, b, step = (float(x) for x in spec.split(":"))
    n = int(round((b - a) / step))
    return tuple(round(a + i * step, 4) for i in range(n + 1))


def gate_detail(loaded: list[tuple[dict, list[dict]]], bench: dict[str, dict], below: float) -> list[dict]:
    """Từng câu: mọi câu out_of_scope và câu answerable có rerank_max < below. rerank_max giống nhau giữa các lần
    lặp (truy xuất + rerank tất định), còn LLM có từ chối hay không thì đếm số lần trên tổng số lần chạy."""
    by = defaultdict(list)
    for _, log in loaded:
        for l in log:
            by[l["qid"]].append(l)
    out = []
    for qid, ls in by.items():
        b = bench[qid]
        mx = min(l["rerank_max"] for l in ls)
        if b["answerable"] and mx >= below:
            continue
        out.append({"qid": qid, "group": b["group"], "answerable": b["answerable"], "rerank_max": round(mx, 4),
                    "llm_refused": f"{sum(is_refusal(l['answer']) for l in ls)}/{len(ls)}",
                    "question": b["question"][:80], "answer": ls[0]["answer"][:100].replace("\n", " ")})
    return sorted(out, key=lambda r: r["rerank_max"])


def rerank_score_summary(log: list[dict], bench: dict[str, dict]) -> dict:
    """Phân bố rerank_max theo answerable / out_of_scope: xem hai nhóm tách nhau tới đâu."""
    def q(xs, p):
        xs = sorted(xs)
        return round(xs[max(0, math.ceil(p * len(xs)) - 1)], 3) if xs else None
    a = [l["rerank_max"] for l in log if bench[l["qid"]]["answerable"]]
    n = [l["rerank_max"] for l in log if not bench[l["qid"]]["answerable"]]
    return {"answerable p05/p25/p50": (q(a, .05), q(a, .25), q(a, .5)),
            "out_of_scope p50/p75/p95": (q(n, .5), q(n, .75), q(n, .95))}


def fmt(v):
    return "" if v is None else (f"{v:.3f}" if isinstance(v, float) else str(v))


def print_table(rows: list[dict], cols: list[str]):
    print("| " + " | ".join(cols) + " |")
    print("|" + " --- |" * len(cols))
    for r in rows:
        print("| " + " | ".join(fmt(r.get(c)) for c in cols) + " |")


def run_group(run_id: str) -> str:
    """run_id bỏ hậu tố lần lặp _rN: các lần lặp của cùng một đợt chạy."""
    head, _, tail = run_id.rpartition("_")
    return head if tail[:1] == "r" and tail[1:].isdigit() else run_id


def result_path(meta: dict, out_dir: Path) -> Path:
    """results/{config}_{benchmark_ver}_{split}_{yyyymmdd-HHMM}[_rN].csv, stamp lấy từ run_id.
    Từ tuần 6 có thêm giờ chạy: hai đợt cùng config, cùng ngày (dev B4 1131 và 1259) không ghi đè nhau.
    CSV tuần 4–5 giữ tên cũ {yyyymmdd}."""
    rid = meta["run_id"]
    rep = rid[len(run_group(rid)) + 1:] or None
    stamp = run_group(rid).rsplit("_", 1)[-1]
    if not (len(stamp) == 13 and stamp[8] == "-"):
        stamp = (meta.get("started_at") or "")[:10].replace("-", "")
    name = f"{Path(meta['config']).stem}_{meta.get('benchmark_version', 'v1')}_{meta['split']}_{stamp}"
    return out_dir / (name + (f"_{rep}" if rep else "") + ".csv")


def write_csv(rows: list[dict], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def repeat_summary(results: dict[str, list[dict]]) -> list[dict]:
    """Gộp các lần lặp của cùng một đợt chạy (run_id bỏ _rN, vd. dev × 3): mean ± sd của dòng "all"."""
    by = defaultdict(list)
    for rid, rows in results.items():
        a = next(r for r in rows if r["group"] == "all")
        by[run_group(rid), a["config"], a["split"]].append(a)
    out = []
    for (grp, cfg, split), alls in sorted(by.items()):
        if len(alls) < 2:
            continue
        row = {"run": grp, "config": cfg, "split": split, "runs": len(alls)}
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
    ap.add_argument("--gate-sweep", action="store_true",
                    help="quét rerank.min_score 0–0,6 trên các run B4 dev chạy không chặn (gộp mọi run truyền vào)")
    ap.add_argument("--gate-grid", default="0:0.6:0.05", help="dải ngưỡng quét a:b:bước (mặc định 0:0.6:0.05)")
    ap.add_argument("--gate-detail", type=float, metavar="T",
                    help="in từng câu out_of_scope và câu answerable có rerank_max < T")
    ap.add_argument("--out", type=Path, default=Path("results"))
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args(argv)

    results, bench_cache = {}, {}
    if a.gate_sweep:
        loaded = [load_run(r) for r in a.runs]
        if any(m["split"] != "dev" for m, _ in loaded):
            print("!!! chọn ngưỡng từ chối phải trên dev")
        bench = {r["qid"]: r for r in read_jsonl(loaded[0][0]["benchmark"])}
        for m, log in loaded:
            print(f"{m['run_id']}: rerank_max " + ", ".join(f"{k} {v}" for k, v in rerank_score_summary(log, bench).items()))
        rows = gate_sweep([log for _, log in loaded], bench, parse_grid(a.gate_grid))
        print_table(rows, list(rows[0]))
        if a.gate_detail is not None:
            det = gate_detail(loaded, bench, a.gate_detail)
            print(f"\n## Câu out_of_scope và câu answerable có rerank_max < {a.gate_detail}")
            print_table(det, ["qid", "group", "answerable", "rerank_max", "llm_refused", "question", "answer"])
        return rows
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
                           "false_refusal", "hedge_rate", "cite_rate", "cite_prec", "num_recall", "num_unsup", "gated", "p95_s"])
        qp = qp_summary(log, bench_cache[bpath])
        if qp:
            print("query processor: " + ", ".join(f"{k} {v}" for k, v in qp.items()))
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
