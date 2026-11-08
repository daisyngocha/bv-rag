"""Quản lý tài khoản demo qua Supabase Auth admin API (SV-16, UC-ADM-01). Chỉ admin gọi (require_admin).

Mật khẩu tạm 12 ký tự, chỉ trả một lần, không lưu ở đâu. Khóa = profiles.is_active = false + ban trên Auth
(token cũ bị Auth từ chối); mở khóa ngược lại. Không cho tự khóa mình hoặc bỏ admin hoạt động cuối cùng.
"""
from __future__ import annotations

import re
import secrets
import string

from app.supabase_rest import SupabaseError

EMAIL = re.compile(r"^[a-z0-9][a-z0-9._-]{0,40}@bv-rag\.local$")
USERNAME = re.compile(r"^[a-z0-9][a-z0-9._-]{2,31}$")
BAN = "876000h"   # ~100 năm


class Conflict(Exception):
    """409: trùng hoặc vi phạm quy tắc an toàn tài khoản."""


class NotFoundUser(Exception):
    pass


def temp_password(n: int = 12) -> str:
    alphabet = string.ascii_letters + string.digits
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(n - 1)) + secrets.choice("!@#$%&*")
        if any(c.islower() for c in pw) and any(c.isupper() for c in pw) and any(c.isdigit() for c in pw):
            return pw


class AdminUserService:
    def __init__(self, db, verifier=None):
        self.db, self.verifier = db, verifier

    def _profiles(self, **flt) -> list[dict]:
        return self.db.select("profiles", select="id,username,display_name,role,is_active,created_at", **flt)

    def _profile(self, user_id: str) -> dict:
        try:
            rows = self._profiles(id=f"eq.{user_id}")
        except SupabaseError as e:
            if e.status_code == 400:
                raise NotFoundUser(user_id)
            raise
        if not rows:
            raise NotFoundUser(user_id)
        return rows[0]

    def list_users(self) -> list[dict]:
        auth = {u["id"]: u for u in self.db.list_users()}
        out = []
        for p in sorted(self._profiles(), key=lambda p: p["username"]):
            a = auth.get(p["id"], {})
            out.append({**p, "email": a.get("email"), "banned_until": a.get("banned_until"),
                        "last_sign_in_at": a.get("last_sign_in_at")})
        return out

    def create_user(self, username: str, email: str, role: str = "user", display_name: str | None = None):
        username, email = username.strip().lower(), email.strip().lower()
        if not USERNAME.match(username):
            raise ValueError("username: 3–32 ký tự a-z, 0-9, . _ -")
        if not EMAIL.match(email):
            raise ValueError("email phải có dạng <tên>@bv-rag.local (email giả, không dùng email thật)")
        if role not in ("user", "admin"):
            raise ValueError("role phải là user hoặc admin")
        if self._profiles(username=f"eq.{username}"):
            raise Conflict(f"username {username} đã tồn tại")
        if self.db.find_user_by_email(email):
            raise Conflict(f"email {email} đã tồn tại")
        pw = temp_password()
        try:
            au = self.db.create_user(email, pw, {"username": username, "display_name": display_name}, {"role": role})
        except SupabaseError as e:
            if e.status_code in (409, 422):
                raise Conflict(str(e.body))
            raise
        # trigger handle_new_user đã tạo profiles; upsert để chắc vai trò/tên khớp
        self.db.upsert("profiles", [{"id": au["id"], "username": username, "display_name": display_name,
                                     "role": role, "is_active": True}], on_conflict="id")
        self.db.upsert("user_settings", [{"user_id": au["id"]}], on_conflict="user_id", ignore_duplicates=True)
        return {**self._profile(au["id"]), "email": email}, pw

    def _active_admins(self) -> list[str]:
        return [p["id"] for p in self._profiles(role="eq.admin", is_active="eq.true")]

    def update_user(self, user_id: str, actor_id: str, role: str | None = None, is_active: bool | None = None):
        p = self._profile(user_id)
        if role is not None and role not in ("user", "admin"):
            raise ValueError("role phải là user hoặc admin")
        if is_active is False and user_id == actor_id:
            raise Conflict("không thể tự khóa tài khoản của mình")
        losing_admin = p["role"] == "admin" and p["is_active"] and (role == "user" or is_active is False)
        if losing_admin and self._active_admins() == [user_id]:
            raise Conflict("không thể bỏ quản trị viên hoạt động cuối cùng")
        changes = {k: v for k, v in (("role", role), ("is_active", is_active)) if v is not None}
        if not changes:
            return {**p}
        attrs = {}
        if role is not None:
            attrs["app_metadata"] = {"role": role}
        if is_active is not None:
            attrs["ban_duration"] = "none" if is_active else BAN
        self.db.update_user(user_id, **attrs)
        self.db.update("profiles", changes, id=f"eq.{user_id}")
        if self.verifier is not None:
            self.verifier.forget_user(user_id)
        return self._profile(user_id)

    def reset_password(self, user_id: str) -> str:
        self._profile(user_id)
        pw = temp_password()
        self.db.update_user(user_id, password=pw)
        return pw
