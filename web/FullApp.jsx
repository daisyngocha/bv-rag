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

const PRODUCTS = [
  { code: "BVP", name: "Bảo Việt An Gia", type: "Sức khỏe", docs: 6, chunks: 842, effective: "27/06/2025" },
  { code: "BTB", name: "Bảo Việt Tâm Bình", type: "Sức khỏe", docs: 5, chunks: 614, effective: "27/06/2025" },
  { code: "ITC", name: "Bảo Việt Intercare", type: "Sức khỏe cao cấp", docs: 7, chunks: 936, effective: "27/06/2025" },
  { code: "C37", name: "37 bệnh hiểm nghèo", type: "Bệnh hiểm nghèo", docs: 4, chunks: 471, effective: "27/06/2025" },
  { code: "FLX", name: "Du lịch Flexi", type: "Du lịch", docs: 8, chunks: 755, effective: "27/06/2025" },
];

const INITIAL_HISTORY = [
  { id: 1, title: "Quyền lợi nội trú An Gia", preview: "Thời hạn giải quyết quyền lợi bảo hiểm...", time: "10:42 hôm nay" },
  { id: 2, title: "So sánh CI37 và Intercare", preview: "So sánh độ tuổi tham gia...", time: "Hôm qua" },
  { id: 3, title: "Phí bảo hiểm du lịch Flexi", preview: "Phí gia đình hạng Kim Cương...", time: "12/11" },
  { id: 4, title: "Thời gian chờ Tâm Bình", preview: "Thời gian chờ quyền lợi thai sản...", time: "10/11" },
];

const SAMPLE_QUESTIONS = [
  ["Tra cứu quy tắc", "Thời hạn giải quyết quyền lợi bảo hiểm An Gia là bao lâu?"],
  ["Quyền lợi", "Trẻ 2 tuổi nằm viện nội trú được hưởng quyền lợi gì trong An Gia?"],
  ["So sánh", "So sánh độ tuổi tham gia của CI37 và Intercare."],
  ["Bảng phí", "Phí gia đình của Flexi hạng Kim Cương cho chuyến đi 204–210 ngày?"],
];

const SOURCES = [
  {
    id: 1,
    title: "Chương IV › Điều 18 › Khoản 2",
    doc: "Quy tắc bảo hiểm sức khỏe Bảo Việt An Gia",
    page: 24,
    text: "Trong thời hạn 15 ngày làm việc kể từ ngày nhận được đầy đủ hồ sơ yêu cầu trả tiền bảo hiểm hợp lệ, Bảo Việt có trách nhiệm xem xét và giải quyết quyền lợi bảo hiểm.",
  },
  {
    id: 2,
    title: "Chương IV › Điều 17 › Khoản 1",
    doc: "Quy tắc bảo hiểm sức khỏe Bảo Việt An Gia",
    page: 23,
    text: "Người được bảo hiểm hoặc người thụ hưởng có trách nhiệm gửi hồ sơ yêu cầu trả tiền bảo hiểm theo danh mục chứng từ được quy định cho từng quyền lợi.",
  },
];

const LOGS = [
  { id: "run_8f20", query: "Thời hạn giải quyết quyền lợi An Gia?", status: "Đã trả lời", latency: "3,2 giây", rating: "Hữu ích", config: "B4", time: "10:42" },
  { id: "run_8f19", query: "Bảo hiểm xe ô tô có quyền lợi gì?", status: "Từ chối", latency: "1,1 giây", rating: "—", config: "B4", time: "10:31" },
  { id: "run_8f18", query: "So sánh CI37 và Intercare", status: "Đã trả lời", latency: "4,8 giây", rating: "Không hữu ích", config: "B4", time: "09:58" },
  { id: "run_8f17", query: "Phí Flexi hạng Kim Cương 210 ngày", status: "Đã trả lời", latency: "2,9 giây", rating: "Hữu ích", config: "B3", time: "09:34" },
];

const ACCOUNTS = [
  { id: 1, username: "nguyentha", role: "Quản trị viên", status: "Hoạt động", last: "Vừa xong" },
  { id: 2, username: "demo_user", role: "Người dùng", status: "Hoạt động", last: "Hôm qua" },
  { id: 3, username: "reviewer", role: "Người dùng", status: "Đã khóa", last: "05/11/2026" },
];

const SYSTEMS = [
  { name: "FastAPI", detail: "Phiên bản 0.162.1 · /health", status: "Sẵn sàng", metric: "42 ms" },
  { name: "Ollama", detail: "qwen2.5:7b-instruct-q4_K_M", status: "Đã nạp", metric: "GPU 100%" },
  { name: "Qdrant", detail: "5 collections · data_version v1", status: "Sẵn sàng", metric: "3.618 chunks" },
  { name: "Embedding & reranker", detail: "bge-m3 · bge-reranker-v2-m3", status: "Sẵn sàng", metric: "L4" },
];

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
  const [theme, setTheme] = useState("light");
  const [largeText, setLargeText] = useState(false);
  const [citationMode, setCitationMode] = useState("inline");
  const [showExcerpts, setShowExcerpts] = useState(true);
  const [showDetails, setShowDetails] = useState(false);
  const [pipeline, setPipeline] = useState("B4");
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
    const clean = maskSensitive(question.trim());
    if (!clean || loading) return;
    setMessages((current) => [...current, { role: "user", text: clean }]);
    setQuery("");
    setLoading(true);
    setStreamText("");
    setFeedback(null);
    if (!messages.length) {
      setHistory((current) => [
        { id: Date.now(), title: clean.slice(0, 48), preview: clean, time: "Vừa xong" },
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
            { role: "assistant", text: response, refused: outOfScope, sources: outOfScope ? [] : SOURCES },
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
      { role: "user", text: item.preview },
      { role: "assistant", text: "Đây là snapshot câu trả lời đã lưu tại thời điểm truy vấn. Nội dung không được chạy lại để bảo toàn cấu hình và nguồn trích dẫn.", sources: SOURCES },
    ]);
    setView("chat");
    setHistoryMenu(null);
  }

  function downloadConversation() {
    const body = messages.map((m) => `## ${m.role === "user" ? "Người dùng" : "Trợ lý"}\n\n${m.text}`).join("\n\n");
    const sourceList = SOURCES.map((s) => `- [${s.id}] ${s.doc}, ${s.title}, trang ${s.page}`).join("\n");
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
    <div className={`full-app theme-${theme} ${largeText ? "large-text" : ""}`}>
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
              <span>NH</span><span className="profile-copy"><strong>Ngọc Hà</strong><small>{role === "admin" ? "Quản trị viên" : "Người dùng"}</small></span><ChevronDown size={16} />
            </button>
            {profileOpen && (
              <div className="profile-menu">
                <div className="profile-menu-head"><strong>nguyentha</strong><small>Phiên demo · không lưu dữ liệu cá nhân</small></div>
                <button onClick={() => { setRole(role === "admin" ? "user" : "admin"); setProfileOpen(false); setToast(`Đã chuyển sang vai trò ${role === "admin" ? "Người dùng" : "Quản trị viên"}`); }}>
                  <UserCog size={17} /> Chuyển sang {role === "admin" ? "Người dùng" : "Quản trị viên"}
                </button>
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
          largeText={largeText}
          setLargeText={setLargeText}
          citationMode={citationMode}
          setCitationMode={setCitationMode}
          showExcerpts={showExcerpts}
          setShowExcerpts={setShowExcerpts}
          showDetails={showDetails}
          setShowDetails={setShowDetails}
        />
      )}
      {systemOpen && <SystemModal onClose={() => setSystemOpen(false)} />}
      {feedbackOpen && <FeedbackModal onClose={() => setFeedbackOpen(false)} onSave={() => { setFeedback("down"); setFeedbackOpen(false); setToast("Đã lưu lý do phản hồi"); }} />}
      {renameItem && <RenameModal item={renameItem} onClose={() => setRenameItem(null)} onSave={(name) => { setHistory((current) => current.map((item) => item.id === renameItem.id ? { ...item, title: name } : item)); setRenameItem(null); setToast("Đã đổi tên cuộc trò chuyện"); }} />}
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
        <label>Tên đăng nhập<input defaultValue="nguyentha" autoComplete="username" /></label>
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
          {role === "admin" && <label className="pipeline-select">Pipeline<select value={pipeline} onChange={(e) => setPipeline(e.target.value)}>{["B0", "B1", "B2", "B3", "B4"].map((x) => <option key={x}>{x}</option>)}</select></label>}
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
            <div className="sample-grid">{SAMPLE_QUESTIONS.map(([group, question]) => <button key={question} onClick={() => sendQuestion(question)}><span>{group}</span><strong>{question}</strong><ArrowUp size={18} /></button>)}</div>
          </div>
        ) : (
          <div className="conversation">
            {privacyMasked && <div className="privacy-banner"><ShieldCheck size={17} /><span>Thông tin nhạy cảm đã được tự động che trước khi lưu lịch sử.</span><button onClick={() => setPrivacyMasked(false)}><X size={16} /></button></div>}
            {messages.map((message, index) => message.role === "user"
              ? <div className="user-row" key={index}><div className="user-bubble">{message.text}</div><div className="avatar user-avatar"><UserRound size={17} /></div></div>
              : <Answer key={index} message={message} sourceOpen={sourceOpen} setSourceOpen={setSourceOpen} feedback={feedback} setFeedback={setFeedback} setFeedbackOpen={setFeedbackOpen} citationMode={citationMode} showExcerpts={showExcerpts} showDetails={showDetails} setToast={setToast} pipeline={pipeline} />
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
            {scopeOpen && <div className="scope-menu"><div><strong>Phạm vi sản phẩm</strong><small>Có thể chọn nhiều sản phẩm để so sánh</small></div>{PRODUCTS.map((p) => <button key={p.code} onClick={() => setSelectedProducts(selectedProducts.includes(p.code) ? selectedProducts.filter((x) => x !== p.code) : [...selectedProducts, p.code])}><span className={`checkbox ${selectedProducts.includes(p.code) ? "checked" : ""}`}>{selectedProducts.includes(p.code) && <Check size={13} />}</span><span><strong>{p.name}</strong><small>{p.code}</small></span></button>)}</div>}
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
  const copy = () => { navigator.clipboard?.writeText(message.text); setToast("Đã sao chép câu trả lời và nguồn"); };
  return (
    <div className="assistant-row">
      <div className="avatar assistant-avatar"><Sparkles size={17} /></div>
      <div className="answer-wrap">
        <div className="answer-label">Trợ lý Bảo Việt</div>
        {message.refused && <div className="refusal-label"><ShieldCheck size={16} /> Từ chối an toàn · Không đủ căn cứ</div>}
        <div className={`answer-text ${message.refused ? "refused" : ""}`}>{message.text.split("\n").map((line, i) => <p key={i}>{formatLine(line, citationMode, setSourceOpen)}</p>)}</div>
        {citationMode === "list" && message.sources?.length > 0 && <div className="citation-list-note">Nguồn được liệt kê theo thứ tự ở cuối câu trả lời.</div>}
        {message.sources?.length > 0 && <SourceStack sources={message.sources} sourceOpen={sourceOpen} setSourceOpen={setSourceOpen} showExcerpts={showExcerpts} />}
        {showDetails && <ProcessingDetails pipeline={pipeline} />}
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
  return <div className="source-stack"><div className="source-heading"><span><FileText size={17} /> Nguồn tham khảo</span><small>{sources.length} trích dẫn</small></div>{sources.map((s) => <div className={`source-card ${sourceOpen === s.id ? "open" : ""}`} key={s.id}><button onClick={() => setSourceOpen(sourceOpen === s.id ? null : s.id)}><span className="source-number">{s.id}</span><span className="source-main"><strong>{s.title}</strong><small>{s.doc} · Trang {s.page}</small></span><ChevronDown size={18} /></button>{sourceOpen === s.id && <div className="source-detail">{showExcerpts && <p>“{s.text}”</p>}<a href="https://baovietonline.com.vn/" target="_blank" rel="noreferrer">Mở tài liệu gốc <ExternalLink size={14} /></a></div>}</div>)}</div>;
}

function ProcessingDetails({ pipeline }) {
  return <div className="processing-panel"><div><span>Query sau xử lý</span><strong>thời hạn giải quyết quyền lợi an gia</strong></div><div><span>Pipeline</span><strong>{pipeline} · Hybrid + Reranker</strong></div><div><span>Rerank max</span><strong>0,824</strong></div><div><span>Token</span><strong>1.284 vào · 126 ra</strong></div><div><span>Độ trễ</span><strong>3.204 ms</strong></div></div>;
}

function HistoryView({ items, search, setSearch, openHistory, menu, setMenu, setRenameItem, setDeleteItem, exportItem, printItem, clearAll }) {
  return <div className="standard-page"><div className="page-header"><div><p className="page-kicker">KHÔNG GIAN CÁ NHÂN</p><h1>Lịch sử trò chuyện</h1><p>Xem lại nguyên trạng câu trả lời và nguồn tại thời điểm truy vấn.</p></div><button className="danger-ghost" onClick={clearAll}><Trash2 size={16} /> Xóa tất cả</button></div><div className="toolbar"><label className="page-search"><Search size={17} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Tìm trong câu hỏi hoặc câu trả lời" /></label><span>{items.length} cuộc trò chuyện</span></div><div className="history-page-list">{items.map((item) => <div className="history-row" key={item.id}><button className="history-row-main" onClick={() => openHistory(item)}><span className="history-row-icon"><MessagesSquare size={19} /></span><span><strong>{item.title}</strong><small>{item.preview}</small></span></button><time>{item.time}</time><div className="row-menu-wrap"><button className="icon-button" onClick={() => setMenu(menu === item.id ? null : item.id)}><MoreHorizontal size={19} /></button>{menu === item.id && <div className="row-menu"><button onClick={() => { setRenameItem(item); setMenu(null); }}><Pencil size={15} /> Đổi tên</button><button onClick={() => { exportItem(); setMenu(null); }}><Download size={15} /> Xuất Markdown</button><button onClick={() => { printItem(); setMenu(null); }}><FileText size={15} /> In / Lưu PDF</button><button className="danger" onClick={() => { setDeleteItem(item); setMenu(null); }}><Trash2 size={15} /> Xóa</button></div>}</div></div>)}</div></div>;
}

function CatalogView() {
  const [selected, setSelected] = useState(PRODUCTS[0]);
  return <div className="standard-page"><div className="page-header"><div><p className="page-kicker">KHO TRI THỨC · DATA VERSION V1</p><h1>Sản phẩm và tài liệu</h1><p>Danh mục tài liệu công khai đang được sử dụng để trả lời.</p></div><div className="version-badge"><CheckCircle2 size={17} /> Cập nhật 08/11/2026</div></div><div className="catalog-layout"><div className="product-table card"><div className="table-head"><span>Sản phẩm</span><span>Loại</span><span>Tài liệu</span><span>Chunks</span></div>{PRODUCTS.map((p) => <button key={p.code} onClick={() => setSelected(p)} className={selected.code === p.code ? "selected" : ""}><span><b>{p.code}</b><strong>{p.name}</strong></span><span>{p.type}</span><span>{p.docs}</span><span>{p.chunks.toLocaleString("vi-VN")}</span></button>)}</div><aside className="product-detail card"><span className="product-code">{selected.code}</span><h2>{selected.name}</h2><p>{selected.type} · Hiệu lực {selected.effective}</p><hr /><h3>Tài liệu trong kho</h3>{["Quy tắc bảo hiểm", "Bảng quyền lợi", "Biểu phí", "Tài liệu giới thiệu"].map((x, i) => <a key={x} href="https://baovietonline.com.vn/" target="_blank" rel="noreferrer"><FileText size={16} /><span><strong>{x}</strong><small>PDF · {12 + i * 4} trang</small></span><ExternalLink size={14} /></a>)}</aside></div></div>;
}

function DashboardView({ setToast }) {
  return <div className="standard-page"><div className="page-header"><div><p className="page-kicker">TỔNG QUAN VẬN HÀNH</p><h1>Dashboard chỉ số</h1><p>Dữ liệu phiên demo và kết quả thực nghiệm B0–B4.</p></div><button className="secondary-button" onClick={() => setToast("Đã cập nhật số liệu dashboard")}><RefreshCw size={16} /> Làm mới</button></div><div className="metric-grid"><Metric label="Câu hỏi hôm nay" value="128" delta="+12%" icon={MessagesSquare} /><Metric label="Độ trễ p95" value="4,8s" delta="-0,4s" icon={Gauge} /><Metric label="Tỷ lệ từ chối" value="18,7%" delta="Đúng phạm vi" icon={ShieldCheck} /><Metric label="Đánh giá tích cực" value="91,4%" delta="+3,2%" icon={ThumbsUp} /></div><div className="dashboard-grid"><div className="card chart-card"><div className="card-title"><div><h2>Chất lượng theo cấu hình</h2><p>Recall@5 và Faithfulness</p></div><BarChart3 size={20} /></div><div className="bar-chart">{[["B0", 24, 42], ["B1", 56, 61], ["B2", 72, 74], ["B3", 84, 82], ["B4", 91, 89]].map(([name, recall, faith]) => <div className="bar-group" key={name}><span>{name}</span><div><i style={{ height: `${recall}%` }} /><i style={{ height: `${faith}%` }} /></div><small>{recall}%</small></div>)}</div><div className="chart-legend"><span><i className="blue" /> Recall@5</span><span><i className="gold" /> Faithfulness</span></div></div><div className="card activity-card"><div className="card-title"><div><h2>Phân bố truy vấn</h2><p>7 ngày gần nhất</p></div></div>{[["Tra cứu", 42], ["Bảng phí", 21], ["So sánh", 17], ["Tình huống", 14], ["Ngoài phạm vi", 6]].map(([x, n]) => <div className="progress-row" key={x}><span>{x}</span><div><i style={{ width: `${n * 2}%` }} /></div><strong>{n}%</strong></div>)}</div></div></div>;
}

function Metric({ label, value, delta, icon: Icon }) {
  return <div className="metric-card card"><span><Icon size={19} /></span><small>{label}</small><strong>{value}</strong><p>{delta}</p></div>;
}

function LogsView({ setToast }) {
  const [filter, setFilter] = useState("Tất cả");
  const [search, setSearch] = useState("");
  const visibleLogs = LOGS.filter((l) => (filter === "Tất cả" || (filter === "Từ chối" && l.status === "Từ chối") || (filter === "Không hữu ích" && l.rating === "Không hữu ích") || (filter === "Độ trễ cao" && parseFloat(l.latency) > 4)) && `${l.id} ${l.query}`.toLowerCase().includes(search.toLowerCase()));
  const exportCsv = () => {
    const csv = ["run_id,query,status,config,latency,rating", ...visibleLogs.map((l) => [l.id, `"${l.query}"`, l.status, l.config, l.latency, l.rating].join(","))].join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "nhat-ky-truy-van.csv";
    anchor.click();
    URL.revokeObjectURL(url);
    setToast("Đã xuất nhật ký CSV");
  };
  return <div className="standard-page"><div className="page-header"><div><p className="page-kicker">GIÁM SÁT TRUY VẤN</p><h1>Nhật ký truy vấn</h1><p>Lọc các câu bị từ chối, phản hồi xấu hoặc có độ trễ cao.</p></div><button className="secondary-button" onClick={exportCsv}><Download size={16} /> Xuất CSV</button></div><div className="toolbar log-toolbar"><label className="page-search"><Search size={17} /><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Tìm theo câu hỏi hoặc run ID" /></label><div className="filter-chips">{["Tất cả", "Từ chối", "Không hữu ích", "Độ trễ cao"].map((x) => <button key={x} className={filter === x ? "active" : ""} onClick={() => setFilter(x)}>{x}</button>)}</div></div><div className="data-table card"><div className="data-row head"><span>Thời gian</span><span>Câu hỏi</span><span>Trạng thái</span><span>Cấu hình</span><span>Độ trễ</span><span>Đánh giá</span></div>{visibleLogs.map((log) => <button className="data-row" key={log.id} onClick={() => setToast(`Đã mở chi tiết ${log.id}`)}><span><strong>{log.time}</strong><small>{log.id}</small></span><span>{log.query}</span><span><b className={`status-tag ${log.status === "Từ chối" ? "warning" : ""}`}>{log.status}</b></span><span>{log.config}</span><span>{log.latency}</span><span>{log.rating}</span></button>)}</div></div>;
}

function AccountsView({ setToast }) {
  const [accounts, setAccounts] = useState(ACCOUNTS);
  const [createOpen, setCreateOpen] = useState(false);
  return <div className="standard-page"><div className="page-header"><div><p className="page-kicker">QUẢN TRỊ TRUY CẬP</p><h1>Tài khoản demo</h1><p>Chỉ lưu tên đăng nhập và vai trò, không lưu thông tin cá nhân.</p></div><button className="primary-button" onClick={() => setCreateOpen(true)}><Plus size={17} /> Tạo tài khoản</button></div><div className="data-table accounts-table card"><div className="data-row head"><span>Tài khoản</span><span>Vai trò</span><span>Trạng thái</span><span>Hoạt động cuối</span><span>Thao tác</span></div>{accounts.map((a) => <div className="data-row" key={a.id}><span className="account-name"><i>{a.username.slice(0, 2).toUpperCase()}</i><strong>{a.username}</strong></span><span>{a.role}</span><span><b className={`status-tag ${a.status === "Đã khóa" ? "muted" : ""}`}>{a.status}</b></span><span>{a.last}</span><span className="account-actions"><button onClick={() => { setAccounts((current) => current.map((x) => x.id === a.id ? { ...x, role: x.role === "Người dùng" ? "Quản trị viên" : "Người dùng" } : x)); setToast("Đã cập nhật vai trò"); }}>Đổi vai trò</button><button onClick={() => { setAccounts((current) => current.map((x) => x.id === a.id ? { ...x, status: x.status === "Đã khóa" ? "Hoạt động" : "Đã khóa" } : x)); setToast(a.status === "Đã khóa" ? "Đã mở khóa tài khoản" : "Đã khóa tài khoản"); }}>{a.status === "Đã khóa" ? "Mở khóa" : "Khóa"}</button><button onClick={() => setToast("Đã tạo mật khẩu tạm thời")}>Đặt lại mật khẩu</button></span></div>)}</div>{createOpen && <CreateAccount onClose={() => setCreateOpen(false)} onSave={(account) => { setAccounts((current) => [...current, { ...account, id: Date.now(), status: "Hoạt động", last: "Chưa đăng nhập" }]); setCreateOpen(false); setToast("Đã tạo tài khoản demo"); }} />}</div>;
}

function CompareView() {
  const [left, setLeft] = useState("B0");
  const [right, setRight] = useState("B4");
  const [question, setQuestion] = useState("Thời hạn giải quyết quyền lợi bảo hiểm An Gia là bao lâu?");
  const [ran, setRan] = useState(false);
  const [compareSourceOpen, setCompareSourceOpen] = useState(null);
  return <div className="standard-page"><div className="page-header"><div><p className="page-kicker">MINH HỌA ABLATION</p><h1>So sánh hai cấu hình</h1><p>Chạy cùng một câu hỏi và đối chiếu câu trả lời, nguồn cùng độ trễ.</p></div></div><div className="compare-query card"><label>Câu hỏi<input value={question} onChange={(e) => setQuestion(e.target.value)} /></label><button className="primary-button" onClick={() => setRan(true)}><Sparkles size={17} /> Chạy so sánh</button></div><div className="compare-grid">{[[left, setLeft, false], [right, setRight, true]].map(([value, setter, rag], index) => <div className="compare-column card" key={index}><div className="compare-head"><label>Cấu hình<select value={value} onChange={(e) => setter(e.target.value)}>{["B0", "B1", "B2", "B3", "B4"].map((x) => <option key={x}>{x}</option>)}</select></label><span>{value === "B4" ? "Pipeline đầy đủ" : "Baseline"}</span></div>{ran ? <><div className="compare-answer"><Bot size={20} /><p>{rag ? "Bảo Việt giải quyết quyền lợi trong 15 ngày làm việc kể từ khi nhận đủ hồ sơ hợp lệ. [1]" : "Thông thường doanh nghiệp bảo hiểm sẽ xử lý hồ sơ trong một khoảng thời gian hợp lý theo quy định."}</p></div><div className="compare-stats"><span>Độ trễ <strong>{rag ? "3,2s" : "1,4s"}</strong></span><span>Nguồn <strong>{rag ? "2" : "0"}</strong></span><span>Faithfulness <strong>{rag ? "0,91" : "0,42"}</strong></span></div>{rag && <SourceStack sources={[SOURCES[0]]} sourceOpen={compareSourceOpen} setSourceOpen={setCompareSourceOpen} showExcerpts={false} />}</> : <div className="empty-compare"><Gauge size={27} /><p>Chạy so sánh để xem kết quả cấu hình {value}</p></div>}</div>)}</div></div>;
}

function SettingsPanel({ onClose, theme, setTheme, largeText, setLargeText, citationMode, setCitationMode, showExcerpts, setShowExcerpts, showDetails, setShowDetails }) {
  return <div className="modal-layer"><button className="modal-scrim" onClick={onClose} /><div className="settings-panel"><div className="settings-title"><div><span>Cài đặt cá nhân</span><h2>Tùy chỉnh trải nghiệm</h2></div><button className="icon-button" onClick={onClose}><X size={20} /></button></div><section><h3>Giao diện</h3><div className="theme-options"><button className={theme === "light" ? "active" : ""} onClick={() => setTheme("light")}><Sun size={20} /> Sáng</button><button className={theme === "dark" ? "active" : ""} onClick={() => setTheme("dark")}><Moon size={20} /> Tối</button></div><Toggle label="Cỡ chữ lớn" detail="Tăng kích thước nội dung hội thoại" value={largeText} setValue={setLargeText} /></section><section><h3>Trích dẫn và xử lý</h3><div className="radio-setting"><span><strong>Cách hiển thị nguồn</strong><small>Chỉ thay đổi giao diện, không đổi prompt</small></span><label><input type="radio" checked={citationMode === "inline"} onChange={() => setCitationMode("inline")} /> Trong câu</label><label><input type="radio" checked={citationMode === "list"} onChange={() => setCitationMode("list")} /> Cuối câu</label></div><Toggle label="Hiển thị đoạn văn gốc" detail="Cho phép mở nội dung chunk nguồn" value={showExcerpts} setValue={setShowExcerpts} /><Toggle label="Chi tiết xử lý" detail="Hiện điểm rerank, token và query sau xử lý" value={showDetails} setValue={setShowDetails} /></section></div></div>;
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
  return <Modal title="Điều gì cần cải thiện?" subtitle="Phản hồi được lưu cùng run ID để phân tích lỗi." onClose={onClose}><div className="reason-list">{["Câu trả lời sai", "Thiếu nguồn", "Trích dẫn không đúng", "Từ chối nhầm", "Nội dung khó hiểu"].map((x) => <label key={x}><input type="radio" name="reason" checked={reason === x} onChange={() => setReason(x)} /> {x}</label>)}</div><div className="modal-actions"><button className="secondary-button" onClick={onClose}>Hủy</button><button className="primary-button" disabled={!reason} onClick={onSave}>Gửi phản hồi</button></div></Modal>;
}

function RenameModal({ item, onClose, onSave }) {
  const [name, setName] = useState(item.title);
  return <Modal title="Đổi tên cuộc trò chuyện" subtitle="Tên mới giúp bạn tìm lại nội dung nhanh hơn." onClose={onClose}><label className="modal-field">Tên cuộc trò chuyện<input value={name} onChange={(e) => setName(e.target.value)} autoFocus /></label><div className="modal-actions"><button className="secondary-button" onClick={onClose}>Hủy</button><button className="primary-button" onClick={() => onSave(name)} disabled={!name.trim()}>Lưu thay đổi</button></div></Modal>;
}

function ConfirmModal({ item, onClose, onConfirm }) {
  return <Modal title="Xác nhận xóa" subtitle={`Bạn sắp xóa ${item.all ? "toàn bộ lịch sử" : `“${item.title}”`}. Hành động này không thể hoàn tác.`} onClose={onClose}><div className="delete-warning"><Trash2 size={21} /> Log thực nghiệm trong hệ thống quản trị sẽ không bị ảnh hưởng.</div><div className="modal-actions"><button className="secondary-button" onClick={onClose}>Hủy</button><button className="danger-button" onClick={onConfirm}>Xóa vĩnh viễn</button></div></Modal>;
}

function CreateAccount({ onClose, onSave }) {
  const [username, setUsername] = useState("");
  const [role, setRole] = useState("Người dùng");
  return <Modal title="Tạo tài khoản demo" subtitle="Không sử dụng email hoặc thông tin cá nhân." onClose={onClose}><label className="modal-field">Tên đăng nhập<input value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Ví dụ: demo_user_02" /></label><label className="modal-field">Vai trò<select value={role} onChange={(e) => setRole(e.target.value)}><option>Người dùng</option><option>Quản trị viên</option></select></label><div className="modal-actions"><button className="secondary-button" onClick={onClose}>Hủy</button><button className="primary-button" disabled={!username} onClick={() => onSave({ username, role })}>Tạo tài khoản</button></div></Modal>;
}

function SessionExpired({ onLogin, onLogout }) {
  return <div className="modal-layer session-layer"><div className="modal-card session-card"><span className="session-lock"><LockKeyhole size={24} /></span><h2>Phiên làm việc đã hết hạn</h2><p>Để bảo vệ phiên demo, hệ thống tự động đăng xuất sau 30 phút không hoạt động.</p><button className="primary-button" onClick={onLogin}>Tiếp tục phiên làm việc</button><button className="text-button" onClick={onLogout}>Quay về đăng nhập</button></div></div>;
}

function Modal({ title, subtitle, onClose, children, wide = false }) {
  return <div className="modal-layer"><button className="modal-scrim" onClick={onClose} /><div className={`modal-card ${wide ? "wide" : ""}`}><div className="modal-head"><div><h2>{title}</h2><p>{subtitle}</p></div><button className="icon-button" onClick={onClose}><X size={20} /></button></div>{children}</div></div>;
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
