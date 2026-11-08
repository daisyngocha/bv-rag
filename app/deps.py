"""Xác thực và phân quyền cho FastAPI (SV-01…SV-03, UC-AUTH-03).

Token: access_token Supabase (JWT) của người dùng, gửi ở header Authorization: Bearer <token>.
Xác minh bằng chính Supabase Auth (GET /auth/v1/user): chạy với cả khóa ký JWT kiểu cũ (HS256) lẫn khóa bất đối xứng
mới, không cần giữ JWT secret ở Colab. Kết quả cache ngắn (mặc định 60 s) theo token để không gọi Auth mỗi câu hỏi;
khóa tài khoản có hiệu lực chậm nhất sau TTL này (Auth từ chối token của người bị ban ngay khi hết cache).
Profile (vai trò, trạng thái) đọc bằng service_role; is_active = false → 403.
"""
from __future__ import annotations

import hashlib
import os
import threading
import time
from dataclasses import dataclass

import httpx
from fastapi import Depends, HTTPException, Request


@dataclass(frozen=True)
class CurrentUser:
    id: str
    email: str | None
    username: str
    display_name: str | None
    role: str
    is_active: bool

    @property
    def is_admin(self) -> bool:
        return self.role == "admin" and self.is_active


class AuthVerifier:
    def __init__(self, url: str, anon_key: str, db, ttl: float = 60, client: httpx.Client | None = None):
        if not url or not anon_key:
            raise ValueError("Thiếu SUPABASE_URL hoặc SUPABASE_ANON_KEY")
        self.http = client or httpx.Client(base_url=url.rstrip("/"), headers={"apikey": anon_key}, timeout=15)
        self.db, self.ttl = db, ttl
        self._cache: dict[str, tuple[float, CurrentUser]] = {}
        self._lock = threading.Lock()

    @classmethod
    def from_env(cls, db) -> "AuthVerifier":
        return cls(os.environ.get("SUPABASE_URL", ""), os.environ.get("SUPABASE_ANON_KEY", ""), db,
                   ttl=float(os.environ.get("AUTH_CACHE_TTL", "60")))

    def verify(self, token: str) -> CurrentUser:
        key = hashlib.sha256(token.encode()).hexdigest()
        now = time.monotonic()
        with self._lock:
            hit = self._cache.get(key)
            if hit and hit[0] > now:
                return hit[1]
        r = self.http.get("/auth/v1/user", headers={"Authorization": f"Bearer {token}"})
        if r.status_code in (401, 403):
            raise HTTPException(401, "Phiên đăng nhập không hợp lệ hoặc đã hết hạn")
        if r.status_code >= 400:
            raise HTTPException(503, f"Không xác thực được với Supabase Auth ({r.status_code})")
        au = r.json()
        rows = self.db.select("profiles", id=f"eq.{au['id']}",
                              select="id,username,display_name,role,is_active")
        if not rows:
            raise HTTPException(403, "Tài khoản chưa có hồ sơ (profiles)")
        p = rows[0]
        user = CurrentUser(id=p["id"], email=au.get("email"), username=p["username"],
                           display_name=p.get("display_name"), role=p["role"], is_active=p["is_active"])
        with self._lock:
            if len(self._cache) > 1000:
                self._cache = {k: v for k, v in self._cache.items() if v[0] > now}
            self._cache[key] = (now + self.ttl, user)
        return user

    def forget_user(self, user_id: str) -> None:
        """Xóa cache của một người dùng (khi admin khóa/đổi vai trò) để có hiệu lực ngay."""
        with self._lock:
            self._cache = {k: v for k, v in self._cache.items() if v[1].id != user_id}


def bearer_token(request: Request) -> str | None:
    h = request.headers.get("authorization", "")
    return h[7:].strip() if h.lower().startswith("bearer ") else None


def get_current_user(request: Request) -> CurrentUser:
    verifier: AuthVerifier | None = request.app.state.verifier
    if verifier is None:
        raise HTTPException(503, "Chưa cấu hình Supabase (SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY)")
    token = bearer_token(request)
    if not token:
        raise HTTPException(401, "Thiếu Authorization: Bearer <access_token>")
    user = verifier.verify(token)
    if not user.is_active:
        raise HTTPException(403, "Tài khoản đã bị khóa")
    return user


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if not user.is_admin:
        raise HTTPException(403, "Chỉ quản trị viên")
    return user


def get_supabase_admin(request: Request):
    db = request.app.state.db
    if db is None:
        raise HTTPException(503, "Chưa cấu hình Supabase service_role")
    return db
