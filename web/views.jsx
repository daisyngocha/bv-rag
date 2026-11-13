// Các màn hình ngoài khung chat: lịch sử, danh mục, dashboard, nhật ký, tài khoản, cấu hình, cài đặt, hệ thống.
import React, { useCallback, useEffect, useState } from "react";
import {
  Activity, ArrowUp, BarChart3, Bot, Check, CheckCircle2, Copy, Download, ExternalLink, FileText, Gauge, KeyRound,
  LockKeyhole, MessagesSquare, Moon, MoreHorizontal, Pencil, Plus, RefreshCw, Search, Settings, ShieldCheck,
  SlidersHorizontal, Sparkles, Sun, ThumbsUp, Trash2, AlertTriangle,
} from "lucide-react";
import { api } from "./lib/api";
import {
  countNegativeFeedback24h, getCatalog, getConfigs, getDemoMetrics, getEvalQuality, listQueryLogs,
} from "./lib/data";
import { exportCsv, formatDate, formatDateTime, initials } from "./lib/util";
import { ErrorNote, Loading, Modal, ProcessingDetails, SourceStack, Toggle, useLanguage } from "./ui";

// ---------------------------------------------------------------- dùng chung
function useAsync(fn, deps) {
  const [state, setState] = useState({ loading: true, data: null, error: null });
  const run = useCallback(() => {
    let live = true;
    setState((s) => ({ ...s, loading: true, error: null }));
    fn().then((data) => live && setState({ loading: false, data, error: null }))
      .catch((e) => live && setState({ loading: false, data: null, error: e.message }));
    return () => { live = false; };
  }, deps); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(run, [run]);
  return { ...state, reload: run };
}

export function useDebounced(value, ms = 300) {
  const [v, setV] = useState(value);
  useEffect(() => { const t = setTimeout(() => setV(value), ms); return () => clearTimeout(t); }, [value, ms]);
  return v;
}

const pct = (x) => (x === null || x === undefined ? "—" : `${(x * 100).toLocaleString("vi-VN", { maximumFractionDigits: 1 })}%`);

// ---------------------------------------------------------------- đăng nhập (PT-AUTH-01)
export function LoginScreen({ onLogin, error, busy }) {
  const { tx } = useLanguage();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  return <div className="login-page">
    <div className="login-brand">
      <img src="/baoviet-logo.png" alt="Bảo hiểm Bảo Việt" />
      <div><span>{tx("TRỢ LÝ SẢN PHẨM BẢO HIỂM", "INSURANCE PRODUCT ASSISTANT")}</span><h1>{tx("Tra cứu nhanh. Căn cứ rõ ràng.", "Fast answers. Clear sources.")}</h1></div>
      <div className="login-trust"><ShieldCheck size={19} /><span>{tx("Chỉ sử dụng tài liệu công khai", "Public documents only")}</span></div>
    </div>
    <form className="login-card" onSubmit={(e) => { e.preventDefault(); onLogin(email.trim(), password); }}>
      <div className="login-icon"><KeyRound size={23} /></div>
      <p className="eyebrow-text">{tx("PHIÊN BẢN DEMO", "DEMO VERSION")}</p>
      <h2>{tx("Đăng nhập hệ thống", "Sign in")}</h2>
      <label>Email<input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="demo01@bv-rag.local" autoComplete="username" required /></label>
      <label>{tx("Mật khẩu", "Password")}<input type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" required /></label>
      {error && <small className="field-error">{error}</small>}
      <div className="login-note"><LockKeyhole size={15} /> {tx("Phiên tự động hết hạn sau 30 phút không thao tác.", "Session expires after 30 minutes of inactivity.")}</div>
      <button type="submit" disabled={busy}>{busy ? tx("Đang đăng nhập…", "Signing in…") : tx("Đăng nhập", "Sign in")} <ArrowUp size={18} /></button>
    </form>
  </div>;
}

export function ConfigErrorScreen({ message }) {
  return <div className="login-page"><div className="login-card"><div className="login-icon"><AlertTriangle size={23} /></div><h2>Chưa cấu hình kết nối</h2><p>{message}</p><p className="empty-copy">Tạo file <code>.env.local</code> ở gốc repo với VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY, VITE_API_URL rồi chạy lại <code>npm run dev</code>.</p></div></div>;
}

export function SessionExpired({ onContinue, onLogout }) {
  const { tx } = useLanguage();
  return <div className="modal-layer session-layer"><div className="modal-card session-card"><span className="session-lock"><LockKeyhole size={24} /></span><h2>{tx("Phiên làm việc đã hết hạn", "Session expired")}</h2><button className="primary-button" onClick={onContinue}>{tx("Tiếp tục phiên làm việc", "Continue session")}</button><button className="text-button" onClick={onLogout}>{tx("Quay về đăng nhập", "Return to sign in")}</button></div></div>;
}

// ---------------------------------------------------------------- lịch sử (PT-HIS-01…08)
export function HistoryView({ items, loading, error, reload, search, setSearch, onOpen, onRename, onDelete, onDeleteAll, onExport, onPrint }) {
  const { tx } = useLanguage();
  const [menu, setMenu] = useState(null);
  return <div className="standard-page">
    <div className="page-header"><div><h1>{tx("Lịch sử trò chuyện", "Chat history")}</h1></div><button className="danger-ghost" onClick={onDeleteAll} disabled={!items.length}><Trash2 size={16} /> {tx("Xóa tất cả", "Delete all")}</button></div>
    <div className="toolbar"><label className="page-search"><Search size={17} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={tx("Tìm trong tiêu đề và nội dung", "Search titles and messages")} /></label><span>{items.length} {tx("cuộc trò chuyện", "conversations")}</span></div>
    <ErrorNote error={error} onRetry={reload} />
    {loading && !items.length ? <Loading /> : !items.length ? <p className="empty-copy">{search ? tx("Không tìm thấy cuộc trò chuyện phù hợp.", "No matching conversations.") : tx("Chưa có cuộc trò chuyện nào.", "No conversations yet.")}</p> : null}
    <div className="history-page-list">{items.map((item) => <div className="history-row" key={item.id}>
      <button className="history-row-main" onClick={() => onOpen(item)}><span className="history-row-icon"><MessagesSquare size={19} /></span><span><strong>{item.title} {item.title_is_custom && <b className="custom-title-badge">{tx("Đã đổi tên", "Renamed")}</b>}</strong><small>{item.preview} · {item.n_messages} {tx("tin nhắn", "messages")}</small></span></button>
      <time><strong>{formatDateTime(item.updated_at)}</strong></time>
      <div className="row-menu-wrap"><button className="icon-button" onClick={() => setMenu(menu === item.id ? null : item.id)} aria-label={tx("Thao tác", "Actions")}><MoreHorizontal size={19} /></button>
        {menu === item.id && <div className="row-menu">
          <button onClick={() => { onRename(item); setMenu(null); }}><Pencil size={15} /> {tx("Đổi tên", "Rename")}</button>
          <button onClick={() => { onExport(item); setMenu(null); }}><Download size={15} /> {tx("Xuất Markdown", "Export Markdown")}</button>
          <button onClick={() => { onPrint(item); setMenu(null); }}><FileText size={15} /> {tx("In / Lưu PDF", "Print / Save PDF")}</button>
          <button className="danger" onClick={() => { onDelete(item); setMenu(null); }}><Trash2 size={15} /> {tx("Xóa", "Delete")}</button>
        </div>}
      </div>
    </div>)}</div>
  </div>;
}

// ---------------------------------------------------------------- danh mục (PT-CHAT-12)
export function CatalogView() {
  const { tx, labels } = useLanguage();
  const { loading, data, error, reload } = useAsync(getCatalog, []);
  const [selected, setSelected] = useState(null);
  if (loading) return <div className="standard-page"><Loading /></div>;
  if (error) return <div className="standard-page"><ErrorNote error={error} onRetry={reload} /></div>;
  const products = [];
  for (const r of data.rows) {
    let p = products.find((x) => x.product_code === r.product_code);
    if (!p) products.push(p = { ...r, documents: [], n_chunks: 0 });
    if (r.document_id) { p.documents.push(r); p.n_chunks += r.n_chunks; }
  }
  const sel = products.find((p) => p.product_code === selected) || products[0];
  return <div className="standard-page">
    <div className="page-header"><div><h1>{tx("Sản phẩm và tài liệu", "Products and documents")}</h1></div>{data.version && <div className="version-badge"><CheckCircle2 size={17} /> {data.version.version} · {(data.version.n_chunks || 0).toLocaleString("vi-VN")} chunks</div>}</div>
    <div className="catalog-layout">
      <div className="product-table card">
        <div className="table-head"><span>{tx("Sản phẩm", "Product")}</span><span>{tx("Nhóm", "Line")}</span><span>{tx("Tài liệu", "Documents")}</span><span>{tx("Đoạn", "Chunks")}</span></div>
        {products.map((p) => <button key={p.product_code} onClick={() => setSelected(p.product_code)} className={sel?.product_code === p.product_code ? "selected" : ""}>
          <span><b>{p.product_code}</b><strong>{p.product_name}</strong></span><span>{labels.line[p.line] || p.line}</span><span>{p.documents.length}</span><span>{p.n_chunks}</span>
        </button>)}
      </div>
      {sel && <aside className="product-detail card">
        <div className="product-detail-head"><span className="product-code">{sel.product_code}</span><b className={`status-tag ${sel.is_active ? "" : "muted"}`}>{sel.is_active ? tx("Đang hoạt động", "Active") : tx("Ngừng hoạt động", "Inactive")}</b></div>
        <h2>{sel.product_name}</h2><p className="empty-copy">{sel.company}</p><hr />
        <h3>{tx("Tài liệu", "Documents")}</h3>
        {sel.documents.length ? sel.documents.map((d) => <a key={d.document_id} href={d.url} target="_blank" rel="noreferrer">
          <FileText size={16} /><span><strong>{labels.doc_type[d.doc_type] || d.doc_type}</strong><small>{d.source_file} · {tx("hiệu lực", "effective")} {formatDate(d.effective_date)} · {d.n_chunks} {tx("đoạn", "chunks")}</small></span><ExternalLink size={14} />
        </a>) : <p className="empty-copy">{tx("Chưa có tài liệu.", "No documents available.")}</p>}
      </aside>}
    </div>
  </div>;
}

// ---------------------------------------------------------------- dashboard (PT-ADM-08, 09)
function Metric({ label, value, icon: Icon, note }) {
  return <div className="metric-card card"><span><Icon size={19} /></span><small>{label}</small><strong>{value}</strong>{note && <p>{note}</p>}</div>;
}

export function DashboardView() {
  const { tx } = useLanguage();
  const [range, setRange] = useState("today");
  const load = useCallback(async () => {
    const to = new Date(Date.now() + 60 * 1000);
    const from = new Date();
    if (range === "today") from.setHours(0, 0, 0, 0); else from.setDate(from.getDate() - 7);
    const [metrics, quality] = await Promise.all([getDemoMetrics(from.toISOString(), to.toISOString()), getEvalQuality()]);
    return { metrics, quality };
  }, [range]);
  const { loading, data, error, reload } = useAsync(load, [load]);
  const m = data?.metrics;
  const maxN = Math.max(1, ...(m?.by_product || []).map((x) => x.n));
  return <div className="standard-page">
    <div className="page-header"><div><h1>{tx("Dashboard chỉ số", "Metrics dashboard")}</h1></div><div className="header-actions">
      <div className="filter-chips"><button className={range === "today" ? "active" : ""} onClick={() => setRange("today")}>{tx("Hôm nay", "Today")}</button><button className={range === "7d" ? "active" : ""} onClick={() => setRange("7d")}>{tx("7 ngày", "7 days")}</button></div>
      <button className="secondary-button" onClick={reload}><RefreshCw size={16} className={loading ? "spin" : ""} /> {tx("Làm mới", "Refresh")}</button></div></div>
    <ErrorNote error={error} onRetry={reload} />
    {loading && !data ? <Loading /> : data && <>
      <div className="metric-grid">
        <Metric label={tx("Số câu hỏi (demo)", "Questions (demo)")} value={m.n_questions} icon={MessagesSquare} />
        <Metric label={tx("Độ trễ p95", "p95 latency")} value={m.latency_p95 === null ? "—" : `${(m.latency_p95 / 1000).toLocaleString("vi-VN", { maximumFractionDigits: 1 })} s`} icon={Gauge} note={m.latency_p50 === null ? null : `p50 ${(m.latency_p50 / 1000).toLocaleString("vi-VN", { maximumFractionDigits: 1 })} s`} />
        <Metric label={tx("Tỷ lệ từ chối", "Refusal rate")} value={pct(m.refusal_rate)} icon={ShieldCheck} />
        <Metric label={tx("Đánh giá tích cực", "Positive feedback")} value={pct(m.positive_rate)} icon={ThumbsUp} />
      </div>
      <div className="dashboard-grid">
        <div className="card chart-card"><div className="card-title"><div><h2>{tx("Chất lượng theo cấu hình (tập test)", "Quality by configuration (test set)")}</h2></div><BarChart3 size={20} /></div>
          {data.quality.length ? <><div className="bar-chart">{data.quality.map((q) => <div className="bar-group" key={q.name} title={q.run_id}><span>{q.name}</span><div><i style={{ height: `${(q["recall@5"] || 0) * 100}%` }} />{q.faithfulness_j1 === undefined ? <i style={{ visibility: "hidden" }} /> : <i style={{ height: `${q.faithfulness_j1 * 100}%` }} title={`Faithfulness ${pct(q.faithfulness_j1)}`} />}</div><small>{pct(q["recall@5"])}</small></div>)}</div>
            <div className="chart-legend"><span><i className="blue" /> Recall@5</span><span><i className="gold" /> Faithfulness (Ragas, j1)</span></div></>
            : <p className="empty-copy">{tx("Chưa có kết quả test (chạy scripts/sync_supabase.py evals).", "No test results yet.")}</p>}
        </div>
        <div className="card activity-card"><div className="card-title"><div><h2>{tx("Phân bố truy vấn theo sản phẩm", "Queries by product")}</h2></div></div>
          {m.by_product.length ? m.by_product.map((p) => <div className="progress-row" key={p.product_code}><span>{p.product_code === "khac" ? tx("Không xác định", "Unknown") : p.product_code}</span><div><i style={{ width: `${(p.n / maxN) * 100}%` }} /></div><strong>{p.n}</strong></div>)
            : <p className="empty-copy">{tx("Chưa có câu hỏi trong khoảng này.", "No questions in this range.")}</p>}
        </div>
      </div>
    </>}
  </div>;
}

// ---------------------------------------------------------------- nhật ký (PT-ADM-05, 06, PT-SET-06)
export function LogsView({ setToast }) {
  const { tx, labels } = useLanguage();
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const q = useDebounced(search);
  const [detail, setDetail] = useState(null);
  const load = useCallback(() => listQueryLogs({ filter, q }), [filter, q]);
  const { loading, data, error, reload } = useAsync(load, [load]);
  const rows = data?.rows || [];
  const filters = [["all", tx("Tất cả", "All")], ["refused", tx("Từ chối", "Refused")], ["down", tx("Không hữu ích", "Not helpful")], ["slow", tx("Độ trễ cao", "High latency")]];
  const exportRows = () => {
    exportCsv("nhat-ky-truy-van.csv", rows, ["created_at", "run_id", "username", "question", "answer", "refused", "refusal_reason", "config_name", "data_version", "latency_ms", "detected_products", "rating", "feedback_reason"]);
    setToast(tx("Đã xuất nhật ký CSV", "Logs exported to CSV"));
  };
  return <div className="standard-page">
    <div className="page-header"><div><h1>{tx("Nhật ký truy vấn", "Query logs")}</h1></div><button className="secondary-button" onClick={exportRows} disabled={!rows.length}><Download size={16} /> {tx("Xuất CSV", "Export CSV")}</button></div>
    <div className="toolbar log-toolbar"><label className="page-search"><Search size={17} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={tx("Tìm câu hỏi hoặc mã lần chạy", "Search question or run ID")} /></label><div className="filter-chips">{filters.map(([v, l]) => <button key={v} className={filter === v ? "active" : ""} onClick={() => setFilter(v)}>{l}</button>)}</div><span>{data?.count ?? 0} {tx("dòng", "rows")}</span></div>
    <ErrorNote error={error} onRetry={reload} />
    {loading && !data ? <Loading /> : <div className="data-table card"><div className="data-row head"><span>{tx("Thời gian / Mã lần chạy", "Time / Run ID")}</span><span>{tx("Câu hỏi", "Question")}</span><span>{tx("Trạng thái", "Status")}</span><span>{tx("Cấu hình", "Configuration")}</span><span>{tx("Độ trễ", "Latency")}</span><span>{tx("Đánh giá", "Feedback")}</span></div>
      {rows.map((r) => <button className="data-row" key={r.message_id} onClick={() => setDetail(r)}>
        <span><strong>{formatDateTime(r.created_at)}</strong><small>{r.run_id}{r.username ? ` · ${r.username}` : ""}</small></span><span>{r.question}</span>
        <span><b className={`status-tag ${r.refused ? "warning" : ""}`}>{r.refused ? (labels.refusal_reason[r.refusal_reason] || tx("Từ chối", "Refused")) : tx("Đã trả lời", "Answered")}</b></span>
        <span><strong>{r.config_name}</strong><small>{r.data_version}</small></span><span>{r.latency_ms ?? "—"} ms</span>
        <span>{r.rating === 1 ? tx("Hữu ích", "Helpful") : r.rating === -1 ? `${tx("Không hữu ích", "Not helpful")}${r.feedback_reason ? ` · ${labels.feedback_reason[r.feedback_reason]}` : ""}` : "—"}</span>
      </button>)}
      {!rows.length && <p className="empty-copy">{tx("Không có dòng nào.", "No rows.")}</p>}
    </div>}
    {detail && <Modal title={detail.run_id} subtitle={formatDateTime(detail.created_at)} onClose={() => setDetail(null)} wide>
      <div className="log-detail"><p><strong>{tx("Hỏi", "Question")}:</strong> {detail.question}</p><p><strong>{tx("Đáp", "Answer")}:</strong> {detail.answer}</p></div>
      <ProcessingDetails messageId={detail.message_id} runId={detail.run_id} />
    </Modal>}
  </div>;
}

export function useNegativeBadge(enabled) {
  const [n, setN] = useState(0);
  useEffect(() => {
    if (!enabled) return undefined;
    let live = true;
    const tick = () => countNegativeFeedback24h().then((c) => live && setN(c)).catch(() => {});
    tick();
    const t = setInterval(tick, 60 * 1000);
    return () => { live = false; clearInterval(t); };
  }, [enabled]);
  return n;
}

// ---------------------------------------------------------------- tài khoản (PT-ADM-01…04, FastAPI)
export function AccountsView({ setToast, me }) {
  const { tx } = useLanguage();
  const { loading, data, error, reload } = useAsync(api.listUsers, []);
  const [createOpen, setCreateOpen] = useState(false);
  const [temp, setTemp] = useState(null);
  const [busy, setBusy] = useState(null);
  const accounts = data || [];
  const act = async (id, fn, ok) => {
    setBusy(id);
    try { const r = await fn(); if (ok) setToast(ok); await reload(); return r; } catch (e) { setToast(e.message, "error"); return null; } finally { setBusy(null); }
  };
  return <div className="standard-page">
    <div className="page-header"><div><h1>{tx("Quản lý tài khoản", "Account management")}</h1></div><button className="primary-button" onClick={() => setCreateOpen(true)}><Plus size={17} /> {tx("Tạo tài khoản", "Create account")}</button></div>
    <ErrorNote error={error} onRetry={reload} />
    {loading && !data ? <Loading /> : <div className="data-table accounts-table card"><div className="data-row head"><span>{tx("Tài khoản", "Account")}</span><span>{tx("Vai trò", "Role")}</span><span>{tx("Trạng thái", "Status")}</span><span>{tx("Đăng nhập cuối", "Last sign-in")}</span><span>{tx("Thao tác", "Actions")}</span></div>
      {accounts.map((a) => <div className="data-row" key={a.id}>
        <span className="account-name"><i>{initials(a.display_name || a.username)}</i><span><strong>{a.display_name || a.username}{a.id === me ? ` (${tx("bạn", "you")})` : ""}</strong><small>{a.username} · {a.email}</small></span></span>
        <span>{a.role === "admin" ? tx("Quản trị viên", "Administrator") : tx("Người dùng", "User")}</span>
        <span><b className={`status-tag ${a.is_active ? "" : "muted"}`}>{a.is_active ? tx("Hoạt động", "Active") : tx("Đã khóa", "Locked")}</b></span>
        <span>{a.last_sign_in_at ? formatDateTime(a.last_sign_in_at) : tx("Chưa đăng nhập", "Never")}</span>
        <span className="account-actions">
          <button disabled={busy === a.id} onClick={() => act(a.id, () => api.updateUser(a.id, { role: a.role === "admin" ? "user" : "admin" }), tx("Đã cập nhật vai trò", "Role updated"))}>{tx("Đổi vai trò", "Change role")}</button>
          <button disabled={busy === a.id || a.id === me} onClick={() => act(a.id, () => api.updateUser(a.id, { is_active: !a.is_active }), a.is_active ? tx("Đã khóa tài khoản", "Account locked") : tx("Đã mở khóa tài khoản", "Account unlocked"))}>{a.is_active ? tx("Khóa", "Lock") : tx("Mở khóa", "Unlock")}</button>
          <button disabled={busy === a.id} onClick={async () => { const r = await act(a.id, () => api.resetPassword(a.id)); if (r) setTemp({ username: a.username, email: a.email, password: r.temp_password }); }}>{tx("Đặt lại mật khẩu", "Reset password")}</button>
        </span>
      </div>)}
    </div>}
    {createOpen && <CreateAccount existing={accounts} onClose={() => setCreateOpen(false)} onSave={async (body) => {
      try {
        const r = await api.createUser(body);
        setCreateOpen(false); setTemp({ username: body.username, email: body.email, password: r.temp_password });
        setToast(tx("Đã tạo tài khoản", "Account created")); reload();
      } catch (e) { setToast(e.message, "error"); }
    }} />}
    {temp && <TempPasswordModal {...temp} onClose={() => setTemp(null)} setToast={setToast} />}
  </div>;
}

function CreateAccount({ existing, onClose, onSave }) {
  const { tx } = useLanguage();
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("user");
  const [saving, setSaving] = useState(false);
  const u = username.trim().toLowerCase();
  const e = email.trim().toLowerCase();
  const validUser = /^[a-z0-9][a-z0-9._-]{2,31}$/.test(u);
  const validEmail = /^[a-z0-9][a-z0-9._-]{0,40}@bv-rag\.local$/.test(e);
  const dupUser = existing.some((a) => a.username === u);
  const dupEmail = existing.some((a) => a.email === e);
  return <Modal title={tx("Tạo tài khoản demo", "Create demo account")} subtitle={tx("Hệ thống sinh mật khẩu tạm, chỉ hiển thị một lần.", "A temporary password is generated and shown once.")} onClose={onClose}>
    <label className="modal-field">Username *<input value={username} onChange={(ev) => setUsername(ev.target.value)} placeholder="demo04" />{u && !validUser && <small className="field-error">{tx("3–32 ký tự a-z, 0-9, . _ -", "3–32 chars a-z, 0-9, . _ -")}</small>}{dupUser && <small className="field-error">{tx("Tên đăng nhập đã tồn tại.", "Username already exists.")}</small>}</label>
    <label className="modal-field">{tx("Tên hiển thị", "Display name")}<input value={displayName} onChange={(ev) => setDisplayName(ev.target.value)} placeholder={tx("Người dùng demo 04", "Demo user 04")} /></label>
    <label className="modal-field">Email *<input value={email} onChange={(ev) => setEmail(ev.target.value)} placeholder="demo04@bv-rag.local" />{e && !validEmail && <small className="field-error">{tx("Email giả dạng <tên>@bv-rag.local", "Use <name>@bv-rag.local")}</small>}{dupEmail && <small className="field-error">{tx("Email đã tồn tại.", "Email already exists.")}</small>}</label>
    <label className="modal-field">{tx("Vai trò", "Role")} *<select value={role} onChange={(ev) => setRole(ev.target.value)}><option value="user">{tx("Người dùng", "User")}</option><option value="admin">{tx("Quản trị viên", "Administrator")}</option></select></label>
    <div className="modal-actions"><button className="secondary-button" onClick={onClose}>{tx("Hủy", "Cancel")}</button><button className="primary-button" disabled={saving || !validUser || !validEmail || dupUser || dupEmail} onClick={async () => { setSaving(true); await onSave({ username: u, email: e, role, display_name: displayName.trim() || null }); setSaving(false); }}>{tx("Tạo tài khoản", "Create account")}</button></div>
  </Modal>;
}

function TempPasswordModal({ username, email, password, onClose, setToast }) {
  const { tx } = useLanguage();
  return <Modal title={tx("Mật khẩu tạm thời", "Temporary password")} subtitle={tx("Chỉ hiển thị một lần. Hãy gửi cho người dùng qua kênh an toàn.", "Shown only once. Share it through a secure channel.")} onClose={onClose}>
    <div className="temp-password"><small>{username} · {email}</small><code>{password}</code></div>
    <div className="modal-actions"><button className="secondary-button" onClick={() => { navigator.clipboard?.writeText(password); setToast(tx("Đã sao chép mật khẩu", "Password copied")); }}><Copy size={16} /> {tx("Sao chép", "Copy")}</button><button className="primary-button" onClick={onClose}>{tx("Đã lưu", "Done")}</button></div>
  </Modal>;
}

// ---------------------------------------------------------------- cấu hình (PT-SET-03, 04, 05)
const LOCAL_DESC = {
  B0: ["Không sử dụng kho tài liệu", "No document retrieval"],
  B1: ["Tìm kiếm dense với đoạn cố định", "Dense retrieval with fixed chunks"],
  B2: ["Tìm kiếm dense với đoạn theo cấu trúc", "Dense retrieval with structured chunks"],
  B3: ["Tìm kiếm hybrid và xử lý câu hỏi", "Hybrid retrieval and query processing"],
  B4: ["Pipeline đầy đủ với reranker, ngưỡng từ chối và trích dẫn", "Full pipeline with reranking, refusal threshold and citations"],
};

export function ConfigurationView({ setToast }) {
  const { tx, language } = useLanguage();
  const { loading, data, error, reload } = useAsync(getConfigs, []);
  const [draft, setDraft] = useState(null);
  const [section, setSection] = useState("settings");
  const [applying, setApplying] = useState(false);
  const configs = (data?.configs || []).filter((c) => /^B\d$/.test(c.name));
  const active = data?.active?.config;
  const desc = (c) => (LOCAL_DESC[c.name] ? LOCAL_DESC[c.name][language === "vi" ? 0 : 1] : c.description);
  useEffect(() => { if (active && !draft) setDraft(active); }, [active, draft]);
  const apply = async () => {
    setApplying(true);
    try {
      const r = await api.setActiveConfig(draft);
      setToast(tx(`Đã chuyển sang ${r.config} (run ${r.run_id})`, `Switched to ${r.config} (run ${r.run_id})`));
      reload();
    } catch (e) { setToast(e.message, "error"); } finally { setApplying(false); }
  };
  return <div className="standard-page configuration-page">
    <div className="page-header"><div><h1>{tx("Cấu hình", "Configuration")}</h1></div>
      <div className="config-section-tabs" role="tablist"><button role="tab" aria-selected={section === "settings"} className={section === "settings" ? "active" : ""} onClick={() => setSection("settings")}><Settings size={16} /> {tx("Cấu hình hệ thống", "System configuration")}</button><button role="tab" aria-selected={section === "compare"} className={section === "compare" ? "active" : ""} onClick={() => setSection("compare")}><SlidersHorizontal size={16} /> {tx("So sánh cấu hình", "Compare configurations")}</button></div></div>
    <ErrorNote error={error} onRetry={reload} />
    {loading && !data ? <Loading /> : section === "settings" ? <div className="configuration-content">
      <div className="config-summary card"><span>{tx("Cấu hình đang sử dụng", "Active configuration")}</span><strong>{active || "—"}</strong><p>{data?.active?.run_id ? `run ${data.active.run_id}` : ""}</p></div>
      <div className="config-list">{configs.map((c) => <button key={c.name} className={`config-option card ${draft === c.name ? "selected" : ""}`} onClick={() => setDraft(c.name)}>
        <span className="config-radio">{draft === c.name && <Check size={15} />}</span>
        <span><strong>{c.name}</strong><small>{desc(c)} · {c.params?.retrieval?.mode}{c.params?.rerank?.enabled ? ` · rerank ${c.params.rerank.min_score ?? ""}` : ""} · {c.params?.prompt || ""}</small></span>
        {active === c.name && <b>{tx("Đang dùng", "Active")}</b>}
      </button>)}</div>
      <div className="config-actions"><button className="primary-button" disabled={!draft || draft === active || applying} onClick={apply}>{applying ? tx("Đang nạp…", "Loading…") : tx("Áp dụng cấu hình", "Apply configuration")}</button></div>
    </div> : <CompareView configs={configs} desc={desc} setToast={setToast} />}
  </div>;
}

function CompareView({ configs, desc, setToast }) {
  const { tx } = useLanguage();
  const names = configs.map((c) => c.name);
  const [left, setLeft] = useState(names.includes("B0") ? "B0" : names[0]);
  const [right, setRight] = useState(names.includes("B4") ? "B4" : names[names.length - 1]);
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [openKey, setOpenKey] = useState(null);
  const run = async () => {
    setRunning(true); setResult(null);
    try { setResult(await api.compare(question, [left, right])); } catch (e) { setToast(e.message, "error"); } finally { setRunning(false); }
  };
  const cols = [[left, setLeft], [right, setRight]];
  return <div className="configuration-compare">
    <div className="compare-query card"><label>{tx("Câu hỏi", "Question")}<input value={question} onChange={(e) => setQuestion(e.target.value)} placeholder={tx("Ví dụ: Thời gian chờ điều trị nội trú của An Gia?", "e.g. Inpatient waiting period of An Gia?")} /></label><button className="primary-button" disabled={running || question.trim().length < 3 || left === right} onClick={run}><Sparkles size={17} className={running ? "spin" : ""} /> {running ? tx("Đang chạy…", "Running…") : tx("Chạy so sánh", "Run comparison")}</button></div>
    {left === right && <p className="field-error">{tx("Chọn 2 cấu hình khác nhau.", "Choose two different configurations.")}</p>}
    <div className="compare-grid">{cols.map(([value, setter], i) => {
      const c = configs.find((x) => x.name === value);
      const a = result?.answers?.[i];
      return <div className="compare-column card" key={i}>
        <div className="compare-head"><label>{tx("Cấu hình", "Configuration")}<select value={value} onChange={(e) => { setter(e.target.value); setResult(null); }}>{configs.map((x) => <option key={x.name} value={x.name}>{x.name}</option>)}</select></label><span>{c ? desc(c) : ""}</span></div>
        {a ? <><div className="compare-answer"><Bot size={20} /><p>{a.answer}</p></div>
          <div className="compare-stats"><span>{tx("Mã lần chạy", "Run ID")}<strong>{a.run_id}</strong></span><span>{tx("Độ trễ", "Latency")}<strong>{a.latency_ms} ms</strong></span><span>{tx("Nguồn", "Sources")}<strong>{a.n_sources}</strong></span></div>
          {a.sources.length > 0 && <SourceStack sources={a.sources} openKey={openKey} setOpenKey={setOpenKey} keyPrefix={`cmp${i}`} showExcerpts />}</>
          : <div className="empty-compare"><Gauge size={27} /><p>{running ? tx("Đang chạy…", "Running…") : tx("Chạy so sánh để xem kết quả", "Run comparison to see results")}</p></div>}
      </div>;
    })}</div>
  </div>;
}

// ---------------------------------------------------------------- cài đặt (PT-SET-01, 02)
export function SettingsPanel({ onClose, settings, update, isAdmin }) {
  const { tx } = useLanguage();
  const s = settings;
  return <div className="modal-layer"><button className="modal-scrim" onClick={onClose} aria-label="Đóng" /><div className="settings-panel"><div className="settings-title"><div><span>{tx("CÀI ĐẶT CÁ NHÂN", "PERSONAL SETTINGS")}</span><h2>{tx("Tùy chỉnh trải nghiệm", "Customize your experience")}</h2></div><button className="icon-button" onClick={onClose} aria-label="Đóng">×</button></div>
    <section><h3>{tx("GIAO DIỆN", "APPEARANCE")}</h3><div className="theme-options three">{[["light", Sun, tx("Sáng", "Light")], ["dark", Moon, tx("Tối", "Dark")], ["system", Settings, tx("Hệ thống", "System")]].map(([v, Icon, l]) => <button key={v} className={s.theme === v ? "active" : ""} onClick={() => update({ theme: v })}><Icon size={20} /> {l}</button>)}</div>
      <div className="range-setting"><span><strong>{tx("Cỡ chữ", "Font size")}</strong></span><input type="range" min="12" max="20" step="1" value={s.font_size} onChange={(e) => update({ font_size: Number(e.target.value) })} /><b>{s.font_size}px</b></div></section>
    <section><h3>{tx("NGÔN NGỮ", "LANGUAGE")}</h3><div className="language-options"><button className={s.language === "vi" ? "active" : ""} onClick={() => update({ language: "vi" })}>Tiếng Việt</button><button className={s.language === "en" ? "active" : ""} onClick={() => update({ language: "en" })}>English</button></div></section>
    <section><h3>{tx("TRÍCH DẪN VÀ XỬ LÝ", "CITATIONS AND PROCESSING")}</h3><div className="radio-setting"><span><strong>{tx("Cách hiển thị nguồn", "Citation display")}</strong></span><label><input type="radio" checked={s.citation_style === "inline"} onChange={() => update({ citation_style: "inline" })} /> {tx("Trong câu", "Inline")}</label><label><input type="radio" checked={s.citation_style === "footnote"} onChange={() => update({ citation_style: "footnote" })} /> {tx("Cuối câu", "Footnote")}</label></div>
      <Toggle label={tx("Hiển thị đoạn văn gốc", "Show source excerpts")} value={s.show_source_text} setValue={(v) => update({ show_source_text: v })} />
      {isAdmin && <Toggle label={tx("Chi tiết xử lý", "Processing details")} detail={tx("Vết truy xuất dưới mỗi câu trả lời", "Retrieval trace under each answer")} value={s.show_processing} setValue={(v) => update({ show_processing: v })} />}</section>
  </div></div>;
}

// ---------------------------------------------------------------- trạng thái hệ thống (PT-ADM-11)
export function SystemModal({ onClose }) {
  const { tx } = useLanguage();
  const { loading, data, error, reload } = useAsync(api.health, []);
  const rows = data ? [
    ["FastAPI", `${data.config} · run ${data.run_id}`, data.api, `${data.api.ms} ms`],
    ["Ollama", data.ollama.model || data.ollama.error, data.ollama, data.ollama.gpu_pct !== undefined ? `GPU ${data.ollama.gpu_pct}%` : ""],
    ["Qdrant", data.qdrant.collection || data.qdrant.note || data.qdrant.error, data.qdrant, data.qdrant.points !== undefined ? `${data.qdrant.points} chunks` : ""],
    ["Embedding", data.encoder.model || data.encoder.note || data.encoder.error, data.encoder, data.encoder.device || ""],
    ["Reranker", data.reranker.model || data.reranker.note || data.reranker.error, data.reranker, data.reranker.min_score !== undefined ? `min_score ${data.reranker.min_score}` : data.reranker.device || ""],
    ["Supabase", data.supabase.data_version ? `${data.supabase.data_version} · ${data.supabase.n_chunks} chunks` : data.supabase.error, data.supabase, `${data.supabase.ms} ms`],
  ] : [];
  return <Modal title={tx("Trạng thái hệ thống", "System status")} onClose={onClose} wide>
    <div className="system-summary">{data?.ok ? <CheckCircle2 size={24} /> : <AlertTriangle size={24} />}<div><strong>{loading ? tx("Đang kiểm tra…", "Checking…") : error ? tx("Không gọi được API", "API unreachable") : data.ok ? tx("Tất cả thành phần đang hoạt động", "All services are operational") : tx("Có thành phần cần kiểm tra", "Some services need attention")}</strong></div><button onClick={reload}><RefreshCw className={loading ? "spin" : ""} size={16} /> {tx("Kiểm tra lại", "Check again")}</button></div>
    <ErrorNote error={error} />
    <div className="system-list">{rows.map(([name, detail, st, metric]) => <div key={name}><span className="system-icon"><Activity size={18} /></span><span><strong>{name}</strong><small>{detail}</small></span><b className={st.ok ? "" : "bad"}><i /> {st.ok ? tx("Sẵn sàng", "Ready") : tx("Lỗi", "Error")}</b><em>{metric}</em></div>)}</div>
  </Modal>;
}

// ---------------------------------------------------------------- modal nhỏ
export function FeedbackModal({ onClose, onSave }) {
  const { tx, labels } = useLanguage();
  const [reason, setReason] = useState("");
  const [comment, setComment] = useState("");
  return <Modal title={tx("Điều gì cần cải thiện?", "What should be improved?")} onClose={onClose}><div className="reason-list">{Object.entries(labels.feedback_reason).map(([value, label]) => <label key={value}><input type="radio" name="reason" checked={reason === value} onChange={() => setReason(value)} /><span><strong>{label}</strong></span></label>)}</div><label className="modal-field">{tx("Ghi chú", "Comment")}<textarea value={comment} onChange={(e) => setComment(e.target.value)} placeholder={tx("Không bắt buộc", "Optional")} /></label><div className="modal-actions"><button className="secondary-button" onClick={onClose}>{tx("Hủy", "Cancel")}</button><button className="primary-button" disabled={!reason} onClick={() => onSave({ reason, comment: comment.trim() || null })}>{tx("Gửi phản hồi", "Submit feedback")}</button></div></Modal>;
}

export function RenameModal({ item, onClose, onSave }) {
  const { tx } = useLanguage();
  const [name, setName] = useState(item.title);
  return <Modal title={tx("Đổi tên cuộc trò chuyện", "Rename conversation")} onClose={onClose}><label className="modal-field">{tx("Tên cuộc trò chuyện", "Conversation title")}<input value={name} onChange={(e) => setName(e.target.value)} maxLength={120} autoFocus /></label><div className="modal-actions"><button className="secondary-button" onClick={onClose}>{tx("Hủy", "Cancel")}</button><button className="primary-button" onClick={() => onSave(name.trim())} disabled={!name.trim()}>{tx("Lưu", "Save")}</button></div></Modal>;
}

export function ConfirmModal({ title, onClose, onConfirm }) {
  const { tx } = useLanguage();
  return <Modal title={tx("Xác nhận xóa", "Confirm deletion")} subtitle={title} onClose={onClose}><div className="delete-warning"><Trash2 size={21} /> {tx("Hành động này không thể hoàn tác. Nhật ký hệ thống (log) không bị xóa.", "This cannot be undone. System logs are kept.")}</div><div className="modal-actions"><button className="secondary-button" onClick={onClose}>{tx("Hủy", "Cancel")}</button><button className="danger-button" onClick={onConfirm}>{tx("Xóa vĩnh viễn", "Delete permanently")}</button></div></Modal>;
}
