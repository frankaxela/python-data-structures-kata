# katas/02_sets/exercises.py
from __future__ import annotations

from collections import Counter
from typing import Any, TypeVar

T = TypeVar("T")


def deduplicate_ordered(items: list[Any]) -> list[Any]:
    """
    Remove duplicates from `items` while preserving original order.

    A plain set() loses order. Find an O(n) approach that does not.

    Example:
        deduplicate_ordered([3, 1, 4, 1, 5, 9, 2, 6, 5, 3])
        -> [3, 1, 4, 5, 9, 2, 6]
    """
    raise NotImplementedError


def reachable_nodes(graph: dict[str, set[str]], start: str) -> set[str]:
    """
    Return all nodes reachable from `start` in an undirected graph
    (represented as an adjacency set dict), including `start` itself.

    Example:
        graph = {"a": {"b", "c"}, "b": {"a"}, "c": {"a", "d"}, "d": {"c"}, "e": {"f"}, "f": {"e"}}
        reachable_nodes(graph, "a") -> {"a", "b", "c", "d"}
    """
    raise NotImplementedError


def changelog_diff(old_items: set[str], new_items: set[str]) -> dict[str, set[str]]:
    """
    Given two snapshots of a collection, return what was added and removed.

    Example:
        changelog_diff({"a", "b", "c"}, {"b", "c", "d"})
        -> {"added": {"d"}, "removed": {"a"}}

    Return {"added": set(), "removed": set()} when nothing changed.
    """
    raise NotImplementedError


def power_set(s: frozenset[Any]) -> set[frozenset[Any]]:
    """
    Return all subsets of `s`, including the empty set and `s` itself.

    Example:
        power_set(frozenset({1, 2}))
        -> {frozenset(), frozenset({1}), frozenset({2}), frozenset({1, 2})}

    Constraint: result must be a set of frozensets (hashable subsets).
    """
    raise NotImplementedError


def multiset_subtract(a: list[Any], b: list[Any]) -> list[Any]:
    """
    Return elements in `a` that remain after removing all occurrences found in `b`,
    respecting multiplicity (multiset subtraction).

    Use Counter arithmetic — do not write a nested loop.

    Example:
        multiset_subtract(["a", "a", "b", "c"], ["a", "b", "b"])
        -> ["a", "c"]   (one "a" remains; one extra "b" in b is ignored)
    """
    raise NotImplementedError


def has_interval_overlap(intervals: list[tuple[int, int]]) -> bool:
    """
    Return True if any two intervals in the list overlap (share at least one integer point).
    Intervals are inclusive: (1, 3) and (3, 5) DO overlap.

    Example:
        has_interval_overlap([(1, 3), (5, 8), (2, 4)]) -> True
        has_interval_overlap([(1, 2), (4, 5), (7, 8)]) -> False
    """
    raise NotImplementedError
