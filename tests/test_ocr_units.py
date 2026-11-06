"""text_fixes, part_heads, manual_units cho BTB (file OCR). Chạy: PYTHONPATH=. python -m pytest -q tests/"""
import pytest

from src.ingest.chunker import Rec, apply_text_fixes, build_units, compile_part_heads


def test_text_fixes_ocr_and_excel_numbers():
    fixes = [[r"\b([Cc])hỉ (phí|trả)\b", r"\1hi \2"], [r"(?<=\d),(?=\d{3}\b)", "."]]
    recs = [Rec("text", "Công ty chỉ chỉ trả Chỉ phí thực tế", 5),
            Rec("table", page=5, rows=[["Đến 6 tuổi", "60,000,000"], ["Tỷ lệ", "0,58%"]])]
    recs, n = apply_text_fixes(recs, fixes)
    assert recs[0].text == "Công ty chỉ chi trả Chi phí thực tế"
    assert recs[1].rows == [["Đến 6 tuổi", "60.000.000"], ["Tỷ lệ", "0,58%"]]
    assert n == 4


def test_no_fixes_is_noop():
    recs = [Rec("text", "chỉ phí", 1)]
    assert apply_text_fixes(recs, None) == (recs, 0) and recs[0].text == "chỉ phí"


def btb_chuong2():
    return [Rec("header", "CHƯƠNG II: PHẠM VI BẢO HIỂM", 15),
            Rec("header", "QUYỀN LỢI BẢO HIỂM CHÍNH - ĐIỀU TRỊ NỘI TRÚ DO BỆNH, TAI NẠN, THAI SẢN", 15),
            Rec("header", "1. Nằm viện do bệnh, tai nạn, thai sản", 15), Rec("text", "a", 15),
            Rec("header", "2. Phẫu thuật do bệnh, tai nạn, thai sản", 15), Rec("text", "b", 15),
            Rec("header", "QUYỀN LỢI BẢO HIỂM BỔ SUNG", 16),
            Rec("header", "1. Tử vong/thương tật vĩnh viễn do mọi nguyên nhân", 16), Rec("text", "c", 16),
            Rec("header", "2. Điều trị ngoại trú do bệnh, tai nạn, biến chứng thai sản, điều trị răng", 17),
            Rec("text", "d", 17),
            Rec("header", "CHƯƠNG III: CÁC ĐIỂM LOẠI TRỪ CHUNG", 20), Rec("text", "e", 20)]


def test_part_heads_restart_numbering():
    heads = compile_part_heads({"A": "^QUYỀN LỢI BẢO HIỂM CHÍNH", "B": "^QUYỀN LỢI BẢO HIỂM BỔ SUNG"})
    ids = ["_".join(u.ids) for u in build_units(btb_chuong2(), "legal", frozenset({2}), None, heads)]
    assert ids == ["C2_A_M1", "C2_A_M2", "C2_B_M1", "C2_B_M2", "C3"]


def test_without_part_heads_bosung_is_nested():
    ids = ["_".join(u.ids) for u in build_units(btb_chuong2(), "legal", frozenset({2}))]
    assert ids == ["C2", "C2_M1", "C2_M2", "C3"]


def test_manual_chunks_ids_continue():
    pytest.importorskip("yaml")
    from scripts.build_kb import manual_chunks
    pc = {"product_code": "BTB", "product_name": "Bảo Việt Tâm Bình", "company": "BHBV", "line": "phi_nhan_tho",
          "effective_date": "2025-06-27",
          "manual_units": [{"doc_type": "bang_phi", "doc_label": "Biểu phí", "source_file": "btb_quytac.pdf",
                            "page": 47, "section_path": "Quyền lợi bổ sung 3",
                            "text": "| QL bổ sung 3 | |\n|---|---|\n| Do tai nạn | 0,58% |"}]}
    structure = [{"chunk_id": "BTB_BP_S1"}, {"chunk_id": "BTB_BP_S2_P1"}, {"chunk_id": "BTB_QT_C1_M1"}]
    fixed = [{"chunk_id": "BTB_BP_F001"}, {"chunk_id": "BTB_BP_F002"}]
    ms, mf = manual_chunks(pc, structure, fixed, lambda s: len(s.split()), 512)
    assert ms[0]["chunk_id"] == "BTB_BP_S3" and mf[0]["chunk_id"] == "BTB_BP_F003"
    assert ms[0]["manual"] and not ms[0]["ocr"] and ms[0]["is_table"] and ms[0]["page"] == 47
    assert ms[0]["text"].startswith("[Bảo Việt Tâm Bình | Biểu phí | Quyền lợi bổ sung 3]\n|")
    with pytest.raises(ValueError):
        manual_chunks({**pc, "manual_units": [{"doc_type": "bang_phi"}]}, structure, fixed, len, 512)
