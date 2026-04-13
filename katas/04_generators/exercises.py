# katas/04_generators/exercises.py
from __future__ import annotations

from contextlib import contextmanager
from itertools import islice
from typing import Any, Callable, Generator, Iterable


def fibonacci() -> Generator[int, None, None]:
    """
    Yield the infinite Fibonacci sequence: 0, 1, 1, 2, 3, 5, 8, 13, ...

    Callers use itertools.islice to take a finite prefix.
    Must be implemented as a generator (use yield).

    Example:
        list(islice(fibonacci(), 7)) -> [0, 1, 1, 2, 3, 5, 8]
    """
    raise NotImplementedError


def lazy_file_reader(filepath: str) -> Generator[str, None, None]:
    """
    Yield lines from a file one at a time without loading the whole file into memory.
    Strip trailing newlines from each line.

    Constraint: must use `yield` inside a `with open(...)` block — never read() or readlines().
    """
    raise NotImplementedError


def transform_pipeline(
    items: Iterable[str],
    min_length: int,
    transform: Callable[[str], str],
) -> Generator[str, None, None]:
    """
    Lazy pipeline: filter items shorter than `min_length`, then apply `transform`.
    Must be a generator (not a list comprehension).

    Example:
        list(transform_pipeline(["hi", "hello", "hey"], 4, str.upper))
        -> ["HELLO"]
    """
    raise NotImplementedError


@contextmanager
def managed_temp_file(suffix: str = ".tmp") -> Generator[str, None, None]:
    """
    Context manager that creates a named temporary file, yields its path,
    and deletes it on exit (even if an exception is raised).

    Example:
        with managed_temp_file(".txt") as path:
            Path(path).write_text("hello")
        # file no longer exists after the block
    """
    raise NotImplementedError


def preorder_traversal(tree: dict[str, Any]) -> Generator[Any, None, None]:
    """
    Yield values from a nested tree dict in pre-order (root before children).
    Tree shape: {"value": X, "children": [subtree, ...]}

    Use `yield from` for recursive delegation — do not accumulate into a list.

    Example:
        tree = {"value": 1, "children": [
            {"value": 2, "children": []},
            {"value": 3, "children": [{"value": 4, "children": []}]},
        ]}
        list(preorder_traversal(tree)) -> [1, 2, 3, 4]
    """
    raise NotImplementedError
