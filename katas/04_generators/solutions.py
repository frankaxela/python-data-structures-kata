# katas/04_generators/solutions.py
from __future__ import annotations

if __name__ == "__main__":
    import os
    import tempfile
    from contextlib import contextmanager
    from typing import Any, Callable, Generator, Iterable

    def fibonacci() -> Generator[int, None, None]:
        # Two-variable swap avoids a temp variable; infinite generators are memory-free
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b

    def lazy_file_reader(filepath: str) -> Generator[str, None, None]:
        # Iterating the file object line-by-line is lazy by default in CPython
        with open(filepath, encoding="utf-8") as f:
            for line in f:
                yield line.rstrip("\n")

    def transform_pipeline(
        items: Iterable[str],
        min_length: int,
        transform: Callable[[str], str],
    ) -> Generator[str, None, None]:
        # Generator expression inside a generator keeps the pipeline fully lazy
        for item in items:
            if len(item) >= min_length:
                yield transform(item)

    @contextmanager
    def managed_temp_file(suffix: str = ".tmp") -> Generator[str, None, None]:
        # try/finally guarantees cleanup even when the caller raises inside the with-block
        fd, path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        try:
            yield path
        finally:
            if os.path.exists(path):
                os.unlink(path)

    def preorder_traversal(tree: dict[str, Any]) -> Generator[Any, None, None]:
        # yield from delegates to child generators without building intermediate lists
        yield tree["value"]
        for child in tree.get("children", []):
            yield from preorder_traversal(child)
