"""FP-Growth (Han, Pei, dan Yin, 2000) untuk transactional database berbentuk horizontal."""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Dict, Iterable, Iterator, List, Mapping, Optional, Tuple


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
