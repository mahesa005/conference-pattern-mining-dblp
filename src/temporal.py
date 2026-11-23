"""Fungsi untuk analisis asosiasi temporal (Bagian E) pada author-year-based database."""
from __future__ import annotations

from typing import Dict, FrozenSet, Iterable, List, Sequence, Set, Tuple

import numpy as np
import pandas as pd

PERIODS: Dict[str, Tuple[int, int]] = {
    "2015-2017": (2015, 2017),
    "2018-2020": (2018, 2020),
    "2021-2023": (2021, 2023),
    "2024-2025": (2024, 2025),
}

Rule = Tuple[Tuple[int, ...], Tuple[int, ...]]


def period_transactions(long: pd.DataFrame, index: pd.DataFrame, start: int, end: int) -> List[FrozenSet[int]]:
    """Transaksi (author, tahun) dengan tahun di [start, end], urut menurut tid.

    Transaksi tanpa item tetap disertakan sebagai himpunan kosong agar ikut dihitung pada penyebut support.
    """
    tids = np.sort(index.loc[index["year"].between(start, end), "tid"].to_numpy())
    sub = long[long["tid"].isin(tids)]
    items = sub.groupby("tid")["item"].apply(lambda s: frozenset(s.tolist()))
    return [items.get(t, frozenset()) for t in tids]


def drop_large(transactions: Sequence[FrozenSet[int]], max_items: int = 20) -> List[FrozenSet[int]]:
    """Mengosongkan transaksi berisi max_items item atau lebih. Jumlah transaksi (penyebut) tetap."""
    return [frozenset() if len(t) >= max_items else t for t in transactions]


def support_counts(transactions: Sequence[FrozenSet[int]], itemsets: Iterable[FrozenSet[int]]) -> Dict[FrozenSet[int], int]:
    """Count setiap itemset, dihitung dengan irisan himpunan tid per item (bentuk vertikal)."""
    targets = [frozenset(s) for s in itemsets]
    needed = set().union(*targets) if targets else set()
    tidsets: Dict[int, Set[int]] = {i: set() for i in needed}
    for tid, t in enumerate(transactions):
        for i in t:
            if i in tidsets:
                tidsets[i].add(tid)
    out: Dict[FrozenSet[int], int] = {}
    for s in targets:
        if s in out:
            continue
        sets = sorted((tidsets[i] for i in s), key=len)
        acc = sets[0].intersection(*sets[1:]) if sets else set(range(len(transactions)))
        out[s] = len(acc)
    return out


def rule_metrics(transactions: Sequence[FrozenSet[int]], rules: Iterable[Rule]) -> pd.DataFrame:
    """Support, confidence, dan lift rule tertentu pada transaksi ini, termasuk rule yang tidak lolos ambang."""
    rules = [(tuple(a), tuple(c)) for a, c in rules]
    sides = [frozenset(a) for a, _ in rules] + [frozenset(c) for _, c in rules] + \
            [frozenset(a) | frozenset(c) for a, c in rules]
    counts = support_counts(transactions, sides)
    n = len(transactions)
    rows = []
    for a, c in rules:
        xy, x, y = counts[frozenset(a) | frozenset(c)], counts[frozenset(a)], counts[frozenset(c)]
        rows.append((a, c, xy, x, y, xy / n,
                     xy / x if x else np.nan,
                     xy * n / (x * y) if x and y else np.nan))
    return pd.DataFrame(rows, columns=["antecedent", "consequent", "count", "antecedent_count",
                                       "consequent_count", "support", "confidence", "lift"])


def classify_presence(presence: Sequence[bool]) -> str:
    """Kategori rule menurut kemunculannya pada periode berurutan.

    bertahan: muncul di semua periode. muncul: tidak ada di awal lalu ada terus sampai akhir.
    hilang: ada di awal lalu tidak ada sampai akhir. berselang: pola lain.
    """
    p = [bool(x) for x in presence]
    if not any(p):
        raise ValueError("rule tidak muncul di periode mana pun")
    if all(p):
        return "bertahan"
    first, last = p.index(True), len(p) - 1 - p[::-1].index(True)
    contiguous = all(p[first:last + 1])
    if contiguous and last == len(p) - 1:
        return "muncul"
    if contiguous and first == 0:
        return "hilang"
    return "berselang"


def choose_main_level(summary: pd.DataFrame, min_rules: int = 15, min_survival: float = 0.8) -> Tuple[float, bool]:
    """Memilih min support utama dari ringkasan per (min_support, period).

    Lolos jika setiap periode memiliki >= min_rules rules dan survival >= min_survival. Dari yang lolos,
    dipilih min support terkecil. Jika tidak ada yang lolos, jumlah rules tetap menjadi syarat (tanpa rules
    tidak ada yang dapat dibandingkan): dipilih min support dengan survival minimum tertinggi di antara yang
    memenuhi syarat jumlah rules, atau min support dengan jumlah rules minimum terbesar jika tidak ada.
    Nilai kedua bernilai False pada kedua kasus cadangan ini.
    """
    g = summary.groupby("min_support").agg(min_rules=("n_rules", "min"), min_surv=("survival", "min"))
    enough = g[g["min_rules"] >= min_rules]
    passing = enough[enough["min_surv"] >= min_survival]
    if len(passing):
        return float(passing.index.min()), True
    if len(enough):
        return float(enough["min_surv"].idxmax()), False
    return float(g["min_rules"].idxmax()), False
