"""B4 (tuần 6): rerank, ngưỡng từ chối, prompt rag_v2 trích dẫn [n], quét ngưỡng trên log dev.
Không cần GPU: reranker, retriever, LLM đều giả. Chạy: PYTHONPATH=. python -m pytest -q tests/test_b4.py"""
import pytest

import eval.metrics as M
from src.generate.llm_client import LLMResult
from src.generate.prompts import REFUSAL, build_prompt
from src.pipeline import RAGPipeline, is_hedged, is_refusal, parse_numbered_citations, unsupported_numbers
from tests.test_eval_harness import LLM_CFG

TEXT = {"BVP_A": "thời gian chờ 30 ngày", "BVP_B": "bảng phí 1.448.000 đồng", "BVP_C": "khác",
        "BTB_A": "thời gian chờ 60 ngày", "BTB_B": "loại trừ suy thận", "BTB_C": "khác"}


def cfg(prompt="rag_v2", min_score=None, use_filter=False, context_n=2):
    return {"name": "B4", "benchmark": "b.jsonl", "data_version": "v1", "chunking": "structure",
            "retrieval": {"mode": "hybrid", "top_k": 30, "use_filter": use_filter}, "context_n": context_n,
            "prompt": prompt, "llm": LLM_CFG, "seed": 42,
            "rerank": {"enabled": True, "model": "fake", "max_length": 1024, "top_n": context_n, "min_score": min_score}}


class Retr:
    """Thứ tự truy xuất cố định: chunk "C" đứng đầu, chunk đúng ở cuối; lọc product_code nếu có."""
    def search(self, query, filters=None, top_k=None, mode=None):
        ids = [c for c in ("BVP_C", "BTB_C", "BVP_B", "BTB_B", "BVP_A", "BTB_A")
               if not filters or c.split("_")[0] in filters["product_code"]]
        return [{"chunk_id": c, "score": 1 / r, "rank": r, "payload": {"chunk_id": c, "text": TEXT[c]}}
                for r, c in enumerate(ids, 1)]


class Rer:
    """Điểm cao cho đoạn chứa 'thời gian chờ' khi câu hỏi hỏi thời gian chờ; câu 'ngoài' → mọi điểm thấp."""
    def __init__(self):
        self.calls = []

    def score(self, query, texts):
        self.calls.append((query, len(texts)))
        if "ngoài" in query:
            return [0.01] * len(texts)
        return [0.9 if "thời gian chờ" in t else 0.2 if "khác" not in t else 0.05 for t in texts]


class LLM:
    def __init__(self, text="Thời gian chờ 30 ngày [1]. Bảng [2], [7]."):
        self.text, self.prompts = text, []

    def generate(self, prompt):
        self.prompts.append(prompt)
        return LLMResult(self.text, tokens_in=100, tokens_out=10, latency_ms=50, prefill_tok_s=None, decode_tok_s=None)


class QP:
    def plan(self, q):
        prods = [p for p in ("BVP", "BTB") if p in q]
        subs = [{"query": q, "filters": {"product_code": [p]}} for p in prods] or [{"query": q, "filters": None}]
        return {"products": prods, "matched": prods, "abbr": [], "query": q, "split": len(subs) > 1, "subqueries": subs}


@pytest.mark.parametrize("name", ["rag_v2", "rag_v3"])
def test_rag_v2_prompt_numbered(name):
    p = build_prompt(name, "Hỏi?", [{"chunk_id": "BVP_QT_C1", "text": "a"}, {"chunk_id": "BTB_QT_C2", "text": "b"}])
    assert '<doc so="1">' in p and '<doc so="2">' in p and "BVP_QT_C1" not in p and "SPMAU" not in p
    assert REFUSAL in p and p.endswith("Trả lời:")


def test_numbered_citations():
    ids = ["BVP_A", "BTB_B", "BVP_C"]
    assert parse_numbered_citations("a [1]. b [2][3], c [1, 3] d [9] [BVP_C] [SPMAU_X_Y]", ids) == \
        (["BVP_A", "BTB_B", "BVP_C"], ["[9]", "SPMAU_X_Y"])
    assert parse_numbered_citations("Điều 5 [Bảo Việt An Gia | Quy tắc]", ids) == ([], [])


def test_refusal_ignores_numbered_citation():
    assert is_refusal("[1] " + REFUSAL) and not is_hedged("[1] " + REFUSAL)


def test_unsupported_numbers():
    ctx = [{"text": "phí 1.448.000 đồng, chờ 30 ngày"}]
    assert unsupported_numbers("Phí 1.448.000 đồng [1], tuổi 45, chờ 90 ngày [2].", ctx, "người 45 tuổi") == ["90"]


def test_rerank_reorders_and_logs():
    rer, llm = Rer(), LLM()
    out = RAGPipeline(cfg(), llm, Retr(), reranker=rer).answer("thời gian chờ?")
    assert [h["chunk_id"] for h in out["retrieved"][:2]] == ["BVP_A", "BTB_A"]       # trước rerank ở hạng 5, 6
    assert [h["ret_rank"] for h in out["retrieved"][:2]] == [5, 6]
    assert out["retrieved"][0]["score"] == 0.9 and out["rerank_max"] == 0.9 and out["gated"] is False
    assert out["contexts"] == ["BVP_A", "BTB_A"]
    assert out["citations"] == ["BVP_A", "BTB_A"] and out["citations_invalid"] == ["[7]"]
    assert '<doc so="1">\nthời gian chờ 30 ngày' in llm.prompts[0]
    assert out["nums_unsupported"] == []


def test_gate_refuses_without_llm():
    llm = LLM()
    out = RAGPipeline(cfg(min_score=0.3), llm, Retr(), reranker=Rer()).answer("ngoài phạm vi?")
    assert out["gated"] and out["answer"] == REFUSAL and out["refused"] and llm.prompts == []
    assert out["tokens_out"] == 0 and out["rerank_max"] == 0.01
    out2 = RAGPipeline(cfg(min_score=None), llm, Retr(), reranker=Rer()).answer("ngoài phạm vi?")
    assert out2["gated"] is False and len(llm.prompts) == 1                         # null = không chặn


def test_rerank_per_product_before_interleave():
    rer = Rer()
    out = RAGPipeline(cfg(use_filter=True), LLM(), Retr(), qp=QP(), reranker=rer).answer("thời gian chờ BVP và BTB?")
    assert out["contexts"] == ["BVP_A", "BTB_A"]                                  # mỗi sản phẩm giữ hạng 1 của mình
    assert [n for _, n in rer.calls] == [3, 3] and out["qp"]["split"]


def test_gate_sweep():
    bench = {"q1": {"answerable": True, "group": "lookup"}, "q2": {"answerable": True, "group": "table"},
             "q3": {"answerable": False, "group": "out_of_scope"}}
    log = [{"qid": "q1", "rerank_max": 0.8, "answer": "30 ngày [1]", "gated": False},
           {"qid": "q2", "rerank_max": 0.2, "answer": "1.448.000 [1]", "gated": False},
           {"qid": "q3", "rerank_max": 0.1, "answer": "Có, 10 ngày.", "gated": False}]
    rows = {r["min_score"]: r for r in M.gate_sweep([log], bench, (0.0, 0.15, 0.25))}
    assert rows[0.0]["refusal_ok"] == 0.0 and rows[0.0]["false_refusal"] == 0.0
    assert rows[0.15]["refusal_ok"] == 1.0 and rows[0.15]["false_refusal"] == 0.0 and rows[0.15]["balanced"] == 1.0
    assert rows[0.25]["false_refusal"] == 0.5 and rows[0.25]["fr_table"] == 1.0
    with pytest.raises(ValueError):
        M.gate_sweep([[dict(log[0], gated=True)]], bench)


def test_gate_grid_and_detail():
    assert M.parse_grid("0.9:0.95:0.01") == (0.9, 0.91, 0.92, 0.93, 0.94, 0.95)
    bench = {"q1": {"answerable": True, "group": "lookup", "question": "a?"},
             "q2": {"answerable": True, "group": "table", "question": "b?"},
             "q3": {"answerable": False, "group": "out_of_scope", "question": "c?"}}
    log = [{"qid": "q1", "rerank_max": 0.99, "answer": "x [1]"}, {"qid": "q2", "rerank_max": 0.95, "answer": "y [1]"},
           {"qid": "q3", "rerank_max": 0.93, "answer": REFUSAL}]
    det = M.gate_detail([({}, log), ({}, [dict(l, answer="z") for l in log])], bench, 0.97)
    assert [d["qid"] for d in det] == ["q3", "q2"] and det[0]["llm_refused"] == "1/2"
