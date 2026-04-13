# katas/03_comprehensions/test_exercises.py
from __future__ import annotations

import pytest

from exercises import (
    comprehension_vs_generator,
    flatten_list,
    parse_csv_records,
    pipeline_transform,
    transform_dict,
    transpose_matrix,
)


@pytest.mark.parametrize("nested,expected", [
    ([[1, 2], [3, 4], [5]], [1, 2, 3, 4, 5]),
    ([], []),
    ([[]], []),
    ([[1]], [1]),
])
def test_flatten_list(nested: list, expected: list) -> None:
    assert flatten_list(nested) == expected


@pytest.mark.parametrize("d,pred,transform,expected", [
    (
        {"a": 1, "b": -2, "c": 3},
        lambda k, v: v > 0,
        lambda k, v: (k.upper(), v * 10),
        {"A": 10, "C": 30},
    ),
    ({}, lambda k, v: True, lambda k, v: (k, v), {}),
    ({"x": 0}, lambda k, v: v != 0, lambda k, v: (k, v), {}),
])
def test_transform_dict(d, pred, transform, expected) -> None:
    assert transform_dict(d, pred, transform) == expected


@pytest.mark.parametrize("lines,fields,expected", [
    (
        ["alice,30,eng", "bob,25,mkt", ""],
        ["name", "age", "dept"],
        [{"name": "alice", "age": "30", "dept": "eng"},
         {"name": "bob", "age": "25", "dept": "mkt"}],
    ),
    ([], ["a", "b"], []),
    (["  ", "1,2"], ["x", "y"], [{"x": "1", "y": "2"}]),
])
def test_parse_csv_records(lines, fields, expected) -> None:
    assert parse_csv_records(lines, fields) == expected


@pytest.mark.parametrize("matrix,expected", [
    ([[1, 2, 3], [4, 5, 6]], [[1, 4], [2, 5], [3, 6]]),
    ([[1]], [[1]]),
    ([[1, 2]], [[1], [2]]),
])
def test_transpose_matrix(matrix, expected) -> None:
    assert transpose_matrix(matrix) == expected


@pytest.mark.parametrize("data,expected_sum", [
    ([1, 2, 3], 14),
    ([], 0),
    ([5], 25),
])
def test_comprehension_vs_generator(data, expected_sum) -> None:
    result = comprehension_vs_generator(data)
    assert result["list_result"] == expected_sum
    assert result["gen_result"] == expected_sum
    assert result["are_equal"] is True


@pytest.mark.parametrize("records,min_score,expected", [
    (
        [{"name": "alice", "score": 90}, {"name": "bob", "score": 40}, {"name": "cara", "score": 85}],
        80,
        ["ALICE: 90", "CARA: 85"],
    ),
    ([], 50, []),
    ([{"name": "x", "score": 50}], 50, ["X: 50"]),
    ([{"name": "x", "score": 49}], 50, []),
])
def test_pipeline_transform(records, min_score, expected) -> None:
    assert pipeline_transform(records, min_score) == expected
