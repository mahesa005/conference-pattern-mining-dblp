"""Pengukuran performa Apriori dan FP-Growth untuk Task 6.

Apriori asli diharapkan di `src/apriori.py` dengan fungsi `apriori(transactions, min_support)` yang
mengembalikan objek beratribut `itemsets` (dict frozenset -> count) atau dict tersebut secara langsung.
Selama file itu belum ada, `load_apriori` memakai `standin_apriori`, pengganti sementara yang hanya
memanggil FP-Growth agar notebook 06 dapat diuji. Hasil dari pengganti ini tidak boleh dipakai sebagai
hasil perbandingan.
"""
from __future__ import annotations

import gc
import importlib
import time
from dataclasses import dataclass
from typing import Callable, Dict, FrozenSet, List, Optional, Sequence, Tuple

from fpgrowth import FPGrowthResult, fpgrowth

Itemsets = Dict[FrozenSet[int], int]
MiningFunction = Callable[[Sequence[FrozenSet[int]], float], object]


def standin_apriori(transactions: Sequence[FrozenSet[int]], min_support: float) -> FPGrowthResult:
    """PENGGANTI SEMENTARA, bukan Apriori. Memanggil FP-Growth agar alur notebook 06 dapat diuji."""
    return fpgrowth(transactions, min_support, keep_tree=False)


def load_apriori() -> Tuple[MiningFunction, bool]:
    """Mengembalikan (fungsi Apriori, apakah pengganti sementara)."""
    try:
        module = importlib.import_module("apriori")
    except ModuleNotFoundError as err:
        if err.name != "apriori":
            raise
        return standin_apriori, True
    return module.apriori, False


def itemsets_of(result: object) -> Itemsets:
    return dict(result.itemsets) if hasattr(result, "itemsets") else dict(result)


@dataclass
class TimedRun:
    algorithm: str
    min_support: float
    repeat: int
    seconds: float
    n_itemsets: int
    t_build: Optional[float] = None
    t_mine: Optional[float] = None


def time_runs(name: str, fn: MiningFunction, transactions: Sequence[FrozenSet[int]], min_support: float,
              repeats: int) -> Tuple[List[TimedRun], Itemsets]:
    """Menjalankan `fn` sebanyak `repeats` kali dan mengukur waktu dinding di sekitar pemanggilan.

    Waktu pemuatan data tidak termasuk. Hasil setiap pengulangan harus sama persis.
    """
    runs: List[TimedRun] = []
    reference: Optional[Itemsets] = None
    for repeat in range(repeats):
        gc.collect()
        start = time.perf_counter()
        result = fn(transactions, min_support)
        seconds = time.perf_counter() - start
        current = itemsets_of(result)
        if reference is None:
            reference = current
        elif current != reference:
            raise AssertionError(f"{name}: hasil berbeda antar pengulangan pada min support {min_support}")
        runs.append(TimedRun(name, min_support, repeat, seconds, len(current),
                             getattr(result, "t_build", None), getattr(result, "t_mine", None)))
        del result
    return runs, reference
