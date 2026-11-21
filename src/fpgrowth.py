"""FP-Growth (Han, Pei, dan Yin, 2000) untuk transactional database berbentuk horizontal."""
from __future__ import annotations

import math
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, Iterator, List, Mapping, Optional, Sequence, Tuple

import pandas as pd


def min_count_for(min_support: float, n_transactions: int) -> int:
    """Count terkecil c sehingga c / n_transactions >= min_support (minimal 1)."""
    c = math.ceil(min_support * n_transactions)
    while c > 0 and (c - 1) / n_transactions >= min_support:
        c -= 1
    while c / n_transactions < min_support:
        c += 1
    return max(c, 1)


def order_items(items: Iterable[int], counts: Mapping[int, int]) -> Tuple[int, ...]:
    """Urutan item di FP-tree: count menurun, lalu id item menaik."""
    return tuple(sorted(items, key=lambda i: (-counts[i], i)))


class FPNode:
    __slots__ = ("item", "count", "parent", "children")

    def __init__(self, item: Optional[int], parent: Optional["FPNode"]):
        self.item = item
        self.count = 0
        self.parent = parent
        self.children: Dict[int, FPNode] = {}


class FPTree:
    def __init__(self):
        self.root = FPNode(None, None)
        self.header: Dict[int, List[FPNode]] = defaultdict(list)

    def insert(self, path: Tuple[int, ...], count: int) -> None:
        node = self.root
        for item in path:
            child = node.children.get(item)
            if child is None:
                child = FPNode(item, node)
                node.children[item] = child
                self.header[item].append(child)
            child.count += count
            node = child

    def prefix_paths(self, item: int) -> Iterator[Tuple[Tuple[int, ...], int]]:
        """Conditional pattern base: (jalur dari root sampai sebelum node, count node)."""
        for node in self.header.get(item, ()):
            path = []
            parent = node.parent
            while parent.item is not None:
                path.append(parent.item)
                parent = parent.parent
            if path:
                path.reverse()
                yield tuple(path), node.count


def render_tree(tree: FPTree, names: Mapping[int, str]) -> str:
    lines: List[str] = []

    def walk(node: FPNode, depth: int) -> None:
        for child in sorted(node.children.values(), key=lambda n: (-n.count, n.item)):
            lines.append("  " * depth + f"{names[child.item]}:{child.count}")
            walk(child, depth + 1)

    walk(tree.root, 0)
    return "\n".join(lines)


@dataclass
class FPGrowthResult:
    itemsets: Dict[FrozenSet[int], int]
    n_transactions: int
    min_support: float
    min_count: int
    t_build: float
    t_mine: float
    tree: FPTree = field(repr=False)


def _mine(tree: FPTree, counts: Mapping[int, int], suffix: Tuple[int, ...],
          min_count: int, out: Dict[FrozenSet[int], int]) -> None:
    for item in sorted(counts, key=lambda i: (counts[i], -i)):
        itemset = suffix + (item,)
        out[frozenset(itemset)] = counts[item]
        base = list(tree.prefix_paths(item))
        if not base:
            continue
        cond_counts: Counter = Counter()
        for path, weight in base:
            for i in path:
                cond_counts[i] += weight
        cond_counts = {i: c for i, c in cond_counts.items() if c >= min_count}
        if not cond_counts:
            continue
        cond_tree = FPTree()
        for path, weight in base:
            kept = order_items([i for i in path if i in cond_counts], cond_counts)
            if kept:
                cond_tree.insert(kept, weight)
        _mine(cond_tree, cond_counts, itemset, min_count, out)


def fpgrowth(transactions: Sequence[FrozenSet[int]], min_support: float) -> FPGrowthResult:
    n = len(transactions)
    min_count = min_count_for(min_support, n)

    t0 = time.perf_counter()
    counts: Counter = Counter()
    for t in transactions:
        counts.update(t)
    frequent = {i: c for i, c in counts.items() if c >= min_count}
    paths: Counter = Counter()
    for t in transactions:
        kept = [i for i in t if i in frequent]
        if len(kept) >= 2:
            paths[order_items(kept, frequent)] += 1
    tree = FPTree()
    for path, weight in paths.items():
        tree.insert(path, weight)
    t1 = time.perf_counter()

    itemsets: Dict[FrozenSet[int], int] = {}
    _mine(tree, frequent, (), min_count, itemsets)
    t2 = time.perf_counter()

    return FPGrowthResult(itemsets, n, min_support, min_count, t1 - t0, t2 - t1, tree)


def to_frame(result: FPGrowthResult, names: Optional[Mapping[int, str]] = None) -> pd.DataFrame:
    rows = [(tuple(sorted(s)), len(s), c) for s, c in result.itemsets.items()]
    df = pd.DataFrame(rows, columns=["itemset", "length", "count"])
    df["support"] = df["count"] / result.n_transactions
    if names is not None:
        df["names"] = [" + ".join(names[i] for i in s) for s in df["itemset"]]
    return df.sort_values(["count", "length", "itemset"], ascending=[False, True, True], ignore_index=True)
