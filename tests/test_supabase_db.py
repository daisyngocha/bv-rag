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


# ---------------------------------------------------------------------------------------------------------------
# Tích hợp: ChatService ghi đúng schema thật (cột, kiểu mảng/jsonb, CHECK, FK) và RLS cho người dùng đọc lại được.
# PsqlDB thay PostgREST: cùng giao diện select/insert/upsert/update của SupabaseRest, chạy SQL bằng role service_role.
class PsqlDB:
    def __init__(self, dsn):
        self.dsn = dsn

    def _sql(self, sql, *params):
        import json as _json
        args = [f"-v", "ON_ERROR_STOP=1", "-Atq"]
        for i, p in enumerate(params):
            args += ["-v", f"p{i}={_json.dumps(p, ensure_ascii=False, default=str)}"]
        r = subprocess.run(["psql", self.dsn, *args], input=f"set role service_role;\n{sql}\n",
                           capture_output=True, text=True)
        if r.returncode:
            raise RuntimeError(r.stderr)
        return [_json.loads(l) for l in r.stdout.splitlines() if l.strip()]

    @staticmethod
    def _where(flt):
        conds = []
        for k, v in flt.items():
            if k == "select":
                continue
            op, _, val = v.partition(".")
            conds.append(f"{k}::text {'=' if op == 'eq' else '<>'} '{val}'")
        return " where " + " and ".join(conds) if conds else ""

    def select(self, table, **flt):
        return self._sql(f"select row_to_json(t) from public.{table} t{self._where(flt)};")

    def _ins(self, table, rows, conflict=""):
        rows = rows if isinstance(rows, list) else [rows]
        cols = ", ".join(rows[0].keys())
        return self._sql(f"insert into public.{table} ({cols}) select {cols} from "
                         f"json_populate_recordset(null::public.{table}, :'p0'::json) {conflict} "
                         f"returning row_to_json({table}.*);", rows)

    def insert(self, table, rows, returning=True):
        out = self._ins(table, rows)
        return out if returning else []

    def upsert(self, table, rows, on_conflict, returning=False, batch=500, ignore_duplicates=False):
        rows = list(rows)
        sets = ", ".join(f"{c} = excluded.{c}" for c in rows[0] if c not in on_conflict.split(","))
        act = "do nothing" if ignore_duplicates or not sets else f"do update set {sets}"
        out = self._ins(table, rows, f"on conflict ({on_conflict}) {act}")
        return out if returning else []

    def update(self, table, values, returning=False, **flt):
        sets = ", ".join(f"{c} = r.{c}" for c in values)
        self._sql(f"update public.{table} t set {sets} from json_populate_record(null::public.{table}, "
                  f":'p0'::json) r{self._where(flt).replace(' where ', ' where t.', 1).replace(' and ', ' and t.')};",
                  values)
        return []


SEED = """
insert into auth.users (id, email, raw_user_meta_data) values
  ('00000000-0000-0000-0000-0000000000b1', 'demo01@bv-rag.local', '{"username":"demo01"}');
insert into public.data_versions (version, is_active) values ('v1', true);
insert into public.products values ('BVP','Bảo Việt An Gia','BHBV','suc_khoe',true), ('BTB','Bảo Việt Tâm Bình','BHBV','phi_nhan_tho',true);
insert into public.documents (product_code, doc_type, source_file, url, downloaded_at) values
  ('BVP','quy_tac','qt_bvp.pdf','https://x/bvp','2026-10-25'), ('BTB','quy_tac','qt_btb.pdf','https://x/btb','2026-10-25');
insert into public.chunks (data_version, chunk_id, document_id, product_code, doc_type, text)
  select 'v1', c, d.id, split_part(c,'_',1), 'quy_tac', '[h]' || chr(10) || c
  from unnest(array['BVP_A','BVP_B','BVP_C','BTB_A','BTB_B','BTB_C']) c
  join public.documents d on d.product_code = split_part(c,'_',1);
insert into public.pipeline_configs (name, params) values ('B4', '{}');
"""


def test_chat_service_writes_real_schema(db, tmp_path):
    from app.deps import CurrentUser
    from app.runlog import RunLogger
    from app.service import ChatService
    from tests.test_api_chat import CATALOG, pipe

    psql(db, "-f", "tests/db/auth_stub.sql")
    for f in sorted(Path("supabase/migrations").glob("*.sql")):
        psql(db, "-f", str(f))
    psql(db, "-c", SEED)
    store = PsqlDB(db)
    svc = ChatService(pipe(), CATALOG, "B4", db=store, runlog=RunLogger(tmp_path))
    svc.start_session()
    user = CurrentUser("00000000-0000-0000-0000-0000000000b1", "demo01@bv-rag.local", "demo01", None, "user", True)
    out = svc.ask_for_user(user, "thời gian chờ BVP, sđt 0912345678")
    assert out["saved"], out["db_error"]
    out2 = svc.ask_for_user(user, "còn BTB", conversation_id=out["conversation_id"], product_filter=["BTB"])
    assert out2["saved"] and out2["conversation_id"] == out["conversation_id"], out2["db_error"]
    svc.close_session()

    claims = '{"sub":"00000000-0000-0000-0000-0000000000b1","role":"authenticated"}'
    r = psql(db, "-Atc", f"set role authenticated; select set_config('request.jwt.claims', '{claims}', false);"
                         "select n_messages || '|' || preview from v_conversation_list;"
                         "select count(*) from v_message_sources;"
                         "select string_agg(product_filter::text, ',') from messages where role = 'user';")
    lines = r.stdout.split("\n")
    assert lines[1] == "4|thời gian chờ BVP, sđt [SĐT]" and lines[2] == "4" and lines[3] == "{BTB}"
    r = psql(db, "-Atc", "select count(*) || '|' || bool_and(finished_at is not null) from runs where split = 'demo';"
                         "select count(*) from retrieval_logs; select count(*) from traces;")
    assert r.stdout.split("\n")[:3] == ["1|true", "6", "2"]
