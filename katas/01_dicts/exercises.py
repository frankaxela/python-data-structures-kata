# katas/01_dicts/exercises.py
from __future__ import annotations

from collections import OrderedDict
from typing import Any, Callable


def frequency_counter(words: list[str]) -> dict[str, int]:
    """
    Count occurrences of each word in `words`.

    Use dict.get() with a default — not Counter — to practise the core pattern.

    Example:
        frequency_counter(["a", "b", "a", "c", "b", "a"])
        -> {"a": 3, "b": 2, "c": 1}
    """
    raise NotImplementedError


def flatten_nested_dict(d: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    """
    Flatten a nested dict by joining keys with dots.

    Example:
        flatten_nested_dict({"a": {"b": {"c": 1}}, "d": 2})
        -> {"a.b.c": 1, "d": 2}

    Constraints: arbitrarily deep nesting; non-dict leaf values preserved as-is.
    """
    raise NotImplementedError


def group_by(items: list[Any], key_fn: Callable[[Any], Any]) -> dict[Any, list[Any]]:
    """
    Partition `items` into groups keyed by `key_fn(item)`.

    Example:
        group_by(["cat", "car", "bar", "bat"], lambda w: w[0])
        -> {"c": ["cat", "car"], "b": ["bar", "bat"]}

    Preserve original order within each group.
    """
    raise NotImplementedError


def invert_dict(d: dict[Any, Any]) -> dict[Any, list[Any]]:
    """
    Invert a dict so values become keys. Collect duplicate values into lists.

    Example:
        invert_dict({"a": 1, "b": 2, "c": 1})
        -> {1: ["a", "c"], 2: ["b"]}
    """
    raise NotImplementedError


class LRUCache:
    """
    Least-Recently-Used cache with fixed capacity using OrderedDict.

    Both get() and put() must be O(1).

    Example:
        cache = LRUCache(2)
        cache.put(1, "a"); cache.put(2, "b")
        cache.get(1)        # "a"; marks 1 most-recent
        cache.put(3, "c")   # evicts 2 (LRU)
        cache.get(2)        # None
    """

    def __init__(self, capacity: int) -> None:
        raise NotImplementedError

    def get(self, key: int) -> str | None:
        raise NotImplementedError

    def put(self, key: int, value: str) -> None:
        raise NotImplementedError


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Recursively merge `override` into `base`; override values win.
    Nested dicts are merged recursively; non-dict values are replaced entirely.
    Must NOT mutate either input.

    Example:
        deep_merge({"a": {"x": 1, "y": 2}, "b": 3},
                   {"a": {"y": 99, "z": 0}, "c": 4})
        -> {"a": {"x": 1, "y": 99, "z": 0}, "b": 3, "c": 4}
    """
    raise NotImplementedError
