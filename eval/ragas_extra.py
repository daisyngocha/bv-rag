"""Ragas bổ sung cho một run: answer_relevancy (ResponseRelevancy), context_precision (LLMContextPrecisionWithReference),
context_recall (LLMContextRecall). Ghi dần từng câu; chạy lại chỉ chấm phần còn thiếu/lỗi (như eval/ragas_eval.py).

    set -a; source .env; set +a
    PYTHONPATH=. .venv-judge/bin/python -m eval.ragas_extra runs/B4rr_v1_test_20261107-1335 \
        --judge configs/judge_j1x.yaml --bench benchmark/benchmark_v1.1.jsonl --metrics all [--qids ...] [--limit 5]
    # B4ng/B4 cùng contexts với B4rr: chép điểm context thay vì chấm lại (script kiểm contexts trùng từng câu)
    PYTHONPATH=. .venv-judge/bin/python -m eval.ragas_extra runs/B4_v1_test_20261107-1335 --metrics context \
        --context-from runs/B4rr_v1_test_20261107-1335

Phạm vi câu:
    relevancy: câu answerable, không bị từ chối; bỏ [n] khỏi câu trả lời.
    context:   mọi câu answerable (kể cả bị từ chối); retrieved_contexts = contexts trong log; reference = đáp án benchmark.
Mỗi dòng CSV là một phần (`part` = relevancy | context) của một câu; summary lấy dòng không lỗi cuối cùng theo (qid, part).
answer_relevancy dùng prompt sinh câu hỏi tiếng Việt (rr_vi_v1, dưới đây): prompt gốc Ragas tiếng Anh có thể sinh câu
hỏi tiếng Anh, làm cosine với câu hỏi tiếng Việt thấp giả. Câu hỏi sinh ra lưu ở cột gen_questions; gen_vi = mọi câu có dấu
tiếng Việt. noncommittal = số câu sinh ra bị đánh noncommittal (điểm = 0 khi tất cả đều noncommittal).
Token judge: results/ragas/{run_id}__{judge_id}.usage.jsonl (LLM từ callback LangChain; embedding chỉ đếm số lần gọi, ký tự).
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import math
import os
import re
import warnings
from pathlib import Path

import yaml

from eval.benchmark import read_jsonl
from eval.ragas_eval import CITE, make_llm

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

FIELDS = ["qid", "group", "part", "refused", "answer_relevancy", "noncommittal", "gen_questions", "gen_vi",
          "context_precision", "context_recall", "n_contexts", "ctx_source", "judge_id", "error"]
PARTS = {"relevancy": ("relevancy",), "context": ("context",), "all": ("relevancy", "context")}
VI = re.compile(r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]")


def rr_prompt(version: str):
    """Prompt sinh câu hỏi cho ResponseRelevancy. Không sửa bản đã dùng chính thức: thêm phiên bản mới."""
    from ragas.metrics._answer_relevance import (ResponseRelevanceInput as I, ResponseRelevanceOutput as O,
                                                 ResponseRelevancePrompt)
    if version == "ragas_en":                    # prompt gốc Ragas 0.4.3 (để đối chiếu)
        return ResponseRelevancePrompt()
    if version != "rr_vi_v1":
        raise SystemExit(f"prompt relevancy không biết: {version}")

    class RrViV1(ResponseRelevancePrompt):
        instruction = (ResponseRelevancePrompt.instruction
                       + ". Write the question in the same language as the answer (Vietnamese answers → Vietnamese "
                         "question). Treat an answer that says the information is not available in the documents as "
                         "noncommittal.")
        examples = [
            (I(response="Thời gian chờ đối với bệnh thông thường là 30 ngày kể từ ngày hợp đồng có hiệu lực."),
             O(question="Thời gian chờ đối với bệnh thông thường là bao lâu?", noncommittal=0)),
            (I(response="Tài liệu được cung cấp không có thông tin về mức phí của gói này, nên tôi không thể trả lời."),
             O(question="Mức phí của gói này là bao nhiêu?", noncommittal=1)),
        ]
    return RrViV1()


def build_rows(run_dir: Path, bench: Path, processed: Path) -> dict[str, list[dict]]:
    qs = {b["qid"]: b for b in read_jsonl(bench)}
    text = {c["chunk_id"]: c["text"] for f in ("chunks.jsonl", "chunks_fixed.jsonl") if (processed / f).exists()
            for c in read_jsonl(processed / f)}
    rows = {"relevancy": [], "context": []}
    for r in read_jsonl(run_dir / "log.jsonl"):
        b = qs[r["qid"]]
        if not b["answerable"]:
            continue
        base = {"qid": r["qid"], "group": b["group"], "refused": int(bool(r["refused"])), "user_input": b["question"],
                "ctx_ids": list(r.get("contexts") or [])}
        if not r["refused"]:
            rows["relevancy"].append({**base, "response": CITE.sub("", r["answer"]).strip()})
        if base["ctx_ids"]:
            rows["context"].append({**base, "retrieved_contexts": [text[c] for c in base["ctx_ids"]],
                                    "reference": b["answer"]})
    return rows


def make_embeddings(jc: dict):
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from ragas.embeddings import LangchainEmbeddingsWrapper
    ec = jc["embedding"]
    key = os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"]
    emb = GoogleGenerativeAIEmbeddings(model=ec["model"], task_type=ec["task_type"], google_api_key=key)
    return CountingEmb(LangchainEmbeddingsWrapper(emb))


class CountingEmb:
    """Bọc embedding để đếm số lần gọi/ký tự (API embedding không trả token qua LangChain)."""
    def __init__(self, inner):
        self.inner, self.calls, self.chars = inner, 0, 0

    def embed_query(self, t):
        self.calls, self.chars = self.calls + 1, self.chars + len(t)
        return self.inner.embed_query(t)

    def embed_documents(self, ts):
        self.calls, self.chars = self.calls + 1, self.chars + sum(map(len, ts))
        return self.inner.embed_documents(ts)

    def __getattr__(self, k):
        return getattr(self.inner, k)


def _f(x) -> str:
    return "" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{float(x):.4f}"


async def score(part: str, rows: list[dict], jc: dict, out: Path) -> dict:
    from langchain_core.callbacks import get_usage_metadata_callback
    from ragas import RunConfig, SingleTurnSample
    from ragas.metrics import LLMContextPrecisionWithReference, LLMContextRecall, ResponseRelevancy
    from ragas.metrics._answer_relevance import ResponseRelevanceInput

    llm = make_llm(jc)
    rc = RunConfig(timeout=jc["timeout_s"], max_retries=jc["max_retries"], seed=jc["seed"])
    emb = None
    if part == "relevancy":
        rv = jc.get("relevancy", {})
        if rv.get("bypass_n"):
            llm.bypass_n = True
        emb = make_embeddings(jc)
        rel = ResponseRelevancy(llm=llm, embeddings=emb, strictness=rv.get("strictness", 3),
                                question_generation=rr_prompt(rv.get("prompt", "rr_vi_v1")))
        metrics = [rel]
    else:
        prec, rec = LLMContextPrecisionWithReference(llm=llm), LLMContextRecall(llm=llm)
        metrics = [prec, rec]
    for m in metrics:
        m.init(rc)
    sem, new = asyncio.Semaphore(jc["max_workers"]), not out.exists()
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "a", newline="", encoding="utf-8") as f, get_usage_metadata_callback() as cb:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()

        async def one(r):
            async with sem:
                row = {"qid": r["qid"], "group": r["group"], "part": part, "refused": r["refused"],
                       "judge_id": jc["judge_id"], "error": ""}
                try:
                    if part == "relevancy":
                        # gọi trực tiếp (thay single_turn_ascore) để giữ câu hỏi sinh ra; công thức điểm giữ nguyên Ragas
                        outs = await asyncio.wait_for(rel.question_generation.generate_multiple(
                            data=ResponseRelevanceInput(response=r["response"]), llm=rel.llm, n=rel.strictness),
                            timeout=jc["timeout_s"])
                        s = await asyncio.to_thread(rel._calculate_score, outs, {"user_input": r["user_input"]})
                        gq = [o.question for o in outs]
                        row.update(answer_relevancy=_f(s), noncommittal=sum(o.noncommittal for o in outs),
                                   gen_questions=json.dumps(gq, ensure_ascii=False),
                                   gen_vi=int(all(VI.search(q.lower()) for q in gq if q)))
                    else:
                        s = SingleTurnSample(user_input=r["user_input"], retrieved_contexts=r["retrieved_contexts"],
                                             reference=r["reference"])
                        row.update(context_precision=_f(await prec.single_turn_ascore(s)),
                                   context_recall=_f(await rec.single_turn_ascore(s)), n_contexts=len(r["ctx_ids"]))
                except Exception as e:  # ghi lỗi; lần chạy sau chấm lại câu này
                    row["error"] = f"{type(e).__name__}: {e}"[:200]
                w.writerow(row)
                f.flush()

        await asyncio.gather(*(one(r) for r in rows))
    usage = {"calls": None,
             "input_tokens": sum(v.get("input_tokens", 0) for v in cb.usage_metadata.values()),
             "output_tokens": sum(v.get("output_tokens", 0) for v in cb.usage_metadata.values())}
    if emb is not None:
        usage |= {"embed_model": jc["embedding"]["model"], "embed_calls": emb.calls, "embed_chars": emb.chars}
    with open(out.with_suffix(".usage.jsonl"), "a", encoding="utf-8") as u:
        u.write(json.dumps({"judge_id": jc["judge_id"], "model": jc["model"], "part": part, "n": len(rows),
                            **({"prompt": jc.get("relevancy", {}).get("prompt", "rr_vi_v1")} if part == "relevancy" else {}),
                            **usage}) + "\n")
    return usage


def done_qids(out: Path, part: str) -> set[str]:
    if not out.exists():
        return set()
    return {r["qid"] for r in csv.DictReader(open(out, encoding="utf-8")) if r["part"] == part and not r["error"]}


def copy_context(src_run: Path, dst_run: Path, rows: list[dict], jc: dict, out: Path) -> int:
    """Chép điểm context từ run khác có contexts trùng từng câu (B4rr → B4ng/B4). Dừng nếu có câu khác contexts."""
    src_log = {r["qid"]: list(r.get("contexts") or []) for r in read_jsonl(src_run / "log.jsonl")}
    diff = [r["qid"] for r in rows if src_log.get(r["qid"]) != r["ctx_ids"]]
    if diff:
        raise SystemExit(f"contexts khác {src_run.name} ở {len(diff)} câu: {diff[:5]}; chấm trực tiếp thay vì chép")
    src_csv = out.parent / f"{src_run.name}__{jc['judge_id']}.csv"
    last = {}
    for r in csv.DictReader(open(src_csv, encoding="utf-8")):
        if r["part"] == "context" and not r["error"]:
            last[r["qid"]] = r
    missing = [r["qid"] for r in rows if r["qid"] not in last]
    if missing:
        raise SystemExit(f"{src_csv.name} chưa có điểm context cho {len(missing)} câu: {missing[:5]}")
    done, new = done_qids(out, "context"), not out.exists()
    n = 0
    with open(out, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for r in rows:
            if r["qid"] in done:
                continue
            s = last[r["qid"]]
            w.writerow({**{k: "" for k in FIELDS}, "qid": r["qid"], "group": r["group"], "part": "context",
                        "refused": r["refused"], "context_precision": s["context_precision"],
                        "context_recall": s["context_recall"], "n_contexts": s["n_contexts"],
                        "ctx_source": src_run.name, "judge_id": jc["judge_id"]})
            n += 1
    return n


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--judge", type=Path, default=Path("configs/judge_j1x.yaml"))
    ap.add_argument("--bench", type=Path, default=Path("benchmark/benchmark_v1.1.jsonl"))
    ap.add_argument("--metrics", choices=PARTS, default="all")
    ap.add_argument("--qids", nargs="*")
    ap.add_argument("--limit", type=int, help="chỉ lấy n câu đầu của mỗi phần (chạy thử)")
    ap.add_argument("--out-dir", type=Path, default=Path("results/ragas"), help="chạy thử: results/ragas/_unofficial")
    ap.add_argument("--context-from", type=Path, help="run có contexts trùng từng câu: chép điểm context, không gọi judge")
    a = ap.parse_args(argv)
    jc = yaml.safe_load(open(a.judge, encoding="utf-8"))
    meta = json.load(open(a.run_dir / "meta.json", encoding="utf-8"))
    rows = build_rows(a.run_dir, a.bench, Path(f"data/processed/{meta['data_version']}"))
    out = a.out_dir / f"{a.run_dir.name}__{jc['judge_id']}.csv"
    for part in PARTS[a.metrics]:
        rs = [r for r in rows[part] if not a.qids or r["qid"] in a.qids][:a.limit]
        if part == "context" and a.context_from:
            print(f"{a.run_dir.name} [{jc['judge_id']}] context: chép {copy_context(a.context_from, a.run_dir, rs, jc, out)}"
                  f" câu từ {a.context_from.name} → {out}")
            continue
        done = done_qids(out, part)
        todo = [r for r in rs if r["qid"] not in done]
        print(f"{a.run_dir.name} [{jc['judge_id']}] {part}: {len(rs)} câu, còn {len(todo)} → {out}")
        if not rs and part == "context":
            print("  (run không có contexts, bỏ qua)")
        if todo:
            print(f"  usage {part}: {asyncio.run(score(part, todo, jc, out))}")


if __name__ == "__main__":
    main()
