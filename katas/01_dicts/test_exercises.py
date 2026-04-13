# katas/01_dicts/test_exercises.py
from __future__ import annotations

import pytest

from exercises import (
    LRUCache,
    deep_merge,
    flatten_nested_dict,
    frequency_counter,
    group_by,
    invert_dict,
)


@pytest.mark.parametrize("words,expected", [
    (["a", "b", "a", "c", "b", "a"], {"a": 3, "b": 2, "c": 1}),
    (["x"], {"x": 1}),
    ([], {}),
    (["z", "z", "z"], {"z": 3}),
])
def test_frequency_counter(words: list[str], expected: dict[str, int]) -> None:
    assert frequency_counter(words) == expected


@pytest.mark.parametrize("d,expected", [
    ({"a": {"b": {"c": 1}}, "d": 2}, {"a.b.c": 1, "d": 2}),
    ({}, {}),
    ({"a": 1}, {"a": 1}),
    ({"a": {"b": 1}, "c": {"d": {"e": 2}}}, {"a.b": 1, "c.d.e": 2}),
])
def test_flatten_nested_dict(d: dict, expected: dict) -> None:
    assert flatten_nested_dict(d) == expected


@pytest.mark.parametrize("items,key_fn,expected", [
    (["cat", "car", "bar", "bat"], lambda w: w[0], {"c": ["cat", "car"], "b": ["bar", "bat"]}),
    ([], lambda x: x, {}),
    ([1, 2, 3, 4], lambda x: x % 2, {1: [1, 3], 0: [2, 4]}),
])
def test_group_by(items, key_fn, expected) -> None:
    assert group_by(items, key_fn) == expected


@pytest.mark.parametrize("d,expected", [
    ({"a": 1, "b": 2, "c": 1}, {1: ["a", "c"], 2: ["b"]}),
    ({}, {}),
    ({"only": "one"}, {"one": ["only"]}),
])
def test_invert_dict(d: dict, expected: dict) -> None:
    assert invert_dict(d) == expected


def test_lru_cache_basic() -> None:
    cache = LRUCache(2)
    cache.put(1, "a")
    cache.put(2, "b")
    assert cache.get(1) == "a"
    cache.put(3, "c")
    assert cache.get(2) is None
    assert cache.get(3) == "c"


def test_lru_cache_update_existing() -> None:
    cache = LRUCache(2)
    cache.put(1, "a")
    cache.put(2, "b")
    cache.put(1, "z")
    cache.put(3, "c")       # evicts 2, not 1
    assert cache.get(1) == "z"
    assert cache.get(2) is None


def test_lru_cache_capacity_one() -> None:
    cache = LRUCache(1)
    cache.put(1, "a")
    cache.put(2, "b")
    assert cache.get(1) is None
    assert cache.get(2) == "b"


@pytest.mark.parametrize("base,override,expected", [
    (
        {"a": {"x": 1, "y": 2}, "b": 3},
        {"a": {"y": 99, "z": 0}, "c": 4},
        {"a": {"x": 1, "y": 99, "z": 0}, "b": 3, "c": 4},
    ),
    ({}, {"a": 1}, {"a": 1}),
    ({"a": 1}, {}, {"a": 1}),
    ({"a": {"b": 1}}, {"a": 2}, {"a": 2}),  # non-dict replaces nested dict
])
def test_deep_merge(base: dict, override: dict, expected: dict) -> None:
    result = deep_merge(base, override)
    assert result == expected
