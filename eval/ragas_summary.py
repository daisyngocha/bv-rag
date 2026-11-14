"""Gộp điểm Ragas từng câu (results/ragas/{run_id}__{judge}.csv) vào CSV metric của run (results/*.csv).

    PYTHONPATH=. python -m eval.ragas_summary --judge j1 --bench benchmark/benchmark_v1.1.jsonl $(ls results/*_v1.1_test_*.csv)

Mỗi CSV metric (dòng all + từng nhóm) được thêm/ghi đè cột:
    faithfulness_{judge}, answer_correctness_{judge}  trung bình, bỏ NaN và câu có `error`
    n_ragas_{judge}                                   số câu chấm được (không lỗi)
Judge của eval/ragas_extra.py (file có cột `part`, vd j1x) thay vào đó có:
    answer_relevancy_{judge}, noncommittal_{judge}    part relevancy; noncommittal = tỷ lệ câu mọi câu hỏi sinh ra đều
                                                      noncommittal (điểm relevancy bị đặt 0)
    context_precision_{judge}, context_recall_{judge} part context (mọi câu answerable, kể cả bị từ chối)
    n_rel_{judge}, n_ctx_{judge}                      số câu chấm được mỗi part
Nhóm lấy từ benchmark (không tin cột group trong file Ragas); nhóm không có câu chấm (out_of_scope) để trống.
B0 không có ngữ cảnh nên faithfulness trống. Chạy lại eval.metrics sẽ xoá các cột này: chạy lại script này sau đó.
Chỉ đọc file judge đúng tên `__{judge}.csv` (bỏ qua j1b/c2b/c1 và `_unofficial/`).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

RAGAS_DIR = Path("results/ragas")
METRICS = ("faithfulness", "answer_correctness")
# ragas_extra: part → (metric, cột n); noncommittal tính từ cột noncommittal == strictness (mọi câu sinh ra)
EXTRA = {"relevancy": (("answer_relevancy", "noncommittal"), "n_rel"),
         "context": (("context_precision", "context_recall"), "n_ctx")}


def load_bench(path: Path) -> dict[str, str]:
    with open(path, encoding="utf-8") as fh:
        return {r["qid"]: r["group"] for r in map(json.loads, filter(str.strip, fh))}


def _num(v: str):
    if v in ("", None):
        return None
    x = float(v)
    return None if math.isnan(x) else x


def _dedup(rows: list[dict], key) -> dict:
    # qid lặp (chấm lại câu lỗi rồi nối vào cuối file): giữ dòng không lỗi cuối cùng, không có thì giữ dòng cuối
    last: dict = {}
    for r in rows:
        prev = last.get(key(r))
        if prev is None or not (r.get("error") or "").strip() or (prev.get("error") or "").strip():
            last[key(r)] = r
    return last


def _mean(vals: list) -> str:
    vals = [x for x in vals if x is not None]
    return f"{sum(vals) / len(vals):.4f}" if vals else ""


def summarize_extra(ragas_csv: Path, groups: dict[str, str], strictness: int = 3) -> dict[str, dict[str, str]]:
    """File của eval/ragas_extra.py: một dòng mỗi (qid, part)."""
    rows = list(csv.DictReader(open(ragas_csv, encoding="utf-8")))
    unknown = [r["qid"] for r in rows if r["qid"] not in groups]
    if unknown:
        raise SystemExit(f"{ragas_csv}: qid không có trong benchmark: {unknown[:5]}")
    last = _dedup(rows, lambda r: (r["qid"], r["part"]))
    ok = [r for r in last.values() if not (r.get("error") or "").strip()]
    if len(ok) < len(last):
        print(f"cảnh báo: {ragas_csv.name}: bỏ {len(last) - len(ok)} dòng có error", file=sys.stderr)
    out: dict[str, dict[str, str]] = {}
    for part, (metrics, ncol) in EXTRA.items():
        rs = [r for r in ok if r["part"] == part]
        by_group: dict[str, list[dict]] = {"all": rs}
        for r in rs:
            by_group.setdefault(groups[r["qid"]], []).append(r)
        for g, grs in by_group.items():
            cell = out.setdefault(g, {})
            cell[ncol] = str(len(grs))
            for m in metrics:
                if m == "noncommittal":
                    cell[m] = _mean([float(int(r[m]) >= strictness) for r in grs if r[m] != ""])
                else:
                    cell[m] = _mean([_num(r.get(m)) for r in grs])
    return out


def summarize(ragas_csv: Path, groups: dict[str, str]) -> dict[str, dict[str, str]]:
    rows = list(csv.DictReader(open(ragas_csv, encoding="utf-8")))
    unknown = [r["qid"] for r in rows if r["qid"] not in groups]
    if unknown:
        raise SystemExit(f"{ragas_csv}: qid không có trong benchmark: {unknown[:5]}")
    # qid lặp (chấm lại câu lỗi rồi nối vào cuối file): giữ dòng không lỗi cuối cùng, không có thì giữ dòng cuối
    last: dict[str, dict] = {}
    for r in rows:
        prev = last.get(r["qid"])
        if prev is None or not (r.get("error") or "").strip() or (prev.get("error") or "").strip():
            last[r["qid"]] = r
    if len(last) < len(rows):
        print(f"ghi chú: {ragas_csv.name}: {len(rows) - len(last)} dòng qid lặp, giữ bản chấm lại", file=sys.stderr)
    ok = [r for r in last.values() if not (r.get("error") or "").strip()]
    if len(ok) < len(last):
        print(f"cảnh báo: {ragas_csv.name}: bỏ {len(last) - len(ok)} câu có error", file=sys.stderr)
    by_group: dict[str, list[dict]] = {"all": ok}
    for r in ok:
        by_group.setdefault(groups[r["qid"]], []).append(r)
    out = {}
    for g, rs in by_group.items():
        cell = {"n_ragas": str(len(rs))}
        for m in METRICS:
            vals = [x for x in (_num(r.get(m)) for r in rs) if x is not None]
            cell[m] = f"{sum(vals) / len(vals):.4f}" if vals else ""
        out[g] = cell
    return out


def update_csv(path: Path, judge: str, groups: dict[str, str]) -> str:
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    run_ids = {r["run_id"] for r in rows}
    if len(run_ids) != 1:
        raise SystemExit(f"{path}: cần đúng một run_id, có {run_ids}")
    run_id = run_ids.pop()
    src = RAGAS_DIR / f"{run_id}__{judge}.csv"
    if not src.exists():
        raise SystemExit(f"{path}: thiếu {src}")
    extra = "part" in (csv.DictReader(open(src, encoding="utf-8")).fieldnames or [])
    summ = summarize_extra(src, groups) if extra else summarize(src, groups)
    keys = ([m for ms, n in EXTRA.values() for m in (*ms, n)] if extra else [*METRICS, "n_ragas"])
    new_cols = [f"{k}_{judge}" for k in keys]
    fields = list(rows[0].keys())
    fields += [c for c in new_cols if c not in fields]
    for r in rows:
        cell = summ.get(r["group"], {})
        for k in keys:
            r[f"{k}_{judge}"] = cell.get(k, "")
    with open(path, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    a = summ.get("all", {})
    if extra:
        return (f"{run_id}\t{judge}\tn_rel={a.get('n_rel')}\tar={a.get('answer_relevancy') or '–'}\t"
                f"noncommittal={a.get('noncommittal') or '–'}\tn_ctx={a.get('n_ctx')}\t"
                f"cp={a.get('context_precision') or '–'}\tcr={a.get('context_recall') or '–'}")
    return f"{run_id}\t{judge}\tn={a.get('n_ragas')}\tfaith={a.get('faithfulness') or '–'}\tac={a.get('answer_correctness') or '–'}"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", required=True, help="mã judge, vd j1, c2")
    ap.add_argument("--bench", type=Path, required=True)
    ap.add_argument("csvs", nargs="+", type=Path)
    a = ap.parse_args(argv)
    groups = load_bench(a.bench)
    for p in a.csvs:
        print(update_csv(p, a.judge, groups))


if __name__ == "__main__":
    main()
