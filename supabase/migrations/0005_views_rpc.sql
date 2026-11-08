-- ĐA1 · 0005: view và RPC (DataDictionary › View & RPC; MethodList v2 DB-05…DB-10).
-- View đặt security_invoker = true để RLS của bảng gốc có hiệu lực với người gọi.

-- UC-HIS-01, UC-HIS-03: danh sách cuộc trò chuyện + câu hỏi đầu (preview) + số tin nhắn.
-- user_id thêm ngoài danh sách cột trong data dictionary để admin phân biệt chủ sở hữu.
create view public.v_conversation_list with (security_invoker = true) as
select c.id,
       c.user_id,
       c.title,
       c.title_is_custom,
       f.content                       as preview,
       coalesce(n.n_messages, 0)::int  as n_messages,
       c.created_at,
       c.updated_at
from public.conversations c
left join lateral (
  select m.content from public.messages m
  where m.conversation_id = c.id and m.role = 'user'
  order by m.created_at, m.id
  limit 1
) f on true
left join lateral (
  select count(*) as n_messages from public.messages m where m.conversation_id = c.id
) n on true;

-- UC-CHAT-04, UC-CHAT-05, UC-HIS-02: nguồn trích dẫn của câu trả lời; text bỏ dòng context header "[…]".
create view public.v_message_sources with (security_invoker = true) as
select mc.message_id,
       mc.ord,
       mc.data_version,
       mc.chunk_id,
       ch.product_code,
       p.product_name,
       ch.doc_type,
       ch.section_path,
       ch.page,
       ch.is_table,
       ch.effective_date,
       regexp_replace(ch.text, '^\[[^\n]*\]\n', '') as text,
       d.source_file,
       d.url
from public.message_citations mc
join public.chunks ch   on ch.data_version = mc.data_version and ch.chunk_id = mc.chunk_id
join public.documents d on d.id = ch.document_id
join public.products p  on p.product_code = ch.product_code;

-- UC-CHAT-13: danh mục sản phẩm và tài liệu, số chunk của phiên bản dữ liệu đang active.
create view public.v_catalog with (security_invoker = true) as
select p.product_code,
       p.product_name,
       p.company,
       p.line,
       p.is_active,
       d.id                         as document_id,
       d.doc_type,
       d.source_file,
       d.url,
       d.effective_date,
       d.downloaded_at,
       coalesce(k.n_chunks, 0)::int as n_chunks,
       dv.version                   as data_version
from public.products p
left join public.documents d on d.product_code = p.product_code
left join public.data_versions dv on dv.is_active
left join lateral (
  select count(*) as n_chunks from public.chunks ch
  where ch.document_id = d.id and ch.data_version = dv.version
) k on true;

-- UC-ADM-03: nhật ký truy vấn (chỉ admin). Một dòng = một câu trả lời.
create view public.v_query_logs with (security_invoker = true) as
select a.id                 as message_id,
       a.created_at,
       a.run_id,
       q.content            as question,
       a.content            as answer,
       a.refused,
       a.refusal_reason,
       r.config_name,
       r.data_version,
       r.split,
       r.runtime,
       t.latency_ms,
       t.detected_products,
       fb.rating,
       fb.reason            as feedback_reason,
       pr.username
from public.messages a
join public.messages q           on q.id = a.reply_to_id
join public.conversations c      on c.id = a.conversation_id
left join public.profiles pr     on pr.id = c.user_id
left join public.runs r          on r.run_id = a.run_id
left join public.traces t        on t.message_id = a.id
left join lateral (
  select f.rating, f.reason from public.feedback f
  where f.message_id = a.id order by f.created_at desc limit 1
) fb on true
where a.role = 'assistant' and (select public.is_admin());

grant select on public.v_conversation_list, public.v_message_sources, public.v_catalog, public.v_query_logs
  to authenticated;
grant select on public.v_conversation_list, public.v_message_sources, public.v_catalog, public.v_query_logs
  to service_role;

-- UC-HIS-03: tìm cuộc trò chuyện theo từ khóa trong tiêu đề hoặc nội dung tin nhắn (pg_trgm).
create or replace function public.search_conversations(q text, lim int default 20, off int default 0)
returns setof public.v_conversation_list
language sql
stable
security invoker
set search_path = ''
as $$
  with kw as (
    select btrim(q) as q,
           '%' || replace(replace(replace(btrim(q), '\', '\\'), '%', '\%'), '_', '\_') || '%' as pat
  )
  select v.*
  from public.v_conversation_list v, kw
  where length(kw.q) > 0
    and (v.title ilike kw.pat
         or extensions.similarity(v.title, kw.q) > 0.3
         or exists (select 1 from public.messages m
                    where m.conversation_id = v.id and m.content ilike kw.pat))
  order by v.updated_at desc
  limit least(greatest(coalesce(lim, 20), 1), 100)
  offset greatest(coalesce(off, 0), 0);
$$;
revoke all on function public.search_conversations(text, int, int) from public, anon;
grant execute on function public.search_conversations(text, int, int) to authenticated, service_role;

-- UC-ADM-04: chỉ số phiên demo (runs.split = 'demo') trong khoảng thời gian; chỉ admin.
-- by_product theo traces.detected_products ('khac' khi không nhận diện được sản phẩm); by_day theo giờ Việt Nam.
create or replace function public.demo_metrics(date_from timestamptz, date_to timestamptz, config text default null)
returns jsonb
language plpgsql
stable
security invoker
set search_path = ''
as $$
declare
  result jsonb;
begin
  if not (select public.is_admin()) and coalesce(auth.role(), '') <> 'service_role' then
    raise exception 'demo_metrics: chỉ admin' using errcode = '42501';
  end if;

  with base as (
    select a.id, a.created_at, a.refused, t.latency_ms, t.detected_products,
           (select f.rating from public.feedback f where f.message_id = a.id
            order by f.created_at desc limit 1) as rating
    from public.messages a
    join public.runs r on r.run_id = a.run_id
    left join public.traces t on t.message_id = a.id
    where a.role = 'assistant' and r.split = 'demo'
      and a.created_at >= date_from and a.created_at < date_to
      and (config is null or r.config_name = config)
  ),
  prod as (
    select coalesce(pc, 'khac') as product_code, b.*
    from base b
    left join lateral unnest(b.detected_products) pc on true
  )
  select jsonb_build_object(
    'n_questions',   (select count(*) from base),
    'latency_p50',   (select percentile_cont(0.5)  within group (order by latency_ms) from base),
    'latency_p95',   (select percentile_cont(0.95) within group (order by latency_ms) from base),
    'refusal_rate',  (select avg(refused::int)::float8 from base),
    'positive_rate', (select (count(*) filter (where rating = 1))::float8 / nullif(count(rating), 0) from base),
    'by_product', coalesce((
      select jsonb_agg(jsonb_build_object('product_code', product_code, 'n', n, 'refusal_rate', rr)
                       order by n desc, product_code)
      from (select product_code, count(*) as n, avg(refused::int)::float8 as rr
            from prod group by product_code) x), '[]'::jsonb),
    'by_day', coalesce((
      select jsonb_agg(jsonb_build_object('day', day, 'n', n, 'refusal_rate', rr, 'latency_p95', p95) order by day)
      from (select (created_at at time zone 'Asia/Ho_Chi_Minh')::date as day, count(*) as n,
                   avg(refused::int)::float8 as rr,
                   percentile_cont(0.95) within group (order by latency_ms) as p95
            from base group by 1) y), '[]'::jsonb)
  ) into result;
  return result;
end;
$$;
revoke all on function public.demo_metrics(timestamptz, timestamptz, text) from public, anon;
grant execute on function public.demo_metrics(timestamptz, timestamptz, text) to authenticated, service_role;
