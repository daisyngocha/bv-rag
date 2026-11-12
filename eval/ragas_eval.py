"""Ragas cho một run, chạy trên WSL (chỉ dữ liệu công khai). Ghi dần từng câu nên chạy lại được (chỉ chấm câu còn thiếu/lỗi).

    set -a; source .env; set +a                      # GEMINI_API_KEY (hoặc GOOGLE_API_KEY) / ANTHROPIC_API_KEY
    PYTHONPATH=. .venv-judge/bin/python -m eval.ragas_eval runs/B4_v1_test_20261107-1335 \
        --judge configs/judge_j1.yaml --bench benchmark/benchmark_v1.1.jsonl [--qids ...]

Bỏ qua câu answerable=false (chấm bằng refusal metric) và câu bị từ chối. Run không có ngữ cảnh (B0): chỉ answer_correctness.
AnswerCorrectness weights=[1, 0]: chỉ phần factual, bỏ semantic similarity (không cần embedding, tránh điểm ảo do câu
tiếng Việt trùng từ). Token judge ghi vào results/ragas/{run_id}__{judge_id}.usage.jsonl (báo chi phí judge riêng).
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import re
import warnings
from pathlib import Path

import yaml

from eval.benchmark import read_jsonl

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

CITE = re.compile(r"\s*\[\d+(?:\s*,\s*\d+)*\](?:\s*,\s*\[\d+(?:\s*,\s*\d+)*\])*")   # bỏ [n], [1, 2], [1], [2]
FIELDS = ["qid", "group", "faithfulness", "answer_correctness", "judge_id", "error"]


def build_samples(run_dir: Path, bench: Path, processed: Path) -> tuple[list[dict], dict]:
    qs = {b["qid"]: b for b in read_jsonl(bench)}
    text = {c["chunk_id"]: c["text"] for f in ("chunks.jsonl", "chunks_fixed.jsonl") if (processed / f).exists()
            for c in read_jsonl(processed / f)}
    out, skip = [], {"out_of_scope": 0, "refused": 0}
    for r in read_jsonl(run_dir / "log.jsonl"):
        b = qs[r["qid"]]
        if not b["answerable"] or r["refused"]:
            skip["refused" if b["answerable"] else "out_of_scope"] += 1
            continue
        out.append({"qid": r["qid"], "group": b["group"], "user_input": b["question"],
                    "response": CITE.sub("", r["answer"]).strip(),
                    "retrieved_contexts": [text[c] for c in r.get("contexts") or []],
                    "reference": b["answer"]})
    return out, skip


def make_llm(jc: dict):
    if jc.get("provider", "gemini") == "anthropic":
        from eval.claude_llm import ClaudeRagasLLM
        return ClaudeRagasLLM(model=jc["model"], effort=jc["effort"], thinking=jc.get("thinking"),
                              max_tokens=jc.get("max_tokens", 4096))
    from langchain_google_genai import ChatGoogleGenerativeAI
    from ragas.llms import LangchainLLMWrapper
    key = os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"]
    return LangchainLLMWrapper(ChatGoogleGenerativeAI(model=jc["model"], temperature=jc["temperature"], google_api_key=key))


async def score(rows: list[dict], jc: dict, out: Path, llm=None) -> dict:
    from langchain_core.callbacks import get_usage_metadata_callback
    from ragas import RunConfig, SingleTurnSample
    from ragas.metrics import AnswerCorrectness, Faithfulness

    llm = llm or make_llm(jc)
    rc = RunConfig(timeout=jc["timeout_s"], max_retries=jc["max_retries"], seed=jc["seed"])
    faith, corr = Faithfulness(llm=llm), AnswerCorrectness(llm=llm, weights=[1.0, 0.0])
    for m in (faith, corr):
        m.init(rc)
    sem, new = asyncio.Semaphore(jc["max_workers"]), not out.exists()
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "a", newline="", encoding="utf-8") as f, get_usage_metadata_callback() as cb:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()

        async def one(r):
            async with sem:
                s = SingleTurnSample(**{k: r[k] for k in ("user_input", "response", "retrieved_contexts", "reference")})
                row = {"qid": r["qid"], "group": r["group"], "judge_id": jc["judge_id"], "error": ""}
                try:
                    row["faithfulness"] = await faith.single_turn_ascore(s) if r["retrieved_contexts"] else ""
                    row["answer_correctness"] = await corr.single_turn_ascore(s)
                except Exception as e:  # ghi lỗi; lần chạy sau chấm lại câu này
                    row["error"] = f"{type(e).__name__}: {e}"[:200]
                w.writerow(row)
                f.flush()

        await asyncio.gather(*(one(r) for r in rows))
    usage = getattr(llm, "usage", None) or {   # Claude: wrapper tự đếm; Gemini: callback LangChain (đã gồm thought tokens)
        "calls": None,
        "input_tokens": sum(v.get("input_tokens", 0) for v in cb.usage_metadata.values()),
        "output_tokens": sum(v.get("output_tokens", 0) for v in cb.usage_metadata.values())}
    with open(out.with_suffix(".usage.jsonl"), "a", encoding="utf-8") as u:
        u.write(json.dumps({"judge_id": jc["judge_id"], "model": jc["model"], "n": len(rows), **usage}) + "\n")
    return usage


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--judge", type=Path, default=Path("configs/judge_j1.yaml"))
    ap.add_argument("--bench", type=Path, default=Path("benchmark/benchmark_v1.1.jsonl"))
    ap.add_argument("--qids", nargs="*")
    a = ap.parse_args(argv)
    jc = yaml.safe_load(open(a.judge, encoding="utf-8"))
    meta = json.load(open(a.run_dir / "meta.json", encoding="utf-8"))
    rows, skip = build_samples(a.run_dir, a.bench, Path(f"data/processed/{meta['data_version']}"))
    rows = [r for r in rows if not a.qids or r["qid"] in a.qids]
    out = Path("results/ragas") / f"{a.run_dir.name}__{jc['judge_id']}.csv"
    done = {r["qid"] for r in csv.DictReader(open(out, encoding="utf-8")) if not r["error"]} if out.exists() else set()
    todo = [r for r in rows if r["qid"] not in done]
    print(f"{a.run_dir.name} [{jc['judge_id']}]: chấm {len(rows)} câu, bỏ qua {skip}, còn {len(todo)} → {out}")
    if todo:
        usage = asyncio.run(score(todo, jc, out))
        print(f"usage {jc['judge_id']}: {usage}")


if __name__ == "__main__":
    main()
