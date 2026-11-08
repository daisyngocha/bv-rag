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

Kiến trúc (decision-log 2026-11-08): giao diện React (`web/`, thiết kế từ Figma) → FastAPI (`app/api.py`) →
`RAGPipeline` với đúng config B4 của run test; Supabase (Auth + Postgres) lưu tài khoản, lịch sử chat, trích dẫn và vết
xử lý theo `docs/roadmap/5.DA1_DataDictionary.xlsx`. React chỉ giữ anon key (đăng nhập, đọc qua RLS); FastAPI xác
thực JWT và ghi câu trả lời bằng service_role. `app/service.py` gắn nguồn cho mỗi đoạn ngữ cảnh (sản phẩm, loại tài
liệu, mục, trang, link trang sản phẩm từ catalog, đoạn văn bản) và đánh dấu đoạn được trích dẫn. Mỗi câu hỏi độc lập
(không dùng lịch sử hội thoại).

API (`app/api.py`, chi tiết `docs/roadmap/7.DA1_MethodList_v2.xlsx`), header `Authorization: Bearer <access_token>`
của Supabase:

| Quyền | Endpoint | Việc |
| --- | --- | --- |
| công khai | `GET /health` | pipeline đã nạp chưa, cấu hình nào |
| người dùng | `POST /chat/ask` | `{question, conversation_id?, product_filter?}` → câu trả lời + nguồn; lưu conversations, messages, message_citations, traces, retrieval_logs |
| người dùng | `POST /chat/ask/stream` | như trên, Server-Sent Events `status` → `token` → `done` \| `error` |
| admin | `GET /admin/health` | Ollama (100% GPU), Qdrant, encoder, reranker, Supabase |
| admin | `PUT /admin/configs/active` | đổi cấu hình demo (B0–B4), mở run mới, ghi app_settings |
| admin | `POST /admin/compare` | 1 câu hỏi trên 2 cấu hình, không lưu hội thoại |
| admin | `GET/POST /admin/users`, `PATCH /admin/users/{id}`, `POST /admin/users/{id}/reset-password` | tài khoản demo, mật khẩu tạm trả một lần |
| kiểm demo | `POST /ask`, `GET /products`, `GET /demo-questions` | `scripts/demo_check.py`; không lưu DB; khi có Supabase cần token hoặc `X-Demo-Key` |

Câu hỏi được che CCCD/CMND/SĐT/email (`app/privacy.py`) trước khi vào pipeline, DB và log. Mỗi phiên demo là một run
`{config}_demo_{yyyymmdd-hhmm}` (bảng `runs`, split = demo) và một thư mục `runs/{run_id}/` (log.jsonl + meta.json,
`$RUNS_DIR` hoặc `$DRIVE_DIR/runs`). Lỗi ghi Supabase không làm mất câu trả lời (`saved: false`, `db_error`).
Cấu hình chunk cố định (B1) không lưu trích dẫn vào DB vì bảng `chunks` chỉ có chunk cấu trúc. Domain frontend khai
trong `CORS_ORIGINS` (mặc định `http://localhost:5173` và `http://127.0.0.1:5173`).

Colab L4: mở `scripts/colab_demo.ipynb`, Run all; cell 7 in link API `https://….trycloudflare.com` (gán vào
`VITE_API_URL` của frontend), cell 8 chạy kịch bản `app/demo_script.yaml` (6 câu dev: tra cứu, bảng phí, tình huống,
so sánh, 2 câu ngoài phạm vi) và ghi bản chép lên Drive `runs/demo/`. Chạy cục bộ (WSL, Ollama CPU rất chậm, chỉ để debug):

```bash
uv pip install -r requirements/demo.txt
DEMO_CONFIG=configs/B4.yaml PYTHONPATH=. uvicorn app.api:app --port 8000   # đọc .env nếu export trước; thiếu Supabase → chỉ /ask
npm install && VITE_API_URL=http://localhost:8000 npm run dev
python scripts/demo_check.py --api http://localhost:8000 --out runs/demo/demo_local
```

## Supabase (Auth + Postgres)

Schema theo `docs/roadmap/5.DA1_DataDictionary.xlsx` (nhóm A–D, đủ ưu tiên 1/2/3; nhóm E để ĐA2/ĐATN):
`supabase/migrations/0001_enums` → `0002_tables` → `0003_indexes` → `0004_rls_grants` → `0005_views_rpc` → `0006_triggers`.
React dùng anon key + JWT (RLS); FastAPI và script dùng service_role (`app/supabase_rest.py`). Key đặt trong `.env`
(mẫu `.env.example`, không commit).

Tạo project cloud (region Singapore), rồi:

```bash
npx supabase@2.20.12 link --project-ref <project-ref>
```

```bash
npx supabase@2.20.12 db push
```

Nạp dữ liệu (cần `chunks.jsonl` của bản đã đóng băng; `--dry-run` để kiểm không ghi):

```bash
PYTHONPATH=. python scripts/sync_supabase.py all --version v1 --processed $DRIVE_DIR/processed/v1 --activate
```

```bash
PYTHONPATH=. python scripts/seed_demo_users.py
```

Thứ tự trong `all`: pipeline_configs → kho tri thức (data_versions, products, documents, chunks) → câu hỏi mẫu (24 câu
dev) → runs + eval_results từ `results/*.csv`. Tài khoản demo trong `configs/demo_users.yaml`; mật khẩu từ `.env`, thiếu thì
script sinh mật khẩu tạm và in một lần. Bảng mới thêm sau này phải tự GRANT/RLS: `0004` thu hồi quyền mặc định của
anon/authenticated chỉ với các bảng đã có.

Kiểm tra migrations + RLS không cần Docker (Postgres ≥ 15 có pg_trgm, stub `auth` trong `tests/db/auth_stub.sql`):

```bash
BV_TEST_PG="host=/var/run/postgresql user=postgres" PYTHONPATH=. pytest tests/test_supabase_db.py tests/test_supabase_sync.py
```

Với Supabase local (`npx supabase start`): `npx supabase db reset` rồi `psql "$DB_URL" -f tests/db/rls_check.sql`.

## Giao diện React (web/)

Thiết kế Figma, nối Supabase (supabase-js + RLS: đăng nhập, lịch sử, cài đặt, danh mục, nhật ký, dashboard) và
FastAPI (hỏi đáp stream, quản trị tài khoản, cấu hình, so sánh, trạng thái hệ thống). Tạo `.env.local` ở gốc repo
(không commit; chỉ anon key, không bao giờ service_role):

```bash
VITE_SUPABASE_URL=https://<project-ref>.supabase.co
VITE_SUPABASE_ANON_KEY=<anon key>
VITE_API_URL=https://<link>.trycloudflare.com
```

```bash
npm install && npm run dev
```

Mở http://localhost:5173, đăng nhập bằng tài khoản demo. `CORS_ORIGINS` của API phải có `http://localhost:5173`
(mặc định đã có). Câu hỏi được che CCCD/CMND/SĐT/email ngay trong trình duyệt trước khi gửi.

Kiểm luồng giao diện không cần Colab (Playwright giả lập Supabase + FastAPI ở tầng mạng):

```bash
node tests/e2e/frontend_smoke.cjs
```

