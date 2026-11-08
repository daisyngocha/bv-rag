"""Demo tuần 7: DemoService gắn nguồn cho trích dẫn, FastAPI /ask, kịch bản demo chỉ dùng câu dev.
Không cần GPU (pipeline giả từ test_b4). Chạy: PYTHONPATH=. python -m pytest -q tests/test_demo.py"""
import json

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from app.api import create_app, demo_questions  # noqa: E402
from app.service import DemoService, load_catalog  # noqa: E402
from src.pipeline import RAGPipeline  # noqa: E402
from tests.test_b4 import LLM, QP, Rer, Retr, cfg  # noqa: E402

CATALOG = {"BVP": {"name": "Bảo Việt An Gia", "effective_date": "2025-01-01", "url": "https://x/bvp",
                   "docs": {"products/BVP/qt.pdf": "https://x/bvp-qt"}},
           "BTB": {"name": "Bảo Việt Tâm Bình", "effective_date": None, "url": None, "docs": {}}}


class RetrMeta(Retr):
    """Như Retr của test_b4 nhưng payload có header và metadata giống chunk thật."""
    def search(self, *a, **k):
        out = super().search(*a, **k)
        for h in out:
            code = h["chunk_id"].split("_")[0]
            h["payload"] |= {"product_code": code, "doc_type": "quy_tac", "section_path": "Điều 5", "page": 3,
                             "source_file": f"products/{code}/qt.pdf", "text": f"[{code} | Quy tắc]\n{h['payload']['text']}"}
        return out


def service(min_score=None, text="Thời gian chờ 30 ngày [1]. Bảng [2], [7]."):
    pipe = RAGPipeline(cfg(min_score=min_score, use_filter=True), LLM(text), RetrMeta(), qp=QP(), reranker=Rer())
    return DemoService(pipe, CATALOG, "B4")


def test_ask_sources_and_citations():
    out = service().ask("  thời gian chờ   BVP ")
    assert out["question"] == "thời gian chờ BVP"
    assert not out["refused"] and out["products_detected"] == ["BVP"]
    assert [s["chunk_id"] for s in out["sources"]] == ["BVP_A", "BVP_B"]
    s1 = out["sources"][0]
    assert s1["cited"] and s1["n"] == 1 and s1["product_name"] == "Bảo Việt An Gia"
    assert s1["doc_label"] == "Quy tắc" and s1["page"] == 3 and s1["url"] == "https://x/bvp-qt"
    assert s1["text"] == "thời gian chờ 30 ngày"          # bỏ dòng header ngữ cảnh
    assert out["citations"] == [{"n": 1, "chunk_id": "BVP_A"}, {"n": 2, "chunk_id": "BVP_B"}]
    assert out["citations_invalid"] == ["[7]"]


def test_ask_gated_refusal():
    out = service(min_score=0.5).ask("câu ngoài phạm vi")
    assert out["refused"] and out["gated"] and out["citations"] == []


def test_ask_empty():
    with pytest.raises(ValueError):
        service().ask("   ")


def test_api_ask_and_log(tmp_path, monkeypatch):
    log = tmp_path / "demo.jsonl"
    monkeypatch.setenv("DEMO_LOG", str(log))
    with TestClient(create_app(service())) as c:
        assert c.get("/health").json() == {"ok": True, "config": "B4"}
        r = c.post("/ask", json={"question": "thời gian chờ BVP"})
        assert r.status_code == 200 and r.json()["sources"][0]["chunk_id"] == "BVP_A"
        assert c.post("/ask", json={"question": "a"}).status_code == 422
        assert {p["product_code"] for p in c.get("/products").json()} == {"BVP", "BTB"}
    assert json.loads(log.read_text(encoding="utf-8"))["question"] == "thời gian chờ BVP"


def test_demo_script_dev_only():
    qs = demo_questions()
    assert len(qs) >= 5 and {q["group"] for q in qs} >= {"lookup", "table", "scenario", "compare", "out_of_scope"}


def test_catalog_real():
    cat = load_catalog()
    assert set(cat) == {"BTB", "BVP", "C37", "FLX", "ITC"} and all(v["url"] for v in cat.values())
