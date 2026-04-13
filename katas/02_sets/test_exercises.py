# katas/02_sets/test_exercises.py
from __future__ import annotations

import pytest

from exercises import (
    changelog_diff,
    deduplicate_ordered,
    has_interval_overlap,
    multiset_subtract,
    power_set,
    reachable_nodes,
)


@pytest.mark.parametrize("items,expected", [
    ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3], [3, 1, 4, 5, 9, 2, 6]),
    ([], []),
    ([1], [1]),
    ([1, 1, 1], [1]),
])
def test_deduplicate_ordered(items: list, expected: list) -> None:
    assert deduplicate_ordered(items) == expected


@pytest.mark.parametrize("graph,start,expected", [
    (
        {"a": {"b", "c"}, "b": {"a"}, "c": {"a", "d"}, "d": {"c"}, "e": {"f"}, "f": {"e"}},
        "a",
        {"a", "b", "c", "d"},
    ),
    ({"x": set()}, "x", {"x"}),
    ({}, "z", {"z"}),
])
def test_reachable_nodes(graph, start, expected) -> None:
    assert reachable_nodes(graph, start) == expected


@pytest.mark.parametrize("old,new,expected", [
    ({"a", "b", "c"}, {"b", "c", "d"}, {"added": {"d"}, "removed": {"a"}}),
    ({"a"}, {"a"}, {"added": set(), "removed": set()}),
    (set(), {"x"}, {"added": {"x"}, "removed": set()}),
])
def test_changelog_diff(old, new, expected) -> None:
    assert changelog_diff(old, new) == expected


@pytest.mark.parametrize("s,expected_size", [
    (frozenset({1, 2}), 4),
    (frozenset(), 1),
    (frozenset({1, 2, 3}), 8),
])
def test_power_set(s, expected_size) -> None:
    result = power_set(s)
    assert isinstance(result, set)
    assert len(result) == expected_size
    assert frozenset() in result
    assert s in result


@pytest.mark.parametrize("a,b,expected", [
    (["a", "a", "b", "c"], ["a", "b", "b"], ["a", "c"]),
    ([], [], []),
    (["x"], ["x"], []),
    (["a", "b"], ["c"], ["a", "b"]),
])
def test_multiset_subtract(a, b, expected) -> None:
    assert sorted(multiset_subtract(a, b)) == sorted(expected)


@pytest.mark.parametrize("intervals,expected", [
    ([(1, 3), (5, 8), (2, 4)], True),
    ([(1, 2), (4, 5), (7, 8)], False),
    ([], False),
    ([(1, 1)], False),
    ([(1, 3), (3, 5)], True),
])
def test_has_interval_overlap(intervals, expected) -> None:
    assert has_interval_overlap(intervals) == expected
