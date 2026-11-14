# bv-rag

Hệ thống hỏi đáp có trích dẫn về sản phẩm bảo hiểm cá nhân Bảo Việt dựa trên RAG (ĐA chuyên ngành 1, HUST, chuyên ngành GenAI).
Đồ án 1/3 (ĐA1 → ĐA2 → ĐATN): retriever, benchmark, harness và log dùng lại cho ĐA2/ĐATN.
Quy ước repo, schema và config theo skill `hust-da1-bh-genai-conventions`.

## Trạng thái (13/11/2026)

| Phần | Trạng thái |
| --- | --- |
| Kho tri thức v1 (đóng băng, `data/manifests/v1.json`) | 5 sản phẩm BHBV (BVP, BTB, C37, ITC, FLX): 634 chunk cấu trúc, 286 chunk cố định; `data/catalog.json`, `data/glossary.json` (241 mục) |
| Benchmark | `benchmark/benchmark_v1.1.jsonl` (150 câu, 5 nhóm × 30; dev 30, test 120), thay đổi so với v1 ở `benchmark/CHANGELOG.md` |
| Thực nghiệm | B0–B4 + ablation trên test Colab L4 (8 run chính thức, `configs/test_runs_official.txt`); Ragas, kiểm định theo cặp, phân tích lỗi xong tuần 8 |
| Demo | React (Vercel) + Supabase + FastAPI trên Colab L4, chạy đầu–cuối |
| Còn lại | Báo cáo, slide (tuần 9–10) |

Kết quả: `docs/results_summary.md` (bảng tổng, sinh tự động), `docs/results_w8.md` (Ragas, kiểm định, phân tích lỗi).
Tiến độ: `docs/progress.md`. Quyết định: `docs/decision-log.md`. Thiết kế (use case, ERD, data dictionary, method list,
kiến trúc): `docs/roadmap/`, `docs/architecture/`.

## Cấu trúc repo

| Thư mục | Nội dung |
| --- | --- |
| `src/ingest/` | parse (Docling), chunk cấu trúc và cố định, embed bge-m3, index Qdrant |
| `src/retrieve/` | `hybrid.Retriever`, `encoder.M3Encoder`, `query_processor`, `reranker` |
| `src/generate/` | `llm_client` (Ollama), `prompts.py` (rag_v1/v2/v3) |
| `src/pipeline.py` | `RAGPipeline` dùng chung cho eval và demo |
| `eval/` | chạy benchmark, metric, Ragas, McNemar/Wilcoxon, kappa, bảng phân tích lỗi |
| `app/` | FastAPI (`api.py`, `service.py`, quản trị, che TTCN, ghi Supabase) |
| `web/` | giao diện React (Vite; `package.json`, `index.html` ở gốc repo) |
| `supabase/migrations/` | schema Postgres, RLS, view/RPC, trigger |
| `configs/` | B0–B4, `ablation/`, `products/`, `judge_*.yaml`, tài khoản demo |
| `data/` | `raw/` (sources.csv), `manual/` (nhập tay), `truth/`, `manifests/`, catalog, glossary; `processed/` không có trong git |
| `benchmark/` | benchmark v1, v1.1, schema `README_schema.md`, CHANGELOG |
| `results/` | CSV metric (`archive_v1/`: số theo v1), `ragas/`, `review/` (chấm tay, kiểm định, phân tích lỗi) |
| `scripts/` | build KB, đóng băng dữ liệu, notebook Colab, đồng bộ Drive/Supabase, chọn mẫu chấm tay |

`runs/`, `data/processed/`, `.env`, `.env.local` không commit.

## Môi trường

| Nơi chạy | Vai trò | Python / torch |
| --- | --- | --- |
| Google Colab L4 (Pay As You Go) | Mọi lần chạy chính thức: embed, B0–B4, demo | 3.13.16 / 2.11.0+cu130 (image Colab) |
| WSL2 Ubuntu (CPU) | Phát triển, xây kho tri thức, debug truy xuất, tính metric từ log, judge Ragas | 3.11 / torch CPU |

Số liệu đưa vào báo cáo chỉ lấy từ lần chạy trên Colab L4, cùng một loại GPU cho cả B0–B4 (decision-log 2026-10-25).
Kết quả chạy trên WSL hoặc T4 chỉ để debug và tham khảo.
Thư viện chính pin trong `requirements/base.txt` theo bản đã đo ở smoke v3, kiểm chứng lại ở v4 (`docs/smoke_colab_L4_20261025_v4.json`);
torch dùng bản có sẵn của Colab, version thực tế mỗi lần chạy ghi trong `meta.json` (smoke test: khối `env`, `colab`).

| File requirements | Cài ở đâu | Dùng cho |
| --- | --- | --- |
| `base.txt` | Colab, WSL | embed, rerank, Qdrant, pipeline (không chứa torch) |
| `ingest.txt` | WSL | Docling, pypdf, torch/torchvision bản CPU (parse PDF) |
| `demo.txt` | Colab, WSL | FastAPI, uvicorn, httpx |
| `bench.txt` | WSL | soạn nháp benchmark bằng Gemini (`eval/bench_draft.py`) |
| `judge.txt` | WSL, venv riêng `.venv-judge` | Ragas 0.4.3 + LangChain 0.3, judge Gemini/Claude |

## Chạy trên Colab L4

Code lấy từ repo public trên GitHub (clone nhánh `main` đầu mỗi phiên); dữ liệu và kết quả trao đổi qua Google Drive.
Mọi thay đổi vào `main` qua nhánh `feat/*` + PR (decision-log 2026-10-25) để `main` luôn chạy được trên Colab.

| Notebook | Việc |
| --- | --- |
| `scripts/colab_smoke.ipynb` | smoke test hạ tầng |
| `scripts/colab_batch.ipynb` | embed + index (dừng nếu GPU không phải L4; kiểm manifest, bỏ qua embed nếu bản đã đóng băng) |
| `scripts/colab_eval.ipynb` | chạy benchmark B0–B4 |
| `scripts/colab_demo.ipynb` | API demo + Ollama, link qua ngrok/cloudflared |

Smoke test:

1. Mở `scripts/colab_smoke.ipynb` trên Colab (File → Open notebook → GitHub → `daisyngocha/bv-rag`).
2. Runtime → Change runtime type → GPU **L4** → Save → Connect. Cell 1 (`nvidia-smi`) phải in `NVIDIA L4`.
3. Runtime → Run all. Notebook cài `requirements/base.txt`, cài Ollama, tải `qwen2.5:7b-instruct-q4_K_M`,
   chạy `scripts/smoke_test.py --qdrant-url :memory: --keep-loaded`, rồi ghi `docs/smoke_colab_<GPU>_<ngày><SUFFIX>.json`
   (kèm GPU, version package, commit repo) và tải về máy.
4. Cell cuối tắt runtime để dừng tính unit. Commit file JSON vào `docs/` và chép tóm tắt vào `docs/progress.md`.

Google Drive (`MyDrive/bv-rag`) là kho artifact giữa WSL và Colab, đồng bộ với WSL bằng rclone (`scripts/sync.sh`):

| Thư mục | Nội dung | Ghi từ |
| --- | --- | --- |
| `processed/vN/` | `chunks.jsonl`, `chunks_fixed.jsonl`, `align_fixed.json`, `catalog.json`, `glossary.json` | WSL |
| `vectors/vN/` | `structure/`, `fixed/`: `dense.npy`, `sparse.jsonl`, chunk_ids | Colab (embed) |
| `runs/{run_id}/` | log JSONL, `meta.json` (GPU, version Ollama, digest model, version package) | Colab (B0–B4, demo) |

Phiên Colab là tạm: đầu ra luôn ghi về Drive, model tải lại mỗi phiên.
Chỉ tài liệu công khai và dữ liệu giả được đưa lên Drive/Colab.

## Cài đặt trên WSL2 Ubuntu

Yêu cầu sẵn có: uv + Python 3.11, Docker Engine trong Ubuntu, khoảng 15 GB ổ trống.
WSL dùng để phát triển và debug; không lấy số liệu báo cáo từ đây.

```bash
# 1. Môi trường Python (.venv): torch CPU + Docling lấy từ ingest.txt, cài TRƯỚC base.txt
cd ~/projects/bv-rag
uv venv --python 3.11 && source .venv/bin/activate
uv pip install -r requirements/ingest.txt
uv pip install -r requirements/base.txt -r requirements/demo.txt -r requirements/bench.txt

# 2. Judge Ragas: venv riêng để LangChain không xung đột với pipeline
uv venv .venv-judge --python 3.11 && uv pip install --python .venv-judge -r requirements/judge.txt

# 3. Qdrant (chỉ để debug truy xuất; run chính thức dùng Qdrant :memory: trên Colab)
sudo service docker start
docker compose up -d
curl -s localhost:6333 | head -c 200; echo

# 4. Ollama (WSL không có systemd nên tự bật server)
curl -fsSL https://ollama.com/install.sh | sh
nohup ollama serve > ~/ollama.log 2>&1 &
ollama pull qwen2.5:7b-instruct-q4_K_M
```

torch/torchvision bản CUDA lệch ABI với torch +cpu (lỗi `torchvision::nms`, FlagEmbedding không import được), vì vậy
trên WSL chỉ dùng bản CPU pin trong `ingest.txt` (decision-log 2026-10-26). Trên Colab chỉ cài `base.txt` (+ `demo.txt` khi demo).

Key API (Gemini, Anthropic, Supabase) đặt trong `.env` (mẫu `.env.example`); nạp bằng `set -a; source .env; set +a`.

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

Chung: LLM `qwen2.5:7b-instruct-q4_K_M` (Ollama, temperature 0,1, `num_ctx` 8192), top-k truy xuất 30, đưa 5 đoạn vào prompt.

| Config | Nội dung |
| --- | --- |
| B0 | Không RAG |
| B1 | Dense bge-m3, chunk cố định 512 token, chồng lấn 64; prompt `rag_v1` |
| B2 | Như B1 nhưng chunk theo cấu trúc (Chương/Mục/Điều/Khoản), bảng Markdown |
| B3 | Hybrid dense + sparse (RRF), query processor nhận diện sản phẩm và lọc `product_code` |
| B4 | B3 + rerank bge-reranker-v2-m3 (top-30 → top-5, `max_length` 1024), ngưỡng từ chối `min_score` 0,90, prompt `rag_v3` |

Ablation (`configs/ablation/`): `B3hyb` (hybrid, không lọc), `B4rr` (rerank + `rag_v1`, không chặn), `B4ng` (B4 không chặn ngưỡng).
B4 (`configs/B4.yaml`) là cấu hình chính thức, chốt trên dev trước khi chạy test; demo dùng đúng config này.

## Xây kho tri thức (WSL)

Mỗi sản phẩm cần 3 thứ: PDF trong `data/raw/products/{P}/` (ghi `data/raw/sources.csv` bằng `scripts/make_sources.py`),
config `configs/products/{P}.yaml` (meta sản phẩm, cấu hình từng file, kiểm tra riêng) và truth lập tay `data/truth/{P}.json`
(xem `data/truth/README.md`). Bảng OCR không đọc được thì nhập tay vào `data/manual/` (ví dụ `BTB_PL3.csv`, `FLX_BQL.csv`).

```bash
PYTHONPATH=. python scripts/build_kb.py --product BVP              # parse (có cache) → chunk → kiểm tra → gộp
PYTHONPATH=. python scripts/build_kb.py --all                      # mọi configs/products/*.yaml
PYTHONPATH=. python scripts/build_kb.py --product BVP --force-parse
PYTHONPATH=. python scripts/build_kb.py --steps merge              # chỉ gộp lại
```

Parser: Docling backend pypdfium2, tách trang 2-up theo đánh dấu trong config, bỏ item nằm ngoài trang; chunker lấy mục
lục (pdftotext) làm khung, nhận tiêu đề bằng regex (decision-log 2026-10-26).
Mỗi sản phẩm sinh 2 bộ chunk từ cùng một bản parse: theo cấu trúc (B2+, `chunks.jsonl`) và cố định 512 token,
chồng lấn 64 (B1, `chunks_fixed.jsonl`); tham số lấy từ `configs/B2.yaml`, `configs/B1.yaml`. Chunk cấu trúc tối đa 1024 token.
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
trên Drive theo manifest và bỏ qua bước embed. v1 đã đóng băng (vector commit `6f28917`).

Collection đặt tên `bv_{ver}_{chunking}`. Truy xuất qua `src.retrieve.hybrid.Retriever` (dense | sparse | hybrid RRF,
lọc metadata bằng dict, ví dụ `{"product_code": ["BVP"], "doc_type": "quy_tac"}`); câu hỏi encode bằng
`src.retrieve.encoder.M3Encoder`, trên WSL chạy CPU được vì câu hỏi ngắn.

## Chạy benchmark và tính metric

Benchmark hiện hành là `benchmark/benchmark_v1.1.jsonl` (sửa đáp án/evidence từ v1, câu hỏi giữ nguyên). Các run chạy
với v1; metric tính lại từ log bằng `--bench benchmark/benchmark_v1.1.jsonl`, không chạy lại GPU. Số theo v1 lưu ở
`results/archive_v1/`. Chỉ tinh chỉnh trên dev, không bao giờ trên test.

Colab L4: mở `scripts/colab_eval.ipynb`, sửa `CONFIGS` (và `BRANCH` nếu chạy nhánh khác main) ở cell 2, Run all. Notebook kiểm manifest, cài Ollama,
rồi gọi `eval/run_eval.py` (dev × 3 lần với seed 42/43/44, test × 1). Mỗi câu ghi ngay vào `runs/{run_id}/log.jsonl`
trên Drive; Colab ngắt thì chạy tiếp bằng `--resume <run_id>`.

```bash
# Colab (notebook gọi sẵn): nhiều config dùng chung LLM đã warmup, bge-m3 và Qdrant :memory:
python -m eval.run_eval --config configs/B0.yaml configs/B1.yaml configs/B2.yaml --split dev --repeat 3
# WSL: kéo log về, tính metric theo nhóm câu
scripts/sync.sh pull runs
PYTHONPATH=. python -m eval.metrics runs/B1_v1_dev_<stamp>_r0 --align-sweep        # chọn ngưỡng căn chỉnh B1 (dev)
PYTHONPATH=. python -m eval.metrics $(cat configs/test_runs_official.txt) --align-threshold 0.3 \
    --bench benchmark/benchmark_v1.1.jsonl                                          # 0.5 để phân tích độ nhạy
```

CSV ghi vào `results/{config}_{benchmark}_{split}_{yyyymmdd-HHMM}[_rN].csv` (stamp lấy từ run_id).
Run test chính thức là 8 run trong `configs/test_runs_official.txt`; không dùng glob `runs/*_v1_test_*` (khớp cả run thử).
`eval.metrics` đánh dấu run không chính thức (không phải Colab L4, LLM < 100% GPU, thiếu câu, `--qids/--limit`,
code chưa commit, prompt vượt `num_ctx`); chỉ run chính thức được đưa vào bảng báo cáo.

B3 (`retrieval.use_filter: true`) chạy thêm query processor `src/retrieve/query_processor.py`: nhận diện sản phẩm
theo tên catalog + `data/manual/product_aliases.csv`, lọc `product_code`, câu nhắc ≥ 2 sản phẩm truy xuất riêng từng
sản phẩm rồi ghép xen kẽ; log có khối `qp`.

B4 (`rerank.enabled: true`) chấm lại top-30 bằng bge-reranker-v2-m3 (`src/retrieve/reranker.py`; câu tách theo sản phẩm
rerank riêng từng danh sách rồi ghép), đưa top-5 sau rerank vào prompt `rag_v3` (đoạn đánh số, trích dẫn `[n]` map về
chunk_id; chỉ dựa vào đoạn nói trực tiếp về đúng đối tượng). Điểm rerank cao nhất < `rerank.min_score` thì từ chối
không gọi LLM. Ngưỡng 0,90 chọn trên dev bằng `--gate-sweep` (decision-log 2026-11-07):

```bash
PYTHONPATH=. python -m eval.metrics runs/B4_v1_dev_<stamp>_r* --gate-sweep     # quét ngưỡng trên dev
```

Prompt ở `src/generate/prompts.py`, chọn bằng khóa `prompt` trong config; prompt đã chạy chính thức thì không sửa, thêm tên mới.

Rà câu nghi lỗi theo từng câu qua nhiều run, rồi sinh bảng tổng:

```bash
PYTHONPATH=. python -m eval.per_question $(cat configs/test_runs_official.txt) \
    --out results/review/per_question_v1.1_test.csv
PYTHONPATH=. python scripts/build_results_summary.py       # docs/results_summary.md, không sửa số bằng tay
```

## Ragas, kiểm định, phân tích lỗi (tuần 8, WSL)

Judge chỉ chấm câu answerable không bị từ chối; dùng Faithfulness và AnswerCorrectness (`weights=[1, 0]`).
j1 = Gemini (`configs/judge_j1.yaml`, judge chính), c2 = Claude Haiku (`configs/judge_c2.yaml`, kiểm độ vững).
Không sửa `eval/ragas_eval.py`, `configs/judge_*.yaml` sau khi đã chấm chính thức.

```bash
set -a; source .env; set +a
# Chấm một run (ghi dần từng câu, chạy lại chỉ chấm câu thiếu/lỗi) → results/ragas/{run_id}__{judge}.csv + .usage.jsonl
PYTHONPATH=. .venv-judge/bin/python -m eval.ragas_eval runs/B4_v1_test_20261107-1335 \
    --judge configs/judge_j1.yaml --bench benchmark/benchmark_v1.1.jsonl
# Gộp điểm vào CSV metric (chạy lại sau mỗi lần eval.metrics)
PYTHONPATH=. python -m eval.ragas_summary --judge j1 --bench benchmark/benchmark_v1.1.jsonl $(ls results/*_v1.1_test_*.csv)
# Hiệu chỉnh judge với 30 câu chấm tay
PYTHONPATH=. .venv-judge/bin/python -m eval.calibrate_judge results/review/manual30_B4_v1_test_20261107-1335.csv \
    results/ragas/B4_v1_test_20261107-1335__j1.csv results/ragas/B4ng_v1_test_20261107-1335__j1.csv
```

| Việc | Lệnh / file |
| --- | --- |
| McNemar theo cặp câu (hit@1, hit@5, từ chối nhầm, khớp số), Holm | `eval/mcnemar.py` → `results/review/mcnemar_v1.1_test.{csv,txt}` |
| Wilcoxon theo cặp (MRR, Ragas) | `eval/paired_tests.py ... --ragas-judge j1` → `results/review/paired_tests_v1.1_test.txt` |
| Chọn mẫu chấm tay 30 câu | `scripts/make_manual30.py` → `results/review/manual30_*` |
| Chấm mù 10 câu, kappa | `scripts/make_blind10.py`, `eval/kappa.py` → `results/review/kappa_blind10.md` |
| Bảng phân tích lỗi (mã R1/R2/P1/G1/G2/F1/F2/D1) | `eval/error_sheet.py` → `results/review/error_analysis_B4_v1.1_test.xlsx` |

Chỉ ghi "cải thiện" khi kiểm định theo cặp có ý nghĩa sau Holm; còn lại ghi "không phân biệt được với n = 96".

## Demo chatbot có trích dẫn

Kiến trúc (decision-log 2026-11-08): giao diện React (`web/`, thiết kế từ Figma, deploy Vercel) → FastAPI (`app/api.py`, chạy
trên Colab L4) → `RAGPipeline` với đúng config B4 của run test; Supabase (Auth + Postgres) lưu tài khoản, lịch sử chat, trích
dẫn và vết xử lý theo `docs/roadmap/5.DA1_DataDictionary.xlsx`. React chỉ giữ anon key (đăng nhập, đọc qua RLS); FastAPI xác
thực token qua Supabase Auth và ghi câu trả lời bằng service_role. `app/service.py` gắn nguồn cho mỗi đoạn ngữ cảnh (sản phẩm,
loại tài liệu, mục, trang, link trang sản phẩm từ catalog, đoạn văn bản) và đánh dấu đoạn được trích dẫn. Mỗi câu hỏi độc lập
(không dùng lịch sử hội thoại). Câu hỏi gợi ý sản phẩm theo nhu cầu bị từ chối đúng phạm vi ĐA1 (để ĐA2).

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

Câu hỏi được che CCCD/CMND/SĐT/email (`app/privacy.py`) trước khi vào pipeline, DB và log. Câu bị từ chối có
`refusal_reason`: `ngoai_pham_vi` khi không nhận diện được sản phẩm, còn lại `khong_du_can_cu`. Mỗi phiên demo là một run
`{config}_demo_{yyyymmdd-hhmm}` (bảng `runs`, split = demo) và một thư mục `runs/{run_id}/` (log.jsonl + meta.json,
`$RUNS_DIR` hoặc `$DRIVE_DIR/runs`). Lỗi ghi Supabase không làm mất câu trả lời (`saved: false`, `db_error`).
Cấu hình chunk cố định (B1) không lưu trích dẫn vào DB vì bảng `chunks` chỉ có chunk cấu trúc.

Colab L4: mở `scripts/colab_demo.ipynb`, Run all; cell 7 mở API ra ngoài qua ngrok static domain (Colab Secrets
`NGROK_AUTHTOKEN`, `NGROK_DOMAIN`; thiếu secret thì dùng cloudflared, link tạm đổi mỗi phiên), cell 8 chạy kịch bản
`app/demo_script.yaml` (6 câu dev: tra cứu, bảng phí, tình huống, so sánh, 2 câu ngoài phạm vi) và ghi bản chép lên Drive
`runs/demo/`. Bản chép và bảng rà lần chạy 09/11: `docs/demo/`.

Chạy cục bộ (WSL, Ollama CPU rất chậm, chỉ để debug):

```bash
DEMO_CONFIG=configs/B4.yaml PYTHONPATH=. uvicorn app.api:app --port 8000   # đọc .env nếu export trước; thiếu Supabase → chỉ /ask
npm install && VITE_API_URL=http://localhost:8000 npm run dev
python scripts/demo_check.py --api http://localhost:8000 --out runs/demo/demo_local
```

## Supabase (Auth + Postgres)

Schema theo `docs/roadmap/5.DA1_DataDictionary.xlsx` (nhóm A–D, đủ ưu tiên 1/2/3; nhóm E để ĐA2/ĐATN):
`supabase/migrations/0001_enums` → `0002_tables` → `0003_indexes` → `0004_rls_grants` → `0005_views_rpc` → `0006_triggers`.
React dùng anon key + JWT (RLS); FastAPI và script dùng service_role (`app/supabase_rest.py`, httpx). Key đặt trong `.env`
(mẫu `.env.example`, không commit).

Tạo project cloud (region Singapore), rồi:

```bash
npx supabase@2.20.12 link --project-ref <project-ref>
npx supabase@2.20.12 db push
```

Nạp dữ liệu (cần `chunks.jsonl` của bản đã đóng băng; `--dry-run` để kiểm không ghi):

```bash
PYTHONPATH=. python scripts/sync_supabase.py all --version v1 --processed $DRIVE_DIR/processed/v1 --activate \
    --benchmark benchmark/benchmark_v1.1.jsonl
PYTHONPATH=. python scripts/seed_demo_users.py
# Sau khi CSV kết quả đổi (ví dụ thêm cột Ragas): chỉ đồng bộ lại runs + eval_results
PYTHONPATH=. python scripts/sync_supabase.py evals --benchmark benchmark/benchmark_v1.1.jsonl
```

Thứ tự trong `all`: pipeline_configs → kho tri thức (data_versions, products, documents, chunks) → câu hỏi mẫu (24 câu
dev) → runs + eval_results từ `results/*.csv` (`runs.benchmark` lấy theo phiên bản trong tên CSV). Tài khoản demo trong
`configs/demo_users.yaml`; mật khẩu từ `.env`, thiếu thì script sinh mật khẩu tạm và in một lần. Bảng mới thêm sau này
phải tự GRANT/RLS: `0004` thu hồi quyền mặc định của anon/authenticated chỉ với các bảng đã có.

Kiểm tra migrations + RLS không cần Docker (Postgres ≥ 15 có pg_trgm, stub `auth` trong `tests/db/auth_stub.sql`):

```bash
BV_TEST_PG="host=/var/run/postgresql user=postgres" PYTHONPATH=. pytest tests/test_supabase_db.py tests/test_supabase_sync.py
```

Với Supabase local (`npx supabase start`): `npx supabase db reset` rồi `psql "$DB_URL" -f tests/db/rls_check.sql`.

## Giao diện React (web/)

Thiết kế Figma, nối Supabase (supabase-js + RLS: đăng nhập, lịch sử, cài đặt, danh mục, nhật ký, dashboard) và
FastAPI (hỏi đáp stream, quản trị tài khoản, cấu hình, so sánh, trạng thái hệ thống). Dashboard "Chất lượng theo cấu
hình" hiển thị Recall@5 và Faithfulness (Ragas, j1) của lần test mới nhất (B0 không có faithfulness).
Tạo `.env.local` ở gốc repo (không commit; chỉ anon key, không bao giờ service_role):

```bash
VITE_SUPABASE_URL=https://<project-ref>.supabase.co
VITE_SUPABASE_ANON_KEY=<anon key>
VITE_API_URL=https://<ten-cua-ban>.ngrok-free.app
```

```bash
npm install && npm run dev
```

Mở http://localhost:5173, đăng nhập bằng tài khoản demo. `CORS_ORIGINS` của API mặc định có `http://localhost:5173`
và `http://127.0.0.1:5173`. Câu hỏi được che CCCD/CMND/SĐT/email ngay trong trình duyệt trước khi gửi.

### Link API cố định và deploy Vercel

1. ngrok (miễn phí): tạo tài khoản, lấy **Authtoken** và **1 static domain** (Dashboard → Domains, dạng
   `ten-cua-ban.ngrok-free.app`). Thêm Colab Secrets `NGROK_AUTHTOKEN`, `NGROK_DOMAIN`. Cell 7 của
   `scripts/colab_demo.ipynb` dùng domain này mỗi lần chạy.
2. `.env.local` và Vercel (Settings → Environment Variables, Production + Preview) đặt một lần:
   `VITE_API_URL=https://ten-cua-ban.ngrok-free.app`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`.
3. Vercel tự build mỗi lần push/merge vào `main` (Framework Vite, build `npm run build`, output `dist`).
   API cho phép CORS từ `bv-rag.vercel.app` và link Preview `bv-rag-…-daisy-ngoc-ha.vercel.app`
   (`CORS_ORIGIN_REGEX` trong `app/api.py`); domain khác thêm vào `CORS_ORIGINS` ở cell 2.
4. Supabase → Authentication → URL Configuration: Site URL = domain Vercel.

Người test chỉ dùng được hỏi đáp khi notebook Colab đang chạy; đăng nhập, lịch sử, danh mục luôn dùng được.
Gửi người test link Production, không gửi link Preview (Vercel Deployment Protection).

## Kiểm thử

```bash
PYTHONPATH=. python -m pytest tests/ -q          # test_supabase_db tự bỏ qua khi thiếu BV_TEST_PG
PYTHONPATH=. python -m pytest tests/test_eval_harness.py -q                   # harness đánh giá
node tests/e2e/frontend_smoke.cjs     # luồng giao diện, Playwright giả lập Supabase + FastAPI ở tầng mạng
```
