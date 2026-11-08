// Tiện ích phía trình duyệt (tầng Client trong MethodList v2).

// PT-CHAT-06: che TTCN để hiển thị/cảnh báo trước khi gửi. Giữ khớp app/privacy.py (server vẫn che lại và là
// bản được lưu). Thứ tự: email → CCCD 12 số → SĐT (0/84/+84 + 9 số) → CMND 9 số.
const PII = [
  ["[EMAIL]", /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g],
  ["[CCCD]", /(?<![\d.,])\d{12}(?![\d.,]?\d)/g],
  ["[SĐT]", /(?<![\d.,])(?:\+84|84|0)(?:[\s.-]?\d){9}(?![\d.,]?\d)/g],
  ["[CMND]", /(?<![\d.,])\d{9}(?![\d.,]?\d)/g],
];

export function maskPreview(text) {
  let out = text;
  let n = 0;
  for (const [token, re] of PII) {
    out = out.replace(re, () => { n += 1; return token; });
  }
  return { text: out, masked: n > 0 };
}

export function formatDate(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("vi-VN", { day: "2-digit", month: "2-digit", year: "numeric" }).format(new Date(value));
}

export function formatDateTime(value) {
  if (!value) return "—";
  return new Intl.DateTimeFormat("vi-VN", { day: "2-digit", month: "2-digit", year: "numeric", hour: "2-digit", minute: "2-digit" }).format(new Date(value));
}

export function formatShort(value) {
  if (!value) return "";
  return new Date(value).toLocaleString("vi-VN", { day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit" });
}

export function initials(name = "") {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "?";
  return (parts.length === 1 ? parts[0].slice(0, 2) : parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

function download(name, content, type) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

export function sourceLine(s) {
  return `[${s.ord}] ${s.product_name || s.product_code || ""} · ${s.source_file || ""} · ${s.section_path || ""}`
    + `${s.page ? ` · trang ${s.page}` : ""} · ${s.data_version}/${s.chunk_id}${s.url ? ` · ${s.url}` : ""}`;
}

// PT-HIS-07: xuất đúng cuộc trò chuyện (câu hỏi, câu trả lời, nguồn của từng câu trả lời).
export function exportMarkdown(title, messages) {
  const parts = [`# ${title || "Cuộc trò chuyện Bảo Việt"}`, ""];
  for (const m of messages) {
    parts.push(`## ${m.role === "user" ? "Người dùng" : "Trợ lý"}`, "", m.content, "");
    if (m.role === "assistant" && m.sources?.length) {
      parts.push("**Nguồn**", "", ...m.sources.map((s) => `- ${sourceLine(s)}`), "");
    }
  }
  parts.push("---", "_Thông tin chỉ mang tính tham khảo. Căn cứ cuối cùng là quy tắc và hợp đồng được phát hành._");
  const slug = (title || "cuoc-tro-chuyen").normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/đ/gi, "d")
    .toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 60);
  download(`${slug || "cuoc-tro-chuyen"}.md`, parts.join("\n"), "text/markdown;charset=utf-8");
}

// PT-ADM-06
export function exportCsv(name, rows, columns) {
  const esc = (v) => {
    const s = v === null || v === undefined ? "" : Array.isArray(v) ? v.join(";") : String(v);
    return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
  };
  const csv = [columns.join(","), ...rows.map((r) => columns.map((c) => esc(r[c])).join(","))].join("\n");
  download(name, "﻿" + csv, "text/csv;charset=utf-8");
}

export const LABELS = {
  vi: {
    question_group: { lookup: "Tra cứu quy tắc", table: "Bảng phí", compare: "So sánh", scenario: "Tình huống" },
    feedback_reason: { sai_noi_dung: "Sai nội dung", thieu_nguon: "Thiếu nguồn", trich_dan_sai: "Trích dẫn sai", tu_choi_nham: "Từ chối nhầm", khac: "Khác" },
    doc_type: { quy_tac: "Quy tắc", dieu_khoan: "Điều khoản", bang_phi: "Biểu phí", bang_quyen_loi: "Bảng quyền lợi", brochure: "Tờ rơi", faq: "Hỏi đáp" },
    line: { phi_nhan_tho: "Phi nhân thọ", nhan_tho: "Nhân thọ", suc_khoe: "Sức khỏe", benh_hiem_ngheo: "Bệnh hiểm nghèo", du_lich: "Du lịch" },
    refusal_reason: { khong_du_can_cu: "Không đủ căn cứ trong tài liệu", ngoai_pham_vi: "Ngoài phạm vi sản phẩm hiện có" },
  },
  en: {
    question_group: { lookup: "Rule lookup", table: "Premium table", compare: "Comparison", scenario: "Scenario" },
    feedback_reason: { sai_noi_dung: "Incorrect content", thieu_nguon: "Missing sources", trich_dan_sai: "Incorrect citation", tu_choi_nham: "Incorrect refusal", khac: "Other" },
    doc_type: { quy_tac: "Policy rules", dieu_khoan: "Terms", bang_phi: "Premium table", bang_quyen_loi: "Benefits table", brochure: "Brochure", faq: "FAQ" },
    line: { phi_nhan_tho: "Non-life", nhan_tho: "Life", suc_khoe: "Health", benh_hiem_ngheo: "Critical illness", du_lich: "Travel" },
    refusal_reason: { khong_du_can_cu: "Not enough grounds in the documents", ngoai_pham_vi: "Outside the available products" },
  },
};
