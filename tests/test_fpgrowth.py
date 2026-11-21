import random
from collections import Counter
from itertools import combinations

import pytest

from fpgrowth import FPTree, fpgrowth, min_count_for, order_items, render_tree, to_frame

# Han, Kamber, Pei (2012) Table 6.1, items I1..I5 coded as 1..5.
TEXTBOOK = [frozenset(t) for t in (
    [1, 2, 5], [2, 4], [2, 3], [1, 2, 4], [1, 3],
    [2, 3], [1, 3], [1, 2, 3, 5], [1, 2, 3],
)]
TEXTBOOK_COUNTS = {1: 6, 2: 7, 3: 6, 4: 2, 5: 2}
NAMES = {i: f"I{i}" for i in range(1, 6)}


def test_min_count_for_real_database():
    assert min_count_for(0.001, 1_821_757) == 1822
    assert min_count_for(0.005, 1_821_757) == 9109
    assert min_count_for(0.01, 1_821_757) == 18218
    assert min_count_for(0.02, 1_821_757) == 36436


def test_min_count_for_exact_fractions():
    assert min_count_for(2 / 9, 9) == 2
    assert min_count_for(0.5, 4) == 2
    assert min_count_for(0.0, 10) == 1


def test_order_items_desc_count_then_id():
    assert order_items([5, 1, 3, 2, 4], TEXTBOOK_COUNTS) == (2, 1, 3, 4, 5)


def _textbook_tree():
    tree = FPTree()
    for t in TEXTBOOK:
        tree.insert(order_items(t, TEXTBOOK_COUNTS), 1)
    return tree


def test_tree_shape_matches_textbook():
    tree = _textbook_tree()
    assert {i: n.count for i, n in tree.root.children.items()} == {2: 7, 1: 2}
    assert len(tree.header[3]) == 3
    assert sum(n.count for n in tree.header[5]) == 2


def test_prefix_paths_of_item_5():
    tree = _textbook_tree()
    assert sorted(tree.prefix_paths(5)) == [((2, 1), 1), ((2, 1, 3), 1)]


def test_render_tree():
    assert render_tree(_textbook_tree(), NAMES).splitlines() == [
        "I2:7",
        "  I1:4",
        "    I3:2",
        "      I5:1",
        "    I4:1",
        "    I5:1",
        "  I3:2",
        "  I4:1",
        "I1:2",
        "  I3:2",
    ]


def brute_force(transactions, min_support):
    mc = min_count_for(min_support, len(transactions))
    counts = Counter()
    for t in transactions:
        items = sorted(t)
        for k in range(1, len(items) + 1):
            for combo in combinations(items, k):
                counts[frozenset(combo)] += 1
    return {s: c for s, c in counts.items() if c >= mc}


def test_textbook_frequent_itemsets():
    result = fpgrowth(TEXTBOOK, 2 / 9)
    expected = {
        frozenset([1]): 6, frozenset([2]): 7, frozenset([3]): 6, frozenset([4]): 2, frozenset([5]): 2,
        frozenset([1, 2]): 4, frozenset([1, 3]): 4, frozenset([1, 5]): 2,
        frozenset([2, 3]): 4, frozenset([2, 4]): 2, frozenset([2, 5]): 2,
        frozenset([1, 2, 3]): 2, frozenset([1, 2, 5]): 2,
    }
    assert result.itemsets == expected
    assert result.min_count == 2
    assert result.n_transactions == 9


def test_single_item_transactions_count_but_skip_tree():
    tx = [frozenset([1])] * 3 + [frozenset([1, 2])]
    assert fpgrowth(tx, 0.5).itemsets == {frozenset([1]): 4}
    assert fpgrowth(tx, 0.25).itemsets == {frozenset([1]): 4, frozenset([2]): 1, frozenset([1, 2]): 1}
    assert set(fpgrowth(tx, 0.25).tree.root.children) == {1}


def test_empty_transactions_stay_in_denominator():
    tx = [frozenset()] * 6 + [frozenset([1, 2])] * 4
    assert fpgrowth(tx, 0.4).itemsets == {frozenset([1]): 4, frozenset([2]): 4, frozenset([1, 2]): 4}
    assert fpgrowth(tx, 0.5).itemsets == {}


def test_timings_recorded():
    result = fpgrowth(TEXTBOOK, 2 / 9)
    assert result.t_build >= 0 and result.t_mine >= 0


@pytest.mark.parametrize("seed", [0, 1, 2, 3])
@pytest.mark.parametrize("min_support", [0.01, 0.05, 0.1, 0.2])
def test_matches_brute_force(seed, min_support):
    rng = random.Random(seed)
    tx = [frozenset(rng.sample(range(12), rng.choice([0, 1, 1, 1, 2, 2, 3, 4, 6]))) for _ in range(300)]
    assert fpgrowth(tx, min_support).itemsets == brute_force(tx, min_support)


def test_to_frame_columns_and_order():
    df = to_frame(fpgrowth(TEXTBOOK, 2 / 9), NAMES)
    assert list(df.columns) == ["itemset", "length", "count", "support", "names"]
    assert df.iloc[0]["itemset"] == (2,)
    assert df.iloc[0]["support"] == pytest.approx(7 / 9)
    assert df.loc[df["itemset"].apply(lambda s: s == (1, 2)), "names"].item() == "I1 + I2"
