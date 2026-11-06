"""bge-m3: một lượt encode cho cả dense và sparse (lexical weights). Dùng chung cho embed kho và câu hỏi."""
from __future__ import annotations

import numpy as np

# Giới hạn token khi embed chunk và khi rerank (cặp câu hỏi + chunk). Chunk cấu trúc có thể vượt max_tokens 512
# (đơn vị không tách được, vd. BTB BQL 562 token); 1024 để không cắt đuôi. build_kb chặn chunk vượt ngưỡng này.
CHUNK_MAX_LENGTH = 1024


class M3Encoder:
    def __init__(self, model_name: str = "BAAI/bge-m3", device: str | None = None):
        import torch
        from FlagEmbedding import BGEM3FlagModel

        self.cuda = torch.cuda.is_available() if device is None else device.startswith("cuda")
        self.model_name = model_name
        self.model = BGEM3FlagModel(model_name, use_fp16=self.cuda)

    def encode(self, texts: list[str], max_length: int = CHUNK_MAX_LENGTH, batch_size: int | None = None):
        """Trả về (dense float32 [n, 1024] đã chuẩn hóa, sparse list[dict[int, float]])."""
        out = self.model.encode(texts, batch_size=batch_size or (32 if self.cuda else 8), max_length=max_length,
                                return_dense=True, return_sparse=True)
        dense = np.asarray(out["dense_vecs"], dtype=np.float32)
        sparse = [{int(k): float(v) for k, v in lw.items()} for lw in out["lexical_weights"]]
        return dense, sparse

    def encode_queries(self, queries: list[str], max_length: int = 128):
        return self.encode(queries, max_length=max_length)
