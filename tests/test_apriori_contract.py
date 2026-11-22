"""Kontrak untuk Apriori di src/apriori.py (Harfhan). Dilewati selama file itu belum ada.

Apriori harus menerima list frozenset item_id dan min support, lalu mengembalikan objek dengan
atribut `itemsets` (dict frozenset -> count) atau dict tersebut secara langsung. Hasilnya harus
sama persis dengan FP-Growth dan brute force, dengan penyebut support seluruh transaksi.
"""
import random
from collections import Counter
from itertools import combinations

import pytest

from benchmark import itemsets_of
from fpgrowth import min_count_for

apriori_module = pytest.importorskip("apriori", reason="src/apriori.py belum ada")
apriori = apriori_module.apriori

TEXTBOOK = [frozenset(t) for t in (
    [1, 2, 5], [2, 4], [2, 3], [1, 2, 4], [1, 3],
    [2, 3], [1, 3], [1, 2, 3, 5], [1, 2, 3],
)]


def brute_force(transactions, min_support):
    mc = min_count_for(min_support, len(transactions))
    counts = Counter()
    for t in transactions:
        items = sorted(t)
        for k in range(1, len(items) + 1):
            for combo in combinations(items, k):
                counts[frozenset(combo)] += 1
    return {s: c for s, c in counts.items() if c >= mc}


def test_textbook():
    assert itemsets_of(apriori(TEXTBOOK, 2 / 9)) == brute_force(TEXTBOOK, 2 / 9)


def test_empty_transactions_stay_in_denominator():
    tx = [frozenset()] * 6 + [frozenset([1, 2])] * 4
    assert itemsets_of(apriori(tx, 0.4)) == {frozenset([1]): 4, frozenset([2]): 4, frozenset([1, 2]): 4}
    assert itemsets_of(apriori(tx, 0.5)) == {}


@pytest.mark.parametrize("seed", [0, 1, 2])
@pytest.mark.parametrize("min_support", [0.02, 0.1])
def test_matches_brute_force(seed, min_support):
    rng = random.Random(seed)
    tx = [frozenset(rng.sample(range(12), rng.choice([0, 1, 1, 1, 2, 2, 3, 4, 6]))) for _ in range(300)]
    assert itemsets_of(apriori(tx, min_support)) == brute_force(tx, min_support)
