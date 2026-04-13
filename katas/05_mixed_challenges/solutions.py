# katas/05_mixed_challenges/solutions.py
from __future__ import annotations

if __name__ == "__main__":
    import heapq
    import re
    from collections import Counter, deque
    from typing import Iterable

    def top_words(text: str, n: int) -> list[tuple[str, int]]:
        # re.findall extracts alphabetic tokens cleanly; Counter does counting + ranking in one step
        words = re.findall(r"[a-z]+", text.lower())
        return Counter(words).most_common(n)

    def group_anagrams(words: list[str]) -> list[list[str]]:
        # Sorting the letters gives a canonical anagram key; dict groups them
        groups: dict[str, list[str]] = {}
        for word in words:
            key = "".join(sorted(word))
            groups.setdefault(key, []).append(word)
        return [sorted(group) for group in groups.values()]

    def sliding_window_max(nums: list[int], k: int) -> list[int]:
        # Monotonic deque stores indices in decreasing value order; front is always the max
        dq: deque[int] = deque()
        result: list[int] = []
        for i, val in enumerate(nums):
            while dq and nums[dq[-1]] <= val:
                dq.pop()
            dq.append(i)
            if dq[0] < i - k + 1:
                dq.popleft()
            if i >= k - 1:
                result.append(nums[dq[0]])
        return result

    def top_n_from_stream(stream: Iterable[int], n: int) -> list[int]:
        # heapq.nlargest is O(m log n) where m is stream length; no full sort needed
        return heapq.nlargest(n, stream)

    def bfs_shortest_path(
        graph: dict[str, list[str]],
        start: str,
        end: str,
    ) -> list[str] | None:
        # Store full path in deque to reconstruct it without a parent map
        if start == end:
            return [start]
        queue: deque[list[str]] = deque([[start]])
        visited: set[str] = {start}
        while queue:
            path = queue.popleft()
            for neighbour in graph.get(path[-1], []):
                if neighbour == end:
                    return path + [neighbour]
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(path + [neighbour])
        return None
