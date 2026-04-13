# katas/01_dicts/solutions.py
from __future__ import annotations

if __name__ == "__main__":
    from collections import OrderedDict
    from typing import Any, Callable

    def frequency_counter(words: list[str]) -> dict[str, int]:
        # dict.get with default 0 avoids a separate existence check — more Pythonic than setdefault for simple counting
        counts: dict[str, int] = {}
        for word in words:
            counts[word] = counts.get(word, 0) + 1
        return counts

    def flatten_nested_dict(d: dict[str, Any], prefix: str = "") -> dict[str, Any]:
        # Recursion with prefix accumulation mirrors the tree shape; update() merges sub-results without a temp list
        result: dict[str, Any] = {}
        for key, value in d.items():
            full_key = f"{prefix}.{key}" if prefix else key
            if isinstance(value, dict):
                result.update(flatten_nested_dict(value, full_key))
            else:
                result[full_key] = value
        return result

    def group_by(items: list[Any], key_fn: Callable[[Any], Any]) -> dict[Any, list[Any]]:
        # setdefault beats defaultdict when you want explicit typing and no import overhead
        groups: dict[Any, list[Any]] = {}
        for item in items:
            groups.setdefault(key_fn(item), []).append(item)
        return groups

    def invert_dict(d: dict[Any, Any]) -> dict[Any, list[Any]]:
        # Same setdefault pattern — accumulate original keys under each value
        result: dict[Any, list[Any]] = {}
        for k, v in d.items():
            result.setdefault(v, []).append(k)
        return result

    class LRUCache:
        def __init__(self, capacity: int) -> None:
            self._cap = capacity
            # OrderedDict.move_to_end + popitem(last=False) gives O(1) LRU eviction
            self._cache: OrderedDict[int, str] = OrderedDict()

        def get(self, key: int) -> str | None:
            if key not in self._cache:
                return None
            self._cache.move_to_end(key)
            return self._cache[key]

        def put(self, key: int, value: str) -> None:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = value
            if len(self._cache) > self._cap:
                self._cache.popitem(last=False)  # evict front = least recently used

    def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
        # Start from a shallow copy of base so we never mutate the input
        result = dict(base)
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result
