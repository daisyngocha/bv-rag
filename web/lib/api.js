// OPS-08: gọi FastAPI (Colab, qua tunnel cloudflared) với Bearer = access_token Supabase hiện tại.
// VITE_API_URL trỏ link tunnel, vd https://xxxx.trycloudflare.com (mặc định http://localhost:8000).
import { supabase } from "./supabase";

export const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

// Trình duyệt không phân biệt được API tắt với bị chặn CORS: nêu cả hai khả năng.
function connectMessage() {
  return `Không kết nối được API (${API_URL}). Kiểm tra: (1) mở ${API_URL}/health thấy {"ok":true}; `
    + `(2) CORS_ORIGINS trên Colab có ${window.location.origin}; (3) VITE_API_URL đúng link tunnel hiện tại.`;
}

async function authHeaders() {
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function errorFrom(res) {
  let detail = res.statusText;
  try {
    const body = await res.json();
    detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail ?? body);
  } catch { /* không phải JSON */ }
  return new ApiError(res.status, detail || `HTTP ${res.status}`);
}

export async function apiFetch(path, { method = "GET", body, signal } = {}) {
  let res;
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      signal,
      headers: { ...(await authHeaders()), ...(body !== undefined ? { "Content-Type": "application/json" } : {}) },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch (e) {
    if (e.name === "AbortError") throw e;
    throw new ApiError(0, connectMessage());
  }
  if (!res.ok) throw await errorFrom(res);
  return res.status === 204 ? null : res.json();
}

// PT-CHAT-02: POST /chat/ask/stream, đọc Server-Sent Events bằng fetch (EventSource không gửi được header).
// onEvent({ event: "status" | "token" | "done" | "error", data }). Trả payload của sự kiện done.
export async function askStream(body, onEvent, signal) {
  let res;
  try {
    res = await fetch(`${API_URL}/chat/ask/stream`, {
      method: "POST",
      signal,
      headers: { ...(await authHeaders()), "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify(body),
    });
  } catch (e) {
    if (e.name === "AbortError") throw e;
    throw new ApiError(0, connectMessage());
  }
  if (!res.ok) throw await errorFrom(res);
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let done = null;
  for (;;) {
    const { value, done: finished } = await reader.read();
    if (value) buffer += decoder.decode(value, { stream: true });
    let cut;
    while ((cut = buffer.indexOf("\n\n")) >= 0) {
      const block = buffer.slice(0, cut);
      buffer = buffer.slice(cut + 2);
      const event = /^event: (.*)$/m.exec(block)?.[1];
      const raw = /^data: (.*)$/m.exec(block)?.[1];
      if (!event || raw === undefined) continue;
      const data = JSON.parse(raw);
      onEvent?.({ event, data });
      if (event === "done") done = data;
      if (event === "error") throw new ApiError(500, data.message || "Lỗi khi sinh câu trả lời");
    }
    if (finished) break;
  }
  if (!done) throw new ApiError(500, "Luồng trả lời kết thúc mà không có kết quả");
  return done;
}

export const api = {
  health: () => apiFetch("/admin/health"),
  setActiveConfig: (config) => apiFetch("/admin/configs/active", { method: "PUT", body: { config } }),
  compare: (question, configs) => apiFetch("/admin/compare", { method: "POST", body: { question, configs } }),
  listUsers: () => apiFetch("/admin/users"),
  createUser: (user) => apiFetch("/admin/users", { method: "POST", body: user }),
  updateUser: (id, patch) => apiFetch(`/admin/users/${id}`, { method: "PATCH", body: patch }),
  resetPassword: (id) => apiFetch(`/admin/users/${id}/reset-password`, { method: "POST" }),
};
