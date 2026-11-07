"""bge-reranker-v2-m3: chấm lại cặp (câu hỏi, chunk) cho B4.

Điểm đã chuẩn hóa sigmoid (normalize=True) về [0, 1] để ngưỡng từ chối `rerank.min_score` có nghĩa giữa các câu.
L4: ~0,56 s cho 30 cặp (smoke v4). Nạp SAU khi LLM đã warmup (src/generate/llm_client.py).
"""
from __future__ import annotations

from src.retrieve.encoder import CHUNK_MAX_LENGTH


class BgeReranker:
    def __init__(self, model_name: str = "BAAI/bge-reranker-v2-m3", max_length: int = CHUNK_MAX_LENGTH,
                 device: str | None = None, batch_size: int | None = None):
        import torch
        from FlagEmbedding import FlagReranker

        self.cuda = torch.cuda.is_available() if device is None else device.startswith("cuda")
        self.model_name, self.max_length = model_name, max_length
        self.batch_size = batch_size or (32 if self.cuda else 8)
        self.model = FlagReranker(model_name, use_fp16=self.cuda)

    def score(self, query: str, texts: list[str]) -> list[float]:
        if not texts:
            return []
        s = self.model.compute_score([[query, t] for t in texts], normalize=True,
                                     max_length=self.max_length, batch_size=self.batch_size)
        return [float(x) for x in (s if isinstance(s, list) else [s])]


def rerank(reranker, query: str, hits: list[dict]) -> list[dict]:
    """Sắp lại hits theo điểm rerank. Mỗi hit giữ hạng/điểm truy xuất ở ret_rank/ret_score;
    score = điểm rerank, rank = hạng mới. Hòa điểm giữ thứ tự truy xuất."""
    scores = reranker.score(query, [h["payload"]["text"] for h in hits])
    out = [dict(h, ret_rank=h["rank"], ret_score=h["score"], score=s) for h, s in zip(hits, scores)]
    out.sort(key=lambda h: (-h["score"], h["ret_rank"]))
    for r, h in enumerate(out, 1):
        h["rank"] = r
    return out
