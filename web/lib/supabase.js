// OPS-07: client supabase-js dùng chung. Chỉ anon key (công khai được); mọi quyền nằm ở RLS.
// Biến môi trường Vite (web/.env.local hoặc .env.local ở gốc repo): VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY.
import { createClient } from "@supabase/supabase-js";

const url = import.meta.env.VITE_SUPABASE_URL;
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

export const configError = !url || !anonKey
  ? "Thiếu VITE_SUPABASE_URL hoặc VITE_SUPABASE_ANON_KEY (xem .env.example)."
  : null;

export const supabase = configError
  ? null
  : createClient(url, anonKey, { auth: { persistSession: true, autoRefreshToken: true } });
