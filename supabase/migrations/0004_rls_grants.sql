-- ĐA1 · 0004: is_admin(), RLS và GRANT (DataDictionary › RLS; MethodList v2 DB-03, DB-11…DB-15).
-- Người dùng/admin dùng JWT qua supabase-js (role authenticated). service_role (FastAPI, script) bỏ qua RLS.
-- Ghi nội dung chat (conversations tạo mới, messages, message_citations, traces, retrieval_logs) chỉ qua service_role.
-- GRANT tối thiểu theo bảng (phòng thủ thêm ngoài RLS): thu hồi quyền mặc định của Supabase rồi cấp lại đúng chỗ cần.

create or replace function public.is_admin()
returns boolean
language sql
stable
security definer
set search_path = ''
as $$
  select exists (
    select 1 from public.profiles p
    where p.id = (select auth.uid()) and p.role = 'admin' and p.is_active
  );
$$;
revoke all on function public.is_admin() from public, anon;
grant execute on function public.is_admin() to authenticated, service_role;

-- ---------- GRANT ----------
revoke all on all tables in schema public from anon, authenticated;
grant all on all tables in schema public to service_role;

-- A. Tài khoản
grant select on public.profiles to authenticated;
grant select, update on public.user_settings to authenticated;
-- B. Hội thoại
grant select, delete on public.conversations to authenticated;
grant update (title, title_is_custom) on public.conversations to authenticated;   -- đổi tên (UC-HIS-04)
grant select on public.messages, public.message_citations to authenticated;
grant select on public.traces, public.retrieval_logs to authenticated;            -- RLS: chỉ admin
grant select, insert, update on public.feedback to authenticated;
-- C. Kho tri thức
grant select on public.data_versions, public.products, public.documents, public.chunks,
                public.sample_questions to authenticated;
-- D. Vận hành
grant select on public.pipeline_configs to authenticated;
grant select on public.runs, public.eval_results, public.app_settings to authenticated;  -- RLS: chỉ admin

-- ---------- Bật RLS trên mọi bảng ----------
alter table public.profiles          enable row level security;
alter table public.user_settings     enable row level security;
alter table public.conversations     enable row level security;
alter table public.messages          enable row level security;
alter table public.message_citations enable row level security;
alter table public.traces            enable row level security;
alter table public.retrieval_logs    enable row level security;
alter table public.feedback          enable row level security;
alter table public.data_versions     enable row level security;
alter table public.products          enable row level security;
alter table public.documents         enable row level security;
alter table public.chunks            enable row level security;
alter table public.sample_questions  enable row level security;
alter table public.pipeline_configs  enable row level security;
alter table public.runs              enable row level security;
alter table public.eval_results      enable row level security;
alter table public.app_settings      enable row level security;

-- ---------- A. Tài khoản ----------
create policy profiles_select on public.profiles for select to authenticated
  using (id = (select auth.uid()) or (select public.is_admin()));

create policy user_settings_select on public.user_settings for select to authenticated
  using (user_id = (select auth.uid()));
create policy user_settings_update on public.user_settings for update to authenticated
  using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));

-- ---------- B. Hội thoại ----------
create policy conversations_select on public.conversations for select to authenticated
  using (user_id = (select auth.uid()) or (select public.is_admin()));
create policy conversations_update on public.conversations for update to authenticated
  using (user_id = (select auth.uid())) with check (user_id = (select auth.uid()));
create policy conversations_delete on public.conversations for delete to authenticated
  using (user_id = (select auth.uid()));

-- messages, message_citations: chủ sở hữu chỉ đọc, không có policy INSERT/UPDATE/DELETE (xóa qua cascade).
create policy messages_select on public.messages for select to authenticated
  using (
    (select public.is_admin())
    or exists (select 1 from public.conversations c
               where c.id = messages.conversation_id and c.user_id = (select auth.uid()))
  );
create policy citations_select on public.message_citations for select to authenticated
  using (
    (select public.is_admin())
    or exists (select 1 from public.messages m
               join public.conversations c on c.id = m.conversation_id
               where m.id = message_citations.message_id and c.user_id = (select auth.uid()))
  );

create policy traces_select on public.traces for select to authenticated
  using ((select public.is_admin()));
create policy retrieval_logs_select on public.retrieval_logs for select to authenticated
  using ((select public.is_admin()));

-- feedback: chủ sở hữu đọc/tạo/sửa cho câu trả lời (role = assistant) thuộc cuộc của mình; admin đọc tất cả.
create policy feedback_select on public.feedback for select to authenticated
  using (user_id = (select auth.uid()) or (select public.is_admin()));
create policy feedback_insert on public.feedback for insert to authenticated
  with check (
    user_id = (select auth.uid())
    and exists (select 1 from public.messages m
                join public.conversations c on c.id = m.conversation_id
                where m.id = feedback.message_id and m.role = 'assistant' and c.user_id = (select auth.uid()))
  );
create policy feedback_update on public.feedback for update to authenticated
  using (user_id = (select auth.uid()))
  with check (
    user_id = (select auth.uid())
    and exists (select 1 from public.messages m
                join public.conversations c on c.id = m.conversation_id
                where m.id = feedback.message_id and m.role = 'assistant' and c.user_id = (select auth.uid()))
  );

-- ---------- C. Kho tri thức + pipeline_configs: authenticated chỉ đọc ----------
create policy data_versions_read    on public.data_versions    for select to authenticated using (true);
create policy products_read         on public.products         for select to authenticated using (true);
create policy documents_read        on public.documents        for select to authenticated using (true);
create policy chunks_read           on public.chunks           for select to authenticated using (true);
create policy sample_questions_read on public.sample_questions for select to authenticated using (true);
create policy pipeline_configs_read on public.pipeline_configs for select to authenticated using (true);

-- ---------- D. Vận hành: chỉ admin đọc ----------
create policy runs_select         on public.runs         for select to authenticated using ((select public.is_admin()));
create policy eval_results_select on public.eval_results for select to authenticated using ((select public.is_admin()));
create policy app_settings_select on public.app_settings for select to authenticated using ((select public.is_admin()));
