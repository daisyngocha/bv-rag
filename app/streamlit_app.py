"""Giao diện demo (Streamlit) gọi FastAPI /ask. Chạy: BV_API_URL=http://localhost:8000 streamlit run app/streamlit_app.py

Hội thoại nhiều lượt chỉ ở mức hiển thị: mỗi câu hỏi được trả lời độc lập (pipeline B4 không dùng lịch sử).
"""
from __future__ import annotations

import os
import re

import requests
import streamlit as st

API = os.environ.get("BV_API_URL", "http://localhost:8000").rstrip("/")
NUM_CITE = re.compile(r"\[\s*(\d{1,2}(?:\s*[,;]\s*\d{1,2})*)\s*\]")

st.set_page_config(page_title="Tra cứu sản phẩm Bảo Việt (RAG)", page_icon="📄", layout="wide")


@st.cache_data(ttl=60)
def get(path: str):
    r = requests.get(f"{API}{path}", timeout=10)
    r.raise_for_status()
    return r.json()


def ask(question: str) -> dict:
    r = requests.post(f"{API}/ask", json={"question": question}, timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f"API {r.status_code}: {r.text[:300]}")
    return r.json()


def render_answer(text: str) -> str:
    """[1, 2] → **[1]** **[2]** để dễ đối chiếu với danh sách nguồn."""
    return NUM_CITE.sub(lambda m: " ".join(f"**[{n}]**" for n in re.findall(r"\d+", m.group(1))), text)


def render_result(res: dict):
    if res["refused"]:
        why = "điểm rerank dưới ngưỡng, không gọi LLM" if res.get("gated") else "LLM từ chối"
        st.warning(f"{res['answer']}\n\n_({why})_")
    else:
        st.markdown(render_answer(res["answer"]))
    flags = []
    if res.get("nums_unsupported"):
        flags.append("số không có trong nguồn: " + ", ".join(res["nums_unsupported"]))
    if res.get("citations_invalid"):
        flags.append("trích dẫn không hợp lệ: " + ", ".join(res["citations_invalid"]))
    if flags:
        st.error("Cần kiểm tra lại: " + "; ".join(flags))
    meta = [f"{res['latency_ms'] / 1000:.1f} s (truy xuất {res['retrieval_ms']} ms, LLM {res['llm_ms']} ms)"]
    if res.get("products_detected"):
        meta.append("sản phẩm nhận diện: " + ", ".join(res["products_detected"]))
    if res.get("rerank_max") is not None:
        meta.append(f"rerank max {res['rerank_max']:.3f}")
    meta.append(f"config {res.get('config')}")
    st.caption(" · ".join(meta))
    if not res["sources"]:
        return
    cited = [s for s in res["sources"] if s["cited"]]
    other = [s for s in res["sources"] if not s["cited"]]
    other_title = "Đoạn truy xuất được (không dùng để trả lời)" if res["refused"] else "Đoạn ngữ cảnh khác"
    for title, group, expanded in (("Nguồn được trích dẫn", cited, False), (other_title, other, False)):
        if not group:
            continue
        st.markdown(f"**{title}**")
        for s in group:
            label = f"[{s['n']}] {s['product_name']} · {s['doc_label']} · {s['section'] or ''} · tr. {s['page']}"
            with st.expander(label, expanded=expanded):
                link = f" · [trang sản phẩm]({s['url']})" if s.get("url") else ""
                notes = [x for x, on in (("bảng", s.get("is_table")), ("OCR", s.get("ocr")),
                                         ("bảng nhập tay", s.get("manual"))) if on]
                st.caption(f"`{s['chunk_id']}` · {s['source_file']} · hiệu lực {s.get('effective_date') or '?'}"
                           f"{' · ' + ', '.join(notes) if notes else ''}{link}")
                st.markdown(s["text"])


with st.sidebar:
    st.header("Tra cứu sản phẩm BHBV")
    try:
        h = get("/health")
        st.success(f"API sẵn sàng ({h.get('config')})" if h.get("ok") else "API đang khởi động")
        prods = get("/products")
        st.markdown("**Sản phẩm trong kho**")
        for p in prods:
            st.markdown(f"- {p['product_name']} (`{p['product_code']}`, hiệu lực {p.get('effective_date') or '?'})")
        demo = get("/demo-questions")
    except Exception as e:   # API chưa chạy: vẫn hiện giao diện
        st.error(f"Không kết nối được API {API}: {e}")
        demo = []
    if demo:
        st.markdown("**Câu hỏi mẫu (dev)**")
        for q in demo:
            if st.button(f"{q['label']}: {q['note']}", key=q["qid"], width="stretch"):
                st.session_state.pending = q["question"]
    if st.button("Xóa hội thoại", width="stretch"):
        st.session_state.history = []
    st.caption("Câu trả lời chỉ dựa trên quy tắc, bảng quyền lợi, biểu phí đã nạp; không thay thế tư vấn chính thức.")

st.session_state.setdefault("history", [])
for turn in st.session_state.history:
    with st.chat_message("user"):
        st.markdown(turn["question"])
    with st.chat_message("assistant"):
        if "result" in turn:
            render_result(turn["result"])
        else:
            st.error(turn["error"])

q = st.chat_input("Hỏi về quy tắc, quyền lợi, biểu phí…") or st.session_state.pop("pending", None)
if q:
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        with st.spinner("Đang truy xuất và sinh câu trả lời…"):
            try:
                turn = {"question": q, "result": ask(q)}
                render_result(turn["result"])
            except Exception as e:
                turn = {"question": q, "error": str(e)}
                st.error(str(e))
    st.session_state.history.append(turn)
