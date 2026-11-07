"""Schema và kiểm tra benchmark (benchmark/benchmark_vN.jsonl); dùng chung cho bước soạn và harness đánh giá.

    PYTHONPATH=. python -m eval.benchmark benchmark/benchmark_v1.jsonl --processed data/processed/v1 [--final]
"""
import argparse, json, re, sys
from collections import Counter
from pathlib import Path

from src.ingest.catalog import numbers

GROUPS = ("lookup", "table", "compare", "scenario", "out_of_scope")
DIFFICULTIES = ("easy", "medium", "hard")
SPLITS = ("dev", "test")
FIELDS = ("qid", "question", "answer", "evidence_ids", "products", "group", "difficulty", "answerable",
          "split", "created_by", "version")
NUMBER_STRICT = {"lookup", "table", "compare"}   # số trong đáp án phải có trong evidence; scenario chỉ cảnh báo
TARGET = {"per_group": 30, "dev_per_group": 6}   # benchmark v1: 150 câu, dev 30


def read_jsonl(path) -> list[dict]:
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def load_chunks(processed: Path) -> dict[str, dict]:
    return {c["chunk_id"]: c for c in read_jsonl(processed / "chunks.jsonl")}


def missing_numbers(answer: str, evidence_texts: list[str]) -> list[str]:
    have = set()
    for t in evidence_texts:
        have.update(numbers(t))
    return [n for n in numbers(answer) if n not in have]


def validate(rows: list[dict], chunks: dict[str, dict], refusal: str, final: bool = False) -> tuple[list[str], list[str]]:
    """Trả (lỗi, cảnh báo). final=True: bắt buộc đúng phân bố v1 (30/nhóm, dev 6/nhóm)."""
    errors, warnings = [], []
    qids, questions = Counter(r.get("qid") for r in rows), Counter(r.get("question", "").strip().lower() for r in rows)
    for r in rows:
        q = r.get("qid", "?")
        miss = [f for f in FIELDS if f not in r]
        if miss:
            errors.append(f"{q}: thiếu trường {miss}")
            continue
        if not re.fullmatch(r"v\d+-\d{4}", q) or qids[q] > 1:
            errors.append(f"{q}: qid sai dạng hoặc trùng")
        if questions[r["question"].strip().lower()] > 1:
            errors.append(f"{q}: câu hỏi trùng nguyên văn")
        if r["group"] not in GROUPS or r["difficulty"] not in DIFFICULTIES or r["split"] not in SPLITS:
            errors.append(f"{q}: group/difficulty/split ngoài tập cho phép")
        if not r["question"].strip() or not r["answer"].strip():
            errors.append(f"{q}: câu hỏi hoặc đáp án rỗng")
        if not r["answerable"]:
            if r["evidence_ids"] or r["answer"] != refusal or r["group"] != "out_of_scope":
                errors.append(f"{q}: answerable=false phải có evidence_ids=[], đáp án từ chối chuẩn, group out_of_scope")
            continue
        if r["group"] == "out_of_scope":
            errors.append(f"{q}: out_of_scope phải answerable=false")
        if not r["evidence_ids"]:
            errors.append(f"{q}: answerable nhưng không có evidence_ids")
        bad = [e for e in r["evidence_ids"] if e not in chunks]
        if bad:
            errors.append(f"{q}: evidence không có trong kho {bad}")
            continue
        ev_products = {chunks[e]["product_code"] for e in r["evidence_ids"]}
        if not ev_products <= set(r["products"]):
            errors.append(f"{q}: products {r['products']} thiếu {sorted(ev_products - set(r['products']))}")
        if r["group"] == "compare" and len(ev_products) < 2:
            errors.append(f"{q}: compare cần evidence từ ≥ 2 sản phẩm")
        miss_n = missing_numbers(r["answer"], [chunks[e]["text"] for e in r["evidence_ids"]])
        if miss_n:
            (errors if r["group"] in NUMBER_STRICT else warnings).append(f"{q}: số {miss_n} trong đáp án không có trong evidence")
    if final:
        by = Counter(r["group"] for r in rows)
        dev = Counter(r["group"] for r in rows if r["split"] == "dev")
        for g in GROUPS:
            if by[g] != TARGET["per_group"] or dev[g] != TARGET["dev_per_group"]:
                errors.append(f"phân bố {g}: {by[g]} câu (cần {TARGET['per_group']}), dev {dev[g]} (cần {TARGET['dev_per_group']})")
    return errors, warnings


def summary(rows: list[dict]) -> str:
    out = []
    for key in ("group", "split", "difficulty"):
        out.append(f"{key}: {dict(sorted(Counter(r[key] for r in rows).items()))}")
    out.append(f"products: {dict(sorted(Counter(p for r in rows for p in r['products']).items()))}")
    dev = Counter(r["group"] for r in rows if r["split"] == "dev")
    out.append(f"dev theo nhóm: {dict(sorted(dev.items()))}")
    return "\n".join(out)


def main():
    import yaml
    ap = argparse.ArgumentParser()
    ap.add_argument("path", type=Path)
    ap.add_argument("--processed", type=Path, default=Path("data/processed/v1"))
    ap.add_argument("--config", type=Path, default=Path("benchmark/draft_config.yaml"))
    ap.add_argument("--final", action="store_true", help="kiểm phân bố v1 (30/nhóm, dev 6/nhóm)")
    a = ap.parse_args()
    rows = read_jsonl(a.path)
    refusal = yaml.safe_load(open(a.config, encoding="utf-8"))["refusal"]
    errors, warnings = validate(rows, load_chunks(a.processed), refusal, a.final)
    print(f"{len(rows)} câu\n{summary(rows)}")
    for w in warnings:
        print("  cảnh báo:", w)
    if errors:
        sys.exit("Lỗi:\n  " + "\n  ".join(errors))
    print("OK")


if __name__ == "__main__":
    main()
