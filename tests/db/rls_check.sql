-- Kiểm tra migrations: trigger, ràng buộc, RLS/GRANT, view, RPC. Chạy trên DB vừa áp migrations (dữ liệu giả, rollback cuối file).
-- psql -v ON_ERROR_STOP=1 -f tests/db/rls_check.sql   → lỗi đầu tiên dừng script; in "RLS CHECK OK" khi qua hết.
\set QUIET on
begin;

-- ---------- Dữ liệu giả (chạy với quyền postgres) ----------
insert into auth.users (id, email, raw_user_meta_data, raw_app_meta_data) values
  ('00000000-0000-0000-0000-0000000000a1', 'admin01@bv-rag.local', '{"username":"admin01","display_name":"Quản trị"}', '{"role":"admin"}'),
  ('00000000-0000-0000-0000-0000000000b1', 'demo01@bv-rag.local',  '{"username":"demo01","role":"admin"}', '{}'),
  ('00000000-0000-0000-0000-0000000000b2', 'demo02@bv-rag.local',  '{}', '{}');

do $$ begin
  assert (select count(*) from public.profiles) = 3, 'handle_new_user phải tạo 3 profiles';
  assert (select count(*) from public.user_settings) = 3, 'default_settings phải tạo 3 user_settings';
  assert (select role from public.profiles where username = 'admin01') = 'admin', 'role admin lấy từ app_metadata';
  assert (select role from public.profiles where username = 'demo01') = 'user', 'role trong user_metadata bị bỏ qua';
  assert (select username from public.profiles where id = '00000000-0000-0000-0000-0000000000b2') = 'demo02', 'username mặc định = phần trước @';
end $$;

insert into public.data_versions (version, is_active, n_chunks) values ('v1', true, 1);
insert into public.products values ('BVP', 'Bảo Việt An Gia', 'BHBV', 'suc_khoe', true);
insert into public.documents (product_code, doc_type, source_file, url, effective_date, downloaded_at)
  values ('BVP', 'quy_tac', 'bvp_quytac.pdf', 'https://example.invalid/bvp', '2025-06-27', '2026-10-25');
insert into public.chunks (data_version, chunk_id, document_id, product_code, doc_type, section_path, page, text)
  select 'v1', 'BVP_QT_C2_M3', id, 'BVP', 'quy_tac', 'Chương II > Mục III', 7,
         E'[Bảo Việt An Gia | Quy tắc | Thời gian chờ]\nThời gian chờ 30 ngày.' from public.documents;
insert into public.sample_questions values ('v1-0002', 'Thời hạn giải quyết bồi thường?', 'lookup', '{BVP}', true);
insert into public.pipeline_configs (name, params) values ('B4', '{"name":"B4"}');
insert into public.runs (run_id, config_name, data_version, split, runtime, started_at)
  values ('B4_demo_20261120-0930', 'B4', 'v1', 'demo', 'colab', now());

-- Hội thoại do FastAPI (service_role) ghi.
set local role service_role;
insert into public.conversations (id, user_id, title) values
  ('00000000-0000-0000-0000-0000000000c1', '00000000-0000-0000-0000-0000000000b1', 'Thời gian chờ An Gia'),
  ('00000000-0000-0000-0000-0000000000c2', '00000000-0000-0000-0000-0000000000b2', 'Câu của demo02');
insert into public.messages (id, conversation_id, role, content) values
  ('00000000-0000-0000-0000-0000000001a1', '00000000-0000-0000-0000-0000000000c1', 'user', 'Thời gian chờ điều trị nội trú?'),
  ('00000000-0000-0000-0000-0000000002a1', '00000000-0000-0000-0000-0000000000c2', 'user', 'Câu hỏi riêng của demo02');
insert into public.messages (id, conversation_id, reply_to_id, role, content, run_id) values
  ('00000000-0000-0000-0000-0000000001a2', '00000000-0000-0000-0000-0000000000c1', '00000000-0000-0000-0000-0000000001a1', 'assistant', 'Thời gian chờ là 30 ngày [1].', 'B4_demo_20261120-0930'),
  ('00000000-0000-0000-0000-0000000002a2', '00000000-0000-0000-0000-0000000000c2', '00000000-0000-0000-0000-0000000002a1', 'assistant', 'Trả lời demo02.', 'B4_demo_20261120-0930');
insert into public.message_citations values ('00000000-0000-0000-0000-0000000001a2', 1, 'v1', 'BVP_QT_C2_M3');
insert into public.traces (message_id, detected_products, retrieval_mode, latency_ms) values
  ('00000000-0000-0000-0000-0000000001a2', '{BVP}', 'hybrid', 2310),
  ('00000000-0000-0000-0000-0000000002a2', null, 'hybrid', 4100);
insert into public.retrieval_logs values ('00000000-0000-0000-0000-0000000001a2', 1, 'v1', 'BVP_QT_C2_M3', 0.82, 0.71, true);
reset role;

-- ---------- Ràng buộc ----------
do $$ begin
  begin
    insert into public.data_versions (version, is_active) values ('v2', true);
    raise exception 'FAIL: cho phép 2 data_version active';
  exception when unique_violation then null; end;
  begin
    insert into public.messages (conversation_id, reply_to_id, role, content)
      values ('00000000-0000-0000-0000-0000000000c1', '00000000-0000-0000-0000-0000000001a1', 'assistant', 'thiếu run_id');
    raise exception 'FAIL: câu trả lời thiếu run_id';
  exception when check_violation then null; end;
  begin
    insert into public.messages (conversation_id, role, content, refusal_reason)
      values ('00000000-0000-0000-0000-0000000000c1', 'user', 'x', 'ngoai_pham_vi');
    raise exception 'FAIL: refusal_reason khi refused = false';
  exception when check_violation then null; end;
  begin
    update public.user_settings set font_size = 30 where user_id = '00000000-0000-0000-0000-0000000000b1';
    raise exception 'FAIL: font_size ngoài 12–20';
  exception when check_violation then null; end;
end $$;

-- ---------- Người dùng demo01 ----------
set local role authenticated;
select set_config('request.jwt.claims', '{"sub":"00000000-0000-0000-0000-0000000000b1","role":"authenticated"}', true) as _jwt \gset

do $$ declare r record; begin
  assert (select count(*) from public.profiles) = 1, 'user chỉ thấy profile của mình';
  assert (select count(*) from public.user_settings) = 1, 'user chỉ thấy settings của mình';
  update public.user_settings set font_size = 16, language = 'en';
  assert (select font_size from public.user_settings) = 16, 'user sửa được settings của mình';

  select * into r from public.v_conversation_list;
  assert (select count(*) from public.v_conversation_list) = 1, 'user chỉ thấy cuộc của mình';
  assert r.preview = 'Thời gian chờ điều trị nội trú?' and r.n_messages = 2, 'preview/n_messages sai';
  assert (select count(*) from public.messages) = 2, 'user chỉ thấy tin nhắn của mình';
  assert (select count(*) from public.traces) = 0, 'user không đọc traces';
  assert (select count(*) from public.retrieval_logs) = 0, 'user không đọc retrieval_logs';
  assert (select count(*) from public.runs) = 0, 'user không đọc runs';
  assert (select count(*) from public.v_query_logs) = 0, 'user không đọc v_query_logs';
  assert (select count(*) from public.products) = 1 and (select count(*) from public.chunks) = 1, 'user đọc kho tri thức';
  assert (select count(*) from public.v_catalog) = 1 and (select n_chunks from public.v_catalog) = 1, 'v_catalog sai';
  assert (select text from public.v_message_sources) = 'Thời gian chờ 30 ngày.', 'v_message_sources phải bỏ context header';
  assert (select count(*) from public.search_conversations('nội trú')) = 1, 'search theo nội dung tin nhắn';
  assert (select count(*) from public.search_conversations('an gia')) = 1, 'search theo tiêu đề';
  assert (select count(*) from public.search_conversations('demo02')) = 0, 'search không lộ cuộc người khác';

  update public.conversations set title = 'Đổi tên', title_is_custom = true where id = '00000000-0000-0000-0000-0000000000c1';
  assert (select title from public.conversations where id = '00000000-0000-0000-0000-0000000000c1') = 'Đổi tên', 'đổi tên';
  update public.conversations set title = 'hack' where id = '00000000-0000-0000-0000-0000000000c2';
  assert not found, 'không đổi tên cuộc người khác';

  begin
    insert into public.messages (conversation_id, role, content) values ('00000000-0000-0000-0000-0000000000c1', 'user', 'tự chèn');
    raise exception 'FAIL: user tự chèn message';
  exception when insufficient_privilege then null; end;
  begin
    insert into public.message_citations values ('00000000-0000-0000-0000-0000000001a2', 2, 'v1', 'BVP_QT_C2_M3');
    raise exception 'FAIL: user tự chèn citation';
  exception when insufficient_privilege then null; end;
  begin
    insert into public.conversations (user_id, title) values ('00000000-0000-0000-0000-0000000000b1', 'tự tạo');
    raise exception 'FAIL: user tự tạo conversation';
  exception when insufficient_privilege then null; end;
  begin
    update public.conversations set user_id = '00000000-0000-0000-0000-0000000000b2';
    raise exception 'FAIL: user sửa user_id';
  exception when insufficient_privilege then null; end;
  begin
    update public.profiles set role = 'admin';
    raise exception 'FAIL: user tự nâng quyền';
  exception when insufficient_privilege then null; end;
  begin
    insert into public.products values ('XXX', 'x', 'x', 'x', true);
    raise exception 'FAIL: user ghi kho tri thức';
  exception when insufficient_privilege then null; end;
  begin
    perform public.demo_metrics(now() - interval '1 day', now() + interval '1 day');
    raise exception 'FAIL: user gọi demo_metrics';
  exception when insufficient_privilege then null; end;

  -- feedback
  insert into public.feedback (message_id, user_id, rating, reason)
    values ('00000000-0000-0000-0000-0000000001a2', '00000000-0000-0000-0000-0000000000b1', -1, 'trich_dan_sai');
  insert into public.feedback (message_id, user_id, rating)
    values ('00000000-0000-0000-0000-0000000001a2', '00000000-0000-0000-0000-0000000000b1', 1)
    on conflict (message_id, user_id) do update set rating = excluded.rating, reason = null;
  assert (select rating from public.feedback) = 1, 'upsert feedback';
  begin
    insert into public.feedback (message_id, user_id, rating, reason)
      values ('00000000-0000-0000-0000-0000000001a1', '00000000-0000-0000-0000-0000000000b1', -1, 'khac');
    raise exception 'FAIL: feedback cho câu hỏi (role = user)';
  exception when insufficient_privilege then null; end;
  begin
    insert into public.feedback (message_id, user_id, rating, reason)
      values ('00000000-0000-0000-0000-0000000002a2', '00000000-0000-0000-0000-0000000000b1', -1, 'khac');
    raise exception 'FAIL: feedback cho câu trả lời của người khác';
  exception when insufficient_privilege then null; end;
  begin
    update public.feedback set rating = -1, reason = null;
    raise exception 'FAIL: rating -1 không có lý do';
  exception when check_violation then null; end;
end $$;
reset role;

-- ---------- Admin ----------
set local role authenticated;
select set_config('request.jwt.claims', '{"sub":"00000000-0000-0000-0000-0000000000a1","role":"authenticated"}', true) as _jwt \gset
do $$ declare m jsonb; begin
  assert (select count(*) from public.profiles) = 3, 'admin đọc mọi profile';
  assert (select count(*) from public.v_conversation_list) = 2, 'admin đọc mọi cuộc';
  assert (select count(*) from public.traces) = 2 and (select count(*) from public.retrieval_logs) = 1, 'admin đọc traces';
  assert (select count(*) from public.runs) = 1, 'admin đọc runs';
  assert (select count(*) from public.v_query_logs) = 2, 'admin đọc v_query_logs';
  assert (select rating from public.v_query_logs where username = 'demo01') = 1, 'v_query_logs gắn feedback';
  assert (select count(*) from public.user_settings) = 1, 'admin không đọc settings người khác (RLS sheet)';
  m := public.demo_metrics(now() - interval '1 day', now() + interval '1 day');
  assert (m ->> 'n_questions')::int = 2, 'demo_metrics n_questions';
  assert (m ->> 'refusal_rate')::float = 0 and (m ->> 'positive_rate')::float = 1, 'demo_metrics tỷ lệ';
  assert jsonb_array_length(m -> 'by_product') = 2, 'by_product gồm BVP và khac';
  assert (public.demo_metrics(now() - interval '1 day', now() + interval '1 day', 'B0') ->> 'n_questions')::int = 0, 'lọc config';
  begin
    insert into public.messages (conversation_id, role, content) values ('00000000-0000-0000-0000-0000000000c1', 'user', 'x');
    raise exception 'FAIL: admin JWT ghi messages';
  exception when insufficient_privilege then null; end;
end $$;
reset role;

-- ---------- anon ----------
set local role anon;
select set_config('request.jwt.claims', '{"role":"anon"}', true) as _jwt \gset
do $$ begin
  begin
    perform 1 from public.products;
    raise exception 'FAIL: anon đọc products';
  exception when insufficient_privilege then null; end;
end $$;
reset role;

-- ---------- Xóa cuộc (cascade) + trigger touch ----------
set local role authenticated;
select set_config('request.jwt.claims', '{"sub":"00000000-0000-0000-0000-0000000000b1","role":"authenticated"}', true) as _jwt \gset
delete from public.conversations where id = '00000000-0000-0000-0000-0000000000c1';
reset role;
do $$ begin
  assert (select count(*) from public.messages where conversation_id = '00000000-0000-0000-0000-0000000000c1') = 0, 'cascade messages';
  assert (select count(*) from public.message_citations) = 0 and (select count(*) from public.feedback) = 0, 'cascade citations/feedback';
  assert (select count(*) from public.traces) = 1, 'cascade traces';
  assert (select count(*) from public.conversations) = 1, 'chỉ xóa cuộc của mình';
end $$;

\echo RLS CHECK OK
rollback;
