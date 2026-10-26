"""Truy xuất trên Qdrant: dense, sparse hoặc hybrid (RRF), có lọc metadata.

Viết để ĐA2 đóng gói thành tool search_docs() không phải sửa: đầu vào là câu hỏi + bộ lọc dạng dict,
đầu ra là list dict thuần (chunk_id, score, rank, payload).
"""
from __future__ import annotations

import os

MODES = ("dense", "sparse", "hybrid")


def get_client(url: str | None = None):
    """QDRANT_URL: WSL http://localhost:6333 (Docker); Colab :memory:."""
    from qdrant_client import QdrantClient

    url = url or os.environ.get("QDRANT_URL", "http://localhost:6333")
    return QdrantClient(":memory:") if url == ":memory:" else QdrantClient(url=url)


def collection_name(data_version: str, chunking: str) -> str:
    return f"bv_{data_version}_{chunking}"


def make_filter(filters: dict | None):
    """{"product_code": "BVP"} hoặc {"product_code": ["BVP", "BTB"], "doc_type": "quy_tac"} → Filter (AND giữa các khóa)."""
    from qdrant_client import models

    if not filters:
        return None
    must = []
    for key, val in filters.items():
        if isinstance(val, (list, tuple, set)):
            must.append(models.FieldCondition(key=key, match=models.MatchAny(any=list(val))))
        else:
            must.append(models.FieldCondition(key=key, match=models.MatchValue(value=val)))
    return models.Filter(must=must)


class Retriever:
    def __init__(self, client, collection: str, encoder, mode: str = "hybrid", top_k: int = 30):
        assert mode in MODES, f"mode phải thuộc {MODES}"
        self.client, self.collection, self.encoder = client, collection, encoder
        self.mode, self.top_k = mode, top_k

    def search(self, query: str, filters: dict | None = None, top_k: int | None = None,
               mode: str | None = None) -> list[dict]:
        return self.search_many([query], filters, top_k, mode)[0]

    def search_many(self, queries: list[str], filters: dict | list[dict | None] | None = None,
                    top_k: int | None = None, mode: str | None = None) -> list[list[dict]]:
        """Encode cả lô câu hỏi một lần; filters là 1 dict dùng chung hoặc list theo từng câu."""
        from qdrant_client import models

        mode, k = mode or self.mode, top_k or self.top_k
        dense, sparse = self.encoder.encode_queries(queries)
        flts = filters if isinstance(filters, list) else [filters] * len(queries)
        out = []
        for i in range(len(queries)):
            dv = dense[i].tolist()
            sv = models.SparseVector(indices=list(sparse[i]), values=list(sparse[i].values()))
            flt = make_filter(flts[i])
            if mode == "hybrid":
                res = self.client.query_points(
                    self.collection,
                    prefetch=[models.Prefetch(query=dv, using="dense", limit=k, filter=flt),
                              models.Prefetch(query=sv, using="sparse", limit=k, filter=flt)],
                    query=models.FusionQuery(fusion=models.Fusion.RRF), limit=k, with_payload=True)
            else:
                res = self.client.query_points(self.collection, query=dv if mode == "dense" else sv,
                                               using=mode, query_filter=flt, limit=k, with_payload=True)
            out.append([{"chunk_id": p.payload["chunk_id"], "score": float(p.score), "rank": r, "payload": p.payload}
                        for r, p in enumerate(res.points, 1)])
        return out
