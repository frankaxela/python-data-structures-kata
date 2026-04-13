# katas/03_comprehensions/solutions.py
from __future__ import annotations

if __name__ == "__main__":
    from typing import Any, Callable

    def flatten_list(nested: list[list[Any]]) -> list[Any]:
        # Double-loop comprehension reads left-to-right like English: "x from sub, for sub in nested"
        return [x for sub in nested for x in sub]

    def transform_dict(
        d: dict[str, Any],
        predicate: Callable[[str, Any], bool],
        transform: Callable[[str, Any], tuple[str, Any]],
    ) -> dict[str, Any]:
        # Dict comprehension with inline filtering; k2/v2 from transform keep names clean
        return {k2: v2 for k, v in d.items() if predicate(k, v) for k2, v2 in [transform(k, v)]}

    def parse_csv_records(lines: list[str], fields: list[str]) -> list[dict[str, str]]:
        # zip(fields, values) pairs header with cell — more readable than index slicing
        return [
            {field: val for field, val in zip(fields, line.split(","))}
            for line in lines
            if line.strip()
        ]

    def transpose_matrix(matrix: list[list[int]]) -> list[list[int]]:
        # zip(*matrix) unpacks rows as arguments; list() converts each zip tuple to a list
        return [list(row) for row in zip(*matrix)]

    def comprehension_vs_generator(data: list[int]) -> dict[str, Any]:
        # List comprehension: all squares in memory; generator: computed on demand by sum()
        list_result = sum([x * x for x in data])
        gen_result = sum(x * x for x in data)
        return {"list_result": list_result, "gen_result": gen_result, "are_equal": list_result == gen_result}

    def pipeline_transform(records: list[dict[str, Any]], min_score: int) -> list[str]:
        # sorted() wraps the comprehension — filter+format in one expression, sort is O(n log n) outside
        return sorted(
            f"{r['name'].upper()}: {r['score']}"
            for r in records
            if r["score"] >= min_score
        )
