import random

import pytest

from fpgrowth import fpgrowth
from validation import compare_itemsets, mlxtend_reference


@pytest.mark.parametrize("min_support", [0.02, 0.1])
def test_mlxtend_agrees_with_fpgrowth(min_support):
    rng = random.Random(7)
    tx = [frozenset(rng.sample(range(15), rng.choice([0, 1, 1, 2, 3, 5]))) for _ in range(400)]
    ours = fpgrowth(tx, min_support).itemsets
    assert compare_itemsets(ours, mlxtend_reference(tx, min_support))["identical"]


def test_mlxtend_reference_no_frequent_items():
    assert mlxtend_reference([frozenset([1]), frozenset([2])], 0.9) == {}


def test_compare_itemsets_reports_differences():
    a = {frozenset([1]): 3, frozenset([2]): 2}
    b = {frozenset([1]): 4, frozenset([3]): 2}
    assert compare_itemsets(a, b) == {
        "n_ours": 2, "n_ref": 2, "missing": 1, "extra": 1, "count_mismatch": 1, "identical": False,
    }


def test_mlxtend_reference_item_ids_not_starting_at_zero():
    tx = [frozenset([5, 7]), frozenset([5, 7]), frozenset([5]), frozenset()]
    assert mlxtend_reference(tx, 0.5) == {frozenset([5]): 3, frozenset([7]): 2, frozenset([5, 7]): 2}


def test_mlxtend_reference_keeps_full_denominator():
    tx = [frozenset()] * 95 + [frozenset([1, 2])] * 3 + [frozenset([1]), frozenset([3])]
    assert mlxtend_reference(tx, 0.03) == {frozenset([1]): 4, frozenset([2]): 3, frozenset([1, 2]): 3}
    assert mlxtend_reference(tx, 0.04) == {frozenset([1]): 4}
