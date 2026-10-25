"""Client gọi LLM qua Ollama, dùng chung cho pipeline, eval và smoke test.

Ollama chọn số layer đưa lên GPU (num_gpu) và kích thước ngữ cảnh (num_ctx) lúc NẠP model.
Nếu một request sau mang options khác, Ollama nạp lại model và có thể chia layer sang CPU.
Vì vậy:
  - gọi warmup() một lần, TRƯỚC khi PyTorch (bge-m3, reranker) chiếm VRAM;
  - mọi request dùng đúng bộ load_options đó;
  - keep_alive=-1 giữ model trên GPU suốt phiên Colab.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass

import requests

NS = 1e9
# Đoạn văn chung chung ~400 token, chỉ để khởi tạo kernel; không liên quan dữ liệu dự án.
WARMUP_PROMPT = ("Bảo hiểm là cơ chế chia sẻ rủi ro giữa nhiều người tham gia. " * 30
                 + "Hãy tóm tắt đoạn trên trong một câu.")


@dataclass
class LLMResult:
    text: str
    tokens_in: int | None
    tokens_out: int | None
    latency_ms: int
    prefill_tok_s: float | None
    decode_tok_s: float | None


class OllamaClient:
    def __init__(self, llm_cfg: dict, seed: int | None = None, base_url: str | None = None):
        self.model = llm_cfg["model"]
        self.base_url = (base_url or os.environ.get("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
        self.keep_alive = llm_cfg.get("keep_alive", -1)
        self.load_options = {"num_ctx": llm_cfg.get("num_ctx", 4096), "num_gpu": llm_cfg.get("num_gpu", 99)}
        self.gen_options = {"temperature": llm_cfg.get("temperature", 0.1),
                            "num_predict": llm_cfg.get("max_tokens", 600)}
        if seed is not None:
            self.gen_options["seed"] = seed

    # ------------------------------------------------------------ vòng đời model
    def warmup(self, compute: bool = True, timeout: int = 900) -> dict:
        """Nạp model lên GPU rồi chạy một lượt sinh ngắn.

        Prompt rỗng chỉ nạp trọng số; lượt sinh đầu tiên còn phải khởi tạo kernel CUDA (có thể vài chục
        giây), nên chạy một lượt ~400 token ngay tại đây để câu hỏi thật đầu tiên không gánh chi phí đó.
        """
        t0 = time.perf_counter()
        r = requests.post(f"{self.base_url}/api/generate", timeout=timeout, json={
            "model": self.model, "prompt": "", "keep_alive": self.keep_alive, "options": self.load_options})
        r.raise_for_status()
        out = {"load_s": round(time.perf_counter() - t0, 1)}
        if compute:
            w = self.generate(WARMUP_PROMPT, timeout=timeout, num_predict=8)
            out.update(warmup_s=round(w.latency_ms / 1000, 1), warmup_tokens_in=w.tokens_in,
                       warmup_prefill_tok_s=w.prefill_tok_s)
        return out

    def unload(self) -> None:
        requests.post(f"{self.base_url}/api/generate", timeout=60,
                      json={"model": self.model, "prompt": "", "keep_alive": 0})

    # ------------------------------------------------------------ sinh
    def generate(self, prompt: str, timeout: int = 1800, **options) -> LLMResult:
        opts = {**self.gen_options, **options, **self.load_options}  # load_options luôn thắng để không nạp lại
        t0 = time.perf_counter()
        r = requests.post(f"{self.base_url}/api/generate", timeout=timeout, json={
            "model": self.model, "prompt": prompt, "stream": False,
            "keep_alive": self.keep_alive, "options": opts})
        r.raise_for_status()
        d = r.json()
        latency_ms = int((time.perf_counter() - t0) * 1000)

        def rate(n, dur):
            return round(n / (dur / NS), 1) if n and dur else None

        return LLMResult(
            text=d.get("response", "").strip(),
            tokens_in=d.get("prompt_eval_count"), tokens_out=d.get("eval_count"), latency_ms=latency_ms,
            prefill_tok_s=rate(d.get("prompt_eval_count"), d.get("prompt_eval_duration")),
            decode_tok_s=rate(d.get("eval_count"), d.get("eval_duration")),
        )

    # ------------------------------------------------------------ thông tin môi trường (ghi vào meta.json)
    def gpu_status(self) -> dict:
        """Tỷ lệ model nằm trên VRAM, từ /api/ps. 100 = toàn bộ trên GPU."""
        models = requests.get(f"{self.base_url}/api/ps", timeout=10).json().get("models", [])
        m = next((x for x in models if x.get("name", "").startswith(self.model)), None)
        if not m:
            return {"loaded": False}
        size, vram = m.get("size", 0), m.get("size_vram", 0)
        return {"loaded": True, "size_gb": round(size / 1024**3, 2), "vram_gb": round(vram / 1024**3, 2),
                "gpu_pct": round(100 * vram / size, 1) if size else None}

    def version(self) -> str | None:
        return requests.get(f"{self.base_url}/api/version", timeout=10).json().get("version")

    def digest(self) -> str | None:
        tags = requests.get(f"{self.base_url}/api/tags", timeout=10).json().get("models", [])
        return next((m.get("digest") for m in tags if m.get("name") == self.model), None)


def make_llm(llm_cfg: dict, seed: int | None = None):
    if llm_cfg.get("provider", "ollama") == "ollama":
        return OllamaClient(llm_cfg, seed=seed)
    raise NotImplementedError(f"provider {llm_cfg['provider']!r} chưa hỗ trợ")
