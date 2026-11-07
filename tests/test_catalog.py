"""Product Catalog. Chạy: PYTHONPATH=. python -m pytest -q tests/test_catalog.py"""
import json

import src.ingest.catalog as cat


def setup(tmp_path, monkeypatch, rows):
    proc = tmp_path / "v1"
    proc.mkdir()
    chunks = [{"chunk_id": "BVP_QT_C4_M1", "product_code": "BVP", "doc_type": "quy_tac", "page": 20,
               "text": "[An Gia | Quy tắc | Đối tượng]\nNgười từ 15 ngày tuổi đến 65 tuổi, STBH 1.000.000.000 đồng, thời hạn 1 năm, chương trình ĐỒNG"}]
    (proc / "chunks.jsonl").write_text("\n".join(json.dumps(c, ensure_ascii=False) for c in chunks), encoding="utf-8")
    csv_path = tmp_path / "catalog.csv"
    csv_path.write_text("product_code,field,value,source,note\n" + "\n".join(rows) + "\n", encoding="utf-8")
    monkeypatch.setattr(cat, "MANUAL_CSV", csv_path)
    return proc


def full_rows(age_max="65 tuổi"):
    base = {"product_type": "Sức khỏe", "insured": "Cá nhân", "age_min": "15 ngày tuổi", "age_max": age_max,
            "territory": "Việt Nam", "term": "1 năm", "programs": "Đồng"}
    return [f"BVP,{f},{v},BVP_QT_C4_M1," for f, v in base.items()]


def test_build_ok_and_auto_fields(tmp_path, monkeypatch):
    proc = setup(tmp_path, monkeypatch, full_rows() + ["BVP,sum_insured,1.000.000.000 đồng,BVP_QT_C4_M1,"])
    catalog, errors = cat.build(proc)
    assert errors == []
    p = catalog["products"][0]
    assert p["product_name"] == "Bảo Việt An Gia" and p["decision"] == "6029/QĐ-BHBV"
    assert p["fields"]["age_max"] == {"value": "65 tuổi", "source": "BVP_QT_C4_M1"}
    assert p["fields"]["programs"] == [{"value": "Đồng", "source": "BVP_QT_C4_M1"}]
    assert any(d["doc_type"] == "quy_tac" for d in p["documents"])


def test_number_not_in_source_fails(tmp_path, monkeypatch):
    proc = setup(tmp_path, monkeypatch, full_rows(age_max="70 tuổi"))
    _, errors = cat.build(proc)
    assert any("['70']" in e for e in errors)


def test_missing_required_and_bad_source(tmp_path, monkeypatch):
    rows = [r for r in full_rows() if ",term," not in r] + ["BVP,programs,Đồng,BVP_QT_X,"]
    proc = setup(tmp_path, monkeypatch, rows)
    _, errors = cat.build(proc)
    assert any("BVP_QT_X" in e for e in errors) and any("thiếu trường term" in e for e in errors)


def test_program_name_must_be_verbatim(tmp_path, monkeypatch):
    proc = setup(tmp_path, monkeypatch, [r for r in full_rows() if ",programs," not in r] + ["BVP,programs,Kim Cương,BVP_QT_C4_M1,"])
    _, errors = cat.build(proc)
    assert any("không có nguyên văn" in e for e in errors)
