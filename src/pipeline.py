"""RAGPipeline(config).answer(query) -> dict: một câu hỏi qua truy xuất + sinh, dùng chung cho eval, demo, ĐA2.

Thành phần (LLM, Retriever) được truyền vào để test bằng đối tượng giả và để eval dùng chung một LLM/encoder
cho nhiều config trong một phiên. Dựng đủ từ config: `build_components()`.

Config dùng các khóa:
    retrieval.mode      none | dense | sparse | hybrid   (none = B0, không truy xuất)
    retrieval.top_k     số chunk truy xuất, ghi hết vào log để tính Recall@k với k bất kỳ ≤ top_k
    retrieval.use_filter  B3+: query processor (src/retrieve/query_processor.py): lọc product_code theo sản phẩm nhận
                        diện được, câu nhắc ≥ 2 sản phẩm truy xuất riêng từng sản phẩm rồi ghép xen kẽ
    context_n           số chunk đầu đưa vào prompt (mặc định 5)
    prompt              tên prompt trong src/generate/prompts.py
    rerank.enabled      B4: chấm lại top_k bằng bge-reranker-v2-m3 (src/retrieve/reranker.py); câu đã tách theo sản
                        phẩm thì rerank riêng từng danh sách rồi mới ghép xen kẽ. `retrieved` ghi theo thứ tự sau
                        rerank (score = điểm rerank, ret_rank/ret_score = hạng/điểm truy xuất)
    rerank.min_score    ngưỡng từ chối: điểm rerank cao nhất < min_score → trả câu từ chối chuẩn, không gọi LLM
                        (gated). null = không chặn (chạy dev để quét ngưỡng bằng eval.metrics --gate-sweep)
"""
from __future__ import annotations

import re
import time
import unicodedata

from src.generate.prompts import NUMBERED, REFUSAL, REFUSAL_CORE, build_prompt
from src.ingest.catalog import numbers

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


NUM_CITE = re.compile(r"\[\s*(\d{1,2}(?:\s*[,;]\s*\d{1,2})*)\s*\]")


def parse_numbered_citations(answer: str, ctx_ids: list[str]) -> tuple[list[str], list[str]]:
    """Prompt đánh số (rag_v2): [n], [n, m], [n][m] → chunk_id của đoạn thứ n. Trả (hợp lệ, không hợp lệ).
    Mã chunk viết thẳng (kiểu rag_v1) vẫn nhận nếu nằm trong ngữ cảnh."""
    ok, bad = [], []
    for block in NUM_CITE.findall(answer):
        for n in re.findall(r"\d+", block):
            i = int(n)
            if 1 <= i <= len(ctx_ids):
                if ctx_ids[i - 1] not in ok:
                    ok.append(ctx_ids[i - 1])
            elif f"[{i}]" not in bad:
                bad.append(f"[{i}]")
    for cid in parse_citations(answer):
        if cid in ok or cid in bad:
            continue
        (ok if cid in ctx_ids else bad).append(cid)
    return ok, bad


ANY_BRACKET = re.compile(r"\[[^\[\]]{1,200}\]")


def unsupported_numbers(answer: str, contexts: list[dict], query: str = "") -> list[str]:
    """Số trong câu trả lời (bỏ khối trong ngoặc vuông) không có trong ngữ cảnh lẫn câu hỏi: cờ hậu kiểm
    (skill bước 10), không sửa câu trả lời."""
    known = set(numbers(query))
    for c in contexts:
        known.update(numbers(c["text"]))
    out = []
    for n in numbers(ANY_BRACKET.sub(" ", answer)):
        if n not in known and n not in out:
            out.append(n)
    return out


def _norm(s: str) -> str:
    return " ".join(unicodedata.normalize("NFC", s).lower().split())


REFUSAL_MAX_LEAD_WORDS = 8   # số từ tối đa đứng trước cụm từ chối ("Xin lỗi, tài liệu ..." vẫn là từ chối)
WORD = re.compile(r"\w+", re.UNICODE)


def _lead_words(answer: str) -> int | None:
    """Số từ nội dung đứng trước lần xuất hiện ĐẦU TIÊN của cụm từ chối; None nếu không có cụm từ chối."""
    a = _norm(answer)
    i = a.find(_norm(REFUSAL_CORE))
    if i < 0:
        return None
    return len(WORD.findall(ANY_BRACKET.sub(" ", a[:i])))


def is_refusal(answer: str) -> bool:
    """Từ chối = câu trả lời MỞ ĐẦU bằng câu từ chối (trước cụm "không có thông tin để trả lời" tối đa
    REFUSAL_MAX_LEAD_WORDS từ). Câu đã trả lời rồi chép thêm câu từ chối ở cuối không tính là từ chối
    (decision-log 2026-11-07, dev B2: 3/8 câu "từ chối" theo quy tắc cũ là như vậy); xem is_hedged."""
    n = _lead_words(answer)
    return n is not None and n <= REFUSAL_MAX_LEAD_WORDS


def is_hedged(answer: str) -> bool:
    """Đã trả lời nhưng có chèn câu từ chối (thường ở cuối): đầu vào cho prompt B4."""
    n = _lead_words(answer)
    return n is not None and n > REFUSAL_MAX_LEAD_WORDS


class RAGPipeline:
    def __init__(self, cfg: dict, llm, retriever=None, qp=None, reranker=None):
        self.cfg = cfg
        self.mode = cfg["retrieval"]["mode"]
        self.top_k = cfg["retrieval"]["top_k"]
        self.context_n = cfg.get("context_n", 5)
        self.prompt_name = cfg.get("prompt") or ("norag_v1" if self.mode == "none" else "rag_v1")
        if self.mode != "none" and retriever is None:
            raise ValueError(f"retrieval.mode={self.mode} cần retriever")
        self.llm, self.retriever = llm, retriever
        rr = cfg.get("rerank") or {}
        self.reranker, self.min_score = None, None
        if rr.get("enabled") and self.mode != "none":
            if reranker is None:
                from src.retrieve.reranker import BgeReranker
                reranker = BgeReranker(rr.get("model", "BAAI/bge-reranker-v2-m3"), rr.get("max_length", 1024))
            self.reranker, self.min_score = reranker, rr.get("min_score")
            if rr.get("top_n", self.context_n) != self.context_n:
                raise ValueError("rerank.top_n phải bằng context_n (số đoạn đưa vào prompt)")
        self.qp = None
        if cfg["retrieval"].get("use_filter") and self.mode != "none":
            if qp is None:
                from src.retrieve.query_processor import QueryProcessor
                qp = QueryProcessor.from_files(**cfg.get("query_processor", {}))
            self.qp = qp
        num_ctx = cfg["llm"].get("num_ctx", 4096)
        self.prompt_budget = num_ctx - cfg["llm"].get("max_tokens", 600)

    def retrieve(self, query: str) -> tuple[list[dict], int, dict | None]:
        """Trả (hits, retrieval_ms, plan của query processor hoặc None). retrieval_ms gồm cả rerank."""
        if self.mode == "none":
            return [], 0, None
        t0 = time.perf_counter()
        self.rerank_ms = 0
        if self.qp is None:
            hits, plan = self._rerank(query, self.retriever.search(query, top_k=self.top_k, mode=self.mode)), None
        else:
            hits, plan = self._retrieve_planned(query)
        return hits, int((time.perf_counter() - t0) * 1000), plan

    def _rerank(self, query: str, hits: list[dict]) -> list[dict]:
        if self.reranker is None or not hits:
            return hits
        from src.retrieve.reranker import rerank

        t0 = time.perf_counter()
        out = rerank(self.reranker, query, hits)
        self.rerank_ms += int((time.perf_counter() - t0) * 1000)
        return out

    def _retrieve_planned(self, query: str) -> tuple[list[dict], dict]:
        from src.retrieve.query_processor import interleave

        plan = self.qp.plan(query)
        subs = plan["subqueries"]
        lists = [self.retriever.search(s["query"], filters=s["filters"], top_k=self.top_k, mode=self.mode) for s in subs]
        # B4: rerank TRƯỚC khi ghép để mỗi sản phẩm vẫn giữ suất trong top-n (rerank chung dễ dồn về một sản phẩm)
        lists = [self._rerank(s["query"], x) for s, x in zip(subs, lists)]
        hits = lists[0] if len(lists) == 1 else interleave(lists, self.top_k)
        plan["fallback"] = False
        if any(s["filters"] for s in subs) and len(hits) < self.context_n:
            # Lọc sai sản phẩm hoặc sản phẩm ít chunk: bù bằng kết quả không lọc
            extra = self.retriever.search(plan["query"], top_k=self.top_k, mode=self.mode)
            seen = {h["chunk_id"] for h in hits}
            hits = [dict(h) for h in hits] + [dict(h) for h in extra if h["chunk_id"] not in seen]
            hits = hits[:self.top_k]
            for r, h in enumerate(hits, 1):
                h["rank"] = r
            if self.reranker is not None:
                hits = self._rerank(plan["query"], [{k: v for k, v in h.items() if k not in ("ret_rank", "ret_score")}
                                                    | {"score": h.get("ret_score", h["score"])} for h in hits])
            plan["fallback"] = True
        plan["n_hits"] = [len(x) for x in lists]
        return hits, plan

    def prepare(self, query: str) -> tuple[list[dict], list[dict], str, int]:
        """Truy xuất + dựng prompt, chưa gọi LLM (dùng cả cho bước kiểm độ dài prompt trước khi chạy)."""
        hits, retrieval_ms, plan = self.retrieve(query)
        self.last_plan, self.last_hits = plan, hits   # demo (app/service.py) đọc payload chunk để hiển thị nguồn
        contexts = [{"chunk_id": h["chunk_id"], "text": h["payload"]["text"]} for h in hits[:self.context_n]]
        return hits, contexts, build_prompt(self.prompt_name, query, contexts or None), retrieval_ms

    def gated(self, hits: list[dict]) -> bool:
        """B4: điểm rerank cao nhất dưới ngưỡng → từ chối không gọi LLM."""
        return self.reranker is not None and self.min_score is not None and \
            (not hits or max(h["score"] for h in hits) < self.min_score)

    def answer(self, query: str) -> dict:
        t0 = time.perf_counter()
        hits, contexts, prompt, retrieval_ms = self.prepare(query)
        gated = self.gated(hits)
        if gated:
            text, res = REFUSAL, None
        else:
            res = self.llm.generate(prompt)
            text = res.text
        ctx_ids = [c["chunk_id"] for c in contexts]
        if self.prompt_name in NUMBERED:
            cites, bad = parse_numbered_citations(text, ctx_ids)
        else:
            raw = parse_citations(text)
            cites, bad = [c for c in raw if c in ctx_ids], [c for c in raw if c not in ctx_ids]
        ret = [{"chunk_id": h["chunk_id"], "score": round(h["score"], 6), "rank": h["rank"]} for h in hits]
        if self.reranker is not None:
            for r, h in zip(ret, hits):
                r["ret_rank"] = h.get("ret_rank")
        return {
            "query": query,
            "retrieved": ret,
            "contexts": ctx_ids,
            "answer": text,
            "citations": cites,
            "citations_invalid": bad,
            "refused": is_refusal(text),
            "latency_ms": int((time.perf_counter() - t0) * 1000),
            "retrieval_ms": retrieval_ms,
            "llm_ms": res.latency_ms if res else 0,
            "tokens_in": res.tokens_in if res else 0,
            "tokens_out": res.tokens_out if res else 0,
            # Ollama cắt phần ĐẦU prompt (mất hướng dẫn) khi prompt vượt ngữ cảnh. tokens_in có thể thiếu phần prefix
            # Ollama tái dùng từ KV cache, nên cờ này chỉ là kiểm sau; kiểm chính là check_prompt_lengths trước khi chạy
            "ctx_overflow": bool(res and res.tokens_in and res.tokens_in >= self.prompt_budget),
            "prompt": self.prompt_name,
            "nums_unsupported": [] if gated else unsupported_numbers(text, contexts, query) if contexts else None,
            **({"rerank_ms": self.rerank_ms, "rerank_max": round(max((h["score"] for h in hits), default=0.0), 6),
                "gated": gated} if self.reranker is not None else {}),
            **({"qp": {k: v for k, v in self.last_plan.items() if k != "subqueries"}
                       | {"filters": [s["filters"] for s in self.last_plan["subqueries"]]}} if self.last_plan else {}),
        }


def build_components(cfgs: list[dict], processed_root, vectors_root, llm=None, encoder=None, client=None,
                     reranker=None) -> dict:
    """Dựng LLM (warmup TRƯỚC khi nạp bge-m3), encoder, Qdrant và Retriever cho các config; dùng chung giữa config.

    processed_root, vectors_root: thư mục processed/{ver}, vectors/{ver} (cùng data_version cho mọi config).
    Trả {"llm", "warmup", "gpu_after_torch", "retrievers": {chunking: Retriever}, "index": {collection: n},
    "reranker"}; reranker (B4) nạp một lần nếu có config bật rerank, mọi config phải cùng model/max_length.
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
    rr = {(c["rerank"]["model"], c["rerank"].get("max_length", 1024)) for c in cfgs
          if (c.get("rerank") or {}).get("enabled") and c["retrieval"]["mode"] != "none"}
    if len(rr) > 1:
        raise ValueError(f"các config bật rerank phải cùng model/max_length, đang có {rr}")
    if rr and reranker is None:
        from src.retrieve.reranker import BgeReranker
        reranker = BgeReranker(*rr.pop())
    out["reranker"] = reranker
    if reranker is not None and hasattr(llm, "gpu_status"):
        out["gpu_after_torch"] = llm.gpu_status()
    return out
