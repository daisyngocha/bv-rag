"""FastAPI cho demo: POST /ask, GET /products, GET /health, GET /demo-questions.

Chạy (Colab L4, sau khi Ollama đã chạy): DEMO_CONFIG=configs/B4.yaml uvicorn app.api:app --port 8000
Model nạp một lần khi khởi động (~75 s gồm warm-up). Mỗi câu hỏi + kết quả ghi thêm vào $DEMO_LOG (jsonl) nếu đặt.
"""
from __future__ import annotations

import json
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DEMO_SCRIPT = Path(__file__).with_name("demo_script.yaml")


class AskIn(BaseModel):
    question: str = Field(..., min_length=3, max_length=2000)


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


def create_app(service=None) -> FastAPI:
    """service: đối tượng có ask(question), products(); None = dựng DemoService từ $DEMO_CONFIG khi khởi động."""
    state = {"svc": service}

    @asynccontextmanager
    async def lifespan(app):
        if state["svc"] is None:
            from app.service import DemoService
            t0 = time.perf_counter()
            state["svc"] = DemoService.from_config(os.environ.get("DEMO_CONFIG", "configs/B4.yaml"))
            print(f"Demo sẵn sàng sau {time.perf_counter() - t0:.0f} s: {getattr(state['svc'], 'info', '')}", flush=True)
        yield

    app = FastAPI(title="bv-rag demo", lifespan=lifespan)
    # Frontend React gọi API từ domain khác (tunnel cloudflared); CORS_ORIGINS cách nhau bởi dấu phẩy.
    origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
    app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST", "DELETE"],
                       allow_headers=["Authorization", "Content-Type"])

    @app.get("/health")
    def health():
        svc = state["svc"]
        return {"ok": svc is not None, "config": getattr(svc, "config_name", None)}

    @app.get("/products")
    def products():
        return state["svc"].products()

    @app.get("/demo-questions")
    def demo_qs():
        return demo_questions()

    @app.post("/ask")
    def ask(body: AskIn):
        try:
            out = state["svc"].ask(body.question)
        except ValueError as e:
            raise HTTPException(422, str(e))
        log = os.environ.get("DEMO_LOG")
        if log:
            Path(log).parent.mkdir(parents=True, exist_ok=True)
            with open(log, "a", encoding="utf-8") as f:
                f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), **out}, ensure_ascii=False) + "\n")
        return out

    return app


app = create_app()   # model chỉ nạp khi server khởi động (lifespan), import module không tốn gì
