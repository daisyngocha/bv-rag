"""Mục lục khai báo trong YAML (toc:) cho file OCR. Chạy: PYTHONPATH=. python -m pytest -q tests/test_toc_cfg.py"""
import pytest

from src.ingest.chunker import Rec, apply_toc_titles, reconcile, toc_from_cfg

TOC = [["CHƯƠNG I: ĐỊNH NGHĨA", 2], ["CHƯƠNG II: PHẠM VI BẢO HIỂM", 13],
       ["CHƯƠNG III: CÁC ĐIỂM LOẠI TRỪ CHUNG", 18], ["CHƯƠNG IV: QUY ĐỊNH CHUNG", 23],
       ["PHỤ LỤC III: BẢNG TỈ LỆ TRẢ TIỀN TỬ VONG/THƯƠNG TẬT VĨNH VIỄN", 39]]


def ocr_recs():
    return [Rec("header", "CHƯƠNG I: ĐỊNH NGHĨA.", 4), Rec("text", "1. Bác sĩ", 4),
            Rec("header", "CHƯƠNG II: PHẠM VI BẢO HIỂM", 15), Rec("text", "x", 16),
            Rec("header", "CHƯƠNG II: CÁC ĐIÊỀM LOẠI TRỪ CHUNG", 20), Rec("text", "y", 20),  # OCR: III → II
            Rec("text", "z", 25),                                                            # mất CHƯƠNG IV
            Rec("header", "PHỤ LỤC II: BẢNG TỈ LỆ TRẢ TIỀN TỬ VONG/THƯƠNG TẬT VĨNH VIÊN", 41)]


def test_titles_fixed_by_text_not_number():
    toc, recs = toc_from_cfg(TOC), ocr_recs()
    rep = apply_toc_titles(recs, toc)
    assert rep["toc_titles_unmatched"] == []
    assert [r.text for r in recs if r.kind == "header"] == [t for t, _ in TOC if not t.startswith("CHƯƠNG IV")]


def test_reconcile_inserts_missing_chapter_with_offset():
    toc, recs = toc_from_cfg(TOC), ocr_recs()
    apply_toc_titles(recs, toc)
    recs, rep = reconcile(recs, toc, page_offset=2)
    assert rep["matched"] == len(TOC) and rep["inserted"] == ["CHƯƠNG IV: QUY ĐỊNH CHUNG"]
    ins = next(r for r in recs if r.synthetic)
    assert ins.page == 25 and recs[recs.index(ins) + 1].text == "z"


def test_unrelated_header_not_replaced():
    toc, recs = toc_from_cfg(TOC), [Rec("header", "CHƯƠNG V: THỦ TỤC YÊU CẦU BỒI THƯỜNG", 36)]
    rep = apply_toc_titles(recs, toc)
    assert recs[0].text.startswith("CHƯƠNG V") and len(rep["toc_titles_unmatched"]) == 1


@pytest.mark.parametrize("bad", [[["Chương 1 Định nghĩa", 2]],
                                 [["CHƯƠNG I: A", 5], ["CHƯƠNG II: B", 3]],
                                 [["CHƯƠNG I: A", "2"]]])
def test_bad_config_raises(bad):
    with pytest.raises(ValueError):
        toc_from_cfg(bad)
