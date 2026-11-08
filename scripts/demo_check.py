"""Chạy kịch bản demo (app/demo_script.yaml) qua API đang chạy, ghi bản chép hội thoại Markdown + JSONL.

Dùng trên Colab sau khi API sẵn sàng: kiểm demo trước buổi bảo vệ và làm bản dự phòng (cùng video quay màn hình).
    python scripts/demo_check.py --api http://localhost:8000 --out $DRIVE_DIR/runs/demo/demo_<stamp>
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import requests

NUM_CITE = re.compile(r"\[\s*\d{1,2}(?:\s*[,;]\s*\d{1,2})*\s*\]")


def transcript(items: list[dict]) -> str:
    out = ["# Kịch bản demo: bản chép", ""]
    for q, r in items:
        status = "TỪ CHỐI" + (" (ngưỡng)" if r["gated"] else "") if r["refused"] else "trả lời"
        exp = "từ chối" if not q["answerable"] else "trả lời"
        out += [f"## {q['label']} ({q['qid']}, {q['group']}): {status}, kỳ vọng {exp}", "",
                f"**Hỏi:** {q['question']}", "", f"**Đáp:** {r['answer']}", ""]
        for s in r["sources"]:
            mark = "x" if s["cited"] else " "
            out.append(f"- [{mark}] [{s['n']}] {s['product_name']} · {s['doc_label']} · {s['section']} · tr. {s['page']}"
                       f" (`{s['chunk_id']}`)")
        flags = [f"số không có trong nguồn {r['nums_unsupported']}"] if r["nums_unsupported"] else []
        flags += [f"trích dẫn sai {r['citations_invalid']}"] if r["citations_invalid"] else []
        out += ["", f"_{r['latency_ms'] / 1000:.1f} s · rerank max {r.get('rerank_max')} · sản phẩm "
                    f"{r['products_detected']}{' · ' + '; '.join(flags) if flags else ''}_", ""]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="http://localhost:8000")
    ap.add_argument("--out", required=True, help="tiền tố file ra: <out>.md, <out>.jsonl")
    a = ap.parse_args(argv)
    api = a.api.rstrip("/")
    qs = requests.get(f"{api}/demo-questions", timeout=10).json()
    items = []
    for q in qs:
        r = requests.post(f"{api}/ask", json={"question": q["question"]}, timeout=300)
        r.raise_for_status()
        items.append((q, r.json()))
        ok = r.json()["refused"] != q["answerable"]
        print(f"{q['qid']} {q['label']:15s} {'đúng hành vi' if ok else 'SAI hành vi'} "
              f"{'từ chối' if r.json()['refused'] else 'trả lời'} {r.json()['latency_ms'] / 1000:.1f} s", flush=True)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".md").write_text(transcript(items), encoding="utf-8")
    with open(out.with_suffix(".jsonl"), "w", encoding="utf-8") as f:
        for q, r in items:
            f.write(json.dumps({"qid": q["qid"], **r}, ensure_ascii=False) + "\n")
    print(f"Ghi {out}.md, {out}.jsonl")


if __name__ == "__main__":
    main()
