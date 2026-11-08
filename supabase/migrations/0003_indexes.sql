-- ĐA1 · 0003: index (ERD trang 2 › Kiểu enum, index, migration) + index cho khóa ngoại hay join.

create index conversations_user_updated on public.conversations (user_id, updated_at desc);   -- UC-HIS-01
create index messages_conv_created      on public.messages (conversation_id, created_at);      -- UC-HIS-02
create index messages_reply_to          on public.messages (reply_to_id);
create index messages_run               on public.messages (run_id);                           -- demo_metrics, v_query_logs
create index messages_content_trgm      on public.messages using gin (content extensions.gin_trgm_ops);   -- UC-HIS-03
create index conversations_title_trgm   on public.conversations using gin (title extensions.gin_trgm_ops);  -- UC-HIS-03
create index feedback_rating            on public.feedback (rating);
create index feedback_user              on public.feedback (user_id);
create index chunks_document            on public.chunks (document_id);
create index chunks_version_product     on public.chunks (data_version, product_code);
create index documents_product          on public.documents (product_code);
create index citations_chunk            on public.message_citations (data_version, chunk_id);
create index retrieval_logs_chunk       on public.retrieval_logs (data_version, chunk_id);
create index runs_config_split          on public.runs (config_name, split);
