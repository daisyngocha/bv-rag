// Thành phần dùng chung: ngôn ngữ, modal, câu trả lời, nguồn trích dẫn, chi tiết xử lý.
import React, { createContext, useContext, useEffect, useState } from "react";
import { ChevronDown, Copy, ExternalLink, FileText, ShieldCheck, Sparkles, ThumbsDown, ThumbsUp, X } from "lucide-react";
import { getTrace } from "./lib/data";
import { LABELS, sourceLine } from "./lib/util";

export const LanguageContext = createContext({ language: "vi", tx: (vi) => vi, labels: LABELS.vi });
export const useLanguage = () => useContext(LanguageContext);

export function Modal({ title, subtitle, onClose, children, wide = false }) {
  return <div className="modal-layer"><button className="modal-scrim" onClick={onClose} aria-label="Đóng" /><div className={`modal-card ${wide ? "wide" : ""}`} role="dialog" aria-modal="true"><div className="modal-head"><div><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div><button className="icon-button" onClick={onClose} aria-label="Đóng"><X size={20} /></button></div>{children}</div></div>;
}

export function Toggle({ label, detail, value, setValue }) {
  return <div className="setting-row"><div><strong>{label}</strong>{detail && <small>{detail}</small>}</div><button className={`switch ${value ? "on" : ""}`} onClick={() => setValue(!value)} aria-pressed={value} aria-label={label}><span /></button></div>;
}

export function NavButton({ active, icon: Icon, label, onClick, badge }) {
  return <button className={`nav-button ${active ? "active" : ""}`} onClick={onClick}><Icon size={18} /><span>{label}</span>{badge ? <b>{badge}</b> : null}</button>;
}

export function Loading({ text }) {
  const { tx } = useLanguage();
  return <div className="empty-copy loading-copy"><span className="spinner" /> {text || tx("Đang tải…", "Loading…")}</div>;
}

export function ErrorNote({ error, onRetry }) {
  const { tx } = useLanguage();
  if (!error) return null;
  return <div className="error-note"><span>{error}</span>{onRetry && <button className="text-button" onClick={onRetry}>{tx("Thử lại", "Retry")}</button>}</div>;
}

// PT-CHAT-07: [n] → nút trích dẫn (inline) hoặc chỉ số trên (footnote); **đậm**.
export function formatLine(line, mode, onCitation) {
  const parts = line.split(/(\*\*.*?\*\*|\[\d+(?:\s*[,;]\s*\d+)*\])/g).filter(Boolean);
  return parts.map((part, index) => {
    if (part.startsWith("**") && part.endsWith("**") && part.length > 4) return <strong key={index}>{part.slice(2, -2)}</strong>;
    if (/^\[\d+(?:\s*[,;]\s*\d+)*\]$/.test(part)) {
      const ids = part.slice(1, -1).split(/[,;]/).map((x) => Number(x.trim()));
      return <React.Fragment key={index}>{ids.map((id) => mode === "inline"
        ? <button className="citation" onClick={() => onCitation(id)} key={id}>{id}</button>
        : <sup key={id}>[{id}]</sup>)}</React.Fragment>;
    }
    return part;
  });
}

// PT-CHAT-08
export function SourceStack({ sources, openKey, setOpenKey, keyPrefix, showExcerpts }) {
  const { tx } = useLanguage();
  return <div className="source-stack"><div className="source-heading"><span><FileText size={17} /> {tx("Nguồn tham khảo", "Sources")}</span><small>{sources.length} {tx("trích dẫn", "citations")}</small></div>
    {sources.map((s) => {
      const key = `${keyPrefix}:${s.ord}`;
      const open = openKey === key;
      return <div className={`source-card ${open ? "open" : ""}`} key={key} id={`src-${key}`}>
        <button onClick={() => setOpenKey(open ? null : key)} aria-expanded={open}><span className="source-number">{s.ord}</span><span className="source-main"><strong>{s.product_name ? `${s.product_name} · ` : ""}{s.section_path || s.chunk_id}</strong><small>{s.source_file}{s.page ? ` · ${tx("Trang", "Page")} ${s.page}` : ""}</small></span><ChevronDown size={18} /></button>
        {open && <div className="source-detail">{showExcerpts && s.text && <p>“{s.text}”</p>}<small className="source-id">{s.data_version}/{s.chunk_id}</small>{s.url && <a href={s.url} target="_blank" rel="noreferrer">{tx("Mở tài liệu gốc", "Open original document")} <ExternalLink size={14} /></a>}</div>}
      </div>;
    })}
  </div>;
}

// PT-SET-06: traces + retrieval_logs (chỉ admin đọc được qua RLS).
export function ProcessingDetails({ messageId, runId }) {
  const { tx } = useLanguage();
  const [state, setState] = useState({ loading: true });
  useEffect(() => {
    let live = true;
    getTrace(messageId).then((d) => live && setState(d)).catch((e) => live && setState({ error: e.message }));
    return () => { live = false; };
  }, [messageId]);
  if (state.loading) return <div className="processing-detail-wrap"><Loading /></div>;
  if (state.error) return <div className="processing-detail-wrap"><ErrorNote error={state.error} /></div>;
  const t = state.trace;
  if (!t) return <div className="processing-detail-wrap"><p className="empty-copy">{tx("Chưa có vết xử lý cho câu trả lời này.", "No trace for this answer.")}</p></div>;
  const rows = [
    ["run_id", runId], ["query_processed", t.query_processed], ["detected_products", (t.detected_products || []).join(", ") || "—"],
    ["retrieval_mode", t.retrieval_mode], ["latency_ms", t.latency_ms], ["tokens_in / tokens_out", `${t.tokens_in ?? "—"} / ${t.tokens_out ?? "—"}`],
    ["cost_usd", t.cost_usd ?? "—"], ["timings_ms", Object.entries(t.timings_ms || {}).map(([k, v]) => `${k}: ${v}`).join(" · ")], ["error", t.error || "—"],
  ];
  return <div className="processing-detail-wrap">
    <div className="processing-panel">{rows.map(([k, v]) => <div key={k}><span>{k}</span><strong>{v ?? "—"}</strong></div>)}</div>
    {state.logs.length > 0 && <div className="retrieval-mini-table"><div><b>rank</b><b>chunk_id</b><b>score</b><b>rerank</b><b>in_context</b></div>{state.logs.map((r) => <div key={r.rank}><span>{r.rank}</span><code>{r.chunk_id}</code><span>{Number(r.score).toFixed(4)}</span><span>{r.rerank === null ? "—" : Number(r.rerank).toFixed(4)}</span><span>{r.in_context ? "true" : "false"}</span></div>)}</div>}
    <small className="admin-only-note"><ShieldCheck size={13} /> {tx("Chỉ quản trị viên được đọc traces và retrieval_logs.", "Only administrators can read traces and retrieval logs.")}</small>
  </div>;
}

export function Answer({ message, settings, showDetails, openKey, setOpenKey, onRate, onRateDown, setToast }) {
  const { tx, labels } = useLanguage();
  const mode = settings.citation_style;
  const sources = message.sources || [];
  const onCitation = (n) => {
    const key = `${message.id}:${n}`;
    setOpenKey(key);
    setTimeout(() => document.getElementById(`src-${key}`)?.scrollIntoView({ behavior: "smooth", block: "nearest" }), 50);
  };
  const copy = () => {
    const text = [message.content, ...(sources.length ? ["", tx("Nguồn:", "Sources:"), ...sources.map(sourceLine)] : [])].join("\n");
    navigator.clipboard?.writeText(text);
    setToast(tx("Đã sao chép câu trả lời và nguồn", "Answer and sources copied"));
  };
  const rating = message.feedback?.rating;
  const canRate = Boolean(message.id) && !String(message.id).startsWith("tmp-");
  return <div className="assistant-row">
    <div className="avatar assistant-avatar"><Sparkles size={17} /></div>
    <div className="answer-wrap">
      <div className="answer-label">{tx("Trợ lý Bảo Việt", "Bảo Việt Assistant")}</div>
      {message.refused && <div className="refusal-label"><ShieldCheck size={16} /> {tx("Từ chối an toàn", "Safe refusal")}{message.refusal_reason ? ` · ${labels.refusal_reason[message.refusal_reason] || message.refusal_reason}` : ""}</div>}
      <div className={`answer-text ${message.refused ? "refused" : ""}`}>{message.content.split("\n").map((line, i) => <p key={i}>{formatLine(line, mode, onCitation)}</p>)}</div>
      {message.refused && message.refusal_reason === "ngoai_pham_vi" && <p className="refusal-hint">{tx("Câu hỏi này nằm ngoài các sản phẩm đang có trong kho tài liệu. Vui lòng liên hệ kênh tư vấn chính thức của Bảo Việt hoặc đại lý để được hỗ trợ.", "This question is outside the products in the document base. Please contact Bảo Việt's official advisory channels or an agent.")}</p>}
      {mode === "footnote" && sources.length > 0 && <ol className="footnote-list">{sources.map((s) => <li key={s.ord} value={s.ord}>{s.product_name ? `${s.product_name} · ` : ""}{s.section_path}{s.page ? `, ${tx("trang", "page")} ${s.page}` : ""}</li>)}</ol>}
      {sources.length > 0 && <SourceStack sources={sources} openKey={openKey} setOpenKey={setOpenKey} keyPrefix={message.id} showExcerpts={settings.show_source_text} />}
      {showDetails && canRate && <ProcessingDetails messageId={message.id} runId={message.run_id} />}
      <div className="answer-actions">
        <button onClick={copy}><Copy size={16} /> {tx("Sao chép", "Copy")}</button><span />
        <span>{tx("Câu trả lời này có hữu ích?", "Was this answer helpful?")}</span>
        <button className={rating === 1 ? "selected" : ""} disabled={!canRate} onClick={() => onRate(message)} aria-label={tx("Hữu ích", "Helpful")}><ThumbsUp size={16} /></button>
        <button className={rating === -1 ? "selected" : ""} disabled={!canRate} onClick={() => onRateDown(message)} aria-label={tx("Không hữu ích", "Not helpful")}><ThumbsDown size={16} /></button>
      </div>
    </div>
  </div>;
}

export function StreamingAnswer({ text, stage }) {
  const { tx } = useLanguage();
  return <div className="assistant-row"><div className="avatar assistant-avatar"><Sparkles size={17} /></div><div className="answer-wrap"><div className="answer-label">{tx("Trợ lý Bảo Việt", "Bảo Việt Assistant")}</div>{!text ? <div className="thinking"><strong>{stage || tx("Đang tìm trong tài liệu chính thức", "Searching official documents")}</strong><div><i /><i /><i /></div></div> : <div className="answer-text streaming"><p>{text}<span className="stream-caret" /></p></div>}</div></div>;
}
