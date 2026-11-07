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

# B4 (tuần 6, decision-log 2026-11-07 đầu vào B4): đoạn ngữ cảnh đánh số, trích dẫn [n] rồi map về chunk_id
# (src/pipeline.parse_numbered_citations) thay vì bắt model chép mã chunk: rag_v1 hay đổi mã thật sang tiền tố mã
# ví dụ SPMAU_. Thêm quy tắc cho câu hỏi loại trừ (7/14 câu nghi lỗi test từ chối dù evidence trong top-5), đọc bảng
# và câu nhiều sản phẩm (hedge ở compare).
_RAG_V2 = (
    "Bạn là trợ lý hỏi đáp về sản phẩm bảo hiểm cá nhân của Bảo Việt. "
    "Chỉ dùng thông tin trong các đoạn tài liệu đánh số dưới đây, không dùng kiến thức bên ngoài.\n"
    "Quy tắc:\n"
    "1. Trả lời ngắn gọn bằng tiếng Việt, giữ nguyên số liệu (số tiền, tỷ lệ, tuổi, thời hạn) như trong tài liệu.\n"
    "2. Sau mỗi ý, ghi số thứ tự của đoạn làm căn cứ trong ngoặc vuông, ví dụ [1] hoặc [2][3]. "
    "Chỉ dùng số của các đoạn bên dưới, không ghi tên hay mã tài liệu.\n"
    "3. Với câu hỏi có được chi trả, bồi thường hay bảo hiểm không: nếu tài liệu ghi trường hợp đó thuộc điểm loại trừ "
    "hoặc không được chi trả thì trả lời là không được chi trả, nêu lý do và trích dẫn đoạn đó. "
    "Đây là câu trả lời có căn cứ, không phải trường hợp thiếu thông tin.\n"
    "4. Khi lấy số từ bảng, xác định đúng dòng và cột theo chương trình, độ tuổi, hạng mục mà câu hỏi nêu.\n"
    "5. Câu hỏi về nhiều sản phẩm: trả lời riêng cho từng sản phẩm; sản phẩm nào không có đoạn nào đề cập thì ghi "
    "\"chưa có thông tin trong các đoạn được cung cấp\" cho riêng sản phẩm đó.\n"
    "6. Chỉ khi không đoạn nào liên quan đến câu hỏi mới trả lời đúng một câu: \"{refusal}\", không viết thêm gì.\n\n"
    "{context}\n\n"
    "Câu hỏi: {question}\nTrả lời:"
)

PROMPTS = {"norag_v1": _NORAG_V1, "rag_v1": _RAG_V1, "rag_v2": _RAG_V2}
NUMBERED = {"rag_v2"}   # prompt trích dẫn bằng số thứ tự đoạn [n]


def format_context(contexts: list[dict], numbered: bool = False) -> str:
    """contexts: list dict có chunk_id, text (payload của Retriever). numbered: <doc so="n"> thay vì mã chunk."""
    if numbered:
        return "\n\n".join(f"<doc so=\"{i}\">\n{c['text']}\n</doc>" for i, c in enumerate(contexts, 1))
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
    return PROMPTS[name].format(refusal=REFUSAL, question=question, context=format_context(contexts, name in NUMBERED))
