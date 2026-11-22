"""Apriori (Agrawal dan Srikant, 1994) untuk transactional database berbentuk horizontal."""
from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass
from itertools import combinations
from math import comb
from typing import Dict, FrozenSet, List, Sequence, Set, Tuple

from fpgrowth import min_count_for

Itemset = Tuple[int, ...]


@dataclass
class AprioriResult:
    itemsets: Dict[FrozenSet[int], int]
    n_transactions: int
    min_support: float
    min_count: int
    level_seconds: List[float]  # waktu tiap level k = 1, 2, ...; level 1 termasuk pra-pemrosesan
    n_candidates: List[int]  # |C_k| tiap level; level 1 = jumlah item unik


def generate_candidates(frequent: Sequence[Itemset]) -> Set[Itemset]:
    """Join L(k-1) dengan dirinya (prefiks k-2 item sama), lalu prune kandidat yang punya
    subset (k-1) tidak frequent. Itemset disimpan sebagai tuple terurut menaik."""
    prev = set(frequent)
    by_prefix: Dict[Itemset, List[int]] = {}
    for s in sorted(frequent):
        by_prefix.setdefault(s[:-1], []).append(s[-1])
    out: Set[Itemset] = set()
    for prefix, lasts in by_prefix.items():
        for a, b in combinations(lasts, 2):
            cand = prefix + (a, b)
            if all(cand[:i] + cand[i + 1:] in prev for i in range(len(cand) - 2)):
                out.add(cand)
    return out


def count_candidates(db: Sequence[Tuple[Itemset, int]], candidates: Set[Itemset], k: int) -> Counter:
    """Menghitung count berbobot tiap kandidat. Per transaksi dipilih cara yang lebih murah:
    enumerasi k-subset transaksi, atau cek setiap kandidat sebagai subset transaksi."""
    cand_items = {i for c in candidates for i in c}
    counts: Counter = Counter()
    for t, w in db:
        t = tuple(i for i in t if i in cand_items)
        if len(t) < k:
            continue
        if comb(len(t), k) <= len(candidates):
            for s in combinations(t, k):
                if s in candidates:
                    counts[s] += w
        else:
            ts = set(t)
            for c in candidates:
                if ts.issuperset(c):
                    counts[c] += w
    return counts


def apriori(transactions: Sequence[FrozenSet[int]], min_support: float) -> AprioriResult:
    n = len(transactions)
    min_count = min_count_for(min_support, n)
    level_seconds: List[float] = []
    n_candidates: List[int] = []

    # Level 1: scan pertama, lalu bangun database terpangkas dan tergabung.
    t0 = time.perf_counter()
    item_counts: Counter = Counter()
    for t in transactions:
        item_counts.update(t)
    frequent1 = {i: c for i, c in item_counts.items() if c >= min_count}
    merged: Counter = Counter()
    for t in transactions:
        kept = [i for i in t if i in frequent1]
        if len(kept) >= 2:
            merged[tuple(sorted(kept))] += 1
    db = list(merged.items())
    itemsets: Dict[FrozenSet[int], int] = {frozenset([i]): c for i, c in frequent1.items()}
    level = [(i,) for i in sorted(frequent1)]
    n_candidates.append(len(item_counts))
    level_seconds.append(time.perf_counter() - t0)

    k = 2
    while level:
        t0 = time.perf_counter()
        candidates = generate_candidates(level)
        if not candidates:
            break
        n_candidates.append(len(candidates))
        counts = count_candidates(db, candidates, k)
        level = sorted(s for s, c in counts.items() if c >= min_count)
        itemsets.update((frozenset(s), counts[s]) for s in level)
        level_seconds.append(time.perf_counter() - t0)
        k += 1

    return AprioriResult(itemsets, n, min_support, min_count, level_seconds, n_candidates)
