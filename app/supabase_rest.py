"""Client Supabase phía server (service_role): PostgREST + Auth admin API qua httpx, không cần supabase-py.

Dùng cho scripts/sync_supabase.py, scripts/seed_demo_users.py và FastAPI (bước 2). service_role bỏ qua RLS:
chỉ dùng ở server/script, KHÔNG đưa key này vào frontend.

Biến môi trường: SUPABASE_URL (vd https://xxxx.supabase.co hoặc http://127.0.0.1:54321), SUPABASE_SERVICE_ROLE_KEY.
"""
from __future__ import annotations

import os
from typing import Any, Iterable

import httpx


class SupabaseError(RuntimeError):
    def __init__(self, resp: httpx.Response):
        self.status_code = resp.status_code
        try:
            self.body = resp.json()
        except ValueError:
            self.body = resp.text
        super().__init__(f"{resp.request.method} {resp.request.url.path} → {resp.status_code}: {self.body}")


def _check(resp: httpx.Response) -> httpx.Response:
    if resp.status_code >= 400:
        raise SupabaseError(resp)
    return resp


def eq(value: Any) -> str:
    """Bộ lọc PostgREST col=eq.value."""
    return f"eq.{value}"


class SupabaseRest:
    def __init__(self, url: str, service_key: str, client: httpx.Client | None = None, timeout: float = 60):
        if not url or not service_key:
            raise ValueError("Thiếu SUPABASE_URL hoặc SUPABASE_SERVICE_ROLE_KEY")
        headers = {"apikey": service_key, "Authorization": f"Bearer {service_key}"}
        self.http = client or httpx.Client(base_url=url.rstrip("/"), headers=headers, timeout=timeout)

    @classmethod
    def from_env(cls) -> "SupabaseRest":
        return cls(os.environ.get("SUPABASE_URL", ""), os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""))

    # ---------- PostgREST ----------
    def select(self, table: str, **params: str) -> list[dict]:
        return _check(self.http.get(f"/rest/v1/{table}", params=params)).json()

    def insert(self, table: str, rows: list[dict] | dict, returning: bool = True) -> list[dict]:
        prefer = "return=representation" if returning else "return=minimal"
        r = _check(self.http.post(f"/rest/v1/{table}", json=rows, headers={"Prefer": prefer}))
        return r.json() if returning else []

    def upsert(self, table: str, rows: Iterable[dict], on_conflict: str, returning: bool = False,
               batch: int = 500, ignore_duplicates: bool = False) -> list[dict]:
        """INSERT … ON CONFLICT (on_conflict) DO UPDATE theo lô. Các dòng trong một lô phải cùng tập khóa."""
        rows = list(rows)
        res = "ignore-duplicates" if ignore_duplicates else "merge-duplicates"
        prefer = f"resolution={res},missing=default," + ("return=representation" if returning else "return=minimal")
        out: list[dict] = []
        for i in range(0, len(rows), batch):
            r = _check(self.http.post(f"/rest/v1/{table}", params={"on_conflict": on_conflict},
                                      json=rows[i:i + batch], headers={"Prefer": prefer}))
            if returning:
                out += r.json()
        return out

    def update(self, table: str, values: dict, returning: bool = False, **filters: str) -> list[dict]:
        if not filters:
            raise ValueError("update không có bộ lọc: từ chối cập nhật cả bảng")
        prefer = "return=representation" if returning else "return=minimal"
        r = _check(self.http.patch(f"/rest/v1/{table}", params=filters, json=values, headers={"Prefer": prefer}))
        return r.json() if returning else []

    def delete(self, table: str, **filters: str) -> None:
        if not filters:
            raise ValueError("delete không có bộ lọc: từ chối xóa cả bảng")
        _check(self.http.delete(f"/rest/v1/{table}", params=filters))

    def rpc(self, fn: str, args: dict | None = None) -> Any:
        return _check(self.http.post(f"/rest/v1/rpc/{fn}", json=args or {})).json()

    # ---------- Auth admin API (GoTrue) ----------
    def list_users(self, per_page: int = 200) -> list[dict]:
        users, page = [], 1
        while True:
            r = _check(self.http.get("/auth/v1/admin/users", params={"page": page, "per_page": per_page})).json()
            batch = r.get("users", r) if isinstance(r, dict) else r
            users += batch
            if len(batch) < per_page:
                return users
            page += 1

    def find_user_by_email(self, email: str) -> dict | None:
        email = email.lower()
        return next((u for u in self.list_users() if (u.get("email") or "").lower() == email), None)

    def create_user(self, email: str, password: str, user_metadata: dict | None = None,
                    app_metadata: dict | None = None) -> dict:
        body = {"email": email, "password": password, "email_confirm": True,
                "user_metadata": user_metadata or {}, "app_metadata": app_metadata or {}}
        return _check(self.http.post("/auth/v1/admin/users", json=body)).json()

    def update_user(self, user_id: str, **attrs: Any) -> dict:
        """attrs: password, user_metadata, app_metadata, ban_duration ('876000h' để khóa, 'none' để mở)."""
        return _check(self.http.put(f"/auth/v1/admin/users/{user_id}", json=attrs)).json()
