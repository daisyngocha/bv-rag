// Kiểm luồng giao diện React với Supabase + FastAPI GIẢ ở tầng mạng (Playwright chặn request), không cần Colab.
// Chạy (cần Chromium + Playwright; dev server tự bật):
//   node tests/e2e/frontend_smoke.cjs            # mặc định cổng 5179, in "FRONTEND SMOKE OK" khi qua hết
// Kiểm: đăng nhập → câu hỏi mẫu → hỏi (SSE, che SĐT, lọc sản phẩm) → trích dẫn/nguồn → 👍/👎 → lịch sử
// (mở, đổi tên, xóa) → cài đặt (lưu user_settings) → danh mục → màn quản trị (nhật ký, tài khoản, cấu hình,
// so sánh, trạng thái hệ thống) → xem như người dùng → đăng xuất.
const { spawn } = require("child_process");
const path = require("path");
const { chromium } = require("playwright");

const PORT = process.env.SMOKE_PORT || "5179";
const SB = "http://sb.test";
const API = "http://api.test";
const ROOT = path.resolve(__dirname, "../..");
const UID = "00000000-0000-0000-0000-0000000000a1";
const CONV = "11111111-1111-1111-1111-111111111111";

const calls = [];
const json = (route, body, status = 200, headers = {}) => route.fulfill({
  status, contentType: "application/json", headers: { "access-control-allow-origin": "*", ...headers }, body: JSON.stringify(body),
});
const wantsObject = (req) => (req.headers().accept || "").includes("vnd.pgrst.object");

const state = {
  settings: { user_id: UID, theme: "light", font_size: 14, citation_style: "inline", show_source_text: true, language: "vi", show_processing: true },
  conversations: [{ id: CONV, user_id: UID, title: "Thời gian chờ An Gia", title_is_custom: false, preview: "Thời gian chờ?", n_messages: 2, created_at: "2026-11-08T10:00:00Z", updated_at: "2026-11-08T10:01:00Z" }],
};
const SOURCE = { ord: 1, data_version: "v1", chunk_id: "BVP_QT_C2_M1_B", product_code: "BVP", product_name: "Bảo Việt An Gia", doc_type: "quy_tac", section_path: "Chương II > Thời gian chờ", page: 7, source_file: "bvp_quytac.pdf", url: "https://example.invalid/bvp", text: "Thời gian chờ 30 ngày." };

async function supabaseRoute(route) {
  const req = route.request();
  const url = new URL(req.url());
  const p = url.pathname;
  const method = req.method();
  calls.push(`${method} ${p}${url.search}`);
  if (method === "OPTIONS") return route.fulfill({ status: 200, headers: { "access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "*" } });
  const user = { id: UID, aud: "authenticated", role: "authenticated", email: "admin01@bv-rag.local", app_metadata: { role: "admin" }, user_metadata: {} };
  if (p === "/auth/v1/token") {
    const body = JSON.parse(req.postData() || "{}");
    if (body.password === "sai") return json(route, { error: "invalid_grant", error_description: "Invalid login credentials", msg: "Invalid login credentials" }, 400);
    return json(route, { access_token: "tok-admin", token_type: "bearer", expires_in: 3600, expires_at: Math.floor(Date.now() / 1000) + 3600, refresh_token: "r1", user });
  }
  if (p === "/auth/v1/user") return json(route, user);
  if (p === "/auth/v1/logout") return route.fulfill({ status: 204, headers: { "access-control-allow-origin": "*" } });
  const table = p.replace("/rest/v1/", "");
  const one = (row) => json(route, wantsObject(req) ? row : [row]);
  switch (table) {
    case "profiles": return one({ id: UID, username: "admin01", display_name: "Quản trị viên", role: "admin", is_active: true });
    case "user_settings":
      if (method === "PATCH") { Object.assign(state.settings, JSON.parse(req.postData())); return json(route, [], 204); }
      return one(state.settings);
    case "products": return json(route, [{ product_code: "BTB", product_name: "Bảo Việt Tâm Bình", line: "phi_nhan_tho" }, { product_code: "BVP", product_name: "Bảo Việt An Gia", line: "phi_nhan_tho" }]);
    case "sample_questions": return json(route, [{ qid: "v1-0002", question: "Thời hạn giải quyết bồi thường An Gia?", question_group: "lookup", products: ["BVP"] }]);
    case "v_conversation_list": return json(route, state.conversations);
    case "rpc/search_conversations": return json(route, state.conversations.filter((c) => c.title.toLowerCase().includes(JSON.parse(req.postData()).q.toLowerCase())));
    case "conversations":
      if (method === "PATCH") { const b = JSON.parse(req.postData()); state.conversations = state.conversations.map((c) => ({ ...c, ...b })); return json(route, [], 204); }
      if (method === "DELETE") { state.conversations = []; return json(route, [], 204); }
      break;
    case "messages": return json(route, [
      { id: "m-q", conversation_id: CONV, role: "user", content: "Thời gian chờ?", pii_masked: false, created_at: "2026-11-08T10:00:00Z" },
      { id: "m-a", conversation_id: CONV, reply_to_id: "m-q", role: "assistant", content: "Thời gian chờ là 30 ngày [1].", refused: false, refusal_reason: null, run_id: "B4_demo_1", created_at: "2026-11-08T10:01:00Z" },
    ]);
    case "v_message_sources": return json(route, [{ ...SOURCE, message_id: "m-a" }]);
    case "feedback":
      if (method === "POST") { calls.push(`FEEDBACK ${req.postData()}`); return json(route, [], 201); }
      return json(route, []);
    case "traces": return one({ message_id: "x", query_processed: "thời gian chờ", detected_products: ["BVP"], retrieval_mode: "hybrid", latency_ms: 2300, tokens_in: 900, tokens_out: 60, cost_usd: null, timings_ms: { retrieve: 20, rerank: 500, generate: 1700 }, error: null });
    case "retrieval_logs": return json(route, [{ rank: 1, chunk_id: "BVP_QT_C2_M1_B", score: 0.031, rerank: 0.97, in_context: true }]);
    case "v_catalog": return json(route, [{ product_code: "BVP", product_name: "Bảo Việt An Gia", company: "BHBV", line: "phi_nhan_tho", is_active: true, document_id: 1, doc_type: "quy_tac", source_file: "bvp_quytac.pdf", url: "https://example.invalid/bvp", effective_date: "2025-06-27", n_chunks: 120, data_version: "v1" }]);
    case "data_versions": return one({ version: "v1", n_chunks: 634 });
    case "v_query_logs":
      if (method === "HEAD") return route.fulfill({ status: 200, headers: { "access-control-allow-origin": "*", "access-control-expose-headers": "content-range", "content-range": "*/2" } });
      return json(route, [{ message_id: "m-a", created_at: "2026-11-08T10:01:00Z", run_id: "B4_demo_1", question: "Thời gian chờ?", answer: "30 ngày [1].", refused: false, refusal_reason: null, config_name: "B4", data_version: "v1", latency_ms: 2300, detected_products: ["BVP"], rating: -1, feedback_reason: "thieu_nguon", username: "demo01" }], 200, { "content-range": "0-0/1", "access-control-expose-headers": "content-range" });
    case "pipeline_configs": return json(route, ["B0", "B3", "B4"].map((n) => ({ name: n, description: n, params: { retrieval: { mode: n === "B0" ? "none" : "hybrid" }, prompt: "rag_v3", rerank: n === "B4" ? { enabled: true, min_score: 0.9 } : null } })));
    case "app_settings": return one({ value: { config: "B4", run_id: "B4_demo_1" } });
    case "rpc/demo_metrics": return json(route, { n_questions: 3, latency_p50: 2100, latency_p95: 4800, refusal_rate: 0.33, positive_rate: 0.5, by_product: [{ product_code: "BVP", n: 2, refusal_rate: 0 }, { product_code: "khac", n: 1, refusal_rate: 1 }], by_day: [] });
    case "eval_results": return json(route, [{ run_id: "B4_v1_test_1", question_group: "all", metric: "recall@5", value: 0.906, runs: { config_name: "B4", split: "test", started_at: "2026-11-07" } }]);
    default: break;
  }
  return json(route, { message: `unmocked ${method} ${p}` }, 404);
}

async function apiRoute(route) {
  const req = route.request();
  const p = new URL(req.url()).pathname;
  calls.push(`API ${req.method()} ${p} ${req.headers().authorization || ""}`);
  const cors = { "access-control-allow-origin": "*", "access-control-allow-headers": "*", "access-control-allow-methods": "*" };
  if (req.method() === "OPTIONS") return route.fulfill({ status: 200, headers: cors });
  if (p === "/chat/ask/stream") {
    const body = JSON.parse(req.postData());
    calls.push(`ASK ${JSON.stringify(body)}`);
    const done = { question: body.question, answer: "Thời gian chờ điều trị nội trú là 30 ngày [1].", refused: false, refusal_reason: null, sources: [SOURCE], run_id: "B4_demo_1", conversation_id: CONV, question_id: "q-new", message_id: "a-new", title: "Thời gian chờ", saved: true, db_error: null };
    const ev = (e, d) => `event: ${e}\ndata: ${JSON.stringify(d)}\n\n`;
    return route.fulfill({ status: 200, headers: { ...cors, "content-type": "text/event-stream" }, body: ev("status", { stage: "retrieve", message: "Đang tìm trong tài liệu chính thức" }) + ev("token", { text: "Thời gian chờ " }) + ev("token", { text: "30 ngày [1]." }) + ev("done", done) });
  }
  if (p === "/admin/users") {
    if (req.method() === "POST") return route.fulfill({ status: 201, headers: { ...cors, "content-type": "application/json" }, body: JSON.stringify({ profile: { id: "n1", username: "demo09" }, temp_password: "TamThoi123!x" }) });
    return route.fulfill({ status: 200, headers: { ...cors, "content-type": "application/json" }, body: JSON.stringify([{ id: UID, username: "admin01", display_name: "Quản trị viên", email: "admin01@bv-rag.local", role: "admin", is_active: true, last_sign_in_at: null }, { id: "u2", username: "demo01", display_name: null, email: "demo01@bv-rag.local", role: "user", is_active: true, last_sign_in_at: null }]) });
  }
  if (p === "/admin/users/u2") return route.fulfill({ status: 200, headers: { ...cors, "content-type": "application/json" }, body: "{}" });
  if (p === "/admin/configs/active") return route.fulfill({ status: 200, headers: { ...cors, "content-type": "application/json" }, body: JSON.stringify({ config: "B3", run_id: "B3_demo_2", loaded_in_ms: 200 }) });
  if (p === "/admin/compare") return route.fulfill({ status: 200, headers: { ...cors, "content-type": "application/json" }, body: JSON.stringify({ answers: [{ config: "B0", run_id: "B0_demo_1", answer: "Không RAG.", sources: [], n_sources: 0, latency_ms: 900 }, { config: "B4", run_id: "B4_demo_1", answer: "30 ngày [1].", sources: [SOURCE], n_sources: 1, latency_ms: 2300 }] }) });
  if (p === "/admin/health") return route.fulfill({ status: 200, headers: { ...cors, "content-type": "application/json" }, body: JSON.stringify({ ok: true, config: "B4", run_id: "B4_demo_1", data_version: "v1", api: { ok: true, ms: 3 }, ollama: { ok: true, model: "qwen", gpu_pct: 100 }, qdrant: { ok: true, collection: "bv_v1_structure", points: 634 }, encoder: { ok: true, model: "bge-m3", device: "cuda" }, reranker: { ok: true, model: "rr", min_score: 0.9 }, supabase: { ok: true, data_version: "v1", n_chunks: 634, ms: 120 } }) });
  return route.fulfill({ status: 404, headers: cors, body: "{}" });
}

function assert(cond, msg) { if (!cond) throw new Error(`FAIL: ${msg}`); }
const step = (name) => console.log(`- ${name}`);

(async () => {
  const server = spawn("npx", ["vite", "--port", PORT, "--strictPort"], {
    cwd: ROOT, env: { ...process.env, VITE_SUPABASE_URL: SB, VITE_SUPABASE_ANON_KEY: "anon", VITE_API_URL: API }, stdio: "pipe",
  });
  let out = "";
  server.stdout.on("data", (d) => { out += d; });
  for (let i = 0; i < 60 && !out.includes("Local"); i++) await new Promise((r) => setTimeout(r, 500));
  const browser = await chromium.launch();
  const errors = [];
  try {
    const page = await browser.newPage({ viewport: { width: 1360, height: 900 } });
    page.setDefaultTimeout(10000);
    page.on("pageerror", (e) => errors.push(e.message));
    await page.route(`${SB}/**`, supabaseRoute);
    await page.route(`${API}/**`, apiRoute);
    await page.goto(`http://localhost:${PORT}/`);

    step("đăng nhập");
    // Đăng nhập sai rồi đúng
    await page.fill('input[autocomplete="username"]', "admin01@bv-rag.local");
    await page.fill('input[type="password"]', "sai");
    await page.click('button[type="submit"]');
    await page.getByText("Email hoặc mật khẩu không đúng.").waitFor();
    await page.fill('input[type="password"]', "dung");
    await page.click('button[type="submit"]');
    await page.getByText("Bạn muốn tìm hiểu điều gì?").waitFor();
    await page.getByText("Thời hạn giải quyết bồi thường An Gia?").waitFor();     // câu hỏi mẫu từ sample_questions
    await page.getByText("Thời gian chờ An Gia").first().waitFor();                 // lịch sử gần đây

    step("hỏi đáp");
    // Hỏi: chọn sản phẩm, có SĐT → che trước khi gửi
    await page.click(".scope-button");
    await page.click('.scope-menu button:has-text("Bảo Việt Tâm Bình")');
    await page.fill(".composer textarea", "Thời gian chờ? gọi 0912345678");
    await page.keyboard.press("Enter");
    await page.getByText("Thời gian chờ điều trị nội trú là 30 ngày").waitFor();
    const ask = calls.find((c) => c.startsWith("ASK "));
    assert(ask.includes("[SĐT]") && !ask.includes("0912345678") && ask.includes('"product_filter":["BTB"]'), `body gửi API: ${ask}`);
    assert(calls.some((c) => c.startsWith("API POST /chat/ask/stream Bearer tok-admin")), "gửi Bearer token");
    assert(await page.locator(".privacy-banner").isVisible(), "banner che TTCN");

    step("trích dẫn");
    // Trích dẫn → mở nguồn; chi tiết xử lý (admin + show_processing)
    await page.locator(".answer-text .citation").last().click();
    await page.getByText("“Thời gian chờ 30 ngày.”").last().waitFor();
    await page.locator(".processing-panel").last().waitFor();

    step("đánh giá");
    // Đánh giá 👍 và 👎 (có lý do)
    await page.locator('.answer-actions button[aria-label="Hữu ích"]').last().click();
    await page.locator('.answer-actions button[aria-label="Không hữu ích"]').last().click();
    await page.click('.reason-list label:has-text("Thiếu nguồn")');
    await page.click('button:has-text("Gửi phản hồi")');
    await page.waitForTimeout(200);
    const fb = calls.filter((c) => c.startsWith("FEEDBACK"));
    assert(fb.length === 2 && fb[0].includes('"rating":1') && fb[1].includes('"rating":-1') && fb[1].includes("thieu_nguon") && fb[1].includes('"message_id":"a-new"'), `feedback: ${fb}`);

    step("lịch sử");
    // Lịch sử: mở, đổi tên, tìm, xóa
    await page.click('.main-nav button:has-text("Lịch sử chat")');
    await page.getByText("2 tin nhắn", { exact: false }).waitFor();
    await page.click(".row-menu-wrap .icon-button");
    await page.click('.row-menu button:has-text("Đổi tên")');
    await page.fill(".modal-field input", "Đổi tên mới");
    await page.click('.modal-actions button:has-text("Lưu")');
    await page.getByText("Đổi tên mới").first().waitFor();
    await page.click(".history-row-main");
    await page.getByText("Thời gian chờ là 30 ngày").waitFor();
    await page.click('.main-nav button:has-text("Lịch sử chat")');
    await page.click('button:has-text("Xóa tất cả")');
    await page.click('button:has-text("Xóa vĩnh viễn")');
    await page.getByText("Chưa có cuộc trò chuyện nào.").waitFor();
    assert(calls.some((c) => c.startsWith("DELETE /rest/v1/conversations?user_id=eq.")), "xóa tất cả theo user_id");

    step("cài đặt");
    // Cài đặt: đổi ngôn ngữ → lưu user_settings sau debounce
    await page.click('.sidebar-footer button:has-text("Cài đặt")');
    await page.click('.language-options button:has-text("English")');
    await page.waitForTimeout(800);
    assert(state.settings.language === "en", "lưu language");
    await page.getByText("Customize your experience").waitFor();
    await page.click('.language-options button:has-text("Tiếng Việt")');
    await page.click(".settings-title .icon-button");

    step("quản trị");
    // Danh mục, quản trị
    await page.click('.main-nav button:has-text("Sản phẩm & tài liệu")');
    await page.getByText("bvp_quytac.pdf", { exact: false }).waitFor();
    await page.click('.main-nav button:has-text("Dashboard")');
    await page.getByText("Recall@5").waitFor();
    await page.click('.main-nav button:has-text("Nhật ký truy vấn")');
    await page.getByText("Không hữu ích · Thiếu nguồn").waitFor();
    assert((await page.locator('.nav-button:has-text("Nhật ký truy vấn") b').textContent()) === "2", "badge 👎 24 giờ");
    await page.click('.main-nav button:has-text("Quản lý tài khoản")');
    await page.getByText("demo01@bv-rag.local", { exact: false }).waitFor();
    await page.click('button:has-text("Tạo tài khoản")');
    await page.fill('input[placeholder="demo04"]', "demo09");
    await page.fill('input[placeholder="demo04@bv-rag.local"]', "demo09@bv-rag.local");
    await page.click('.modal-actions button:has-text("Tạo tài khoản")');
    await page.getByText("TamThoi123!x").waitFor();
    await page.click('button:has-text("Đã lưu")');
    await page.click('.main-nav button:has-text("Cấu hình")');
    await page.click('.config-option:has-text("B3")');
    await page.click('button:has-text("Áp dụng cấu hình")');
    await page.getByText("Đã chuyển sang B3", { exact: false }).waitFor();
    await page.click('button:has-text("So sánh cấu hình")');
    await page.fill(".compare-query input", "Thời gian chờ An Gia?");
    await page.click('button:has-text("Chạy so sánh")');
    await page.getByText("Không RAG.").waitFor();
    await page.click('.sidebar-footer button:has-text("Trạng thái hệ thống")');
    await page.getByText("Tất cả thành phần đang hoạt động").waitFor();
    await page.keyboard.press("Escape");
    assert(!(await page.locator(".modal-card").count()), "Escape đóng modal");

    step("xem như người dùng");
    // Xem như người dùng: ẩn menu quản trị; đăng xuất
    await page.click(".profile-button");
    await page.click('button:has-text("Xem như Người dùng")');
    assert(!(await page.locator('.main-nav button:has-text("Dashboard")').count()), "ẩn menu quản trị");
    await page.screenshot({ path: path.join(ROOT, "tests/e2e/last_smoke.png") });
    await page.click(".profile-button");
    await page.click('button:has-text("Đăng xuất")');
    await page.getByText("Đăng nhập hệ thống").waitFor();
    assert(!errors.length, `lỗi JS: ${errors.join(" | ")}`);
    console.log("FRONTEND SMOKE OK");
  } catch (e) {
    console.error(e.message);
    console.error(calls.slice(-15).join("\n"));
    if (errors.length) console.error("pageerror:", errors.join(" | "));
    process.exitCode = 1;
  } finally {
    await Promise.race([browser.close(), new Promise((r) => setTimeout(r, 5000))]);
    server.kill();
    setTimeout(() => process.exit(), 500);
  }
})();
