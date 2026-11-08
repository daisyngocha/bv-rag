"""Che thông tin cá nhân trong câu hỏi trước khi gửi pipeline, lưu Supabase và log (UC-CHAT-11, SV-04).

Regex đơn giản, ưu tiên không che nhầm số tiền/điều khoản: chỉ che dãy số liền (hoặc nhóm số điện thoại) có đúng độ dài.
  email                     → [EMAIL]
  CCCD 12 số                → [CCCD]
  SĐT VN (0/84/+84 + 9 số)  → [SĐT]   cho phép dấu cách/chấm/gạch giữa các nhóm số
  CMND 9 số                 → [CMND]
Số tiền kiểu 1.448.000 hay 100.000.000 không bị che (nhóm 3 chữ số, không bắt đầu bằng 0/84).
"""
from __future__ import annotations

import re

PATTERNS = [
    ("[EMAIL]", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("[CCCD]", re.compile(r"(?<![\d.,])\d{12}(?![\d.,]?\d)")),
    ("[SĐT]", re.compile(r"(?<![\d.,])(?:\+84|84|0)(?:[\s.-]?\d){9}(?![\d.,]?\d)")),
    ("[CMND]", re.compile(r"(?<![\d.,])\d{9}(?![\d.,]?\d)")),
]


def mask_pii(text: str) -> tuple[str, int]:
    """Trả (văn bản đã che, số giá trị bị che)."""
    total = 0
    for token, pat in PATTERNS:
        text, n = pat.subn(token, text)
        total += n
    return text, total
