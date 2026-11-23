import random
from itertools import combinations

import numpy as np
import pandas as pd
import pytest

from temporal import (PERIODS, choose_main_level, classify_presence, drop_large, period_transactions,
                      rule_metrics, support_counts)


def test_periods_cover_2015_2025_without_gaps():
    years = [y for a, b in PERIODS.values() for y in range(a, b + 1)]
    assert years == list(range(2015, 2026))


def test_period_transactions_keeps_empty_and_filters_year():
    long = pd.DataFrame({"tid": [0, 0, 1, 3, 3, 3], "item": [5, 7, 5, 1, 2, 9]})
    index = pd.DataFrame({"tid": [0, 1, 2, 3], "year": [2015, 2016, 2016, 2019]})
    tx = period_transactions(long, index, 2015, 2017)
    assert tx == [frozenset({5, 7}), frozenset({5}), frozenset()]
    assert period_transactions(long, index, 2018, 2020) == [frozenset({1, 2, 9})]


def test_drop_large_empties_but_keeps_length():
    tx = [frozenset({1, 2}), frozenset(range(20)), frozenset(range(19))]
    out = drop_large(tx, max_items=20)
    assert len(out) == 3
    assert out[0] == tx[0] and out[1] == frozenset() and out[2] == tx[2]


def test_support_counts_matches_brute_force():
    rng = random.Random(7)
    tx = [frozenset(rng.sample(range(8), rng.randint(0, 5))) for _ in range(300)]
    targets = [frozenset(c) for k in (1, 2, 3) for c in combinations(range(8), k)]
    got = support_counts(tx, targets)
    for s in targets:
        assert got[s] == sum(s <= t for t in tx)


def test_rule_metrics_hand_example():
    # N = 10; A in 4 tx, B in 5 tx, A and B together in 3 tx.
    tx = ([frozenset({1, 2})] * 3 + [frozenset({1})] + [frozenset({2})] * 2 + [frozenset({3})] * 3
          + [frozenset()])
    df = rule_metrics(tx, [((1,), (2,)), ((9,), (2,))])
    a = df.iloc[0]
    assert (a["count"], a["antecedent_count"], a["consequent_count"]) == (3, 4, 5)
    assert a["support"] == pytest.approx(0.3)
    assert a["confidence"] == pytest.approx(0.75)
    assert a["lift"] == pytest.approx(0.75 / 0.5)
    b = df.iloc[1]
    assert b["count"] == 0 and np.isnan(b["confidence"]) and np.isnan(b["lift"])


@pytest.mark.parametrize("presence, expected", [
    ((True, True, True, True), "bertahan"),
    ((False, False, True, True), "muncul"),
    ((False, False, False, True), "muncul"),
    ((True, True, False, False), "hilang"),
    ((True, False, False, False), "hilang"),
    ((True, False, True, True), "berselang"),
    ((False, True, True, False), "berselang"),
])
def test_classify_presence(presence, expected):
    assert classify_presence(presence) == expected


def test_classify_presence_rejects_absent_rule():
    with pytest.raises(ValueError):
        classify_presence((False, False, False, False))


def _summary(rows):
    return pd.DataFrame(rows, columns=["min_support", "period", "n_rules", "survival"])


def test_choose_main_level_lowest_passing():
    rows = []
    for ms, n, surv in ((0.0001, 100, 0.9), (0.0002, 40, 0.95), (0.0005, 5, 1.0)):
        rows += [(ms, p, n, surv) for p in PERIODS]
    assert choose_main_level(_summary(rows)) == (0.0001, True)


def test_choose_main_level_skips_level_failing_one_period():
    rows = []
    for ms in (0.0001, 0.0002):
        rows += [(ms, p, 50, 0.9) for p in list(PERIODS)[:3]]
    rows += [(0.0001, "2024-2025", 500, 0.64), (0.0002, "2024-2025", 200, 0.85)]
    assert choose_main_level(_summary(rows)) == (0.0002, True)


def test_choose_main_level_fallback_keeps_rule_count():
    # Pola data asli: survival 2024-2025 < 80% di semua level, 0,05% terlalu sedikit rules.
    counts = {0.0001: (70, 130, 480, 7741), 0.0002: (17, 32, 113, 1874), 0.0005: (2, 4, 25, 282)}
    survival = {0.0001: (0.96, 1.0, 0.93, 0.64), 0.0002: (0.94, 1.0, 0.98, 0.67), 0.0005: (1.0, 1.0, 0.96, 0.78)}
    rows = [(ms, p, counts[ms][i], survival[ms][i]) for ms in counts for i, p in enumerate(PERIODS)]
    assert choose_main_level(_summary(rows)) == (0.0002, False)


def test_choose_main_level_fallback_most_rules_when_none_enough():
    rows = []
    for ms, n in ((0.0001, 10), (0.0002, 5)):
        rows += [(ms, p, n, 1.0) for p in PERIODS]
    assert choose_main_level(_summary(rows)) == (0.0001, False)
