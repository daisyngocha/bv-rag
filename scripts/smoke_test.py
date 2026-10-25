"""Smoke test hạ tầng ĐA1: môi trường, bge-m3, reranker, Qdrant hybrid, Ollama.

Chạy từ thư mục gốc repo, đã kích hoạt .venv:
    python scripts/smoke_test.py                      # chạy đủ các bước
    python scripts/smoke_test.py --skip ollama        # bỏ bước nào đó
    python scripts/smoke_test.py --no-preload         # nạp Ollama SAU PyTorch (cách cũ, để so sánh)
Kết quả: in bảng tóm tắt và ghi logs/smoke_YYYYMMDD_HHMM.json.

Thứ tự mặc định: nạp model Ollama lên GPU (ollama_load) TRƯỚC khi bge-m3/reranker chiếm VRAM,
cùng load options với pipeline (configs/*.yaml → llm). Tỷ lệ model nằm trên GPU ghi ở gpu_pct.

Dữ liệu thử là các đoạn GIẢ tự soạn cho "Sản phẩm mẫu" (SP-MAU), không phải tài liệu thật.
Mỗi bước chạy độc lập: một bước lỗi không chặn các bước sau.
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import platform
import random
import resource
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.generate.llm_client import OllamaClient  # noqa: E402

# Giả định cho ước tính một lần chạy test: 120 câu × 5 cấu hình, câu trả lời có trích dẫn
ASSUME = {"n_gen": 600, "n_rerank": 120, "prompt_tokens": 2500, "output_tokens": 150}

# ---------------------------------------------------------------- dữ liệu giả
SAMPLE = [
    ("SPMAU_QT_D2_K5", "[Sản phẩm mẫu | Quy tắc | Điều 2. Giải thích từ ngữ]\n"
     "5. Thời gian chờ là khoảng thời gian kể từ ngày hợp đồng có hiệu lực mà trong đó các sự kiện "
     "bảo hiểm phát sinh không được chi trả quyền lợi, trừ trường hợp do tai nạn."),
    ("SPMAU_QT_D7", "[Sản phẩm mẫu | Quy tắc | Điều 7. Thời gian chờ]\n"
     "Thời gian chờ áp dụng như sau: 30 ngày đối với ốm đau, bệnh tật thông thường; 365 ngày đối với "
     "bệnh đặc biệt và bệnh có sẵn; 270 ngày đối với sinh con. Không áp dụng thời gian chờ đối với tai nạn."),
    ("SPMAU_QT_D9", "[Sản phẩm mẫu | Quy tắc | Điều 9. Loại trừ bảo hiểm]\n"
     "Công ty không chi trả trong các trường hợp: điều trị thẩm mỹ, chỉnh hình răng; hành vi cố ý của "
     "người được bảo hiểm; sử dụng chất kích thích; tham gia đánh nhau, trừ trường hợp tự vệ."),
    ("SPMAU_QT_D12", "[Sản phẩm mẫu | Quy tắc | Điều 12. Hồ sơ yêu cầu bồi thường]\n"
     "Người yêu cầu bồi thường nộp hồ sơ trong vòng 365 ngày kể từ ngày kết thúc điều trị, gồm: giấy "
     "yêu cầu bồi thường, giấy ra viện, hóa đơn và bảng kê chi phí, đơn thuốc."),
    ("SPMAU_BQL_TB1", "[Sản phẩm mẫu | Bảng quyền lợi | Bảng 1. Quyền lợi điều trị nội trú]\n"
     "| Quyền lợi | Chương trình Đồng | Chương trình Bạc | Chương trình Vàng |\n"
     "| --- | --- | --- | --- |\n"
     "| Giới hạn năm | 50 triệu | 100 triệu | 200 triệu |\n"
     "| Tiền giường/ngày | 1 triệu | 2 triệu | 3 triệu |\n"
     "| Phẫu thuật/năm | 25 triệu | 50 triệu | 100 triệu |"),
    ("SPMAU_QT_D4", "[Sản phẩm mẫu | Quy tắc | Điều 4. Đối tượng bảo hiểm]\n"
     "Người được bảo hiểm từ 15 ngày tuổi đến 65 tuổi tại thời điểm tham gia; được tái tục đến 70 tuổi."),
    ("SPMAU_QT_D15", "[Sản phẩm mẫu | Quy tắc | Điều 15. Chấm dứt hợp đồng]\n"
     "Bên mua bảo hiểm có quyền chấm dứt hợp đồng bằng văn bản. Công ty hoàn lại 80% phí bảo hiểm "
     "tương ứng thời gian còn lại nếu chưa có khoản bồi thường nào được chi trả."),
    ("SPMAU_FAQ_1", "[Sản phẩm mẫu | FAQ | Câu 1]\n"
     "Hỏi: Tôi có thể mua cho con 2 tuổi không? Đáp: Có, trẻ từ 15 ngày tuổi được tham gia nếu bố "
     "hoặc mẹ cùng tham gia hợp đồng."),
]
QUESTIONS = [  # (câu hỏi, chunk_id đúng)
    ("Thời gian chờ đối với bệnh đặc biệt là bao lâu?", "SPMAU_QT_D7"),
    ("Tiền giường mỗi ngày của chương trình Bạc là bao nhiêu?", "SPMAU_BQL_TB1"),
    ("Hạn nộp hồ sơ bồi thường là bao lâu sau khi kết thúc điều trị?", "SPMAU_QT_D12"),
]
_FILLER_TOPICS = [
    "Phương thức đóng phí", "Thông báo thay đổi địa chỉ", "Giải quyết tranh chấp",
    "Ngôn ngữ hợp đồng", "Nghĩa vụ kê khai thông tin", "Hiệu lực của hợp đồng",
]
_FILLER_SENT = (
    "Bên mua bảo hiểm và Công ty thực hiện các quyền và nghĩa vụ theo thỏa thuận tại hợp đồng này và "
    "theo quy định của pháp luật hiện hành. Mọi thông báo phải được lập thành văn bản và gửi đến địa chỉ "
    "đã đăng ký. Trường hợp có thay đổi, các bên có trách nhiệm thông báo cho nhau trong thời hạn quy định. "
)


def build_corpus(n: int = 100) -> list[tuple[str, str]]:
    """8 đoạn mẫu + đoạn nhiễu dài cỡ 300–400 token để đo thời gian sát thực tế."""
    corpus = list(SAMPLE)
    for i in range(n - len(SAMPLE)):
        topic = _FILLER_TOPICS[i % len(_FILLER_TOPICS)]
        corpus.append((f"SPMAU_QT_D{20 + i}",
                       f"[Sản phẩm mẫu | Quy tắc | Điều {20 + i}. {topic}]\n" + _FILLER_SENT * 4))
    return corpus


# ---------------------------------------------------------------- tiện ích
def peak_rss_gb() -> float:
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 / 1024, 2)


def meminfo_gb() -> dict:
    out = {}
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            k, v = line.split(":", 1)
            if k in ("MemTotal", "MemAvailable"):
                out[k] = round(int(v.split()[0]) / 1024 / 1024, 1)
    except OSError:
        pass
    return out


def free_gpu() -> dict:
    """Trả lại VRAM PyTorch đang giữ để không lấn phần của Ollama."""
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            peak = torch.cuda.max_memory_reserved() / 1024**3
            torch.cuda.empty_cache()
            return {"torch_peak_vram_gb": round(peak, 2),
                    "torch_vram_after_free_gb": round(torch.cuda.memory_reserved() / 1024**3, 2)}
    except ImportError:
        pass
    return {}


def make_client(args) -> OllamaClient:
    cfg = yaml.safe_load((ROOT / args.config).read_text(encoding="utf-8"))
    llm = dict(cfg["llm"])
    if args.model:
        llm["model"] = args.model
    return OllamaClient(llm, seed=cfg.get("seed"), base_url=args.ollama_url)


def check_url(url: str, timeout: int = 10) -> str:
    try:
        r = requests.get(url, timeout=timeout)
        return f"OK ({r.status_code})"
    except requests.RequestException as e:
        return f"FAIL ({type(e).__name__})"


# ---------------------------------------------------------------- các bước
def step_env(args, ctx) -> dict:
    res = {"python": sys.version.split()[0], "platform": platform.platform(),
           "cpu_count": os.cpu_count(), **meminfo_gb()}
    try:
        import torch
        res["torch"] = torch.__version__
        res["cuda"] = torch.cuda.is_available()
        if res["cuda"]:
            p = torch.cuda.get_device_properties(0)
            res["gpu"] = p.name
            res["vram_gb"] = round(p.total_memory / 1024**3, 1)
    except ImportError:
        res["torch"] = "chưa cài"
        res["cuda"] = False
    ctx["cuda"] = res.get("cuda", False)
    res["huggingface"] = check_url("https://huggingface.co")
    res["ollama_server"] = check_url(f"{args.ollama_url}/api/tags")
    res["qdrant_server"] = "in-memory" if args.qdrant_url == ":memory:" else check_url(args.qdrant_url)
    res["https_proxy"] = bool(os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy"))
    return res


def step_embed(args, ctx) -> dict:
    from FlagEmbedding import BGEM3FlagModel

    corpus = build_corpus(args.n_chunks)
    t0 = time.perf_counter()
    model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=ctx.get("cuda", False))
    load_s = time.perf_counter() - t0

    texts = [t for _, t in corpus]
    t0 = time.perf_counter()
    out = model.encode(texts, batch_size=32 if ctx.get("cuda") else 8, max_length=512,
                       return_dense=True, return_sparse=True)
    enc_s = time.perf_counter() - t0
    q = model.encode([x for x, _ in QUESTIONS], max_length=128, return_dense=True, return_sparse=True)

    # top-1 theo dense để xem bge-m3 hiểu tiếng Việt ở mức tối thiểu
    ids = [i for i, _ in corpus]
    sims = q["dense_vecs"] @ out["dense_vecs"].T
    hits = [ids[int(s.argmax())] == gold for s, (_, gold) in zip(sims, QUESTIONS)]

    ctx.update(corpus=corpus, doc_dense=out["dense_vecs"], doc_sparse=out["lexical_weights"],
               q_dense=q["dense_vecs"], q_sparse=q["lexical_weights"])
    per_chunk = enc_s / len(texts)
    dim = int(out["dense_vecs"].shape[1])
    del model, out, q
    return {"model_load_s": round(load_s, 1), "n_chunks": len(texts),
            "encode_s": round(enc_s, 1), "s_per_chunk": round(per_chunk, 3),
            "est_4000_chunks_min": round(per_chunk * 4000 / 60, 1), "dense_dim": dim,
            "dense_top1_correct": f"{sum(hits)}/{len(hits)}", "peak_rss_gb": peak_rss_gb(), **free_gpu()}


def step_rerank(args, ctx) -> dict:
    from FlagEmbedding import FlagReranker

    corpus = ctx.get("corpus") or build_corpus(args.n_chunks)
    cands = corpus[:30]  # đúng top_k=30 của config: 1 câu hỏi × 30 đoạn
    t0 = time.perf_counter()
    rr = FlagReranker("BAAI/bge-reranker-v2-m3", use_fp16=ctx.get("cuda", False))
    load_s = time.perf_counter() - t0

    times, hits, gold_scores = [], [], []
    for question, gold in QUESTIONS:
        t0 = time.perf_counter()
        scores = rr.compute_score([[question, t] for _, t in cands], normalize=True)
        times.append(time.perf_counter() - t0)
        best = cands[max(range(len(scores)), key=lambda i: scores[i])][0]
        hits.append(best == gold)
        gold_scores.append(round(float(scores[[c[0] for c in cands].index(gold)]), 3))
    del rr
    ctx["rerank_s"] = sum(times) / len(times)
    return {"model_load_s": round(load_s, 1), "s_per_query_30_pairs": round(sum(times) / len(times), 2),
            "top1_correct": f"{sum(hits)}/{len(hits)}", "gold_scores": gold_scores,
            "peak_rss_gb": peak_rss_gb(), **free_gpu()}


def _sparse(lw: dict):
    from qdrant_client import models
    return models.SparseVector(indices=[int(k) for k in lw], values=[float(v) for v in lw.values()])


def step_qdrant(args, ctx) -> dict:
    from qdrant_client import QdrantClient, models

    res = {}
    if "doc_dense" in ctx:
        corpus, dd, ds, qd, qs = (ctx[k] for k in ("corpus", "doc_dense", "doc_sparse", "q_dense", "q_sparse"))
        dd, qd = dd.tolist(), qd.tolist()
        res["vectors"] = "bge-m3"
    else:  # bước embed bị bỏ qua: dùng vector ngẫu nhiên, chỉ kiểm tra hạ tầng
        rnd = random.Random(42)
        corpus = build_corpus(args.n_chunks)
        dd = [[rnd.random() for _ in range(1024)] for _ in corpus]
        ds = [{str(rnd.randint(0, 250000)): rnd.random() for _ in range(20)} for _ in corpus]
        qd = [[rnd.random() for _ in range(1024)] for _ in QUESTIONS]
        qs = [{str(rnd.randint(0, 250000)): rnd.random() for _ in range(5)} for _ in QUESTIONS]
        res["vectors"] = "random (không đánh giá chất lượng)"

    if args.qdrant_url == ":memory:":
        client = QdrantClient(":memory:")
    else:
        client = QdrantClient(url=args.qdrant_url)
        res["server_version"] = requests.get(args.qdrant_url, timeout=10).json().get("version")

    name = "smoke_test"
    if client.collection_exists(name):
        client.delete_collection(name)
    client.create_collection(
        name,
        vectors_config={"dense": models.VectorParams(size=len(dd[0]), distance=models.Distance.COSINE)},
        sparse_vectors_config={"sparse": models.SparseVectorParams()},
    )
    t0 = time.perf_counter()
    client.upsert(name, points=[
        models.PointStruct(id=i, vector={"dense": dd[i], "sparse": _sparse(ds[i])},
                           payload={"chunk_id": cid, "product_code": "SPMAU"})
        for i, (cid, _) in enumerate(corpus)
    ])
    res["upsert_s"] = round(time.perf_counter() - t0, 2)

    ranks, times = [], []
    for i, (_, gold) in enumerate(QUESTIONS):
        t0 = time.perf_counter()
        hits = client.query_points(
            name,
            prefetch=[models.Prefetch(query=qd[i], using="dense", limit=30),
                      models.Prefetch(query=_sparse(qs[i]), using="sparse", limit=30)],
            query=models.FusionQuery(fusion=models.Fusion.RRF),
            query_filter=models.Filter(must=[models.FieldCondition(
                key="product_code", match=models.MatchValue(value="SPMAU"))]),
            limit=5,
        ).points
        times.append(time.perf_counter() - t0)
        got = [h.payload["chunk_id"] for h in hits]
        ranks.append(got.index(gold) + 1 if gold in got else None)
    client.delete_collection(name)
    res.update(hybrid_query_ms=round(1000 * sum(times) / len(times), 1),
               gold_rank_in_top5=ranks, collection_deleted=True)
    return res


def step_ollama_load(args, ctx) -> dict:
    """Nạp model Ollama lên GPU trước khi PyTorch chiếm VRAM, cùng load options với pipeline."""
    client = make_client(args)
    names = [m["name"] for m in requests.get(f"{args.ollama_url}/api/tags", timeout=10).json().get("models", [])]
    if client.model not in names:
        raise RuntimeError(f"chưa có model {client.model}; chạy: ollama pull {client.model}")
    load_s = client.warmup()
    ctx["llm"] = client
    return {"model": client.model, "load_options": client.load_options, "keep_alive": client.keep_alive,
            "load_s": load_s, **{f"before_torch_{k}": v for k, v in client.gpu_status().items()}}


def build_prompt(corpus) -> str:
    by_id = dict(corpus)
    # ngữ cảnh 5 đoạn như B4: 1 đoạn đúng + 4 đoạn nhiễu dài, để prompt cỡ ~1.500–2.500 token
    ctx_ids = ["SPMAU_QT_D7"] + [cid for cid, _ in corpus[len(SAMPLE):len(SAMPLE) + 4]]
    context = "\n\n".join(f"<doc id=\"{cid}\">\n{by_id[cid]}\n</doc>" for cid in ctx_ids)
    return (
        "Bạn là trợ lý hỏi đáp sản phẩm bảo hiểm. Chỉ trả lời dựa trên các đoạn tài liệu dưới đây. "
        "Sau mỗi ý, ghi mã đoạn nguồn trong ngoặc vuông, ví dụ [SPMAU_QT_D7]. "
        "Nếu tài liệu không có căn cứ, trả lời: \"Tài liệu không có thông tin để trả lời câu hỏi này.\"\n\n"
        f"{context}\n\nCâu hỏi: {QUESTIONS[0][0]}\nTrả lời bằng tiếng Việt:"
    )


def step_ollama(args, ctx) -> dict:
    res = {}
    client = ctx.get("llm")
    if client is None:  # --no-preload: nạp SAU PyTorch như phiên bản cũ
        client = make_client(args)
        res["load_s"] = client.warmup()
        ctx["llm"] = client
    corpus = ctx.get("corpus") or build_corpus(args.n_chunks)

    # 1) câu hỏi có ngữ cảnh: đo prefill và kiểm tra trích dẫn
    a = client.generate(build_prompt(corpus), num_predict=args.num_predict)
    # 2) câu trả lời dài: đo decode ổn định hơn (câu trả lời 1 chỉ vài chục token)
    b = client.generate("Viết khoảng 200 từ bằng tiếng Việt giải thích thời gian chờ trong bảo hiểm sức khỏe.",
                        num_predict=args.num_predict)

    prefill, decode = a.prefill_tok_s, b.decode_tok_s or a.decode_tok_s
    rerank_s = (ctx.get("rerank_s") or 0)
    est_h = None
    if prefill and decode:
        per_gen = ASSUME["prompt_tokens"] / prefill + ASSUME["output_tokens"] / decode
        est_h = round((ASSUME["n_gen"] * per_gen + ASSUME["n_rerank"] * rerank_s) / 3600, 2)
    res.update({
        "model": client.model, "ollama_version": client.version(), "model_digest": client.digest(),
        **{f"after_torch_{k}": v for k, v in client.gpu_status().items()},
        "prompt_tokens": a.tokens_in, "output_tokens": a.tokens_out, "prefill_tok_s": prefill,
        "answer_s": round(a.latency_ms / 1000, 1),
        "decode_probe_tokens": b.tokens_out, "decode_tok_s": decode,
        "est_test_run_h": est_h, "assume": ASSUME,
        "cites_gold": "SPMAU_QT_D7" in a.text, "mentions_365": "365" in a.text, "answer": a.text,
    })
    if not args.keep_loaded:
        client.unload()
    return res


STEPS = {"env": step_env, "ollama_load": step_ollama_load, "embed": step_embed, "rerank": step_rerank,
         "qdrant": step_qdrant, "ollama": step_ollama}


# ---------------------------------------------------------------- tóm tắt
def hints(results: dict) -> list[str]:
    out = []
    env = results.get("env", {})
    if env and not env.get("cuda"):
        out.append("Không có CUDA: embedding, rerank và LLM đều chạy CPU.")
    if str(env.get("huggingface", "")).startswith("FAIL"):
        out.append("Không tới được huggingface.co: kiểm tra proxy (HTTPS_PROXY) hoặc tải model ở mạng khác.")
    oll = results.get("ollama", {})
    if isinstance(oll.get("est_test_run_h"), (int, float)) and oll["est_test_run_h"] > 8:
        out.append(f"Chạy test 600 lượt sinh mất ~{oll['est_test_run_h']} giờ (> 1 đêm): cân nhắc API cho bước "
                   "sinh (dữ liệu công khai), giữ cùng LLM cho mọi cấu hình.")
    for key in ("before_torch_gpu_pct", "after_torch_gpu_pct"):
        pct = results.get("ollama_load", {}).get(key, results.get("ollama", {}).get(key))
        if isinstance(pct, (int, float)) and pct < 100:
            out.append(f"Ollama chỉ có {pct}% model trên GPU ({key}): decode sẽ chậm. Kiểm tra VRAM trống, "
                       "num_gpu, và nạp Ollama trước PyTorch.")
            break
    emb = results.get("embed", {})
    if isinstance(emb.get("est_4000_chunks_min"), (int, float)) and emb["est_4000_chunks_min"] > 60:
        out.append("Embed 4.000 chunk mất > 1 giờ: cân nhắc embed trên Colab/Kaggle rồi chép vector về.")
    for name in ("embed", "rerank"):
        if results.get(name, {}).get("peak_rss_gb", 0) > 0.8 * env.get("MemTotal", 1e9):
            out.append(f"Bước {name} dùng gần hết RAM của WSL: tăng memory trong %UserProfile%\\.wslconfig.")
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skip", nargs="*", default=[], choices=list(STEPS))
    ap.add_argument("--no-preload", action="store_true", help="nạp Ollama sau PyTorch (cách cũ) để so sánh")
    ap.add_argument("--keep-loaded", action="store_true", help="không giải phóng model Ollama khi xong")
    ap.add_argument("--qdrant-url", default="http://localhost:6333", help='hoặc ":memory:" để thử không cần Docker')
    ap.add_argument("--ollama-url", default="http://localhost:11434")
    ap.add_argument("--config", default="configs/B4.yaml")
    ap.add_argument("--model", default=None, help="ghi đè llm.model trong config")
    ap.add_argument("--num-predict", type=int, default=300, help="số token sinh khi đo LLM")
    ap.add_argument("--n-chunks", type=int, default=100)
    args = ap.parse_args()

    # Mạng công ty thường đặt HTTPS_PROXY; không để request tới Ollama/Qdrant local đi qua proxy.
    for var in ("NO_PROXY", "no_proxy"):
        cur = os.environ.get(var, "")
        if "localhost" not in cur:
            os.environ[var] = ",".join(x for x in (cur, "localhost,127.0.0.1") if x)

    skip = set(args.skip)
    if "ollama" in skip or args.no_preload:
        skip.add("ollama_load")

    ctx, results = {}, {}
    for name, fn in STEPS.items():
        if name in skip:
            continue
        print(f"\n=== {name} ===", flush=True)
        t0 = time.perf_counter()
        try:
            results[name] = fn(args, ctx)
        except Exception as e:  # noqa: BLE001 – smoke test cần chạy tiếp các bước khác
            results[name] = {"error": f"{type(e).__name__}: {e}", "trace": traceback.format_exc(limit=3)}
        results[name]["step_s"] = round(time.perf_counter() - t0, 1)
        for k, v in results[name].items():
            if k not in ("trace", "answer", "assume"):
                print(f"  {k:24} {v}")
        if "answer" in results[name]:
            print("  answer:\n    " + results[name]["answer"].replace("\n", "\n    "))

    results["hints"] = hints(results)
    print("\n=== gợi ý ===")
    for h in results["hints"] or ["Không có cảnh báo."]:
        print(f"  - {h}")

    out = ROOT / "logs" / f"smoke_{datetime.now():%Y%m%d_%H%M}.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"ts": datetime.now().isoformat(timespec="seconds"), **results},
                              ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\nĐã ghi {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
