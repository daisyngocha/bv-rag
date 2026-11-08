"""Ghi runs/{run_id}/log.jsonl + meta.json cho phiên demo và so sánh cấu hình (SV-18; thay biến DEMO_LOG).

Thư mục gốc: $RUNS_DIR, hoặc $DRIVE_DIR/runs, hoặc runs/. Một dòng log = một câu hỏi, cùng các trường kết quả của
RAGPipeline.answer() như log benchmark (retrieved, contexts, citations, latency…), thêm metadata phiên demo.
Log ghi độc lập với Supabase: xóa hội thoại (HIS-05) không xóa log.
"""
from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path


def default_runs_dir() -> Path:
    if os.environ.get("RUNS_DIR"):
        return Path(os.environ["RUNS_DIR"])
    drive = os.environ.get("DRIVE_DIR")
    return Path(f"{drive}/runs") if drive else Path("runs")


class RunLogger:
    def __init__(self, runs_dir: str | Path | None = None):
        self.root = Path(runs_dir) if runs_dir else default_runs_dir()
        self._lock = threading.Lock()

    def append(self, run_id: str, record: dict) -> None:
        d = self.root / run_id
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "run_id": run_id, **record}
        with self._lock:
            d.mkdir(parents=True, exist_ok=True)
            with open(d / "log.jsonl", "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False, default=str) + "\n")

    def write_meta(self, run_id: str, meta: dict) -> None:
        d = self.root / run_id
        with self._lock:
            d.mkdir(parents=True, exist_ok=True)
            old = json.loads((d / "meta.json").read_text(encoding="utf-8")) if (d / "meta.json").exists() else {}
            (d / "meta.json").write_text(json.dumps({**old, **meta}, ensure_ascii=False, indent=2, default=str),
                                         encoding="utf-8")
