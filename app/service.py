"""Lớp dịch vụ demo (tuần 7): bọc RAGPipeline, gắn metadata nguồn cho từng trích dẫn để giao diện hiển thị.

Không đổi logic trả lời: câu trả lời, trích dẫn, từ chối lấy nguyên từ `RAGPipeline.answer()` (cùng config với run test
B4). Dịch vụ chỉ thêm: tên sản phẩm, loại tài liệu, mục, trang, link sản phẩm (từ catalog) và đoạn văn bản nguồn.

Dựng đủ trên Colab L4: `DemoService.from_config("configs/B4.yaml")` (đọc $DRIVE_DIR/processed, vectors như eval).
"""
from __future__ import annotations

import json
import os
import re
import threading
from pathlib import Path

DOC_LABEL = {"quy_tac": "Quy tắc", "bang_quyen_loi": "Bảng quyền lợi", "bang_phi": "Biểu phí"}
HEADER = re.compile(r"^\[[^\]\n]*\]\n")   # dòng header ngữ cảnh "[Tên SP | Loại TL | Điều …]" đầu text chunk


def load_catalog(path="data/catalog.json") -> dict:
    """{product_code: {"name", "url", "effective_date", "docs": {file: url}}}."""
    cat = json.load(open(path, encoding="utf-8"))
    out = {}
    for p in cat["products"]:
        docs = {d["file"]: d.get("url") for d in p.get("documents", [])}
        out[p["product_code"]] = {"name": p["product_name"], "effective_date": p.get("effective_date"),
                                  "url": next((u for u in docs.values() if u), None), "docs": docs}
    return out


def source_of(payload: dict, catalog: dict) -> dict:
    """Thông tin nguồn của một chunk để hiển thị (không gồm text)."""
    code = payload.get("product_code")
    prod = catalog.get(code, {})
    src = payload.get("source_file")
    return {
        "product_code": code,
        "product_name": prod.get("name", code),
        "doc_type": payload.get("doc_type"),
        "doc_label": DOC_LABEL.get(payload.get("doc_type"), payload.get("doc_type")),
        "section": payload.get("section_path"),
        "page": payload.get("page"),
        "source_file": src,
        "url": prod.get("docs", {}).get(src) or prod.get("url"),
        "effective_date": payload.get("effective_date") or prod.get("effective_date"),
        "is_table": payload.get("is_table"),
        "ocr": payload.get("ocr"),
        "manual": payload.get("manual"),
    }


class DemoService:
    def __init__(self, pipe, catalog: dict, config_name: str = ""):
        self.pipe, self.catalog, self.config_name = pipe, catalog, config_name
        self._lock = threading.Lock()   # một LLM/encoder dùng chung: xử lý tuần tự, tránh tranh VRAM

    @classmethod
    def from_config(cls, config_path: str, processed=None, vectors=None, catalog_path="data/catalog.json"):
        from eval.run_eval import load_config
        from src.pipeline import RAGPipeline, build_components

        cfg = load_config(config_path)
        ver, drive = cfg["data_version"], os.environ.get("DRIVE_DIR")
        processed = Path(processed or (f"{drive}/processed/{ver}" if drive else f"data/processed/{ver}"))
        vectors = Path(vectors or (f"{drive}/vectors/{ver}" if drive else f"data/vectors/{ver}"))
        comps = build_components([cfg], processed, vectors)
        pipe = RAGPipeline(cfg, comps["llm"], comps["retrievers"].get(cfg["chunking"]), reranker=comps.get("reranker"))
        svc = cls(pipe, load_catalog(catalog_path), cfg["name"])
        svc.info = {"index": comps["index"], "warmup": comps.get("warmup"), "gpu": comps.get("gpu_after_torch")}
        return svc

    def products(self) -> list[dict]:
        return [{"product_code": k, "product_name": v["name"], "effective_date": v["effective_date"], "url": v["url"]}
                for k, v in self.catalog.items()]

    def ask(self, question: str) -> dict:
        question = " ".join(question.split())
        if not question:
            raise ValueError("câu hỏi rỗng")
        with self._lock:
            res = self.pipe.answer(question)
            hits = list(getattr(self.pipe, "last_hits", []) or [])
        payload = {h["chunk_id"]: h["payload"] for h in hits}
        n_ctx = len(res["contexts"])
        sources = []
        for i, cid in enumerate(res["contexts"], 1):
            p = payload.get(cid, {"chunk_id": cid})
            sources.append({"n": i, "chunk_id": cid, "cited": cid in res["citations"],
                            "score": next((h["score"] for h in hits if h["chunk_id"] == cid), None),
                            "text": HEADER.sub("", p.get("text", ""), count=1), **source_of(p, self.catalog)})
        return {
            "question": question,
            "answer": res["answer"],
            "refused": res["refused"],
            "gated": res.get("gated", False),
            "citations": [{"n": res["contexts"].index(c) + 1, "chunk_id": c} for c in res["citations"]],
            "citations_invalid": res["citations_invalid"],
            "nums_unsupported": res.get("nums_unsupported") or [],
            "sources": sources,
            "products_detected": (res.get("qp") or {}).get("products", []),
            "rerank_max": res.get("rerank_max"),
            "latency_ms": res["latency_ms"],
            "retrieval_ms": res["retrieval_ms"],
            "llm_ms": res["llm_ms"],
            "tokens_in": res["tokens_in"],
            "tokens_out": res["tokens_out"],
            "config": self.config_name,
            "n_contexts": n_ctx,
        }
