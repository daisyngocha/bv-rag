"""Đóng băng một phiên bản kho chunk: ghi manifest (sha256, số chunk, kiểm tra) vào repo và kiểm tra lại về sau.

data/processed/ không commit nên manifest data/manifests/{ver}.json là bằng chứng duy nhất trong repo rằng
benchmark, vector và mọi lần chạy B0–B4 dùng đúng một bản chunk. Khi manifest tồn tại, build_kb.py từ chối
ghi vào processed/{ver}: sửa chunk thì nâng data_version (v2…).

Chạy ở gốc repo, trên WSL:
    PYTHONPATH=. python scripts/freeze_data.py freeze v1 --vectors data/vectors/v1   # tạo manifest (một lần)
    PYTHONPATH=. python scripts/freeze_data.py verify v1 --vectors data/vectors/v1   # so lại với manifest
"""
import argparse, hashlib, json, subprocess, sys
from collections import Counter
from datetime import datetime
from pathlib import Path

PROCESSED, MANIFESTS = Path("data/processed"), Path("data/manifests")
CHUNK_FILES = {"structure": "chunks.jsonl", "fixed": "chunks_fixed.jsonl"}
VECTOR_FILES = ("dense.npy", "sparse.jsonl", "chunk_ids.json")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def file_hashes(root: Path) -> dict[str, str]:
    """sha256 mọi file trong thư mục (đường dẫn tương đối, sắp xếp), kể cả thư mục con theo sản phẩm."""
    return {str(p.relative_to(root)): sha256(p) for p in sorted(root.rglob("*")) if p.is_file()}


def collect(ver: str, vectors: Path | None) -> tuple[dict, list[str]]:
    """Trả về (nội dung manifest, danh sách lỗi). Lỗi = điều kiện không được đóng băng."""
    root, errors = PROCESSED / ver, []
    if not root.is_dir():
        sys.exit(f"Không có {root}")

    chunks = {ch: read_jsonl(root / f) for ch, f in CHUNK_FILES.items()}
    counts = {ch: dict(sorted(Counter(c["product_code"] for c in rows).items())) for ch, rows in chunks.items()}
    for ch, rows in chunks.items():
        ids = [c["chunk_id"] for c in rows]
        if len(ids) != len(set(ids)):
            errors.append(f"{ch}: chunk_id trùng {[i for i, n in Counter(ids).items() if n > 1][:5]}")

    products = {}
    for d in sorted(p for p in root.iterdir() if (p / "report.json").exists()):
        rep = json.load(open(d / "report.json", encoding="utf-8"))
        failed = [k for k, v in rep["checks"].items() if not v]
        products[d.name] = {"checks_passed": f"{len(rep['checks']) - len(failed)}/{len(rep['checks'])}",
                            "tokenizer": rep.get("tokenizer"), "align": rep.get("align")}
        if failed or rep.get("tokenizer") != "bge-m3":
            errors.append(f"{d.name}: kiểm tra chưa đạt {failed} hoặc tokenizer {rep.get('tokenizer')}")
    merged = set(counts["structure"])
    if merged != set(products):
        errors.append(f"sản phẩm đã gộp {sorted(merged)} khác sản phẩm có report {sorted(products)}")

    manifest = {
        "data_version": ver,
        "frozen_at": datetime.now().isoformat(timespec="seconds"),
        "repo_commit": subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                                      text=True).stdout.strip() or None,
        "counts": {ch: {"total": len(rows), "by_product": counts[ch]} for ch, rows in chunks.items()},
        "products": products,
        "files": file_hashes(root),
    }

    if vectors:
        manifest["vectors"] = {}
        for ch, rows in chunks.items():
            vd = vectors / ch
            if not vd.is_dir():
                errors.append(f"không có {vd}")
                continue
            ids = json.load(open(vd / "chunk_ids.json", encoding="utf-8"))
            if ids != [c["chunk_id"] for c in rows]:
                errors.append(f"vectors/{ch}: chunk_ids.json lệch {CHUNK_FILES[ch]} (embed lại)")
            meta = json.load(open(vd / "meta.json", encoding="utf-8"))
            manifest["vectors"][ch] = {
                "n": meta.get("n"), "model": meta.get("model"), "max_length": meta.get("max_length"),
                "gpu": meta.get("gpu"), "repo_commit": meta.get("repo_commit"), "created_at": meta.get("created_at"),
                "files": {f: sha256(vd / f) for f in VECTOR_FILES},
            }
    return manifest, errors


def diff(old: dict, new: dict) -> list[str]:
    out = []
    for key in ("files",):
        a, b = old[key], new[key]
        out += [f"thiếu {k}" for k in a.keys() - b.keys()]
        out += [f"thừa {k}" for k in b.keys() - a.keys()]
        out += [f"khác sha256 {k}" for k in a.keys() & b.keys() if a[k] != b[k]]
    if old["counts"] != new["counts"]:
        out.append(f"số chunk khác: {old['counts']} ≠ {new['counts']}")
    for ch, v in old.get("vectors", {}).items():
        nv = new.get("vectors", {}).get(ch)
        if nv is None:
            out.append(f"vectors/{ch}: không kiểm được (thiếu --vectors?)")
        elif nv["files"] != v["files"]:
            out.append(f"vectors/{ch}: sha256 khác manifest")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["freeze", "verify"])
    ap.add_argument("ver")
    ap.add_argument("--vectors", type=Path, help="data/vectors/{ver} (kéo về bằng scripts/sync.sh pull vectors)")
    a = ap.parse_args()
    path = MANIFESTS / f"{a.ver}.json"

    manifest, errors = collect(a.ver, a.vectors)
    if errors:
        sys.exit("Không đạt:\n  " + "\n  ".join(errors))

    if a.cmd == "freeze":
        if path.exists():
            sys.exit(f"{path} đã có: {a.ver} đã đóng băng. Sửa chunk thì nâng data_version.")
        MANIFESTS.mkdir(parents=True, exist_ok=True)
        json.dump(manifest, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        c = manifest["counts"]
        print(f"Đóng băng {a.ver}: {c['structure']['total']} chunk cấu trúc, {c['fixed']['total']} cố định, "
              f"{len(manifest['files'])} file → {path}")
        return

    if not path.exists():
        sys.exit(f"Chưa có {path}")
    problems = diff(json.load(open(path, encoding="utf-8")), manifest)
    if problems:
        sys.exit(f"{a.ver} KHÔNG khớp manifest:\n  " + "\n  ".join(problems))
    print(f"{a.ver} khớp manifest ({len(manifest['files'])} file"
          f"{', có vectors' if a.vectors else ''})")


if __name__ == "__main__":
    main()
