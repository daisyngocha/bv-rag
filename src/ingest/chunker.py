# src/ingest/chunker.py
import re
import unicodedata

FIX_CHARS = str.maketrans({"Ð": "Đ", "ð": "đ"})   # BVP: font WinAnsi map sai Đ/đ thành Eth

def clean_text(s: str) -> str:
    """Chuẩn hóa text sau khi parse, trước khi nhận diện tiêu đề và tạo chunk."""
    return unicodedata.normalize("NFC", s).translate(FIX_CHARS)

ROMAN = r"(?=[IVX])X{0,3}(?:IX|IV|V?I{0,3})"
PAT = {
    "chuong": re.compile(rf"^CHƯƠNG\s+({ROMAN})\b\s*[-:]?\s*(.*)$"),
    "phuluc": re.compile(r"^PHỤ LỤC\s+(\d+)\s*[-:.]?\s*(.*)$"),
    "muc":    re.compile(rf"^({ROMAN})\.\s+(\S.*)$"),
    "bosung": re.compile(r"^Quyền lợi bổ sung\s+(\d+)\s*:\s*(.+)$"),
    "khoan":  re.compile(r"^(\d+)\.\s+(\S.*)$"),
}
TOC_LINE = re.compile(r"\.{5,}\s*\d*\s*$")
