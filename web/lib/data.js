// Truy vấn Supabase trực tiếp bằng supabase-js (tầng Supabase trong MethodList v2). Quyền do RLS quyết định.
import { supabase } from "./supabase";

function check({ data, error, count }) {
  if (error) throw new Error(error.message || String(error));
  return count !== undefined && count !== null && data === null ? count : data;
}

// ---------- Tài khoản, cài đặt (PT-AUTH-03, PT-SET-01, PT-SET-02)
export async function getProfile(uid) {
  return check(await supabase.from("profiles").select("id,username,display_name,role,is_active").eq("id", uid).single());
}

export async function getSettings(uid) {
  return check(await supabase.from("user_settings").select("*").eq("user_id", uid).maybeSingle());
}

export async function saveSettings(uid, patch) {
  return check(await supabase.from("user_settings").update(patch).eq("user_id", uid));
}

// ---------- Hỏi đáp (PT-CHAT-03, 04, 05)
export async function listProducts() {
  return check(await supabase.from("products").select("product_code,product_name,line").eq("is_active", true).order("product_code"));
}

export async function listSampleQuestions() {
  return check(await supabase.from("sample_questions").select("qid,question,question_group,products").eq("is_active", true));
}

export async function saveFeedback({ message_id, user_id, rating, reason = null, comment = null }) {
  return check(await supabase.from("feedback")
    .upsert({ message_id, user_id, rating, reason, comment }, { onConflict: "message_id,user_id" }));
}

// ---------- Danh mục (PT-CHAT-12)
export async function getCatalog() {
  const [rows, version] = await Promise.all([
    supabase.from("v_catalog").select("*").order("product_code"),
    supabase.from("data_versions").select("version,n_chunks").eq("is_active", true).maybeSingle(),
  ]);
  return { rows: check(rows), version: check(version) };
}

// ---------- Lịch sử (PT-HIS-01…06). Admin đọc được mọi cuộc qua RLS nên luôn lọc user_id của mình.
export async function listConversations(uid, { q = "", lim = 50, off = 0 } = {}) {
  if (q.trim()) {
    const rows = check(await supabase.rpc("search_conversations", { q: q.trim(), lim, off }));
    return rows.filter((r) => r.user_id === uid);
  }
  return check(await supabase.from("v_conversation_list").select("*").eq("user_id", uid)
    .order("updated_at", { ascending: false }).range(off, off + lim - 1));
}

export async function loadConversation(conversationId) {
  const messages = check(await supabase.from("messages")
    .select("id,conversation_id,reply_to_id,role,content,pii_masked,product_filter,refused,refusal_reason,run_id,created_at")
    .eq("conversation_id", conversationId).order("created_at"));
  const ids = messages.filter((m) => m.role === "assistant").map((m) => m.id);
  if (!ids.length) return messages;
  const [sources, feedback] = await Promise.all([
    supabase.from("v_message_sources").select("*").in("message_id", ids).order("ord"),
    supabase.from("feedback").select("message_id,rating,reason").in("message_id", ids),
  ]);
  const src = check(sources);
  const fb = Object.fromEntries(check(feedback).map((f) => [f.message_id, f]));
  return messages.map((m) => m.role !== "assistant" ? m : {
    ...m, sources: src.filter((s) => s.message_id === m.id), feedback: fb[m.id] || null,
  });
}

export async function renameConversation(id, title) {
  return check(await supabase.from("conversations").update({ title, title_is_custom: true }).eq("id", id));
}

export async function deleteConversation(id) {
  return check(await supabase.from("conversations").delete().eq("id", id));
}

export async function deleteAllConversations(uid) {
  return check(await supabase.from("conversations").delete().eq("user_id", uid));
}

// ---------- Cấu hình, vết xử lý (PT-SET-03, PT-SET-06)
export async function getConfigs() {
  const [configs, active] = await Promise.all([
    supabase.from("pipeline_configs").select("name,description,params").order("name"),
    supabase.from("app_settings").select("value").eq("key", "active_config").maybeSingle(),
  ]);
  return { configs: check(configs), active: check(active)?.value || null };
}

export async function getTrace(messageId) {
  const [trace, logs] = await Promise.all([
    supabase.from("traces").select("*").eq("message_id", messageId).maybeSingle(),
    supabase.from("retrieval_logs").select("*").eq("message_id", messageId).order("rank"),
  ]);
  return { trace: check(trace), logs: check(logs) };
}

// ---------- Quản trị (PT-ADM-05, 07, 08, 09)
export async function listQueryLogs({ filter = "all", q = "", lim = 100 } = {}) {
  let query = supabase.from("v_query_logs").select("*", { count: "exact" });
  if (filter === "refused") query = query.eq("refused", true);
  if (filter === "down") query = query.eq("rating", -1);
  if (filter === "slow") query = query.gt("latency_ms", 4000);
  const s = q.trim().replace(/[%,()]/g, " ");
  if (s) query = query.or(`question.ilike.%${s}%,run_id.ilike.%${s}%`);
  const { data, error, count } = await query.order("created_at", { ascending: false }).range(0, lim - 1);
  if (error) throw new Error(error.message);
  return { rows: data, count };
}

export async function countNegativeFeedback24h() {
  const since = new Date(Date.now() - 24 * 3600 * 1000).toISOString();
  const { count, error } = await supabase.from("v_query_logs").select("message_id", { count: "exact", head: true })
    .eq("rating", -1).gte("created_at", since);
  if (error) throw new Error(error.message);
  return count || 0;
}

export async function getDemoMetrics(dateFrom, dateTo, config = null) {
  return check(await supabase.rpc("demo_metrics", { date_from: dateFrom, date_to: dateTo, config }));
}

// Chất lượng B0–B4 trên tập test: lần chạy test mới nhất của mỗi cấu hình.
export async function getEvalQuality(metrics = ["recall@5", "faithfulness_j1"]) {
  const rows = check(await supabase.from("eval_results")
    .select("run_id,question_group,metric,value,runs!inner(config_name,split,started_at)")
    .eq("question_group", "all").in("metric", metrics).eq("runs.split", "test"));
  const latest = {};
  for (const r of rows) {
    const cfg = r.runs.config_name;
    if (!latest[cfg] || r.runs.started_at > latest[cfg].started_at) latest[cfg] = { run_id: r.run_id, started_at: r.runs.started_at };
  }
  const out = {};
  for (const r of rows) {
    const cfg = r.runs.config_name;
    if (latest[cfg].run_id !== r.run_id) continue;
    out[cfg] = { ...(out[cfg] || { name: cfg, run_id: r.run_id }), [r.metric]: Number(r.value) };
  }
  return Object.values(out).sort((a, b) => a.name.localeCompare(b.name));
}
