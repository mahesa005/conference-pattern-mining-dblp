from fpgrowth import FPTree, min_count_for, order_items, render_tree

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
