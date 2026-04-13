# katas/05_mixed_challenges/exercises.py
from __future__ import annotations

import heapq
from collections import Counter, deque
from typing import Any, Iterable


def top_words(text: str, n: int) -> list[tuple[str, int]]:
    """
    Return the `n` most common words in `text` (case-insensitive, ignore punctuation),
    ordered by frequency descending. Ties broken alphabetically.

    Use Counter.most_common() — do not sort manually.

    Example:
        top_words("the cat sat on the mat the cat", 2)
        -> [("the", 3), ("cat", 2)]
    """
    raise NotImplementedError


def group_anagrams(words: list[str]) -> list[list[str]]:
    """
    Group `words` into lists of anagrams. Order of groups and order within
    each group do not matter, but each group must be sorted alphabetically.

    Example:
        group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"])
        -> [["ate", "eat", "tea"], ["nat", "tan"], ["bat"]]
    """
    raise NotImplementedError


def sliding_window_max(nums: list[int], k: int) -> list[int]:
    """
    For each window of size `k` sliding across `nums`, return the maximum.
    Use a monotonic deque for O(n) time — not a nested loop.

    Example:
        sliding_window_max([1, 3, -1, -3, 5, 3, 6, 7], 3)
        -> [3, 3, 5, 5, 6, 7]
    """
    raise NotImplementedError


def top_n_from_stream(stream: Iterable[int], n: int) -> list[int]:
    """
    Return the `n` largest values from `stream` without loading all values into memory.
    Use heapq — maintain a min-heap of size n.

    Example:
        top_n_from_stream(iter([3, 1, 4, 1, 5, 9, 2, 6, 5, 3]), 3)
        -> [9, 6, 5]  (order within the result does not matter)
    """
    raise NotImplementedError


def bfs_shortest_path(
    graph: dict[str, list[str]],
    start: str,
    end: str,
) -> list[str] | None:
    """
    Return the shortest path from `start` to `end` in an unweighted directed graph
    (adjacency list), or None if no path exists.

    Use a deque as the BFS frontier — not a list with pop(0).

    Example:
        bfs_shortest_path({"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}, "a", "d")
        -> ["a", "b", "d"]  or  ["a", "c", "d"]  (either valid shortest path)
    """
    raise NotImplementedError
