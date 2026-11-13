import math

from eval import kappa as K
from scripts import make_blind10 as MB


def test_kappa_perfect_and_shift():
    a = [5, 5, 4, 3, 1, 5, 2, 4, 5, 3]
    assert K.kappa(a, a, "ordinal") == 1.0
    b = [max(1, x - 1) for x in a]
    k = K.kappa(a, b, "ordinal")
    assert 0.5 < k < 1.0                                    # lệch 1 điểm: weighted kappa vẫn cao
    assert math.isnan(K.kappa([5] * 4, [5] * 4, "ordinal"))  # chỉ một nhãn: không xác định


def test_norm_codes():
    assert K.norm("", "nominal") == "OK" and K.norm(None, "nominal") == "OK"
    assert K.norm("g1", "nominal") == "G1" and K.norm("P1 → G1", "nominal") == "P1"
    assert K.norm(1.0, "nominal") == "1" and K.norm("4", "ordinal") == 4


def test_select_quota_and_low():
    rows = []
    for g, n in (("lookup", 7), ("table", 7), ("compare", 8), ("scenario", 8)):
        for i in range(n):
            low = i < 2
            rows.append({"qid": f"{g}{i}", "group": g, "correct": "2" if low else "5", "faithful": "5"})
    chosen = MB.select(rows, MB.QUOTA, n_low=4, seed=1)
    assert len(chosen) == 10
    assert {g: sum(r["group"] == g for r in chosen) for g in MB.QUOTA} == MB.QUOTA
    assert sum(r["correct"] == "2" for r in chosen) >= 4
    assert MB.select(rows, MB.QUOTA, 4, 1) == chosen         # seed cố định → cùng mẫu
