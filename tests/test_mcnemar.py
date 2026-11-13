from eval.mcnemar import binom_two_sided, compare, holm


def test_binom_two_sided():
    assert binom_two_sided(0, 0) == 1.0
    assert binom_two_sided(0, 1) == 1.0
    assert abs(binom_two_sided(0, 5) - 0.0625) < 1e-9          # 2 * 0,5^5
    assert abs(binom_two_sided(9, 28) - binom_two_sided(28, 9)) < 1e-12


def test_holm_monotone():
    adj = holm([0.01, 0.04, 0.03])
    assert adj == [0.03, 0.06, 0.06]


def test_compare_counts():
    a = {"q1": 1, "q2": 1, "q3": 0, "q4": 0}
    b = {"q1": 1, "q2": 0, "q3": 1, "q4": 1, "q5": 1}
    r = compare(a, b)
    assert (r["n"], r["only_a"], r["only_b"]) == (4, 1, 2)
