# katas/03_comprehensions/exercises.py
from __future__ import annotations

from typing import Any, Callable


def flatten_list(nested: list[list[Any]]) -> list[Any]:
    """
    Flatten one level of nesting into a single list — as a one-liner comprehension.

    Example:
        flatten_list([[1, 2], [3, 4], [5]])
        -> [1, 2, 3, 4, 5]

    Constraint: must be a single list comprehension expression.
    """
    raise NotImplementedError


def transform_dict(
    d: dict[str, Any],
    predicate: Callable[[str, Any], bool],
    transform: Callable[[str, Any], tuple[str, Any]],
) -> dict[str, Any]:
    """
    Build a new dict from `d` keeping only entries where predicate(key, value)
    is True, then applying transform(key, value) -> (new_key, new_value).

    Example:
        transform_dict(
            {"a": 1, "b": -2, "c": 3},
            predicate=lambda k, v: v > 0,
            transform=lambda k, v: (k.upper(), v * 10),
        )
        -> {"A": 10, "C": 30}

    Constraint: must be a single dict comprehension expression.
    """
    raise NotImplementedError


def parse_csv_records(lines: list[str], fields: list[str]) -> list[dict[str, str]]:
    """
    Parse CSV lines (no header row) into a list of dicts using `fields` as keys.
    Skip blank lines.

    Example:
        parse_csv_records(["alice,30,eng", "bob,25,mkt", ""], ["name", "age", "dept"])
        -> [{"name": "alice", "age": "30", "dept": "eng"},
            {"name": "bob",   "age": "25", "dept": "mkt"}]

    Constraint: the outer list and inner dicts must both be comprehensions.
    """
    raise NotImplementedError


def transpose_matrix(matrix: list[list[int]]) -> list[list[int]]:
    """
    Transpose a 2D matrix (rows become columns).

    Example:
        transpose_matrix([[1, 2, 3], [4, 5, 6]])
        -> [[1, 4], [2, 5], [3, 6]]

    Constraint: use zip(*matrix) inside a comprehension — no manual indexing.
    """
    raise NotImplementedError


def comprehension_vs_generator(data: list[int]) -> dict[str, Any]:
    """
    Compute the sum of squares for `data` two ways: list comprehension and generator expression.
    Return a dict with keys "list_result" and "gen_result" containing the sums,
    and "are_equal" (bool) confirming they match.

    Example:
        comprehension_vs_generator([1, 2, 3])
        -> {"list_result": 14, "gen_result": 14, "are_equal": True}

    This exercise exists to highlight when each form is preferable:
    list comprehension materialises all values (random access, reusable);
    generator expression is lazy (O(1) memory, single-pass only).
    """
    raise NotImplementedError


def pipeline_transform(
    records: list[dict[str, Any]],
    min_score: int,
) -> list[str]:
    """
    From a list of {"name": str, "score": int} records:
    1. Keep only records where score >= min_score
    2. Format each as "NAME: score" (name uppercased)
    3. Sort alphabetically

    Example:
        pipeline_transform(
            [{"name": "alice", "score": 90}, {"name": "bob", "score": 40}, {"name": "cara", "score": 85}],
            min_score=80,
        )
        -> ["ALICE: 90", "CARA: 85"]

    Constraint: solve in one chained comprehension expression (filter inside, sorted outside).
    """
    raise NotImplementedError
