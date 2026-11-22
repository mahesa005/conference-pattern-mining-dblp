"""Association rules dari frequent itemsets (support, confidence, lift)."""
from __future__ import annotations

from itertools import combinations
from pathlib import Path
from typing import Dict, FrozenSet, Mapping, Optional, Sequence, Union

import pandas as pd

COLUMNS = ["antecedent", "consequent", "n_antecedent", "n_consequent", "count",
           "antecedent_count", "consequent_count"]


def load_itemsets(path: Union[str, Path]) -> Dict[FrozenSet[int], int]:
    """Membaca frequent itemsets hasil notebook 04 (kolom `itemset` dan `count`)."""
    df = pd.read_parquet(path, columns=["itemset", "count"])
    return {frozenset(int(i) for i in s): int(c) for s, c in zip(df["itemset"], df["count"])}


def rule_label(antecedent: Sequence[int], consequent: Sequence[int], names: Mapping[int, str]) -> str:
    def side(items):
        return " + ".join(names[i] for i in items)

    return f"{side(antecedent)} → {side(consequent)}"


def generate_rules(itemsets: Mapping[FrozenSet[int], int], n_transactions: int, min_confidence: float,
                   names: Optional[Mapping[int, str]] = None) -> pd.DataFrame:
    """Semua rule X -> Y dari setiap itemset berukuran >= 2 dengan confidence >= min_confidence.

    Setiap subset dari frequent itemset juga frequent, sehingga count X dan Y selalu tersedia di
    `itemsets`. Metrik dihitung dari count bulat:
    support = count(XY) / N, confidence = count(XY) / count(X), lift = count(XY) * N / (count(X) * count(Y)).
    """
    rows = []
    for itemset, count in itemsets.items():
        if len(itemset) < 2:
            continue
        items = sorted(itemset)
        for k in range(1, len(items)):
            for ante in combinations(items, k):
                ante_count = itemsets[frozenset(ante)]
                if count / ante_count < min_confidence:
                    continue
                cons = tuple(i for i in items if i not in ante)
                rows.append((ante, cons, k, len(cons), count, ante_count, itemsets[frozenset(cons)]))
    df = pd.DataFrame(rows, columns=COLUMNS)
    df["support"] = df["count"] / n_transactions
    df["confidence"] = df["count"] / df["antecedent_count"]
    df["lift"] = df["count"] * n_transactions / (df["antecedent_count"] * df["consequent_count"])
    df = df.sort_values(["lift", "confidence", "count", "antecedent", "consequent"],
                        ascending=[False, False, False, True, True], ignore_index=True)
    if names is not None:
        df["rule"] = [rule_label(a, c, names) for a, c in zip(df["antecedent"], df["consequent"])]
    return df
