"""Embed kho chunk bằng bge-m3 và nạp vào Qdrant (dense + sparse, payload để lọc metadata).

Vector ghi theo phiên bản dữ liệu và kiểu chunk (skill quy ước, mục 4):
    vectors/{ver}/{chunking}/dense.npy      float32 [n, 1024], đã chuẩn hóa
    vectors/{ver}/{chunking}/sparse.jsonl   {"chunk_id", "sparse": {token_id: weight}} theo đúng thứ tự
    vectors/{ver}/{chunking}/chunk_ids.json thứ tự dòng của dense.npy
    vectors/{ver}/{chunking}/meta.json      model, số chunk, thời gian, GPU, version package, commit
chunking ∈ {structure (chunks.jsonl, B2+), fixed (chunks_fixed.jsonl, B1)}.

Embed chạy trên Colab L4 (scripts/colab_batch.ipynb); nạp Qdrant chạy được ở cả Colab (:memory:) và WSL (Docker).
CLI: python -m src.ingest.indexer embed --processed DIR --vectors DIR [--chunking structure,fixed]
     python -m src.ingest.indexer index --processed DIR --vectors DIR --version v1   # nạp vào QDRANT_URL
"""
from __future__ import annotations

import argparse
import json
import platform
import subprocess
import time
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np

CHUNK_FILES = {"structure": "chunks.jsonl", "fixed": "chunks_fixed.jsonl"}
PAYLOAD_INDEX = ("product_code", "doc_type", "company", "line", "is_table")


def read_jsonl(path) -> list[dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def _env_meta() -> dict:
    meta = {"host": platform.node(), "python": platform.python_version()}
    try:
        import torch
        meta["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
    except Exception:
        meta["gpu"] = None
    pk = {}
    for name in ("torch", "transformers", "FlagEmbedding", "qdrant-client"):
        try:
            from importlib.metadata import version
            pk[name] = version(name)
        except Exception:
            pk[name] = None
    meta["packages"] = pk
    try:
        meta["repo_commit"] = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:
        meta["repo_commit"] = None
    return meta


def embed_corpus(chunks_path, out_dir, encoder, max_length: int = 512) -> dict:
    chunks = read_jsonl(chunks_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    dense, sparse = encoder.encode([c["text"] for c in chunks], max_length=max_length)
    sec = time.perf_counter() - t0
    ids = [c["chunk_id"] for c in chunks]
    np.save(out / "dense.npy", dense)
    with open(out / "sparse.jsonl", "w", encoding="utf-8") as f:
        for cid, sp in zip(ids, sparse):
            f.write(json.dumps({"chunk_id": cid, "sparse": sp}) + "\n")
    json.dump(ids, open(out / "chunk_ids.json", "w", encoding="utf-8"), ensure_ascii=False)
    meta = {"chunks": str(chunks_path), "n": len(ids), "dim": int(dense.shape[1]), "model": encoder.model_name,
            "max_length": max_length, "encode_s": round(sec, 2), "s_per_chunk": round(sec / len(ids), 4),
            "created_at": datetime.now().isoformat(timespec="seconds"), **_env_meta()}
    json.dump(meta, open(out / "meta.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    return meta


def load_vectors(vec_dir) -> tuple[list[str], np.ndarray, list[dict[int, float]]]:
    d = Path(vec_dir)
    ids = json.load(open(d / "chunk_ids.json", encoding="utf-8"))
    dense = np.load(d / "dense.npy")
    rows = read_jsonl(d / "sparse.jsonl")
    assert [r["chunk_id"] for r in rows] == ids and len(dense) == len(ids), f"{d}: vector lệch chunk_ids"
    return ids, dense, [{int(k): v for k, v in r["sparse"].items()} for r in rows]


def build_index(client, collection: str, chunks: list[dict], vec_dir, recreate: bool = True) -> int:
    """Nạp chunk + vector vào collection; payload = toàn bộ trường chunk (gồm text để sinh câu trả lời)."""
    from qdrant_client import models

    ids, dense, sparse = load_vectors(vec_dir)
    by_id = {c["chunk_id"]: c for c in chunks}
    missing = [i for i in ids if i not in by_id]
    assert not missing and len(ids) == len(by_id), f"vector và chunks.jsonl không khớp (thiếu {missing[:5]})"
    if recreate and client.collection_exists(collection):
        client.delete_collection(collection)
    client.create_collection(
        collection,
        vectors_config={"dense": models.VectorParams(size=int(dense.shape[1]), distance=models.Distance.COSINE)},
        sparse_vectors_config={"sparse": models.SparseVectorParams()},
    )
    with warnings.catch_warnings():                # Qdrant :memory: bỏ qua payload index và cảnh báo
        warnings.simplefilter("ignore", UserWarning)
        for key in PAYLOAD_INDEX:
            schema = models.PayloadSchemaType.BOOL if key == "is_table" else models.PayloadSchemaType.KEYWORD
            client.create_payload_index(collection, key, field_schema=schema)
    points = [models.PointStruct(id=i, payload=by_id[cid],
                                 vector={"dense": dense[i].tolist(),
                                         "sparse": models.SparseVector(indices=list(sparse[i]),
                                                                       values=list(sparse[i].values()))})
              for i, cid in enumerate(ids)]
    for j in range(0, len(points), 256):
        client.upsert(collection, points=points[j:j + 256])
    return len(points)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["embed", "index"])
    ap.add_argument("--processed", required=True, help="thư mục processed/{ver}")
    ap.add_argument("--vectors", required=True, help="thư mục vectors/{ver}")
    ap.add_argument("--chunking", default="structure,fixed")
    ap.add_argument("--version", help="index: phiên bản dữ liệu, đặt tên collection bv_{ver}_{chunking}")
    a = ap.parse_args()
    if a.cmd == "embed":
        from src.retrieve.encoder import M3Encoder
        enc = M3Encoder()
        for ch in a.chunking.split(","):
            meta = embed_corpus(Path(a.processed) / CHUNK_FILES[ch], Path(a.vectors) / ch, enc)
            print(f"{ch}: {meta['n']} chunk, {meta['encode_s']} s ({meta['s_per_chunk']} s/chunk), GPU {meta['gpu']}")
        return
    from src.retrieve.hybrid import collection_name, get_client
    assert a.version, "index cần --version"
    client = get_client()
    for ch in a.chunking.split(","):
        col = collection_name(a.version, ch)
        n = build_index(client, col, read_jsonl(Path(a.processed) / CHUNK_FILES[ch]), Path(a.vectors) / ch)
        print(f"{col}: {n} điểm")


if __name__ == "__main__":
    main()
