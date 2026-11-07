"""Chạy benchmark qua pipeline, ghi runs/{run_id}/log.jsonl + meta.json (schema: skill conventions mục 9).

Chạy chính thức trên Colab L4 (scripts/colab_eval.ipynb); WSL chỉ để debug (Qdrant Docker, Ollama CPU).
Nhiều config trong một phiên dùng chung LLM (đã warmup), bge-m3 và collection Qdrant:

    PYTHONPATH=. python -m eval.run_eval --config configs/B0.yaml configs/B1.yaml configs/B2.yaml \
        --split dev --repeat 3 --processed $DRIVE_DIR/processed/v1 --vectors $DRIVE_DIR/vectors/v1 \
        --runs-dir $DRIVE_DIR/runs

--repeat N: lần r dùng seed = seed + r (r = 0 trùng seed của lần chạy test), run_id thêm hậu tố _r{r};
dùng trên dev để đo dao động của LLM.
--resume RUN_ID: chạy tiếp một run bị ngắt (bỏ qua qid đã có trong log.jsonl), chỉ với 1 config, repeat 1.
Mỗi câu ghi và flush ngay để không mất kết quả khi Colab ngắt.
Trước khi sinh, mọi prompt được đếm token bằng tokenizer của LLM (llm.hf_tokenizer); có câu vượt
num_ctx − max_tokens − TEMPLATE_MARGIN thì dừng (Ollama cắt phần đầu prompt, mất hướng dẫn).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml

from eval.benchmark import read_jsonl


def load_config(path) -> dict:
    cfg = yaml.safe_load(open(path, encoding="utf-8"))
    cfg["_path"] = str(path)
    return cfg


def select(rows: list[dict], split: str, qids: list[str] | None = None, limit: int | None = None) -> list[dict]:
    out = [r for r in rows if split == "all" or r["split"] == split]
    if qids:
        out = [r for r in out if r["qid"] in set(qids)]
    return out[:limit] if limit else out


def make_run_id(cfg: dict, bench_ver: str, split: str, stamp: str, rep: int | None) -> str:
    return f"{cfg['name']}_{bench_ver}_{split}_{stamp}" + (f"_r{rep}" if rep is not None else "")


def sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def qp_files(cfg: dict) -> dict | None:
    """sha256 các file query processor dùng (B3+), để biết run nào chạy với từ điển alias nào."""
    if not cfg["retrieval"].get("use_filter"):
        return None
    from src.retrieve import query_processor as QP
    kw = cfg.get("query_processor", {})
    files = [kw.get("catalog", QP.CATALOG), kw.get("aliases_csv", QP.ALIASES_CSV), kw.get("glossary", QP.GLOSSARY)]
    return {str(f): sha256(f) for f in files if Path(f).exists()}


def env_meta() -> dict:
    from importlib.metadata import version

    pk = {}
    for name in ("torch", "transformers", "FlagEmbedding", "qdrant-client"):
        try:
            pk[name] = version(name)
        except Exception:
            pk[name] = None
    try:
        import torch
        gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    except Exception:
        gpu = None
    try:
        commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=no"], text=True).strip())
    except Exception:
        commit, dirty = None, None
    runtime = "colab" if ("google.colab" in sys.modules or os.environ.get("COLAB_RELEASE_TAG")) else "local"
    return {"runtime": runtime, "host": platform.node(), "python": platform.python_version(), "gpu_name": gpu,
            "gpu": "L4" if gpu and "L4" in gpu else gpu, "packages": pk, "repo_commit": commit, "repo_dirty": dirty}


TEMPLATE_MARGIN = 64   # token chat template Ollama thêm vào (system mặc định của Qwen2.5, <|im_start|>…)


def load_tokenizer(name: str):
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(name)


def check_prompt_lengths(pipe, rows: list[dict], count) -> dict:
    """Đếm token mọi prompt của một config; count(str) -> int. Trả thống kê + danh sách qid vượt ngân sách."""
    llm = pipe.cfg["llm"]
    budget = llm.get("num_ctx", 4096) - llm.get("max_tokens", 600) - TEMPLATE_MARGIN
    lens = {}
    for r in rows:
        _, _, prompt, _ = pipe.prepare(r["question"])
        lens[r["qid"]] = count(prompt)
    xs = sorted(lens.values())
    over = sorted(q for q, n in lens.items() if n > budget)
    return {"budget": budget, "max": xs[-1], "p95": xs[max(0, -(-95 * len(xs) // 100) - 1)],
            "median": xs[len(xs) // 2], "over": over}


def run_one(pipe, cfg: dict, rows: list[dict], run_dir: Path, run_id: str, meta: dict, seed: int) -> dict:
    """Chạy các câu chưa có trong log; trả meta đã cập nhật."""
    run_dir.mkdir(parents=True, exist_ok=True)
    log_path = run_dir / "log.jsonl"
    done = {json.loads(l)["qid"] for l in open(log_path, encoding="utf-8")} if log_path.exists() else set()
    todo = [r for r in rows if r["qid"] not in done]
    if hasattr(pipe.llm, "gen_options"):
        pipe.llm.gen_options["seed"] = seed
    meta.update(started_at=meta.get("started_at") or datetime.now().isoformat(timespec="seconds"),
                n=len(rows), seed=seed)
    json.dump(meta, open(run_dir / "meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    t0 = time.perf_counter()
    with open(log_path, "a", encoding="utf-8") as f:
        for i, r in enumerate(todo, 1):
            out = pipe.answer(r["question"])
            rec = {"ts": datetime.now().isoformat(timespec="seconds"), "run_id": run_id, "qid": r["qid"], **out,
                   "cost_usd": None}   # chi phí tính sau theo giờ GPU (eval/metrics.py), không theo câu
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            f.flush()
            if i % 10 == 0 or i == len(todo):
                print(f"  {run_id}: {len(done) + i}/{len(rows)} câu, {time.perf_counter() - t0:.0f} s", flush=True)
    logged = read_jsonl(log_path)
    gpu = pipe.llm.gpu_status() if hasattr(pipe.llm, "gpu_status") else {}
    meta.update(finished_at=datetime.now().isoformat(timespec="seconds"),
                wall_s=round(meta.get("wall_s", 0) + time.perf_counter() - t0, 1),
                n_logged=len(logged), ctx_overflow=sum(bool(x.get("ctx_overflow")) for x in logged),
                llm_gpu_end=gpu)
    pcts = [p for p in (meta.get("llm_gpu_pct_start"), gpu.get("gpu_pct")) if p is not None]
    meta["llm_gpu_pct"] = min(pcts) if pcts else None
    json.dump(meta, open(run_dir / "meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return meta


def main(argv=None):
    from src.pipeline import RAGPipeline, build_components

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", nargs="+", required=True)
    ap.add_argument("--split", choices=["dev", "test", "all"], required=True)
    ap.add_argument("--repeat", type=int, default=1)
    ap.add_argument("--processed", help="processed/{ver}; mặc định $DRIVE_DIR/processed/{ver} hoặc data/processed/{ver}")
    ap.add_argument("--vectors", help="vectors/{ver}; mặc định $DRIVE_DIR/vectors/{ver} hoặc data/vectors/{ver}")
    ap.add_argument("--runs-dir", help="mặc định $DRIVE_DIR/runs hoặc runs/")
    ap.add_argument("--qids", nargs="*", help="chỉ chạy các qid này (debug)")
    ap.add_argument("--limit", type=int, help="chỉ chạy n câu đầu (debug)")
    ap.add_argument("--resume", help="run_id cần chạy tiếp")
    ap.add_argument("--check-only", action="store_true", help="chỉ kiểm độ dài prompt, không sinh")
    ap.add_argument("--skip-ctx-check", action="store_true", help="bỏ kiểm độ dài prompt (debug; run bị đánh dấu)")
    a = ap.parse_args(argv)

    cfgs = [load_config(p) for p in a.config]
    bench = cfgs[0]["benchmark"]
    assert all(c["benchmark"] == bench for c in cfgs), "các config phải cùng benchmark"
    ver = cfgs[0]["data_version"]
    drive = os.environ.get("DRIVE_DIR")
    processed = Path(a.processed or (f"{drive}/processed/{ver}" if drive else f"data/processed/{ver}"))
    vectors = Path(a.vectors or (f"{drive}/vectors/{ver}" if drive else f"data/vectors/{ver}"))
    runs_dir = Path(a.runs_dir or (f"{drive}/runs" if drive else "runs"))
    rows = select(read_jsonl(bench), a.split, a.qids, a.limit)
    bench_ver = rows[0]["version"] if rows else "v?"
    if a.resume and (len(cfgs) > 1 or a.repeat > 1):
        sys.exit("--resume chỉ dùng với 1 config và --repeat 1")
    debug = bool(a.qids or a.limit)

    comps = build_components(cfgs, processed, vectors)
    llm = comps["llm"]
    env = env_meta()
    gpu_start = comps.get("gpu_after_torch") or (llm.gpu_status() if hasattr(llm, "gpu_status") else {})
    llm_info = {"ollama_version": llm.version(), "model_digest": llm.digest()} if hasattr(llm, "digest") else {}
    print(f"GPU {env['gpu_name']} | LLM trên GPU {gpu_start.get('gpu_pct')}% | index {comps['index']}", flush=True)
    if env["runtime"] == "colab" and env["gpu"] != "L4":
        print("!!! GPU không phải L4: kết quả chỉ để debug, không đưa vào bảng báo cáo", flush=True)

    pipes = {cfg["name"]: RAGPipeline(cfg, llm, comps["retrievers"].get(cfg["chunking"]), reranker=comps.get("reranker"))
             for cfg in cfgs}
    ctx_check = {}
    if not a.skip_ctx_check:
        tok = load_tokenizer(cfgs[0]["llm"]["hf_tokenizer"])
        count = lambda p: len(tok(p, add_special_tokens=False)["input_ids"])
        for name, pipe in pipes.items():
            ctx_check[name] = c = check_prompt_lengths(pipe, rows, count)
            print(f"{name}: prompt token trung vị {c['median']}, p95 {c['p95']}, max {c['max']} "
                  f"(ngân sách {c['budget']}), vượt {len(c['over'])} câu {c['over'][:10]}", flush=True)
        bad = {n: c["over"] for n, c in ctx_check.items() if c["over"]}
        if bad:
            sys.exit(f"Prompt vượt num_ctx ở {sorted(bad)}: tăng llm.num_ctx (giống nhau ở mọi config B0–B4) rồi chạy lại")
    if a.check_only:
        return []

    stamp = datetime.now().strftime("%Y%m%d-%H%M")
    done = []
    for cfg in cfgs:
        pipe = pipes[cfg["name"]]
        for rep in range(a.repeat):
            run_id = a.resume or make_run_id(cfg, bench_ver, a.split, stamp, rep if a.repeat > 1 else None)
            run_dir = runs_dir / run_id
            old = json.load(open(run_dir / "meta.json", encoding="utf-8")) if (run_dir / "meta.json").exists() else {}
            if old and not a.resume:
                sys.exit(f"{run_dir} đã có; dùng --resume {run_id} để chạy tiếp")
            meta = old or {
                "run_id": run_id, "config": cfg["_path"], "config_values": {k: v for k, v in cfg.items() if k != "_path"},
                "benchmark": bench, "benchmark_sha256": sha256(bench), "benchmark_version": bench_ver,
                "data_version": ver, "chunking": cfg["chunking"], "retrieval_mode": cfg["retrieval"]["mode"],
                "prompt": pipe.prompt_name, "context_n": pipe.context_n, "split": a.split, "debug": debug,
                "processed": str(processed), "vectors": str(vectors),
                "model": cfg["llm"]["model"], **llm_info, "warmup": comps.get("warmup"),
                "llm_gpu_pct_start": gpu_start.get("gpu_pct"), "ctx_check": ctx_check.get(cfg["name"]),
                "qp_files": qp_files(cfg),
                "rerank": ({"model": cfg["rerank"]["model"], "max_length": cfg["rerank"].get("max_length"),
                            "min_score": pipe.min_score} if pipe.reranker is not None else None),
                **env}
            meta = run_one(pipe, cfg, rows, run_dir, run_id, meta, cfg.get("seed", 42) + rep)
            done.append(run_id)
            print(f"{run_id}: {meta['n_logged']}/{meta['n']} câu, {meta['wall_s']} s, "
                  f"LLM GPU {meta['llm_gpu_pct']}%, ctx_overflow {meta['ctx_overflow']}", flush=True)
    print("Xong:", " ".join(done))
    return done


if __name__ == "__main__":
    main()
