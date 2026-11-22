from types import SimpleNamespace

import pytest

import benchmark
from benchmark import load_apriori, standin_apriori, time_runs
from fpgrowth import fpgrowth

TEXTBOOK = [frozenset(t) for t in (
    [1, 2, 5], [2, 4], [2, 3], [1, 2, 4], [1, 3],
    [2, 3], [1, 3], [1, 2, 3, 5], [1, 2, 3],
)]


def test_load_apriori_falls_back_to_standin(monkeypatch):
    def missing(name):
        raise ModuleNotFoundError(f"No module named '{name}'", name=name)

    monkeypatch.setattr(benchmark.importlib, "import_module", missing)
    fn, is_standin = load_apriori()
    assert is_standin
    assert fn is standin_apriori


def test_load_apriori_uses_real_module(monkeypatch):
    def real(transactions, min_support):
        return {}

    monkeypatch.setattr(benchmark.importlib, "import_module", lambda name: SimpleNamespace(apriori=real))
    fn, is_standin = load_apriori()
    assert not is_standin
    assert fn is real


def test_load_apriori_reraises_missing_dependency(monkeypatch):
    def broken(name):
        raise ModuleNotFoundError("No module named 'somedep'", name="somedep")

    monkeypatch.setattr(benchmark.importlib, "import_module", broken)
    with pytest.raises(ModuleNotFoundError):
        load_apriori()


def test_standin_matches_fpgrowth():
    assert standin_apriori(TEXTBOOK, 2 / 9).itemsets == fpgrowth(TEXTBOOK, 2 / 9).itemsets


def test_time_runs_records_every_repeat():
    runs, itemsets = time_runs("FP-Growth", lambda tx, ms: fpgrowth(tx, ms, keep_tree=False), TEXTBOOK, 2 / 9, 3)
    assert [r.repeat for r in runs] == [0, 1, 2]
    assert all(r.seconds >= 0 and r.n_itemsets == 13 for r in runs)
    assert all(r.t_build is not None and r.t_mine is not None for r in runs)
    assert len(itemsets) == 13


def test_time_runs_accepts_plain_dict():
    runs, itemsets = time_runs("dict", lambda tx, ms: {frozenset([1]): 6}, TEXTBOOK, 0.5, 2)
    assert itemsets == {frozenset([1]): 6}
    assert runs[0].t_build is None


def test_time_runs_rejects_changing_results():
    outputs = iter([{frozenset([1]): 6}, {frozenset([1]): 5}])
    with pytest.raises(AssertionError):
        time_runs("flaky", lambda tx, ms: next(outputs), TEXTBOOK, 0.5, 2)
