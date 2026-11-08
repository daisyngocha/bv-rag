-- ĐA1 · 0002: bảng nhóm A–D theo 5.DA1_DataDictionary.xlsx (đủ ưu tiên Bắt buộc / Nên có / Tùy chọn).
-- Thứ tự tạo theo phụ thuộc khóa ngoại: C (kho tri thức) và D (vận hành) trước B (hội thoại).

-- ============ A. Tài khoản ============
create table public.profiles (
  id           uuid primary key references auth.users (id) on delete cascade,      -- PROF-01
  username     text not null unique,                                               -- PROF-02
  display_name text,                                                               -- PROF-03
  role         public.user_role not null default 'user',                           -- PROF-04
  is_active    boolean not null default true,                                      -- PROF-05
  created_at   timestamptz not null default now(),                                 -- PROF-06
  updated_at   timestamptz not null default now()                                  -- PROF-07
);

create table public.user_settings (
  user_id          uuid primary key references public.profiles (id) on delete cascade,   -- USET-01
  theme            public.theme_mode not null default 'system',                          -- USET-02
  font_size        smallint not null default 14 check (font_size between 12 and 20),     -- USET-03
  citation_style   public.citation_style not null default 'inline',                      -- USET-04
  show_source_text boolean not null default true,                                        -- USET-05
  updated_at       timestamptz not null default now(),                                   -- USET-06
  language         public.ui_language not null default 'vi',                             -- USET-07
  show_processing  boolean not null default false                                        -- USET-08 (chỉ có tác dụng với admin)
);

-- ============ C. Kho tri thức (bản sao đồng bộ một chiều từ file) ============
create table public.data_versions (
  version    text primary key,                          -- DV-01
  is_active  boolean not null default false,            -- DV-02
  n_chunks   integer check (n_chunks >= 0),             -- DV-03
  note       text,                                      -- DV-04
  created_at timestamptz not null default now()         -- DV-05
);
-- Chỉ 1 phiên bản active.
create unique index data_versions_one_active on public.data_versions (is_active) where is_active;

create table public.products (
  product_code text primary key,                        -- PRD-01
  product_name text not null,                           -- PRD-02
  company      text not null,                           -- PRD-03
  line         text not null,                           -- PRD-04 nhóm nghiệp vụ
  is_active    boolean not null default true            -- PRD-05
);

create table public.documents (
  id             bigint generated always as identity primary key,               -- DOC-01
  product_code   text not null references public.products (product_code),       -- DOC-02
  doc_type       public.doc_type not null,                                      -- DOC-03
  source_file    text not null unique,                                          -- DOC-04 tên file ASCII
  url            text not null,                                                 -- DOC-05
  effective_date date,                                                          -- DOC-06
  downloaded_at  date not null                                                  -- DOC-07
);

create table public.chunks (
  data_version   text not null references public.data_versions (version),       -- CHK-01
  chunk_id       text not null,                                                 -- CHK-02
  document_id    bigint not null references public.documents (id),              -- CHK-03
  product_code   text not null references public.products (product_code),       -- CHK-04
  doc_type       public.doc_type not null,                                      -- CHK-05
  section_path   text,                                                          -- CHK-06
  page           integer,                                                       -- CHK-07
  is_table       boolean not null default false,                                -- CHK-08
  effective_date date,                                                          -- CHK-09
  text           text not null,                                                 -- CHK-10 bắt đầu bằng context header
  primary key (data_version, chunk_id)
);

create table public.sample_questions (
  qid            text primary key,                                                            -- SQ-01
  question       text not null,                                                               -- SQ-02
  question_group text not null check (question_group in ('lookup', 'table', 'compare', 'scenario')),  -- SQ-03
  products       text[],                                                                      -- SQ-04
  is_active      boolean not null default true                                                -- SQ-05
);

-- ============ D. Vận hành và thực nghiệm ============
create table public.pipeline_configs (
  name        text primary key,                         -- CFG-01
  description text,                                     -- CFG-02
  params      jsonb not null,                           -- CFG-03 nội dung YAML
  synced_at   timestamptz not null default now()        -- CFG-04
);

create table public.runs (
  run_id         text primary key,                                                  -- RUN-01
  config_name    text not null references public.pipeline_configs (name),            -- RUN-02
  benchmark      text,                                                              -- RUN-03 null khi demo
  data_version   text not null references public.data_versions (version),          -- RUN-04
  split          text not null check (split in ('demo', 'dev', 'test')),            -- RUN-05
  runtime        text not null check (runtime in ('colab', 'wsl')),                 -- RUN-06
  gpu            text,                                                              -- RUN-07
  ollama_version text,                                                              -- RUN-08
  model_digest   text,                                                              -- RUN-09
  packages       jsonb,                                                             -- RUN-10
  repo_commit    text,                                                              -- RUN-11
  llm_gpu_pct    real,                                                              -- RUN-12
  n              integer,                                                           -- RUN-13 null khi demo
  started_at     timestamptz not null,                                              -- RUN-14
  finished_at    timestamptz,                                                       -- RUN-15
  check (split <> 'demo' or benchmark is null)
);

create table public.eval_results (
  run_id         text not null references public.runs (run_id) on delete cascade,   -- EVR-01
  question_group text not null,                                                      -- EVR-02 nhóm câu hoặc 'all'
  metric         text not null,                                                      -- EVR-03
  value          numeric not null,                                                   -- EVR-04
  primary key (run_id, question_group, metric)
);

create table public.app_settings (
  key        text primary key,                                                -- APS-01
  value      jsonb not null,                                                  -- APS-02
  updated_by uuid references public.profiles (id) on delete set null,         -- APS-03
  updated_at timestamptz not null default now()                               -- APS-04
);

-- ============ B. Hội thoại ============
create table public.conversations (
  id              uuid primary key default gen_random_uuid(),                       -- CONV-01
  user_id         uuid not null references public.profiles (id) on delete cascade,  -- CONV-02
  title           text not null check (length(btrim(title)) > 0),                   -- CONV-03
  title_is_custom boolean not null default false,                                   -- CONV-04
  created_at      timestamptz not null default now(),                               -- CONV-05
  updated_at      timestamptz not null default now()                                -- CONV-06
);

create table public.messages (
  id              uuid primary key default gen_random_uuid(),                             -- MSG-01
  conversation_id uuid not null references public.conversations (id) on delete cascade,   -- MSG-02
  reply_to_id     uuid references public.messages (id) on delete cascade,                 -- MSG-03
  role            public.msg_role not null,                                               -- MSG-04
  content         text not null,                                                          -- MSG-05 đã che CCCD/SĐT/email
  pii_masked      boolean not null default false,                                         -- MSG-06
  product_filter  text[],                                                                 -- MSG-07
  refused         boolean not null default false,                                         -- MSG-08
  refusal_reason  text check (refusal_reason in ('khong_du_can_cu', 'ngoai_pham_vi')),    -- MSG-09
  run_id          text references public.runs (run_id),                                   -- MSG-10
  created_at      timestamptz not null default now(),                                     -- MSG-11
  -- câu hỏi: không trả lời cho tin nào; câu trả lời: phải có câu hỏi và run_id
  constraint messages_user_no_reply   check (role <> 'user' or reply_to_id is null),
  constraint messages_assistant_links check (role <> 'assistant' or (reply_to_id is not null and run_id is not null)),
  constraint messages_refusal_reason  check (refused or refusal_reason is null)
);

create table public.message_citations (
  message_id   uuid not null references public.messages (id) on delete cascade,   -- CIT-01
  ord          smallint not null check (ord >= 1),                                 -- CIT-02 [n]
  data_version text not null,                                                      -- CIT-03
  chunk_id     text not null,                                                      -- CIT-04
  primary key (message_id, ord),
  foreign key (data_version, chunk_id) references public.chunks (data_version, chunk_id)
);

create table public.traces (
  message_id        uuid primary key references public.messages (id) on delete cascade,              -- TRC-01
  query_processed   text,                                                                           -- TRC-02
  detected_products text[],                                                                         -- TRC-03
  retrieval_mode    text not null check (retrieval_mode in ('none', 'dense', 'sparse', 'hybrid')),  -- TRC-04
  latency_ms        integer not null check (latency_ms >= 0),                                       -- TRC-05
  tokens_in         integer,                                                                        -- TRC-06
  tokens_out        integer,                                                                        -- TRC-07
  cost_usd          numeric(10, 6),                                                                 -- TRC-08
  timings_ms        jsonb,                                                                          -- TRC-09
  error             text                                                                            -- TRC-10
);

create table public.retrieval_logs (
  message_id   uuid not null references public.messages (id) on delete cascade,   -- RET-01
  rank         smallint not null check (rank >= 1),                                -- RET-02
  data_version text not null,                                                      -- RET-03
  chunk_id     text not null,                                                      -- RET-04
  score        real not null,                                                      -- RET-05
  rerank       real,                                                               -- RET-06
  in_context   boolean not null default false,                                     -- RET-07
  primary key (message_id, rank),
  foreign key (data_version, chunk_id) references public.chunks (data_version, chunk_id)
);

create table public.feedback (
  id         uuid primary key default gen_random_uuid(),                            -- FB-01
  message_id uuid not null references public.messages (id) on delete cascade,       -- FB-02
  user_id    uuid not null references public.profiles (id) on delete cascade,       -- FB-03
  rating     smallint not null check (rating in (1, -1)),                           -- FB-04
  reason     public.feedback_reason,                                                -- FB-05
  comment    text,                                                                  -- FB-06
  created_at timestamptz not null default now(),                                    -- FB-07
  unique (message_id, user_id),
  constraint feedback_reason_required check (rating = 1 or reason is not null)
);

comment on table public.messages is 'Snapshot hỏi đáp; INSERT chỉ FastAPI (service_role). Người dùng chỉ đọc.';
comment on table public.chunks is 'Bản sao processed/{ver}/chunks.jsonl để hiển thị trích dẫn; vector ở Qdrant.';
