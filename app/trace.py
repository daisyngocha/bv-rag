"""Kết quả pipeline → 1 dòng traces + N dòng retrieval_logs (SV-14). Cùng nguồn với log.jsonl."""
from __future__ import annotations

import os


def cost_usd(latency_ms: int | None) -> float | None:
    """Chi phí theo giờ GPU: $GPU_USD_PER_HOUR × thời gian xử lý. Không đặt biến → null."""
    rate = os.environ.get("GPU_USD_PER_HOUR")
    if not rate or latency_ms is None:
        return None
    return round(float(rate) * latency_ms / 3_600_000, 6)


def build_trace_rows(res: dict, hits: list[dict], data_version: str, message_id: str,
                     retrieval_mode: str, error: str | None = None) -> tuple[dict, list[dict]]:
    qp = res.get("qp") or {}
    rerank_ms = res.get("rerank_ms") or 0
    trace = {
        "message_id": message_id,
        "query_processed": qp.get("query"),
        "detected_products": qp.get("products") or None,
        "retrieval_mode": retrieval_mode,
        "latency_ms": int(res.get("latency_ms") or 0),
        "tokens_in": res.get("tokens_in") or None,
        "tokens_out": res.get("tokens_out") or None,
        "cost_usd": cost_usd(res.get("latency_ms")),
        "timings_ms": {"retrieve": max(int(res.get("retrieval_ms") or 0) - rerank_ms, 0), "rerank": rerank_ms,
                       "generate": int(res.get("llm_ms") or 0)},
        "error": error,
    }
    in_ctx = set(res.get("contexts") or [])
    reranked = "rerank_max" in res
    logs = []
    for h in hits:
        logs.append({
            "message_id": message_id, "rank": h["rank"], "data_version": data_version, "chunk_id": h["chunk_id"],
            "score": float(h.get("ret_score", h["score"]) if reranked else h["score"]),
            "rerank": float(h["score"]) if reranked else None,
            "in_context": h["chunk_id"] in in_ctx,
        })
    return trace, logs
