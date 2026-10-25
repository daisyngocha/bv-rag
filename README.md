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
Notebook chạy theo lô `scripts/colab_batch.ipynb` và script đồng bộ `scripts/sync.sh` sẽ viết ở tuần 2–3;
notebook đó dừng ngay nếu GPU không phải L4, trước mọi lần chạy chính thức.

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
