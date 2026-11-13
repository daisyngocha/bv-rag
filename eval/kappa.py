"""Độ nhất quán chấm tay: so điểm chấm mù (scripts/make_blind10.py) với điểm chốt manual30, tùy chọn với đề xuất dx_*.

    PYTHONPATH=. python -m eval.kappa                                   # mặc định đường dẫn tuần 8
    PYTHONPATH=. python -m eval.kappa --dx results/review/manual30_B4_v1_test_20261107-1335.xlsx \
        --out results/review/kappa_blind10.md

correct, faithful (thang 1–5, có thứ bậc): weighted kappa trọng số bậc hai, trùng chính xác, lệch ≤ 1.
error_code (danh định, trống = OK), cite_ok (0/1): Cohen kappa thường, trùng chính xác.
CI95 bootstrap theo câu (mặc định 2.000 lần, bỏ mẫu kappa không xác định). n nhỏ nên chỉ là số tham khảo.
--dx: thêm so sánh chấm mù với điểm đề xuất dx_* (sheet Review) để xem lần chấm đầu có bị neo theo đề xuất không.
"""
from __future__ import annotations

import argparse
import csv
import math
import random
import sys
from pathlib import Path

from openpyxl import load_workbook
from sklearn.metrics import cohen_kappa_score

SCALE = [1, 2, 3, 4, 5]
FIELDS = {  # tên cột chấm mù → (cột manual30 csv, cột dx_* trong xlsx, loại)
    "correct_1_5": ("correct", "dx_correct", "ordinal"),
    "faithful_1_5": ("faithful", "dx_faithful", "ordinal"),
    "cite_ok": ("cite_ok", "dx_cite_ok", "nominal"),
    "error_code": ("error_code", "dx_error_code", "nominal"),
}


def norm(v, kind):
    if kind == "ordinal":
        return int(float(v))
    if v in (None, "") or str(v).strip() in ("", "-", "OK"):
        return "OK"
    s = str(v).strip()
    try:
        return str(int(float(s)))                   # cite_ok 1 / 1.0 / "1"
    except ValueError:
        return s.split()[0].upper()                 # "P1 → G1" giữ mã đầu như manual30


def kappa(a, b, kind):
    if len(set(a) | set(b)) < 2:
        return float("nan")                         # chỉ một nhãn: kappa không xác định
    if kind == "ordinal":
        return cohen_kappa_score(a, b, weights="quadratic", labels=SCALE)
    return cohen_kappa_score(a, b)


def boot_ci(a, b, kind, n_boot, seed):
    rng = random.Random(seed)
    idx, vals = range(len(a)), []
    for _ in range(n_boot):
        s = [rng.choice(idx) for _ in idx]
        k = kappa([a[i] for i in s], [b[i] for i in s], kind)
        if not math.isnan(k):
            vals.append(k)
    if len(vals) < n_boot * 0.5:
        return None
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def compare(a, b, kind, n_boot, seed):
    k = kappa(a, b, kind)
    row = {"n": len(a), "kappa": k, "exact": sum(x == y for x, y in zip(a, b)) / len(a)}
    row["within1"] = sum(abs(x - y) <= 1 for x, y in zip(a, b)) / len(a) if kind == "ordinal" else None
    row["ci"] = None if math.isnan(k) else boot_ci(a, b, kind, n_boot, seed)
    return row


def read_blind(path: Path) -> dict[str, dict]:
    ws = load_workbook(path, data_only=True)["Chấm mù"]
    rows = list(ws.iter_rows(values_only=True))
    head = list(rows[0])
    return {r[head.index("code")]: dict(zip(head, r)) for r in rows[1:] if r[head.index("code")]}


def read_dx(path: Path) -> dict[tuple[str, str], dict]:
    ws = load_workbook(path, read_only=True, data_only=True)["Review"]
    rows = list(ws.iter_rows(values_only=True))
    head = list(rows[0])
    return {(r[head.index("qid")], r[head.index("run_id")]): dict(zip(head, r)) for r in rows[1:] if r[0]}


def vn(x, d=3):
    return "–" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}".replace(".", ",")


def table(title, results):
    out = [f"### {title}", "", "| Cột | n | kappa | CI95 bootstrap | Trùng chính xác | Lệch ≤ 1 |", "| --- | --- | --- | --- | --- | --- |"]
    for name, r in results.items():
        kind = FIELDS[name][2]
        ci = "–" if not r["ci"] else f"[{vn(r['ci'][0], 2)}; {vn(r['ci'][1], 2)}]"
        label = f"{name} ({'weighted, bậc hai' if kind == 'ordinal' else 'Cohen'})"
        out.append(f"| {label} | {r['n']} | {vn(r['kappa'])} | {ci} | {vn(r['exact'], 2)} | {vn(r['within1'], 2)} |")
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--blind", type=Path, default=Path("results/review/blind10_B4_v1.1_test.xlsx"))
    ap.add_argument("--key", type=Path, default=Path("results/review/blind10_key.csv"))
    ap.add_argument("--manual", type=Path, default=Path("results/review/manual30_B4_v1_test_20261107-1335.csv"))
    ap.add_argument("--dx", type=Path, help="manual30 xlsx (sheet Review) để so với điểm đề xuất dx_*")
    ap.add_argument("--boot", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, help="ghi bảng Markdown (mặc định chỉ in)")
    a = ap.parse_args(argv)

    blind = read_blind(a.blind)
    key = {r["code"]: r for r in csv.DictReader(open(a.key, encoding="utf-8"))}
    manual = {(r["qid"], r["run_id"]): r for r in csv.DictReader(open(a.manual, encoding="utf-8"))}
    dx = read_dx(a.dx) if a.dx else None

    missing = [c for c, r in blind.items()
               if any(r.get(f) in (None, "") for f in ("correct_1_5", "faithful_1_5", "cite_ok"))]
    if missing:
        sys.exit(f"chưa chấm đủ correct/faithful/cite_ok: {missing}")
    if set(blind) != set(key):
        sys.exit(f"mã trong file chấm và khóa không khớp: {sorted(set(blind) ^ set(key))}")

    codes = sorted(blind)
    pairs = [(blind[c], manual[(key[c]["qid"], key[c]["run_id"])], key[c]) for c in codes]
    res_m, res_dx = {}, {}
    for name, (mcol, dxcol, kind) in FIELDS.items():
        b = [norm(p[0][name], kind) for p in pairs]
        res_m[name] = compare(b, [norm(p[1][mcol], kind) for p in pairs], kind, a.boot, a.seed)
        if dx is not None:
            res_dx[name] = compare(b, [norm(dx[(p[2]["qid"], p[2]["run_id"])][dxcol], kind) for p in pairs],
                                   kind, a.boot, a.seed)

    L = [f"## Chấm mù {len(codes)} câu manual30", "",
         f"File chấm `{a.blind}`, khóa `{a.key}`, điểm chốt `{a.manual}`. Kappa trống khi cả hai lần chỉ có một nhãn.", ""]
    L += table("Chấm mù so với điểm chốt manual30 (độ nhất quán của người chấm)", res_m)
    if dx is not None:
        L += [""] + table("Chấm mù so với đề xuất dx_* (kiểm tra neo theo đề xuất)", res_dx)
    L += ["", "### Từng câu (chấm mù / manual30)", "", "| Mã | qid | correct | faithful | cite_ok | error_code |",
          "| --- | --- | --- | --- | --- | --- |"]
    for c, (b, m, k) in zip(codes, pairs):
        cell = lambda f: f"{norm(b[f], FIELDS[f][2])} / {norm(m[FIELDS[f][0]], FIELDS[f][2])}"
        L.append(f"| {c} | {k['qid']} | {cell('correct_1_5')} | {cell('faithful_1_5')} | {cell('cite_ok')} | {cell('error_code')} |")
    text = "\n".join(L) + "\n"
    print(text)
    if a.out:
        a.out.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
