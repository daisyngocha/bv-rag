// Giao diện React (thiết kế Figma) nối Supabase (đăng nhập, lịch sử, cài đặt, danh mục, nhật ký) và
// FastAPI (hỏi đáp, quản trị). Phương thức theo docs/roadmap/7.DA1_MethodList_v2.xlsx (tầng Supabase + Client).
import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  Activity, AlertTriangle, ArrowUp, BookOpen, Check, ChevronDown, Clock3, Download, Eye, FileClock, History,
  LayoutDashboard, LogOut, Menu, MessageCirclePlus, MessagesSquare, Settings, ShieldCheck, Sparkles, UserRound,
  Users, X,
} from "lucide-react";
import { askStream } from "./lib/api";
import {
  deleteAllConversations, deleteConversation, getProfile, getSettings, listConversations, listProducts,
  listSampleQuestions, loadConversation, renameConversation, saveFeedback, saveSettings,
} from "./lib/data";
import { configError, supabase } from "./lib/supabase";
import { exportMarkdown, formatShort, initials, LABELS, maskPreview } from "./lib/util";
import { Answer, LanguageContext, NavButton, StreamingAnswer, useLanguage } from "./ui";
import {
  AccountsView, CatalogView, ConfigErrorScreen, ConfigurationView, ConfirmModal, DashboardView, FeedbackModal,
  HistoryView, LoginScreen, LogsView, RenameModal, SessionExpired, SettingsPanel, SystemModal, useDebounced,
  useNegativeBadge,
} from "./views";

const IDLE_SECONDS = 30 * 60;   // UC-AUTH-04: tự hết phiên sau 30 phút không thao tác
const DEFAULT_SETTINGS = { theme: "system", font_size: 14, citation_style: "inline", show_source_text: true, language: "vi", show_processing: false };

export default function FullApp() {
  const [session, setSession] = useState(undefined);   // undefined = đang kiểm tra
  const [profile, setProfile] = useState(null);
  const [authError, setAuthError] = useState("");
  const [busy, setBusy] = useState(false);
  const [loginLang, setLoginLang] = useState("vi");

  useEffect(() => {
    if (!supabase) return undefined;
    supabase.auth.getSession().then(({ data }) => setSession(data.session));
    const { data } = supabase.auth.onAuthStateChange((_event, s) => setSession(s));
    return () => data.subscription.unsubscribe();
  }, []);

  useEffect(() => {
    const uid = session?.user?.id;
    if (!uid) { setProfile(null); return; }
    if (profile?.id === uid) return;
    getProfile(uid).then((p) => {
      if (!p.is_active) {
        setAuthError("Tài khoản đã bị khóa. Liên hệ quản trị viên.");
        supabase.auth.signOut();
        return;
      }
      setProfile(p);
    }).catch((e) => setAuthError(e.message));
  }, [session?.user?.id]); // eslint-disable-line react-hooks/exhaustive-deps

  const login = async (email, password) => {
    setBusy(true); setAuthError("");
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    if (error) setAuthError(error.message === "Invalid login credentials" ? "Email hoặc mật khẩu không đúng." : error.message);
    setBusy(false);
  };

  const loginCtx = { language: loginLang, setLanguage: setLoginLang, tx: (vi, en) => (loginLang === "vi" ? vi : en), labels: LABELS[loginLang] };
  if (configError) return <ConfigErrorScreen message={configError} />;
  if (session === undefined || (session && !profile && !authError)) {
    return <div className="login-page"><div className="login-card"><span className="spinner" /> Đang tải…</div></div>;
  }
  if (!session || !profile) return <LanguageContext.Provider value={loginCtx}><LoginScreen onLogin={login} error={authError} busy={busy} /></LanguageContext.Provider>;
  return <Workspace key={profile.id} user={session.user} profile={profile} onLogout={async () => { await supabase.auth.signOut(); setProfile(null); }} />;
}

function Workspace({ user, profile, onLogout }) {
  const uid = user.id;
  // ---------- cài đặt cá nhân (PT-SET-01, 02): lưu sau 500 ms
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const settingsLoaded = useRef(false);
  const pendingPatch = useRef({});
  useEffect(() => {
    getSettings(uid).then((s) => { if (s) setSettings((cur) => ({ ...cur, ...s })); settingsLoaded.current = true; })
      .catch(() => { settingsLoaded.current = true; });
  }, [uid]);
  useEffect(() => {
    if (!settingsLoaded.current || !Object.keys(pendingPatch.current).length) return undefined;
    const t = setTimeout(() => {
      const patch = pendingPatch.current;
      pendingPatch.current = {};
      saveSettings(uid, patch).catch((e) => notify(e.message, "error"));
    }, 500);
    return () => clearTimeout(t);
  }, [settings, uid]); // eslint-disable-line react-hooks/exhaustive-deps
  const updateSettings = (patch) => { pendingPatch.current = { ...pendingPatch.current, ...patch }; setSettings((s) => ({ ...s, ...patch })); };

  const language = settings.language;
  const tx = useCallback((vi, en) => (language === "vi" ? vi : en), [language]);
  const ctx = useMemo(() => ({ language, tx, labels: LABELS[language] }), [language, tx]);

  // ---------- vai trò (PT-AUTH-03, 05: "Xem như Người dùng" chỉ đổi giao diện, quyền thật ở RLS/FastAPI)
  const [viewAsUser, setViewAsUser] = useState(false);
  const isAdmin = profile.role === "admin" && !viewAsUser;

  // ---------- giao diện chung
  const [view, setView] = useState("chat");
  const [mobileNav, setMobileNav] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [systemOpen, setSystemOpen] = useState(false);
  const [toast, setToast] = useState(null);
  const notify = useCallback((text, kind = "ok") => setToast({ text, kind }), []);
  useEffect(() => {
    if (!toast) return undefined;
    const t = setTimeout(() => setToast(null), toast.kind === "error" ? 5000 : 2200);
    return () => clearTimeout(t);
  }, [toast]);

  // ---------- hết phiên khi không thao tác (PT-AUTH-04)
  const [idleLeft, setIdleLeft] = useState(IDLE_SECONDS);
  const [expired, setExpired] = useState(false);
  const lastActive = useRef(Date.now());
  useEffect(() => {
    const touch = () => { lastActive.current = Date.now(); };
    const evs = ["pointerdown", "keydown", "wheel", "touchstart"];
    evs.forEach((e) => window.addEventListener(e, touch, { passive: true }));
    const t = setInterval(() => {
      const left = Math.max(0, IDLE_SECONDS - Math.floor((Date.now() - lastActive.current) / 1000));
      setIdleLeft(left);
      if (left === 0) setExpired(true);
    }, 1000);
    return () => { evs.forEach((e) => window.removeEventListener(e, touch)); clearInterval(t); };
  }, []);
  const continueSession = async () => {
    const { error } = await supabase.auth.refreshSession();
    if (error) { onLogout(); return; }
    lastActive.current = Date.now(); setIdleLeft(IDLE_SECONDS); setExpired(false);
  };

  // ---------- danh mục, câu hỏi mẫu (PT-CHAT-03, 04)
  const [products, setProducts] = useState([]);
  const [samples, setSamples] = useState([]);
  useEffect(() => {
    listProducts().then(setProducts).catch((e) => notify(e.message, "error"));
    listSampleQuestions().then((rows) => {
      const pick = [];
      for (const g of ["lookup", "table", "scenario", "compare"]) {
        const inGroup = rows.filter((r) => r.question_group === g);
        if (inGroup.length) pick.push(inGroup[Math.floor(Math.random() * inGroup.length)]);
      }
      setSamples(pick.length ? pick : rows.slice(0, 4));
    }).catch(() => {});
  }, [notify]);

  // ---------- lịch sử (PT-HIS-01, 02)
  const [history, setHistory] = useState([]);
  const [historyState, setHistoryState] = useState({ loading: true, error: null });
  const [historySearch, setHistorySearch] = useState("");
  const q = useDebounced(historySearch);
  const reloadHistory = useCallback(() => {
    setHistoryState((s) => ({ ...s, loading: true }));
    return listConversations(uid, { q }).then((rows) => { setHistory(rows); setHistoryState({ loading: false, error: null }); })
      .catch((e) => setHistoryState({ loading: false, error: e.message }));
  }, [uid, q]);
  useEffect(() => { reloadHistory(); }, [reloadHistory]);
  const [recent, setRecent] = useState([]);
  const reloadRecent = useCallback(() => listConversations(uid, { lim: 4 }).then(setRecent).catch(() => {}), [uid]);
  useEffect(() => { reloadRecent(); }, [reloadRecent]);
  const refreshLists = () => { reloadHistory(); reloadRecent(); };

  // ---------- hỏi đáp
  const [conversation, setConversation] = useState(null);   // { id, title }
  const [messages, setMessages] = useState([]);
  const [query, setQuery] = useState("");
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [scopeOpen, setScopeOpen] = useState(false);
  const [pending, setPending] = useState(null);   // { stage, text } khi đang trả lời
  const [openKey, setOpenKey] = useState(null);
  const [privacyMasked, setPrivacyMasked] = useState(false);
  const [feedbackFor, setFeedbackFor] = useState(null);
  const abortRef = useRef(null);
  const chatEnd = useRef(null);
  useEffect(() => { chatEnd.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, pending?.text]);

  const stopPending = () => { abortRef.current?.abort(); abortRef.current = null; setPending(null); };

  async function sendQuestion(text = query) {
    const raw = text.trim();
    if (raw.length < 3 || pending) return;
    const { text: masked, masked: hadPii } = maskPreview(raw);   // không gửi TTCN ra khỏi trình duyệt
    if (hadPii) setPrivacyMasked(true);
    const tempId = `tmp-${Date.now()}`;
    setMessages((m) => [...m, { id: tempId, role: "user", content: masked }]);
    setQuery(""); setScopeOpen(false);
    setPending({ stage: tx("Đang tìm trong tài liệu chính thức", "Searching official documents"), text: "" });
    const ctrl = new AbortController();
    abortRef.current = ctrl;
    try {
      const done = await askStream({
        question: masked,
        conversation_id: conversation?.id || null,
        product_filter: selectedProducts.length ? selectedProducts : null,
      }, ({ event, data }) => {
        if (event === "status") setPending((p) => p && { ...p, stage: language === "vi" ? data.message : (data.stage === "generate" ? "Writing the answer" : "Searching official documents") });
        if (event === "token") setPending((p) => p && { ...p, text: p.text + data.text });
      }, ctrl.signal);
      if (ctrl.signal.aborted) return;
      setMessages((m) => [
        ...m.map((x) => (x.id === tempId ? { ...x, id: done.question_id || tempId, content: done.question } : x)),
        { id: done.message_id || `tmp-a-${Date.now()}`, role: "assistant", content: done.answer, refused: done.refused,
          refusal_reason: done.refusal_reason, run_id: done.run_id, sources: done.sources || [], feedback: null },
      ]);
      if (done.conversation_id) setConversation({ id: done.conversation_id, title: done.title });
      if (!done.saved) notify(tx(`Câu trả lời chưa được lưu vào lịch sử: ${done.db_error || "lỗi không rõ"}`, `Answer not saved: ${done.db_error || "unknown error"}`), "error");
      refreshLists();
    } catch (e) {
      if (e.name === "AbortError") return;
      setMessages((m) => [...m, { id: `err-${Date.now()}`, role: "error", content: e.message }]);
      if (e.status === 401) notify(tx("Phiên đăng nhập hết hạn, vui lòng đăng nhập lại.", "Session expired, please sign in again."), "error");
    } finally {
      if (abortRef.current === ctrl) { abortRef.current = null; setPending(null); }
    }
  }

  function newChat() {
    stopPending();
    setMessages([]); setConversation(null); setOpenKey(null); setPrivacyMasked(false);
    setView("chat"); setMobileNav(false);
  }

  async function openConversation(item, { thenPrint = false } = {}) {
    stopPending();
    try {
      const msgs = await loadConversation(item.id);
      setMessages(msgs); setConversation({ id: item.id, title: item.title }); setOpenKey(null);
      setPrivacyMasked(msgs.some((m) => m.pii_masked));
      setView("chat"); setMobileNav(false);
      if (thenPrint) setTimeout(() => window.print(), 400);
    } catch (e) { notify(e.message, "error"); }
  }

  async function exportConversation(item) {
    try {
      const msgs = item ? await loadConversation(item.id) : messages.filter((m) => m.role !== "error");
      exportMarkdown(item?.title || conversation?.title, msgs);
      notify(tx("Đã xuất cuộc trò chuyện dạng Markdown", "Conversation exported as Markdown"));
    } catch (e) { notify(e.message, "error"); }
  }

  // PT-CHAT-05: đánh giá theo từng câu trả lời
  async function rate(message, rating, extra = {}) {
    try {
      await saveFeedback({ message_id: message.id, user_id: uid, rating, ...extra });
      setMessages((m) => m.map((x) => (x.id === message.id ? { ...x, feedback: { rating, reason: extra.reason || null } } : x)));
      notify(tx("Cảm ơn phản hồi của bạn", "Thanks for your feedback"));
    } catch (e) { notify(e.message, "error"); }
  }

  // ---------- đổi tên, xóa (PT-HIS-04…06)
  const [renameItem, setRenameItem] = useState(null);
  const [deleteItem, setDeleteItem] = useState(null);
  async function doRename(title) {
    try {
      await renameConversation(renameItem.id, title);
      if (conversation?.id === renameItem.id) setConversation((c) => ({ ...c, title }));
      setRenameItem(null); refreshLists(); notify(tx("Đã đổi tên", "Renamed"));
    } catch (e) { notify(e.message, "error"); }
  }
  async function doDelete() {
    try {
      if (deleteItem.all) await deleteAllConversations(uid); else await deleteConversation(deleteItem.id);
      if (deleteItem.all || conversation?.id === deleteItem.id) newChat();
      setDeleteItem(null); refreshLists(); notify(tx("Đã xóa", "Deleted"));
    } catch (e) { notify(e.message, "error"); }
  }

  const badge = useNegativeBadge(isAdmin);
  const mm = String(Math.floor(idleLeft / 60)).padStart(2, "0");
  const ss = String(idleLeft % 60).padStart(2, "0");
  const name = profile.display_name || profile.username;
  const themeClass = settings.theme === "system"
    ? (window.matchMedia?.("(prefers-color-scheme: dark)").matches ? "theme-dark theme-system" : "theme-light theme-system")
    : `theme-${settings.theme}`;

  return <LanguageContext.Provider value={ctx}>
    <div className={`full-app ${themeClass} ${settings.font_size >= 17 ? "large-text" : ""}`} style={{ "--app-font-size": `${settings.font_size}px` }}>
      <a className="skip-link" href="#page-content">{tx("Bỏ qua đến nội dung chính", "Skip to main content")}</a>
      <header className="topbar full-topbar">
        <button className="icon-button mobile-only" onClick={() => setMobileNav(true)} aria-label={tx("Mở menu", "Open menu")}><Menu size={22} /></button>
        <button className="brand brand-button" onClick={() => setView("chat")}>
          <img src="/baoviet-logo.png" alt="Bảo hiểm Bảo Việt" />
          <span className="brand-divider" />
          <span><strong>{tx("Trợ lý tư vấn sản phẩm bảo hiểm", "Insurance product advisory assistant")}</strong><small>{tx("Hỏi đáp có trích dẫn", "Citation-grounded answers")}</small></span>
        </button>
        <div className="topbar-actions">
          <button className="session-pill" onClick={continueSession} title={tx("Nhấn để gia hạn phiên", "Click to extend session")}><Clock3 size={15} /> {mm}:{ss}</button>
          <div className="profile-wrap">
            <button className="profile-button" onClick={() => setProfileOpen(!profileOpen)}>
              <span>{initials(name)}</span><span className="profile-copy"><strong>{name}</strong><small>{profile.role === "admin" ? (viewAsUser ? tx("Đang xem như Người dùng", "Viewing as User") : tx("Quản trị viên", "Administrator")) : tx("Người dùng", "User")}</small></span><ChevronDown size={16} />
            </button>
            {profileOpen && <div className="profile-menu">
              <div className="profile-menu-head"><strong>{name}</strong><small>{user.email}</small></div>
              {profile.role === "admin" && <button onClick={() => { setViewAsUser(!viewAsUser); setProfileOpen(false); setView("chat"); }}><Eye size={17} /> {viewAsUser ? tx("Trở lại Quản trị viên", "Back to Administrator") : tx("Xem như Người dùng", "View as User")}</button>}
              <button onClick={onLogout}><LogOut size={17} /> {tx("Đăng xuất", "Sign out")}</button>
            </div>}
          </div>
        </div>
      </header>

      <div className="workspace">
        <aside className={`sidebar full-sidebar ${mobileNav ? "mobile-open" : ""}`}>
          <div className="sidebar-top">
            <button className="new-chat" onClick={newChat}><MessageCirclePlus size={19} /><span>{tx("Cuộc trò chuyện mới", "New conversation")}</span></button>
            <button className="icon-button mobile-only" onClick={() => setMobileNav(false)} aria-label={tx("Đóng menu", "Close menu")}><X size={20} /></button>
          </div>
          <nav className="main-nav" aria-label={tx("Điều hướng chính", "Main navigation")}>
            <NavButton active={view === "chat"} icon={MessagesSquare} label={tx("Hỏi đáp", "Chat")} onClick={() => { setView("chat"); setMobileNav(false); }} />
            <NavButton active={view === "history"} icon={History} label={tx("Lịch sử chat", "Chat history")} onClick={() => { setView("history"); setMobileNav(false); }} />
            <NavButton active={view === "catalog"} icon={BookOpen} label={tx("Sản phẩm & tài liệu", "Products & documents")} onClick={() => { setView("catalog"); setMobileNav(false); }} />
            {isAdmin && <>
              <p className="nav-label">{tx("QUẢN TRỊ", "ADMINISTRATION")}</p>
              <NavButton active={view === "dashboard"} icon={LayoutDashboard} label="Dashboard" onClick={() => { setView("dashboard"); setMobileNav(false); }} />
              <NavButton active={view === "logs"} icon={FileClock} label={tx("Nhật ký truy vấn", "Query logs")} onClick={() => { setView("logs"); setMobileNav(false); }} badge={badge || null} />
              <NavButton active={view === "accounts"} icon={Users} label={tx("Quản lý tài khoản", "Account management")} onClick={() => { setView("accounts"); setMobileNav(false); }} />
              <NavButton active={view === "configuration"} icon={Settings} label={tx("Cấu hình", "Configuration")} onClick={() => { setView("configuration"); setMobileNav(false); }} />
            </>}
          </nav>
          <div className="sidebar-history-mini">
            <div className="section-label"><span>{tx("GẦN ĐÂY", "RECENT")}</span><button onClick={() => setView("history")}>{tx("Xem tất cả", "View all")}</button></div>
            {recent.map((item) => <button key={item.id} className={conversation?.id === item.id ? "active" : ""} onClick={() => openConversation(item)}><span>{item.title}</span><small>{formatShort(item.updated_at)}</small></button>)}
          </div>
          <div className="sidebar-footer">
            <button onClick={() => setSettingsOpen(true)}><Settings size={18} /><span>{tx("Cài đặt", "Settings")}</span></button>
            {isAdmin && <button onClick={() => setSystemOpen(true)}><Activity size={18} /><span>{tx("Trạng thái hệ thống", "System status")}</span></button>}
          </div>
        </aside>
        {mobileNav && <button className="mobile-scrim" onClick={() => setMobileNav(false)} aria-label={tx("Đóng menu", "Close menu")} />}

        <main id="page-content" className="page-area">
          {view === "chat" && <ChatView
            messages={messages} pending={pending} query={query} setQuery={setQuery} sendQuestion={sendQuestion}
            products={products} samples={samples} selectedProducts={selectedProducts} setSelectedProducts={setSelectedProducts}
            scopeOpen={scopeOpen} setScopeOpen={setScopeOpen} settings={settings} showDetails={isAdmin && settings.show_processing}
            openKey={openKey} setOpenKey={setOpenKey} privacyMasked={privacyMasked} setPrivacyMasked={setPrivacyMasked}
            conversation={conversation} onExport={() => exportConversation(null)} onStop={stopPending}
            onRate={(m) => rate(m, 1)} onRateDown={(m) => setFeedbackFor(m)} notify={notify} chatEnd={chatEnd} />}
          {view === "history" && <HistoryView items={history} loading={historyState.loading} error={historyState.error} reload={reloadHistory}
            search={historySearch} setSearch={setHistorySearch} onOpen={(item) => openConversation(item)} onRename={setRenameItem}
            onDelete={(item) => setDeleteItem(item)} onDeleteAll={() => setDeleteItem({ all: true, title: tx("Toàn bộ lịch sử của bạn", "All of your history") })}
            onExport={exportConversation} onPrint={(item) => openConversation(item, { thenPrint: true })} />}
          {view === "catalog" && <CatalogView />}
          {view === "dashboard" && isAdmin && <DashboardView />}
          {view === "logs" && isAdmin && <LogsView setToast={notify} />}
          {view === "accounts" && isAdmin && <AccountsView setToast={notify} me={uid} />}
          {view === "configuration" && isAdmin && <ConfigurationView setToast={notify} />}
        </main>
      </div>

      {settingsOpen && <SettingsPanel onClose={() => setSettingsOpen(false)} settings={settings} update={updateSettings} isAdmin={isAdmin} />}
      {systemOpen && isAdmin && <SystemModal onClose={() => setSystemOpen(false)} />}
      {feedbackFor && <FeedbackModal onClose={() => setFeedbackFor(null)} onSave={({ reason, comment }) => { rate(feedbackFor, -1, { reason, comment }); setFeedbackFor(null); }} />}
      {renameItem && <RenameModal item={renameItem} onClose={() => setRenameItem(null)} onSave={doRename} />}
      {deleteItem && <ConfirmModal title={deleteItem.title} onClose={() => setDeleteItem(null)} onConfirm={doDelete} />}
      {expired && <SessionExpired onContinue={continueSession} onLogout={onLogout} />}
      {toast && <div className={`toast ${toast.kind === "error" ? "toast-error" : ""}`} role="status">{toast.kind === "error" ? <AlertTriangle size={17} /> : <Check size={17} />} {toast.text}</div>}
    </div>
  </LanguageContext.Provider>;
}

function ChatView(props) {
  const { tx, labels } = useLanguage();
  const {
    messages, pending, query, setQuery, sendQuestion, products, samples, selectedProducts, setSelectedProducts,
    scopeOpen, setScopeOpen, settings, showDetails, openKey, setOpenKey, privacyMasked, setPrivacyMasked,
    conversation, onExport, onStop, onRate, onRateDown, notify, chatEnd,
  } = props;
  const empty = !messages.length && !pending;
  const toggleProduct = (code) => setSelectedProducts(selectedProducts.includes(code) ? selectedProducts.filter((x) => x !== code) : [...selectedProducts, code]);
  return <div className="chat-page">
    <div className="page-header compact">
      <div><div className="page-kicker"><span /> RAG</div><h1>{conversation?.title || (messages.length ? tx("Cuộc trò chuyện hiện tại", "Current conversation") : tx("Trợ lý tra cứu sản phẩm bảo hiểm", "Insurance product assistant"))}</h1></div>
      <div className="header-actions">{messages.length > 0 && !pending && <button className="secondary-button" onClick={onExport}><Download size={16} /> {tx("Xuất Markdown", "Export Markdown")}</button>}</div>
    </div>
    <section className="chat-scroll full-chat-scroll" aria-live="polite">
      {empty ? <div className="welcome">
        <div className="welcome-mark"><Sparkles size={26} /></div>
        <p className="welcome-kicker">TRỢ LÝ BẢO VIỆT</p>
        <h2>{tx("Bạn muốn tìm hiểu điều gì?", "What would you like to know?")}</h2>
        <p className="welcome-copy">{tx("Tra cứu quy tắc, quyền lợi và biểu phí từ tài liệu sản phẩm chính thức.", "Search official product rules, benefits, and premium tables.")}</p>
        <div className="sample-grid">{samples.map((s) => <button key={s.qid} onClick={() => sendQuestion(s.question)}><span>{labels.question_group[s.question_group]}</span><strong>{s.question}</strong><small>{s.products?.join(", ")}</small><ArrowUp size={18} /></button>)}</div>
      </div> : <div className="conversation">
        {privacyMasked && <div className="privacy-banner"><ShieldCheck size={17} /><span>{tx("Thông tin nhạy cảm đã được tự động che trước khi gửi và lưu lịch sử.", "Sensitive information was masked before sending and saving.")}</span><button onClick={() => setPrivacyMasked(false)} aria-label="Đóng"><X size={16} /></button></div>}
        {messages.map((m) => m.role === "user"
          ? <div className="user-row" key={m.id}><div className="user-bubble">{m.content}</div><div className="avatar user-avatar"><UserRound size={17} /></div></div>
          : m.role === "error"
            ? <div className="assistant-row" key={m.id}><div className="avatar assistant-avatar"><AlertTriangle size={17} /></div><div className="answer-wrap"><div className="error-note"><span>{m.content}</span></div></div></div>
            : <Answer key={m.id} message={m} settings={settings} showDetails={showDetails} openKey={openKey} setOpenKey={setOpenKey} onRate={onRate} onRateDown={onRateDown} setToast={notify} />)}
        {pending && <StreamingAnswer text={pending.text} stage={pending.stage} />}
        <div ref={chatEnd} />
      </div>}
    </section>
    <div className="composer-zone">
      <div className="scope-row">
        <div className="scope-wrap">
          <button className="scope-button" onClick={() => setScopeOpen(!scopeOpen)}><BookOpen size={16} />{selectedProducts.length ? tx(`Đã chọn ${selectedProducts.length} sản phẩm`, `${selectedProducts.length} products selected`) : tx("Tự động nhận diện sản phẩm", "Detect products automatically")}<ChevronDown size={16} /></button>
          {scopeOpen && <div className="scope-menu"><div><strong>{tx("Phạm vi sản phẩm", "Product scope")}</strong>{selectedProducts.length > 0 && <button className="text-button" onClick={() => setSelectedProducts([])}>{tx("Bỏ chọn", "Clear")}</button>}</div>
            {products.map((p) => <button key={p.product_code} onClick={() => toggleProduct(p.product_code)}><span className={`checkbox ${selectedProducts.includes(p.product_code) ? "checked" : ""}`}>{selectedProducts.includes(p.product_code) && <Check size={13} />}</span><span><strong>{p.product_name}</strong><small>{p.product_code}</small></span></button>)}</div>}
        </div>
        <span className="privacy-note"><ShieldCheck size={15} /> {tx("Tự động che thông tin cá nhân", "Personal information is masked automatically")}</span>
      </div>
      <div className="composer">
        <textarea value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendQuestion(); } }} placeholder={tx("Hỏi về quy tắc, quyền lợi, biểu phí…", "Ask about rules, benefits, or premiums…")} rows={1} maxLength={2000} />
        <div className="composer-footer"><span>{pending ? <button className="text-button" onClick={onStop}>{tx("Dừng", "Stop")}</button> : tx("Enter để gửi · Shift + Enter để xuống dòng", "Enter to send · Shift + Enter for a new line")}</span><button onClick={() => sendQuestion()} disabled={query.trim().length < 3 || Boolean(pending)} aria-label={tx("Gửi câu hỏi", "Send question")}><ArrowUp size={20} /></button></div>
      </div>
      <p className="disclaimer">{tx("Thông tin chỉ mang tính tham khảo. Căn cứ cuối cùng là quy tắc và hợp đồng được phát hành.", "For reference only. Issued policy terms and contracts remain the final authority.")}</p>
    </div>
  </div>;
}
