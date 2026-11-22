import pandas as pd

from fpm_data import load_horizontal, load_item_names


def test_load_horizontal(tmp_path):
    path = tmp_path / "tx.parquet"
    pd.DataFrame({"tid": [0, 0, 1, 2, 2, 2], "item": [3, 5, 1, 0, 2, 4]}, dtype="int32").to_parquet(path, index=False)
    assert load_horizontal(path) == [frozenset({3, 5}), frozenset({1}), frozenset({0, 2, 4})]


def test_load_item_names(tmp_path):
    path = tmp_path / "items.csv"
    pd.DataFrame({"venue": ["a", "b"], "item_id": [0, 1], "nama": ["AAA", "BBB"]}).to_csv(path, index=False)
    assert load_item_names(path) == {0: "AAA", 1: "BBB"}
