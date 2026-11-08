-- ĐA1 · 0006: trigger (DataDictionary › View & RPC; MethodList v2 DB-04).

-- updated_at = now() trước mỗi UPDATE.
create or replace function public.set_updated_at()
returns trigger
language plpgsql
set search_path = ''
as $$
begin
  new.updated_at := now();
  return new;
end;
$$;

create trigger profiles_updated_at      before update on public.profiles      for each row execute function public.set_updated_at();
create trigger user_settings_updated_at before update on public.user_settings for each row execute function public.set_updated_at();
create trigger conversations_updated_at before update on public.conversations for each row execute function public.set_updated_at();
create trigger app_settings_updated_at  before update on public.app_settings  for each row execute function public.set_updated_at();

-- Tin nhắn mới → đẩy cuộc trò chuyện lên đầu lịch sử (UC-HIS-01).
create or replace function public.touch_conversation()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  update public.conversations set updated_at = now() where id = new.conversation_id;
  return null;
end;
$$;
create trigger messages_touch_conversation after insert on public.messages
  for each row execute function public.touch_conversation();

-- Hồ sơ mới → cài đặt mặc định (UC-SET-01, UC-ADM-01).
create or replace function public.default_settings()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
begin
  insert into public.user_settings (user_id) values (new.id) on conflict (user_id) do nothing;
  return null;
end;
$$;
create trigger profiles_default_settings after insert on public.profiles
  for each row execute function public.default_settings();

-- Tài khoản Auth mới (admin API; sign-up đã tắt) → profiles, cùng lúc với auth.users.
-- username/display_name lấy từ user_metadata; role chỉ lấy từ app_metadata (người dùng không tự sửa được).
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer
set search_path = ''
as $$
declare
  r text := new.raw_app_meta_data ->> 'role';
begin
  insert into public.profiles (id, username, display_name, role)
  values (
    new.id,
    coalesce(nullif(new.raw_user_meta_data ->> 'username', ''), split_part(new.email, '@', 1)),
    nullif(new.raw_user_meta_data ->> 'display_name', ''),
    case when r in ('user', 'admin') then r::public.user_role else 'user' end
  )
  on conflict (id) do nothing;
  return null;
end;
$$;
create trigger on_auth_user_created after insert on auth.users
  for each row execute function public.handle_new_user();

revoke all on function public.set_updated_at(), public.touch_conversation(), public.default_settings(),
                       public.handle_new_user() from public, anon, authenticated;
