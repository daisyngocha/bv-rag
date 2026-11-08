"""Kiểm tra trạng thái hệ thống trước/trong buổi demo (SV-17, PT-ADM-11). Mỗi thành phần: {"ok": bool, ...}."""
from __future__ import annotations

import time


def _timed(fn):
    t0 = time.perf_counter()
    try:
        out = fn() or {}
        return {"ok": out.pop("ok", True), **out, "ms": int((time.perf_counter() - t0) * 1000)}
    except Exception as e:
        return {"ok": False, "error": f"{type(e).__name__}: {e}", "ms": int((time.perf_counter() - t0) * 1000)}


def _device(obj) -> str | None:
    """Thiết bị của model FlagEmbedding (cuda/cpu), nếu đọc được."""
    for path in (("model", "model", "device"), ("model", "device"), ("device",)):
        cur = obj
        try:
            for a in path:
                cur = getattr(cur, a)
            return str(cur)
        except AttributeError:
            continue
    cuda = getattr(obj, "cuda", None)
    return None if cuda is None else ("cuda" if cuda else "cpu")


class HealthService:
    def __init__(self, svc, db=None):
        self.svc, self.db = svc, db

    def _ollama(self):
        llm = getattr(self.svc.pipe, "llm", None)
        if llm is None or not hasattr(llm, "gpu_status"):
            return {"ok": False, "error": "LLM không hỗ trợ kiểm tra"}
        g = llm.gpu_status()
        return {"ok": bool(g.get("loaded")) and g.get("gpu_pct") == 100.0, "model": llm.model,
                "version": llm.version(), "digest": llm.digest(), **g}

    def _qdrant(self):
        r = self.svc.pipe.retriever
        if r is None:
            return {"ok": True, "note": "cấu hình không truy xuất (B0)"}
        n = r.client.count(r.collection, exact=True).count
        return {"ok": n > 0, "collection": r.collection, "points": n}

    def _encoder(self):
        r = self.svc.pipe.retriever
        if r is None:
            return {"ok": True, "note": "không dùng"}
        return {"ok": True, "model": getattr(r.encoder, "model_name", None), "device": _device(r.encoder)}

    def _reranker(self):
        rr = self.svc.pipe.reranker
        if rr is None:
            return {"ok": True, "note": "cấu hình không rerank"}
        return {"ok": True, "model": getattr(rr, "model_name", None), "device": _device(rr),
                "min_score": self.svc.pipe.min_score}

    def _supabase(self):
        if self.db is None:
            return {"ok": False, "error": "chưa cấu hình"}
        rows = self.db.select("data_versions", is_active="eq.true", select="version,n_chunks")
        setting = self.db.select("app_settings", key="eq.active_config", select="value")
        return {"ok": bool(rows), "data_version": rows[0]["version"] if rows else None,
                "n_chunks": rows[0]["n_chunks"] if rows else None,
                "active_config": setting[0]["value"] if setting else None}

    def check(self) -> dict:
        t0 = time.perf_counter()
        out = {"ollama": _timed(self._ollama), "qdrant": _timed(self._qdrant), "encoder": _timed(self._encoder),
               "reranker": _timed(self._reranker), "supabase": _timed(self._supabase)}
        sb = out["supabase"]
        if sb.get("ok") and sb.get("data_version") and sb["data_version"] != self.svc.data_version:
            sb.update(ok=False, error=f"Supabase active {sb['data_version']} ≠ pipeline {self.svc.data_version}")
        out["api"] = {"ok": True, "ms": int((time.perf_counter() - t0) * 1000)}
        out.update(config=self.svc.config_name, run_id=self.svc.run_id, data_version=self.svc.data_version,
                   ok=all(v["ok"] for v in out.values() if isinstance(v, dict)))
        return out
