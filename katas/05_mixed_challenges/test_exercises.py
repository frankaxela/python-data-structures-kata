# katas/05_mixed_challenges/test_exercises.py
from __future__ import annotations

import pytest

from exercises import (
    bfs_shortest_path,
    group_anagrams,
    sliding_window_max,
    top_n_from_stream,
    top_words,
)


@pytest.mark.parametrize("text,n,expected", [
    ("the cat sat on the mat the cat", 2, [("the", 3), ("cat", 2)]),
    ("", 5, []),
    ("a", 1, [("a", 1)]),
])
def test_top_words(text, n, expected) -> None:
    assert top_words(text, n) == expected


@pytest.mark.parametrize("words,expected_groups", [
    (
        ["eat", "tea", "tan", "ate", "nat", "bat"],
        [["ate", "eat", "tea"], ["nat", "tan"], ["bat"]],
    ),
    ([], []),
    (["a"], [["a"]]),
])
def test_group_anagrams(words, expected_groups) -> None:
    result = [sorted(g) for g in group_anagrams(words)]
    assert sorted(result) == sorted(expected_groups)


@pytest.mark.parametrize("nums,k,expected", [
    ([1, 3, -1, -3, 5, 3, 6, 7], 3, [3, 3, 5, 5, 6, 7]),
    ([1], 1, [1]),
    ([4, 3, 2, 1], 2, [4, 3, 2]),
])
def test_sliding_window_max(nums, k, expected) -> None:
    assert sliding_window_max(nums, k) == expected


@pytest.mark.parametrize("stream,n,expected_set", [
    ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3], 3, {9, 6, 5}),
    ([1], 1, {1}),
    ([], 3, set()),
])
def test_top_n_from_stream(stream, n, expected_set) -> None:
    assert set(top_n_from_stream(iter(stream), n)) == expected_set


@pytest.mark.parametrize("graph,start,end,expected_len", [
    ({"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}, "a", "d", 3),
    ({"a": ["b"], "b": []}, "a", "b", 2),
    ({"a": ["b"], "b": []}, "a", "z", None),
    ({"a": []}, "a", "a", 1),
])
def test_bfs_shortest_path(graph, start, end, expected_len) -> None:
    result = bfs_shortest_path(graph, start, end)
    if expected_len is None:
        assert result is None
    else:
        assert result is not None
        assert len(result) == expected_len
        assert result[0] == start
        assert result[-1] == end
