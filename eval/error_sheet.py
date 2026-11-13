"""Bảng phân tích lỗi một run (mặc định B4 test) ra Excel, mỗi câu một dòng, một mã lỗi chính.

    PYTHONPATH=. python -m eval.error_sheet runs/B4_v1_test_20261107-1335 --ng-run runs/B4ng_v1_test_20261107-1335 \
        --bench benchmark/benchmark_v1.1.jsonl --ragas results/ragas/B4_v1_test_20261107-1335__j1.csv \
        --per-question results/review/per_question_v1.1_test.csv \
        --manual results/review/manual30_B4_v1_test_20261107-1335.csv \
        --include $(cat results/review/error_include_qids.txt) \
        [--draft results/review/error_draft_B4_v1.1_test.csv] --out results/review/error_analysis_B4_v1.1_test.xlsx

Chọn câu (tối đa --max, mặc định 40, chỉ câu answerable):
  1. --include (danh sách định sẵn);  2. câu manual30 có error_code;
  3. bổ sung tự động theo cờ của run chính: F từ chối nhầm, R evidence ngoài top-5, N khớp số < 1, A answer_correctness < 0,5.
     Nhiều cờ xếp trước; câu manual30 đã chấm "không lỗi" không bổ sung tự động.
Câu bị ngưỡng chặn ở run chính (gated) thì kèm câu trả lời của --ng-run (cùng truy xuất, không ngưỡng).
Mã lỗi: R1 truy xuất trượt, R2 lọc nhầm sản phẩm, P1 bảng parse sai, G1 sinh sai/bịa số hay kết luận, G2 trích dẫn sai,
F1 từ chối nhầm, D1 lỗi benchmark, OK không lỗi. `code` từ manual30 giữ nguyên (code_src = manual30, kể cả "không lỗi");
--draft (qid, code, note) điền cho câu chưa có, code_src = draft (Claude soạn; trạng thái duyệt ghi trong docs).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

CODES = {"R1": "truy xuất trượt", "R2": "lọc nhầm sản phẩm", "P1": "bảng parse sai", "G1": "sinh sai/bịa số, sai kết luận",
         "G2": "trích dẫn sai", "F1": "từ chối nhầm", "D1": "lỗi benchmark", "OK": "không lỗi"}


def jsonl(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(x) for x in fh if x.strip()]


def as_list(v):
    if isinstance(v, list):
        return v
    if v in (None, "", "[]"):
        return []
    import ast
    return ast.literal_eval(v)


def truthy(v) -> bool:
    return str(v).strip().lower() in ("1", "true", "1.0")


def fnum(v):
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(x) else x


def load_log(run_dir: Path) -> dict[str, dict]:
    return {r["qid"]: r for r in jsonl(run_dir / "log.jsonl")}


def top5(log: dict, ev: set[str]) -> str:
    return "\n".join(f"[{i}] {c}{' *' if c in ev else ''}" for i, c in enumerate(as_list(log.get("contexts")), 1))


def cites(log: dict, ev: set[str]) -> str:
    ctx = as_list(log.get("contexts"))
    out = []
    for c in as_list(log.get("citations")):
        pos = ctx.index(c) + 1 if c in ctx else "?"
        out.append(f"[{pos}] {c}{' *' if c in ev else ''}")
    out += [f"(không hợp lệ) {c}" for c in as_list(log.get("citations_invalid"))]
    return "\n".join(out)


def select(bench, pq, manual, include, ragas, max_n, run_qids):
    ans = {q for q, b in bench.items()
           if q in run_qids and b.get("answerable", True) and b["group"] != "out_of_scope"}
    chosen: dict[str, str] = {}
    for q in include:
        if q not in bench or q not in run_qids:
            raise SystemExit(f"--include: {q} không có trong benchmark hoặc log run")
        chosen.setdefault(q, "include")
    for q, m in manual.items():
        if m["error_code"]:
            chosen.setdefault(q, "manual30")
    flags = {}
    for q in sorted(ans):
        p = pq.get(q, {})
        f = ""
        f += "F" if truthy(p.get("ref_B4")) else ""
        f += "R" if (fnum(p.get("rank_B4")) or 99) > 5 else ""
        f += "N" if fnum(p.get("num_B4")) is not None and fnum(p.get("num_B4")) < 1 else ""
        f += "A" if (fnum(ragas.get(q, {}).get("answer_correctness")) or 1) < 0.5 else ""
        flags[q] = f
    pool = [q for q in ans if flags[q] and q not in chosen and not (q in manual and not manual[q]["error_code"])]
    pool.sort(key=lambda q: (-len(flags[q]), q))
    for q in pool[:max(0, max_n - len(chosen))]:
        chosen[q] = f"auto:{flags[q]}"
    if len(chosen) > max_n:
        raise SystemExit(f"include + manual30 = {len(chosen)} câu > --max {max_n}")
    return chosen, flags


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run", type=Path)
    ap.add_argument("--ng-run", type=Path, required=True)
    ap.add_argument("--bench", type=Path, required=True)
    ap.add_argument("--ragas", type=Path, required=True)
    ap.add_argument("--per-question", type=Path, required=True)
    ap.add_argument("--manual", type=Path, required=True)
    ap.add_argument("--include", nargs="*", default=[])
    ap.add_argument("--draft", type=Path, help="CSV qid,code,note (nháp) cho câu chưa có code manual30")
    ap.add_argument("--chunks", type=Path, default=Path("data/processed/v1/chunks.jsonl"))
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)

    bench = {b["qid"]: b for b in jsonl(a.bench)}
    chunks = {c["chunk_id"]: c["text"] for c in jsonl(a.chunks)}
    pq = {r["qid"]: r for r in csv.DictReader(open(a.per_question, encoding="utf-8-sig"))}
    manual = {r["qid"]: r for r in csv.DictReader(open(a.manual, encoding="utf-8"))}
    ragas = {}
    for r in csv.DictReader(open(a.ragas, encoding="utf-8")):
        if not (r.get("error") or "").strip():
            ragas[r["qid"]] = r
    draft = {}
    if a.draft and a.draft.exists():
        draft = {r["qid"]: r for r in csv.DictReader(open(a.draft, encoding="utf-8"))}
    main_log, ng_log = load_log(a.run), load_log(a.ng_run)

    chosen, flags = select(bench, pq, manual, a.include, ragas, a.max, set(main_log))
    cols = ["qid", "group", "difficulty", "source", "flags", "question", "gold_answer", "evidence_ids", "evidence_text",
            "rank_B4", "top5_B4", "refused_B4", "gated_B4", "answer_B4", "cites_B4", "answer_B4ng", "cites_B4ng",
            "num_B4", "num_B4ng", "faith_j1", "ac_j1", "manual_correct", "manual_faithful", "code", "code_src", "note"]
    rows = []
    for q in sorted(chosen):
        b, p, L, N = bench[q], pq.get(q, {}), main_log[q], ng_log[q]
        ev = set(b["evidence_ids"])
        m, d = manual.get(q), draft.get(q)
        gated = truthy(L.get("gated"))
        if m:
            code, src = (m["error_code"] or "OK"), "manual30"
            note = (d or {}).get("note", "") if d else ""
            if m["run_id"].startswith("B4ng"):
                note = ("manual30 chấm câu trả lời B4ng. " + note).strip()
        elif d:
            code, src, note = d["code"], "draft", d.get("note", "")
        else:
            code, src, note = "", "", ""
        rg = ragas.get(q, {})
        rows.append({
            "qid": q, "group": b["group"], "difficulty": b.get("difficulty", ""), "source": chosen[q], "flags": flags.get(q, ""),
            "question": b["question"], "gold_answer": b["answer"], "evidence_ids": "\n".join(b["evidence_ids"]),
            "evidence_text": "\n\n".join(f"[{e}]\n{chunks.get(e, '(không có chunk)')[:1500]}" for e in b["evidence_ids"]),
            "rank_B4": p.get("rank_B4", ""), "top5_B4": top5(L, ev), "refused_B4": truthy(L.get("refused")), "gated_B4": gated,
            "answer_B4": L["answer"], "cites_B4": cites(L, ev),
            "answer_B4ng": N["answer"] if (gated or N["answer"] != L["answer"]) else "(giống B4)",
            "cites_B4ng": cites(N, ev) if (gated or N["answer"] != L["answer"]) else "",
            "num_B4": p.get("num_B4", ""), "num_B4ng": p.get("num_B4ng", ""),
            "faith_j1": fnum(rg.get("faithfulness")), "ac_j1": fnum(rg.get("answer_correctness")),
            "manual_correct": m["correct"] if m else "", "manual_faithful": m["faithful"] if m else "",
            "code": code, "code_src": src, "note": note})

    wb = Workbook()
    ws = wb.active
    ws.title = "errors"
    ws.append(cols)
    for r in rows:
        ws.append([r[c] for c in cols])
    for c in ws[1]:
        c.font = Font(bold=True)
    widths = {"question": 50, "gold_answer": 50, "evidence_text": 70, "answer_B4": 60, "answer_B4ng": 50, "top5_B4": 30,
              "cites_B4": 30, "cites_B4ng": 30, "note": 60, "evidence_ids": 22}
    for i, c in enumerate(cols, 1):
        ws.column_dimensions[ws.cell(1, i).column_letter].width = widths.get(c, 11)
    lock = PatternFill("solid", fgColor="DDEBF7")
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(wrap_text=True, vertical="top")
        if row[cols.index("code_src")].value == "manual30":
            row[cols.index("code")].fill = lock
    ws.freeze_panes = "B2"
    lg = wb.create_sheet("legend")
    lg.append(["code", "ý nghĩa"])
    for k, v in CODES.items():
        lg.append([k, v])
    lg.append([])
    lg.append(["source", "include = --include; manual30 = có mã trong manual30; auto:<cờ> = bổ sung tự động"])
    lg.append(["flags", "F từ chối nhầm, R evidence ngoài top-5, N khớp số < 1, A answer_correctness j1 < 0,5"])
    lg.append(["top5/cites", "[n] = vị trí trong ngữ cảnh; * = thuộc evidence_ids"])
    lg.append(["code_src", "manual30 = HA đã chốt (ô xanh, không sửa); draft = Claude soạn (--draft), trạng thái duyệt xem docs/results_w8.md"])
    a.out.parent.mkdir(parents=True, exist_ok=True)
    wb.save(a.out)

    from collections import Counter
    print(f"{len(rows)} câu → {a.out}")
    print("nguồn:", dict(Counter(r["source"].split(":")[0] for r in rows)))
    print("chưa có code:", [r["qid"] for r in rows if not r["code"]])


if __name__ == "__main__":
    main()
