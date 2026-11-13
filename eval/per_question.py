"""Bảng theo từng câu qua nhiều run (B1, B2, B3…) để rà câu benchmark nghi lỗi và phân tích lỗi.

    PYTHONPATH=. python -m eval.per_question runs/B1_v1_test_<stamp> runs/B2_v1_test_<stamp> runs/B3_v1_test_<stamp> \
        --out results/review/per_question_v1_test.csv

Mỗi dòng một câu: với mỗi run, hạng chunk đúng đầu tiên (rank_), từ chối (ref_), khớp số (num_); thêm sản phẩm
query processor nhận diện (B3+). Cột `suspect` gắn cờ câu đáng xem lại đáp án/evidence (không tự sửa benchmark):
  miss_all        mọi run có truy xuất đều không đưa evidence vào top-10
  refuse_all      câu answerable bị mọi run RAG từ chối
  num0_all        câu có số trong đáp án chuẩn, mọi run RAG trả lời nhưng không khớp số nào
  oos_answered    câu out_of_scope mà mọi run RAG đều trả lời (có thể tài liệu thật ra có thông tin)
Câu sửa sau khi rà ghi vào benchmark/CHANGELOG.md.

`--dump-md file.md` xuất các câu bị gắn cờ (hoặc `--dump-qids`) kèm text evidence, top-5 và câu trả lời của từng run
để rà tay:
    PYTHONPATH=. python -m eval.per_question runs/... --out results/review/per_question_v1_test.csv \
        --dump-md results/review/suspect_v1_test.md
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from eval.benchmark import read_jsonl
from eval.metrics import load_run, relevance_fn
from src.ingest.catalog import numbers
from src.pipeline import is_refusal


def first_rank(rel, b, l, k=30):
    for h in l["retrieved"][:k]:
        if rel(h["chunk_id"], b["evidence_ids"]):
            return h["rank"]
    return None


def num_match(b, l):
    gold = set(numbers(b["answer"]))
    return round(len(gold & set(numbers(l["answer"]))) / len(gold), 2) if gold else None


def build(runs: list[tuple[dict, list[dict]]], bench: dict[str, dict], align: dict | None, threshold: float) -> list[dict]:
    names = [Path(m["config"]).stem for m, _ in runs]
    logs = [{l["qid"]: l for l in log} for _, log in runs]
    rels = [relevance_fn(m, align, threshold) for m, _ in runs]
    rag = [i for i, (m, _) in enumerate(runs) if m.get("retrieval_mode") != "none"]
    qids = sorted(set().union(*[set(x) for x in logs]))
    out = []
    for q in qids:
        b = bench[q]
        row = {"qid": q, "group": b["group"], "difficulty": b["difficulty"], "products": " ".join(b["products"]),
               "evidence": " ".join(b["evidence_ids"]), "question": b["question"]}
        ranks, refs, nums, answered = {}, {}, {}, {}
        for i, n in enumerate(names):
            l = logs[i].get(q)
            if l is None:
                continue
            refs[i] = is_refusal(l["answer"])
            row[f"ref_{n}"] = int(refs[i])
            if b["answerable"]:
                nums[i] = num_match(b, l)
                row[f"num_{n}"] = nums[i]
                if i in rag:
                    ranks[i] = first_rank(rels[i], b, l)
                    row[f"rank_{n}"] = ranks[i]
            if "qp" in l:
                row[f"qp_{n}"] = " ".join(l["qp"]["products"]) + (" fb" if l["qp"].get("fallback") else "")
        flags = []
        rr = [i for i in rag if i in refs]
        if b["answerable"]:
            if ranks and all(r is None or r > 10 for r in ranks.values()):
                flags.append("miss_all")
            if rr and all(refs[i] for i in rr):
                flags.append("refuse_all")
            ans = [i for i in rr if not refs[i] and nums.get(i) is not None]
            if ans and len(ans) == len(rr) and all(nums[i] == 0 for i in ans):
                flags.append("num0_all")
        elif rr and not any(refs[i] for i in rr):
            flags.append("oos_answered")
        row["suspect"] = " ".join(flags)
        out.append(row)
    return out


def dump_md(rows: list[dict], runs: list[tuple[dict, list[dict]]], bench: dict[str, dict], chunks: dict[str, str],
            qids: list[str], path: Path, max_chars: int = 2500):
    names = [Path(m["config"]).stem for m, _ in runs]
    logs = [{l["qid"]: l for l in log} for _, log in runs]
    by = {r["qid"]: r for r in rows}
    out = [f"# Rà câu nghi lỗi ({len(qids)} câu)\n",
           "Kết luận mỗi câu: `ok` (lỗi hệ thống), `sửa đáp án`, `sửa evidence`, `bỏ câu`; ghi vào benchmark/CHANGELOG.md.\n"]
    for q in qids:
        b, r = bench[q], by.get(q, {})
        out += [f"## {q} · {b['group']} · {b['difficulty']} · cờ: {r.get('suspect') or '-'}\n",
                f"**Câu hỏi:** {b['question']}\n", f"**Đáp án chuẩn:** {b['answer']}\n"]
        for e in b["evidence_ids"]:
            t = chunks.get(e, "(không có trong processed)")
            out += [f"**Evidence `{e}`:**\n", "```text", t[:max_chars] + (" …" if len(t) > max_chars else ""), "```\n"]
        for i, n in enumerate(names):
            l = logs[i].get(q)
            if l is None:
                continue
            top = ", ".join(("**" + h["chunk_id"] + "**") if h["chunk_id"] in b["evidence_ids"] else h["chunk_id"]
                            for h in l["retrieved"][:5]) or "-"
            qp = f" · qp {l['qp']['products']}" if "qp" in l else ""
            out += [f"**{n}** (rank {r.get(f'rank_{n}', '-')}{qp}) top-5: {top}\n", "> " + l["answer"].replace("\n", "\n> ") + "\n"]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", type=Path)
    ap.add_argument("--processed", type=Path, help="processed/{ver} có align_fixed.json (cần khi có run B1)")
    ap.add_argument("--align-threshold", type=float, default=0.3)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--dump-md", type=Path, help="xuất câu nghi lỗi kèm evidence + câu trả lời để rà tay")
    ap.add_argument("--dump-qids", nargs="*", help="qid cần xuất (mặc định: mọi câu bị gắn cờ)")
    ap.add_argument("--bench", type=Path)
    a = ap.parse_args(argv)
    runs = [load_run(d) for d in a.runs]
    benches = {str(a.bench)} if a.bench else {m["benchmark"] for m, _ in runs}
    if len(benches) > 1 or len({m["split"] for m, _ in runs}) > 1:
        raise SystemExit("các run phải cùng benchmark và split")
    bench = {r["qid"]: r for r in read_jsonl(benches.pop())}
    align = None
    if any(m.get("chunking") == "fixed" and m.get("retrieval_mode") != "none" for m, _ in runs):
        proc = a.processed or Path(f"data/processed/{runs[0][0]['data_version']}")
        align = json.load(open(proc / "align_fixed.json", encoding="utf-8"))
    rows = build(runs, bench, align, a.align_threshold)
    cols = list(dict.fromkeys(k for r in rows for k in r))
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    sus = [r for r in rows if r["suspect"]]
    print(f"{len(rows)} câu, {len(sus)} câu nghi lỗi → {a.out}")
    for r in sus:
        print(f"  {r['qid']} {r['group']:12s} {r['suspect']:24s} {r['question'][:90]}")
    if a.dump_md:
        proc = a.processed or Path(f"data/processed/{runs[0][0]['data_version']}")
        chunks = {c["chunk_id"]: c["text"] for c in read_jsonl(proc / "chunks.jsonl")}
        dump_md(rows, runs, bench, chunks, a.dump_qids or [r["qid"] for r in sus], a.dump_md)
        print(f"→ {a.dump_md}")


if __name__ == "__main__":
    main()
