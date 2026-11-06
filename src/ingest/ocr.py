"""OCR một trang PDF bằng tesseract CLI (ngoài Docling): dùng cho probe chọn cấu hình và kiểm tra nhanh.
Thân văn bản trong kho vẫn parse bằng Docling + TesseractCliOcrOptions (src/ingest/parser.py).
Chỉ dùng stdlib + poppler/tesseract để dùng lại được cho ĐA2/ĐATN (baseline OCR chứng từ)."""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

WORD = re.compile(r"[^\W\d_]+")


def ocr_lines(pdf: str, page: int, dpi: int = 216, lang: str = "vie", psm: int | None = None,
              tessdata: str | None = None, threads: int | None = 1) -> list[str]:
    """Dòng chữ OCR của trang `page` (đánh số từ 1). dpi 216 = scale 3.0 của Docling.
    threads=1: tắt OpenMP của tesseract để chạy song song nhiều trang không tranh CPU."""
    env = dict(os.environ, OMP_THREAD_LIMIT=str(threads)) if threads else None
    with tempfile.TemporaryDirectory() as d:
        png = Path(d) / "p"
        subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(page), "-l", str(page), "-png", "-singlefile",
                        pdf, str(png)], check=True, capture_output=True)
        cmd = ["tesseract", f"{png}.png", "-", "-l", lang]
        if psm is not None:
            cmd += ["--psm", str(psm)]
        if tessdata:
            cmd += ["--tessdata-dir", str(tessdata)]
        r = subprocess.run(cmd, capture_output=True, text=True, env=env)
        if r.returncode:
            raise RuntimeError(f"tesseract lỗi trang {page}: {r.stderr.strip()[-300:]}")
        return r.stdout.splitlines()


def oov_rate(text: str, vocab: set[str]) -> float:
    """Tỷ lệ từ không có trong từ vựng tham chiếu (chỉ bắt lỗi ra từ không tồn tại; không bắt chi → chỉ)."""
    ws = [w.lower() for w in WORD.findall(text)]
    return sum(w not in vocab for w in ws) / max(len(ws), 1)
