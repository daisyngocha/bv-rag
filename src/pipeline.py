"""RAGPipeline(config).answer(query) -> dict: một câu hỏi qua truy xuất + sinh, dùng chung cho eval, demo, ĐA2.

Thành phần (LLM, Retriever) được truyền vào để test bằng đối tượng giả và để eval dùng chung một LLM/encoder
cho nhiều config trong một phiên. Dựng đủ từ config: `build_components()`.

Config dùng các khóa:
    retrieval.mode      none | dense | sparse | hybrid   (none = B0, không truy xuất)
    retrieval.top_k     số chunk truy xuất, ghi hết vào log để tính Recall@k với k bất kỳ ≤ top_k
    retrieval.use_filter  B3+: lọc metadata (chưa dùng ở B0–B2)
    context_n           số chunk đầu đưa vào prompt (mặc định 5)
    prompt              tên prompt trong src/generate/prompts.py
    rerank.enabled      B4 (chưa hỗ trợ ở đây; báo lỗi nếu bật)
"""
from __future__ import annotations

import re
import time
import unicodedata

from src.generate.prompts import REFUSAL_CORE, build_prompt

CITE_BLOCK = re.compile(r"\[([^\[\]]{3,200})\]")
CITE_ID = re.compile(r"[A-Za-z0-9]+(?:_[A-Za-z0-9]+)+")


def parse_citations(answer: str) -> list[str]:
    """Mã chunk trong ngoặc vuông, giữ thứ tự, bỏ trùng. Chấp nhận [A, B] và [A; B]."""
    out = []
    for block in CITE_BLOCK.findall(answer):
        for cid in CITE_ID.findall(block):
            if cid not in out:
                out.append(cid)
    return out


def _norm(s: str) -> str:
    return " ".join(unicodedata.normalize("NFC", s).lower().split())


def is_refusal(answer: str) -> bool:
    """Từ chối = câu trả lời chứa cụm cốt lõi của câu từ chối chuẩn (kể cả khi model thêm lời dẫn)."""
    return _norm(REFUSAL_CORE) in _norm(answer)


class RAGPipeline:
    def __init__(self, cfg: dict, llm, retriever=None):
        self.cfg = cfg
        self.mode = cfg["retrieval"]["mode"]
        self.top_k = cfg["retrieval"]["top_k"]
        self.context_n = cfg.get("context_n", 5)
        self.prompt_name = cfg.get("prompt") or ("norag_v1" if self.mode == "none" else "rag_v1")
        if cfg.get("rerank", {}).get("enabled"):
            raise NotImplementedError("rerank chưa có trong pipeline (B4, tuần 6)")
        if cfg["retrieval"].get("use_filter"):
            raise NotImplementedError("lọc metadata/query processor chưa có trong pipeline (B3, tuần 5)")
        if self.mode != "none" and retriever is None:
            raise ValueError(f"retrieval.mode={self.mode} cần retriever")
        self.llm, self.retriever = llm, retriever
        num_ctx = cfg["llm"].get("num_ctx", 4096)
        self.prompt_budget = num_ctx - cfg["llm"].get("max_tokens", 600)

    def retrieve(self, query: str) -> tuple[list[dict], int]:
        if self.mode == "none":
            return [], 0
        t0 = time.perf_counter()
        hits = self.retriever.search(query, top_k=self.top_k, mode=self.mode)
        return hits, int((time.perf_counter() - t0) * 1000)

    def prepare(self, query: str) -> tuple[list[dict], list[dict], str, int]:
        """Truy xuất + dựng prompt, chưa gọi LLM (dùng cả cho bước kiểm độ dài prompt trước khi chạy)."""
        hits, retrieval_ms = self.retrieve(query)
        contexts = [{"chunk_id": h["chunk_id"], "text": h["payload"]["text"]} for h in hits[:self.context_n]]
        return hits, contexts, build_prompt(self.prompt_name, query, contexts or None), retrieval_ms

    def answer(self, query: str) -> dict:
        t0 = time.perf_counter()
        hits, contexts, prompt, retrieval_ms = self.prepare(query)
        res = self.llm.generate(prompt)
        ctx_ids = [c["chunk_id"] for c in contexts]
        cites = parse_citations(res.text)
        return {
            "query": query,
            "retrieved": [{"chunk_id": h["chunk_id"], "score": round(h["score"], 6), "rank": h["rank"]} for h in hits],
            "contexts": ctx_ids,
            "answer": res.text,
            "citations": [c for c in cites if c in ctx_ids],
            "citations_invalid": [c for c in cites if c not in ctx_ids],
            "refused": is_refusal(res.text),
            "latency_ms": int((time.perf_counter() - t0) * 1000),
            "retrieval_ms": retrieval_ms,
            "llm_ms": res.latency_ms,
            "tokens_in": res.tokens_in,
            "tokens_out": res.tokens_out,
            # Ollama cắt phần ĐẦU prompt (mất hướng dẫn) khi prompt vượt ngữ cảnh. tokens_in có thể thiếu phần prefix
            # Ollama tái dùng từ KV cache, nên cờ này chỉ là kiểm sau; kiểm chính là check_prompt_lengths trước khi chạy
            "ctx_overflow": bool(res.tokens_in and res.tokens_in >= self.prompt_budget),
            "prompt": self.prompt_name,
        }


def build_components(cfgs: list[dict], processed_root, vectors_root, llm=None, encoder=None, client=None) -> dict:
    """Dựng LLM (warmup TRƯỚC khi nạp bge-m3), encoder, Qdrant và Retriever cho các config; dùng chung giữa config.

    processed_root, vectors_root: thư mục processed/{ver}, vectors/{ver} (cùng data_version cho mọi config).
    Trả {"llm", "warmup", "gpu_after_torch", "retrievers": {chunking: Retriever}, "index": {collection: n}}.
    """
    from pathlib import Path

    from src.generate.llm_client import make_llm

    llm_blocks = {repr(sorted(c["llm"].items())) for c in cfgs}
    if len(llm_blocks) > 1:
        raise ValueError("các config phải có khối llm giống hệt nhau (quy ước B0–B4)")
    vers = {c["data_version"] for c in cfgs}
    if len(vers) > 1:
        raise ValueError(f"các config phải cùng data_version, đang có {vers}")
    out = {"retrievers": {}, "index": {}}
    if llm is None:
        llm = make_llm(cfgs[0]["llm"], seed=cfgs[0].get("seed"))
        out["warmup"] = llm.warmup()
    out["llm"] = llm
    need = sorted({c["chunking"] for c in cfgs if c["retrieval"]["mode"] != "none"})
    if not need:
        return out
    from src.ingest.indexer import CHUNK_FILES, build_index, read_jsonl
    from src.retrieve.hybrid import Retriever, collection_name, get_client

    if encoder is None:
        from src.retrieve.encoder import M3Encoder
        encoder = M3Encoder()
    if hasattr(llm, "gpu_status"):
        out["gpu_after_torch"] = llm.gpu_status()
    client = client or get_client()
    ver = vers.pop()
    for ch in need:
        col = collection_name(ver, ch)
        chunks = read_jsonl(Path(processed_root) / CHUNK_FILES[ch])
        out["index"][col] = build_index(client, col, chunks, Path(vectors_root) / ch)
        out["retrievers"][ch] = Retriever(client, col, encoder)
    return out
