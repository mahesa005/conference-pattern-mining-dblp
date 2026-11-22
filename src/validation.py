"""Validasi hasil FP-Growth dan association rules terhadap mlxtend."""
from __future__ import annotations

import math
from typing import Dict, FrozenSet, Mapping, Sequence, Tuple

import numpy as np
import pandas as pd
from scipy import sparse

from fpgrowth import min_count_for


def mlxtend_reference(transactions: Sequence[FrozenSet[int]], min_support: float) -> Dict[FrozenSet[int], int]:
    from mlxtend.frequent_patterns import fpgrowth as mlx_fpgrowth

    n = len(transactions)
    lengths = np.fromiter((len(t) for t in transactions), dtype=np.int64, count=n)
    total = int(lengths.sum())
    if total == 0:
        return {}
    rows = np.repeat(np.arange(n), lengths)
    cols = np.fromiter((i for t in transactions for i in t), dtype=np.int64, count=total)
    items, col_idx = np.unique(cols, return_inverse=True)
    matrix = sparse.csr_matrix((np.ones(total, dtype=bool), (rows, col_idx)), shape=(n, len(items)))
    min_count = min_count_for(min_support, n)
    keep = np.flatnonzero(matrix.getnnz(axis=0) >= min_count)
    if len(keep) == 0:
        return {}
    # Baris tanpa item frequent tidak memuat itemset frequent apa pun, jadi dibuang agar mlxtend
    # (yang sempat membuat salinan dense) muat di memori. Ambang diubah ke jumlah baris tersisa:
    # count / m >= (min_count - 0,5) / m setara dengan count >= min_count untuk count bulat.
    reduced = matrix[:, keep]
    reduced = reduced[reduced.getnnz(axis=1) > 0]
    m = reduced.shape[0]
    # mlxtend menolak nama kolom integer yang tidak dimulai dari 0, jadi kolom diberi nama string.
    df = pd.DataFrame.sparse.from_spmatrix(reduced, columns=[str(i) for i in items[keep]])
    res = mlx_fpgrowth(df, min_support=(min_count - 0.5) / m, use_colnames=True)
    return {frozenset(int(i) for i in s): int(round(sup * m)) for s, sup in zip(res["itemsets"], res["support"])}


def compare_itemsets(ours: Mapping[FrozenSet[int], int], ref: Mapping[FrozenSet[int], int]) -> dict:
    missing = set(ref) - set(ours)
    extra = set(ours) - set(ref)
    mismatch = [s for s in set(ours) & set(ref) if ours[s] != ref[s]]
    return {
        "n_ours": len(ours), "n_ref": len(ref), "missing": len(missing), "extra": len(extra),
        "count_mismatch": len(mismatch), "identical": not (missing or extra or mismatch),
    }


RuleKey = Tuple[FrozenSet[int], FrozenSet[int]]


def mlxtend_rules_reference(itemsets: Mapping[FrozenSet[int], int], n_transactions: int,
                            min_confidence: float) -> Dict[RuleKey, Tuple[float, float, float]]:
    """Rules dari mlxtend.association_rules: {(antecedent, consequent): (support, confidence, lift)}."""
    from mlxtend.frequent_patterns import association_rules

    if not any(len(s) >= 2 for s in itemsets):
        return {}
    df = pd.DataFrame({
        "support": [c / n_transactions for c in itemsets.values()],
        "itemsets": [frozenset(str(i) for i in s) for s in itemsets],
    })
    res = association_rules(df, num_itemsets=n_transactions, metric="confidence", min_threshold=min_confidence)

    def to_ids(s):
        return frozenset(int(i) for i in s)

    cols = ["antecedents", "consequents", "support", "confidence", "lift"]
    return {(to_ids(a), to_ids(c)): (s, cf, l) for a, c, s, cf, l in res[cols].itertuples(index=False)}


def compare_rules(ours: pd.DataFrame, ref: Mapping[RuleKey, Tuple[float, float, float]], rel_tol: float = 1e-9) -> dict:
    cols = ["antecedent", "consequent", "support", "confidence", "lift"]
    mine = {(frozenset(a), frozenset(c)): (s, cf, l) for a, c, s, cf, l in ours[cols].itertuples(index=False)}
    missing = set(ref) - set(mine)
    extra = set(mine) - set(ref)
    mismatch = [k for k in set(mine) & set(ref)
                if not all(math.isclose(x, y, rel_tol=rel_tol) for x, y in zip(mine[k], ref[k]))]
    return {"n_ours": len(mine), "n_ref": len(ref), "missing": len(missing), "extra": len(extra),
            "metric_mismatch": len(mismatch), "identical": not (missing or extra or mismatch)}
