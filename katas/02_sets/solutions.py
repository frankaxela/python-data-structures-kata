# katas/02_sets/solutions.py
from __future__ import annotations

if __name__ == "__main__":
    from collections import Counter
    from typing import Any

    def deduplicate_ordered(items: list[Any]) -> list[Any]:
        # dict.fromkeys preserves insertion order (CPython 3.7+) and removes dups in O(n)
        return list(dict.fromkeys(items))

    def reachable_nodes(graph: dict[str, set[str]], start: str) -> set[str]:
        # BFS with a visited set prevents revisiting; set operations are O(1) average
        visited: set[str] = set()
        frontier = {start}
        while frontier:
            visited |= frontier
            frontier = {n for node in frontier for n in graph.get(node, set()) if n not in visited}
        return visited

    def changelog_diff(old_items: set[str], new_items: set[str]) -> dict[str, set[str]]:
        # Set difference reads like the English description — added is new minus old
        return {"added": new_items - old_items, "removed": old_items - new_items}

    def power_set(s: frozenset[Any]) -> set[frozenset[Any]]:
        # Iterative bit-mask approach: each integer 0..2^n-1 encodes a subset
        items = list(s)
        return {frozenset(item for j, item in enumerate(items) if mask >> j & 1)
                for mask in range(1 << len(items))}

    def multiset_subtract(a: list[Any], b: list[Any]) -> list[Any]:
        # Counter subtraction drops negatives automatically, then elements() rebuilds list
        return list((Counter(a) - Counter(b)).elements())

    def has_interval_overlap(intervals: list[tuple[int, int]]) -> bool:
        # Convert each interval to an integer set; union of sets detects overlap via len comparison
        covered: list[set[int]] = [set(range(lo, hi + 1)) for lo, hi in intervals]
        total = sum(len(s) for s in covered)
        return len(set().union(*covered)) < total
