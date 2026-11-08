# bv-rag

Hệ thống hỏi đáp có trích dẫn về sản phẩm bảo hiểm cá nhân dựa trên RAG (ĐA chuyên ngành 1, HUST).
Quy ước repo, schema và config theo skill `hust-da1-bh-genai-conventions`.

## Môi trường

| Nơi chạy | Vai trò | Python / torch |
| --- | --- | --- |
| Google Colab L4 (Pay As You Go) | Mọi lần chạy chính thức: embed, B0–B4, demo | 3.13.16 / 2.11.0+cu130 (image Colab) |
| WSL2 Ubuntu (CPU) | Phát triển, xây kho tri thức, debug truy xuất, phân tích log | 3.11 / torch CPU |

Số liệu đưa vào báo cáo chỉ lấy từ lần chạy trên Colab L4, cùng một loại GPU cho cả B0–B4 (decision-log 2026-10-25).
Kết quả chạy trên WSL hoặc T4 chỉ để debug và tham khảo.
Thư viện chính pin trong `requirements/base.txt` theo bản đã đo ở smoke v3, kiểm chứng lại ở v4 (`docs/smoke_colab_L4_20261025_v4.json`);
torch dùng bản có sẵn của Colab, version thực tế mỗi lần chạy ghi trong `meta.json` (smoke test: khối `env`, `colab`).

## Chạy trên Colab L4

Code lấy từ repo public trên GitHub (clone đầu mỗi phiên); dữ liệu và kết quả trao đổi qua Google Drive.

1. Mở `scripts/colab_smoke.ipynb` trên Colab (File → Open notebook → GitHub → `daisyngocha/bv-rag`).
2. Runtime → Change runtime type → GPU **L4** → Save → Connect. Cell 1 (`nvidia-smi`) phải in `NVIDIA L4`.
3. Runtime → Run all. Notebook cài `requirements/base.txt`, cài Ollama, tải `qwen2.5:7b-instruct-q4_K_M`,
   chạy `scripts/smoke_test.py --qdrant-url :memory: --keep-loaded`, rồi ghi `docs/smoke_colab_<GPU>_<ngày><SUFFIX>.json`
   (kèm GPU, version package, commit repo) và tải về máy.
4. Cell cuối tắt runtime để dừng tính unit. Commit file JSON vào `docs/` và chép tóm tắt vào `docs/progress.md`.

Google Drive (`MyDrive/bv-rag`) là kho artifact giữa WSL và Colab, đồng bộ với WSL bằng rclone:

| Thư mục | Nội dung | Ghi từ |
| --- | --- | --- |
| `processed/vN/` | `chunks.jsonl`, `catalog.json`, `glossary.json` | WSL |
| `vectors/vN/` | `dense.npy`, `sparse.jsonl`, chunk_ids | Colab (embed) |
| `runs/{run_id}/` | log JSONL, `meta.json` (GPU, version Ollama, digest model, version package) | Colab (B0–B4) |

Phiên Colab là tạm: đầu ra luôn ghi về Drive, model tải lại mỗi phiên.
Chỉ tài liệu công khai và dữ liệu giả được đưa lên Drive/Colab.
Chạy lô dùng `scripts/colab_batch.ipynb` (dừng ngay nếu GPU không phải L4); đồng bộ WSL ↔ Drive bằng `scripts/sync.sh`
(xem mục Embed và index).

## Cài đặt trên WSL2 Ubuntu

Yêu cầu sẵn có: uv + Python 3.11, Docker Engine trong Ubuntu, khoảng 15 GB ổ trống.
WSL dùng để phát triển và debug; không lấy số liệu báo cáo từ đây.

```bash
# 1. Môi trường Python
cd ~/projects/bv-rag
uv venv --python 3.11 && source .venv/bin/activate
uv pip install torch --index-url https://download.pytorch.org/whl/cpu      # máy không có GPU NVIDIA
# uv pip install torch --index-url https://download.pytorch.org/whl/cu121  # máy có GPU, nvidia-smi chạy được trong WSL
uv pip install -r requirements/base.txt

# 2. Qdrant
sudo service docker start
docker compose up -d
curl -s localhost:6333 | head -c 200; echo

# 3. Ollama (WSL không có systemd nên tự bật server)
curl -fsSL https://ollama.com/install.sh | sh
nohup ollama serve > ~/ollama.log 2>&1 &
ollama pull qwen2.5:7b-instruct-q4_K_M
```

## Smoke test hạ tầng

```bash
python scripts/smoke_test.py                    # đủ 5 bước: env, embed, rerank, qdrant, ollama
python scripts/smoke_test.py --skip ollama      # bỏ bước nào đó
python scripts/smoke_test.py --qdrant-url :memory:   # thử Qdrant không cần Docker
```

Lần đầu tải bge-m3 và bge-reranker-v2-m3 (mỗi model khoảng 2,3 GB) vào `~/.cache/huggingface`.
Kết quả ghi ở `logs/smoke_*.json`; chép phần tóm tắt vào `docs/progress.md`.
Trên Colab chạy qua `scripts/colab_smoke.ipynb` (mục Chạy trên Colab L4).

## Cấu hình thực nghiệm

| Config | Nội dung |
| --- | --- |
| B0 | Không RAG |
| B1 | Dense bge-m3, chunk cố định 512 token |
| B2 | Chunk theo Chương/Mục/Điều/Khoản, bảng Markdown |
| B3 | Hybrid dense + sparse, lọc metadata, query processor |
| B4 | Reranker, ngưỡng từ chối, prompt trích dẫn |

## Cài đặt Docling
Trên WSL chạy pip install -r requirements/base.txt -r requirements/ingest.txt, trên Colab chỉ cài base.txt.
Cần xác nhận base.txt không chứa dòng torch nào bị cài đè khi chạy trên WSL.
Nếu có (ví dụ torch==2.11.0+cu130), tách dòng đó sang một file chỉ dùng cho Colab, hoặc thêm điều kiện môi trường.

## Xây kho tri thức (WSL)

Mỗi sản phẩm cần 3 thứ: PDF trong `data/raw/products/{P}/` (ghi `data/raw/sources.csv` bằng `scripts/make_sources.py`),
config `configs/products/{P}.yaml` (meta sản phẩm, cấu hình từng file, kiểm tra riêng) và truth lập tay `data/truth/{P}.json`
(xem `data/truth/README.md`).

```bash
PYTHONPATH=. python scripts/build_kb.py --product BVP              # parse (có cache) → chunk → kiểm tra → gộp
PYTHONPATH=. python scripts/build_kb.py --all                      # mọi configs/products/*.yaml
PYTHONPATH=. python scripts/build_kb.py --product BVP --force-parse
PYTHONPATH=. python scripts/build_kb.py --steps merge              # chỉ gộp lại
```

Mỗi sản phẩm sinh 2 bộ chunk từ cùng một bản parse: theo cấu trúc (B2+, `chunks.jsonl`) và cố định 512 token,
chồng lấn 64 (B1, `chunks_fixed.jsonl`); tham số lấy từ `configs/B2.yaml`, `configs/B1.yaml`.
Chỉ sản phẩm đạt mọi kiểm tra và dùng tokenizer bge-m3 mới được gộp vào `data/processed/{ver}/`.
`align_fixed.json` ghi chunk cố định nào phủ chunk cấu trúc nào, dùng để chấm Recall@k/MRR của B1
vì `evidence_ids` của benchmark theo chunk cấu trúc.

## Embed và index

Một lần, trên WSL: cài rclone và tạo remote Google Drive tên `gdrive` (`rclone config`, loại `drive`);
tên khác thì đặt `RCLONE_REMOTE=<tên>:bv-rag`.

```bash
# WSL: đẩy kho chunk lên Drive
scripts/sync.sh push processed v1
# Colab L4: mở scripts/colab_batch.ipynb, Run all → vectors/v1/{structure,fixed}/ trên Drive
# WSL: kéo vector về, nạp Qdrant Docker để debug truy xuất
scripts/sync.sh pull vectors v1
QDRANT_URL=http://localhost:6333 PYTHONPATH=. python -m src.ingest.indexer index \
    --processed data/processed/v1 --vectors data/vectors/v1 --version v1
```

Đóng băng một phiên bản (trước khi soạn benchmark và chạy B0–B4 trên nó) bằng
`PYTHONPATH=. python scripts/freeze_data.py freeze v1 --vectors data/vectors/v1`, rồi commit `data/manifests/v1.json`.
Sau đó `build_kb.py` không ghi đè `processed/v1` nữa, còn `colab_batch.ipynb` (cell 3b) kiểm `processed` và `vectors`
trên Drive theo manifest và bỏ qua bước embed.

Collection đặt tên `bv_{ver}_{chunking}`. Truy xuất qua `src.retrieve.hybrid.Retriever` (dense | sparse | hybrid RRF,
lọc metadata bằng dict, ví dụ `{"product_code": ["BVP"], "doc_type": "quy_tac"}`); câu hỏi encode bằng
`src.retrieve.encoder.M3Encoder`, trên WSL chạy CPU được vì câu hỏi ngắn.


## Chạy benchmark và tính metric

Colab L4: mở `scripts/colab_eval.ipynb`, sửa `CONFIGS` (và `BRANCH` nếu chạy nhánh khác main) ở cell 2, Run all. Notebook kiểm manifest, cài Ollama,
rồi gọi `eval/run_eval.py` (dev × 3 lần với seed 42/43/44, test × 1). Mỗi câu ghi ngay vào `runs/{run_id}/log.jsonl`
trên Drive; Colab ngắt thì chạy tiếp bằng `--resume <run_id>`.

```bash
# Colab (notebook gọi sẵn): nhiều config dùng chung LLM đã warmup, bge-m3 và Qdrant :memory:
python -m eval.run_eval --config configs/B0.yaml configs/B1.yaml configs/B2.yaml --split dev --repeat 3
# WSL: kéo log về, tính metric theo nhóm câu, ghi results/{config}_v1_{split}_{yyyymmdd}[_rN].csv
scripts/sync.sh pull runs
PYTHONPATH=. python -m eval.metrics runs/B1_v1_dev_<stamp>_r0 --align-sweep        # chọn ngưỡng căn chỉnh B1 (dev)
PYTHONPATH=. python -m eval.metrics runs/B*_v1_dev_<stamp>_r* --align-threshold 0.3   # ngưỡng chính; 0.5 để phân tích độ nhạy
```

B3 (`retrieval.use_filter: true`) chạy thêm query processor `src/retrieve/query_processor.py`: nhận diện sản phẩm
theo tên catalog + `data/manual/product_aliases.csv`, lọc `product_code`, câu nhắc ≥ 2 sản phẩm truy xuất riêng từng
sản phẩm rồi ghép xen kẽ; log có khối `qp`. Ablation hybrid không lọc: `configs/ablation/B3hyb.yaml`.
Rà câu nghi lỗi và phân tích lỗi theo từng câu qua nhiều run:

```bash
PYTHONPATH=. python -m eval.per_question runs/B1_v1_test_<stamp> runs/B2_v1_test_<stamp> runs/B3_v1_test_<stamp> \
    --out results/review/per_question_v1_test.csv
```

`eval.metrics` đánh dấu run không chính thức (không phải Colab L4, LLM < 100% GPU, thiếu câu, `--qids/--limit`,
code chưa commit, prompt vượt `num_ctx`); chỉ run chính thức được đưa vào bảng báo cáo.
B4 (`rerank.enabled: true`) chấm lại top-30 bằng bge-reranker-v2-m3 (`src/retrieve/reranker.py`; câu tách theo sản phẩm
rerank riêng từng danh sách rồi ghép), đưa top-5 sau rerank vào prompt `rag_v2` (đoạn đánh số, trích dẫn `[n]` map về
chunk_id). Điểm rerank cao nhất < `rerank.min_score` thì từ chối không gọi LLM. Chọn ngưỡng trên dev (B4 để `min_score: null`):

```bash
PYTHONPATH=. python -m eval.metrics runs/B4_v1_dev_<stamp>_r* --gate-sweep     # ghi min_score vào configs/B4.yaml rồi mới chạy test
```

Ablation: `configs/ablation/B4rr.yaml` (rerank, prompt rag_v1, không chặn), `configs/ablation/B4ng.yaml` (B4 không chặn, chỉ test).
Prompt ở `src/generate/prompts.py`, chọn bằng khóa `prompt` trong config; prompt đã chạy chính thức thì không sửa, thêm tên mới.

## Demo chatbot có trích dẫn (tuần 7)

FastAPI `app/api.py` (`POST /ask`, `GET /products`, `GET /demo-questions`, `GET /health`) bọc `RAGPipeline` với đúng
config B4 của run test; `app/service.py` gắn nguồn cho mỗi đoạn ngữ cảnh (sản phẩm, loại tài liệu, mục, trang, link
trang sản phẩm từ catalog, đoạn văn bản) và đánh dấu đoạn được trích dẫn. Giao diện `app/streamlit_app.py`: câu trả lời
với `[n]`, danh sách nguồn mở rộng được, cảnh báo khi từ chối do ngưỡng, số không có trong nguồn hoặc trích dẫn sai.
Mỗi câu hỏi độc lập (không dùng lịch sử hội thoại).

Colab L4: mở `scripts/colab_demo.ipynb`, Run all; cell 7 in link `https://….trycloudflare.com`, cell 8 chạy kịch bản
`app/demo_script.yaml` (6 câu dev: tra cứu, bảng phí, tình huống, so sánh, 2 câu ngoài phạm vi) và ghi bản chép lên
Drive `runs/demo/`. Chạy cục bộ (WSL, Ollama CPU rất chậm, chỉ để debug):

```bash
uv pip install -r requirements/demo.txt
DEMO_CONFIG=configs/B4.yaml PYTHONPATH=. uvicorn app.api:app --port 8000
BV_API_URL=http://localhost:8000 streamlit run app/streamlit_app.py
python scripts/demo_check.py --api http://localhost:8000 --out runs/demo/demo_local
```
