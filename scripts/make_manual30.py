"""Chọn mẫu chấm tay 30 câu của B4 (test) và xuất file chấm: CSV để điền điểm + Markdown để đọc ngữ cảnh.

    PYTHONPATH=. python scripts/make_manual30.py --run runs/B4_v1_test_20261107-1335 \
        --run-ng runs/B4ng_v1_test_20261107-1335 --processed data/processed/v1

Mẫu chính 30 câu: câu answerable mà B4 trả lời (không từ chối), phân tầng theo nhóm (lookup 7, table 7, compare 8,
scenario 8), trong nhóm lấy theo tỷ lệ độ khó (mỗi độ khó có mặt ít nhất 1 câu), seed cố định; luôn gồm các câu
--force (mặc định v1-0050: scenario tụt khỏi top-5 do rerank nhưng vẫn trả lời).
Mẫu phụ: câu compare bị ngưỡng 0,90 chặn ở B4 nhưng B4ng trả lời; chấm câu trả lời của B4ng để biết ngưỡng chặn mất
câu đúng hay câu sai (không tính vào 30 câu, không dùng hiệu chỉnh Ragas).
Mục đích: đo trích dẫn đúng (mục tiêu ≥ 0,85) và hiệu chỉnh judge Ragas (Spearman với correct/faithful).
"""
from __future__ import annotations

import argparse
import csv
import random
import re
from collections import defaultdict
from pathlib import Path

from eval.benchmark import read_jsonl
from eval.metrics import load_run
from src.pipeline import is_refusal

QUOTA = {"lookup": 7, "table": 7, "compare": 8, "scenario": 8}
DIFF = ("easy", "medium", "hard")
CITE = re.compile(r"\[(\d{1,2})\]")

RUBRIC = """## Thang chấm

- `correct_1_5` (đúng so với đáp án chuẩn): 5 đúng và đủ mọi ý/số; 4 đúng ý chính, thiếu chi tiết phụ;
  3 đúng một phần, thiếu ý quan trọng hoặc lẫn 1 chi tiết sai không đổi kết luận; 2 phần lớn sai hoặc kết luận
  đúng nhưng lý do sai; 1 sai hoặc trả lời câu khác.
- `faithful_1_5` (trung thành với ngữ cảnh đã cấp, không xét đáp án chuẩn): 5 mọi khẳng định có trong ngữ cảnh;
  4 có diễn giải nhẹ nhưng không thêm thông tin; 3 có 1 khẳng định không có căn cứ; 2 nhiều khẳng định không căn cứ;
  1 bịa số/điều khoản.
- `cite_ok`: số trích dẫn [n] mà đoạn [n] thật sự chứa thông tin của câu mang trích dẫn đó (≤ `cite_total`).
  Trích dẫn đúng = Σ cite_ok / Σ cite_total.
- `error_code` (bỏ trống nếu không lỗi): R1 truy xuất trượt, R2 lọc nhầm sản phẩm, P1 bảng parse sai,
  G1 sinh sai/bịa số, G2 trích dẫn sai, F1 từ chối nhầm, D1 lỗi benchmark. Một nhãn chính.
- `auto_cite_in_evidence` chỉ để tham khảo (cận dưới tự động: trích dẫn trỏ đúng evidence_ids); chấm theo nội dung đoạn.
"""


def cited_numbers(answer: str) -> list[int]:
    seen = []
    for m in CITE.finditer(answer):
        n = int(m.group(1))
        if n not in seen:
            seen.append(n)
    return seen


def pick(pool: list[dict], quota: dict, force: set[str], seed: int) -> list[dict]:
    rnd = random.Random(seed)
    out = []
    by_group = defaultdict(list)
    for b in pool:
        by_group[b["group"]].append(b)
    for g, k in quota.items():
        cands = sorted(by_group[g], key=lambda b: b["qid"])
        chosen = [b for b in cands if b["qid"] in force]
        rest = [b for b in cands if b["qid"] not in force]
        by_d = defaultdict(list)
        for b in rest:
            by_d[b["difficulty"]].append(b)
        need = k - len(chosen)
        total = len(rest)
        alloc = {d: max(1, round(need * len(by_d[d]) / total)) if by_d[d] else 0 for d in DIFF}
        while sum(alloc.values()) > need:          # bớt ở độ khó đông nhất
            d = max(alloc, key=lambda d: (alloc[d], len(by_d[d])))
            alloc[d] -= 1
        while sum(alloc.values()) < need:
            d = max(DIFF, key=lambda d: len(by_d[d]) - alloc[d])
            alloc[d] += 1
        for d in DIFF:
            chosen += rnd.sample(by_d[d], min(alloc[d], len(by_d[d])))
        out += sorted(chosen, key=lambda b: b["qid"])
    return out


def row(b: dict, l: dict, part: str, run_id: str) -> dict:
    nums = cited_numbers(l["answer"])
    ctx = l["contexts"]
    cited_ids = [ctx[n - 1] for n in nums if 0 < n <= len(ctx)]
    return {"part": part, "qid": b["qid"], "group": b["group"], "difficulty": b["difficulty"],
            "products": " ".join(b["products"]), "run_id": run_id, "question": b["question"],
            "ref_answer": b["answer"], "evidence_ids": " ".join(b["evidence_ids"]), "answer": l["answer"],
            "cited": " ".join(f"[{n}]={ctx[n - 1]}" if 0 < n <= len(ctx) else f"[{n}]=?" for n in nums),
            "cite_total": len(nums),
            "auto_cite_in_evidence": sum(c in b["evidence_ids"] for c in cited_ids),
            "correct_1_5": "", "faithful_1_5": "", "cite_ok": "", "error_code": "", "note": ""}


def md_block(r: dict, l: dict, chunks: dict[str, dict]) -> list[str]:
    cited = set(cited_numbers(l["answer"]))
    out = [f"## {r['qid']} · {r['group']} · {r['difficulty']} · {r['products']}"
           + (" · phụ: B4ng (B4 bị ngưỡng chặn)" if r["part"] != "main" else ""), "",
           f"**Câu hỏi:** {r['question']}", "", f"**Đáp án chuẩn:** {r['ref_answer']}", "",
           f"**Evidence:** `{r['evidence_ids']}`", "", "**Câu trả lời:**", "", *[f"> {x}" for x in r["answer"].splitlines()],
           "", "**Ngữ cảnh đã cấp** (★ = được trích dẫn, ✓ = thuộc evidence_ids):", ""]
    for i, cid in enumerate(l["contexts"], 1):
        mark = ("★" if i in cited else "") + ("✓" if cid in r["evidence_ids"].split() else "")
        text = chunks.get(cid, {}).get("text", "(không tìm thấy text)").strip()
        out += [f"<details{' open' if i in cited else ''}><summary>[{i}] {cid} {mark}</summary>", "", "```text", text,
                "```", "</details>", ""]
    out += ["---", ""]
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path, required=True)
    ap.add_argument("--run-ng", type=Path, help="run B4ng cùng stamp: thêm mẫu phụ câu bị ngưỡng chặn")
    ap.add_argument("--processed", type=Path, default=Path("data/processed/v1"))
    ap.add_argument("--benchmark", type=Path, default=Path("benchmark/benchmark_v1.jsonl"))
    ap.add_argument("--force", nargs="*", default=["v1-0050"])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, default=Path("results/review/manual30_v1_test_b4"))
    a = ap.parse_args(argv)

    bench = {b["qid"]: b for b in read_jsonl(a.benchmark)}
    chunks = {c["chunk_id"]: c for c in read_jsonl(a.processed / "chunks.jsonl")}
    meta, log = load_run(a.run)
    logs = {l["qid"]: l for l in log}
    pool = [bench[q] for q, l in logs.items() if bench[q]["answerable"] and not is_refusal(l["answer"])]
    main_set = pick(pool, QUOTA, set(a.force), a.seed)
    rows = [(row(b, logs[b["qid"]], "main", meta["run_id"]), logs[b["qid"]]) for b in main_set]
    if a.run_ng:
        meta_ng, log_ng = load_run(a.run_ng)
        ng = {l["qid"]: l for l in log_ng}
        for q, l in sorted(logs.items()):
            if bench[q]["answerable"] and l.get("gated") and q in ng and not is_refusal(ng[q]["answer"]):
                rows.append((row(bench[q], ng[q], "gated_b4ng", meta_ng["run_id"]), ng[q]))

    a.out.parent.mkdir(parents=True, exist_ok=True)
    cols = list(rows[0][0])
    with open(a.out.with_suffix(".csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(r for r, _ in rows)
    n_main = sum(r["part"] == "main" for r, _ in rows)
    md = ["# Chấm tay B4 (test): mẫu 30 câu + mẫu phụ câu bị ngưỡng chặn", "",
          f"Run `{meta['run_id']}`; seed {a.seed}; mẫu chính {n_main} câu, mẫu phụ {len(rows) - n_main} câu. "
          f"Điền điểm vào `{a.out.with_suffix('.csv').name}` (mở bằng Excel, UTF-8).", "", RUBRIC]
    for r, l in rows:
        md += md_block(r, l, chunks)
    a.out.with_suffix(".md").write_text("\n".join(md), encoding="utf-8")
    print(f"Ghi {a.out.with_suffix('.csv')} và .md: {n_main} câu chính, {len(rows) - n_main} câu phụ")


if __name__ == "__main__":
    main()
