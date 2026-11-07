"""Glossary 2 cấp. Chạy: PYTHONPATH=. python -m pytest -q tests/test_glossary.py"""
from src.ingest.glossary import general_entries, lookup, product_entries, split_definition


def test_split_definition_forms():
    assert split_definition("12. Bệnh có sẵn: là tình trạng bệnh") == ("Bệnh có sẵn", "tình trạng bệnh")
    assert split_definition("3. “Tai nạn” là sự kiện bất ngờ") == ("Tai nạn", "sự kiện bất ngờ")
    assert split_definition("1. Bệnh viện\nlà cơ sở khám chữa bệnh") == ("Bệnh viện", "cơ sở khám chữa bệnh")
    assert split_definition("Không có dấu phân tách nào ở đây cả") is None


def chunk(cid, text, P="BVP", path="Chương I > I. Định nghĩa"):
    return {"chunk_id": cid, "text": f"[An Gia | Quy tắc | {path.split(' > ')[-1]}]\n{text}",
            "effective_date": "2025-06-27", "product_code": P, "section_path": path}


def test_product_entries_merge_parts_and_count(tmp_path):
    (tmp_path / "BVP.yaml").write_text("product_code: BVP\nchecks:\n  definitions: {prefix: BVP_QT_C1_M1_K, count: 2}\n",
                                       encoding="utf-8")
    chunks = [chunk("BVP_QT_C1_M1", "Trong Quy tắc này các từ ngữ được hiểu như sau"),
              chunk("BVP_QT_C1_M1_K2_P2", "b) phần sau"), chunk("BVP_QT_C1_M1_K1", "1. Bệnh viện: là cơ sở y tế"),
              chunk("BVP_QT_C1_M1_K2_P1", "2. Phẫu thuật: là a) phần đầu"), chunk("BVP_QT_C2_M1", "1. Khác: x")]
    entries, errors = product_entries(chunks, tmp_path, {})
    assert errors == []
    assert [(e["term"], e["source"]) for e in entries] == [("Bệnh viện", "BVP_QT_C1_M1_K1"), ("Phẫu thuật", "BVP_QT_C1_M1_K2_P1")]
    assert entries[1]["definition"] == "a) phần đầu b) phần sau"
    entries, errors = product_entries([chunks[2]], tmp_path, {})
    assert errors and "thấy 1" in errors[0]


def test_general_keep_and_effective_date():
    rows = [{"term": "Phí bảo hiểm", "definition": "khoản tiền", "keep": "1",
             "source": "Luật Kinh doanh bảo hiểm (VBHN 31/VBHN-VPQH), Điều 4, khoản 28", "amended_by": ""},
            {"term": "Đồng bảo hiểm", "definition": "x", "keep": "",
             "source": "Luật Kinh doanh bảo hiểm (VBHN 31/VBHN-VPQH), Điều 4, khoản 29", "amended_by": ""}]
    sources = [{"file": "legal/vbhn_31_2026_luat_kdbh.pdf", "effective_date": "2026-01-01"}]
    entries, errors = general_entries(rows, sources)
    assert errors == [] and len(entries) == 1 and entries[0]["effective_date"] == "2026-01-01"


def test_lookup_prefers_product_scope():
    es = [{"term": "Thời gian chờ", "aliases": ["TGC"], "scope": "general"},
          {"term": "Thời gian chờ", "aliases": [], "scope": "BVP"}]
    assert [e["scope"] for e in lookup(es, "thời gian chờ", ["BVP"])] == ["BVP"]
    assert [e["scope"] for e in lookup(es, "TGC", ["ITC"])] == ["general"]


def test_term_from_section_path(tmp_path):
    (tmp_path / "BTB.yaml").write_text("product_code: BTB\nchecks:\n  definitions: {prefix: BTB_QT_C1_M, count: 3}\n",
                                       encoding="utf-8")
    chunks = [chunk("BTB_QT_C1_M1", "Là một bác sĩ được cấp giấy phép: gồm a) b)", "BTB", "CHƯƠNG I: ĐỊNH NGHĨA > 1. Bác sĩ"),
              chunk("BTB_QT_C1_M2", "`.\n.&\nThời hạn bảo hiểm được tính từ", "BTB", "CHƯƠNG I: ĐỊNH NGHĨA > 2. Thời hạn bảo hiểm:"),
              chunk("BTB_QT_C1_M3", "bị cản trở", "BTB", "CHƯƠNG I: ĐỊNH NGHĨA > 3. “Thương tật”: là các tổn thương")]
    entries, errors = product_entries(chunks, tmp_path, {})
    assert errors == []
    assert [(e["term"], e["definition"]) for e in entries] == [
        ("Bác sĩ", "một bác sĩ được cấp giấy phép: gồm a) b)"),
        ("Thời hạn bảo hiểm", "Thời hạn bảo hiểm được tính từ"),
        ("Thương tật", "các tổn thương bị cản trở")]
