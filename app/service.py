"""ChatService (đổi tên từ DemoService): bọc RAGPipeline cho demo và lưu hội thoại vào Supabase (SV-05…SV-11).

Không đổi logic trả lời: câu trả lời, trích dẫn, từ chối lấy nguyên từ `RAGPipeline.answer()` (cùng config với run test
B4). Dịch vụ thêm: che thông tin cá nhân, metadata nguồn (sản phẩm, loại tài liệu, mục, trang, link), lưu Supabase
(service_role), ghi runs/{run_id}/log.jsonl, đổi cấu hình và so sánh 2 cấu hình.

Dựng đủ trên Colab L4: `ChatService.from_config("configs/B4.yaml", db=SupabaseRest.from_env())`
(đọc $DRIVE_DIR/processed, vectors như eval). db = None: chỉ hỏi đáp, không lưu (POST /ask, scripts/demo_check.py).
"""
from __future__ import annotations

import json
import logging
import os
import re
import threading
import time
from datetime import datetime
from pathlib import Path

from app.privacy import mask_pii
from app.repo import ChatRepo, RunRepo, utcnow
from app.runlog import RunLogger
from app.trace import build_trace_rows

log = logging.getLogger("bv-rag")

DOC_LABEL = {"quy_tac": "Quy tắc", "dieu_khoan": "Điều khoản", "bang_quyen_loi": "Bảng quyền lợi",
             "bang_phi": "Biểu phí", "brochure": "Tờ rơi", "faq": "Hỏi đáp"}
HEADER = re.compile(r"^\[[^\]\n]*\]\n")   # dòng header ngữ cảnh "[Tên SP | Loại TL | Điều …]" đầu text chunk
CONFIG_NAME = re.compile(r"^[A-Za-z0-9_-]{1,40}$")
STAGE_MSG = {"retrieve": "Đang tìm trong tài liệu chính thức", "generate": "Đang soạn câu trả lời"}


class NotFound(Exception):
    """Đối tượng không tồn tại hoặc không thuộc người dùng (→ 404)."""


def load_catalog(path="data/catalog.json") -> dict:
    """{product_code: {"name", "url", "effective_date", "docs": {file: url}}}; docs có cả đường dẫn lẫn tên file."""
    cat = json.load(open(path, encoding="utf-8"))
    out = {}
    for p in cat["products"]:
        docs = {}
        for d in p.get("documents", []):
            docs[d["file"]] = docs[Path(d["file"]).name] = d.get("url")
        out[p["product_code"]] = {"name": p["product_name"], "effective_date": p.get("effective_date"),
                                  "url": next((u for u in docs.values() if u), None), "docs": docs}
    return out


def config_path(name: str, root="configs") -> Path:
    """configs/{name}.yaml hoặc configs/ablation/{name}.yaml."""
    if not CONFIG_NAME.match(name or ""):
        raise NotFound(f"tên cấu hình không hợp lệ: {name!r}")
    for p in (Path(root) / f"{name}.yaml", Path(root) / "ablation" / f"{name}.yaml"):
        if p.exists():
            return p
    raise NotFound(f"không có cấu hình {name}")


def source_of(payload: dict, catalog: dict) -> dict:
    """Thông tin nguồn của một chunk để hiển thị (không gồm text)."""
    code = payload.get("product_code")
    prod = catalog.get(code, {})
    src = payload.get("source_file")
    return {
        "product_code": code,
        "product_name": prod.get("name", code),
        "doc_type": payload.get("doc_type"),
        "doc_label": DOC_LABEL.get(payload.get("doc_type"), payload.get("doc_type")),
        "section": payload.get("section_path"),
        "page": payload.get("page"),
        "source_file": src,
        "url": prod.get("docs", {}).get(src) or prod.get("url"),
        "effective_date": payload.get("effective_date") or prod.get("effective_date"),
        "is_table": payload.get("is_table"),
        "ocr": payload.get("ocr"),
        "manual": payload.get("manual"),
    }


def make_title(question: str, max_len: int = 48) -> str:
    """Tiêu đề cuộc trò chuyện từ câu hỏi đầu: cắt ở ranh giới từ, thêm '…' nếu dài."""
    q = " ".join(question.split()).rstrip("?.!… ")
    if len(q) <= max_len:
        return q or "Cuộc trò chuyện mới"
    cut = q[:max_len].rsplit(" ", 1)[0]
    return (cut or q[:max_len]) + "…"


def classify_refusal(res: dict) -> str | None:
    """messages.refusal_reason (SV-11, sửa 08/11). Câu bị từ chối (chặn ngưỡng hoặc LLM tự từ chối):
    ngoai_pham_vi khi query processor không nhận diện sản phẩm nào và người dùng không chọn sản phẩm
    (vd hỏi bảo hiểm xe ô tô); còn lại khong_du_can_cu (hỏi đúng sản phẩm nhưng tài liệu không có căn cứ).
    Cấu hình không có query processor (B0–B2) không biết sản phẩm → khong_du_can_cu."""
    if not res.get("refused"):
        return None
    qp = res.get("qp")
    if qp is not None and not qp.get("products") and not qp.get("user_filter"):
        return "ngoai_pham_vi"
    return "khong_du_can_cu"


class ChatService:
    def __init__(self, pipe, catalog: dict, config_name: str = "", *, db=None, runlog: RunLogger | None = None,
                 builder=None, env: dict | None = None, data_version: str | None = None):
        """pipe: RAGPipeline của cấu hình đang dùng. builder(name) -> RAGPipeline: nạp cấu hình khác khi đổi/so sánh
        (from_config dựng sẵn; test truyền dict). db: SupabaseRest service_role hoặc None."""
        self.catalog, self.config_name = catalog, config_name
        self.pipelines = {config_name: pipe}
        self.builder = builder
        self.db = db
        self.repo = ChatRepo(db) if db is not None else None
        self.runs = RunRepo(db) if db is not None else None
        self.runlog = runlog or RunLogger()
        self.env = env or {}
        self.data_version = data_version or pipe.cfg.get("data_version")
        self.run_id: str | None = None
        self.extra_runs: dict[str, str] = {}   # run của cấu hình chỉ dùng để so sánh
        self.info: dict = {}
        self._lock = threading.Lock()          # một LLM/encoder dùng chung: xử lý tuần tự, tránh tranh VRAM

    # ------------------------------------------------------------------ dựng
    @classmethod
    def from_config(cls, config_file: str, processed=None, vectors=None, catalog_path="data/catalog.json", db=None,
                    runlog=None):
        from eval.run_eval import env_meta, load_config
        from src.pipeline import RAGPipeline, build_components

        cfg = load_config(config_file)
        ver, drive = cfg["data_version"], os.environ.get("DRIVE_DIR")
        processed = Path(processed or (f"{drive}/processed/{ver}" if drive else f"data/processed/{ver}"))
        vectors = Path(vectors or (f"{drive}/vectors/{ver}" if drive else f"data/vectors/{ver}"))
        comps = build_components([cfg], processed, vectors)
        llm = comps["llm"]
        shared = {"retrievers": dict(comps["retrievers"]), "reranker": comps.get("reranker"), "encoder": None,
                  "client": None}
        for r in shared["retrievers"].values():
            shared["encoder"], shared["client"] = r.encoder, r.client

        def make_pipe(c):
            ch, mode = c["chunking"], c["retrieval"]["mode"]
            if mode != "none" and ch not in shared["retrievers"]:
                more = build_components([c], processed, vectors, llm=llm, encoder=shared["encoder"],
                                        client=shared["client"], reranker=shared["reranker"])
                shared["retrievers"].update(more["retrievers"])
                shared["reranker"] = shared["reranker"] or more.get("reranker")
                for r in more["retrievers"].values():
                    shared["encoder"], shared["client"] = r.encoder, r.client
            p = RAGPipeline(c, llm, shared["retrievers"].get(ch), reranker=shared["reranker"])
            shared["reranker"] = shared["reranker"] or p.reranker
            return p

        def builder(name: str):
            c = load_config(str(config_path(name)))
            if c["data_version"] != ver:
                raise ValueError(f"{name} dùng data_version {c['data_version']}, phiên demo đang nạp {ver}")
            return make_pipe(c)

        env = {}
        try:
            env = {k: v for k, v in env_meta().items() if k in ("runtime", "gpu", "packages", "repo_commit")}
            env.update(ollama_version=llm.version(), model_digest=llm.digest(),
                       llm_gpu_pct=(llm.gpu_status() or {}).get("gpu_pct"))
        except Exception as e:   # thông tin môi trường không chặn demo
            log.warning("env_meta: %s", e)
        svc = cls(make_pipe(cfg), load_catalog(catalog_path), cfg["name"], db=db, runlog=runlog, builder=builder,
                  env=env, data_version=ver)
        svc.llm = llm
        svc.info = {"index": comps["index"], "warmup": comps.get("warmup"), "gpu": comps.get("gpu_after_torch")}
        return svc

    @property
    def pipe(self):
        return self.pipelines[self.config_name]

    def get_pipeline(self, name: str):
        if name not in self.pipelines:
            if self.builder is None:
                raise NotFound(f"không có cấu hình {name}")
            self.pipelines[name] = self.builder(name) if callable(self.builder) else self.builder[name]
        return self.pipelines[name]

    # ------------------------------------------------------------------ phiên demo (run)
    def _start_run(self, name: str) -> str:
        rid = RunRepo.demo_run_id(name)
        if self.runs is not None:
            rid = self.runs.start_demo_run(name, self.data_version, self.env, run_id=rid)
        self.runlog.write_meta(rid, {"run_id": rid, "config": name, "split": "demo", "data_version": self.data_version,
                                     "started_at": datetime.now().isoformat(timespec="seconds"), **self.env})
        return rid

    def _finish_run(self, rid: str) -> None:
        self.runlog.write_meta(rid, {"finished_at": datetime.now().isoformat(timespec="seconds")})
        if self.runs is not None:
            try:
                self.runs.finish_run(rid)
            except Exception as e:
                log.warning("finish_run %s: %s", rid, e)

    def start_session(self) -> str:
        """Mở run demo khi API khởi động và ghi app_settings.active_config = cấu hình + run đang chạy
        (trước đây chỉ ghi khi admin đổi cấu hình nên /admin/health hiện run của phiên cũ)."""
        self.run_id = self._start_run(self.config_name)
        if self.runs is not None:
            try:
                self.runs.set_setting("active_config", {"config": self.config_name, "run_id": self.run_id})
            except Exception as e:   # không chặn khởi động
                log.warning("ghi app_settings.active_config: %s", e)
        return self.run_id

    def close_session(self) -> None:
        for rid in [self.run_id, *self.extra_runs.values()]:
            if rid:
                self._finish_run(rid)

    def switch_pipeline(self, name: str) -> str:
        """Đổi cấu hình (dùng lại LLM/encoder/reranker), đóng run cũ, mở run mới (SV-09)."""
        self.get_pipeline(name)
        with self._lock:
            old = self.run_id
            self.config_name = name
            self.run_id = self.extra_runs.pop(name, None) or self._start_run(name)
            if old and old != self.run_id:
                self._finish_run(old)
        return self.run_id

    # ------------------------------------------------------------------ hỏi đáp
    def products(self) -> list[dict]:
        return [{"product_code": k, "product_name": v["name"], "effective_date": v["effective_date"], "url": v["url"]}
                for k, v in self.catalog.items()]

    def _check_filter(self, product_filter) -> list[str] | None:
        if not product_filter:
            return None
        pf = list(dict.fromkeys(product_filter))
        bad = [p for p in pf if p not in self.catalog]
        if bad:
            raise ValueError(f"sản phẩm không có trong kho: {bad}")
        return pf

    def _run(self, pipe, question: str, product_filter=None) -> tuple[dict, list[dict]]:
        with self._lock:
            res = pipe.answer(question, product_filter) if product_filter else pipe.answer(question)
            return res, list(getattr(pipe, "last_hits", []) or [])

    def _sources(self, res: dict, hits: list[dict], cited_only: bool) -> list[dict]:
        payload = {h["chunk_id"]: h["payload"] for h in hits}
        out = []
        for i, cid in enumerate(res["contexts"], 1):
            cited = cid in res["citations"]
            if cited_only and not cited:
                continue
            p = payload.get(cid, {"chunk_id": cid})
            out.append({"n": i, "ord": i, "chunk_id": cid, "data_version": self.data_version, "cited": cited,
                        "score": next((h["score"] for h in hits if h["chunk_id"] == cid), None),
                        "text": HEADER.sub("", p.get("text", ""), count=1), **source_of(p, self.catalog),
                        "section_path": p.get("section_path")})
        return out

    def _payload(self, question: str, res: dict, hits: list[dict], config: str) -> dict:
        return {
            "question": question,
            "answer": res["answer"],
            "refused": res["refused"],
            "refusal_reason": classify_refusal(res),
            "gated": res.get("gated", False),
            "citations": [{"n": res["contexts"].index(c) + 1, "chunk_id": c} for c in res["citations"]],
            "citations_invalid": res["citations_invalid"],
            "nums_unsupported": res.get("nums_unsupported") or [],
            "sources": self._sources(res, hits, cited_only=False),
            "products_detected": (res.get("qp") or {}).get("products", []),
            "product_filter": (res.get("qp") or {}).get("user_filter"),
            "rerank_max": res.get("rerank_max"),
            "latency_ms": res["latency_ms"],
            "retrieval_ms": res["retrieval_ms"],
            "llm_ms": res["llm_ms"],
            "tokens_in": res["tokens_in"],
            "tokens_out": res["tokens_out"],
            "config": config,
            "n_contexts": len(res["contexts"]),
        }

    def _log(self, run_id: str | None, kind: str, question: str, res: dict, **extra) -> None:
        if not run_id:
            return
        try:
            self.runlog.append(run_id, {"kind": kind, "question": question, **extra, **res})
        except Exception as e:
            log.warning("runlog %s: %s", run_id, e)

    def ask(self, question: str, product_filter=None) -> dict:
        """Hỏi đáp không lưu DB (POST /ask, scripts/demo_check.py). Ghi log.jsonl của run hiện tại."""
        question = " ".join(question.split())
        if not question:
            raise ValueError("câu hỏi rỗng")
        pf = self._check_filter(product_filter)
        name, pipe, rid = self.config_name, self.pipe, self.run_id
        res, hits = self._run(pipe, question, pf)
        self._log(rid, "ask", question, res)
        return self._payload(question, res, hits, name) | {"run_id": rid}

    # ---------- hỏi đáp có tài khoản (POST /chat/ask, /chat/ask/stream)
    def prepare_user_question(self, user, question: str, conversation_id=None, product_filter=None) -> dict:
        """Kiểm tra trước khi chạy pipeline: che TTCN, độ dài, sản phẩm, quyền sở hữu cuộc trò chuyện."""
        q = " ".join((question or "").split())
        masked, n_masked = mask_pii(q)
        if len(masked) < 3:
            raise ValueError("câu hỏi quá ngắn")
        pf = self._check_filter(product_filter)
        conv = None
        if conversation_id:
            if self.repo is None:
                raise NotFound("không có cuộc trò chuyện")
            conv = self.repo.get_conversation(str(conversation_id))
            if conv is None or conv["user_id"] != user.id:
                raise NotFound("không có cuộc trò chuyện")
        return {"user": user, "question": masked, "pii_masked": n_masked > 0, "conv": conv, "product_filter": pf,
                "asked_at": utcnow()}

    def ask_for_user(self, user, question: str, conversation_id=None, product_filter=None) -> dict:
        """SV-06: che TTCN → kiểm tra cuộc → pipeline → lưu cuộc/câu hỏi/câu trả lời/trích dẫn/trace → log.jsonl.
        Pipeline chạy trước khi ghi DB để lỗi pipeline không để lại câu hỏi mồ côi; lỗi ghi DB vẫn trả câu trả lời."""
        ctx = self.prepare_user_question(user, question, conversation_id, product_filter)
        name, pipe, rid = self.config_name, self.pipe, self.run_id
        res, hits = self._run(pipe, ctx["question"], ctx["product_filter"])
        return self._persist(ctx, res, hits, name, pipe, rid)

    def ask_stream(self, ctx: dict):
        """SV-07: sự kiện status → token → done (payload như ask_for_user) | error. ctx từ prepare_user_question."""
        name, pipe, rid = self.config_name, self.pipe, self.run_id
        self._lock.acquire()
        locked = True
        try:
            res, hits = None, []
            for ev in pipe.answer_stream(ctx["question"], ctx["product_filter"]):
                if ev["type"] == "status":
                    yield {"event": "status", "data": {"stage": ev["stage"], "message": STAGE_MSG.get(ev["stage"])}}
                elif ev["type"] == "token":
                    yield {"event": "token", "data": {"text": ev["text"]}}
                elif ev["type"] == "done":
                    res = ev["result"]
            hits = list(getattr(pipe, "last_hits", []) or [])
            self._lock.release()
            locked = False
            yield {"event": "done", "data": self._persist(ctx, res, hits, name, pipe, rid)}
        except Exception as e:
            log.exception("ask_stream")
            yield {"event": "error", "data": {"message": str(e)}}
        finally:
            if locked:
                self._lock.release()

    def _persist(self, ctx: dict, res: dict, hits: list[dict], name: str, pipe, rid: str | None) -> dict:
        user, question = ctx["user"], ctx["question"]
        out = self._payload(question, res, hits, name)
        cited = [s for s in out["sources"] if s["cited"]]
        out.update(sources=cited, run_id=rid, pii_masked=ctx["pii_masked"], conversation_id=None, question_id=None,
                   message_id=None, title=None, saved=False, db_error=None)
        if ctx["conv"]:
            out.update(conversation_id=ctx["conv"]["id"], title=ctx["conv"]["title"])
        structure = pipe.cfg.get("chunking") == "structure" and pipe.cfg["retrieval"]["mode"] != "none"
        if self.repo is not None:
            try:
                conv = ctx["conv"] or self.repo.create_conversation(user.id, make_title(question))
                out.update(conversation_id=conv["id"], title=conv["title"])
                common = {"conversation_id": conv["id"], "product_filter": ctx["product_filter"]}
                q_row = self.repo.insert_messages([
                    {**common, "role": "user", "content": question, "pii_masked": ctx["pii_masked"],
                     "created_at": ctx["asked_at"]},
                ])[0]
                a_row = self.repo.insert_messages([
                    {**common, "reply_to_id": q_row["id"], "role": "assistant", "content": res["answer"],
                     "refused": res["refused"], "refusal_reason": out["refusal_reason"], "run_id": rid},
                ])[0]
                out.update(question_id=q_row["id"], message_id=a_row["id"])
                note = None
                if structure:
                    self.repo.insert_citations([{"message_id": a_row["id"], "ord": s["ord"],
                                                 "data_version": self.data_version, "chunk_id": s["chunk_id"]}
                                                for s in cited])
                elif pipe.cfg["retrieval"]["mode"] != "none":
                    note = "chunking fixed: không lưu trích dẫn/retrieval_logs (bảng chunks chỉ có chunk cấu trúc)"
                trace, logs = build_trace_rows(res, hits if structure else [], self.data_version, a_row["id"],
                                               pipe.cfg["retrieval"]["mode"], error=note)
                self.repo.insert_trace(trace, logs)
                out["saved"] = True
            except Exception as e:   # lỗi DB không làm mất câu trả lời; vẫn ghi log.jsonl
                log.exception("persist")
                out["db_error"] = str(e)
        self._log(rid, "chat", question, res, user_id=user.id, conversation_id=out["conversation_id"],
                  message_id=out["message_id"], pii_masked=ctx["pii_masked"], db_error=out["db_error"])
        return out

    # ---------- so sánh 2 cấu hình (không lưu hội thoại)
    def compare(self, question: str, configs: list[str]) -> dict:
        q = " ".join((question or "").split())
        masked, n_masked = mask_pii(q)
        if len(masked) < 3:
            raise ValueError("câu hỏi quá ngắn")
        if len(configs) != 2 or configs[0] == configs[1]:
            raise ValueError("cần đúng 2 cấu hình khác nhau")
        pipes = [self.get_pipeline(c) for c in configs]
        answers = []
        for name, pipe in zip(configs, pipes):
            rid = self.run_id if name == self.config_name else self.extra_runs.get(name)
            if rid is None:
                rid = self.extra_runs[name] = self._start_run(name)
            t0 = time.perf_counter()
            res, hits = self._run(pipe, masked)
            self._log(rid, "compare", masked, res, compare_with=[c for c in configs if c != name][0])
            p = self._payload(masked, res, hits, name)
            answers.append({"config": name, "run_id": rid, "answer": p["answer"], "refused": p["refused"],
                            "refusal_reason": p["refusal_reason"], "gated": p["gated"],
                            "sources": [s for s in p["sources"] if s["cited"]], "n_sources": len(p["citations"]),
                            "n_contexts": p["n_contexts"], "latency_ms": res["latency_ms"],
                            "wall_ms": int((time.perf_counter() - t0) * 1000)})
        return {"question": masked, "pii_masked": n_masked > 0, "answers": answers}


DemoService = ChatService   # tên cũ (tuần 7, trước khi nối Supabase)
