"""FastAPI cho demo (MethodList v2, tầng FastAPI). Chạy trên Colab L4 sau khi Ollama đã chạy:

    DEMO_CONFIG=configs/B4.yaml uvicorn app.api:app --port 8000

Endpoint
  công khai   GET  /health                         liveness: pipeline đã nạp chưa, cấu hình nào
  người dùng  POST /chat/ask                       hỏi đáp có trích dẫn, lưu hội thoại Supabase (PT-CHAT-01)
              POST /chat/ask/stream                như trên, Server-Sent Events status → token → done | error (PT-CHAT-02)
  admin       GET  /admin/health                   Ollama, Qdrant, encoder, reranker, Supabase (PT-ADM-11)
              PUT  /admin/configs/active           đổi cấu hình demo, mở run mới (PT-SET-04)
              POST /admin/compare                  1 câu hỏi trên 2 cấu hình, không lưu hội thoại (PT-SET-05)
              GET/POST /admin/users, PATCH /admin/users/{id}, POST /admin/users/{id}/reset-password (PT-ADM-01…04)
  kiểm demo   POST /ask, GET /products, GET /demo-questions  (scripts/demo_check.py; không lưu DB)

Supabase: SUPABASE_URL, SUPABASE_ANON_KEY (xác minh token), SUPABASE_SERVICE_ROLE_KEY (ghi DB). Thiếu → chỉ /ask,
/health chạy; /chat/* và /admin/* trả 503. Khi đã cấu hình Supabase, /ask cần token người dùng hoặc header
X-Demo-Key = $DEMO_CHECK_KEY. Model nạp một lần khi khởi động (~75 s gồm warm-up).
"""
from __future__ import annotations

import json
import logging
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

import yaml
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.deps import CurrentUser, bearer_token, get_current_user, get_supabase_admin, require_admin

DEMO_SCRIPT = Path(__file__).with_name("demo_script.yaml")
DEFAULT_ORIGIN_REGEX = r"https://bv-rag(-[a-z0-9-]+)?(-daisy-ngoc-ha)?\.vercel\.app"
ENV = object()   # create_app(db=ENV): đọc cấu hình Supabase từ biến môi trường
log = logging.getLogger("bv-rag")


class AskIn(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    product_filter: list[str] | None = Field(None, max_length=10)


class ChatAskIn(AskIn):
    conversation_id: str | None = None


class ActiveConfigIn(BaseModel):
    config: str = Field(..., min_length=1, max_length=40)


class CompareIn(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)
    configs: list[str] = Field(..., min_length=2, max_length=2)


class CreateUserIn(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    email: str = Field(..., max_length=80)
    role: Literal["user", "admin"] = "user"
    display_name: str | None = Field(None, max_length=80)


class UpdateUserIn(BaseModel):
    role: Literal["user", "admin"] | None = None
    is_active: bool | None = None


def demo_questions(script=DEMO_SCRIPT, bench=None) -> list[dict]:
    """Kịch bản demo: qid trong demo_script.yaml (chỉ split dev) → câu hỏi lấy từ benchmark."""
    spec = yaml.safe_load(open(script, encoding="utf-8"))
    rows = {}
    for line in open(bench or spec["benchmark"], encoding="utf-8"):
        r = json.loads(line)
        rows[r["qid"]] = r
    out = []
    for it in spec["questions"]:
        r = rows[it["qid"]]
        if r["split"] != "dev":
            raise ValueError(f"{it['qid']} thuộc split {r['split']}: kịch bản demo chỉ dùng câu dev")
        out.append({"qid": r["qid"], "label": it["label"], "group": r["group"], "answerable": r["answerable"],
                    "question": r["question"], "note": it.get("note", "")})
    return out


def _db_from_env():
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_ROLE_KEY"):
        from app.supabase_rest import SupabaseRest
        return SupabaseRest.from_env()
    return None


def _startup_config(db) -> str:
    """$DEMO_CONFIG nếu đặt; không thì cấu hình admin chọn lần trước (app_settings.active_config); mặc định B4."""
    if os.environ.get("DEMO_CONFIG"):
        return os.environ["DEMO_CONFIG"]
    if db is not None:
        try:
            from app.repo import RunRepo
            from app.service import config_path
            v = RunRepo(db).get_setting("active_config")
            if v and v.get("config"):
                return str(config_path(v["config"]))
        except Exception as e:
            log.warning("đọc app_settings.active_config: %s", e)
    return "configs/B4.yaml"


def sse(event: dict) -> str:
    return f"event: {event['event']}\ndata: {json.dumps(event['data'], ensure_ascii=False, default=str)}\n\n"


def create_app(service=None, db=ENV, verifier=ENV) -> FastAPI:
    """service: ChatService (test truyền pipeline giả); None = dựng từ cấu hình khởi động.
    db: SupabaseRest service_role | None; verifier: AuthVerifier | None; mặc định đọc từ biến môi trường."""
    from app.service import NotFound

    @asynccontextmanager
    async def lifespan(app):
        st = app.state
        if st.db is ENV:
            st.db = _db_from_env()
        if st.verifier is ENV:
            st.verifier = None
            if st.db is not None and os.environ.get("SUPABASE_ANON_KEY"):
                from app.deps import AuthVerifier
                st.verifier = AuthVerifier.from_env(st.db)
        if st.svc is None:
            from app.service import ChatService
            t0 = time.perf_counter()
            st.svc = ChatService.from_config(_startup_config(st.db), db=st.db)
            log.warning("Demo sẵn sàng sau %.0f s: %s", time.perf_counter() - t0, st.svc.info)
        if getattr(st.svc, "run_id", None) is None and hasattr(st.svc, "start_session"):
            try:
                st.svc.start_session()
            except Exception as e:   # Supabase lỗi: vẫn phục vụ /ask, run chỉ ghi file
                log.warning("start_session: %s", e)
        print(f"Demo sẵn sàng: config {st.svc.config_name}, run {getattr(st.svc, 'run_id', None)}, "
              f"Supabase {'có' if st.db else 'không'}", flush=True)
        yield
        if hasattr(st.svc, "close_session"):
            st.svc.close_session()

    app = FastAPI(title="bv-rag demo", lifespan=lifespan)
    app.state.svc, app.state.db, app.state.verifier = service, db, verifier
    # Frontend React gọi API từ domain khác (Vercel, localhost) qua tunnel ngrok/cloudflared.
    # CORS_ORIGINS: danh sách chính xác, cách nhau bởi dấu phẩy. CORS_ORIGIN_REGEX: domain Vercel của project
    # (Production bv-rag.vercel.app, Preview bv-rag-<...>-daisy-ngoc-ha.vercel.app); đặt rỗng để tắt.
    origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if o.strip()]
    origin_regex = os.environ.get("CORS_ORIGIN_REGEX", DEFAULT_ORIGIN_REGEX) or None
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_origin_regex=origin_regex,
                       allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
                       allow_headers=["Authorization", "Content-Type", "X-Demo-Key", "ngrok-skip-browser-warning"])

    def svc(request: Request):
        s = request.app.state.svc
        if s is None:
            raise HTTPException(503, "pipeline chưa nạp xong")
        return s

    def errors(fn, *a, **k):
        """Ánh xạ lỗi nghiệp vụ → HTTP."""
        from app.admin import Conflict, NotFoundUser
        try:
            return fn(*a, **k)
        except (NotFound, NotFoundUser) as e:
            raise HTTPException(404, str(e) or "không tìm thấy")
        except Conflict as e:
            raise HTTPException(409, str(e))
        except ValueError as e:
            raise HTTPException(422, str(e))

    # ------------------------------------------------------------------ công khai / kiểm demo
    @app.get("/health")
    def health(request: Request):
        s = request.app.state.svc
        return {"ok": s is not None, "config": getattr(s, "config_name", None)}

    def demo_access(request: Request):
        """/ask: mở khi chưa có Supabase (WSL, test); có Supabase → cần token hoặc X-Demo-Key."""
        if request.app.state.verifier is None:
            return
        key = os.environ.get("DEMO_CHECK_KEY")
        if key and request.headers.get("x-demo-key") == key:
            return
        if bearer_token(request):
            get_current_user(request)
            return
        raise HTTPException(401, "Cần đăng nhập hoặc X-Demo-Key")

    @app.get("/products")
    def products(request: Request):
        return svc(request).products()

    @app.get("/demo-questions")
    def demo_qs():
        return demo_questions()

    @app.post("/ask", dependencies=[Depends(demo_access)])
    def ask(body: AskIn, request: Request):
        return errors(svc(request).ask, body.question, body.product_filter)

    # ------------------------------------------------------------------ hỏi đáp có tài khoản
    @app.post("/chat/ask")
    def chat_ask(body: ChatAskIn, request: Request, user: CurrentUser = Depends(get_current_user),
                 _db=Depends(get_supabase_admin)):
        return errors(svc(request).ask_for_user, user, body.question, body.conversation_id, body.product_filter)

    @app.post("/chat/ask/stream")
    def chat_ask_stream(body: ChatAskIn, request: Request, user: CurrentUser = Depends(get_current_user),
                        _db=Depends(get_supabase_admin)):
        s = svc(request)
        ctx = errors(s.prepare_user_question, user, body.question, body.conversation_id, body.product_filter)
        return StreamingResponse((sse(ev) for ev in s.ask_stream(ctx)), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    # ------------------------------------------------------------------ quản trị
    @app.get("/admin/health")
    def admin_health(request: Request, _admin: CurrentUser = Depends(require_admin)):
        from app.health import HealthService
        return HealthService(svc(request), request.app.state.db).check()

    @app.put("/admin/configs/active")
    def set_active_config(body: ActiveConfigIn, request: Request, admin: CurrentUser = Depends(require_admin)):
        from app.configs import ConfigService
        return errors(ConfigService(svc(request), request.app.state.db).set_active, body.config, admin.id)

    @app.post("/admin/compare")
    def compare(body: CompareIn, request: Request, _admin: CurrentUser = Depends(require_admin)):
        from app.service import config_path
        for c in body.configs:
            errors(config_path, c)
        return errors(svc(request).compare, body.question, body.configs)

    def users(request: Request):
        from app.admin import AdminUserService
        return AdminUserService(get_supabase_admin(request), request.app.state.verifier)

    @app.get("/admin/users")
    def list_users(request: Request, _admin: CurrentUser = Depends(require_admin)):
        return users(request).list_users()

    @app.post("/admin/users", status_code=201)
    def create_user(body: CreateUserIn, request: Request, _admin: CurrentUser = Depends(require_admin)):
        profile, pw = errors(users(request).create_user, body.username, body.email, body.role, body.display_name)
        return {"profile": profile, "temp_password": pw}

    @app.patch("/admin/users/{user_id}")
    def update_user(user_id: str, body: UpdateUserIn, request: Request, admin: CurrentUser = Depends(require_admin)):
        return errors(users(request).update_user, user_id, admin.id, body.role, body.is_active)

    @app.post("/admin/users/{user_id}/reset-password")
    def reset_password(user_id: str, request: Request, _admin: CurrentUser = Depends(require_admin)):
        return {"temp_password": errors(users(request).reset_password, user_id)}

    return app


app = create_app()   # model chỉ nạp khi server khởi động (lifespan), import module không tốn gì
