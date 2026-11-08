"""Tạo/cập nhật tài khoản demo trên Supabase (MethodList v2 OPS-05) qua Auth admin API, bằng service_role.

  PYTHONPATH=. python scripts/seed_demo_users.py                      # tạo tài khoản còn thiếu, cập nhật vai trò
  PYTHONPATH=. python scripts/seed_demo_users.py --reset-password     # đặt lại mật khẩu mọi tài khoản trong file

Trigger on_auth_user_created tạo profiles (role lấy từ app_metadata), default_settings tạo user_settings.
Script upsert lại profiles để vai trò/tên hiển thị khớp file kể cả với tài khoản đã có.
Mật khẩu: biến môi trường password_env (.env); thiếu → sinh ngẫu nhiên, in ra một lần, không ghi file.
"""
from __future__ import annotations

import argparse
import os
import secrets
import string
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.sync_supabase import load_env  # noqa: E402

ROLES = {"user", "admin"}


def temp_password(n: int = 14) -> str:
    alphabet = string.ascii_letters + string.digits
    while True:
        pw = "".join(secrets.choice(alphabet) for _ in range(n - 2)) + secrets.choice("!@#$%") + secrets.choice(string.digits)
        if any(c.islower() for c in pw) and any(c.isupper() for c in pw):
            return pw


def load_spec(path) -> list[dict]:
    users = (yaml.safe_load(open(path, encoding="utf-8")) or {}).get("users", [])
    seen = set()
    for u in users:
        for k in ("username", "email", "role"):
            if not u.get(k):
                raise ValueError(f"thiếu {k}: {u}")
        if u["role"] not in ROLES:
            raise ValueError(f"role phải thuộc {ROLES}: {u}")
        if not u["email"].endswith("@bv-rag.local"):
            raise ValueError(f"chỉ dùng email giả @bv-rag.local: {u['email']}")
        if u["username"] in seen:
            raise ValueError(f"username trùng: {u['username']}")
        seen.add(u["username"])
    return users


def seed_users(db, spec="configs/demo_users.yaml", reset_password: bool = False) -> list[dict]:
    existing = {(u.get("email") or "").lower(): u for u in db.list_users()}
    out = []
    for u in load_spec(spec):
        meta_user = {"username": u["username"], "display_name": u.get("display_name")}
        meta_app = {"role": u["role"]}
        pw_env = u.get("password_env")
        pw = os.environ.get(pw_env) if pw_env else None
        generated = False
        cur = existing.get(u["email"].lower())
        if cur is None:
            if not pw:
                pw, generated = temp_password(), True
            cur = db.create_user(u["email"], pw, meta_user, meta_app)
            action = "created"
        else:
            attrs = {"user_metadata": meta_user, "app_metadata": meta_app}
            if reset_password:
                if not pw:
                    pw, generated = temp_password(), True
                attrs["password"] = pw
            db.update_user(cur["id"], **attrs)
            action = "updated"
        db.upsert("profiles", [{"id": cur["id"], "username": u["username"], "display_name": u.get("display_name"),
                                "role": u["role"], "is_active": True}], on_conflict="id")
        db.upsert("user_settings", [{"user_id": cur["id"]}], on_conflict="user_id", ignore_duplicates=True)
        out.append({"username": u["username"], "email": u["email"], "role": u["role"], "action": action,
                    "temp_password": pw if generated else None})
    return out


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--spec", default="configs/demo_users.yaml")
    ap.add_argument("--reset-password", action="store_true")
    a = ap.parse_args(argv)
    load_env()
    from app.supabase_rest import SupabaseRest
    for r in seed_users(SupabaseRest.from_env(), a.spec, a.reset_password):
        pw = f"  mật khẩu tạm: {r['temp_password']}" if r["temp_password"] else ""
        print(f"{r['action']:8} {r['username']:10} {r['email']:28} {r['role']}{pw}")


if __name__ == "__main__":
    main()
