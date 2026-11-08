import React, { createContext, useContext, useEffect, useMemo, useRef, useState } from "react";
import {
  Activity,
  ArrowLeft,
  ArrowUp,
  BarChart3,
  BookOpen,
  Bot,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  Clock3,
  Copy,
  Download,
  ExternalLink,
  Eye,
  FileClock,
  FileText,
  Gauge,
  History,
  KeyRound,
  LayoutDashboard,
  ListFilter,
  LockKeyhole,
  LogOut,
  Menu,
  MessageCirclePlus,
  MessagesSquare,
  Moon,
  MoreHorizontal,
  Pencil,
  Plus,
  RefreshCw,
  Search,
  Settings,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Sun,
  ThumbsDown,
  ThumbsUp,
  Trash2,
  UserCog,
  UserRound,
  Users,
  X,
} from "lucide-react";
import {
  ACCOUNTS,
  APP_SETTINGS,
  CHUNKS,
  CONVERSATIONS,
  CONVERSATION_MESSAGES,
  DATA_VERSIONS,
  DOCUMENTS,
  ENUM_LABELS,
  EVAL_RESULTS,
  MESSAGE_CITATIONS,
  PIPELINE_CONFIGS,
  PRODUCTS,
  QUERY_LOGS,
  RETRIEVAL_LOGS,
  SAMPLE_QUESTIONS,
  SYSTEMS,
  TRACE,
} from "./dataDictionaryMock";

const INITIAL_HISTORY = CONVERSATIONS.map((conversation) => ({
  ...conversation,
  preview: CONVERSATION_MESSAGES[conversation.id],
  time: new Date(conversation.updated_at).toLocaleString("vi-VN", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" }),
}));

const SOURCES = MESSAGE_CITATIONS.map((citation) => {
  const chunk = CHUNKS.find((item) => item.data_version === citation.data_version && item.chunk_id === citation.chunk_id);
  const document = DOCUMENTS.find((item) => item.id === chunk?.document_id);
  return {
    message_id: citation.message_id,
    ord: citation.ord,
    data_version: citation.data_version,
    chunk_id: citation.chunk_id,
    section_path: chunk?.section_path,
    page: chunk?.page,
    text: chunk?.text,
    source_file: document?.source_file,
    url: document?.url,
  };
});

const LanguageContext = createContext({ language: "vi", setLanguage: () => {}, tx: (vi) => vi });
const useLanguage = () => useContext(LanguageContext);
const EN_LABELS = {
  question_group: { lookup: "Rule lookup", table: "Premium table", compare: "Comparison", scenario: "Scenario" },
  line: { suc_khoe: "Health", benh_hiem_ngheo: "Critical illness", du_lich: "Travel" },
  doc_type: { quy_tac: "Policy rules", dieu_khoan: "Terms", bang_phi: "Premium table", bang_quyen_loi: "Benefits table", brochure: "Brochure", faq: "FAQ" },
};

export default function FullApp() {
  const [authenticated, setAuthenticated] = useState(true);
  const [role, setRole] = useState("admin");
  const [profileOpen, setProfileOpen] = useState(false);
  const [view, setView] = useState("chat");
  const [mobileNav, setMobileNav] = useState(false);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [systemOpen, setSystemOpen] = useState(false);
  const [sessionSeconds, setSessionSeconds] = useState(29 * 60 + 58);
  const [sessionExpired, setSessionExpired] = useState(false);
  const [theme, setTheme] = useState("system");
  const [language, setLanguage] = useState("vi");
  const [fontSize, setFontSize] = useState(14);
  const [citationMode, setCitationMode] = useState("inline");
  const [showExcerpts, setShowExcerpts] = useState(true);
  const [showDetails, setShowDetails] = useState(false);
  const [pipeline, setPipeline] = useState(APP_SETTINGS.value.config);
  const [history, setHistory] = useState(INITIAL_HISTORY);
  const [activeHistory, setActiveHistory] = useState(null);
  const [historySearch, setHistorySearch] = useState("");
  const [historyMenu, setHistoryMenu] = useState(null);
  const [renameItem, setRenameItem] = useState(null);
  const [deleteItem, setDeleteItem] = useState(null);
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [scopeOpen, setScopeOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [streamText, setStreamText] = useState("");
  const [sourceOpen, setSourceOpen] = useState(null);
  const [feedback, setFeedback] = useState(null);
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [privacyMasked, setPrivacyMasked] = useState(false);
  const [toast, setToast] = useState("");
  const chatEnd = useRef(null);

  useEffect(() => {
    if (!authenticated || sessionExpired) return undefined;
    const timer = setInterval(() => {
      setSessionSeconds((value) => {
        if (value <= 1) {
          setSessionExpired(true);
          return 0;
        }
        return value - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [authenticated, sessionExpired]);

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamText]);

  useEffect(() => {
    if (!toast) return undefined;
    const timer = setTimeout(() => setToast(""), 2200);
    return () => clearTimeout(timer);
  }, [toast]);

  const filteredHistory = useMemo(
    () => history.filter((item) => `${item.title} ${item.preview}`.toLowerCase().includes(historySearch.toLowerCase())),
    [history, historySearch],
  );

  function maskSensitive(text) {
    let masked = text
      .replace(/\b\d{9,12}\b/g, "[ĐÃ CHE SỐ ĐỊNH DANH]")
      .replace(/\b(?:0|\+84)\d{9}\b/g, "[ĐÃ CHE SĐT]")
      .replace(/[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/gi, "[ĐÃ CHE EMAIL]");
    if (masked !== text) setPrivacyMasked(true);
    return masked;
  }

  function sendQuestion(question = query) {
    const raw = question.trim();
    const clean = maskSensitive(raw);
    if (!clean || loading) return;
    const userMessageId = crypto.randomUUID();
    const conversationId = activeHistory || crypto.randomUUID();
    setMessages((current) => [...current, {
      id: userMessageId,
      conversation_id: conversationId,
      reply_to_id: null,
      role: "user",
      content: clean,
      pii_masked: clean !== raw,
      product_filter: selectedProducts.length ? selectedProducts : null,
      refused: false,
      refusal_reason: null,
      run_id: null,
      created_at: new Date().toISOString(),
    }]);
    setQuery("");
    setLoading(true);
    setStreamText("");
    setFeedback(null);
    if (!messages.length) {
      const now = new Date().toISOString();
      setActiveHistory(conversationId);
      setHistory((current) => [
        { id: conversationId, user_id: ACCOUNTS[0].id, title: clean.slice(0, 48), title_is_custom: false, created_at: now, updated_at: now, preview: clean, time: formatDateTime(now) },
        ...current,
      ]);
    }
    const outOfScope = /ô tô|pvi|hợp đồng của tôi|tính phí cho tôi/i.test(clean);
    const response = outOfScope
      ? "Tài liệu hiện có không đề cập đủ nội dung này để đưa ra câu trả lời đáng tin cậy. Bạn có thể hỏi về quy tắc, quyền lợi, biểu phí hoặc điều kiện của các sản phẩm đang có trong kho tài liệu."
      : "Theo Quy tắc bảo hiểm sức khỏe Bảo Việt An Gia, Bảo Việt xem xét và giải quyết quyền lợi trong vòng **15 ngày làm việc** kể từ khi nhận đủ hồ sơ yêu cầu trả tiền bảo hiểm hợp lệ. [1]\n\nĐể tránh chậm trễ, người được bảo hiểm hoặc người thụ hưởng cần nộp đầy đủ chứng từ theo danh mục áp dụng cho từng quyền lợi. [2]";
    setTimeout(() => {
      setLoading(false);
      let index = 0;
      const stream = setInterval(() => {
        index += 4;
        setStreamText(response.slice(0, index));
        if (index >= response.length) {
          clearInterval(stream);
          setStreamText("");
          setMessages((current) => [
            ...current,
            {
              id: crypto.randomUUID(),
              conversation_id: conversationId,
              reply_to_id: userMessageId,
              role: "assistant",
              content: response,
              pii_masked: false,
              product_filter: null,
              refused: outOfScope,
              refusal_reason: outOfScope ? "ngoai_pham_vi" : null,
              run_id: `${pipeline}_demo_20261120-1042`,
              created_at: new Date().toISOString(),
              sources: outOfScope ? [] : SOURCES,
            },
          ]);
        }
      }, 18);
    }, 700);
  }

  function newChat() {
    setMessages([]);
    setActiveHistory(null);
    setFeedback(null);
    setView("chat");
    setMobileNav(false);
  }

  function openHistory(item) {
    setActiveHistory(item.id);
    setMessages([
      { id: crypto.randomUUID(), conversation_id: item.id, reply_to_id: null, role: "user", content: item.preview, pii_masked: false, product_filter: null, refused: false, refusal_reason: null, run_id: null, created_at: item.created_at },
      { id: crypto.randomUUID(), conversation_id: item.id, reply_to_id: null, role: "assistant", content: "Đây là snapshot câu trả lời đã lưu tại thời điểm truy vấn. Nội dung không được chạy lại để bảo toàn cấu hình và nguồn trích dẫn.", pii_masked: false, product_filter: null, refused: false, refusal_reason: null, run_id: `${pipeline}_demo_20261120-1042`, created_at: item.updated_at, sources: SOURCES },
    ]);
    setView("chat");
    setHistoryMenu(null);
  }

  function downloadConversation() {
    const body = messages.map((m) => `## ${m.role === "user" ? "Người dùng" : "Trợ lý"}\n\n${m.content}`).join("\n\n");
    const sourceList = SOURCES.map((s) => `- [${s.ord}] ${s.source_file}, ${s.section_path}, trang ${s.page} · ${s.data_version}/${s.chunk_id}`).join("\n");
    const blob = new Blob([`# Cuộc trò chuyện Bảo Việt\n\n${body}\n\n## Nguồn\n${sourceList}`], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "cuoc-tro-chuyen-bao-viet.md";
    anchor.click();
    URL.revokeObjectURL(url);
    setToast("Đã xuất cuộc trò chuyện dạng Markdown");
  }

  function printConversation() {
    window.print();
    setToast("Đã mở hộp thoại in / lưu PDF");
  }

  function login(event) {
    event.preventDefault();
    setAuthenticated(true);
    setSessionExpired(false);
    setSessionSeconds(29 * 60 + 59);
  }

  function logout() {
    setAuthenticated(false);
    setProfileOpen(false);
    setMessages([]);
  }

  const tx = (vi, en) => language === "vi" ? vi : en;

  if (!authenticated) return <LanguageContext.Provider value={{ language, setLanguage, tx }}><LoginScreen onLogin={login} /></LanguageContext.Provider>;

  const mm = String(Math.floor(sessionSeconds / 60)).padStart(2, "0");
  const ss = String(sessionSeconds % 60).padStart(2, "0");

  return (
    <LanguageContext.Provider value={{ language, setLanguage, tx }}>
    <div className={`full-app theme-${theme} ${fontSize >= 17 ? "large-text" : ""}`} style={{ "--app-font-size": `${fontSize}px` }}>
      <a className="skip-link" href="#page-content">Bỏ qua đến nội dung chính</a>
      <header className="topbar full-topbar">
        <button className="icon-button mobile-only" onClick={() => setMobileNav(true)} aria-label="Mở menu"><Menu size={22} /></button>
        <button className="brand brand-button" onClick={() => setView("chat")}>
          <img src="/baoviet-logo.png" alt="Bảo hiểm Bảo Việt" />
          <span className="brand-divider" />
          <span><strong>{tx("Trợ lý sản phẩm", "Product assistant")}</strong><small>{tx("Hỏi đáp có trích dẫn", "Citation-grounded answers")}</small></span>
        </button>
        <div className="topbar-actions">
          <button className="status-pill" onClick={() => setSystemOpen(true)}><span /> {tx("Hệ thống sẵn sàng", "System ready")}</button>
          <button className="session-pill" onClick={() => setSessionSeconds(29 * 60 + 59)} title="Nhấn để gia hạn phiên"><Clock3 size={15} /> {mm}:{ss}</button>
          <button className="icon-button" onClick={() => setSystemOpen(true)} aria-label="Trợ giúp"><CircleHelp size={20} /></button>
          <button className="icon-button" onClick={() => setSettingsOpen(true)} aria-label="Cài đặt"><Settings size={20} /></button>
          <div className="profile-wrap">
            <button className="profile-button" onClick={() => setProfileOpen(!profileOpen)}>
              <span>D1</span><span className="profile-copy"><strong>{language === "vi" ? ACCOUNTS[0].display_name : "Demo user 01"}</strong><small>{role === "admin" ? tx("Quản trị viên", "Administrator") : tx("Người dùng", "User")}</small></span><ChevronDown size={16} />
            </button>
            {profileOpen && (
              <div className="profile-menu">
                <div className="profile-menu-head"><strong>{ACCOUNTS[0].username}</strong><small>{tx("Phiên demo · không lưu dữ liệu cá nhân", "Demo session · no personal data stored")}</small></div>
                <button onClick={() => { setRole(role === "admin" ? "user" : "admin"); setProfileOpen(false); setView("chat"); setToast(role === "admin" ? tx("Đã chuyển sang Người dùng", "Switched to User") : tx("Đã chuyển sang Quản trị viên", "Switched to Administrator")); }}><UserCog size={17} /> {role === "admin" ? tx("Chuyển sang Người dùng", "Switch to User") : tx("Chuyển sang Quản trị viên", "Switch to Administrator")}</button>
                <button onClick={logout}><LogOut size={17} /> {tx("Đăng xuất", "Sign out")}</button>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="workspace">
        <aside className={`sidebar full-sidebar ${mobileNav ? "mobile-open" : ""}`}>
          <div className="sidebar-top">
            <button className="new-chat" onClick={newChat}><MessageCirclePlus size={19} /><span>{tx("Cuộc trò chuyện mới", "New conversation")}</span></button>
            <button className="icon-button mobile-only" onClick={() => setMobileNav(false)} aria-label="Đóng menu"><X size={20} /></button>
          </div>
          <nav className="main-nav" aria-label="Điều hướng chính">
            <NavButton active={view === "chat"} icon={MessagesSquare} label={tx("Hỏi đáp", "Chat")} onClick={() => setView("chat")} />
            <NavButton active={view === "history"} icon={History} label={tx("Lịch sử chat", "Chat history")} onClick={() => setView("history")} />
            <NavButton active={view === "catalog"} icon={BookOpen} label={tx("Sản phẩm & tài liệu", "Products & documents")} onClick={() => setView("catalog")} />
            {role === "admin" && (
              <>
                <p className="nav-label">{tx("QUẢN TRỊ", "ADMINISTRATION")}</p>
                <NavButton active={view === "dashboard"} icon={LayoutDashboard} label="Dashboard" onClick={() => setView("dashboard")} />
                <NavButton active={view === "logs"} icon={FileClock} label={tx("Nhật ký truy vấn", "Query logs")} onClick={() => setView("logs")} badge="4" />
                <NavButton active={view === "accounts"} icon={Users} label={tx("Tài khoản demo", "Demo accounts")} onClick={() => setView("accounts")} />
                <NavButton active={view === "configuration"} icon={Settings} label={tx("Cấu hình", "Configuration")} onClick={() => setView("configuration")} />
                <NavButton active={view === "compare"} icon={SlidersHorizontal} label={tx("So sánh cấu hình", "Compare configurations")} onClick={() => setView("compare")} />
              </>
            )}
          </nav>
          <div className="sidebar-history-mini">
            <div className="section-label"><span>{tx("GẦN ĐÂY", "RECENT")}</span><button onClick={() => setView("history")}>{tx("Xem tất cả", "View all")}</button></div>
            {history.slice(0, 4).map((item) => (
              <button key={item.id} className={activeHistory === item.id ? "active" : ""} onClick={() => openHistory(item)}>
                <span>{item.title}</span><small>{item.time}</small>
              </button>
            ))}
          </div>
          <div className="sidebar-footer">
            <button onClick={() => setSettingsOpen(true)}><Settings size={18} /><span>{tx("Cài đặt", "Settings")}</span></button>
            <button onClick={() => setSystemOpen(true)}><Activity size={18} /><span>{tx("Trạng thái hệ thống", "System status")}</span></button>
          </div>
        </aside>
        {mobileNav && <button className="mobile-scrim" onClick={() => setMobileNav(false)} aria-label="Đóng menu" />}

        <main id="page-content" className="page-area">
          {view === "chat" && (
            <ChatView
              messages={messages}
              loading={loading}
              streamText={streamText}
              query={query}
              setQuery={setQuery}
              sendQuestion={sendQuestion}
              selectedProducts={selectedProducts}
              setSelectedProducts={setSelectedProducts}
              scopeOpen={scopeOpen}
              setScopeOpen={setScopeOpen}
              pipeline={pipeline}
              setPipeline={setPipeline}
              role={role}
              sourceOpen={sourceOpen}
              setSourceOpen={setSourceOpen}
              feedback={feedback}
              setFeedback={setFeedback}
              setFeedbackOpen={setFeedbackOpen}
              privacyMasked={privacyMasked}
              setPrivacyMasked={setPrivacyMasked}
              citationMode={citationMode}
              showExcerpts={showExcerpts}
              showDetails={showDetails}
              setToast={setToast}
              downloadConversation={downloadConversation}
              chatEnd={chatEnd}
            />
          )}
          {view === "history" && (
            <HistoryView
              items={filteredHistory}
              search={historySearch}
              setSearch={setHistorySearch}
              openHistory={openHistory}
              menu={historyMenu}
              setMenu={setHistoryMenu}
              setRenameItem={setRenameItem}
              setDeleteItem={setDeleteItem}
              exportItem={downloadConversation}
              printItem={printConversation}
              clearAll={() => setDeleteItem({ all: true, title: "toàn bộ lịch sử" })}
            />
          )}
          {view === "catalog" && <CatalogView />}
          {view === "dashboard" && role === "admin" && <DashboardView setToast={setToast} />}
          {view === "logs" && role === "admin" && <LogsView setToast={setToast} />}
          {view === "accounts" && role === "admin" && <AccountsView setToast={setToast} />}
          {view === "configuration" && role === "admin" && <ConfigurationView pipeline={pipeline} setPipeline={setPipeline} setToast={setToast} />}
          {view === "compare" && role === "admin" && <CompareView />}
        </main>
      </div>

      {settingsOpen && (
        <SettingsPanel
          onClose={() => setSettingsOpen(false)}
          theme={theme}
          setTheme={setTheme}
          fontSize={fontSize}
          setFontSize={setFontSize}
          citationMode={citationMode}
          setCitationMode={setCitationMode}
          showExcerpts={showExcerpts}
          setShowExcerpts={setShowExcerpts}
          showDetails={showDetails}
          setShowDetails={setShowDetails}
          role={role}
        />
      )}
      {systemOpen && <SystemModal onClose={() => setSystemOpen(false)} />}
      {feedbackOpen && <FeedbackModal onClose={() => setFeedbackOpen(false)} onSave={() => { setFeedback("down"); setFeedbackOpen(false); setToast("Đã lưu lý do phản hồi"); }} />}
      {renameItem && <RenameModal item={renameItem} onClose={() => setRenameItem(null)} onSave={(name) => { setHistory((current) => current.map((item) => item.id === renameItem.id ? { ...item, title: name, title_is_custom: true, updated_at: new Date().toISOString() } : item)); setRenameItem(null); setToast("Đã cập nhật conversations.title và title_is_custom"); }} />}
      {deleteItem && <ConfirmModal item={deleteItem} onClose={() => setDeleteItem(null)} onConfirm={() => { setHistory((current) => deleteItem.all ? [] : current.filter((item) => item.id !== deleteItem.id)); setDeleteItem(null); setToast("Đã xóa lịch sử"); }} />}
      {sessionExpired && <SessionExpired onLogin={() => { setSessionExpired(false); setSessionSeconds(29 * 60 + 59); }} onLogout={logout} />}
      {toast && <div className="toast"><Check size={17} /> {toast}</div>}
    </div>
    </LanguageContext.Provider>
  );
}

function NavButton({ active, icon: Icon, label, onClick, badge }) {
  return <button className={`nav-button ${active ? "active" : ""}`} onClick={onClick}><Icon size={18} /><span>{label}</span>{badge && <b>{badge}</b>}</button>;
}

function LoginScreen({ onLogin }) {
  const { tx } = useLanguage();
  return (
    <div className="login-page">
      <div className="login-brand">
        <img src="/baoviet-logo.png" alt="Bảo hiểm Bảo Việt" />
        <div><span>{tx("TRỢ LÝ SẢN PHẨM BẢO HIỂM", "INSURANCE PRODUCT ASSISTANT")}</span><h1>{tx("Tra cứu nhanh. Căn cứ rõ ràng.", "Fast answers. Clear sources.")}</h1></div>
        <div className="login-trust"><ShieldCheck size={19} /><span>{tx("Chỉ sử dụng tài liệu công khai", "Public documents only")}</span></div>
      </div>
      <form className="login-card" onSubmit={onLogin}>
        <div className="login-icon"><KeyRound size={23} /></div>
        <p className="eyebrow-text">{tx("PHIÊN BẢN DEMO", "DEMO VERSION")}</p>
        <h2>{tx("Đăng nhập hệ thống", "Sign in")}</h2>
        <label>Email<input defaultValue="demo01@bv-rag.local" autoComplete="username" /></label>
        <label>{tx("Mật khẩu", "Password")}<input type="password" defaultValue="baoviet-demo" autoComplete="current-password" /></label>
        <div className="login-note"><LockKeyhole size={15} /> {tx("Phiên tự động hết hạn sau 30 phút.", "Session expires after 30 minutes.")}</div>
        <button type="submit">{tx("Đăng nhập", "Sign in")} <ArrowUp size={18} /></button>
      </form>
    </div>
  );
}

function ChatView(props) {
  const { tx, language } = useLanguage();
  const {
    messages, loading, streamText, query, setQuery, sendQuestion, selectedProducts, setSelectedProducts,
    scopeOpen, setScopeOpen, pipeline, setPipeline, role, sourceOpen, setSourceOpen, feedback,
    setFeedback, setFeedbackOpen, privacyMasked, setPrivacyMasked, citationMode, showExcerpts,
    showDetails, setToast, downloadConversation, chatEnd,
  } = props;
  return (
    <div className="chat-page">
      <div className="page-header compact">
        <div><div className="page-kicker"><span /> RAG</div><h1>{messages.length ? tx("Cuộc trò chuyện hiện tại", "Current conversation") : tx("Trợ lý tra cứu sản phẩm bảo hiểm", "Insurance product assistant")}</h1></div>
        <div className="header-actions">
          {messages.length > 0 && <button className="secondary-button" onClick={downloadConversation}><Download size={16} /> {tx("Xuất Markdown", "Export Markdown")}</button>}
        </div>
      </div>
      <section className="chat-scroll full-chat-scroll" aria-live="polite">
        {!messages.length && !streamText ? (
          <div className="welcome">
            <div className="welcome-mark"><Sparkles size={26} /></div>
            <p className="welcome-kicker">TRỢ LÝ BẢO VIỆT</p>
            <h2>{tx("Bạn muốn tìm hiểu điều gì?", "What would you like to know?")}</h2>
            <p className="welcome-copy">{tx("Tra cứu quy tắc, quyền lợi và biểu phí từ tài liệu sản phẩm chính thức.", "Search official product rules, benefits, and premium tables.")}</p>
            <div className="sample-grid">{SAMPLE_QUESTIONS.filter((item) => item.is_active).map((item) => <button key={item.qid} onClick={() => sendQuestion(item.question)}><span>{language === "vi" ? ENUM_LABELS.question_group[item.question_group] : EN_LABELS.question_group[item.question_group]}</span><strong>{item.question}</strong><small>{item.products?.join(", ")}</small><ArrowUp size={18} /></button>)}</div>
          </div>
        ) : (
          <div className="conversation">
            {privacyMasked && <div className="privacy-banner"><ShieldCheck size={17} /><span>{tx("Thông tin nhạy cảm đã được tự động che trước khi lưu lịch sử.", "Sensitive information was masked before saving.")}</span><button onClick={() => setPrivacyMasked(false)}><X size={16} /></button></div>}
            {messages.map((message, index) => message.role === "user"
              ? <div className="user-row" key={message.id || index}><div className="user-bubble">{message.content}</div><div className="avatar user-avatar"><UserRound size={17} /></div></div>
              : <Answer key={index} message={message} sourceOpen={sourceOpen} setSourceOpen={setSourceOpen} feedback={feedback} setFeedback={setFeedback} setFeedbackOpen={setFeedbackOpen} citationMode={citationMode} showExcerpts={showExcerpts} showDetails={showDetails && role === "admin"} setToast={setToast} pipeline={pipeline} />
            )}
            {(loading || streamText) && <StreamingAnswer text={streamText} loading={loading} />}
            <div ref={chatEnd} />
          </div>
        )}
      </section>
      <div className="composer-zone">
        <div className="scope-row">
          <div className="scope-wrap">
            <button className="scope-button" onClick={() => setScopeOpen(!scopeOpen)}><BookOpen size={16} />{selectedProducts.length ? tx(`Đã chọn ${selectedProducts.length} sản phẩm`, `${selectedProducts.length} products selected`) : tx("Tự động nhận diện sản phẩm", "Detect products automatically")}<ChevronDown size={16} /></button>
            {scopeOpen && <div className="scope-menu"><div><strong>{tx("Phạm vi sản phẩm", "Product scope")}</strong></div>{PRODUCTS.filter((p) => p.is_active).map((p) => <button key={p.product_code} onClick={() => setSelectedProducts(selectedProducts.includes(p.product_code) ? selectedProducts.filter((x) => x !== p.product_code) : [...selectedProducts, p.product_code])}><span className={`checkbox ${selectedProducts.includes(p.product_code) ? "checked" : ""}`}>{selectedProducts.includes(p.product_code) && <Check size={13} />}</span><span><strong>{p.product_name}</strong><small>{p.product_code}</small></span></button>)}</div>}
          </div>
          <span className="privacy-note"><ShieldCheck size={15} /> {tx("Tự động che thông tin cá nhân", "Personal information is masked automatically")}</span>
        </div>
        <div className="composer">
          <textarea value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendQuestion(); } }} placeholder={tx("Hỏi về quy tắc, quyền lợi, biểu phí…", "Ask about rules, benefits, or premiums…")} rows={1} />
          <div className="composer-footer"><span>{tx("Enter để gửi · Shift + Enter để xuống dòng", "Enter to send · Shift + Enter for a new line")}</span><button onClick={() => sendQuestion()} disabled={!query.trim() || loading} aria-label={tx("Gửi câu hỏi", "Send question")}><ArrowUp size={20} /></button></div>
        </div>
        <p className="disclaimer">{tx("Thông tin chỉ mang tính tham khảo. Căn cứ cuối cùng là quy tắc và hợp đồng được phát hành.", "For reference only. Issued policy terms and contracts remain the final authority.")}</p>
      </div>
    </div>
  );
}

function Answer({ message, sourceOpen, setSourceOpen, feedback, setFeedback, setFeedbackOpen, citationMode, showExcerpts, showDetails, setToast, pipeline }) {
  const { tx } = useLanguage();
  const copy = () => { navigator.clipboard?.writeText(message.content); setToast("Đã sao chép câu trả lời và nguồn"); };
  return (
    <div className="assistant-row">
      <div className="avatar assistant-avatar"><Sparkles size={17} /></div>
      <div className="answer-wrap">
        <div className="answer-label">{tx("Trợ lý Bảo Việt", "Bảo Việt Assistant")}</div>
        {message.refused && <div className="refusal-label"><ShieldCheck size={16} /> {tx("Từ chối an toàn", "Safe refusal")}</div>}
        <div className={`answer-text ${message.refused ? "refused" : ""}`}>{message.content.split("\n").map((line, i) => <p key={i}>{formatLine(line, citationMode, setSourceOpen)}</p>)}</div>
        {citationMode === "footnote" && message.sources?.length > 0 && <div className="citation-list-note">Nguồn được hiển thị theo kiểu footnote ở cuối câu trả lời.</div>}
        {message.sources?.length > 0 && <SourceStack sources={message.sources} sourceOpen={sourceOpen} setSourceOpen={setSourceOpen} showExcerpts={showExcerpts} />}
        {showDetails && <ProcessingDetails pipeline={pipeline} runId={message.run_id} />}
        <div className="answer-actions">
          <button onClick={copy}><Copy size={16} /> {tx("Sao chép", "Copy")}</button><span />
          <span>{tx("Câu trả lời này có hữu ích?", "Was this answer helpful?")}</span>
          <button className={feedback === "up" ? "selected" : ""} onClick={() => { setFeedback("up"); setToast("Cảm ơn phản hồi của bạn"); }}><ThumbsUp size={16} /></button>
          <button className={feedback === "down" ? "selected" : ""} onClick={() => setFeedbackOpen(true)}><ThumbsDown size={16} /></button>
        </div>
      </div>
    </div>
  );
}

function StreamingAnswer({ text, loading }) {
  const { tx } = useLanguage();
  return <div className="assistant-row"><div className="avatar assistant-avatar"><Sparkles size={17} /></div><div className="answer-wrap"><div className="answer-label">{tx("Trợ lý Bảo Việt", "Bảo Việt Assistant")}</div>{loading ? <div className="thinking"><strong>{tx("Đang tìm trong tài liệu chính thức", "Searching official documents")}</strong><div><i /><i /><i /></div></div> : <div className="answer-text streaming"><p>{text}<span className="stream-caret" /></p></div>}</div></div>;
}

function SourceStack({ sources, sourceOpen, setSourceOpen, showExcerpts }) {
  const { tx } = useLanguage();
  return <div className="source-stack"><div className="source-heading"><span><FileText size={17} /> {tx("Nguồn tham khảo", "Sources")}</span><small>{sources.length} {tx("trích dẫn", "citations")}</small></div>{sources.map((s) => <div className={`source-card ${sourceOpen === s.ord ? "open" : ""}`} key={`${s.message_id}-${s.ord}`}><button onClick={() => setSourceOpen(sourceOpen === s.ord ? null : s.ord)}><span className="source-number">{s.ord}</span><span className="source-main"><strong>{s.section_path}</strong><small>{s.source_file} · {tx("Trang", "Page")} {s.page}</small></span><ChevronDown size={18} /></button>{sourceOpen === s.ord && <div className="source-detail">{showExcerpts && <p>“{s.text}”</p>}<a href={s.url} target="_blank" rel="noreferrer">{tx("Mở tài liệu gốc", "Open original document")} <ExternalLink size={14} /></a></div>}</div>)}</div>;
}

function ProcessingDetails({ pipeline, runId }) {
  return <div className="processing-detail-wrap"><div className="processing-panel"><div><span>run_id</span><strong>{runId}</strong></div><div><span>query_processed</span><strong>{TRACE.query_processed}</strong></div><div><span>detected_products</span><strong>{TRACE.detected_products.join(", ")}</strong></div><div><span>retrieval_mode</span><strong>{TRACE.retrieval_mode}</strong></div><div><span>latency_ms</span><strong>{TRACE.latency_ms}</strong></div><div><span>tokens_in / tokens_out</span><strong>{TRACE.tokens_in} / {TRACE.tokens_out}</strong></div><div><span>cost_usd</span><strong>{TRACE.cost_usd.toFixed(6)}</strong></div><div><span>timings_ms</span><strong>{Object.entries(TRACE.timings_ms).map(([key, value]) => `${key}: ${value}`).join(" · ")}</strong></div><div><span>error</span><strong>{TRACE.error || "—"}</strong></div></div><div className="retrieval-mini-table"><div><b>rank</b><b>chunk_id</b><b>score</b><b>rerank</b><b>in_context</b></div>{RETRIEVAL_LOGS.map((row) => <div key={`${row.message_id}-${row.rank}`}><span>{row.rank}</span><code>{row.chunk_id}</code><span>{row.score}</span><span>{row.rerank ?? "—"}</span><span>{row.in_context ? "true" : "false"}</span></div>)}</div><small className="admin-only-note"><ShieldCheck size={13} /> Chỉ quản trị viên được đọc traces và retrieval_logs.</small></div>;
}

function HistoryView({ items, search, setSearch, openHistory, menu, setMenu, setRenameItem, setDeleteItem, exportItem, printItem, clearAll }) {
  const { tx } = useLanguage();
  return <div className="standard-page"><div className="page-header"><div><h1>{tx("Lịch sử trò chuyện", "Chat history")}</h1></div><button className="danger-ghost" onClick={clearAll}><Trash2 size={16} /> {tx("Xóa tất cả", "Delete all")}</button></div><div className="toolbar"><label className="page-search"><Search size={17} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={tx("Tìm trong lịch sử", "Search history")} /></label><span>{items.length} {tx("cuộc trò chuyện", "conversations")}</span></div><div className="history-page-list">{items.map((item) => <div className="history-row" key={item.id}><button className="history-row-main" onClick={() => openHistory(item)}><span className="history-row-icon"><MessagesSquare size={19} /></span><span><strong>{item.title} {item.title_is_custom && <b className="custom-title-badge">{tx("Đã đổi tên", "Renamed")}</b>}</strong><small>{item.preview}</small></span></button><time><strong>{formatDateTime(item.updated_at)}</strong></time><div className="row-menu-wrap"><button className="icon-button" onClick={() => setMenu(menu === item.id ? null : item.id)}><MoreHorizontal size={19} /></button>{menu === item.id && <div className="row-menu"><button onClick={() => { setRenameItem(item); setMenu(null); }}><Pencil size={15} /> {tx("Đổi tên", "Rename")}</button><button onClick={() => { exportItem(); setMenu(null); }}><Download size={15} /> {tx("Xuất Markdown", "Export Markdown")}</button><button onClick={() => { printItem(); setMenu(null); }}><FileText size={15} /> {tx("In / Lưu PDF", "Print / Save PDF")}</button><button className="danger" onClick={() => { setDeleteItem(item); setMenu(null); }}><Trash2 size={15} /> {tx("Xóa", "Delete")}</button></div>}</div></div>)}</div></div>;
}

function CatalogView() {
  const { tx, language } = useLanguage();
  const [selected, setSelected] = useState(PRODUCTS[0]);
  const version = DATA_VERSIONS.find((item) => item.is_active);
  const selectedDocuments = DOCUMENTS.filter((item) => item.product_code === selected.product_code);
  return <div className="standard-page">
    <div className="page-header">
      <div><h1>{tx("Sản phẩm và tài liệu", "Products and documents")}</h1></div>
      <div className="version-badge"><CheckCircle2 size={17} /> {version.version} · {version.n_chunks.toLocaleString("vi-VN")} chunks</div>
    </div>
    <div className="catalog-layout">
      <div className="product-table card">
        <div className="table-head"><span>{tx("Sản phẩm", "Product")}</span><span>{tx("Nhóm", "Line")}</span><span>{tx("Tài liệu", "Documents")}</span><span>{tx("Đoạn", "Chunks")}</span></div>
        {PRODUCTS.map((product) => {
          const documentCount = DOCUMENTS.filter((item) => item.product_code === product.product_code).length;
          const chunkCount = CHUNKS.filter((item) => item.product_code === product.product_code && item.data_version === version.version).length;
          return <button key={product.product_code} onClick={() => setSelected(product)} className={selected.product_code === product.product_code ? "selected" : ""}>
            <span><b>{product.product_code}</b><strong>{product.product_name}</strong></span>
            <span>{language === "vi" ? ENUM_LABELS.line[product.line] : EN_LABELS.line[product.line]}</span><span>{documentCount}</span><span>{chunkCount}</span>
          </button>;
        })}
      </div>
      <aside className="product-detail card">
        <div className="product-detail-head"><span className="product-code">{selected.product_code}</span><b className={`status-tag ${selected.is_active ? "" : "muted"}`}>{selected.is_active ? tx("Đang hoạt động", "Active") : tx("Ngừng hoạt động", "Inactive")}</b></div>
        <h2>{selected.product_name}</h2><hr />
        <h3>{tx("Tài liệu", "Documents")}</h3>
        {selectedDocuments.length ? selectedDocuments.map((document) => <a key={document.id} href={document.url} target="_blank" rel="noreferrer">
          <FileText size={16} /><span><strong>{language === "vi" ? ENUM_LABELS.doc_type[document.doc_type] : EN_LABELS.doc_type[document.doc_type]}</strong><small>{document.source_file} · {tx("hiệu lực", "effective")} {formatDate(document.effective_date)}</small></span><ExternalLink size={14} />
        </a>) : <p className="empty-copy">{tx("Chưa có tài liệu.", "No documents available.")}</p>}
      </aside>
    </div>
  </div>;
}

function DashboardView({ setToast }) {
  const { tx } = useLanguage();
  const chartData = PIPELINE_CONFIGS.map((config) => {
    const recall = EVAL_RESULTS.find((item) => item.run_id.startsWith(config.name) && item.question_group === "all" && item.metric === "recall@5")?.value || 0;
    const faithfulness = EVAL_RESULTS.find((item) => item.run_id.startsWith(config.name) && item.question_group === "all" && item.metric === "faithfulness")?.value || 0;
    return { name: config.name, recall, faithfulness };
  });
  return <div className="standard-page"><div className="page-header"><div><h1>{tx("Dashboard chỉ số", "Metrics dashboard")}</h1></div><button className="secondary-button" onClick={() => setToast(tx("Đã cập nhật số liệu", "Metrics refreshed"))}><RefreshCw size={16} /> {tx("Làm mới", "Refresh")}</button></div><div className="metric-grid"><Metric label={tx("Câu hỏi hôm nay", "Questions today")} value="128" icon={MessagesSquare} /><Metric label={tx("Độ trễ p95", "p95 latency")} value="4,8s" icon={Gauge} /><Metric label={tx("Tỷ lệ từ chối", "Refusal rate")} value="18,7%" icon={ShieldCheck} /><Metric label={tx("Đánh giá tích cực", "Positive feedback")} value="91,4%" icon={ThumbsUp} /></div><div className="dashboard-grid"><div className="card chart-card"><div className="card-title"><div><h2>{tx("Chất lượng theo cấu hình", "Quality by configuration")}</h2></div><BarChart3 size={20} /></div><div className="bar-chart">{chartData.map((item) => <div className="bar-group" key={item.name}><span>{item.name}</span><div><i style={{ height: `${item.recall * 100}%` }} /><i style={{ height: `${item.faithfulness * 100}%` }} /></div><small>{Math.round(item.recall * 100)}%</small></div>)}</div><div className="chart-legend"><span><i className="blue" /> Recall@5</span><span><i className="gold" /> Faithfulness</span></div></div><div className="card activity-card"><div className="card-title"><div><h2>{tx("Phân bố truy vấn", "Query distribution")}</h2></div></div>{[["lookup", 42], ["table", 21], ["compare", 17], ["scenario", 14], ["refused", 6]].map(([group, value]) => <div className="progress-row" key={group}><span>{group}</span><div><i style={{ width: `${value * 2}%` }} /></div><strong>{value}%</strong></div>)}</div></div></div>;
}

function Metric({ label, value, delta, icon: Icon }) {
  return <div className="metric-card card"><span><Icon size={19} /></span><small>{label}</small><strong>{value}</strong>{delta && <p>{delta}</p>}</div>;
}

function LogsView({ setToast }) {
  const { tx } = useLanguage();
  const [filter, setFilter] = useState("Tất cả");
  const [search, setSearch] = useState("");
  const visibleLogs = QUERY_LOGS.filter((log) => (filter === "Tất cả" || (filter === "Từ chối" && log.refused) || (filter === "Không hữu ích" && log.rating === -1) || (filter === "Độ trễ cao" && log.latency_ms > 4000)) && `${log.run_id} ${log.content}`.toLowerCase().includes(search.toLowerCase()));
  const exportCsv = () => {
    const csv = ["run_id,content,refused,refusal_reason,config_name,data_version,latency_ms,rating,feedback_reason", ...visibleLogs.map((log) => [log.run_id, `"${log.content}"`, log.refused, log.refusal_reason || "", log.config_name, log.data_version, log.latency_ms, log.rating ?? "", log.feedback_reason || ""].join(","))].join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "nhat-ky-truy-van.csv";
    anchor.click();
    URL.revokeObjectURL(url);
    setToast("Đã xuất nhật ký CSV");
  };
  const filters = [{ value: "Tất cả", label: tx("Tất cả", "All") }, { value: "Từ chối", label: tx("Từ chối", "Refused") }, { value: "Không hữu ích", label: tx("Không hữu ích", "Not helpful") }, { value: "Độ trễ cao", label: tx("Độ trễ cao", "High latency") }];
  return <div className="standard-page"><div className="page-header"><div><h1>{tx("Nhật ký truy vấn", "Query logs")}</h1></div><button className="secondary-button" onClick={exportCsv}><Download size={16} /> {tx("Xuất CSV", "Export CSV")}</button></div><div className="toolbar log-toolbar"><label className="page-search"><Search size={17} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder={tx("Tìm câu hỏi hoặc mã lần chạy", "Search question or run ID")} /></label><div className="filter-chips">{filters.map((item) => <button key={item.value} className={filter === item.value ? "active" : ""} onClick={() => setFilter(item.value)}>{item.label}</button>)}</div></div><div className="data-table card"><div className="data-row head"><span>{tx("Thời gian / Mã lần chạy", "Time / Run ID")}</span><span>{tx("Câu hỏi", "Question")}</span><span>{tx("Trạng thái", "Status")}</span><span>{tx("Cấu hình", "Configuration")}</span><span>{tx("Độ trễ", "Latency")}</span><span>{tx("Đánh giá", "Feedback")}</span></div>{visibleLogs.map((log) => <button className="data-row" key={log.message_id} onClick={() => setToast(tx(`Đã mở chi tiết ${log.run_id}`, `Opened details for ${log.run_id}`))}><span><strong>{formatDateTime(log.created_at)}</strong><small>{log.run_id}</small></span><span>{log.content}</span><span><b className={`status-tag ${log.refused ? "warning" : ""}`}>{log.refused ? tx("Từ chối", "Refused") : tx("Đã trả lời", "Answered")}</b></span><span><strong>{log.config_name}</strong><small>{log.data_version}</small></span><span>{log.latency_ms} ms</span><span>{log.rating === 1 ? tx("Hữu ích", "Helpful") : log.rating === -1 ? tx("Không hữu ích", "Not helpful") : "—"}</span></button>)}</div></div>;
}

function AccountsView({ setToast }) {
  const { tx } = useLanguage();
  const [accounts, setAccounts] = useState(ACCOUNTS);
  const [createOpen, setCreateOpen] = useState(false);
  return <div className="standard-page"><div className="page-header"><div><h1>{tx("Tài khoản demo", "Demo accounts")}</h1></div><button className="primary-button" onClick={() => setCreateOpen(true)}><Plus size={17} /> {tx("Tạo tài khoản", "Create account")}</button></div><div className="data-table accounts-table card"><div className="data-row head"><span>{tx("Tài khoản", "Account")}</span><span>{tx("Vai trò", "Role")}</span><span>{tx("Trạng thái", "Status")}</span><span>{tx("Đăng nhập cuối", "Last sign-in")}</span><span>{tx("Thao tác", "Actions")}</span></div>{accounts.map((account) => <div className="data-row" key={account.id}><span className="account-name"><i>{account.username.slice(0, 2).toUpperCase()}</i><span><strong>{account.display_name || account.username}</strong><small>{account.username} · {account.email}</small></span></span><span>{account.role === "admin" ? tx("Quản trị viên", "Administrator") : tx("Người dùng", "User")}</span><span><b className={`status-tag ${account.is_active ? "" : "muted"}`}>{account.is_active ? tx("Hoạt động", "Active") : tx("Đã khóa", "Locked")}</b></span><span>{account.last_sign_in_at ? formatDateTime(account.last_sign_in_at) : tx("Chưa đăng nhập", "Never")}</span><span className="account-actions"><button onClick={() => { setAccounts((current) => current.map((x) => x.id === account.id ? { ...x, role: x.role === "user" ? "admin" : "user" } : x)); setToast(tx("Đã cập nhật vai trò", "Role updated")); }}>{tx("Đổi vai trò", "Change role")}</button><button onClick={() => { setAccounts((current) => current.map((x) => x.id === account.id ? { ...x, is_active: !x.is_active, banned_until: x.is_active ? "2026-12-20T09:31:05+07:00" : null } : x)); setToast(account.is_active ? tx("Đã khóa tài khoản", "Account locked") : tx("Đã mở khóa tài khoản", "Account unlocked")); }}>{account.is_active ? tx("Khóa", "Lock") : tx("Mở khóa", "Unlock")}</button><button onClick={() => setToast(tx("Đã tạo mật khẩu tạm thời", "Temporary password created"))}>{tx("Đặt lại mật khẩu", "Reset password")}</button></span></div>)}</div>{createOpen && <CreateAccount existingUsernames={accounts.map((account) => account.username)} existingEmails={accounts.map((account) => account.email)} onClose={() => setCreateOpen(false)} onSave={(account) => { setAccounts((current) => [...current, { ...account, id: crypto.randomUUID(), is_active: true, last_sign_in_at: null, banned_until: null }]); setCreateOpen(false); setToast(tx("Đã tạo tài khoản", "Account created")); }} />}</div>;
}

function ConfigurationView({ pipeline, setPipeline, setToast }) {
  const { tx } = useLanguage();
  const [draft, setDraft] = useState(pipeline);
  const descriptions = {
    B0: tx("Không sử dụng kho tài liệu", "No document retrieval"),
    B1: tx("Tìm kiếm dense với đoạn cố định", "Dense retrieval with fixed chunks"),
    B2: tx("Tìm kiếm dense với đoạn theo cấu trúc", "Dense retrieval with structured chunks"),
    B3: tx("Tìm kiếm hybrid và xử lý câu hỏi", "Hybrid retrieval and query processing"),
    B4: tx("Pipeline đầy đủ với reranker và trích dẫn", "Full pipeline with reranking and citations"),
  };
  return <div className="standard-page configuration-page">
    <div className="page-header"><div><h1>{tx("Cấu hình hệ thống", "System configuration")}</h1></div></div>
    <div className="configuration-content">
      <div className="config-summary card">
        <span>{tx("Cấu hình đang sử dụng", "Active configuration")}</span>
        <strong>{pipeline}</strong>
        <p>{descriptions[pipeline]}</p>
      </div>
      <div className="config-list">
        {PIPELINE_CONFIGS.map((config) => <button key={config.name} className={`config-option card ${draft === config.name ? "selected" : ""}`} onClick={() => setDraft(config.name)}>
          <span className="config-radio">{draft === config.name && <Check size={15} />}</span>
          <span><strong>{config.name}</strong><small>{descriptions[config.name]}</small></span>
          {pipeline === config.name && <b>{tx("Đang dùng", "Active")}</b>}
        </button>)}
      </div>
      <div className="config-actions"><button className="primary-button" disabled={draft === pipeline} onClick={() => { setPipeline(draft); setToast(tx(`Đã chuyển cấu hình sang ${draft}`, `Active configuration changed to ${draft}`)); }}>{tx("Áp dụng cấu hình", "Apply configuration")}</button></div>
    </div>
  </div>;
}

function CompareView() {
  const { tx } = useLanguage();
  const [left, setLeft] = useState("B0");
  const [right, setRight] = useState("B4");
  const [question, setQuestion] = useState("Thời hạn giải quyết quyền lợi bảo hiểm An Gia là bao lâu?");
  const [ran, setRan] = useState(false);
  const [compareSourceOpen, setCompareSourceOpen] = useState(null);
  return <div className="standard-page"><div className="page-header"><div><h1>{tx("So sánh cấu hình", "Compare configurations")}</h1></div></div><div className="compare-query card"><label>{tx("Câu hỏi", "Question")}<input value={question} onChange={(e) => setQuestion(e.target.value)} /></label><button className="primary-button" onClick={() => setRan(true)}><Sparkles size={17} /> {tx("Chạy so sánh", "Run comparison")}</button></div><div className="compare-grid">{[[left, setLeft, false], [right, setRight, true]].map(([value, setter, rag], index) => { const config = PIPELINE_CONFIGS.find((item) => item.name === value); return <div className="compare-column card" key={index}><div className="compare-head"><label>{tx("Cấu hình", "Configuration")}<select value={value} onChange={(e) => setter(e.target.value)}>{PIPELINE_CONFIGS.map((item) => <option key={item.name} value={item.name}>{item.name}</option>)}</select></label><span>{config.description}</span></div>{ran ? <><div className="compare-answer"><Bot size={20} /><p>{rag ? "Bảo Việt giải quyết quyền lợi trong 15 ngày làm việc kể từ khi nhận đủ hồ sơ hợp lệ. [1]" : "Thông thường doanh nghiệp bảo hiểm sẽ xử lý hồ sơ trong một khoảng thời gian hợp lý theo quy định."}</p></div><div className="compare-stats"><span>{tx("Mã lần chạy", "Run ID")}<strong>{value}_demo_20261120-1100</strong></span><span>{tx("Độ trễ", "Latency")}<strong>{rag ? "3204 ms" : "1408 ms"}</strong></span><span>{tx("Nguồn", "Sources")}<strong>{rag ? "2" : "0"}</strong></span></div>{rag && <SourceStack sources={[SOURCES[0]]} sourceOpen={compareSourceOpen} setSourceOpen={setCompareSourceOpen} showExcerpts={false} />}</> : <div className="empty-compare"><Gauge size={27} /><p>{tx("Chạy so sánh để xem kết quả", "Run comparison to see results")}</p></div>}</div>; })}</div></div>;
}

function SettingsPanel({ onClose, theme, setTheme, fontSize, setFontSize, citationMode, setCitationMode, showExcerpts, setShowExcerpts, showDetails, setShowDetails, role }) {
  const { language, setLanguage, tx } = useLanguage();
  return <div className="modal-layer"><button className="modal-scrim" onClick={onClose} /><div className="settings-panel"><div className="settings-title"><div><span>{tx("CÀI ĐẶT CÁ NHÂN", "PERSONAL SETTINGS")}</span><h2>{tx("Tùy chỉnh trải nghiệm", "Customize your experience")}</h2></div><button className="icon-button" onClick={onClose}><X size={20} /></button></div>
    <section><h3>{tx("GIAO DIỆN", "APPEARANCE")}</h3><div className="theme-options three"><button className={theme === "light" ? "active" : ""} onClick={() => setTheme("light")}><Sun size={20} /> {tx("Sáng", "Light")}</button><button className={theme === "dark" ? "active" : ""} onClick={() => setTheme("dark")}><Moon size={20} /> {tx("Tối", "Dark")}</button><button className={theme === "system" ? "active" : ""} onClick={() => setTheme("system")}><Settings size={20} /> {tx("Hệ thống", "System")}</button></div><div className="range-setting"><span><strong>{tx("Cỡ chữ", "Font size")}</strong></span><input type="range" min="12" max="20" step="1" value={fontSize} onChange={(event) => setFontSize(Number(event.target.value))} /><b>{fontSize}px</b></div></section>
    <section><h3>{tx("NGÔN NGỮ", "LANGUAGE")}</h3><div className="language-options"><button className={language === "vi" ? "active" : ""} onClick={() => setLanguage("vi")}>Tiếng Việt</button><button className={language === "en" ? "active" : ""} onClick={() => setLanguage("en")}>English</button></div></section>
    <section><h3>{tx("TRÍCH DẪN VÀ XỬ LÝ", "CITATIONS AND PROCESSING")}</h3><div className="radio-setting"><span><strong>{tx("Cách hiển thị nguồn", "Citation display")}</strong></span><label><input type="radio" checked={citationMode === "inline"} onChange={() => setCitationMode("inline")} /> {tx("Trong câu", "Inline")}</label><label><input type="radio" checked={citationMode === "footnote"} onChange={() => setCitationMode("footnote")} /> {tx("Cuối câu", "Footnote")}</label></div><Toggle label={tx("Hiển thị đoạn văn gốc", "Show source excerpts")} value={showExcerpts} setValue={setShowExcerpts} />{role === "admin" && <Toggle label={tx("Chi tiết xử lý", "Processing details")} value={showDetails} setValue={setShowDetails} />}</section>
  </div></div>;
}

function Toggle({ label, detail, value, setValue }) {
  return <div className="setting-row"><div><strong>{label}</strong>{detail && <small>{detail}</small>}</div><button className={`switch ${value ? "on" : ""}`} onClick={() => setValue(!value)} aria-pressed={value}><span /></button></div>;
}

function SystemModal({ onClose }) {
  const { tx } = useLanguage();
  const [checking, setChecking] = useState(false);
  return <Modal title={tx("Trạng thái hệ thống", "System status")} onClose={onClose} wide><div className="system-summary"><CheckCircle2 size={24} /><div><strong>{checking ? tx("Đang kiểm tra…", "Checking…") : tx("Tất cả thành phần đang hoạt động", "All services are operational")}</strong></div><button onClick={() => { setChecking(true); setTimeout(() => setChecking(false), 900); }}><RefreshCw className={checking ? "spin" : ""} size={16} /> {tx("Kiểm tra lại", "Check again")}</button></div><div className="system-list">{SYSTEMS.map((s) => <div key={s.name}><span className="system-icon"><Activity size={18} /></span><span><strong>{s.name}</strong><small>{s.detail}</small></span><b><i /> {tx("Sẵn sàng", "Ready")}</b><em>{s.metric}</em></div>)}</div></Modal>;
}

function FeedbackModal({ onClose, onSave }) {
  const { tx } = useLanguage();
  const [reason, setReason] = useState("");
  const [comment, setComment] = useState("");
  const reasons = { sai_noi_dung: tx("Sai nội dung", "Incorrect content"), thieu_nguon: tx("Thiếu nguồn", "Missing sources"), trich_dan_sai: tx("Trích dẫn sai", "Incorrect citation"), tu_choi_nham: tx("Từ chối nhầm", "Incorrect refusal"), khac: tx("Khác", "Other") };
  return <Modal title={tx("Điều gì cần cải thiện?", "What should be improved?")} onClose={onClose}><div className="reason-list">{Object.entries(reasons).map(([value, label]) => <label key={value}><input type="radio" name="reason" checked={reason === value} onChange={() => setReason(value)} /><span><strong>{label}</strong></span></label>)}</div><label className="modal-field">{tx("Ghi chú", "Comment")}<textarea value={comment} onChange={(event) => setComment(event.target.value)} placeholder={tx("Không bắt buộc", "Optional")} /></label><div className="modal-actions"><button className="secondary-button" onClick={onClose}>{tx("Hủy", "Cancel")}</button><button className="primary-button" disabled={!reason} onClick={() => onSave({ rating: -1, reason, comment: comment || null })}>{tx("Gửi phản hồi", "Submit feedback")}</button></div></Modal>;
}

function RenameModal({ item, onClose, onSave }) {
  const { tx } = useLanguage();
  const [name, setName] = useState(item.title);
  return <Modal title={tx("Đổi tên cuộc trò chuyện", "Rename conversation")} onClose={onClose}><label className="modal-field">{tx("Tên cuộc trò chuyện", "Conversation title")}<input value={name} onChange={(e) => setName(e.target.value)} autoFocus /></label><div className="modal-actions"><button className="secondary-button" onClick={onClose}>{tx("Hủy", "Cancel")}</button><button className="primary-button" onClick={() => onSave(name)} disabled={!name.trim()}>{tx("Lưu", "Save")}</button></div></Modal>;
}

function ConfirmModal({ item, onClose, onConfirm }) {
  const { tx } = useLanguage();
  return <Modal title={tx("Xác nhận xóa", "Confirm deletion")} onClose={onClose}><div className="delete-warning"><Trash2 size={21} /> {tx("Hành động này không thể hoàn tác.", "This action cannot be undone.")}</div><div className="modal-actions"><button className="secondary-button" onClick={onClose}>{tx("Hủy", "Cancel")}</button><button className="danger-button" onClick={onConfirm}>{tx("Xóa vĩnh viễn", "Delete permanently")}</button></div></Modal>;
}

function CreateAccount({ existingUsernames, existingEmails, onClose, onSave }) {
  const { tx } = useLanguage();
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("user");
  const validEmail = /^demo\d+@bv-rag\.local$/.test(email);
  const duplicateUsername = existingUsernames.includes(username);
  const duplicateEmail = existingEmails.includes(email);
  return <Modal title={tx("Tạo tài khoản demo", "Create demo account")} onClose={onClose}><label className="modal-field">Username *<input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="demo04" />{duplicateUsername && <small className="field-error">{tx("Tên đăng nhập đã tồn tại.", "Username already exists.")}</small>}</label><label className="modal-field">{tx("Tên hiển thị", "Display name")}<input value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder={tx("Người dùng demo 04", "Demo user 04")} /></label><label className="modal-field">Email *<input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="demo04@bv-rag.local" />{email && !validEmail && <small className="field-error">{tx("Email phải có dạng demoNN@bv-rag.local", "Use the format demoNN@bv-rag.local")}</small>}{duplicateEmail && <small className="field-error">{tx("Email đã tồn tại.", "Email already exists.")}</small>}</label><label className="modal-field">{tx("Vai trò", "Role")} *<select value={role} onChange={(e) => setRole(e.target.value)}><option value="user">User</option><option value="admin">Administrator</option></select></label><div className="modal-actions"><button className="secondary-button" onClick={onClose}>{tx("Hủy", "Cancel")}</button><button className="primary-button" disabled={!username || !validEmail || duplicateUsername || duplicateEmail} onClick={() => onSave({ username, display_name: displayName || null, email, role })}>{tx("Tạo tài khoản", "Create account")}</button></div></Modal>;
}

function SessionExpired({ onLogin, onLogout }) {
  const { tx } = useLanguage();
  return <div className="modal-layer session-layer"><div className="modal-card session-card"><span className="session-lock"><LockKeyhole size={24} /></span><h2>{tx("Phiên làm việc đã hết hạn", "Session expired")}</h2><button className="primary-button" onClick={onLogin}>{tx("Tiếp tục phiên làm việc", "Continue session")}</button><button className="text-button" onClick={onLogout}>{tx("Quay về đăng nhập", "Return to sign in")}</button></div></div>;
}

function Modal({ title, subtitle, onClose, children, wide = false }) {
  return <div className="modal-layer"><button className="modal-scrim" onClick={onClose} /><div className={`modal-card ${wide ? "wide" : ""}`}><div className="modal-head"><div><h2>{title}</h2><p>{subtitle}</p></div><button className="icon-button" onClick={onClose}><X size={20} /></button></div>{children}</div></div>;
}

function formatDate(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("vi-VN", { day: "2-digit", month: "2-digit", year: "numeric" }).format(new Date(value));
}

function formatDateTime(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("vi-VN", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

function formatLine(line, mode, onCitation) {
  const parts = line.split(/(\*\*.*?\*\*|\[\d+\])/g).filter(Boolean);
  return parts.map((part, index) => {
    if (part.startsWith("**")) return <strong key={index}>{part.slice(2, -2)}</strong>;
    if (/^\[\d+\]$/.test(part)) {
      const id = Number(part.slice(1, -1));
      return mode === "inline" ? <button className="citation" onClick={() => onCitation(id)} key={index}>{id}</button> : <sup key={index}>[{id}]</sup>;
    }
    return part;
  });
}
