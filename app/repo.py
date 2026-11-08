"""Ghi Supabase bằng service_role (SV-12, SV-13). Người dùng không có quyền INSERT các bảng này (RLS)."""
from __future__ import annotations

from datetime import datetime, timezone

from app.supabase_rest import SupabaseError


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class ChatRepo:
    def __init__(self, db):
        self.db = db

    def get_conversation(self, conversation_id: str) -> dict | None:
        try:
            rows = self.db.select("conversations", id=f"eq.{conversation_id}", select="id,user_id,title")
        except SupabaseError as e:
            if e.status_code == 400:   # uuid sai định dạng
                return None
            raise
        return rows[0] if rows else None

    def create_conversation(self, user_id: str, title: str) -> dict:
        return self.db.insert("conversations", {"user_id": user_id, "title": title})[0]

    def insert_messages(self, rows: list[dict]) -> list[dict]:
        """Câu hỏi và câu trả lời cùng một request (câu trả lời có reply_to_id → phải chèn câu hỏi trước)."""
        return [self.db.insert("messages", r)[0] for r in rows]

    def insert_citations(self, rows: list[dict]) -> None:
        if rows:
            self.db.insert("message_citations", rows, returning=False)

    def insert_trace(self, trace: dict, logs: list[dict]) -> None:
        self.db.insert("traces", trace, returning=False)
        if logs:
            self.db.insert("retrieval_logs", logs, returning=False)


class RunRepo:
    def __init__(self, db):
        self.db = db

    @staticmethod
    def demo_run_id(config_name: str, when: datetime | None = None) -> str:
        return f"{config_name}_demo_{(when or datetime.now()).strftime('%Y%m%d-%H%M')}"

    def start_demo_run(self, config_name: str, data_version: str, env: dict | None = None,
                       run_id: str | None = None) -> str:
        env = env or {}
        run_id = run_id or self.demo_run_id(config_name)
        self.db.upsert("runs", [{
            "run_id": run_id, "config_name": config_name, "benchmark": None, "data_version": data_version,
            "split": "demo", "runtime": "colab" if env.get("runtime") == "colab" else "wsl",
            "gpu": env.get("gpu"), "ollama_version": env.get("ollama_version"), "model_digest": env.get("model_digest"),
            "packages": env.get("packages"), "repo_commit": env.get("repo_commit"),
            "llm_gpu_pct": env.get("llm_gpu_pct"), "n": None, "started_at": utcnow(), "finished_at": None,
        }], on_conflict="run_id")
        return run_id

    def finish_run(self, run_id: str) -> None:
        self.db.update("runs", {"finished_at": utcnow()}, run_id=f"eq.{run_id}")

    def config_exists(self, name: str) -> bool:
        return bool(self.db.select("pipeline_configs", name=f"eq.{name}", select="name"))

    def set_setting(self, key: str, value: dict, updated_by: str | None = None) -> None:
        self.db.upsert("app_settings", [{"key": key, "value": value, "updated_by": updated_by}], on_conflict="key")

    def get_setting(self, key: str) -> dict | None:
        rows = self.db.select("app_settings", key=f"eq.{key}", select="value")
        return rows[0]["value"] if rows else None
