"""Query processor B3 và nhánh use_filter của pipeline (không cần GPU, Qdrant).
Chạy: PYTHONPATH=. python -m pytest -q tests/test_query_processor.py"""
import json

from src.pipeline import RAGPipeline
from src.retrieve.query_processor import QueryProcessor, interleave, load_product_terms
from tests.test_eval_harness import FakeLLM, cfg

TERMS = {"BVP": ["bảo việt an gia", "an gia"], "BTB": ["bảo việt tâm bình", "tâm bình"],
         "C37": ["bảo hiểm 37 bệnh hiểm nghèo (ci37)", "ci37", "37 bệnh hiểm nghèo"], "FLX": ["flexi"]}


def test_detect_products_order_and_folding():
    qp = QueryProcessor(TERMS)
    assert qp.detect_products("Thời gian chờ của Bảo Việt An Gia?")[0] == ["BVP"]
    assert qp.detect_products("So sánh CI37 với Bảo Việt Tâm Bình")[0] == ["C37", "BTB"]
    assert qp.detect_products("bao viet an gia co bao lanh vien phi khong")[0] == ["BVP"]
    assert qp.detect_products("biểu phí du lịch quốc tế Flexi")[0] == ["FLX"]
    # Ranh giới từ: "an giang" không phải An Gia; câu có dấu không so trên bản bỏ dấu
    assert qp.detect_products("Tôi ở An Giang")[0] == []
    assert qp.detect_products("Bảo hiểm sức khỏe nói chung")[0] == []


def test_plan_filters_and_split():
    qp = QueryProcessor(TERMS)
    p = qp.plan("An Gia thời gian chờ?")
    assert p["subqueries"] == [{"query": "An Gia thời gian chờ?", "filters": {"product_code": ["BVP"]}}]
    p = qp.plan("An Gia khác Tâm Bình thế nào?")
    assert p["split"] and [s["filters"] for s in p["subqueries"]] == [{"product_code": ["BVP"]}, {"product_code": ["BTB"]}]
    assert QueryProcessor(TERMS, split_compare=False).plan("An Gia khác Tâm Bình?")["subqueries"][0]["filters"] == \
        {"product_code": ["BVP", "BTB"]}
    assert qp.plan("Câu chung chung")["subqueries"][0]["filters"] is None


def test_abbreviation_expansion():
    qp = QueryProcessor(TERMS, {"HĐBH": "Hợp đồng bảo hiểm"})
    q, used = qp.expand("Hủy HĐBH An Gia thế nào?")
    assert q == "Hủy HĐBH (Hợp đồng bảo hiểm) An Gia thế nào?" and used == ["HĐBH"]
    assert qp.expand("Hợp đồng bảo hiểm (HĐBH) là gì?")[1] == []


def test_interleave():
    a = [{"chunk_id": x, "rank": i} for i, x in enumerate(["A1", "A2", "S"], 1)]
    b = [{"chunk_id": x, "rank": i} for i, x in enumerate(["B1", "S", "B2"], 1)]
    out = interleave([a, b], 4)
    assert [h["chunk_id"] for h in out] == ["A1", "B1", "A2", "S"] and [h["rank"] for h in out] == [1, 2, 3, 4]


def test_load_terms_from_files(tmp_path):
    cat = tmp_path / "catalog.json"
    cat.write_text(json.dumps({"products": [{"product_code": "C37", "product_name": "Bảo hiểm 37 bệnh hiểm nghèo (CI37)"}]},
                              ensure_ascii=False), encoding="utf-8")
    al = tmp_path / "aliases.csv"
    al.write_text("product_code,alias,note\nC37,CI 37,\n", encoding="utf-8")
    t = load_product_terms(cat, al)["C37"]
    assert t == ["bảo hiểm 37 bệnh hiểm nghèo (ci37)", "bảo hiểm 37 bệnh hiểm nghèo", "ci 37"]


def test_real_catalog_detects_all_benchmark_products():
    """Benchmark v1: mọi câu answerable nhận đúng tập sản phẩm (câu hỏi nêu tên sản phẩm theo schema)."""
    qp = QueryProcessor.from_files()
    rows = [json.loads(l) for l in open("benchmark/benchmark_v1.jsonl", encoding="utf-8")]
    bad = [r["qid"] for r in rows if r["answerable"] and set(qp.detect_products(r["question"])[0]) != set(r["products"])]
    assert bad == []


class FilterRetriever:
    """Mỗi sản phẩm 3 chunk; lọc theo product_code."""
    def __init__(self):
        self.calls = []
        self.chunks = [f"{p}_S{i}" for p in ("BVP", "BTB") for i in (1, 2, 3)]

    def search(self, query, filters=None, top_k=None, mode=None):
        self.calls.append(filters)
        ids = [c for c in self.chunks if not filters or c.split("_")[0] in filters["product_code"]]
        return [{"chunk_id": c, "score": 1 / r, "rank": r, "payload": {"chunk_id": c, "text": c}}
                for r, c in enumerate(ids, 1)][:top_k]


def test_pipeline_use_filter_compare_and_fallback():
    c = cfg("B3", mode="hybrid")
    c["retrieval"]["use_filter"], c["context_n"] = True, 5
    r = FilterRetriever()
    pipe = RAGPipeline(c, FakeLLM(), r, qp=QueryProcessor(TERMS))
    out = pipe.answer("An Gia khác Tâm Bình?")
    assert out["contexts"] == ["BVP_S1", "BTB_S1", "BVP_S2", "BTB_S2", "BVP_S3"]
    assert out["qp"]["products"] == ["BVP", "BTB"] and out["qp"]["fallback"] is False
    assert out["qp"]["filters"] == [{"product_code": ["BVP"]}, {"product_code": ["BTB"]}]
    # 1 sản phẩm chỉ có 3 chunk < context_n = 5 → bù bằng kết quả không lọc
    out = pipe.answer("An Gia thời gian chờ?")
    assert out["qp"]["fallback"] is True and out["contexts"][:3] == ["BVP_S1", "BVP_S2", "BVP_S3"]
    assert [h["rank"] for h in out["retrieved"]] == list(range(1, 7))
    # Không nhận diện được → không lọc, không có fallback
    out = pipe.answer("Câu chung chung")
    assert r.calls[-1] is None and out["qp"]["products"] == []


def test_per_question_flags_and_qp_summary():
    import eval.per_question as PQ
    from eval.metrics import qp_summary
    bench = {"q1": {"qid": "q1", "group": "lookup", "difficulty": "easy", "products": ["BVP"], "evidence_ids": ["E1"],
                    "question": "Q1", "answer": "30 ngày", "answerable": True},
             "q2": {"qid": "q2", "group": "out_of_scope", "difficulty": "easy", "products": [], "evidence_ids": [],
                    "question": "Q2", "answer": "x", "answerable": False}}
    def log(q, ids, ans, qp=None):
        d = {"qid": q, "retrieved": [{"chunk_id": c, "rank": r} for r, c in enumerate(ids, 1)], "answer": ans}
        return d | ({"qp": qp} if qp else {})
    m2 = {"config": "configs/B2.yaml", "retrieval_mode": "dense", "chunking": "structure"}
    m3 = {"config": "configs/B3.yaml", "retrieval_mode": "hybrid", "chunking": "structure"}
    qp = {"products": ["BVP"], "fallback": False}
    runs = [(m2, [log("q1", ["X"], "Khoảng 60 ngày."), log("q2", [], "Có.")]),
            (m3, [log("q1", ["X", "E1"], "60 ngày", qp), log("q2", [], "Có.", {"products": []})])]
    rows = {r["qid"]: r for r in PQ.build(runs, bench, None, 0.3)}
    assert rows["q1"]["rank_B2"] is None and rows["q1"]["rank_B3"] == 2 and rows["q1"]["qp_B3"] == "BVP"
    assert rows["q1"]["suspect"] == "num0_all" and rows["q2"]["suspect"] == "oos_answered"
    s = qp_summary(runs[1][1], bench)
    assert s == {"products_exact": 1.0, "filtered": 0.5, "split": 0, "fallback": 0}
