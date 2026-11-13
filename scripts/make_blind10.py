"""Sinh file chấm mù lại một phần manual30 (đo độ nhất quán của người chấm, weighted kappa bằng eval/kappa.py).

    PYTHONPATH=. python scripts/make_blind10.py            # → results/review/blind10_B4_v1.1_test.xlsx + blind10_key.csv

Chọn --n câu (mặc định 10) từ phần main của manual30 (không lấy 4 câu gated B4ng), phân tầng theo nhóm
(lookup 2, table 2, compare 3, scenario 3) và bảo đảm ít nhất --low câu có điểm thấp (correct hoặc faithful ≤ 3);
phần còn lại chọn ngẫu nhiên, seed cố định. File chấm chỉ có mã M01…, thứ tự xáo; không có qid, điểm cũ, dx_*,
ghi chú hay Ragas. Khóa ghép mã → qid ghi riêng (--key): đừng mở trước khi chấm xong.
Script đọc điểm cũ chỉ để chọn câu, không in điểm ra màn hình. Không ghi đè file chấm đã có (dùng --force nếu chắc).

Ngữ cảnh hiển thị đúng top-5 mà model đã thấy (`<doc so="n">` theo `contexts` trong log), đáp án chuẩn theo benchmark v1.1.
"""
from __future__ import annotations

import argparse
import ast
import csv
import json
import random
import sys
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.datavalidation import DataValidation

QUOTA = {"lookup": 2, "table": 2, "compare": 3, "scenario": 3}
CODES = ["D1", "R2", "R1", "P1", "G1", "G2", "F1", "F2"]


def jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(x) for x in fh if x.strip()]


def as_list(v):
    return v if isinstance(v, list) else ([] if v in (None, "", "[]") else ast.literal_eval(v))


def select(rows: list[dict], quota: dict[str, int], n_low: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    low = [r for r in rows if min(int(r["correct"]), int(r["faithful"])) <= 3]
    rest = [r for r in rows if r not in low]
    rng.shuffle(low)
    rng.shuffle(rest)
    left, chosen = dict(quota), []
    for r in low:                                   # câu điểm thấp trước, vẫn giữ hạn mức nhóm
        if len(chosen) >= n_low:
            break
        if left.get(r["group"], 0) > 0:
            chosen.append(r)
            left[r["group"]] -= 1
    for r in rest + low:                            # lấp đủ hạn mức
        if r not in chosen and left.get(r["group"], 0) > 0:
            chosen.append(r)
            left[r["group"]] -= 1
    if any(left.values()):
        raise SystemExit(f"không đủ câu cho hạn mức nhóm: còn thiếu {left}")
    rng.shuffle(chosen)
    return chosen


def rules_rows(manual_xlsx: Path) -> list[tuple]:
    ws = load_workbook(manual_xlsx, read_only=True)["Quy tắc chấm"]
    out = []
    for r in ws.iter_rows(values_only=True):
        if r and r[0] in ("Cách dùng file",):
            break
        out.append(r)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--manual", type=Path, default=Path("results/review/manual30_B4_v1_test_20261107-1335.csv"))
    ap.add_argument("--manual-xlsx", type=Path, default=Path("results/review/manual30_B4_v1_test_20261107-1335.xlsx"),
                    help="chỉ lấy sheet 'Quy tắc chấm'")
    ap.add_argument("--bench", type=Path, default=Path("benchmark/benchmark_v1.1.jsonl"))
    ap.add_argument("--chunks", type=Path, default=Path("data/processed/v1/chunks.jsonl"))
    ap.add_argument("--runs-dir", type=Path, default=Path("runs"))
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--low", type=int, default=4, help="số câu tối thiểu có correct hoặc faithful ≤ 3")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, default=Path("results/review/blind10_B4_v1.1_test.xlsx"))
    ap.add_argument("--key", type=Path, default=Path("results/review/blind10_key.csv"))
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)

    for p in (a.out, a.key):
        if p.exists() and not a.force:
            sys.exit(f"{p} đã có (có thể đã chấm); dùng --force nếu thật sự muốn tạo lại")
    if sum(QUOTA.values()) != a.n:
        sys.exit(f"--n {a.n} khác tổng hạn mức nhóm {sum(QUOTA.values())}")

    manual = [r for r in csv.DictReader(open(a.manual, encoding="utf-8")) if r["part"] == "main"]
    bench = {b["qid"]: b for b in jsonl(a.bench)}
    chunks = {c["chunk_id"]: c["text"] for c in jsonl(a.chunks)}
    logs: dict[str, dict] = {}
    chosen = select(manual, QUOTA, a.low, a.seed)

    rows = []
    for i, m in enumerate(chosen, 1):
        run = m["run_id"]
        if run not in logs:
            logs[run] = {r["qid"]: r for r in jsonl(a.runs_dir / run / "log.jsonl")}
        L, b = logs[run][m["qid"]], bench[m["qid"]]
        ctx = as_list(L.get("contexts"))
        context = "\n\n".join(f"[{k}]\n{chunks.get(c, '(không có chunk)')}" for k, c in enumerate(ctx, 1))
        cited = [f"[{ctx.index(c) + 1}]" if c in ctx else f"(ngoài ngữ cảnh) {c}" for c in as_list(L.get("citations"))]
        cited += [f"(không hợp lệ) {c}" for c in as_list(L.get("citations_invalid"))]
        rows.append({"code": f"M{i:02d}", "qid": m["qid"], "run_id": run, "group": b["group"],
                     "question": b["question"], "ref_answer": b["answer"], "answer": L["answer"],
                     "cited": " ".join(cited), "cite_total": len(cited), "context_top5": context})

    wb = Workbook()
    ws = wb.active
    ws.title = "Chấm mù"
    cols = ["code", "group", "question", "ref_answer", "answer", "cited", "cite_total",
            "correct_1_5", "faithful_1_5", "cite_ok", "error_code", "note", "context_top5"]
    ws.append(cols)
    for r in rows:
        ws.append([r.get(c, "") for c in cols])
    widths = {"question": 45, "ref_answer": 45, "answer": 60, "cited": 14, "context_top5": 100, "note": 30}
    blank = PatternFill("solid", fgColor="FFF2CC")
    for i, c in enumerate(cols, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = widths.get(c, 11)
        ws.cell(1, i).font = Font(bold=True)
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
        for c in ("correct_1_5", "faithful_1_5", "cite_ok", "error_code", "note"):
            row[cols.index(c)].fill = blank
    last = len(rows) + 1
    col = lambda name: ws.cell(1, cols.index(name) + 1).column_letter
    for name, formula in (("correct_1_5", '"1,2,3,4,5"'), ("faithful_1_5", '"1,2,3,4,5"'), ("cite_ok", '"0,1"'),
                          ("error_code", '"' + ",".join(CODES) + '"')):
        dv = DataValidation(type="list", formula1=formula, allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"{col(name)}2:{col(name)}{last}")
    ws.freeze_panes = "C2"

    rs = wb.create_sheet("Quy tắc chấm")
    for r in rules_rows(a.manual_xlsx):
        rs.append(list(r))
    rs.append([])
    rs.append(["Chấm mù", "Không mở manual30 cũ, không hỏi LLM trong lúc chấm",
               "correct: so với ref_answer, không nhìn context; faithful: so với context_top5, không so với ref. "
               "cite_ok: 1 nếu đoạn gánh ý chính chứa đúng thông tin, 0 nếu không (theo quy tắc ở trên). "
               "error_code: để trống nếu không lỗi."])
    for c in ("A", "B", "C"):
        rs.column_dimensions[c].width = {"A": 18, "B": 50, "C": 90}[c]
    for row in rs.iter_rows():
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(a.out)
    with open(a.key, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["code", "qid", "run_id"], lineterminator="\n")
        w.writeheader()
        w.writerows({k: r[k] for k in ("code", "qid", "run_id")} for r in rows)
    from collections import Counter
    print(f"{len(rows)} câu → {a.out} (khóa: {a.key}, đừng mở trước khi chấm xong)")
    print("theo nhóm:", dict(Counter(r["group"] for r in rows)))


if __name__ == "__main__":
    main()
