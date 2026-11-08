"""Áp supabase/migrations lên Postgres thuần (stub auth) rồi chạy tests/db/rls_check.sql.

Chỉ chạy khi có BV_TEST_PG = chuỗi kết nối tới một Postgres ≥ 15 có pg_trgm, quyền tạo database, vd
  BV_TEST_PG="host=/var/run/postgresql port=5432 user=postgres" PYTHONPATH=. pytest tests/test_supabase_db.py
Với Supabase local (supabase start) dùng thẳng: supabase db reset && psql "$DB_URL" -f tests/db/rls_check.sql
"""
import os
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

DSN = os.environ.get("BV_TEST_PG")
pytestmark = pytest.mark.skipif(not DSN or not shutil.which("psql"), reason="cần BV_TEST_PG và psql")


def psql(dsn, *args, check=True):
    return subprocess.run(["psql", dsn, "-v", "ON_ERROR_STOP=1", "-q", *args], capture_output=True, text=True,
                          check=check)


@pytest.fixture
def db():
    name = f"bvtest_{uuid.uuid4().hex[:8]}"
    psql(DSN, "-c", f"create database {name}")
    dsn = f"{DSN} dbname={name}"
    try:
        yield dsn
    finally:
        psql(DSN, "-c", f"drop database {name} with (force)", check=False)


def test_migrations_and_rls(db):
    psql(db, "-f", "tests/db/auth_stub.sql")
    for f in sorted(Path("supabase/migrations").glob("*.sql")):
        r = psql(db, "-f", str(f), check=False)
        assert r.returncode == 0, f"{f.name}: {r.stderr}"
    r = psql(db, "-f", "tests/db/rls_check.sql", check=False)
    assert r.returncode == 0 and "RLS CHECK OK" in r.stdout, r.stderr
