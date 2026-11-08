"""Bước 2 FastAPI: /chat/ask(+stream), /admin/*, xác thực, ghi Supabase. Không cần GPU/mạng: pipeline giả
(tests/test_b4), Supabase giả trong bộ nhớ, verifier giả. Chạy: PYTHONPATH=. python -m pytest -q tests/test_api_chat.py"""
import json
import uuid

import pytest

pytest.importorskip("fastapi")
from fastapi import HTTPException  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.api import create_app  # noqa: E402
from app.deps import CurrentUser  # noqa: E402
from app.privacy import mask_pii  # noqa: E402
from app.runlog import RunLogger  # noqa: E402
from app.service import ChatService, classify_refusal, make_title  # noqa: E402
from app.supabase_rest import SupabaseError  # noqa: E402
from src.pipeline import RAGPipeline  # noqa: E402
from tests.test_b4 import LLM, QP, Rer, cfg  # noqa: E402
from tests.test_demo import CATALOG, RetrMeta  # noqa: E402

ADMIN = CurrentUser("a-1", "admin01@bv-rag.local", "admin01", "Quản trị", "admin", True)
USER = CurrentUser("u-1", "demo01@bv-rag.local", "demo01", "Demo 01", "user", True)
OTHER = CurrentUser("u-2", "demo02@bv-rag.local", "demo02", None, "user", True)
LOCKED = CurrentUser("u-3", "demo03@bv-rag.local", "demo03", None, "user", False)
TOKENS = {"t-admin": ADMIN, "t-user": USER, "t-other": OTHER, "t-locked": LOCKED}


# ------------------------------------------------------------------ Supabase giả
class Resp:
    def __init__(self, status):
        self.status_code = status
        self.request = type("R", (), {"method": "X", "url": type("U", (), {"path": "/x"})()})()

    def json(self):
        return {"msg": "fake"}


def match(row, flt):
    for k, v in flt.items():
        if k in ("select", "order", "limit"):
            continue
        op, _, val = v.partition(".")
        cur = row.get(k)
        cur_s = str(cur).lower() if isinstance(cur, bool) else str(cur)
        if op == "eq" and cur_s != val:
            return False
        if op == "neq" and cur_s == val:
            return False
    return True


class FakeDB:
    KEYS = {"conversations": "id", "messages": "id", "profiles": "id", "runs": "run_id", "app_settings": "key",
            "pipeline_configs": "name", "user_settings": "user_id", "data_versions": "version"}

    def __init__(self):
        self.t = {k: [] for k in ("conversations", "messages", "message_citations", "traces", "retrieval_logs",
                                  "runs", "app_settings", "pipeline_configs", "profiles", "user_settings",
                                  "data_versions")}
        self.t["pipeline_configs"] = [{"name": "B4"}, {"name": "B3"}]
        self.t["data_versions"] = [{"version": "v1", "is_active": True, "n_chunks": 6}]
        self.t["profiles"] = [{"id": u.id, "username": u.username, "display_name": u.display_name, "role": u.role,
                               "is_active": u.is_active, "created_at": "2026-11-08"} for u in TOKENS.values()]
        self.auth = [{"id": u.id, "email": u.email, "banned_until": None, "last_sign_in_at": None}
                     for u in TOKENS.values()]
        self.fail_on = None
        self.auth_calls = []

    def _fail(self, table):
        if self.fail_on == table:
            raise SupabaseError(Resp(500))

    def select(self, table, **params):
        self._fail(table)
        if "id" in params and table in ("conversations", "profiles"):
            try:
                uuid.UUID(params["id"][3:]) if table == "conversations" else None
            except ValueError:
                raise SupabaseError(Resp(400))
        return [dict(r) for r in self.t[table] if match(r, params)]

    def insert(self, table, rows, returning=True):
        self._fail(table)
        rows = rows if isinstance(rows, list) else [rows]
        out = []
        for r in rows:
            r = dict(r)
            if table in ("conversations", "messages"):
                r.setdefault("id", str(uuid.uuid4()))
            self.t[table].append(r)
            out.append(dict(r))
        return out if returning else []

    def upsert(self, table, rows, on_conflict, returning=False, batch=500, ignore_duplicates=False):
        self._fail(table)
        key = self.KEYS[table]
        for r in rows:
            cur = next((x for x in self.t[table] if x[key] == r[key]), None)
            if cur is None:
                self.t[table].append(dict(r))
            elif not ignore_duplicates:
                cur.update(r)
        return []

    def update(self, table, values, returning=False, **flt):
        self._fail(table)
        for r in self.t[table]:
            if match(r, flt):
                r.update(values)
        return []

    def list_users(self):
        return [dict(u) for u in self.auth]

    def find_user_by_email(self, email):
        return next((u for u in self.auth if u["email"] == email), None)

    def create_user(self, email, password, user_metadata=None, app_metadata=None):
        u = {"id": str(uuid.uuid4()), "email": email, "banned_until": None, "last_sign_in_at": None}
        self.auth.append(u)
        self.auth_calls.append(("create", email, password, app_metadata))
        self.t["profiles"].append({"id": u["id"], "username": user_metadata["username"], "role": "user",
                                   "display_name": None, "is_active": True, "created_at": "now"})
        return u

    def update_user(self, user_id, **attrs):
        self.auth_calls.append(("update", user_id, attrs))
        return {"id": user_id}


class FakeVerifier:
    def __init__(self):
        self.forgot = []

    def verify(self, token):
        if token not in TOKENS:
            raise HTTPException(401, "token sai")
        return TOKENS[token]

    def forget_user(self, uid):
        self.forgot.append(uid)


class StreamLLM(LLM):
    def generate_stream(self, prompt):
        self.prompts.append(prompt)
        parts = ["Thời gian chờ ", "30 ngày [1]."]
        yield from parts
        from src.generate.llm_client import LLMResult
        self.last_result = LLMResult("".join(parts), 100, 10, 50, None, None)


def pipe(min_score=None, text="Thời gian chờ 30 ngày [1]. Bảng [2], [7].", llm=None, name="B4"):
    c = cfg(min_score=min_score, use_filter=True) | {"name": name}
    return RAGPipeline(c, llm or LLM(text), RetrMeta(), qp=QP(), reranker=Rer())


def make(tmp_path, db=None, verifier=None, **kw):
    db = FakeDB() if db is None else db
    svc = ChatService(pipe(**kw), CATALOG, "B4", db=db or None, runlog=RunLogger(tmp_path),
                      builder={"B3": pipe(name="B3", text="B3 trả lời [1].")})
    app = create_app(svc, db=db or None, verifier=FakeVerifier() if verifier is None else verifier)
    return svc, db, app


H = {"Authorization": "Bearer t-user"}
HA = {"Authorization": "Bearer t-admin"}


# ------------------------------------------------------------------ hỏi đáp
def test_chat_ask_creates_conversation_and_persists(tmp_path):
    svc, db, app = make(tmp_path)
    with TestClient(app) as c:
        r = c.post("/chat/ask", headers=H, json={"question": "thời gian chờ BVP? gọi 0912345678",
                                                 "product_filter": None})
        assert r.status_code == 200, r.text
        out = r.json()
    assert out["saved"] and out["db_error"] is None and out["pii_masked"]
    assert out["run_id"] == svc.run_id and out["run_id"].startswith("B4_demo_")
    assert [s["chunk_id"] for s in out["sources"]] == ["BVP_A", "BVP_B"]          # chỉ đoạn được trích dẫn
    s1 = out["sources"][0]
    assert s1["ord"] == 1 and s1["product_name"] == "Bảo Việt An Gia" and s1["text"] == "thời gian chờ 30 ngày"
    conv = db.t["conversations"][0]
    assert conv["user_id"] == USER.id and conv["id"] == out["conversation_id"] and "[SĐT]" in conv["title"]
    q, a = db.t["messages"]
    assert q["role"] == "user" and "0912345678" not in q["content"] and q["pii_masked"]
    assert a["reply_to_id"] == q["id"] == out["question_id"] and a["id"] == out["message_id"]
    assert a["run_id"] == svc.run_id and a["refused"] is False and a["refusal_reason"] is None
    assert [(x["ord"], x["chunk_id"]) for x in db.t["message_citations"]] == [(1, "BVP_A"), (2, "BVP_B")]
    tr = db.t["traces"][0]
    assert tr["message_id"] == a["id"] and tr["retrieval_mode"] == "hybrid" and tr["detected_products"] == ["BVP"]
    logs = db.t["retrieval_logs"]
    assert {x["chunk_id"] for x in logs if x["in_context"]} == {"BVP_A", "BVP_B"}
    assert all(x["rerank"] is not None for x in logs)
    assert db.t["runs"][0]["split"] == "demo" and db.t["runs"][0]["finished_at"]   # đóng khi tắt app
    rec = json.loads((tmp_path / svc.run_id / "log.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert rec["kind"] == "chat" and rec["message_id"] == a["id"] and "0912345678" not in rec["question"]


def test_chat_ask_continue_and_ownership(tmp_path):
    _, db, app = make(tmp_path)
    with TestClient(app) as c:
        cid = c.post("/chat/ask", headers=H, json={"question": "thời gian chờ BVP"}).json()["conversation_id"]
        r = c.post("/chat/ask", headers=H, json={"question": "còn BTB thì sao", "conversation_id": cid})
        assert r.status_code == 200 and r.json()["conversation_id"] == cid
        assert len(db.t["conversations"]) == 1 and len(db.t["messages"]) == 4
        other = {"Authorization": "Bearer t-other"}
        assert c.post("/chat/ask", headers=other, json={"question": "xem trộm", "conversation_id": cid}).status_code == 404
        assert c.post("/chat/ask", headers=H, json={"question": "abc", "conversation_id": "khong-phai-uuid"}).status_code == 404


def test_auth_errors(tmp_path):
    _, _, app = make(tmp_path)
    with TestClient(app) as c:
        assert c.post("/chat/ask", json={"question": "thời gian chờ"}).status_code == 401
        assert c.post("/chat/ask", headers={"Authorization": "Bearer sai"}, json={"question": "abc"}).status_code == 401
        assert c.post("/chat/ask", headers={"Authorization": "Bearer t-locked"},
                      json={"question": "abc"}).status_code == 403
        assert c.get("/admin/health", headers=H).status_code == 403
        assert c.post("/chat/ask", headers=H, json={"question": "ab"}).status_code == 422
    _, _, app = make(tmp_path, db=False, verifier=False)        # chưa cấu hình Supabase
    app.state.verifier = None
    with TestClient(app) as c:
        assert c.post("/chat/ask", headers=H, json={"question": "thời gian chờ"}).status_code == 503
        assert c.post("/ask", json={"question": "thời gian chờ BVP"}).status_code == 200


def test_product_filter(tmp_path):
    _, db, app = make(tmp_path)
    with TestClient(app) as c:
        assert c.post("/chat/ask", headers=H, json={"question": "thời gian chờ", "product_filter": ["XXX"]}).status_code == 422
        r = c.post("/chat/ask", headers=H, json={"question": "thời gian chờ", "product_filter": ["BTB"]}).json()
    assert r["product_filter"] == ["BTB"] and all(s["product_code"] == "BTB" for s in r["sources"])
    assert db.t["messages"][0]["product_filter"] == ["BTB"]


def test_refusal_reasons(tmp_path):
    _, db, app = make(tmp_path, min_score=0.5)
    with TestClient(app) as c:
        r = c.post("/chat/ask", headers=H, json={"question": "câu ngoài phạm vi BVP"}).json()
    assert r["refused"] and r["gated"] and r["refusal_reason"] == "khong_du_can_cu" and r["sources"] == []
    assert db.t["messages"][1]["refusal_reason"] == "khong_du_can_cu" and db.t["message_citations"] == []
    from src.generate.prompts import REFUSAL
    assert classify_refusal({"refused": True, "qp": {"products": []}}) == "ngoai_pham_vi"
    assert classify_refusal({"refused": True, "qp": {"products": [], "user_filter": ["BVP"]}}) == "khong_du_can_cu"
    assert classify_refusal({"refused": True}) == "khong_du_can_cu"
    _, _, app = make(tmp_path, text=REFUSAL)
    with TestClient(app) as c:
        r = c.post("/chat/ask", headers=H, json={"question": "bảo hiểm xe ô tô"}).json()
    assert r["refused"] and r["refusal_reason"] == "ngoai_pham_vi"


def test_db_error_still_answers(tmp_path):
    svc, db, app = make(tmp_path)
    with TestClient(app) as c:
        db.fail_on = "messages"
        r = c.post("/chat/ask", headers=H, json={"question": "thời gian chờ BVP"})
    assert r.status_code == 200 and not r.json()["saved"] and r.json()["db_error"]
    assert r.json()["answer"].startswith("Thời gian chờ")
    assert (tmp_path / svc.run_id / "log.jsonl").exists()


def test_stream(tmp_path):
    _, db, app = make(tmp_path, llm=StreamLLM())
    with TestClient(app) as c:
        r = c.post("/chat/ask/stream", headers=H, json={"question": "thời gian chờ BVP"})
        assert r.status_code == 200 and r.headers["content-type"].startswith("text/event-stream")
        events = [(b.split("\n")[0][7:], json.loads(b.split("\n")[1][6:])) for b in r.text.strip().split("\n\n")]
        assert c.post("/chat/ask/stream", headers=H,
                      json={"question": "abc", "conversation_id": str(uuid.uuid4())}).status_code == 404
    kinds = [e for e, _ in events]
    assert kinds[0] == "status" and kinds[-1] == "done" and kinds.count("token") == 2
    done = events[-1][1]
    assert done["answer"] == "Thời gian chờ 30 ngày [1]." and done["saved"] and done["sources"][0]["chunk_id"] == "BVP_A"
    assert len(db.t["messages"]) == 2 and db.t["traces"][0]["tokens_out"] == 10


def test_stream_gated_no_tokens(tmp_path):
    _, _, app = make(tmp_path, min_score=0.5, llm=StreamLLM())
    with TestClient(app) as c:
        r = c.post("/chat/ask/stream", headers=H, json={"question": "câu ngoài phạm vi"})
    assert "event: token" not in r.text and "event: done" in r.text


# ------------------------------------------------------------------ quản trị
def test_switch_config_and_compare(tmp_path):
    svc, db, app = make(tmp_path)
    with TestClient(app) as c:
        old = svc.run_id
        assert c.put("/admin/configs/active", headers=HA, json={"config": "B9"}).status_code == 404
        r = c.put("/admin/configs/active", headers=HA, json={"config": "B3"})
        assert r.status_code == 200, r.text
        assert r.json()["config"] == "B3" and svc.config_name == "B3" and r.json()["run_id"].startswith("B3_demo_")
        assert db.t["app_settings"][0]["value"] == {"config": "B3", "run_id": r.json()["run_id"]}
        assert next(x for x in db.t["runs"] if x["run_id"] == old)["finished_at"]
        assert c.post("/chat/ask", headers=H, json={"question": "thời gian chờ BVP"}).json()["config"] == "B3"
        n_msg = len(db.t["messages"])
        cmp = c.post("/admin/compare", headers=HA, json={"question": "thời gian chờ BVP", "configs": ["B4", "B3"]})
        assert cmp.status_code == 200, cmp.text
        ans = cmp.json()["answers"]
        assert [a["config"] for a in ans] == ["B4", "B3"] and ans[1]["answer"] == "B3 trả lời [1]."
        assert ans[0]["run_id"].startswith("B4_demo_") and len(db.t["messages"]) == n_msg   # không lưu hội thoại
        assert c.post("/admin/compare", headers=HA, json={"question": "abc", "configs": ["B4", "B4"]}).status_code == 422
        assert c.post("/admin/compare", headers=H, json={"question": "abc", "configs": ["B4", "B3"]}).status_code == 403


def test_admin_health(tmp_path):
    _, _, app = make(tmp_path)
    with TestClient(app) as c:
        h = c.get("/admin/health", headers=HA).json()
    assert set(h) >= {"api", "ollama", "qdrant", "encoder", "reranker", "supabase", "config", "run_id", "data_version"}
    assert h["supabase"]["ok"] and h["supabase"]["data_version"] == "v1" and h["config"] == "B4"


def test_admin_users(tmp_path):
    _, db, app = make(tmp_path)
    with TestClient(app) as c:
        lst = c.get("/admin/users", headers=HA).json()
        assert {u["username"] for u in lst} >= {"admin01", "demo01"} and all("email" in u for u in lst)
        r = c.post("/admin/users", headers=HA, json={"username": "demo04", "email": "demo04@bv-rag.local"})
        assert r.status_code == 201 and len(r.json()["temp_password"]) == 12
        assert c.post("/admin/users", headers=HA, json={"username": "demo04", "email": "x@bv-rag.local"}).status_code == 409
        assert c.post("/admin/users", headers=HA, json={"username": "demo05", "email": "a@gmail.com"}).status_code == 422
        assert c.patch(f"/admin/users/{ADMIN.id}", headers=HA, json={"is_active": False}).status_code == 409
        assert c.patch(f"/admin/users/{ADMIN.id}", headers=HA, json={"role": "user"}).status_code == 409
        r = c.patch(f"/admin/users/{USER.id}", headers=HA, json={"is_active": False})
        assert r.status_code == 200 and r.json()["is_active"] is False
        assert ("update", USER.id, {"ban_duration": "876000h"}) in db.auth_calls
        assert app.state.verifier.forgot == [USER.id]
        assert c.patch("/admin/users/khong-co", headers=HA, json={"role": "user"}).status_code == 404
        pw = c.post(f"/admin/users/{OTHER.id}/reset-password", headers=HA).json()["temp_password"]
        assert ("update", OTHER.id, {"password": pw}) in db.auth_calls
        assert c.get("/admin/users", headers=H).status_code == 403


def test_ask_requires_key_when_supabase(tmp_path, monkeypatch):
    monkeypatch.setenv("DEMO_CHECK_KEY", "k123")
    _, _, app = make(tmp_path)
    with TestClient(app) as c:
        assert c.post("/ask", json={"question": "thời gian chờ BVP"}).status_code == 401
        assert c.post("/ask", headers={"X-Demo-Key": "k123"}, json={"question": "thời gian chờ BVP"}).status_code == 200
        assert c.post("/ask", headers=H, json={"question": "thời gian chờ BVP"}).status_code == 200


# ------------------------------------------------------------------ đơn vị
def test_mask_pii():
    t, n = mask_pii("CCCD 001090012345, sđt 0912 345 678, +84912345678, a.b@gmail.com, CMND 123456789")
    assert n == 5 and "[CCCD]" in t and t.count("[SĐT]") == 2 and "[EMAIL]" in t and "[CMND]" in t
    assert mask_pii("Phí 1.448.000 đồng, STBH 100.000.000, năm 2025, tuổi 18-65") == \
        ("Phí 1.448.000 đồng, STBH 100.000.000, năm 2025, tuổi 18-65", 0)


def test_make_title():
    assert make_title("Thời gian chờ?") == "Thời gian chờ"
    t = make_title("Quyền lợi điều trị nội trú của Bảo Việt An Gia gồm những gì và giới hạn ra sao")
    assert len(t) <= 49 and t.endswith("…")


def test_pipeline_product_filter_overrides_qp():
    p = pipe()
    res = p.answer("thời gian chờ BVP", product_filter=["BTB"])
    assert res["qp"]["products"] == ["BVP"] and res["qp"]["user_filter"] == ["BTB"]
    assert all(c.startswith("BTB") for c in res["contexts"])
    two = p.answer("thời gian chờ", product_filter=["BVP", "BTB"])
    assert two["qp"]["split"] and {c.split("_")[0] for c in two["contexts"]} == {"BVP", "BTB"}
    assert p.answer("thời gian chờ BVP")["qp"].get("user_filter") is None        # hành vi cũ


def test_pipeline_answer_stream_matches_answer():
    a = pipe(llm=StreamLLM()).answer("thời gian chờ BVP")
    evs = list(pipe(llm=StreamLLM()).answer_stream("thời gian chờ BVP"))
    done = evs[-1]["result"]
    assert done["answer"] == "Thời gian chờ 30 ngày [1]." and done["contexts"] == a["contexts"]
    assert [e["type"] for e in evs][:1] == ["status"]


# ------------------------------------------------------------------ AuthVerifier, SupabaseRest (httpx giả)
def test_auth_verifier_cache_and_errors():
    import httpx

    from app.deps import AuthVerifier
    calls = []

    def handler(req):
        calls.append(req.headers["authorization"])
        tok = req.headers["authorization"][7:]
        if tok == "good":
            return httpx.Response(200, json={"id": USER.id, "email": USER.email})
        if tok == "noprofile":
            return httpx.Response(200, json={"id": "zzz", "email": "z@bv-rag.local"})
        return httpx.Response(401, json={"msg": "invalid JWT"})

    http = httpx.Client(base_url="https://x.supabase.co", transport=httpx.MockTransport(handler))
    v = AuthVerifier("https://x.supabase.co", "anon", FakeDB(), ttl=60, client=http)
    u = v.verify("good")
    assert u.id == USER.id and u.role == "user" and u.email == USER.email
    v.verify("good")
    assert len(calls) == 1                                   # lần 2 lấy cache
    v.forget_user(USER.id)
    v.verify("good")
    assert len(calls) == 2
    with pytest.raises(HTTPException) as e:
        v.verify("bad")
    assert e.value.status_code == 401
    with pytest.raises(HTTPException) as e:
        v.verify("noprofile")
    assert e.value.status_code == 403


def test_supabase_rest_requests():
    import httpx

    from app.supabase_rest import SupabaseRest
    seen = []

    def handler(req):
        seen.append(req)
        if req.url.path == "/rest/v1/documents":
            return httpx.Response(201, json=[{"id": 1, "source_file": "a.pdf"}])
        if req.url.path == "/auth/v1/admin/users":
            return httpx.Response(200, json={"users": [{"id": "1", "email": "A@bv-rag.local"}]})
        return httpx.Response(204)

    http = httpx.Client(base_url="https://x.supabase.co", headers={"apikey": "k", "Authorization": "Bearer k"},
                        transport=httpx.MockTransport(handler))
    db = SupabaseRest("https://x.supabase.co", "k", client=http)
    assert db.upsert("documents", [{"source_file": "a.pdf"}], on_conflict="source_file", returning=True)[0]["id"] == 1
    r = seen[-1]
    assert r.url.params["on_conflict"] == "source_file" and "resolution=merge-duplicates" in r.headers["prefer"]
    assert r.headers["apikey"] == "k"
    db.update("runs", {"finished_at": "x"}, run_id="eq.R1")
    assert seen[-1].method == "PATCH" and seen[-1].url.params["run_id"] == "eq.R1"
    with pytest.raises(ValueError):
        db.update("runs", {"x": 1})                         # không bộ lọc → từ chối
    assert db.find_user_by_email("a@bv-rag.local")["id"] == "1"
