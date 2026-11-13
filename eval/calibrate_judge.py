"""Hiệu chỉnh judge: tương quan điểm chấm tay (1–5) với Ragas, ghép theo (run_id, qid).

    PYTHONPATH=. .venv-judge/bin/python -m eval.calibrate_judge results/review/manual30_B4_v1_test_20261107-1335.csv \
        results/ragas/B4_v1_test_20261107-1335__j1.csv results/ragas/B4ng_v1_test_20261107-1335__j1.csv

[main] = 30 câu của run B4 (số báo cáo); [all] = thêm 4 câu B4ng (kiểm tra độ nhạy).
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr

PAIRS = [("faithful", "faithfulness"), ("correct", "answer_correctness")]


def boot_ci(x, y, n=2000, seed=42):
    rng = np.random.default_rng(seed)
    r = [spearmanr(x[i], y[i]).statistic for i in (rng.integers(0, len(x), len(x)) for _ in range(n))]
    return np.nanpercentile(r, [2.5, 97.5])


def main(man_csv: str, *ragas_csvs: str) -> None:
    man = pd.read_csv(man_csv)
    rg = pd.concat([pd.read_csv(f).assign(run_id=Path(f).stem.split("__")[0]) for f in ragas_csvs])
    rg = rg[rg["error"].isna()].drop_duplicates(["run_id", "qid"], keep="last")
    df = man.merge(rg[["run_id", "qid", "faithfulness", "answer_correctness"]], on=["run_id", "qid"])
    print(f"chấm tay {len(man)}, ghép được {len(df)}; thiếu điểm Ragas: {sorted(set(man.qid) - set(df.qid))}")
    for scope, sub in [("main", df[df["part"] == "main"]), ("all", df)]:
        for h, j in PAIRS:
            d = sub[[h, j]].dropna()
            x, y = d[h].to_numpy(float), d[j].to_numpy(float)
            lo, hi = boot_ci(x, y)
            print(f"[{scope}] {h} ~ {j}: n={len(d)} rho={spearmanr(x, y).statistic:.3f} CI95=[{lo:.2f}, {hi:.2f}] "
                  f"tau_b={kendalltau(x, y).statistic:.3f} | điểm tay {d[h].value_counts().sort_index().to_dict()}")
    for h, j in PAIRS:
        df[f"gap_{h}"] = (df[h].rank(pct=True) - df[j].rank(pct=True)).abs()
        print(f"\nLệch nhất ({h}):\n" + df.nlargest(5, f"gap_{h}")[["qid", "group", "error_code", h, j]].to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:])
