"""Prompt sinh câu trả lời, chọn theo khóa `prompt` trong config (B0–B4).

Một prompt khi đã dùng cho lần chạy chính thức thì không sửa nội dung: muốn đổi thì thêm tên mới (rag_v2…),
để mọi run_id truy được về đúng một prompt. Câu từ chối giống hệt đáp án chuẩn của câu out_of_scope trong
benchmark (benchmark/draft_config.yaml, khóa refusal).
"""
from __future__ import annotations

REFUSAL = "Tài liệu sản phẩm hiện có không có thông tin để trả lời câu hỏi này."
# Cụm cốt lõi để nhận diện từ chối khi model diễn đạt lệch đôi chút (thêm/bớt "sản phẩm hiện có", dấu chấm)
REFUSAL_CORE = "không có thông tin để trả lời"

_NORAG_V1 = (
    "Bạn là trợ lý hỏi đáp về sản phẩm bảo hiểm cá nhân của Bảo Việt. "
    "Trả lời ngắn gọn, chính xác bằng tiếng Việt, giữ nguyên số liệu. "
    "Nếu không biết chắc câu trả lời, chỉ trả lời đúng một câu: \"{refusal}\"\n\n"
    "Câu hỏi: {question}\nTrả lời:"
)

_RAG_V1 = (
    "Bạn là trợ lý hỏi đáp về sản phẩm bảo hiểm cá nhân của Bảo Việt. "
    "Chỉ dùng thông tin trong các đoạn tài liệu dưới đây, không dùng kiến thức bên ngoài.\n"
    "Quy tắc:\n"
    "1. Trả lời ngắn gọn bằng tiếng Việt, giữ nguyên số liệu như trong tài liệu.\n"
    "2. Sau mỗi ý, ghi mã đoạn nguồn trong ngoặc vuông, ví dụ [SPMAU_QT_C1_M2_K1].\n"
    "3. Nếu các đoạn tài liệu không có căn cứ để trả lời, chỉ trả lời đúng một câu: \"{refusal}\"\n\n"
    "{context}\n\n"
    "Câu hỏi: {question}\nTrả lời:"
)

PROMPTS = {"norag_v1": _NORAG_V1, "rag_v1": _RAG_V1}


def format_context(contexts: list[dict]) -> str:
    """contexts: list dict có chunk_id, text (payload của Retriever)."""
    return "\n\n".join(f"<doc id=\"{c['chunk_id']}\">\n{c['text']}\n</doc>" for c in contexts)


def build_prompt(name: str, question: str, contexts: list[dict] | None = None) -> str:
    if name not in PROMPTS:
        raise KeyError(f"prompt {name!r} chưa định nghĩa; có: {sorted(PROMPTS)}")
    if name.startswith("norag"):
        if contexts:
            raise ValueError(f"prompt {name} không nhận ngữ cảnh")
        return PROMPTS[name].format(refusal=REFUSAL, question=question)
    if not contexts:
        raise ValueError(f"prompt {name} cần ít nhất 1 đoạn ngữ cảnh")
    return PROMPTS[name].format(refusal=REFUSAL, question=question, context=format_context(contexts))
