"""Sinh docs/results_summary.md từ kết quả test (benchmark v1.1): mọi số lấy từ file, không gõ tay.

    PYTHONPATH=. python scripts/build_results_summary.py            # ghi docs/results_summary.md
    PYTHONPATH=. python scripts/build_results_summary.py --stdout   # chỉ in ra để xem

Nguồn: bảng 1 và 1' từ eval.summary (RUNS); bảng 2 tính hiệu từ chính các CSV đó; bảng 2' từ
results/review/mcnemar_v1.1_test.txt (eval.mcnemar); MRR Wilcoxon từ results/review/paired_tests_v1.1_test.txt.
Có cột Ragas (sau eval.ragas_summary) thì tự thêm vào bảng 2 và mục "Đọc nhanh". Chạy lại mỗi khi CSV đổi.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import io
import re
from pathlib import Path

from eval import summary as S

MCN = Path("results/review/mcnemar_v1.1_test.txt")
PAIRED = Path("results/review/paired_tests_v1.1_test.txt")
OUT = Path("docs/results_summary.md")
MANUAL_CITE = (24, 30)          # manual30: cite_ok đúng / tổng (B4 test)
STEPS = [("Chunk cấu trúc (RQ1)", "B1", "B2"), ("Hybrid", "B2", "B3hyb"), ("Query processor", "B3hyb", "B3"),
         ("Rerank", "B3", "B4rr"), ("Prompt rag_v3", "B4rr", "B4ng"), ("Ngưỡng 0,90", "B4ng", "B4"), ("Tổng", "B2", "B4")]
STEP_COLS = [("recall@1", "R@1"), ("recall@5", "R@5"), ("mrr", "MRR"), ("false_refusal", "Từ chối nhầm"),
             ("cite_rate", "Có trích dẫn"), ("num_recall", "Khớp số"), ("faithfulness_j1", "Faithfulness (j1)"),
             ("answer_correctness_j1", "Ans. corr. (j1)"), ("answer_relevancy_j1x", "Ans. rel. (j1x)"),
             ("context_precision_j1x", "Ctx prec. (j1x)"), ("context_recall_j1x", "Ctx recall (j1x)"), ("p95_s", "p95 (s)")]


def f(x, d=3):
    return "–" if x in ("", None) else f"{float(x):.{d}f}".replace(".", ",")


def sd(x, d=3):
    if x is None:
        return "–"
    s = f"{x:+.{d}f}".replace(".", ",").replace("-", "−")
    return "0" if float(x) == 0 else s


def load_all():
    return {n: S.load(p) for n, _, p, _ in S.RUNS}


def num(d, cfg, col, g="all"):
    v = d[cfg].get(g, {}).get(col)
    return None if v in ("", None) else float(v)


def mcnemar_rows():
    rows, holm = [], {}
    for line in MCN.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("| ---") or line.startswith("| metric"):
            continue
        c = [x.strip() for x in line.strip("|").split("|")]
        holm[(c[0], c[1])] = (c[7], c[8], c[5], c[6])        # p, p Holm, chỉ A, chỉ B
        c = [re.sub(r"^(\d+)\.(\d+)$", r"\1,\2", x) for x in c]
        rows.append("| " + " | ".join(c) + " |")
    return rows, holm


def paired_mrr():
    out = {}
    if PAIRED.exists():
        for line in PAIRED.read_text(encoding="utf-8").splitlines():
            m = re.match(r"\s*(\S+)\s+rr \(MRR\)\s+\d+\s+\S+\s+\S+\s+\d+\s+\d+\s+(\S+)", line)
            if m:
                out[m.group(1)] = m.group(2)
    return out


def targets(d):
    met, miss = [], []
    for col, t in S.TARGET.items():
        if col == "cite_prec":
            continue
        op, val = t[0], float(t[1:].strip().rstrip("*").replace(",", "."))
        v = num(d, "B4", col)
        if v is None:
            continue
        ok = v >= val if op == "≥" else v <= val
        (met if ok else miss).append(f"{dict(S.ALL_COLS).get(col, col)} {f(v, 2 if col == 'p95_s' else 3)}")
    ok = MANUAL_CITE[0] / MANUAL_CITE[1] >= 0.85
    (met if ok else miss).append(f"trích dẫn đúng (kiểm tay) {f(MANUAL_CITE[0] / MANUAL_CITE[1])}")
    return met, miss


def build() -> str:
    d = load_all()
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        S.main()
    t1 = buf.getvalue().replace("## Bảng A. Test, dòng all", "## Bảng 1. Test, dòng all")
    t1 = re.sub(r"## Bảng (.+?) theo nhóm", r"## Bảng 1'. \1 theo nhóm", t1)
    t1 = t1.replace("## Từ chối đúng (out_of_scope", "## Bảng 1'. Từ chối đúng (out_of_scope")
    mrows, holm = mcnemar_rows()
    wil = paired_mrr()
    H = lambda m, a, b: tuple(x.replace(".", ",") for x in holm.get((m, f"{a} → {b}"), ("–",) * 4))
    has_ragas = num(d, "B4", "answer_correctness_j1") is not None
    has_j1x = num(d, "B4", "answer_relevancy_j1x") is not None
    cols = [(c, h) for c, h in STEP_COLS
            if (has_ragas or not c.endswith("_j1")) and (has_j1x or not c.endswith("_j1x"))]

    step_rows = []
    for name, a, b in STEPS:
        cells = [sd(None if num(d, a, c) is None or num(d, b, c) is None else num(d, b, c) - num(d, a, c),
                    2 if c == "p95_s" else 3) for c, _ in cols]
        step_rows.append(f"| {name} | {a} → {b} | " + " | ".join(cells) + " |")

    sc = {n: num(d, n, "recall@5", "scenario") for n in d}
    met, miss = targets(d)
    n_ans = 96
    gate_extra = round((num(d, "B4", "false_refusal") - num(d, "B4ng", "false_refusal")) * n_ans)
    L = []
    L += ["# Bảng tổng kết quả B0–B4 (test)", "",
          "Benchmark **v1.1** test (120 câu: 96 answerable, 24 out_of_scope, 24 câu/nhóm), dữ liệu `processed/v1`, Colab L4,",
          "Qwen2.5 7B q4 (num_ctx 8192, seed 42). Log là các run chính thức chạy với v1 (07/11); metric tính lại theo v1.1",
          "(`eval.metrics --bench benchmark/benchmark_v1.1.jsonl`): 7 câu sửa evidence, 2 câu sửa đáp án chuẩn, câu hỏi giữ",
          "nguyên (`benchmark/CHANGELOG.md`). Số theo v1: `results/archive_v1/`. Danh sách run: `configs/test_runs_official.txt`.",
          "File này sinh bằng `PYTHONPATH=. python scripts/build_results_summary.py`; đừng sửa số bằng tay.",
          "Chi tiết từng bước: `docs/results_w4_baseline.md` (B0–B2), `docs/results_w5_b3.md` (B3), `docs/results_w6_b4.md` (B4),",
          "`docs/results_w8.md` (judge Ragas, kiểm định, phân tích lỗi).", "",
          "| Cấu hình | Run test | Truy xuất | Prompt | Rerank / ngưỡng |", "| --- | --- | --- | --- | --- |",
          "| B0 | `B0_v1_test_20261107-0904` | không | norag_v1 | – |",
          "| B1 | `B1_v1_test_20261107-0904` | dense, chunk cố định 512 (chấm qua căn chỉnh, ngưỡng 0,3) | rag_v1 | – |",
          "| B2 | `B2_v1_test_20261107-0904` | dense, chunk cấu trúc | rag_v1 | – |",
          "| B3hyb (ablation) | `B3hyb_v1_test_20261107-1020` | hybrid RRF, không lọc | rag_v1 | – |",
          "| B3 | `B3_v1_test_20261107-1020` | hybrid + query processor | rag_v1 | – |",
          "| B4rr (ablation) | `B4rr_v1_test_20261107-1335` | như B3 | rag_v1 | rerank, không chặn |",
          "| B4ng (ablation) | `B4ng_v1_test_20261107-1335` | như B3 | rag_v3 | rerank, không chặn |",
          "| B4 | `B4_v1_test_20261107-1335` | như B3 | rag_v3 | rerank, min_score 0,90 |", ""]
    L += [t1.rstrip(), "",
          f"\\* Cận dưới tự động: chỉ tính trích dẫn trỏ đúng `evidence_ids`. \\*\\* Kiểm tay 30 câu B4 (manual30): "
          f"trích dẫn đúng {MANUAL_CITE[0]}/{MANUAL_CITE[1]} = {f(MANUAL_CITE[0] / MANUAL_CITE[1])}.",
          "Mục tiêu B4 đề xuất 07/11, GVHD xác nhận 14/11 (decision-log)."]
    if has_ragas:
        L += ["Ragas (judge j1, `results/ragas/`): chỉ chấm câu answerable không bị từ chối (số câu: cột `n_ragas_j1` trong CSV);",
              "B0 không có ngữ cảnh nên không có faithfulness. Hiệu chỉnh judge với 30 câu chấm tay: `docs/results_w8.md`."]
    if has_j1x:
        L += ["Ragas bổ sung (judge j1x = j1 + embedding `gemini-embedding-001`, `eval/ragas_extra.py`): answer relevancy trên câu",
              "answerable không bị từ chối (cột `n_rel_j1x`); context precision/recall trên mọi câu answerable (96, kể cả bị từ",
              "chối). B4rr/B4ng/B4 cùng contexts từng câu nên chung một điểm context. Chưa hiệu chỉnh bằng nhãn tay."]
    L += ["", "## Bảng 2. Đóng góp từng bước (test, dòng all; trên 96 câu answerable: 0,010 ≈ 1 câu)", "",
          "| Bước | So sánh | " + " | ".join(h for _, h in cols) + " |",
          "| --- | --- |" + " --- |" * len(cols), *step_rows, "",
          "Bảng 2' cho biết bước nào có ý nghĩa thống kê; chênh lệch 1–2 câu không đủ để kết luận.", "",
          "## Bảng 2'. Kiểm định McNemar theo cặp câu (v1.1; Holm hiệu chỉnh trong từng metric qua 6 bước; "
          "dòng B2 → B4 không hiệu chỉnh)", "",
          "| metric | A → B | n | A | B | chỉ A | chỉ B | p | p Holm | ý nghĩa |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |", *mrows, "",
          f"Nguồn: `eval/mcnemar.py --benchmark benchmark/benchmark_v1.1.jsonl` (`{MCN.with_suffix('.csv')}`); "
          "bản v1: `results/archive_v1/mcnemar_v1_test_20261109.csv`. \"Chỉ A / chỉ B\": số câu chỉ cấu hình A / chỉ B đạt; "
          "num_all: câu có số trong đáp án chuẩn (n = 63) và nêu đủ số."]
    if wil:
        L += [f"MRR, Wilcoxon theo cặp câu (`eval/paired_tests.py`): B1 → B2 p {f(wil.get('B1:B2'), 4)}; "
              f"B3 → B4rr p {f(wil.get('B3:B4rr'), 4)}."]

    h1 = H("hit1", "B1", "B2"); n1 = H("num_all", "B1", "B2"); h5 = H("hit5", "B1", "B2")
    r1 = H("hit1", "B3", "B4rr"); nv3 = H("num_all", "B4rr", "B4ng"); g = H("false_refusal", "B4ng", "B4")
    dd = lambda a, b, c: sd(num(d, b, c) - num(d, a, c))
    L += ["", "## Đọc nhanh", "",
          f"1. Bước lớn nhất về truy xuất là chunk theo cấu trúc (RQ1: Recall@5 {dd('B1', 'B2', 'recall@5')}, "
          f"MRR {dd('B1', 'B2', 'mrr')}); sau Holm có ý nghĩa ở Hit@1 (p Holm {h1[1]}) và khớp đủ số ({n1[1]}), "
          f"Recall@5 thì không ({h5[1]}).",
          f"2. Rerank đóng góp cho thứ hạng (Recall@1 {dd('B3', 'B4rr', 'recall@1')}, p Holm {r1[1]}; "
          f"MRR {dd('B3', 'B4rr', 'mrr')}) nhưng không tìm thêm evidence: Recall@5 {dd('B3', 'B4rr', 'recall@5')}, "
          f"scenario {f(sc['B3'])} → {f(sc['B4rr'])}.",
          f"3. Prompt rag_v3 (trích dẫn [n]): có trích dẫn {f(num(d, 'B4rr', 'cite_rate'))} → {f(num(d, 'B4ng', 'cite_rate'))}, "
          f"từ chối nhầm {dd('B4rr', 'B4ng', 'false_refusal')}; đổi lại khớp đủ số giảm "
          f"(chỉ B4rr {nv3[2]} câu, chỉ B4ng {nv3[3]} câu; p {nv3[0]}, Holm {nv3[1]}).",
          f"4. Ngưỡng 0,90 không thêm từ chối đúng trên test (đã 1,000 từ B1) mà tăng từ chối nhầm {gate_extra} câu "
          f"(p Holm {g[1]}); lợi ích chỉ ở độ trễ, giờ GPU và hedge "
          f"({f(num(d, 'B4ng', 'hedge_rate'))} → {f(num(d, 'B4', 'hedge_rate'))}, chưa kiểm định).",
          "5. Hybrid, query processor, prompt rag_v3 và ngưỡng 0,90 không phân biệt được với n = 96 (bảng 2'); "
          "câu out_of_scope được từ chối đúng 100% ở mọi cấu hình có RAG nên RQ3 chưa phân biệt được.",
          f"6. Nhóm khó nhất xuyên suốt là scenario: Recall@5 tối đa {f(max(v for v in sc.values() if v is not None))}, "
          f"từ chối nhầm B4 {f(num(d, 'B4', 'false_refusal', 'scenario'))}, khớp số B4 {f(num(d, 'B4', 'num_recall', 'scenario'))}.",
          f"7. B4 đạt {len(met)}/{len(met) + len(miss)} mục tiêu ({'; '.join(met)}); chưa đạt: {'; '.join(miss)}."]
    if has_ragas:
        L += [f"8. Ragas (j1): B4 faithfulness {f(num(d, 'B4', 'faithfulness_j1'))}, answer correctness "
              f"{f(num(d, 'B4', 'answer_correctness_j1'))}; B0 answer correctness {f(num(d, 'B0', 'answer_correctness_j1'))}."]
    if has_j1x:
        L += [f"9. Ragas bổ sung (j1x): context recall B1 {f(num(d, 'B1', 'context_recall_j1x'))} → B2 "
              f"{f(num(d, 'B2', 'context_recall_j1x'))} → B4 {f(num(d, 'B4', 'context_recall_j1x'))} (cùng chiều Recall@5); "
              f"answer relevancy B4 {f(num(d, 'B4', 'answer_relevancy_j1x'))}, tỷ lệ noncommittal "
              f"{f(num(d, 'B4', 'noncommittal_j1x'))}. Kiểm định: `docs/results_w8.md` mục 7."]
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stdout", action="store_true")
    a = ap.parse_args()
    text = build()
    if a.stdout:
        print(text)
    else:
        OUT.write_text(text, encoding="utf-8")
        print(f"→ {OUT}")
