import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ArrowUp,
  BookOpen,
  Check,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  Clock3,
  Copy,
  ExternalLink,
  FileText,
  History,
  Info,
  Menu,
  MessageCirclePlus,
  MoreHorizontal,
  PanelLeftClose,
  PanelLeftOpen,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
  Trash2,
  UserRound,
  X,
} from "lucide-react";
import "./styles.css";

const products = [
  { code: "BVP", name: "Bảo Việt An Gia" },
  { code: "BTB", name: "Bảo Việt Tâm Bình" },
  { code: "ITC", name: "Bảo Việt Intercare" },
  { code: "C37", name: "37 bệnh hiểm nghèo" },
  { code: "FLX", name: "Du lịch Flexi" },
];

const samples = [
  {
    group: "Tra cứu quy tắc",
    question: "Thời hạn giải quyết quyền lợi bảo hiểm An Gia là bao lâu?",
  },
  {
    group: "Quyền lợi",
    question: "Trẻ 2 tuổi nằm viện nội trú được hưởng quyền lợi gì trong An Gia?",
  },
  {
    group: "So sánh",
    question: "So sánh độ tuổi tham gia của CI37 và Intercare.",
  },
  {
    group: "Bảng phí",
    question: "Phí gia đình của Flexi hạng Kim Cương cho chuyến đi 204–210 ngày?",
  },
];

const initialHistory = [
  { id: 1, title: "Quyền lợi nội trú An Gia", time: "Hôm nay", active: true },
  { id: 2, title: "So sánh CI37 và Intercare", time: "Hôm qua" },
  { id: 3, title: "Phí bảo hiểm du lịch Flexi", time: "12/11" },
  { id: 4, title: "Thời gian chờ Tâm Bình", time: "10/11" },
];

const sources = [
  {
    id: 1,
    product: "Bảo Việt An Gia",
    document: "Quy tắc bảo hiểm sức khỏe Bảo Việt An Gia",
    section: "Chương IV › Điều 18 › Khoản 2",
    page: 24,
    text: "Trong thời hạn 15 ngày làm việc kể từ ngày nhận được đầy đủ hồ sơ yêu cầu trả tiền bảo hiểm hợp lệ, Bảo Việt có trách nhiệm xem xét và giải quyết quyền lợi bảo hiểm.",
  },
  {
    id: 2,
    product: "Bảo Việt An Gia",
    document: "Quy tắc bảo hiểm sức khỏe Bảo Việt An Gia",
    section: "Chương IV › Điều 17 › Khoản 1",
    page: 23,
    text: "Người được bảo hiểm hoặc người thụ hưởng có trách nhiệm gửi hồ sơ yêu cầu trả tiền bảo hiểm theo danh mục chứng từ được quy định cho từng quyền lợi.",
  },
];

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileNav, setMobileNav] = useState(false);
  const [scopeOpen, setScopeOpen] = useState(false);
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState(initialHistory);
  const [historySearch, setHistorySearch] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [sourceOpen, setSourceOpen] = useState(null);
  const [toast, setToast] = useState("");
  const [feedback, setFeedback] = useState(null);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [largeText, setLargeText] = useState(false);
  const chatEnd = useRef(null);

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(""), 2200);
    return () => clearTimeout(timer);
  }, [toast]);

  function newChat() {
    setMessages([]);
    setQuery("");
    setFeedback(null);
    setMobileNav(false);
  }

  function sendQuestion(question = query) {
    const clean = question.trim();
    if (!clean || loading) return;
    setMessages((current) => [...current, { role: "user", text: clean }]);
    setQuery("");
    setLoading(true);
    setFeedback(null);
    if (messages.length === 0) {
      setHistory((current) => [
        { id: Date.now(), title: clean.slice(0, 42), time: "Vừa xong", active: true },
        ...current.map((item) => ({ ...item, active: false })),
      ]);
    }
    setTimeout(() => {
      const outOfScope = /ô tô|pvi|hợp đồng của tôi|tính phí cho tôi/i.test(clean);
      setMessages((current) => [
        ...current,
        outOfScope
          ? {
              role: "assistant",
              refused: true,
              text: "Tài liệu hiện có không đề cập đủ nội dung này để đưa ra câu trả lời đáng tin cậy. Bạn có thể hỏi về quy tắc, quyền lợi, biểu phí hoặc điều kiện của các sản phẩm đang có trong kho tài liệu.",
            }
          : {
              role: "assistant",
              text: "Theo Quy tắc bảo hiểm sức khỏe Bảo Việt An Gia, Bảo Việt xem xét và giải quyết quyền lợi trong vòng **15 ngày làm việc** kể từ khi nhận đủ hồ sơ yêu cầu trả tiền bảo hiểm hợp lệ. [1]\\n\\nĐể tránh chậm trễ, người được bảo hiểm hoặc người thụ hưởng cần nộp đầy đủ chứng từ theo danh mục áp dụng cho từng quyền lợi. [2]",
              sources,
            },
      ]);
      setLoading(false);
    }, 1150);
  }

  function toggleProduct(code) {
    setSelectedProducts((current) =>
      current.includes(code) ? current.filter((item) => item !== code) : [...current, code],
    );
  }

  function copyAnswer(text) {
    navigator.clipboard?.writeText(text.replaceAll("**", ""));
    setToast("Đã sao chép câu trả lời và nguồn");
  }

  const filteredHistory = history.filter((item) =>
    item.title.toLowerCase().includes(historySearch.toLowerCase()),
  );

  return (
    <div className={`app-shell ${largeText ? "large-text" : ""}`}>
      <a className="skip-link" href="#main-chat">Bỏ qua đến nội dung chính</a>

      <header className="topbar">
        <button className="icon-button mobile-only" onClick={() => setMobileNav(true)} aria-label="Mở menu">
          <Menu size={22} />
        </button>
        <div className="brand">
          <img src="/baoviet-logo.png" alt="Bảo hiểm Bảo Việt" />
          <span className="brand-divider" />
          <div>
            <strong>Trợ lý sản phẩm</strong>
            <small>Hỏi đáp có trích dẫn</small>
          </div>
        </div>
        <div className="topbar-actions">
          <div className="status-pill"><span /> Hệ thống sẵn sàng</div>
          <button className="icon-button" aria-label="Trợ giúp"><CircleHelp size={20} /></button>
          <button className="icon-button" onClick={() => setSettingsOpen(true)} aria-label="Cài đặt"><Settings size={20} /></button>
          <button className="profile-button"><span>NH</span><span className="profile-copy"><strong>Ngọc Hà</strong><small>Người dùng</small></span><ChevronDown size={16} /></button>
        </div>
      </header>

      <div className="workspace">
        <aside className={`sidebar ${sidebarOpen ? "" : "collapsed"} ${mobileNav ? "mobile-open" : ""}`}>
          <div className="sidebar-top">
            <button className="new-chat" onClick={newChat}><MessageCirclePlus size={19} /><span>Cuộc trò chuyện mới</span></button>
            <button className="icon-button desktop-only" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="Thu gọn thanh bên">
              {sidebarOpen ? <PanelLeftClose size={19} /> : <PanelLeftOpen size={19} />}
            </button>
            <button className="icon-button mobile-only close-mobile" onClick={() => setMobileNav(false)} aria-label="Đóng menu"><X size={21} /></button>
          </div>
          <div className="sidebar-content">
            <div className="section-label"><span><History size={16} /> Lịch sử</span><button aria-label="Tùy chọn lịch sử"><MoreHorizontal size={18} /></button></div>
            <label className="history-search"><Search size={16} /><input value={historySearch} onChange={(e) => setHistorySearch(e.target.value)} placeholder="Tìm cuộc trò chuyện" /></label>
            <div className="history-list">
              {filteredHistory.map((item) => (
                <button className={`history-item ${item.active ? "active" : ""}`} key={item.id}>
                  <span>{item.title}</span><small>{item.time}</small>
                </button>
              ))}
            </div>
          </div>
          <div className="sidebar-footer">
            <button><BookOpen size={18} /><span>Danh mục sản phẩm</span></button>
            <button><ShieldCheck size={18} /><span>Quyền riêng tư</span></button>
          </div>
        </aside>
        {mobileNav && <button className="mobile-scrim" aria-label="Đóng menu" onClick={() => setMobileNav(false)} />}

        <main id="main-chat" className="chat-area">
          <div className="chat-header">
            <div>
              <div className="eyebrow"><span /> RAG · Kho dữ liệu v1</div>
              <h1>{messages.length ? "Quyền lợi nội trú An Gia" : "Trợ lý tra cứu sản phẩm bảo hiểm"}</h1>
            </div>
            <button className="more-button" aria-label="Tùy chọn cuộc trò chuyện"><MoreHorizontal size={21} /></button>
          </div>

          <section className="chat-scroll" aria-live="polite">
            {messages.length === 0 ? (
              <div className="welcome">
                <div className="welcome-mark"><Sparkles size={26} /></div>
                <p className="welcome-kicker">TRỢ LÝ BẢO VIỆT</p>
                <h2>Bạn muốn tìm hiểu điều gì?</h2>
                <p className="welcome-copy">Tra cứu nhanh quy tắc, quyền lợi và biểu phí từ tài liệu sản phẩm chính thức. Mỗi câu trả lời đều đi kèm nguồn để bạn kiểm tra.</p>
                <div className="sample-grid">
                  {samples.map((sample) => (
                    <button key={sample.question} onClick={() => sendQuestion(sample.question)}>
                      <span>{sample.group}</span>
                      <strong>{sample.question}</strong>
                      <ArrowUp size={18} />
                    </button>
                  ))}
                </div>
                <div className="capabilities">
                  <span><Check size={15} /> Tra cứu 5 sản phẩm</span>
                  <span><Check size={15} /> Trích dẫn đến Điều/Khoản</span>
                  <span><Check size={15} /> Từ chối khi thiếu căn cứ</span>
                </div>
              </div>
            ) : (
              <div className="conversation">
                {messages.map((message, index) =>
                  message.role === "user" ? (
                    <div className="user-row" key={index}>
                      <div className="user-bubble">{message.text}</div>
                      <div className="avatar user-avatar"><UserRound size={17} /></div>
                    </div>
                  ) : (
                    <div className="assistant-row" key={index}>
                      <div className="avatar assistant-avatar"><Sparkles size={17} /></div>
                      <div className="answer-wrap">
                        <div className="answer-label">Trợ lý Bảo Việt</div>
                        {message.refused && <div className="refusal-label"><Info size={16} /> Ngoài phạm vi tài liệu</div>}
                        <div className={`answer-text ${message.refused ? "refused" : ""}`}>
                          {message.text.split("\n").map((line, lineIndex) => (
                            <p key={lineIndex}>{formatLine(line, (id) => setSourceOpen(sourceOpen === id ? null : id))}</p>
                          ))}
                        </div>
                        {message.sources && (
                          <div className="source-stack">
                            <div className="source-heading"><span><FileText size={17} /> Nguồn tham khảo</span><small>{message.sources.length} trích dẫn</small></div>
                            {message.sources.map((source) => (
                              <div className={`source-card ${sourceOpen === source.id ? "open" : ""}`} key={source.id}>
                                <button onClick={() => setSourceOpen(sourceOpen === source.id ? null : source.id)}>
                                  <span className="source-number">{source.id}</span>
                                  <span className="source-main"><strong>{source.section}</strong><small>{source.document} · Trang {source.page}</small></span>
                                  <ChevronDown size={18} />
                                </button>
                                {sourceOpen === source.id && (
                                  <div className="source-detail">
                                    <p>“{source.text}”</p>
                                    <a href="https://baovietonline.com.vn/" target="_blank" rel="noreferrer">Mở tài liệu gốc <ExternalLink size={14} /></a>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                        <div className="answer-actions">
                          <button onClick={() => copyAnswer(message.text)}><Copy size={16} /> Sao chép</button>
                          <span />
                          <span>Câu trả lời này có hữu ích?</span>
                          <button className={feedback === "up" ? "selected" : ""} onClick={() => { setFeedback("up"); setToast("Cảm ơn phản hồi của bạn"); }} aria-label="Hữu ích"><ThumbsUp size={16} /></button>
                          <button className={feedback === "down" ? "selected" : ""} onClick={() => { setFeedback("down"); setToast("Đã ghi nhận để cải thiện"); }} aria-label="Không hữu ích"><ThumbsDown size={16} /></button>
                        </div>
                        <div className="answer-meta"><Clock3 size={14} /> 3,2 giây <span>•</span> Cấu hình B4 <span>•</span> 2 nguồn được trích dẫn</div>
                      </div>
                    </div>
                  ),
                )}
                {loading && (
                  <div className="assistant-row">
                    <div className="avatar assistant-avatar"><Sparkles size={17} /></div>
                    <div className="thinking"><strong>Đang tìm trong tài liệu chính thức</strong><div><i /><i /><i /></div><span>Truy xuất và kiểm tra nguồn phù hợp…</span></div>
                  </div>
                )}
              </div>
            )}
            <div ref={chatEnd} />
          </section>

          <div className="composer-zone">
            <div className="scope-row">
              <div className="scope-wrap">
                <button className="scope-button" onClick={() => setScopeOpen(!scopeOpen)}>
                  <BookOpen size={16} />
                  {selectedProducts.length ? `${selectedProducts.length} sản phẩm đã chọn` : "Tự động nhận diện sản phẩm"}
                  <ChevronDown size={16} />
                </button>
                {scopeOpen && (
                  <div className="scope-menu">
                    <div><strong>Phạm vi sản phẩm</strong><small>Để trống để hệ thống tự nhận diện</small></div>
                    {products.map((product) => (
                      <button key={product.code} onClick={() => toggleProduct(product.code)}>
                        <span className={`checkbox ${selectedProducts.includes(product.code) ? "checked" : ""}`}>{selectedProducts.includes(product.code) && <Check size={13} />}</span>
                        <span><strong>{product.name}</strong><small>{product.code}</small></span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <span className="privacy-note"><ShieldCheck size={15} /> Không nhập CCCD, số điện thoại hoặc thông tin sức khỏe cá nhân</span>
            </div>
            <div className="composer">
              <textarea value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendQuestion(); } }} placeholder="Hỏi về quy tắc, quyền lợi, biểu phí…" rows={1} />
              <div className="composer-footer">
                <span>Enter để gửi · Shift + Enter để xuống dòng</span>
                <button onClick={() => sendQuestion()} disabled={!query.trim() || loading} aria-label="Gửi câu hỏi"><ArrowUp size={20} /></button>
              </div>
            </div>
            <p className="disclaimer">Thông tin chỉ mang tính tham khảo. Căn cứ cuối cùng là quy tắc và hợp đồng do doanh nghiệp bảo hiểm phát hành.</p>
          </div>
        </main>
      </div>

      {settingsOpen && (
        <div className="modal-layer" role="dialog" aria-modal="true" aria-labelledby="settings-title">
          <button className="modal-scrim" onClick={() => setSettingsOpen(false)} aria-label="Đóng cài đặt" />
          <div className="settings-panel">
            <div className="settings-title"><div><span>Cài đặt hiển thị</span><h2 id="settings-title">Tùy chỉnh trải nghiệm</h2></div><button className="icon-button" onClick={() => setSettingsOpen(false)} aria-label="Đóng cài đặt"><X size={20} /></button></div>
            <div className="setting-row"><div><strong>Cỡ chữ lớn</strong><small>Tăng kích thước nội dung hội thoại</small></div><button className={`switch ${largeText ? "on" : ""}`} onClick={() => setLargeText(!largeText)} aria-pressed={largeText}><span /></button></div>
            <div className="setting-row"><div><strong>Hiển thị đoạn nguồn</strong><small>Mở nội dung gốc khi chọn trích dẫn</small></div><span className="setting-value">Khi chọn <ChevronRight size={16} /></span></div>
            <div className="setting-row"><div><strong>Giao diện</strong><small>Được tối ưu cho khả năng đọc tài liệu</small></div><span className="setting-value">Sáng <ChevronRight size={16} /></span></div>
          </div>
        </div>
      )}

      {toast && <div className="toast"><Check size={17} /> {toast}</div>}
    </div>
  );
}

function formatLine(line, onCitation) {
  const parts = line.split(/(\*\*.*?\*\*|\[\d+\])/g).filter(Boolean);
  return parts.map((part, index) => {
    if (part.startsWith("**")) return <strong key={index}>{part.slice(2, -2)}</strong>;
    if (/^\[\d+\]$/.test(part)) {
      const id = Number(part.slice(1, -1));
      return <button className="citation" onClick={() => onCitation(id)} key={index}>{id}</button>;
    }
    return part;
  });
}

createRoot(document.getElementById("root")).render(<App />);
