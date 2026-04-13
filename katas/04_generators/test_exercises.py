# katas/04_generators/test_exercises.py
from __future__ import annotations

import os
from itertools import islice
from pathlib import Path

import pytest

from exercises import (
    fibonacci,
    lazy_file_reader,
    managed_temp_file,
    preorder_traversal,
    transform_pipeline,
)


def test_fibonacci_first_ten() -> None:
    assert list(islice(fibonacci(), 10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_fibonacci_single() -> None:
    assert list(islice(fibonacci(), 1)) == [0]


def test_fibonacci_empty() -> None:
    assert list(islice(fibonacci(), 0)) == []


def test_lazy_file_reader(tmp_path: Path) -> None:
    f = tmp_path / "test.txt"
    f.write_text("line1\nline2\nline3\n")
    result = list(lazy_file_reader(str(f)))
    assert result == ["line1", "line2", "line3"]


def test_lazy_file_reader_empty(tmp_path: Path) -> None:
    f = tmp_path / "empty.txt"
    f.write_text("")
    assert list(lazy_file_reader(str(f))) == []


@pytest.mark.parametrize("items,min_len,transform,expected", [
    (["hi", "hello", "hey"], 4, str.upper, ["HELLO"]),
    ([], 1, str.upper, []),
    (["a", "bb", "ccc"], 2, lambda s: s * 2, ["bbbb", "cccccc"]),
])
def test_transform_pipeline(items, min_len, transform, expected) -> None:
    assert list(transform_pipeline(items, min_len, transform)) == expected


def test_managed_temp_file_creates_and_cleans_up() -> None:
    with managed_temp_file(".txt") as path:
        assert os.path.exists(path)
        assert path.endswith(".txt")
        Path(path).write_text("hello")
    assert not os.path.exists(path)


def test_managed_temp_file_cleans_up_on_exception() -> None:
    saved_path: list[str] = []
    with pytest.raises(RuntimeError):
        with managed_temp_file() as path:
            saved_path.append(path)
            raise RuntimeError("test")
    assert not os.path.exists(saved_path[0])


@pytest.mark.parametrize("tree,expected", [
    (
        {"value": 1, "children": [
            {"value": 2, "children": []},
            {"value": 3, "children": [{"value": 4, "children": []}]},
        ]},
        [1, 2, 3, 4],
    ),
    ({"value": 42, "children": []}, [42]),
])
def test_preorder_traversal(tree, expected) -> None:
    assert list(preorder_traversal(tree)) == expected
