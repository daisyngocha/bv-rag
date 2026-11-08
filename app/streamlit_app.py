"""Giao diện demo (Streamlit) gọi FastAPI /ask. Chạy từ gốc repo để nạp theme `.streamlit/config.toml`:
    BV_API_URL=http://localhost:8000 streamlit run app/streamlit_app.py

Giao diện theo chuẩn Bảo Việt Design (token: primary #00469C, navy #0A2540, Inter, radius 8/12/full, elevation 1).
Trạng thái câu trả lời luôn có icon + chữ, không chỉ dùng màu. Mỗi câu hỏi được trả lời độc lập (pipeline B4 không
dùng lịch sử); lịch sử chỉ để hiển thị. Chỉ sửa phần hiển thị ở file này, không đổi logic trả lời (app/service.py, src/).
"""
from __future__ import annotations

import html
import os
import re

import requests
import streamlit as st

API = os.environ.get("BV_API_URL", "http://localhost:8000").rstrip("/")
NUM_CITE = re.compile(r"\[\s*(\d{1,2}(?:\s*[,;]\s*\d{1,2})*)\s*\]")

st.set_page_config(page_title="Tra cứu sản phẩm Bảo Việt", page_icon=":material/shield:", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,400,0,0&display=block');
:root {
  --bv-primary:#00469C; --bv-primary-light:#3B8FF4; --bv-primary-container:#D1E6FD; --bv-on-primary-container:#001B3D;
  --bv-navy:#0A2540; --bv-gold:#E7AE00; --bv-surface:#FFFFFF; --bv-surface-container:#F0F3F5;
  --bv-surface-high:#E5E9EC; --bv-on-surface-variant:#4F6578; --bv-outline:#6B7C8C; --bv-outline-variant:#BFC8D0;
  --bv-error:#BA1A1A; --bv-error-bg:#FDECEC; --bv-success:#0D8A4E; --bv-success-bg:#E6F4EC;
  --bv-warning-bg:#FFF7DB; --bv-on-warning:#8A6A00; --bv-elev-1:0 1px 3px rgba(10,37,64,.08);
}
.ms { font-family:'Material Symbols Outlined'; font-weight:normal; font-style:normal; font-size:20px; line-height:1;
      display:inline-block; vertical-align:middle; -webkit-font-feature-settings:'liga'; font-feature-settings:'liga'; }
.block-container { padding-top:1.5rem; padding-bottom:2rem; max-width:1200px; }
[data-testid="stHeader"] { background:transparent; }

/* Top bar 64px, nền trắng, elevation 1 */
.bv-topbar { display:flex; align-items:center; justify-content:space-between; gap:16px; min-height:64px;
  background:var(--bv-surface); border-radius:12px; box-shadow:var(--bv-elev-1); padding:8px 24px; margin-bottom:24px; }
.bv-topbar .crumb { font-size:12px; line-height:16px; color:var(--bv-on-surface-variant); }
.bv-topbar h1 { font-size:24px; line-height:32px; font-weight:600; color:var(--bv-navy); margin:0; padding:0; }
.bv-topbar .right { display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end; }

/* Badge trạng thái: radius full, Label Medium, icon 14px + chữ */
.bv-badge { display:inline-flex; align-items:center; gap:4px; border-radius:9999px; padding:2px 10px;
  font-size:12px; line-height:20px; font-weight:500; white-space:nowrap; }
.bv-badge .ms { font-size:16px; }
.bv-badge.success { background:var(--bv-success-bg); color:var(--bv-success); }
.bv-badge.warning { background:var(--bv-warning-bg); color:var(--bv-on-warning); }
.bv-badge.error { background:var(--bv-error-bg); color:var(--bv-error); }
.bv-badge.info { background:var(--bv-primary-container); color:var(--bv-on-primary-container); }
.bv-badge.neutral { background:var(--bv-surface-container); color:var(--bv-on-surface-variant); }

/* Thẻ hỏi đáp: card trắng, radius 12, viền #E5E7EB, elevation 1 */
[class*="st-key-turn_"], .st-key-empty, .st-key-apierror {
  background:var(--bv-surface); border:1px solid #E5E7EB; border-radius:12px; box-shadow:var(--bv-elev-1);
  padding:20px 24px; }
.bv-q-label { font-size:12px; line-height:16px; font-weight:500; color:var(--bv-on-surface-variant);
  text-transform:uppercase; letter-spacing:.04em; display:flex; align-items:center; gap:6px; }
.bv-q { font-size:16px; line-height:24px; font-weight:500; color:var(--bv-navy); margin:4px 0 0; }
.bv-divider { border:none; border-top:1px solid var(--bv-surface-high); margin:4px 0; }
.bv-answer-head { display:flex; align-items:center; justify-content:space-between; gap:8px; flex-wrap:wrap; }
.bv-answer p, .bv-answer li { font-size:16px; line-height:24px; color:var(--bv-navy); }
.bv-cite { display:inline-flex; align-items:center; justify-content:center; min-width:22px; height:20px; padding:0 6px;
  margin:0 1px; border-radius:9999px; background:var(--bv-primary-container); color:var(--bv-on-primary-container);
  font-size:12px; font-weight:600; line-height:20px; vertical-align:1px; font-variant-numeric:tabular-nums; }
.bv-refusal { display:flex; gap:12px; align-items:flex-start; background:var(--bv-warning-bg); border-radius:8px;
  padding:12px 16px; color:var(--bv-navy); font-size:16px; line-height:24px; }
.bv-refusal .ms { color:var(--bv-on-warning); font-size:24px; }
.bv-refusal small { display:block; color:var(--bv-on-warning); font-size:12px; line-height:16px; margin-top:4px; }
.bv-flag { display:flex; gap:8px; align-items:center; background:var(--bv-error-bg); color:var(--bv-error);
  border-radius:8px; padding:8px 12px; font-size:14px; line-height:20px; }
.bv-meta { display:flex; flex-wrap:wrap; gap:4px 16px; margin:4px 0 8px; font-size:12px; line-height:16px; color:var(--bv-on-surface-variant); }
.bv-meta span { display:inline-flex; align-items:center; gap:4px; }
.bv-meta .ms { font-size:16px; }
.bv-section { font-size:14px; line-height:20px; font-weight:500; color:var(--bv-navy); margin:8px 0 0;
  display:flex; align-items:center; gap:6px; }
.bv-section .count { color:var(--bv-on-surface-variant); font-weight:400; }

/* Thẻ nguồn (expander) */
[class*="st-key-turn_"] [data-testid="stExpander"] details { border:1px solid var(--bv-outline-variant); border-radius:12px;
  background:var(--bv-surface); }
[class*="st-key-turn_"] [data-testid="stExpander"] summary:hover { background:rgba(0,70,156,.08); border-radius:12px; }
.bv-src-meta { display:flex; flex-wrap:wrap; gap:6px; align-items:center; font-size:12px; line-height:16px;
  color:var(--bv-on-surface-variant); margin-bottom:8px; }
.bv-src-meta code { background:var(--bv-surface-container); color:var(--bv-navy); border-radius:8px; padding:2px 6px; font-size:12px; }
.bv-src-meta a { color:var(--bv-primary); font-weight:500; text-decoration:none; display:inline-flex; align-items:center; gap:2px; }
.bv-src-meta a:hover { text-decoration:underline; }
.bv-quote { border-left:3px solid var(--bv-primary-light); background:#F5F7F8; border-radius:0 8px 8px 0; padding:12px 16px;
  font-size:14px; line-height:20px; color:var(--bv-navy); white-space:pre-wrap; max-height:320px; overflow:auto; }

/* Trạng thái trống / lỗi */
.bv-empty { text-align:center; padding:24px 8px 8px; }
.bv-empty > .ms { font-size:48px; color:var(--bv-primary); }
.bv-empty h3 { font-size:24px; line-height:32px; font-weight:600; color:var(--bv-navy); margin:8px 0 4px; padding:0; }
.bv-empty p { font-size:14px; line-height:20px; color:var(--bv-on-surface-variant); margin:0 auto; max-width:560px; }
.bv-groups { display:flex; flex-wrap:wrap; justify-content:center; gap:8px; margin-top:16px; }
.bv-error-head { display:flex; gap:12px; align-items:center; }
.bv-error-head .ms { font-size:40px; color:var(--bv-error); }
.bv-error-head h3 { font-size:22px; line-height:28px; font-weight:500; margin:0; padding:0; color:var(--bv-navy); }

/* Ô nhập câu hỏi */
[data-testid="stChatInput"] > div { border-radius:12px; border:1.5px solid #D1D5DB; background:var(--bv-surface); box-shadow:var(--bv-elev-1); }
[data-testid="stChatInput"] > div:focus-within { border-color:var(--bv-primary); box-shadow:0 0 0 3px rgba(0,70,156,.1); }

/* Sidebar navy 256px */
[data-testid="stSidebar"] { min-width:256px; max-width:300px; }
.bv-brand { display:flex; flex-direction:column; gap:6px; padding:4px 0 16px; border-bottom:1px solid rgba(255,255,255,.1); margin-bottom:8px; }
.bv-brand .name { font-size:20px; line-height:28px; font-weight:700; letter-spacing:.08em; color:#FFFFFF; }
.bv-brand .bar { width:32px; height:3px; border-radius:2px; background:var(--bv-gold); }
.bv-brand .sub { font-size:12px; line-height:16px; color:rgba(255,255,255,.6); }
.bv-side-label { font-size:11px; line-height:16px; font-weight:500; text-transform:uppercase; letter-spacing:.06em;
  color:rgba(255,255,255,.6); margin:16px 0 8px; }
.bv-prod { display:flex; justify-content:space-between; align-items:center; gap:8px; padding:6px 0; font-size:14px;
  line-height:20px; color:rgba(255,255,255,.9); border-bottom:1px solid rgba(255,255,255,.06); }
.bv-prod code { background:rgba(59,143,244,.15); color:#A3CDFB; border-radius:8px; padding:1px 6px; font-size:11px; }
.bv-api { display:flex; align-items:center; gap:6px; font-size:12px; line-height:16px; color:rgba(255,255,255,.9);
  background:rgba(255,255,255,.05); border-radius:8px; padding:8px 12px; }
.bv-api .dot { width:8px; height:8px; border-radius:50%; }
[data-testid="stSidebar"] [data-testid="stButton"] button { justify-content:flex-start; text-align:left; min-height:48px;
  background:transparent; border:1px solid rgba(255,255,255,.14); color:rgba(255,255,255,.9); border-radius:8px; }
[data-testid="stSidebar"] [data-testid="stButton"] button p { font-size:13px; line-height:18px; text-align:left; }
[data-testid="stSidebar"] [data-testid="stButton"] button:hover { background:rgba(59,143,244,.15); border-color:#3B8FF4; color:#FFFFFF; }
[data-testid="stSidebar"] [data-testid="stButton"] button:focus-visible { outline:3px solid #3B8FF4; outline-offset:2px; }
.bv-note { font-size:12px; line-height:16px; color:rgba(255,255,255,.6); margin-top:16px; }
</style>
"""

GROUP_LABELS = ["Tra cứu quy tắc", "Bảng quyền lợi, biểu phí", "Tình huống", "So sánh sản phẩm", "Ngoài phạm vi → từ chối"]


def icon(name: str) -> str:
    return f'<span class="ms" aria-hidden="true">{name}</span>'


def badge(kind: str, ic: str, text: str) -> str:
    return f'<span class="bv-badge {kind}">{icon(ic)}{html.escape(text)}</span>'


def get(path: str, timeout: float = 10):
    r = requests.get(f"{API}{path}", timeout=timeout)
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=300, show_spinner=False)
def get_cached(path: str):
    """Danh mục sản phẩm, câu hỏi mẫu: ít đổi nên cache; /health thì không cache để báo đúng trạng thái API."""
    return get(path)


def ask(question: str) -> dict:
    r = requests.post(f"{API}/ask", json={"question": question}, timeout=300)
    if r.status_code != 200:
        raise RuntimeError(f"API {r.status_code}: {r.text[:300]}")
    return r.json()


def render_answer(text: str) -> str:
    """Escape HTML do model sinh ra, giữ Markdown; [1, 2] → pill số trích dẫn."""
    safe = html.escape(text, quote=False)
    return NUM_CITE.sub(lambda m: "".join(f'<span class="bv-cite">{n}</span>' for n in re.findall(r"\d+", m.group(1))), safe)


def status_badge(res: dict) -> str:
    if res["refused"]:
        return badge("warning", "block", "Từ chối · dưới ngưỡng" if res.get("gated") else "Từ chối")
    if res.get("nums_unsupported") or res.get("citations_invalid"):
        return badge("error", "error", "Cần kiểm tra")
    if res.get("citations"):
        return badge("success", "check_circle", f"Có trích dẫn · {len(res['citations'])} nguồn")
    return badge("neutral", "help", "Không có trích dẫn")


def render_source(s: dict):
    label = f"[{s['n']}] {s['product_name']} · {s['doc_label']}"
    if s.get("section"):
        label += f" · {s['section']}"
    label += f" · tr. {s['page']}"
    with st.expander(label, icon=":material/description:" if s["cited"] else ":material/article:"):
        tags = [x for x, on in (("Bảng", s.get("is_table")), ("OCR", s.get("ocr")), ("Bảng nhập tay", s.get("manual"))) if on]
        parts = [f"<code>{html.escape(s['chunk_id'])}</code>", html.escape(s.get("source_file") or ""),
                 f"hiệu lực {html.escape(s.get('effective_date') or '?')}"]
        if s.get("score") is not None:
            parts.append(f"điểm rerank {s['score']:.3f}")
        parts += [badge("neutral", "label", t) for t in tags]
        if s.get("url"):
            parts.append(f'<a href="{html.escape(s["url"])}" target="_blank" rel="noopener">Trang sản phẩm {icon("open_in_new")}</a>')
        st.markdown(f'<div class="bv-src-meta">{" · ".join(parts)}</div>'
                    f'<div class="bv-quote">{html.escape(s["text"])}</div>', unsafe_allow_html=True)


def render_turn(i: int, turn: dict):
    with st.container(key=f"turn_{i}"):
        st.markdown(f'<div class="bv-q-label">{icon("person")}Câu hỏi</div>'
                    f'<p class="bv-q">{html.escape(turn["question"])}</p><hr class="bv-divider">', unsafe_allow_html=True)
        if "error" in turn:
            st.markdown(f'<div class="bv-flag">{icon("error")}Không nhận được câu trả lời: {html.escape(turn["error"])}</div>',
                        unsafe_allow_html=True)
            return
        res = turn["result"]
        st.markdown(f'<div class="bv-answer-head"><div class="bv-q-label">{icon("smart_toy")}Trả lời</div>'
                    f'{status_badge(res)}</div>', unsafe_allow_html=True)
        if res["refused"]:
            why = ("Điểm liên quan cao nhất của tài liệu dưới ngưỡng, hệ thống từ chối không gọi LLM."
                   if res.get("gated") else "LLM xác định ngữ cảnh không đủ căn cứ để trả lời.")
            st.markdown(f'<div class="bv-refusal">{icon("info")}<div>{html.escape(res["answer"])}<small>{why}</small></div></div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="bv-answer">\n\n{render_answer(res["answer"])}\n\n</div>', unsafe_allow_html=True)
        flags = []
        if res.get("nums_unsupported"):
            flags.append("số không có trong nguồn: " + ", ".join(res["nums_unsupported"]))
        if res.get("citations_invalid"):
            flags.append("trích dẫn không hợp lệ: " + ", ".join(res["citations_invalid"]))
        if flags:
            st.markdown(f'<div class="bv-flag">{icon("warning")}Cần kiểm tra lại: {html.escape("; ".join(flags))}</div>',
                        unsafe_allow_html=True)
        meta = [f'{icon("schedule")}{res["latency_ms"] / 1000:.1f} s (truy xuất {res["retrieval_ms"]} ms · LLM {res["llm_ms"]} ms)']
        if res.get("products_detected"):
            meta.append(f'{icon("inventory_2")}Sản phẩm nhận diện: {html.escape(", ".join(res["products_detected"]))}')
        if res.get("rerank_max") is not None:
            meta.append(f'{icon("leaderboard")}Rerank max {res["rerank_max"]:.3f}')
        meta.append(f'{icon("tune")}Cấu hình {html.escape(str(res.get("config")))}')
        st.markdown('<div class="bv-meta">' + "".join(f"<span>{m}</span>" for m in meta) + "</div>", unsafe_allow_html=True)
        cited = [s for s in res["sources"] if s["cited"]]
        other = [s for s in res["sources"] if not s["cited"]]
        other_title = "Đoạn truy xuất được (không dùng để trả lời)" if res["refused"] else "Đoạn ngữ cảnh khác"
        for title, ic, group in (("Nguồn được trích dẫn", "verified", cited), (other_title, "folder_open", other)):
            if group:
                st.markdown(f'<div class="bv-section">{icon(ic)}{title}<span class="count">({len(group)})</span></div>',
                            unsafe_allow_html=True)
                for s in group:
                    render_source(s)


st.markdown(CSS, unsafe_allow_html=True)

# Sidebar: thương hiệu, trạng thái API, sản phẩm, câu hỏi mẫu
api_ok, api_err, health, prods, demo = False, None, {}, [], []
try:
    health = get("/health", timeout=3)
    api_ok = bool(health.get("ok"))
    prods = get_cached("/products")
    demo = get_cached("/demo-questions")
except Exception as e:   # API chưa chạy: vẫn hiện giao diện + trạng thái lỗi
    api_err = str(e)

with st.sidebar:
    st.markdown('<div class="bv-brand"><span class="name">BẢO VIỆT</span><span class="bar"></span>'
                '<span class="sub">Trợ lý tra cứu sản phẩm bảo hiểm · demo ĐA1</span></div>', unsafe_allow_html=True)
    dot, txt = ("#0D8A4E", f"API sẵn sàng · cấu hình {health.get('config')}") if api_ok else \
        ("#E7AE00", "API đang khởi động") if health else ("#BA1A1A", "Mất kết nối API")
    st.markdown(f'<div class="bv-api"><span class="dot" style="background:{dot}"></span>{html.escape(txt)}</div>',
                unsafe_allow_html=True)
    if prods:
        st.markdown('<div class="bv-side-label">Sản phẩm trong kho</div>' + "".join(
            f'<div class="bv-prod"><span>{html.escape(p["product_name"])}</span><code>{p["product_code"]}</code></div>'
            for p in prods), unsafe_allow_html=True)
    if demo:
        st.markdown('<div class="bv-side-label">Câu hỏi mẫu (tập dev)</div>', unsafe_allow_html=True)
        for q in demo:
            if st.button(f"{q['label']} · {q['note']}", key=q["qid"], width="stretch", help=q["question"]):
                st.session_state.pending = q["question"]
    st.markdown('<div class="bv-side-label">Phiên làm việc</div>', unsafe_allow_html=True)
    if st.button("Xóa hội thoại", icon=":material/delete_sweep:", width="stretch"):
        st.session_state.history = []
    st.markdown('<div class="bv-note">Câu trả lời chỉ dựa trên quy tắc, bảng quyền lợi, biểu phí đã nạp; '
                'không thay thế tư vấn chính thức.</div>', unsafe_allow_html=True)

# Top bar
right = badge("success", "check_circle", "Sẵn sàng") if api_ok else badge("error", "cloud_off", "Mất kết nối API")
if health.get("config"):
    right += badge("info", "tune", f"Cấu hình {health['config']}")
if prods:
    right += badge("neutral", "library_books", f"{len(prods)} sản phẩm")
st.markdown(f'<div class="bv-topbar"><div><div class="crumb">ĐA1 · RAG tiếng Việt · Hybrid + rerank + Qwen2.5 7B</div>'
            f'<h1>Tra cứu sản phẩm bảo hiểm</h1></div><div class="right">{right}</div></div>', unsafe_allow_html=True)

st.session_state.setdefault("history", [])

if api_err and not st.session_state.history:
    with st.container(key="apierror"):
        st.markdown(f'<div class="bv-error-head">{icon("cloud_off")}<h3>Không kết nối được API</h3></div>'
                    f'<p style="color:#4F6578;font-size:14px;margin:8px 0">Kiểm tra API tại <code>{html.escape(API)}</code> '
                    f'đã chạy và nạp xong model. Chi tiết: {html.escape(api_err[:200])}</p>', unsafe_allow_html=True)
        if st.button("Thử lại", icon=":material/refresh:", type="primary"):
            st.cache_data.clear()
            st.rerun()
elif not st.session_state.history:
    with st.container(key="empty"):
        st.markdown(f'<div class="bv-empty">{icon("forum")}<h3>Đặt câu hỏi về sản phẩm</h3>'
                    f'<p>Hệ thống truy xuất quy tắc, bảng quyền lợi, biểu phí của {len(prods)} sản phẩm Bảo Việt, trả lời kèm trích dẫn '
                    'nguồn [n] và từ chối khi tài liệu không có căn cứ. Chọn câu hỏi mẫu ở thanh bên hoặc nhập câu hỏi bên dưới.</p>'
                    '<div class="bv-groups">' + "".join(badge("info", "label", g) for g in GROUP_LABELS) + "</div></div>",
                    unsafe_allow_html=True)

for i, turn in enumerate(st.session_state.history):
    render_turn(i, turn)

q = st.chat_input("Hỏi về quy tắc, quyền lợi, biểu phí…", disabled=not api_ok) or st.session_state.pop("pending", None)
if q:
    with st.spinner(f"Đang truy xuất và sinh câu trả lời: {q[:80]}{'…' if len(q) > 80 else ''}"):
        try:
            turn = {"question": q, "result": ask(q)}
        except Exception as e:
            turn = {"question": q, "error": str(e)}
    st.session_state.history.append(turn)
    st.rerun()
