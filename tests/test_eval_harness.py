"""Harness tuần 4: prompt, pipeline, run_eval, metrics với LLM/Retriever giả (không cần GPU, Qdrant, Ollama).
Chạy: PYTHONPATH=. python -m pytest -q tests/test_eval_harness.py"""
import json

import pytest

import eval.metrics as M
import eval.run_eval as RE
from src.generate.llm_client import LLMResult
from src.generate.prompts import REFUSAL, build_prompt
from src.pipeline import RAGPipeline, is_refusal, parse_citations

LLM_CFG = {"provider": "ollama", "model": "fake", "temperature": 0.1, "max_tokens": 600, "num_ctx": 4096}


def cfg(name="B2", mode="dense", chunking="structure", bench="benchmark.jsonl"):
    return {"name": name, "benchmark": bench, "data_version": "v1", "chunking": chunking,
            "retrieval": {"mode": mode, "top_k": 30, "use_filter": False}, "context_n": 2,
            "prompt": "norag_v1" if mode == "none" else "rag_v1",
            "rerank": {"enabled": False}, "llm": LLM_CFG, "seed": 42, "_path": f"configs/{name}.yaml"}


class FakeLLM:
    """Trả lời theo câu hỏi trong prompt: 'ngoài' → từ chối; còn lại trích chunk đầu tiên của ngữ cảnh."""
    def __init__(self):
        self.gen_options, self.prompts = {}, []

    def generate(self, prompt):
        self.prompts.append(prompt)
        q = prompt.rsplit("Câu hỏi:", 1)[1]
        if "ngoài" in q:
            text = REFUSAL
        elif '<doc id="' in prompt:
            cid = prompt.split('<doc id="', 1)[1].split('"', 1)[0]
            text = f"Thời gian chờ là 30 ngày [{cid}]. Xem thêm [KHONG_CO_ID]."
        else:
            text = "Khoảng 30 ngày."
        return LLMResult(text, tokens_in=len(prompt) // 4, tokens_out=12, latency_ms=100,
                         prefill_tok_s=None, decode_tok_s=None)


class FakeRetriever:
    def __init__(self, ranking):
        self.ranking = ranking

    def search(self, query, top_k=None, mode=None):
        ids = self.ranking.get(query, [])
        return [{"chunk_id": c, "score": 1 / r, "rank": r, "payload": {"chunk_id": c, "text": f"[SP | QT]\n{c} 30 ngày"}}
                for r, c in enumerate(ids, 1)][:top_k]


BENCH = [
    {"qid": "v1-0001", "question": "Q1 thời gian chờ?", "answer": "30 ngày.", "evidence_ids": ["SP_S1"], "products": ["BVP"],
     "group": "lookup", "difficulty": "easy", "answerable": True, "split": "dev", "version": "v1"},
    {"qid": "v1-0002", "question": "Q2 so sánh?", "answer": "BVP 30 ngày, BTB 60 ngày.", "evidence_ids": ["SP_S2", "SP_S3"],
     "products": ["BVP", "BTB"], "group": "compare", "difficulty": "hard", "answerable": True, "split": "dev", "version": "v1"},
    {"qid": "v1-0003", "question": "Q3 ngoài phạm vi?", "answer": REFUSAL, "evidence_ids": [], "products": [],
     "group": "out_of_scope", "difficulty": "easy", "answerable": False, "split": "dev", "version": "v1"},
    {"qid": "v1-0004", "question": "Q4 test?", "answer": "x", "evidence_ids": ["SP_S1"], "products": ["BVP"],
     "group": "lookup", "difficulty": "easy", "answerable": True, "split": "test", "version": "v1"},
]
RANKING = {"Q1 thời gian chờ?": ["SP_S1", "SP_S9"], "Q2 so sánh?": ["SP_S9", "SP_S2", "SP_S8", "SP_S3"], "Q3 ngoài phạm vi?": ["SP_S7"]}


def test_prompts():
    p = build_prompt("rag_v1", "Hỏi?", [{"chunk_id": "A_B", "text": "nội dung {có ngoặc}"}])
    assert '<doc id="A_B">' in p and "nội dung {có ngoặc}" in p and REFUSAL in p and p.endswith("Trả lời:")
    assert "<doc" not in build_prompt("norag_v1", "Hỏi?")
    with pytest.raises(ValueError):
        build_prompt("rag_v1", "Hỏi?", [])
    with pytest.raises(KeyError):
        build_prompt("khong_co", "Hỏi?")


def test_citations_and_refusal():
    assert parse_citations("a [BVP_QT_C1_M2_K1]. b [BTB_BQL_S1_TB1, BVP_QT_C1_M2_K1; ITC_BP_S1_TB2] [1]") == \
        ["BVP_QT_C1_M2_K1", "BTB_BQL_S1_TB1", "ITC_BP_S1_TB2"]
    assert is_refusal(REFUSAL)
    assert is_refusal("Xin lỗi, tài liệu  KHÔNG có thông tin để trả lời câu hỏi này")
    assert not is_refusal("Thời gian chờ là 30 ngày.")


def test_pipeline_rag_and_norag():
    llm = FakeLLM()
    out = RAGPipeline(cfg(), llm, FakeRetriever(RANKING)).answer("Q2 so sánh?")
    assert out["contexts"] == ["SP_S9", "SP_S2"] and [h["chunk_id"] for h in out["retrieved"]] == ["SP_S9", "SP_S2", "SP_S8", "SP_S3"]
    assert out["citations"] == ["SP_S9"] and out["citations_invalid"] == ["KHONG_CO_ID"]
    assert not out["refused"] and not out["ctx_overflow"]
    b0 = RAGPipeline(cfg("B0", "none", "fixed"), llm).answer("Q1 thời gian chờ?")
    assert b0["retrieved"] == [] and b0["contexts"] == [] and "<doc" not in llm.prompts[-1]
    with pytest.raises(ValueError):   # rerank.top_n phải bằng context_n
        RAGPipeline({**cfg(), "rerank": {"enabled": True, "top_n": 5}}, llm, FakeRetriever(RANKING), reranker=object())


def _run(tmp_path, monkeypatch, c, split="dev", **kw):
    bench = tmp_path / "benchmark.jsonl"
    bench.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in BENCH), encoding="utf-8")
    c = {**c, "benchmark": str(bench)}
    rows = RE.select(RE.read_jsonl(bench), split)
    run_id = RE.make_run_id(c, "v1", split, "20261110-2000", kw.get("rep"))
    pipe = RAGPipeline(c, FakeLLM(), FakeRetriever(RANKING) if c["retrieval"]["mode"] != "none" else None)
    meta = {"run_id": run_id, "config": c["_path"], "benchmark": str(bench), "benchmark_sha256": RE.sha256(bench),
            "benchmark_version": "v1", "data_version": "v1", "chunking": c["chunking"],
            "retrieval_mode": c["retrieval"]["mode"], "split": split, "runtime": "colab", "gpu": "L4",
            "llm_gpu_pct_start": 100.0, "ctx_check": {"over": []}}
    pipe.llm.gpu_status = lambda: {"gpu_pct": 100.0}
    return RE.run_one(pipe, c, rows, tmp_path / "runs" / run_id, run_id, meta, 42), tmp_path / "runs" / run_id


def test_run_and_metrics_structure(tmp_path, monkeypatch):
    meta, run_dir = _run(tmp_path, monkeypatch, cfg())
    assert meta["n"] == meta["n_logged"] == 3 and meta["llm_gpu_pct"] == 100.0
    assert M.official(meta)[0]
    # chạy lại (resume) không ghi trùng câu
    meta2, _ = _run(tmp_path, monkeypatch, cfg())
    assert meta2["n_logged"] == 3
    m, log = M.load_run(run_dir)
    rows = {r["group"]: r for r in M.evaluate(m, log, {b["qid"]: b for b in BENCH}, None, 0.5)}
    a = rows["all"]
    assert a["recall@1"] == 0.5 and a["recall@3"] == 1.0          # Q1 rank 1, Q2 rank 2
    assert a["mrr"] == 0.75
    assert a["refusal_ok"] == 1.0 and a["false_refusal"] == 0.0
    assert a["cite_rate"] == 1.0 and a["cite_prec"] == 0.5        # Q1 trích S1 (đúng), Q2 trích S9 (sai)
    assert rows["out_of_scope"]["recall@5"] is None or rows["out_of_scope"]["n_answerable"] == 0
    assert a["num_recall"] == pytest.approx(0.75)                  # Q1: 30 có; Q2: 30 có, 60 không
    path = M.result_path(m, tmp_path / "results")
    assert path.name == "B2_v1_dev_20261110-2000.csv"


def test_result_path_and_groups():
    meta = lambda rid: {"run_id": rid, "config": "configs/B4.yaml", "benchmark_version": "v1", "split": "dev",
                        "started_at": "2026-11-07T11:31:00"}
    a, b = M.result_path(meta("B4_v1_dev_20261107-1131_r0"), M.Path("r")), M.result_path(meta("B4_v1_dev_20261107-1259_r0"), M.Path("r"))
    assert a.name == "B4_v1_dev_20261107-1131_r0.csv" and b.name == "B4_v1_dev_20261107-1259_r0.csv"
    assert M.result_path(dict(meta("B4_v1_test_20261107-1400"), split="test"), M.Path("r")).name == "B4_v1_test_20261107-1400.csv"
    assert M.run_group("B4_v1_dev_20261107-1259_r2") == "B4_v1_dev_20261107-1259"
    row = lambda v: [{"group": "all", "config": "B4", "split": "dev", "refusal_ok": v}]
    summ = M.repeat_summary({"B4_v1_dev_20261107-1131_r0": row(0.6), "B4_v1_dev_20261107-1131_r1": row(0.6),
                             "B4_v1_dev_20261107-1259_r0": row(0.8), "B4_v1_dev_20261107-1259_r1": row(0.8)})
    assert [(r["run"], r["runs"], r["refusal_ok"]) for r in summ] == \
        [("B4_v1_dev_20261107-1131", 2, "0.600 ± 0.000"), ("B4_v1_dev_20261107-1259", 2, "0.800 ± 0.000")]


def test_full_recall_all_evidence(tmp_path, monkeypatch):
    meta, run_dir = _run(tmp_path, monkeypatch, cfg())
    m, log = M.load_run(run_dir)
    a = M.evaluate(m, log, {b["qid"]: b for b in BENCH}, None, 0.5)[0]
    # Q1: S1 ∈ top5 → 1; Q2: S2 và S3 đều ∈ top5 → 1
    assert a["full_recall@5"] == 1.0


def test_fixed_chunk_alignment():
    align = {"SP_S1": [["F1", 0.9], ["F2", 0.3]], "SP_S2": [["F5", 0.4], ["F6", 0.35]]}
    rel = M.relevance_fn({"chunking": "fixed"}, align, 0.5)
    assert rel("F1", ["SP_S1"]) == {"SP_S1"} and rel("F2", ["SP_S1"]) == set()
    assert rel("F5", ["SP_S2"]) == {"SP_S2"} and rel("F6", ["SP_S2"]) == set()   # F5 phủ S2 nhiều nhất → luôn tính
    assert M.relevance_fn({"chunking": "fixed"}, align, 0.3)("F2", ["SP_S1"]) == {"SP_S1"}


def test_b0_metrics_and_repeat_summary(tmp_path, monkeypatch):
    res = {}
    for rep in (0, 1):
        meta, run_dir = _run(tmp_path, monkeypatch, cfg("B0", "none", "fixed"), rep=rep)
        m, log = M.load_run(run_dir)
        res[m["run_id"]] = M.evaluate(m, log, {b["qid"]: b for b in BENCH}, None, 0.5)
        assert M.result_path(m, tmp_path).name.endswith(f"_r{rep}.csv")
    a = res[next(iter(res))][0]
    assert a["recall@5"] is None and a["mrr"] is None and a["cite_rate"] is None
    assert a["refusal_ok"] == 1.0 and a["false_refusal"] == 0.0
    summ = M.repeat_summary(res)
    assert summ[0]["runs"] == 2 and summ[0]["refusal_ok"] == "1.000 ± 0.000"


def test_official_flags():
    ok, why = M.official({"runtime": "local", "gpu": None, "llm_gpu_pct": 80, "n": 3, "n_logged": 2, "debug": True})
    assert not ok and len(why) == 5          # thêm: không có ctx_check


def test_check_prompt_lengths():
    c = {**cfg(), "llm": {**LLM_CFG, "num_ctx": 1000, "max_tokens": 600}}   # ngân sách 1000 − 600 − 64 = 336
    pipe = RAGPipeline(c, FakeLLM(), FakeRetriever(RANKING))
    rows = [b for b in BENCH if b["split"] == "dev"]
    long_q = "Q2 so sánh?"
    count = lambda p: 500 if long_q in p else 100
    res = RE.check_prompt_lengths(pipe, rows, count)
    assert res["budget"] == 336 and res["max"] == 500 and res["over"] == ["v1-0002"]


# Câu trả lời thật của B2 trên dev (run B2_v1_dev_20261107-0832_r0), rút gọn
REAL_REFUSED = [
    REFUSAL + "\n\n(Tài liệu cung cấp thông tin về tỷ lệ trả tiền cho một số thương tật cụ thể như mất xương hàm, "
              "lưỡi, nhưng không có thông tin về thương tật liên quan đến việc cắt bỏ vú.) [BVP_QT_PL1_TB1]",   # v1-0020
    REFUSAL,                                                                                                    # v1-0038
    REFUSAL + "\n\n(Tuy nhiên, thông qua phân tích các tài liệu, chúng ta có thể thấy rằng cả hai sản phẩm đều coi "
              "các sự kiện như ngộ độc thức ăn ... là tai nạn.) [SPMAU_QT_C1_M2_K1]",                          # v1-0060
    "Xin lỗi, tài liệu  KHÔNG có thông tin để trả lời câu hỏi này",
]
REAL_HEDGED = [
    "Độ tuổi tối đa để tham gia lần đầu của Bảo hiểm 37 bệnh hiểm nghèo (CI37) là 60 tuổi, trong khi Bảo Việt "
    "Intercare là 69 tuổi. Đối với tái tục, CI37 chỉ được tái tục cho đến khi NĐBH tròn 65 tuổi.\n\n"
    "[" + REFUSAL + "] [C37_QT_C4_M1][ITC_QT_C4_M1_P1]",                                                       # v1-0053
    "Khái niệm 'Tình trạng nguy kịch' có sự khác biệt nhỏ:\n\n- Bảo Việt An Gia: Cần điều trị khẩn cấp để tránh "
    "tử vong [BVP_QT_C1_M1_K49].\n\n- Bảo hiểm Du lịch Flexi: Cần điều trị khẩn cấp để tránh đe dọa đến tính mạng "
    "[FLX_QT_C1_M1_K34].\n\n" + REFUSAL,                                                                         # v1-0064
]


def test_refusal_vs_hedged_real_answers():
    from src.pipeline import is_hedged
    for a in REAL_REFUSED:
        assert is_refusal(a) and not is_hedged(a), a[:60]
    for a in REAL_HEDGED:
        assert not is_refusal(a) and is_hedged(a), a[:60]
    assert not is_refusal("Thời gian chờ là 30 ngày.") and not is_hedged("Thời gian chờ là 30 ngày.")
