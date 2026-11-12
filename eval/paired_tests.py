"""Kiểm định theo cặp câu giữa hai cấu hình (cùng split test, cùng benchmark).

    PYTHONPATH=. python -m eval.paired_tests results/review/per_question_v1.1_test.csv B2:B3 B3:B4 B2:B4 B4ng:B4 \
        [--ragas-judge j1]

hit@1, hit@5 (rank evidence) và từ chối nhầm (câu answerable bị từ chối): McNemar chính xác (binomial trên cặp lệch);
reciprocal rank (MRR): Wilcoxon theo cặp.
--ragas-judge: thêm Wilcoxon theo cặp cho faithfulness / answer_correctness từ results/ragas/{run}__{judge}.csv.
"""
from __future__ import annotations

import argparse
import glob

import pandas as pd
from scipy.stats import binomtest, wilcoxon


def mcnemar(x: pd.Series, y: pd.Series) -> dict:
    b, c = int((x & ~y).sum()), int((~x & y).sum())            # b: chỉ A đạt; c: chỉ B đạt
    p = binomtest(b, b + c, 0.5).pvalue if b + c else 1.0
    return {"n": len(x), "A": int(x.sum()), "B": int(y.sum()), "chi_A": b, "chi_B": c, "p_exact": round(p, 4)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("per_question", nargs="+", help="một hay nhiều CSV của eval.per_question (ghép theo qid)")
    ap.add_argument("pairs", nargs="+", help="cặp config A:B, ví dụ B3:B4")
    ap.add_argument("--ragas-judge")
    a = ap.parse_args(argv)
    files = [f for f in a.per_question if f.endswith(".csv")]
    pairs = [p for p in a.per_question + a.pairs if ":" in p]
    df = pd.concat([pd.read_csv(f).set_index("qid") for f in files], axis=1)
    df = df.loc[:, ~df.columns.duplicated()]
    ans = df[df["group"] != "out_of_scope"]

    rows = []
    for p in pairs:
        A, B = p.split(":")
        hit = lambda n: ans[f"rank_{n}"].fillna(99) <= 5
        rows.append({"pair": p, "metric": "hit@5", **mcnemar(hit(A), hit(B))})
        rows.append({"pair": p, "metric": "hit@1", **mcnemar(ans[f"rank_{A}"].fillna(99) <= 1, ans[f"rank_{B}"].fillna(99) <= 1)})
        rr = {n: (1 / ans[f"rank_{n}"]).fillna(0) for n in (A, B)}      # MRR theo cặp câu: Wilcoxon
        st = wilcoxon(rr[A], rr[B]) if (rr[A] != rr[B]).any() else None
        rows.append({"pair": p, "metric": "rr (MRR)", "n": len(ans), "A": round(rr[A].mean(), 3), "B": round(rr[B].mean(), 3),
                     "chi_A": int((rr[A] > rr[B]).sum()), "chi_B": int((rr[A] < rr[B]).sum()),
                     "p_exact": round(st.pvalue, 4) if st else 1.0})
        ref = lambda n: ans[f"ref_{n}"].astype(bool)
        rows.append({"pair": p, "metric": "false_refusal", **mcnemar(ref(A), ref(B))})
        if a.ragas_judge:
            for m in ("faithfulness", "answer_correctness"):
                s = {}
                for n in (A, B):
                    fs = glob.glob(f"results/ragas/{n}_v1_test_*__{a.ragas_judge}.csv")
                    if len(fs) != 1:
                        raise SystemExit(f"cần đúng 1 file Ragas cho {n}, thấy {fs}")
                    s[n] = pd.read_csv(fs[0]).drop_duplicates("qid", keep="last").set_index("qid")[m]
                d = pd.concat(s, axis=1).dropna()     # chỉ câu cả hai cấu hình đều trả lời
                st = wilcoxon(d[A], d[B]) if (d[A] != d[B]).any() else None
                rows.append({"pair": p, "metric": f"{m}_{a.ragas_judge}", "n": len(d), "A": round(d[A].mean(), 3),
                             "B": round(d[B].mean(), 3), "chi_A": int((d[A] > d[B]).sum()),
                             "chi_B": int((d[A] < d[B]).sum()), "p_exact": round(st.pvalue, 4) if st else 1.0})
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
