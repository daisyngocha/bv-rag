# bv-rag

Hệ thống hỏi đáp có trích dẫn về sản phẩm bảo hiểm cá nhân dựa trên RAG (ĐA chuyên ngành 1, HUST).
Quy ước repo, schema và config theo skill `hust-da1-bh-genai-conventions`.

## Cài đặt trên WSL2 Ubuntu

Yêu cầu sẵn có: uv + Python 3.11, Docker Engine trong Ubuntu, khoảng 15 GB ổ trống.

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

## Cấu hình thực nghiệm

| Config | Nội dung |
| --- | --- |
| B0 | Không RAG |
| B1 | Dense bge-m3, chunk cố định 512 token |
| B2 | Chunk theo Chương/Mục/Điều/Khoản, bảng Markdown |
| B3 | Hybrid dense + sparse, lọc metadata, query processor |
| B4 | Reranker, ngưỡng từ chối, prompt trích dẫn |
