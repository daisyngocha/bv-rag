import React, { useEffect, useMemo, useRef, useState } from "react";
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

  if (!authenticated) return <LoginScreen onLogin={login} />;

  const mm = String(Math.floor(sessionSeconds / 60)).padStart(2, "0");
  const ss = String(sessionSeconds % 60).padStart(2, "0");

  return (
    <div className={`full-app theme-${theme} ${fontSize >= 17 ? "large-text" : ""}`} style={{ "--app-font-size": `${fontSize}px` }}>
      <a className="skip-link" href="#page-content">Bỏ qua đến nội dung chính</a>
      <header className="topbar full-topbar">
        <button className="icon-button mobile-only" onClick={() => setMobileNav(true)} aria-label="Mở menu"><Menu size={22} /></button>
        <button className="brand brand-button" onClick={() => setView("chat")}>
          <img src="/baoviet-logo.png" alt="Bảo hiểm Bảo Việt" />
          <span className="brand-divider" />
          <span><strong>Trợ lý sản phẩm</strong><small>Hỏi đáp có trích dẫn</small></span>
        </button>
        <div className="topbar-actions">
          <button className="status-pill" onClick={() => setSystemOpen(true)}><span /> Hệ thống sẵn sàng</button>
          <button className="session-pill" onClick={() => setSessionSeconds(29 * 60 + 59)} title="Nhấn để gia hạn phiên"><Clock3 size={15} /> {mm}:{ss}</button>
          <button className="icon-button" onClick={() => setSystemOpen(true)} aria-label="Trợ giúp"><CircleHelp size={20} /></button>
          <button className="icon-button" onClick={() => setSettingsOpen(true)} aria-label="Cài đặt"><Settings size={20} /></button>
          <div className="profile-wrap">
            <button className="profile-button" onClick={() => setProfileOpen(!profileOpen)}>
              <span>D1</span><span className="profile-copy"><strong>{ACCOUNTS[0].display_name}</strong><small>{ENUM_LABELS.user_role[role]}</small></span><ChevronDown size={16} />
            </button>
            {profileOpen && (
              <div className="profile-menu">
                <div className="profile-menu-head"><strong>{ACCOUNTS[0].username}</strong><small>{ACCOUNTS[0].email} · không lưu dữ liệu cá nhân</small></div>
                <div className="profile-role-note"><ShieldCheck size={16} /><span>role: <b>{role}</b><small>Vai trò chỉ được quản trị qua profiles.role.</small></span></div>
                <button onClick={logout}><LogOut size={17} /> Đăng xuất</button>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="workspace">
        <aside className={`sidebar full-sidebar ${mobileNav ? "mobile-open" : ""}`}>
          <div className="sidebar-top">
            <button className="new-chat" onClick={newChat}><MessageCirclePlus size={19} /><span>Cuộc trò chuyện mới</span></button>
            <button className="icon-button mobile-only" onClick={() => setMobileNav(false)} aria-label="Đóng menu"><X size={20} /></button>
          </div>
          <nav className="main-nav" aria-label="Điều hướng chính">
            <NavButton active={view === "chat"} icon={MessagesSquare} label="Hỏi đáp" onClick={() => setView("chat")} />
            <NavButton active={view === "history"} icon={History} label="Lịch sử chat" onClick={() => setView("history")} />
            <NavButton active={view === "catalog"} icon={BookOpen} label="Sản phẩm & tài liệu" onClick={() => setView("catalog")} />
            {role === "admin" && (
              <>
                <p className="nav-label">QUẢN TRỊ</p>
                <NavButton active={view === "dashboard"} icon={LayoutDashboard} label="Dashboard" onClick={() => setView("dashboard")} />
                <NavButton active={view === "logs"} icon={FileClock} label="Nhật ký truy vấn" onClick={() => setView("logs")} badge="4" />
                <NavButton active={view === "accounts"} icon={Users} label="Tài khoản demo" onClick={() => setView("accounts")} />
                <NavButton active={view === "compare"} icon={SlidersHorizontal} label="So sánh cấu hình" onClick={() => setView("compare")} />
              </>
            )}
          </nav>
          <div className="sidebar-history-mini">
            <div className="section-label"><span>GẦN ĐÂY</span><button onClick={() => setView("history")}>Xem tất cả</button></div>
            {history.slice(0, 4).map((item) => (
              <button key={item.id} className={activeHistory === item.id ? "active" : ""} onClick={() => openHistory(item)}>
                <span>{item.title}</span><small>{item.time}</small>
              </button>
            ))}
          </div>
          <div className="sidebar-footer">
            <button onClick={() => setSettingsOpen(true)}><Settings size={18} /><span>Cài đặt</span></button>
            <button onClick={() => setSystemOpen(true)}><Activity size={18} /><span>Trạng thái hệ thống</span></button>
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
  );
}

function NavButton({ active, icon: Icon, label, onClick, badge }) {
  return <button className={`nav-button ${active ? "active" : ""}`} onClick={onClick}><Icon size={18} /><span>{label}</span>{badge && <b>{badge}</b>}</button>;
}

function LoginScreen({ onLogin }) {
  return (
    <div className="login-page">
      <div className="login-brand">
        <img src="/baoviet-logo.png" alt="Bảo hiểm Bảo Việt" />
        <div><span>TRỢ LÝ SẢN PHẨM BẢO HIỂM</span><h1>Tra cứu nhanh.<br />Căn cứ rõ ràng.</h1><p>Hệ thống hỏi đáp sử dụng RAG, cung cấp câu trả lời từ tài liệu sản phẩm chính thức và luôn đính kèm trích dẫn để kiểm tra.</p></div>
        <div className="login-trust"><ShieldCheck size={19} /><span>Chỉ sử dụng tài liệu công khai<br /><small>Không nhập thông tin cá nhân hoặc hợp đồng</small></span></div>
      </div>
      <form className="login-card" onSubmit={onLogin}>
        <div className="login-icon"><KeyRound size={23} /></div>
        <p className="eyebrow-text">PHIÊN BẢN DEMO</p>
        <h2>Đăng nhập hệ thống</h2>
        <p>Sử dụng tài khoản demo được cung cấp để tiếp tục.</p>
        <label>email demo<input defaultValue="demo01@bv-rag.local" autoComplete="username" /></label>
        <label>Mật khẩu<input type="password" defaultValue="baoviet-demo" autoComplete="current-password" /></label>
        <div className="login-note"><LockKeyhole size={15} /> Phiên tự động hết hạn sau 30 phút không hoạt động.</div>
        <button type="submit">Đăng nhập <ArrowUp size={18} /></button>
        <small>Không có chức năng đăng ký tài khoản.</small>
      </form>
    </div>
  );
}

function ChatView(props) {
  const {
    messages, loading, streamText, query, setQuery, sendQuestion, selectedProducts, setSelectedProducts,
    scopeOpen, setScopeOpen, pipeline, setPipeline, role, sourceOpen, setSourceOpen, feedback,
    setFeedback, setFeedbackOpen, privacyMasked, setPrivacyMasked, citationMode, showExcerpts,
    showDetails, setToast, downloadConversation, chatEnd,
  } = props;
  return (
    <div className="chat-page">
      <div className="page-header compact">
        <div><div className="page-kicker"><span /> RAG · Kho dữ liệu v1</div><h1>{messages.length ? "Cuộc trò chuyện hiện tại" : "Trợ lý tra cứu sản phẩm bảo hiểm"}</h1></div>
        <div className="header-actions">
          {role === "admin" && <label className="pipeline-select" title={`app_settings.${APP_SETTINGS.key} = ${APP_SETTINGS.value.config}`}>active_config<select value={pipeline} onChange={(e) => setPipeline(e.target.value)}>{PIPELINE_CONFIGS.map((config) => <option key={config.name} value={config.name}>{config.name} · {config.description}</option>)}</select></label>}
          {messages.length > 0 && <button className="secondary-button" onClick={downloadConversation}><Download size={16} /> Xuất Markdown</button>}
        </div>
      </div>
      <section className="chat-scroll full-chat-scroll" aria-live="polite">
        {!messages.length && !streamText ? (
          <div className="welcome">
            <div className="welcome-mark"><Sparkles size={26} /></div>
            <p className="welcome-kicker">TRỢ LÝ BẢO VIỆT</p>
            <h2>Bạn muốn tìm hiểu điều gì?</h2>
            <p className="welcome-copy">Tra cứu quy tắc, quyền lợi và biểu phí từ tài liệu sản phẩm chính thức. Mỗi câu trả lời đều có nguồn để bạn kiểm tra.</p>
            <div className="sample-grid">{SAMPLE_QUESTIONS.filter((item) => item.is_active).map((item) => <button key={item.qid} onClick={() => sendQuestion(item.question)}><span>{ENUM_LABELS.question_group[item.question_group]}</span><strong>{item.question}</strong><small>{item.products?.join(", ")}</small><ArrowUp size={18} /></button>)}</div>
          </div>
        ) : (
          <div className="conversation">
            {privacyMasked && <div className="privacy-banner"><ShieldCheck size={17} /><span>Thông tin nhạy cảm đã được tự động che trước khi lưu lịch sử.</span><button onClick={() => setPrivacyMasked(false)}><X size={16} /></button></div>}
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
            <button className="scope-button" onClick={() => setScopeOpen(!scopeOpen)}><BookOpen size={16} />{selectedProducts.length ? `${selectedProducts.length} sản phẩm đã chọn` : "Tự động nhận diện sản phẩm"}<ChevronDown size={16} /></button>
            {scopeOpen && <div className="scope-menu"><div><strong>Phạm vi sản phẩm</strong><small>messages.product_filter · text[]</small></div>{PRODUCTS.filter((p) => p.is_active).map((p) => <button key={p.product_code} onClick={() => setSelectedProducts(selectedProducts.includes(p.product_code) ? selectedProducts.filter((x) => x !== p.product_code) : [...selectedProducts, p.product_code])}><span className={`checkbox ${selectedProducts.includes(p.product_code) ? "checked" : ""}`}>{selectedProducts.includes(p.product_code) && <Check size={13} />}</span><span><strong>{p.product_name}</strong><small>{p.product_code} · {ENUM_LABELS.line[p.line]}</small></span></button>)}</div>}
          </div>
          <span className="privacy-note"><ShieldCheck size={15} /> Hệ thống tự che CCCD, SĐT và email trong câu hỏi</span>
        </div>
        <div className="composer">
          <textarea value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendQuestion(); } }} placeholder="Hỏi về quy tắc, quyền lợi, biểu phí…" rows={1} />
          <div className="composer-footer"><span>Enter để gửi · Shift + Enter để xuống dòng</span><button onClick={() => sendQuestion()} disabled={!query.trim() || loading} aria-label="Gửi câu hỏi"><ArrowUp size={20} /></button></div>
        </div>
        <p className="disclaimer">Thông tin chỉ mang tính tham khảo. Căn cứ cuối cùng là quy tắc và hợp đồng do doanh nghiệp bảo hiểm phát hành.</p>
      </div>
    </div>
  );
}

function Answer({ message, sourceOpen, setSourceOpen, feedback, setFeedback, setFeedbackOpen, citationMode, showExcerpts, showDetails, setToast, pipeline }) {
  const copy = () => { navigator.clipboard?.writeText(message.content); setToast("Đã sao chép câu trả lời và nguồn"); };
  return (
    <div className="assistant-row">
      <div className="avatar assistant-avatar"><Sparkles size={17} /></div>
      <div className="answer-wrap">
        <div className="answer-label">Trợ lý Bảo Việt</div>
        {message.refused && <div className="refusal-label"><ShieldCheck size={16} /> Từ chối an toàn · {ENUM_LABELS.refusal_reason[message.refusal_reason]}</div>}
        <div className={`answer-text ${message.refused ? "refused" : ""}`}>{message.content.split("\n").map((line, i) => <p key={i}>{formatLine(line, citationMode, setSourceOpen)}</p>)}</div>
        {citationMode === "footnote" && message.sources?.length > 0 && <div className="citation-list-note">Nguồn được hiển thị theo kiểu footnote ở cuối câu trả lời.</div>}
        {message.sources?.length > 0 && <SourceStack sources={message.sources} sourceOpen={sourceOpen} setSourceOpen={setSourceOpen} showExcerpts={showExcerpts} />}
        {showDetails && <ProcessingDetails pipeline={pipeline} runId={message.run_id} />}
        <div className="answer-actions">
          <button onClick={copy}><Copy size={16} /> Sao chép</button><span />
          <span>Câu trả lời này có hữu ích?</span>
          <button className={feedback === "up" ? "selected" : ""} onClick={() => { setFeedback("up"); setToast("Cảm ơn phản hồi của bạn"); }}><ThumbsUp size={16} /></button>
          <button className={feedback === "down" ? "selected" : ""} onClick={() => setFeedbackOpen(true)}><ThumbsDown size={16} /></button>
        </div>
      </div>
    </div>
  );
}

function StreamingAnswer({ text, loading }) {
  return <div className="assistant-row"><div className="avatar assistant-avatar"><Sparkles size={17} /></div><div className="answer-wrap"><div className="answer-label">Trợ lý Bảo Việt</div>{loading ? <div className="thinking"><strong>Đang tìm trong tài liệu chính thức</strong><div><i /><i /><i /></div><span>Truy xuất và kiểm tra nguồn phù hợp…</span></div> : <div className="answer-text streaming"><p>{text}<span className="stream-caret" /></p></div>}</div></div>;
}

function SourceStack({ sources, sourceOpen, setSourceOpen, showExcerpts }) {
  return <div className="source-stack"><div className="source-heading"><span><FileText size={17} /> Nguồn tham khảo</span><small>{sources.length} trích dẫn</small></div>{sources.map((s) => <div className={`source-card ${sourceOpen === s.ord ? "open" : ""}`} key={`${s.message_id}-${s.ord}`}><button onClick={() => setSourceOpen(sourceOpen === s.ord ? null : s.ord)}><span className="source-number">{s.ord}</span><span className="source-main"><strong>{s.section_path}</strong><small>{s.source_file} · Trang {s.page}</small></span><ChevronDown size={18} /></button>{sourceOpen === s.ord && <div className="source-detail">{showExcerpts && <p>“{s.text}”</p>}<div className="source-metadata"><code>{s.data_version}</code><code>{s.chunk_id}</code></div><a href={s.url} target="_blank" rel="noreferrer">Mở tài liệu gốc <ExternalLink size={14} /></a></div>}</div>)}</div>;
}

function ProcessingDetails({ pipeline, runId }) {
  return <div className="processing-detail-wrap"><div className="processing-panel"><div><span>run_id</span><strong>{runId}</strong></div><div><span>query_processed</span><strong>{TRACE.query_processed}</strong></div><div><span>detected_products</span><strong>{TRACE.detected_products.join(", ")}</strong></div><div><span>retrieval_mode</span><strong>{TRACE.retrieval_mode}</strong></div><div><span>latency_ms</span><strong>{TRACE.latency_ms}</strong></div><div><span>tokens_in / tokens_out</span><strong>{TRACE.tokens_in} / {TRACE.tokens_out}</strong></div><div><span>cost_usd</span><strong>{TRACE.cost_usd.toFixed(6)}</strong></div><div><span>timings_ms</span><strong>{Object.entries(TRACE.timings_ms).map(([key, value]) => `${key}: ${value}`).join(" · ")}</strong></div><div><span>error</span><strong>{TRACE.error || "—"}</strong></div></div><div className="retrieval-mini-table"><div><b>rank</b><b>chunk_id</b><b>score</b><b>rerank</b><b>in_context</b></div>{RETRIEVAL_LOGS.map((row) => <div key={`${row.message_id}-${row.rank}`}><span>{row.rank}</span><code>{row.chunk_id}</code><span>{row.score}</span><span>{row.rerank ?? "—"}</span><span>{row.in_context ? "true" : "false"}</span></div>)}</div><small className="admin-only-note"><ShieldCheck size={13} /> Chỉ quản trị viên được đọc traces và retrieval_logs.</small></div>;
}

function HistoryView({ items, search, setSearch, openHistory, menu, setMenu, setRenameItem, setDeleteItem, exportItem, printItem, clearAll }) {
  return <div className="standard-page"><div className="page-header"><div><p className="page-kicker">CONVERSATIONS + MESSAGES · OWNER RLS</p><h1>Lịch sử trò chuyện</h1><p>Snapshot messages và message_citations; không chạy lại pipeline khi mở lịch sử.</p></div><button className="danger-ghost" onClick={clearAll}><Trash2 size={16} /> Xóa tất cả</button></div><div className="toolbar"><label className="page-search"><Search size={17} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Tìm trong messages.content" /></label><span>{items.length} conversations</span></div><div className="history-page-list">{items.map((item) => <div className="history-row" key={item.id}><button className="history-row-main" onClick={() => openHistory(item)}><span className="history-row-icon"><MessagesSquare size={19} /></span><span><strong>{item.title} {item.title_is_custom && <b className="custom-title-badge">Đã đổi tên</b>}</strong><small>{item.preview}</small></span></button><time><strong>{formatDateTime(item.updated_at)}</strong><small>updated_at</small></time><div className="row-menu-wrap"><button className="icon-button" onClick={() => setMenu(menu === item.id ? null : item.id)}><MoreHorizontal size={19} /></button>{menu === item.id && <div className="row-menu"><button onClick={() => { setRenameItem(item); setMenu(null); }}><Pencil size={15} /> Đổi tên</button><button onClick={() => { exportItem(); setMenu(null); }}><Download size={15} /> Xuất Markdown</button><button onClick={() => { printItem(); setMenu(null); }}><FileText size={15} /> In / Lưu PDF</button><button className="danger" onClick={() => { setDeleteItem(item); setMenu(null); }}><Trash2 size={15} /> Xóa cascade</button></div>}</div></div>)}</div></div>;
}

function CatalogView() {
  const [selected, setSelected] = useState(PRODUCTS[0]);
  const version = DATA_VERSIONS.find((item) => item.is_active);
  const selectedDocuments = DOCUMENTS.filter((item) => item.product_code === selected.product_code);
  return <div className="standard-page">
    <div className="page-header">
      <div><p className="page-kicker">KHO TRI THỨC · DATA VERSION {version.version.toUpperCase()}</p><h1>Sản phẩm và tài liệu</h1><p>Danh mục đồng bộ một chiều từ catalog.json, sources.csv và chunks.jsonl.</p></div>
      <div className="version-badge"><CheckCircle2 size={17} /> {version.version} đang hoạt động · {version.n_chunks.toLocaleString("vi-VN")} chunks</div>
    </div>
    <div className="data-version-note"><strong>{version.note}</strong><span>created_at: {formatDateTime(version.created_at)}</span></div>
    <div className="catalog-layout">
      <div className="product-table card">
        <div className="table-head"><span>Sản phẩm</span><span>line</span><span>documents</span><span>chunks</span></div>
        {PRODUCTS.map((product) => {
          const documentCount = DOCUMENTS.filter((item) => item.product_code === product.product_code).length;
          const chunkCount = CHUNKS.filter((item) => item.product_code === product.product_code && item.data_version === version.version).length;
          return <button key={product.product_code} onClick={() => setSelected(product)} className={selected.product_code === product.product_code ? "selected" : ""}>
            <span><b>{product.product_code}</b><strong>{product.product_name}</strong></span>
            <span>{ENUM_LABELS.line[product.line] || product.line}</span><span>{documentCount}</span><span>{chunkCount}</span>
          </button>;
        })}
      </div>
      <aside className="product-detail card">
        <div className="product-detail-head"><span className="product-code">{selected.product_code}</span><b className={`status-tag ${selected.is_active ? "" : "muted"}`}>{selected.is_active ? "Đang hoạt động" : "Ngừng hoạt động"}</b></div>
        <h2>{selected.product_name}</h2><p>company: {selected.company} · line: {selected.line}</p><hr />
        <h3>Tài liệu trong kho</h3>
        {selectedDocuments.length ? selectedDocuments.map((document) => <a key={document.id} href={document.url} target="_blank" rel="noreferrer">
          <FileText size={16} /><span><strong>{ENUM_LABELS.doc_type[document.doc_type]}</strong><small>{document.source_file} · hiệu lực {formatDate(document.effective_date)}</small><small>Tải ngày {formatDate(document.downloaded_at)}</small></span><ExternalLink size={14} />
        </a>) : <p className="empty-copy">Chưa có document được đồng bộ cho sản phẩm này.</p>}
      </aside>
    </div>
  </div>;
}

function DashboardView({ setToast }) {
  const chartData = PIPELINE_CONFIGS.map((config) => {
    const recall = EVAL_RESULTS.find((item) => item.run_id.startsWith(config.name) && item.question_group === "all" && item.metric === "recall@5")?.value || 0;
    const faithfulness = EVAL_RESULTS.find((item) => item.run_id.startsWith(config.name) && item.question_group === "all" && item.metric === "faithfulness")?.value || 0;
    return { name: config.name, recall, faithfulness };
  });
  return <div className="standard-page"><div className="page-header"><div><p className="page-kicker">VIEW THỐNG KÊ + EVAL_RESULTS · ADMIN ONLY</p><h1>Dashboard chỉ số</h1><p>Metric được nhóm theo run_id, question_group, metric và value.</p></div><button className="secondary-button" onClick={() => setToast("Đã đọc lại view thống kê và eval_results")}><RefreshCw size={16} /> Làm mới</button></div><div className="metric-grid"><Metric label="Câu hỏi hôm nay" value="128" delta="View thống kê" icon={MessagesSquare} /><Metric label="Độ trễ p95" value="4,8s" delta="traces.latency_ms" icon={Gauge} /><Metric label="Tỷ lệ từ chối" value="18,7%" delta="messages.refused" icon={ShieldCheck} /><Metric label="Đánh giá tích cực" value="91,4%" delta="feedback.rating" icon={ThumbsUp} /></div><div className="dashboard-grid"><div className="card chart-card"><div className="card-title"><div><h2>eval_results theo cấu hình</h2><p>question_group = all</p></div><BarChart3 size={20} /></div><div className="bar-chart">{chartData.map((item) => <div className="bar-group" key={item.name}><span>{item.name}</span><div><i style={{ height: `${item.recall * 100}%` }} /><i style={{ height: `${item.faithfulness * 100}%` }} /></div><small>{Math.round(item.recall * 100)}%</small></div>)}</div><div className="chart-legend"><span><i className="blue" /> metric: recall@5</span><span><i className="gold" /> metric: faithfulness</span></div></div><div className="card activity-card"><div className="card-title"><div><h2>Phân bố truy vấn</h2><p>View thống kê · 7 ngày gần nhất</p></div></div>{[["lookup", 42], ["table", 21], ["compare", 17], ["scenario", 14], ["refused", 6]].map(([group, value]) => <div className="progress-row" key={group}><span>{ENUM_LABELS.question_group[group] || group}</span><div><i style={{ width: `${value * 2}%` }} /></div><strong>{value}%</strong></div>)}</div></div></div>;
}

function Metric({ label, value, delta, icon: Icon }) {
  return <div className="metric-card card"><span><Icon size={19} /></span><small>{label}</small><strong>{value}</strong><p>{delta}</p></div>;
}

function LogsView({ setToast }) {
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
  return <div className="standard-page"><div className="page-header"><div><p className="page-kicker">GIÁM SÁT TRUY VẤN · ADMIN ONLY</p><h1>Nhật ký truy vấn</h1><p>Joined view từ messages, traces, feedback và runs; log.jsonl không bị xóa cùng hội thoại.</p></div><button className="secondary-button" onClick={exportCsv}><Download size={16} /> Xuất CSV</button></div><div className="toolbar log-toolbar"><label className="page-search"><Search size={17} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Tìm theo content hoặc run_id" /></label><div className="filter-chips">{["Tất cả", "Từ chối", "Không hữu ích", "Độ trễ cao"].map((x) => <button key={x} className={filter === x ? "active" : ""} onClick={() => setFilter(x)}>{x}</button>)}</div></div><div className="data-table card"><div className="data-row head"><span>created_at / run_id</span><span>messages.content</span><span>refused</span><span>config / version</span><span>latency_ms</span><span>feedback</span></div>{visibleLogs.map((log) => <button className="data-row" key={log.message_id} onClick={() => setToast(`Đã mở trace của ${log.run_id}`)}><span><strong>{formatDateTime(log.created_at)}</strong><small>{log.run_id}</small></span><span>{log.content}</span><span><b className={`status-tag ${log.refused ? "warning" : ""}`}>{log.refused ? ENUM_LABELS.refusal_reason[log.refusal_reason] : "false"}</b></span><span><strong>{log.config_name}</strong><small>{log.data_version} · {log.split} · {log.runtime}</small></span><span>{log.latency_ms}</span><span>{log.rating === 1 ? "1 · Hữu ích" : log.rating === -1 ? `-1 · ${ENUM_LABELS.feedback_reason[log.feedback_reason]}` : "—"}</span></button>)}</div></div>;
}

function AccountsView({ setToast }) {
  const [accounts, setAccounts] = useState(ACCOUNTS);
  const [createOpen, setCreateOpen] = useState(false);
  return <div className="standard-page"><div className="page-header"><div><p className="page-kicker">AUTH.USERS + PROFILES · ADMIN ONLY</p><h1>Tài khoản demo</h1><p>Supabase Auth quản lý mật khẩu; hồ sơ chỉ dùng email giả, username, display_name và role.</p></div><button className="primary-button" onClick={() => setCreateOpen(true)}><Plus size={17} /> Tạo tài khoản</button></div><div className="data-table accounts-table card"><div className="data-row head"><span>username / email</span><span>role</span><span>is_active</span><span>last_sign_in_at</span><span>Thao tác</span></div>{accounts.map((account) => <div className="data-row" key={account.id}><span className="account-name"><i>{account.username.slice(0, 2).toUpperCase()}</i><span><strong>{account.display_name || account.username}</strong><small>{account.username} · {account.email}</small></span></span><span><b className="enum-code">{account.role}</b><small>{ENUM_LABELS.user_role[account.role]}</small></span><span><b className={`status-tag ${account.is_active ? "" : "muted"}`}>{String(account.is_active)}</b>{account.banned_until && <small>banned_until: {formatDateTime(account.banned_until)}</small>}</span><span>{account.last_sign_in_at ? formatDateTime(account.last_sign_in_at) : "Chưa đăng nhập"}</span><span className="account-actions"><button onClick={() => { setAccounts((current) => current.map((x) => x.id === account.id ? { ...x, role: x.role === "user" ? "admin" : "user" } : x)); setToast("Đã cập nhật profiles.role"); }}>Đổi role</button><button onClick={() => { setAccounts((current) => current.map((x) => x.id === account.id ? { ...x, is_active: !x.is_active, banned_until: x.is_active ? "2026-12-20T09:31:05+07:00" : null } : x)); setToast(account.is_active ? "Đã khóa tài khoản" : "Đã mở khóa tài khoản"); }}>{account.is_active ? "Khóa" : "Mở khóa"}</button><button onClick={() => setToast("Supabase Auth đã tạo mật khẩu tạm thời")}>Đặt lại mật khẩu</button></span></div>)}</div>{createOpen && <CreateAccount existingUsernames={accounts.map((account) => account.username)} existingEmails={accounts.map((account) => account.email)} onClose={() => setCreateOpen(false)} onSave={(account) => { setAccounts((current) => [...current, { ...account, id: crypto.randomUUID(), is_active: true, last_sign_in_at: null, banned_until: null }]); setCreateOpen(false); setToast("Đã tạo auth.users và profiles"); }} />}</div>;
}

function CompareView() {
  const [left, setLeft] = useState("B0");
  const [right, setRight] = useState("B4");
  const [question, setQuestion] = useState("Thời hạn giải quyết quyền lợi bảo hiểm An Gia là bao lâu?");
  const [ran, setRan] = useState(false);
  const [compareSourceOpen, setCompareSourceOpen] = useState(null);
  return <div className="standard-page"><div className="page-header"><div><p className="page-kicker">2 MESSAGES CÙNG REPLY_TO_ID · KHÁC RUN_ID</p><h1>So sánh hai cấu hình</h1><p>Chạy cùng một câu hỏi và đối chiếu câu trả lời, nguồn cùng độ trễ.</p></div></div><div className="compare-query card"><label>messages.content<input value={question} onChange={(e) => setQuestion(e.target.value)} /></label><button className="primary-button" onClick={() => setRan(true)}><Sparkles size={17} /> Chạy so sánh</button></div><div className="compare-grid">{[[left, setLeft, false], [right, setRight, true]].map(([value, setter, rag], index) => { const config = PIPELINE_CONFIGS.find((item) => item.name === value); return <div className="compare-column card" key={index}><div className="compare-head"><label>config_name<select value={value} onChange={(e) => setter(e.target.value)}>{PIPELINE_CONFIGS.map((item) => <option key={item.name} value={item.name}>{item.name}</option>)}</select></label><span>{config.description}</span></div>{ran ? <><div className="compare-answer"><Bot size={20} /><p>{rag ? "Bảo Việt giải quyết quyền lợi trong 15 ngày làm việc kể từ khi nhận đủ hồ sơ hợp lệ. [1]" : "Thông thường doanh nghiệp bảo hiểm sẽ xử lý hồ sơ trong một khoảng thời gian hợp lý theo quy định."}</p></div><div className="compare-stats"><span>run_id<strong>{value}_demo_20261120-1100</strong></span><span>latency_ms<strong>{rag ? "3204" : "1408"}</strong></span><span>Nguồn<strong>{rag ? "2" : "0"}</strong></span></div>{rag && <SourceStack sources={[SOURCES[0]]} sourceOpen={compareSourceOpen} setSourceOpen={setCompareSourceOpen} showExcerpts={false} />}</> : <div className="empty-compare"><Gauge size={27} /><p>Chạy so sánh để xem kết quả cấu hình {value}</p></div>}</div>; })}</div></div>;
}

function SettingsPanel({ onClose, theme, setTheme, fontSize, setFontSize, citationMode, setCitationMode, showExcerpts, setShowExcerpts, showDetails, setShowDetails, role }) {
  return <div className="modal-layer"><button className="modal-scrim" onClick={onClose} /><div className="settings-panel"><div className="settings-title"><div><span>user_settings</span><h2>Tùy chỉnh trải nghiệm</h2></div><button className="icon-button" onClick={onClose}><X size={20} /></button></div><section><h3>theme · theme_mode</h3><div className="theme-options three"><button className={theme === "light" ? "active" : ""} onClick={() => setTheme("light")}><Sun size={20} /> light</button><button className={theme === "dark" ? "active" : ""} onClick={() => setTheme("dark")}><Moon size={20} /> dark</button><button className={theme === "system" ? "active" : ""} onClick={() => setTheme("system")}><Settings size={20} /> system</button></div><div className="range-setting"><span><strong>font_size</strong><small>smallint · CHECK 12–20 · mặc định 14</small></span><input type="range" min="12" max="20" step="1" value={fontSize} onChange={(event) => setFontSize(Number(event.target.value))} /><b>{fontSize}px</b></div></section><section><h3>Trích dẫn</h3><div className="radio-setting"><span><strong>citation_style</strong><small>enum: inline | footnote</small></span><label><input type="radio" checked={citationMode === "inline"} onChange={() => setCitationMode("inline")} /> inline</label><label><input type="radio" checked={citationMode === "footnote"} onChange={() => setCitationMode("footnote")} /> footnote</label></div><Toggle label="show_source_text" detail="boolean · mặc định true" value={showExcerpts} setValue={setShowExcerpts} />{role === "admin" && <Toggle label="Chi tiết xử lý" detail="Admin only · traces và retrieval_logs" value={showDetails} setValue={setShowDetails} />}</section><p className="settings-updated">updated_at được cập nhật tự động khi lưu.</p></div></div>;
}

function Toggle({ label, detail, value, setValue }) {
  return <div className="setting-row"><div><strong>{label}</strong><small>{detail}</small></div><button className={`switch ${value ? "on" : ""}`} onClick={() => setValue(!value)} aria-pressed={value}><span /></button></div>;
}

function SystemModal({ onClose }) {
  const [checking, setChecking] = useState(false);
  return <Modal title="Trạng thái hệ thống" subtitle="Kiểm tra trước khi bắt đầu phiên demo" onClose={onClose} wide><div className="system-summary"><CheckCircle2 size={24} /><div><strong>{checking ? "Đang kiểm tra các thành phần…" : "Tất cả thành phần đang hoạt động"}</strong><small>Kiểm tra gần nhất: vừa xong</small></div><button onClick={() => { setChecking(true); setTimeout(() => setChecking(false), 900); }}><RefreshCw className={checking ? "spin" : ""} size={16} /> Kiểm tra lại</button></div><div className="system-list">{SYSTEMS.map((s) => <div key={s.name}><span className="system-icon"><Activity size={18} /></span><span><strong>{s.name}</strong><small>{s.detail}</small></span><b><i /> {s.status}</b><em>{s.metric}</em></div>)}</div></Modal>;
}

function FeedbackModal({ onClose, onSave }) {
  const [reason, setReason] = useState("");
  const [comment, setComment] = useState("");
  return <Modal title="Điều gì cần cải thiện?" subtitle="feedback.rating = -1 nên reason là bắt buộc." onClose={onClose}><div className="reason-list">{Object.entries(ENUM_LABELS.feedback_reason).map(([value, label]) => <label key={value}><input type="radio" name="reason" checked={reason === value} onChange={() => setReason(value)} /><span><strong>{label}</strong><small>{value}</small></span></label>)}</div><label className="modal-field">comment<textarea value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Ghi chú thêm (không bắt buộc)" /></label><div className="modal-actions"><button className="secondary-button" onClick={onClose}>Hủy</button><button className="primary-button" disabled={!reason} onClick={() => onSave({ rating: -1, reason, comment: comment || null })}>Gửi phản hồi</button></div></Modal>;
}

function RenameModal({ item, onClose, onSave }) {
  const [name, setName] = useState(item.title);
  return <Modal title="Đổi tên cuộc trò chuyện" subtitle="Tên mới giúp bạn tìm lại nội dung nhanh hơn." onClose={onClose}><label className="modal-field">Tên cuộc trò chuyện<input value={name} onChange={(e) => setName(e.target.value)} autoFocus /></label><div className="modal-actions"><button className="secondary-button" onClick={onClose}>Hủy</button><button className="primary-button" onClick={() => onSave(name)} disabled={!name.trim()}>Lưu thay đổi</button></div></Modal>;
}

function ConfirmModal({ item, onClose, onConfirm }) {
  return <Modal title="Xác nhận xóa" subtitle={`Bạn sắp xóa ${item.all ? "toàn bộ lịch sử" : `“${item.title}”`}. Hành động này không thể hoàn tác.`} onClose={onClose}><div className="delete-warning"><Trash2 size={21} /> Log thực nghiệm trong hệ thống quản trị sẽ không bị ảnh hưởng.</div><div className="modal-actions"><button className="secondary-button" onClick={onClose}>Hủy</button><button className="danger-button" onClick={onConfirm}>Xóa vĩnh viễn</button></div></Modal>;
}

function CreateAccount({ existingUsernames, existingEmails, onClose, onSave }) {
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("user");
  const validEmail = /^demo\d+@bv-rag\.local$/.test(email);
  const duplicateUsername = existingUsernames.includes(username);
  const duplicateEmail = existingEmails.includes(email);
  return <Modal title="Tạo tài khoản demo" subtitle="Email bắt buộc dùng miền giả @bv-rag.local; sign-up công khai bị tắt." onClose={onClose}><label className="modal-field">username * · UQ<input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="demo04" />{duplicateUsername && <small className="field-error">username đã tồn tại.</small>}</label><label className="modal-field">display_name<input value={displayName} onChange={(e) => setDisplayName(e.target.value)} placeholder="Người dùng demo 04" /></label><label className="modal-field">email giả * · UQ<input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="demo04@bv-rag.local" />{email && !validEmail && <small className="field-error">Định dạng yêu cầu: demoNN@bv-rag.local</small>}{duplicateEmail && <small className="field-error">email đã tồn tại.</small>}</label><label className="modal-field">role *<select value={role} onChange={(e) => setRole(e.target.value)}><option value="user">user</option><option value="admin">admin</option></select></label><div className="modal-actions"><button className="secondary-button" onClick={onClose}>Hủy</button><button className="primary-button" disabled={!username || !validEmail || duplicateUsername || duplicateEmail} onClick={() => onSave({ username, display_name: displayName || null, email, role })}>Tạo tài khoản</button></div></Modal>;
}

function SessionExpired({ onLogin, onLogout }) {
  return <div className="modal-layer session-layer"><div className="modal-card session-card"><span className="session-lock"><LockKeyhole size={24} /></span><h2>Phiên làm việc đã hết hạn</h2><p>Để bảo vệ phiên demo, hệ thống tự động đăng xuất sau 30 phút không hoạt động.</p><button className="primary-button" onClick={onLogin}>Tiếp tục phiên làm việc</button><button className="text-button" onClick={onLogout}>Quay về đăng nhập</button></div></div>;
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
