#!/usr/bin/env bash
# Đồng bộ artifact giữa WSL và Google Drive (MyDrive/bv-rag) bằng rclone. Chỉ copy, không xóa ở đích.
#   scripts/sync.sh push processed v1     # WSL → Drive: data/processed/v1 → processed/v1
#   scripts/sync.sh pull vectors v1       # Drive → WSL: vectors/v1 → data/vectors/v1 (debug Qdrant Docker)
#   scripts/sync.sh pull runs [run_id]    # Drive → WSL: runs/ → runs/ (tính metric, phân tích lỗi)
#   DRY=1 scripts/sync.sh ...             # chỉ in việc sẽ làm
# Remote mặc định gdrive:bv-rag (đặt RCLONE_REMOTE nếu tên remote khác; tạo remote: rclone config, loại drive).
# Chỉ tài liệu công khai và dữ liệu giả được lên Drive; không dùng script này cho dữ liệu thật.
set -euo pipefail
REMOTE="${RCLONE_REMOTE:-gdrive:bv-rag}"
cd "$(git rev-parse --show-toplevel)"
cmd="${1:-}"; what="${2:-}"; arg="${3:-}"

case "$cmd $what" in
  "push processed") [[ -n "$arg" ]] || { echo "Thiếu phiên bản (v1…)"; exit 1; }
                    src="data/processed/$arg"; dst="$REMOTE/processed/$arg" ;;
  "pull processed") [[ -n "$arg" ]] || { echo "Thiếu phiên bản (v1…)"; exit 1; }
                    src="$REMOTE/processed/$arg"; dst="data/processed/$arg" ;;
  "pull vectors")   [[ -n "$arg" ]] || { echo "Thiếu phiên bản (v1…)"; exit 1; }
                    src="$REMOTE/vectors/$arg"; dst="data/vectors/$arg" ;;
  "pull runs")      src="$REMOTE/runs${arg:+/$arg}"; dst="runs${arg:+/$arg}" ;;
  *) sed -n '2,8p' "$0"; exit 1 ;;   # vectors và runs chỉ do Colab ghi nên không có push
esac

[[ "$cmd" == push && ! -d "$src" ]] && { echo "Không có $src"; exit 1; }
echo "$src → $dst"
rclone copy "$src" "$dst" --progress ${DRY:+--dry-run}
