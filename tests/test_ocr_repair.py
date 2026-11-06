"""Sửa cấu trúc sau OCR (BTB build 1): tách tiêu đề gộp, sửa số mục, bảng nhập tay. PYTHONPATH=. python -m pytest -q tests/"""
import pytest

from src.ingest.chunker import (Rec, apply_table_overrides, build_units, compile_part_heads, repair_numbering,
                                split_merged_heads)

HEADS = compile_part_heads({"A": r"^QUY\S+ LỢI B\S+ HI\S+ CHÍNH", "B": r"^QUY\S+ LỢI B\S+ HI\S+ B\S+ SUNG"})


def h(t, p=4):
    return Rec("header", t, p)


def test_split_merged_chapter_and_muc():
    recs = [h("CHƯƠNG V: THỦ TỤC YÊU CẦU BỒI THƯỜNG VÀ BẢO LÃNH VIỆN PHÍ I. HÒ SƠ BÒI THƯỜNG", 36), Rec("text", "1. Giấy", 36)]
    log = split_merged_heads(recs)
    assert [r.text for r in recs[:2]] == ["CHƯƠNG V: THỦ TỤC YÊU CẦU BỒI THƯỜNG VÀ BẢO LÃNH VIỆN PHÍ", "I. HÒ SƠ BÒI THƯỜNG"]
    assert len(log) == 1 and len(recs) == 3


def test_split_leaves_normal_chapter():
    recs = [h("CHƯƠNG II: PHẠM VI BẢO HIỂM"), h("CHƯƠNG IV: QUY ĐỊNH CHUNG")]
    assert split_merged_heads(recs) == [] and len(recs) == 2


def test_repair_dots_and_garbled_numbers():
    recs = [h("CHƯƠNG I: ĐỊNH NGHĨA"), h("1. Bác sĩ"), h("2. Bảng quyền lợi"), h("3. Bên mua"), h("4. Bệnh/Ốm đau"), h("5... Bệnh bẩm sinh/dị tật bẩm sinh"),
            Rec("text", "Là bất kỳ bệnh", 5), h("6. Bệnh có sẵn", 5), h("7. Bệnh di truyền", 5),
            h("§. Bệnh đặc biệt", 5), Rec("list", "1. Ung thư", 5), Rec("list", "2. Bệnh tim", 5), h("9. Bệnh nghề nghiệp", 6),
            h("CHƯƠNG III: LOẠI TRỪ", 20), h("§. không sửa ngoài chương đánh số", 20)]
    rep = repair_numbering(recs, frozenset({1}), HEADS)
    texts = [r.text for r in recs]
    assert "5. Bệnh bẩm sinh/dị tật bẩm sinh" in texts and "8. Bệnh đặc biệt" in texts
    assert "§. không sửa ngoài chương đánh số" in texts
    assert len(rep["numbering_fixed"]) == 2 and rep["numbering_gaps"] == []


def test_repair_part_restart_and_gap_report():
    t = lambda x, p: Rec("text", x, p)
    recs = [h("CHƯƠNG II: PHẠM VI BẢO HIỂM", 15), h("QUYỀN LỢI BẢO HIỂM CHÍNH - NỘI TRÚ", 15), h("1. Nằm viện", 15),
            t("a", 15), h("2. Phẫu thuật", 15), t("b", 15), h("QUYỀN LỢI BẢO HIỂM BỎ SUNG", 16),
            h("L. Tử vong/thương tật vĩnh viễn", 16), t("c", 16), h("1.1. Bảo hiểm tai nạn cá nhân", 17),
            h("2. Điều trị ngoại trú", 17), t("d", 17), h("3. Trợ cấp", 18), t("e", 18),
            h("CHƯƠNG IV: QUY ĐỊNH CHUNG", 25), h("1. Phạm vi", 25), h("4. Ký kết", 28)]
    rep = repair_numbering(recs, frozenset({2, 4}), HEADS)
    assert recs[7].text == "1. Tử vong/thương tật vĩnh viễn" and recs[9].text.startswith("1.1.")
    assert rep["numbering_gaps"] == ["CHƯƠNG IV: QUY ĐỊNH CHUNG: 1 → 4, thiếu 2 số, 0 ứng viên"]
    ids = ["_".join(u.ids) for u in build_units(recs[:14], "legal", frozenset({2}), None, HEADS)]
    assert ids[-3:] == ["C2_B_M1", "C2_B_M2", "C2_B_M3"]


def test_table_override(tmp_path):
    f = tmp_path / "pl3.csv"
    f.write_text("# ghi chú\npage,STT,QUYỀN LỢI,TỈ LỆ\n41,1,Hỏng toàn bộ chức năng nhai và nói,100%\n"
                 "41,,CHI TRÊN,\n43,74,Cắt bỏ đoạn mỗi xương sườn,08%\n", encoding="utf-8")
    recs = [Rec("text", "PHỤ LỤC III", 41), Rec("table", page=41, rows=[["", "Hỏng", ""]], row_pages=[41]),
            Rec("table", page=43, rows=[["61", "Mất", "1%"]], row_pages=[43]), Rec("text", "Nguyên tắc", 45),
            Rec("table", page=23, rows=[["Bệnh", "x"]], row_pages=[23])]
    out, rep, pages = apply_table_overrides(recs, [{"pages": [41, 45], "csv": str(f)}])
    t = [r for r in out if r.kind == "table"]
    assert len(t) == 2 and t[0].rows[0] == ["STT", "QUYỀN LỢI", "TỈ LỆ"] and t[0].row_pages == [41, 41, 41, 43]
    assert t[1].page == 23 and rep[0]["replaced_tables"] == 2 and rep[0]["rows"] == 3 and 43 in pages
    with pytest.raises(ValueError):
        apply_table_overrides(recs, [{"pages": [50, 50], "csv": str(f)}])
