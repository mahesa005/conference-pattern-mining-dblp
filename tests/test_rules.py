import random
from itertools import combinations

import pandas as pd
import pytest

from fpgrowth import fpgrowth
from rules import generate_rules, load_itemsets, rule_label

TEXTBOOK = [frozenset(t) for t in (
    [1, 2, 5], [2, 4], [2, 3], [1, 2, 4], [1, 3],
    [2, 3], [1, 3], [1, 2, 3, 5], [1, 2, 3],
)]
NAMES = {i: f"I{i}" for i in range(1, 6)}


def brute_force_rules(transactions, itemsets, min_confidence):
    """Oracle: counts every side directly from the transactions."""
    def count(s):
        return sum(1 for t in transactions if s <= t)

    n = len(transactions)
    out = {}
    for itemset in itemsets:
        if len(itemset) < 2:
            continue
        for k in range(1, len(itemset)):
            for ante in combinations(sorted(itemset), k):
                a = frozenset(ante)
                c = itemset - a
                conf = count(itemset) / count(a)
                if conf >= min_confidence:
                    out[(a, c)] = (count(itemset) / n, conf, conf / (count(c) / n))
    return out


def as_dict(df):
    return {(frozenset(a), frozenset(c)): (s, cf, l)
            for a, c, s, cf, l in df[["antecedent", "consequent", "support", "confidence", "lift"]].itertuples(index=False)}


def test_textbook_rules_from_i1_i2_i5():
    itemsets = fpgrowth(TEXTBOOK, 2 / 9).itemsets
    df = generate_rules(itemsets, 9, 0.7)
    from_125 = df[df.apply(lambda r: set(r.antecedent) | set(r.consequent) == {1, 2, 5}, axis=1)]
    assert sorted(zip(from_125.antecedent, from_125.consequent)) == [((1, 5), (2,)), ((2, 5), (1,)), ((5,), (1, 2))]
    row = from_125[from_125.antecedent.apply(lambda a: a == (5,))].iloc[0]
    assert row.confidence == pytest.approx(1.0)
    assert row.support == pytest.approx(2 / 9)
    assert row.lift == pytest.approx(2 * 9 / (2 * 4))


def test_confidence_threshold_is_inclusive():
    itemsets = fpgrowth(TEXTBOOK, 2 / 9).itemsets
    df = generate_rules(itemsets, 9, 0.5)
    assert ((1, 2), (5,)) in set(zip(df.antecedent, df.consequent))  # 2/4 = 0.5 exactly


@pytest.mark.parametrize("seed", [0, 1, 2])
@pytest.mark.parametrize("min_confidence", [0.3, 0.5, 0.8])
def test_matches_brute_force(seed, min_confidence):
    rng = random.Random(seed)
    tx = [frozenset(rng.sample(range(10), rng.choice([0, 1, 1, 2, 3, 4, 5]))) for _ in range(250)]
    itemsets = fpgrowth(tx, 0.03).itemsets
    ours = as_dict(generate_rules(itemsets, len(tx), min_confidence))
    oracle = brute_force_rules(tx, itemsets, min_confidence)
    assert ours.keys() == oracle.keys()
    for key, vals in oracle.items():
        assert ours[key] == pytest.approx(vals)


def test_no_rules_from_single_items():
    df = generate_rules({frozenset([1]): 5, frozenset([2]): 4}, 10, 0.5)
    assert len(df) == 0
    assert {"antecedent", "consequent", "support", "confidence", "lift"} <= set(df.columns)


def test_sorted_by_lift_and_labels():
    itemsets = fpgrowth(TEXTBOOK, 2 / 9).itemsets
    df = generate_rules(itemsets, 9, 0.5, NAMES)
    assert df["lift"].is_monotonic_decreasing
    assert rule_label((1, 5), (2,), NAMES) == "I1 + I5 → I2"
    assert "rule" in df.columns


def test_load_itemsets_round_trip(tmp_path):
    path = tmp_path / "itemsets.parquet"
    pd.DataFrame({"itemset": [[1], [2], [1, 2]], "length": [1, 1, 2], "count": [5, 4, 3]}).to_parquet(path, index=False)
    assert load_itemsets(path) == {frozenset([1]): 5, frozenset([2]): 4, frozenset([1, 2]): 3}
