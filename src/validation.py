"""Validasi hasil FP-Growth terhadap mlxtend."""
from __future__ import annotations

from typing import Dict, FrozenSet, Mapping, Sequence

import numpy as np
import pandas as pd
from scipy import sparse


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
    keep = np.flatnonzero(matrix.getnnz(axis=0) / n >= min_support)
    if len(keep) == 0:
        return {}
    # mlxtend menolak nama kolom integer yang tidak dimulai dari 0, jadi kolom diberi nama string.
    df = pd.DataFrame.sparse.from_spmatrix(matrix[:, keep], columns=[str(i) for i in items[keep]])
    res = mlx_fpgrowth(df, min_support=min_support, use_colnames=True)
    return {frozenset(int(i) for i in s): int(round(sup * n)) for s, sup in zip(res["itemsets"], res["support"])}


def compare_itemsets(ours: Mapping[FrozenSet[int], int], ref: Mapping[FrozenSet[int], int]) -> dict:
    missing = set(ref) - set(ours)
    extra = set(ours) - set(ref)
    mismatch = [s for s in set(ours) & set(ref) if ours[s] != ref[s]]
    return {
        "n_ours": len(ours), "n_ref": len(ref), "missing": len(missing), "extra": len(extra),
        "count_mismatch": len(mismatch), "identical": not (missing or extra or mismatch),
    }
