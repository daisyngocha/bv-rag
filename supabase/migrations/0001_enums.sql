-- ĐA1 · 0001: extension và kiểu enum (5.DA1_DataDictionary.xlsx › Enum; MethodList v2 DB-01).
-- Nhóm E (policies, tool_calls, claim_cases, claim_documents) thuộc ĐA2/ĐATN: chưa tạo.

create schema if not exists extensions;
create extension if not exists pg_trgm with schema extensions;   -- tìm lịch sử (UC-HIS-03)

create type public.user_role       as enum ('user', 'admin');
create type public.msg_role        as enum ('user', 'assistant');            -- ĐA2 thêm: tool
create type public.theme_mode      as enum ('light', 'dark', 'system');
create type public.citation_style  as enum ('inline', 'footnote');           -- inline: [n] trong câu; footnote: cuối câu trả lời
create type public.feedback_reason as enum ('sai_noi_dung', 'thieu_nguon', 'trich_dan_sai', 'tu_choi_nham', 'khac');
create type public.doc_type        as enum ('quy_tac', 'dieu_khoan', 'bang_phi', 'bang_quyen_loi', 'brochure', 'faq');
create type public.ui_language     as enum ('vi', 'en');
