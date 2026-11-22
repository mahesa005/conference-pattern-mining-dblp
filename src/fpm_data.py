"""Memuat transactional database dari tabel panjang (tid, item) hasil notebook 02."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, FrozenSet, List, Union

import numpy as np
import pandas as pd

PathLike = Union[str, Path]


def load_horizontal(path: PathLike) -> List[FrozenSet[int]]:
    long = pd.read_parquet(path, columns=["tid", "item"])
    tids = long["tid"].to_numpy()
    assert tids[0] == 0 and (np.diff(tids) >= 0).all() and len(np.unique(tids)) == tids[-1] + 1
    bounds = np.flatnonzero(np.diff(tids)) + 1
    return [frozenset(chunk.tolist()) for chunk in np.split(long["item"].to_numpy(), bounds)]


def load_item_names(path: PathLike) -> Dict[int, str]:
    items = pd.read_csv(path)
    return dict(zip(items["item_id"].astype(int), items["nama"]))
