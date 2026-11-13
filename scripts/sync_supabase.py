"""Đồng bộ một chiều file → Supabase (MethodList v2 OPS-01…OPS-04). Nguồn sự thật vẫn là file; chạy lại an toàn (upsert).

  kb       data_versions, products, documents, chunks   ← catalog.json, sources.csv, processed/{ver}/chunks.jsonl
  configs  pipeline_configs                            ← configs/*.yaml, configs/ablation/*.yaml
  samples  sample_questions                            ← benchmark (chỉ split dev; từ chối test)
  evals    runs + eval_results                          ← results/*.csv (+ runs/{run_id}/meta.json nếu có)
  all      configs → kb → samples → evals

Ví dụ (WSL hoặc Colab; cần SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY trong môi trường hoặc .env):
  PYTHONPATH=. python scripts/sync_supabase.py kb --version v1 --processed $DRIVE_DIR/processed/v1 --activate
  PYTHONPATH=. python scripts/sync_supabase.py all --version v1 --processed $DRIVE_DIR/processed/v1 --activate
  PYTHONPATH=. python scripts/sync_supabase.py kb --version v1 --processed data/processed/v1 --dry-run
Không xóa chunk cũ: message_citations/retrieval_logs trỏ tới (data_version, chunk_id) như snapshot.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

DOC_TYPES = {"quy_tac", "dieu_khoan", "bang_phi", "bang_quyen_loi", "brochure", "faq"}
SAMPLE_GROUPS = {"lookup", "table", "compare", "scenario"}
RESULT_ID_COLS = {"run_id", "config", "split", "group", "official"}
CSV_NAME_RE = re.compile(r"^(?P<config>[^_]+)_(?P<ver>v\d+(?:\.\d+)?)_(?P<split>dev|test|demo)_")
RUN_ID_RE = re.compile(r"^(?P<config>.+?)_(?P<ver>v\d+)_(?P<split>dev|test|demo)_(?P<stamp>\d{8}(?:-\d{4})?)(?:_r\d+)?$")
VN = ZoneInfo("Asia/Ho_Chi_Minh")


def read_jsonl(path) -> list[dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def load_env(path: str = ".env") -> None:
    """Nạp .env đơn giản (KEY=VALUE) nếu có; không ghi đè biến đã đặt."""
    import os
    p = Path(path)
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# ====================== OPS-01: kho tri thức ======================
def build_kb_rows(data_version: str, catalog: dict, sources: list[dict], chunks: list[dict],
                  manifest: dict | None = None) -> dict:
    """Dựng dòng cho data_versions, products, documents, chunks. Chunk giữ 'source_file' để map document_id sau."""
    products = [{"product_code": p["product_code"], "product_name": p["product_name"], "company": p["company"],
                 "line": p["line"], "is_active": True} for p in catalog["products"]]
    codes = {p["product_code"] for p in products}

    documents, skipped = [], []
    for s in sources:
        if s.get("product_code") not in codes or s.get("doc_type") not in DOC_TYPES:
            skipped.append(s.get("file"))   # văn bản pháp luật: chỉ dùng cho glossary, không vào kho truy xuất
            continue
        documents.append({"product_code": s["product_code"], "doc_type": s["doc_type"],
                          "source_file": Path(s["file"]).name, "url": s["url"],
                          "effective_date": s.get("effective_date") or None,
                          "downloaded_at": s["downloaded_at"]})
    dup = {d["source_file"] for d in documents if sum(x["source_file"] == d["source_file"] for x in documents) > 1}
    if dup:
        raise ValueError(f"source_file trùng trong sources.csv: {sorted(dup)}")
    doc_files = {d["source_file"] for d in documents}

    rows, problems = [], []
    for c in chunks:
        if c["product_code"] not in codes:
            problems.append(f"{c['chunk_id']}: product_code {c['product_code']} không có trong catalog")
        elif c["doc_type"] not in DOC_TYPES:
            problems.append(f"{c['chunk_id']}: doc_type {c['doc_type']} không thuộc enum")
        elif c["source_file"] not in doc_files:
            problems.append(f"{c['chunk_id']}: source_file {c['source_file']} không có trong sources.csv")
        rows.append({"data_version": data_version, "chunk_id": c["chunk_id"], "source_file": c["source_file"],
                     "product_code": c["product_code"], "doc_type": c["doc_type"],
                     "section_path": c.get("section_path"), "page": c.get("page"),
                     "is_table": bool(c.get("is_table")), "effective_date": c.get("effective_date") or None,
                     "text": c["text"]})
    if problems:
        raise ValueError(f"{len(problems)} chunk không khớp catalog/sources:\n  " + "\n  ".join(problems[:20]))
    ids = [r["chunk_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("chunk_id trùng trong chunks.jsonl")

    note = None
    if manifest:
        note = f"frozen_at {manifest.get('frozen_at')}, repo_commit {manifest.get('repo_commit')}"
        expected = (manifest.get("counts", {}).get("structure", {}) or {}).get("total")
        if expected is not None and expected != len(rows):
            raise ValueError(f"chunks.jsonl có {len(rows)} chunk, manifest {data_version} ghi {expected}")
    version = {"version": data_version, "n_chunks": len(rows), "note": note}
    return {"data_version": version, "products": products, "documents": documents, "chunks": rows,
            "skipped_sources": skipped}


def sync_kb(db, data_version: str, processed_dir, activate: bool = False, catalog_path="data/catalog.json",
            sources_path="data/raw/sources.csv", manifest_dir="data/manifests", dry_run: bool = False) -> dict:
    catalog = json.load(open(catalog_path, encoding="utf-8"))
    cat_ver = catalog.get("_meta", {}).get("data_version")
    if cat_ver and cat_ver != data_version:
        raise ValueError(f"catalog.json thuộc {cat_ver}, không phải {data_version}")
    sources = list(csv.DictReader(open(sources_path, encoding="utf-8")))
    chunks = read_jsonl(Path(processed_dir) / "chunks.jsonl")
    mpath = Path(manifest_dir) / f"{data_version}.json"
    manifest = json.load(open(mpath, encoding="utf-8")) if mpath.exists() else None
    kb = build_kb_rows(data_version, catalog, sources, chunks, manifest)
    stats = {"products": len(kb["products"]), "documents": len(kb["documents"]), "chunks": len(kb["chunks"]),
             "skipped_sources": len(kb["skipped_sources"]), "activated": activate}
    if dry_run:
        return stats

    db.upsert("data_versions", [kb["data_version"]], on_conflict="version")
    db.upsert("products", kb["products"], on_conflict="product_code")
    docs = db.upsert("documents", kb["documents"], on_conflict="source_file", returning=True)
    doc_id = {d["source_file"]: d["id"] for d in docs}
    rows = [{**{k: v for k, v in r.items() if k != "source_file"}, "document_id": doc_id[r["source_file"]]}
            for r in kb["chunks"]]
    db.upsert("chunks", rows, on_conflict="data_version,chunk_id", batch=200)
    if activate:
        # Partial unique index chỉ cho 1 bản active: tắt bản khác trước rồi mới bật.
        db.update("data_versions", {"is_active": False}, is_active="eq.true", version=f"neq.{data_version}")
        db.update("data_versions", {"is_active": True}, version=f"eq.{data_version}")
    return stats


# ====================== OPS-02: cấu hình pipeline ======================
def config_description(path: Path, cfg: dict) -> str | None:
    if cfg.get("description"):
        return str(cfg["description"])
    first = path.read_text(encoding="utf-8").splitlines()[0] if path.stat().st_size else ""
    return first.split("#", 1)[1].strip() if "#" in first else None


def build_config_rows(configs_dir="configs") -> list[dict]:
    rows = []
    paths = sorted(Path(configs_dir).glob("*.yaml")) + sorted(Path(configs_dir).glob("ablation/*.yaml"))
    for p in paths:
        cfg = yaml.safe_load(open(p, encoding="utf-8")) or {}
        if "name" not in cfg:
            continue   # configs/products/*.yaml, demo_users.yaml… không phải cấu hình pipeline
        rows.append({"name": cfg["name"], "description": config_description(p, cfg),
                     "params": json.loads(json.dumps(cfg, default=str)),
                     "synced_at": datetime.now(timezone.utc).isoformat()})
    names = [r["name"] for r in rows]
    if len(names) != len(set(names)):
        raise ValueError(f"tên config trùng: {names}")
    return rows


def sync_configs(db, configs_dir="configs", dry_run: bool = False) -> int:
    rows = build_config_rows(configs_dir)
    if not dry_run:
        db.upsert("pipeline_configs", rows, on_conflict="name")
    return len(rows)


# ====================== OPS-03: câu hỏi mẫu ======================
def build_sample_rows(benchmark, split: str = "dev") -> list[dict]:
    if split != "dev":
        raise ValueError("Câu hỏi mẫu chỉ lấy split dev: không đưa câu test lên giao diện")
    return [{"qid": r["qid"], "question": r["question"], "question_group": r["group"],
             "products": r.get("products") or None, "is_active": True}
            for r in read_jsonl(benchmark)
            if r["split"] == "dev" and r["group"] in SAMPLE_GROUPS and r.get("answerable", True)]


def sync_sample_questions(db, benchmark="benchmark/benchmark_v1.jsonl", split: str = "dev",
                          dry_run: bool = False) -> int:
    rows = build_sample_rows(benchmark, split)
    if not dry_run:
        db.upsert("sample_questions", rows, on_conflict="qid")
    return len(rows)


# ====================== OPS-04: kết quả đánh giá ======================
def _ts(value: str | None, runtime: str) -> str | None:
    """Thời điểm trong meta/run_id là giờ máy chạy, không có múi giờ: Colab = UTC, WSL = giờ Việt Nam."""
    if not value:
        return None
    dt = datetime.fromisoformat(value) if "T" in value or " " in value else datetime.strptime(value, "%Y%m%d-%H%M")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc if runtime == "colab" else VN)
    return dt.isoformat()


def build_run_row(run_id: str, csv_row: dict, meta: dict | None, configs: set[str]) -> dict:
    m = RUN_ID_RE.match(run_id)
    if not m:
        raise ValueError(f"run_id không đúng quy ước: {run_id}")
    meta = meta or {}
    config = csv_row.get("config") or m["config"]
    if config not in configs:
        raise ValueError(f"{run_id}: config {config} chưa có trong pipeline_configs (chạy sync configs trước)")
    runtime = meta.get("runtime", "colab")
    runtime = "colab" if runtime == "colab" else "wsl"
    stamp = m["stamp"] if "-" in m["stamp"] else m["stamp"] + "-0000"
    return {"run_id": run_id, "config_name": config, "benchmark": meta.get("benchmark"),
            "data_version": meta.get("data_version") or (meta.get("config_values") or {}).get("data_version") or m["ver"],
            "split": csv_row.get("split") or m["split"], "runtime": runtime, "gpu": meta.get("gpu"),
            "ollama_version": meta.get("ollama_version"), "model_digest": meta.get("model_digest"),
            "packages": meta.get("packages"), "repo_commit": meta.get("repo_commit"),
            "llm_gpu_pct": meta.get("llm_gpu_pct"), "n": meta.get("n"),
            "started_at": _ts(meta.get("started_at"), runtime) or _ts(stamp, runtime),
            "finished_at": _ts(meta.get("finished_at"), runtime)}


def build_eval_rows(results_dir="results", runs_dir="runs", configs: set[str] | None = None,
                    benchmark: str | None = None) -> tuple[list[dict], list[dict]]:
    by_run: dict[str, list[dict]] = defaultdict(list)
    bench_ver: dict[str, set[str]] = defaultdict(set)      # phiên bản benchmark dùng tính metric, lấy từ tên CSV
    for p in sorted(Path(results_dir).glob("*.csv")):        # bỏ thư mục con (review/, sens_*/)
        m = CSV_NAME_RE.match(p.stem)
        for r in csv.DictReader(open(p, encoding="utf-8")):
            by_run[r["run_id"]].append(r)
            if m:
                bench_ver[r["run_id"]].add(m["ver"])
    runs, evals = [], []
    for run_id, rows in sorted(by_run.items()):
        mp = Path(runs_dir) / run_id / "meta.json"
        meta = json.load(open(mp, encoding="utf-8")) if mp.exists() else None
        run = build_run_row(run_id, rows[0], meta, configs or set())
        if run["benchmark"] is None and run["split"] != "demo":
            run["benchmark"] = benchmark
        # Metric tính lại theo benchmark mới từ log cũ (vd CSV B4_v1.1_test_… của run B4_v1_test_…): runs.benchmark là
        # benchmark của metric, không phải benchmark ghi trong meta.json lúc chạy.
        vers = bench_ver.get(run_id, set())
        if len(vers) > 1:
            raise ValueError(f"{run_id}: CSV kết quả theo nhiều phiên bản benchmark {sorted(vers)}")
        if vers and run["split"] != "demo":
            ver = vers.pop()
            if ver != RUN_ID_RE.match(run_id)["ver"]:
                path = Path(f"benchmark/benchmark_{ver}.jsonl")
                if not path.exists():
                    raise ValueError(f"{run_id}: không thấy {path} cho CSV phiên bản {ver}")
                run["benchmark"] = str(path)
        if run["n"] is None:
            alls = [r for r in rows if r.get("group") == "all"]
            run["n"] = int(float(alls[0]["n"])) if alls and alls[0].get("n") else None
        runs.append(run)
        seen = set()
        for r in rows:
            for k, v in r.items():
                if k in RESULT_ID_COLS or v in ("", None):
                    continue
                try:
                    x = float(v)
                except ValueError:
                    continue
                if math.isnan(x) or (r["group"], k) in seen:
                    continue
                seen.add((r["group"], k))
                evals.append({"run_id": run_id, "question_group": r["group"], "metric": k, "value": x})
    return runs, evals


def sync_eval_results(db, results_dir="results", runs_dir="runs", benchmark="benchmark/benchmark_v1.jsonl",
                      dry_run: bool = False) -> dict:
    configs = {r["name"] for r in build_config_rows()} if dry_run else \
        {r["name"] for r in db.select("pipeline_configs", select="name")}
    runs, evals = build_eval_rows(results_dir, runs_dir, configs, benchmark)
    if not dry_run:
        known = {r["version"] for r in db.select("data_versions", select="version")}
        missing = {r["data_version"] for r in runs} - known
        if missing:
            raise ValueError(f"data_version {sorted(missing)} chưa có trong data_versions (chạy sync kb trước)")
        db.upsert("runs", runs, on_conflict="run_id")
        db.upsert("eval_results", evals, on_conflict="run_id,question_group,metric")
    return {"runs": len(runs), "eval_results": len(evals)}


# ====================== CLI ======================
def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["kb", "configs", "samples", "evals", "all"])
    ap.add_argument("--version", default="v1", help="data_version")
    ap.add_argument("--processed", help="thư mục processed/{ver} chứa chunks.jsonl")
    ap.add_argument("--activate", action="store_true", help="đặt data_version này là bản active")
    ap.add_argument("--benchmark", default="benchmark/benchmark_v1.jsonl")
    ap.add_argument("--results-dir", default="results")
    ap.add_argument("--runs-dir", default="runs")
    ap.add_argument("--dry-run", action="store_true", help="chỉ dựng và kiểm dữ liệu, không ghi Supabase")
    a = ap.parse_args(argv)

    load_env()
    db = None
    if not a.dry_run:
        from app.supabase_rest import SupabaseRest
        db = SupabaseRest.from_env()
    out = {}
    if a.what in ("configs", "all"):
        out["pipeline_configs"] = sync_configs(db, dry_run=a.dry_run)
    if a.what in ("kb", "all"):
        if not a.processed:
            sys.exit("--processed bắt buộc với kb/all (vd $DRIVE_DIR/processed/v1)")
        out["kb"] = sync_kb(db, a.version, a.processed, activate=a.activate, dry_run=a.dry_run)
    if a.what in ("samples", "all"):
        out["sample_questions"] = sync_sample_questions(db, a.benchmark, dry_run=a.dry_run)
    if a.what in ("evals", "all"):
        out["evals"] = sync_eval_results(db, a.results_dir, a.runs_dir, a.benchmark, dry_run=a.dry_run)
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
