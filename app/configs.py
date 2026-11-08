"""Đổi cấu hình pipeline cho phiên demo (SV-15, PT-SET-04, UC-SET-03)."""
from __future__ import annotations

import time

from app.repo import RunRepo
from app.service import NotFound, config_path


class ConfigService:
    def __init__(self, svc, db=None):
        self.svc, self.db = svc, db
        self.runs = RunRepo(db) if db is not None else None

    def set_active(self, config_name: str, admin_id: str | None = None) -> dict:
        config_path(config_name)   # NotFound nếu không có file
        if self.runs is not None and not self.runs.config_exists(config_name):
            raise NotFound(f"{config_name} chưa có trong pipeline_configs (chạy scripts/sync_supabase.py configs)")
        t0 = time.perf_counter()
        run_id = self.svc.switch_pipeline(config_name)
        loaded_ms = int((time.perf_counter() - t0) * 1000)
        if self.runs is not None:
            self.runs.set_setting("active_config", {"config": config_name, "run_id": run_id}, admin_id)
        return {"config": config_name, "run_id": run_id, "loaded_in_ms": loaded_ms}
