export const DATA_VERSIONS = [
  {
    version: "v2",
    is_active: true,
    n_chunks: 3618,
    note: "Chunk theo mục cấp thấp nhất; bảng = 1 chunk",
    created_at: "2026-11-20T09:31:05+07:00",
  },
];

export const PRODUCTS = [
  { product_code: "BVP", product_name: "Bảo Việt An Gia", company: "BHBV", line: "suc_khoe", is_active: true },
  { product_code: "BTB", product_name: "Bảo Việt Tâm Bình", company: "BHBV", line: "suc_khoe", is_active: true },
  { product_code: "ITC", product_name: "Bảo Việt Intercare", company: "BHBV", line: "suc_khoe", is_active: true },
  { product_code: "C37", product_name: "37 bệnh hiểm nghèo", company: "BHBV", line: "benh_hiem_ngheo", is_active: true },
  { product_code: "FLX", product_name: "Du lịch Flexi", company: "BHBV", line: "du_lich", is_active: true },
];

export const DOCUMENTS = [
  { id: 1, product_code: "BVP", doc_type: "quy_tac", source_file: "BVP_quytac.pdf", url: "https://baovietonline.com.vn/", effective_date: "2025-06-27", downloaded_at: "2026-10-25" },
  { id: 2, product_code: "BVP", doc_type: "bang_quyen_loi", source_file: "BVP_bangquyenloi.pdf", url: "https://baovietonline.com.vn/", effective_date: "2025-06-27", downloaded_at: "2026-10-25" },
  { id: 3, product_code: "BTB", doc_type: "quy_tac", source_file: "BTB_quytac.pdf", url: "https://baovietonline.com.vn/", effective_date: "2025-06-27", downloaded_at: "2026-10-25" },
  { id: 4, product_code: "ITC", doc_type: "dieu_khoan", source_file: "ITC_dieukhoan.pdf", url: "https://baovietonline.com.vn/", effective_date: "2025-06-27", downloaded_at: "2026-10-25" },
  { id: 5, product_code: "C37", doc_type: "bang_quyen_loi", source_file: "C37_bangquyenloi.pdf", url: "https://baovietonline.com.vn/", effective_date: "2025-06-27", downloaded_at: "2026-10-25" },
  { id: 6, product_code: "FLX", doc_type: "bang_phi", source_file: "FLX_bangphi.pdf", url: "https://baovietonline.com.vn/", effective_date: "2025-06-27", downloaded_at: "2026-10-25" },
];

export const CHUNKS = [
  { data_version: "v2", chunk_id: "BVP_QT_C4_D18_K2", document_id: 1, product_code: "BVP", doc_type: "quy_tac", section_path: "Chương IV > Điều 18 > Khoản 2", page: 24, is_table: false, effective_date: "2025-06-27", text: "Trong thời hạn 15 ngày làm việc kể từ ngày nhận được đầy đủ hồ sơ yêu cầu trả tiền bảo hiểm hợp lệ…" },
  { data_version: "v2", chunk_id: "BVP_QT_C4_D17_K1", document_id: 1, product_code: "BVP", doc_type: "quy_tac", section_path: "Chương IV > Điều 17 > Khoản 1", page: 23, is_table: false, effective_date: "2025-06-27", text: "Người được bảo hiểm hoặc người thụ hưởng có trách nhiệm gửi hồ sơ yêu cầu trả tiền bảo hiểm…" },
];

export const CONVERSATIONS = [
  { id: "8c41d2f7-2a6e-4b19-b3d5-6e0f1a9c4d27", user_id: "3f2a9c1e-7b4d-4e2a-9c1f-2d8e5a6b7c90", title: "Quyền lợi nội trú An Gia", title_is_custom: false, created_at: "2026-11-20T10:42:00+07:00", updated_at: "2026-11-20T10:42:20+07:00" },
  { id: "4c15d2f7-9a6e-4b19-b3d5-6e0f1a9c4d88", user_id: "3f2a9c1e-7b4d-4e2a-9c1f-2d8e5a6b7c90", title: "So sánh CI37 và Intercare", title_is_custom: true, created_at: "2026-11-19T15:20:00+07:00", updated_at: "2026-11-19T15:21:08+07:00" },
  { id: "7a41d2f7-2a6e-4b19-b3d5-6e0f1a9c4d31", user_id: "3f2a9c1e-7b4d-4e2a-9c1f-2d8e5a6b7c90", title: "Phí bảo hiểm du lịch Flexi", title_is_custom: false, created_at: "2026-11-12T09:14:00+07:00", updated_at: "2026-11-12T09:14:32+07:00" },
  { id: "2f41d2f7-2a6e-4b19-b3d5-6e0f1a9c4d19", user_id: "3f2a9c1e-7b4d-4e2a-9c1f-2d8e5a6b7c90", title: "Thời gian chờ Tâm Bình", title_is_custom: false, created_at: "2026-11-10T11:08:00+07:00", updated_at: "2026-11-10T11:08:41+07:00" },
];

export const CONVERSATION_MESSAGES = {
  "8c41d2f7-2a6e-4b19-b3d5-6e0f1a9c4d27": "Thời hạn giải quyết quyền lợi bảo hiểm An Gia là bao lâu?",
  "4c15d2f7-9a6e-4b19-b3d5-6e0f1a9c4d88": "So sánh độ tuổi tham gia của CI37 và Intercare.",
  "7a41d2f7-2a6e-4b19-b3d5-6e0f1a9c4d31": "Phí gia đình hạng Kim Cương cho chuyến đi 204–210 ngày?",
  "2f41d2f7-2a6e-4b19-b3d5-6e0f1a9c4d19": "Thời gian chờ quyền lợi thai sản của Tâm Bình?",
};

export const SAMPLE_QUESTIONS = [
  { qid: "v1-0002", question: "Thời hạn giải quyết quyền lợi bảo hiểm An Gia là bao lâu?", question_group: "lookup", products: ["BVP"], is_active: true },
  { qid: "v1-0035", question: "Trẻ 2 tuổi nằm viện nội trú được hưởng quyền lợi gì trong An Gia?", question_group: "scenario", products: ["BVP"], is_active: true },
  { qid: "v1-0053", question: "So sánh độ tuổi tham gia của CI37 và Intercare.", question_group: "compare", products: ["C37", "ITC"], is_active: true },
  { qid: "v1-0022", question: "Phí gia đình của Flexi hạng Kim Cương cho chuyến đi 204–210 ngày?", question_group: "table", products: ["FLX"], is_active: true },
];

export const MESSAGE_CITATIONS = [
  { message_id: "b7e9035a-41c8-4f6d-a2e1-90c3d58f6b14", ord: 1, data_version: "v2", chunk_id: "BVP_QT_C4_D18_K2" },
  { message_id: "b7e9035a-41c8-4f6d-a2e1-90c3d58f6b14", ord: 2, data_version: "v2", chunk_id: "BVP_QT_C4_D17_K1" },
];

export const PIPELINE_CONFIGS = [
  { name: "B0", description: "Không dùng RAG", params: { retrieval: { mode: "none" } }, synced_at: "2026-11-20T09:31:05+07:00" },
  { name: "B1", description: "Dense retrieval, chunk cố định", params: { retrieval: { mode: "dense", top_k: 30 } }, synced_at: "2026-11-20T09:31:05+07:00" },
  { name: "B2", description: "Dense retrieval, chunk theo cấu trúc", params: { retrieval: { mode: "dense", top_k: 30 } }, synced_at: "2026-11-20T09:31:05+07:00" },
  { name: "B3", description: "Hybrid search và query processor", params: { retrieval: { mode: "hybrid", top_k: 30 } }, synced_at: "2026-11-20T09:31:05+07:00" },
  { name: "B4", description: "B3 + reranker + ngưỡng từ chối + prompt trích dẫn", params: { retrieval: { mode: "hybrid", top_k: 30 }, rerank: { top_n: 5, min_score: 0.3 } }, synced_at: "2026-11-20T09:31:05+07:00" },
];

export const APP_SETTINGS = {
  key: "active_config",
  value: { config: "B4" },
  updated_by: "3f2a9c1e-7b4d-4e2a-9c1f-2d8e5a6b7c90",
  updated_at: "2026-11-20T09:31:05+07:00",
};

export const EVAL_RESULTS = [
  { run_id: "B0_v1_test_20261107", question_group: "all", metric: "recall@5", value: 0.24 },
  { run_id: "B1_v1_test_20261107", question_group: "all", metric: "recall@5", value: 0.56 },
  { run_id: "B2_v1_test_20261107", question_group: "all", metric: "recall@5", value: 0.72 },
  { run_id: "B3_v1_test_20261107", question_group: "all", metric: "recall@5", value: 0.84 },
  { run_id: "B4_v1_test_20261107", question_group: "all", metric: "recall@5", value: 0.91 },
  { run_id: "B0_v1_test_20261107", question_group: "all", metric: "faithfulness", value: 0.42 },
  { run_id: "B1_v1_test_20261107", question_group: "all", metric: "faithfulness", value: 0.61 },
  { run_id: "B2_v1_test_20261107", question_group: "all", metric: "faithfulness", value: 0.74 },
  { run_id: "B3_v1_test_20261107", question_group: "all", metric: "faithfulness", value: 0.82 },
  { run_id: "B4_v1_test_20261107", question_group: "all", metric: "faithfulness", value: 0.89 },
];

export const QUERY_LOGS = [
  { message_id: "b7e9035a-41c8-4f6d-a2e1-90c3d58f6b14", content: "Thời hạn giải quyết quyền lợi An Gia?", refused: false, refusal_reason: null, run_id: "B4_demo_20261120-1042", created_at: "2026-11-20T10:42:00+07:00", latency_ms: 3204, rating: 1, feedback_reason: null, config_name: "B4", data_version: "v2", split: "demo", runtime: "colab" },
  { message_id: "e1d4a8c2-5f37-4b90-8e6a-3c2b1d7f9a05", content: "Bảo hiểm xe ô tô có quyền lợi gì?", refused: true, refusal_reason: "ngoai_pham_vi", run_id: "B4_demo_20261120-1031", created_at: "2026-11-20T10:31:00+07:00", latency_ms: 1105, rating: null, feedback_reason: null, config_name: "B4", data_version: "v2", split: "demo", runtime: "colab" },
  { message_id: "a9d4a8c2-5f37-4b90-8e6a-3c2b1d7f9a31", content: "So sánh CI37 và Intercare", refused: false, refusal_reason: null, run_id: "B4_demo_20261120-0958", created_at: "2026-11-20T09:58:00+07:00", latency_ms: 4820, rating: -1, feedback_reason: "thieu_nguon", config_name: "B4", data_version: "v2", split: "demo", runtime: "colab" },
  { message_id: "c7d4a8c2-5f37-4b90-8e6a-3c2b1d7f9a22", content: "Phí Flexi hạng Kim Cương 210 ngày", refused: false, refusal_reason: null, run_id: "B3_demo_20261120-0934", created_at: "2026-11-20T09:34:00+07:00", latency_ms: 2910, rating: 1, feedback_reason: null, config_name: "B3", data_version: "v2", split: "demo", runtime: "colab" },
];

export const ACCOUNTS = [
  { id: "3f2a9c1e-7b4d-4e2a-9c1f-2d8e5a6b7c90", email: "demo01@bv-rag.local", username: "demo01", display_name: "Ngọc Hà", role: "admin", is_active: true, last_sign_in_at: "2026-11-20T09:31:05+07:00", banned_until: null },
  { id: "6a2a9c1e-7b4d-4e2a-9c1f-2d8e5a6b7c11", email: "demo02@bv-rag.local", username: "demo02", display_name: "Người dùng demo 02", role: "user", is_active: true, last_sign_in_at: "2026-11-19T14:10:00+07:00", banned_until: null },
  { id: "8b2a9c1e-7b4d-4e2a-9c1f-2d8e5a6b7c42", email: "demo03@bv-rag.local", username: "demo03", display_name: "Người dùng demo 03", role: "user", is_active: false, last_sign_in_at: "2026-11-05T08:20:00+07:00", banned_until: "2026-12-05T08:20:00+07:00" },
];

export const RETRIEVAL_LOGS = [
  { message_id: "b7e9035a-41c8-4f6d-a2e1-90c3d58f6b14", rank: 1, data_version: "v2", chunk_id: "BVP_QT_C4_D18_K2", score: 0.82, rerank: 0.71, in_context: true },
  { message_id: "b7e9035a-41c8-4f6d-a2e1-90c3d58f6b14", rank: 2, data_version: "v2", chunk_id: "BVP_QT_C4_D17_K1", score: 0.78, rerank: 0.66, in_context: true },
];

export const TRACE = {
  message_id: "b7e9035a-41c8-4f6d-a2e1-90c3d58f6b14",
  query_processed: "thời hạn giải quyết quyền lợi an gia",
  detected_products: ["BVP"],
  retrieval_mode: "hybrid",
  latency_ms: 3204,
  tokens_in: 1284,
  tokens_out: 126,
  cost_usd: 0.0016,
  timings_ms: { retrieve: 12, rerank: 560, generate: 2632 },
  error: null,
};

export const SYSTEMS = [
  { name: "FastAPI", detail: "Endpoint /health", status: "Sẵn sàng", metric: "42 ms" },
  { name: "Ollama", detail: "qwen2.5:7b-instruct-q4_K_M", status: "Đã nạp", metric: "GPU 100%" },
  { name: "Qdrant", detail: "Vector ở Qdrant · không dùng pgvector", status: "Sẵn sàng", metric: "3.618 chunks" },
  { name: "Embedding & reranker", detail: "bge-m3 · bge-reranker-v2-m3", status: "Sẵn sàng", metric: "L4" },
];

export const ENUM_LABELS = {
  user_role: { user: "Người dùng", admin: "Quản trị viên" },
  question_group: { lookup: "Tra cứu quy tắc", table: "Bảng phí", compare: "So sánh", scenario: "Tình huống" },
  feedback_reason: { sai_noi_dung: "Sai nội dung", thieu_nguon: "Thiếu nguồn", trich_dan_sai: "Trích dẫn sai", tu_choi_nham: "Từ chối nhầm", khac: "Khác" },
  doc_type: { quy_tac: "Quy tắc", dieu_khoan: "Điều khoản", bang_phi: "Bảng phí", bang_quyen_loi: "Bảng quyền lợi", brochure: "Brochure", faq: "FAQ" },
  line: { suc_khoe: "Sức khỏe", benh_hiem_ngheo: "Bệnh hiểm nghèo", du_lich: "Du lịch" },
  refusal_reason: { khong_du_can_cu: "Không đủ căn cứ", ngoai_pham_vi: "Ngoài phạm vi" },
};
