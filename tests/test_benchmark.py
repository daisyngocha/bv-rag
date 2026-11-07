"""Benchmark: kiểm tra schema và vòng review → build. Chạy: PYTHONPATH=. python -m pytest -q tests/test_benchmark.py"""
import csv, json

import eval.bench_draft as bd
from eval.benchmark import validate

REFUSAL = "Tài liệu sản phẩm hiện có không có thông tin để trả lời câu hỏi này."
CHUNKS = {
    "BVP_QT_C2_M1_B": {"chunk_id": "BVP_QT_C2_M1_B", "product_code": "BVP", "ocr": False,
                       "text": "[An Gia | Quy tắc | B]\nThời gian chờ 30 ngày đối với bệnh thông thường."},
    "ITC_QT_C4_M10_K1": {"chunk_id": "ITC_QT_C4_M10_K1", "product_code": "ITC", "ocr": False,
                         "text": "[Intercare | Quy tắc | 10]\nĐiều trị nội trú: 30 ngày đối với bệnh thông thường."},
}


def rec(**kw):
    r = {"qid": "v1-0001", "question": "Thời gian chờ bệnh thông thường của An Gia?", "answer": "30 ngày.",
         "evidence_ids": ["BVP_QT_C2_M1_B"], "products": ["BVP"], "group": "lookup", "difficulty": "easy",
         "answerable": True, "split": "dev", "created_by": "llm_draft+human", "version": "v1"}
    r.update(kw)
    return r


def test_validate_ok_and_number_check():
    assert validate([rec()], CHUNKS, REFUSAL) == ([], [])
    errors, _ = validate([rec(answer="90 ngày.")], CHUNKS, REFUSAL)
    assert any("['90']" in e for e in errors)
    _, warnings = validate([rec(answer="90 ngày.", group="scenario")], CHUNKS, REFUSAL)
    assert warnings                                       # scenario: chỉ cảnh báo


def test_validate_out_of_scope_and_compare():
    oos = rec(qid="v1-0002", question="Bảo Việt có bảo hiểm xe máy không?", group="out_of_scope",
              answerable=False, evidence_ids=[], products=[], answer=REFUSAL)
    assert validate([oos], CHUNKS, REFUSAL)[0] == []
    errors, _ = validate([dict(oos, answer="Không có.")], CHUNKS, REFUSAL)
    assert errors
    cmp_one = rec(qid="v1-0003", group="compare", question="So sánh?")
    assert any("≥ 2 sản phẩm" in e for e in validate([cmp_one], CHUNKS, REFUSAL)[0])
    cmp_ok = rec(qid="v1-0003", group="compare", question="So sánh?", products=["BVP", "ITC"],
                 evidence_ids=["BVP_QT_C2_M1_B", "ITC_QT_C4_M10_K1"], answer="Cả hai đều 30 ngày.")
    assert validate([cmp_ok], CHUNKS, REFUSAL)[0] == []


def test_review_then_build_keeps_qids(tmp_path, monkeypatch):
    drafts = tmp_path / "drafts"
    drafts.mkdir()
    proc = tmp_path / "v1"
    proc.mkdir()
    (proc / "chunks.jsonl").write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in CHUNKS.values()), encoding="utf-8")
    d = [{"task_id": "w3-001", "group": "lookup", "evidence_ids": ["BVP_QT_C2_M1_B"], "products": ["BVP"],
          "output": {"question": "An Gia chờ bao lâu với bệnh thông thường?", "answer": "30 ngày.", "difficulty": "easy"}},
         {"task_id": "w3-002", "group": "out_of_scope", "evidence_ids": [], "products": [], "topic": "legal",
          "output": {"question": "Luật cho phép thời gian chờ tối đa bao lâu?", "reason": "luật", "difficulty": "easy"}}]
    (drafts / "w3_drafts.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in d), encoding="utf-8")
    monkeypatch.setattr(bd, "DRAFTS", drafts)
    path = bd.review("w3", proc)
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    assert [r["split"] for r in rows] == ["dev", "dev"] and rows[1]["answer"] == REFUSAL
    for r in rows:
        r["decision"] = "keep"
    rows[0]["decision"], rows[0]["edited_answer"] = "edit", "30 ngày kể từ ngày bắt đầu hiệu lực."
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=bd.REVIEW_COLS)
        w.writeheader()
        w.writerows(rows)
    out = tmp_path / "benchmark_v1.jsonl"
    bd.build(proc, out, final=False)
    got = [json.loads(l) for l in open(out, encoding="utf-8")]
    assert [g["qid"] for g in got] == ["v1-0001", "v1-0002"]
    assert got[0]["answer"].startswith("30 ngày kể từ") and got[1]["answerable"] is False
    bd.build(proc, out, final=False)                       # build lại giữ nguyên qid
    assert [json.loads(l)["qid"] for l in open(out, encoding="utf-8")] == ["v1-0001", "v1-0002"]
