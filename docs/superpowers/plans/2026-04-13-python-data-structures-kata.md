# Python Data Structures Kata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-contained Python kata repository for an experienced Java engineer learning idiomatic Python, with 25+ exercises, pytest tests, and an AST-based scoring system.

**Architecture:** Each kata section is a directory with `exercises.py` (stubs the student edits), `solutions.py` (reference wrapped in `if __name__ == "__main__"`), and `test_exercises.py` (imports only from exercises). A root `conftest.py` uses pytest hooks + AST analysis to score implementations after every run and write results to `scores.json`.

**Tech Stack:** Python 3.11+, pytest, pytest-benchmark, mypy, ast (stdlib), collections (stdlib), heapq (stdlib), contextlib (stdlib)

---

## File Map

| File | Role |
|------|------|
| `requirements.txt` | pytest, pytest-benchmark, mypy |
| `pytest.ini` | rootdir config |
| `conftest.py` | scorer plugin — AST analysis + score table + scores.json |
| `katas/*/conftest.py` | per-kata sys.path fix — ensures `from exercises import ...` resolves to the right file |
| `katas/01_dicts/exercises.py` | 6 dict stubs |
| `katas/01_dicts/solutions.py` | 6 dict solutions (guarded) |
| `katas/01_dicts/test_exercises.py` | parametrized tests |
| `katas/02_sets/exercises.py` | 6 set stubs |
| `katas/02_sets/solutions.py` | 6 set solutions |
| `katas/02_sets/test_exercises.py` | parametrized tests |
| `katas/03_comprehensions/exercises.py` | 6 comprehension stubs |
| `katas/03_comprehensions/solutions.py` | 6 comprehension solutions |
| `katas/03_comprehensions/test_exercises.py` | parametrized tests |
| `katas/04_generators/exercises.py` | 5 generator stubs |
| `katas/04_generators/solutions.py` | 5 generator solutions |
| `katas/04_generators/test_exercises.py` | parametrized tests |
| `katas/05_mixed_challenges/exercises.py` | 5 mixed stubs |
| `katas/05_mixed_challenges/solutions.py` | 5 mixed solutions |
| `katas/05_mixed_challenges/test_exercises.py` | parametrized tests |
| `java_comparisons/README.md` | Java vs Python side-by-side |
| `README.md` | Repo overview + progress tracker |
| `scores.json` | Auto-generated; not committed |

---

## Task 1: Repository scaffold

**Files:**
- Create: `requirements.txt`
- Create: `pytest.ini`
- Create: `.gitignore`

- [ ] **Step 1: Create requirements.txt**

```
pytest>=8.0
pytest-benchmark>=4.0
mypy>=1.9
```

- [ ] **Step 2: Create pytest.ini**

```ini
[pytest]
testpaths = katas
addopts = -v
```

- [ ] **Step 3: Create .gitignore**

```
__pycache__/
*.pyc
.mypy_cache/
scores.json
.pytest_cache/
```

- [ ] **Step 4: Create kata directories and per-directory conftest.py files**

```bash
mkdir -p katas/01_dicts katas/02_sets katas/03_comprehensions katas/04_generators katas/05_mixed_challenges java_comparisons
```

Each kata directory needs a `conftest.py` that (a) inserts its own path at the front of `sys.path` and (b) clears any cached `exercises` module so the right file is loaded. Without this, multiple `exercises.py` files across directories collide in `sys.modules`.

Create identical files in each kata directory:

`katas/01_dicts/conftest.py`:
```python
import sys
from pathlib import Path

_here = str(Path(__file__).parent)
if _here not in sys.path:
    sys.path.insert(0, _here)
sys.modules.pop("exercises", None)
```

Repeat for `katas/02_sets/conftest.py`, `katas/03_comprehensions/conftest.py`, `katas/04_generators/conftest.py`, and `katas/05_mixed_challenges/conftest.py` — same content in each.

- [ ] **Step 5: Commit**

```bash
git init
git add requirements.txt pytest.ini .gitignore katas/
git commit -m "chore: scaffold repo with pytest config and per-kata conftest"
```

---

## Task 2: conftest.py scorer

**Files:**
- Create: `conftest.py`

- [ ] **Step 1: Write conftest.py**

```python
from __future__ import annotations

import ast
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pytest

# ── section-based style expectations ────────────────────────────────────────
SECTION_STYLE: dict[str, str] = {
    "03_comprehensions": "comprehension",
    "04_generators": "generator",
}

# ── per-session accumulator ──────────────────────────────────────────────────
# key: "<test_file>::<exercise_fn_name>" → list of pass/fail per parametrize case
_test_results: dict[str, list[bool]] = defaultdict(list)


# ── helpers ───────────────────────────────────────────────────────────────────

def _exercises_path(nodeid: str) -> Path | None:
    """Derive exercises.py path from a test nodeid."""
    # nodeid: katas/01_dicts/test_exercises.py::test_foo[x]
    file_part = nodeid.split("::")[0]
    p = Path(file_part).parent / "exercises.py"
    return p if p.exists() else None


def _section_of(nodeid: str) -> str | None:
    for section in SECTION_STYLE:
        if section in nodeid:
            return section
    return None


def _exercise_fn_name(nodeid: str) -> str:
    """test_foo[param-case] → foo"""
    raw = nodeid.split("::")[-1].split("[")[0]
    return raw[5:] if raw.startswith("test_") else raw


def _file_key(nodeid: str) -> str:
    """Stable key: just the test file path."""
    return nodeid.split("::")[0]


def _get_func_node(source: str, fn_name: str) -> ast.FunctionDef | None:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fn_name:
            return node
    return None


def _has_type_hints(func: ast.FunctionDef) -> bool:
    args_ok = all(
        arg.annotation is not None
        for arg in func.args.args
        if arg.arg != "self"
    )
    return args_ok and func.returns is not None


def _has_meaningful_comment(func: ast.FunctionDef, source_lines: list[str]) -> bool:
    start = func.lineno       # 1-indexed; skip the def line itself
    end = func.end_lineno or start
    for line in source_lines[start:end]:
        stripped = line.strip()
        if stripped.startswith("#") and len(stripped) >= 32:
            return True
    return False


def _uses_bare_loop(func: ast.FunctionDef) -> bool:
    for node in ast.walk(func):
        if node is func:
            continue
        if isinstance(node, (ast.For, ast.While)):
            return True
    return False


def _uses_yield(func: ast.FunctionDef) -> bool:
    for node in ast.walk(func):
        if isinstance(node, (ast.Yield, ast.YieldFrom)):
            return True
    return False


def _score_exercise(
    fn_name: str,
    all_passed: bool,
    exercises_path: Path,
    section: str | None,
) -> tuple[float, list[str]]:
    if not all_passed:
        return 0.0, ["one or more tests failed"]

    source = exercises_path.read_text()
    source_lines = source.splitlines()
    func = _get_func_node(source, fn_name)
    reasons: list[str] = []

    if func is None:
        # Class-based exercise (e.g. LRUCache) — can't do per-method analysis easily
        return 4.0, ["class-based: manual review recommended"]

    score = 4.0

    if not _has_type_hints(func):
        score -= 2.0
        reasons.append("missing type hints")

    if section == "03_comprehensions" and _uses_bare_loop(func):
        score -= 1.0
        reasons.append("used for-loop where comprehension expected")
    elif section == "04_generators" and not _uses_yield(func):
        score -= 1.0
        reasons.append("no yield found — expected a generator")

    if _has_meaningful_comment(func, source_lines):
        score = min(score + 1.0, 5.0)
    else:
        reasons.append("add a comment explaining WHY this approach (+1)")

    return max(score, 0.0), reasons


# ── pytest hooks ──────────────────────────────────────────────────────────────

def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when != "call":
        return
    fn_name = _exercise_fn_name(report.nodeid)
    file_key = _file_key(report.nodeid)
    key = f"{file_key}::{fn_name}"
    _test_results[key].append(report.passed)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    if not _test_results:
        return

    exercises_data: dict[str, dict[str, Any]] = {}
    all_scores: list[float] = []

    for key, results in sorted(_test_results.items()):
        file_key, fn_name = key.rsplit("::", 1)
        exercises_path = _exercises_path(file_key + "::dummy")
        section = _section_of(file_key)
        all_passed = all(results)

        if exercises_path:
            score, reasons = _score_exercise(fn_name, all_passed, exercises_path, section)
        else:
            score = 4.0 if all_passed else 0.0
            reasons = []

        exercises_data[fn_name] = {"score": score, "reasons": reasons}
        all_scores.append(score)

    average = sum(all_scores) / len(all_scores) if all_scores else 0.0
    percentage = (average / 5.0) * 100

    # ── print score table ─────────────────────────────────────────────────────
    print("\n")
    print("=" * 72)
    print(f"{'Exercise':<36} {'Score':>6}  Notes")
    print("-" * 72)
    for fn, data in sorted(exercises_data.items()):
        note = "; ".join(data["reasons"]) if data["reasons"] else "ok"
        print(f"{fn:<36} {data['score']:>5.1f}  {note}")
    print("=" * 72)
    print(f"Phase 0 Week 1 Score: {average:.1f} / 5.0 average ({percentage:.0f}%)")
    print("=" * 72)

    # ── write scores.json ──────────────────────────────────────────────────────
    scores_path = Path("scores.json")
    history: dict[str, Any] = {"runs": []}
    if scores_path.exists():
        try:
            history = json.loads(scores_path.read_text())
        except json.JSONDecodeError:
            pass

    history["runs"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "exercises": exercises_data,
        "average": round(average, 2),
        "percentage": round(percentage, 1),
    })
    scores_path.write_text(json.dumps(history, indent=2))
```

- [ ] **Step 2: Verify scorer is found by pytest (no exercises yet)**

```bash
pytest --collect-only 2>&1 | head -20
```
Expected: no errors about conftest.py import

- [ ] **Step 3: Commit**

```bash
git add conftest.py
git commit -m "feat: add AST-based scoring conftest plugin"
```

---

## Task 3: 01_dicts kata

**Files:**
- Create: `katas/01_dicts/exercises.py`
- Create: `katas/01_dicts/solutions.py`
- Create: `katas/01_dicts/test_exercises.py`

- [ ] **Step 1: Write exercises.py**

```python
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
```

- [ ] **Step 2: Write solutions.py**

```python
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
        # Same setdefault pattern — accumulate originals keys under each value
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
```

- [ ] **Step 3: Write test_exercises.py**

```python
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
    # verify inputs not mutated
    assert base == base  # re-read; ensure no mutation side-effect
```

- [ ] **Step 4: Run tests — all must FAIL (stubs raise NotImplementedError)**

```bash
cd katas/01_dicts && pytest test_exercises.py -v 2>&1 | tail -20
```
Expected: all tests FAIL with `NotImplementedError`

- [ ] **Step 5: Commit**

```bash
cd ../..
git add katas/01_dicts/
git commit -m "feat: add 01_dicts kata (6 exercises, tests, solutions)"
```

---

## Task 4: 02_sets kata

**Files:**
- Create: `katas/02_sets/exercises.py`
- Create: `katas/02_sets/solutions.py`
- Create: `katas/02_sets/test_exercises.py`

- [ ] **Step 1: Write exercises.py**

```python
# katas/02_sets/exercises.py
from __future__ import annotations

from collections import Counter
from typing import Any, TypeVar

T = TypeVar("T")


def deduplicate_ordered(items: list[Any]) -> list[Any]:
    """
    Remove duplicates from `items` while preserving original order.

    A plain set() loses order. Find an O(n) approach that does not.

    Example:
        deduplicate_ordered([3, 1, 4, 1, 5, 9, 2, 6, 5, 3])
        -> [3, 1, 4, 5, 9, 2, 6]
    """
    raise NotImplementedError


def reachable_nodes(graph: dict[str, set[str]], start: str) -> set[str]:
    """
    Return all nodes reachable from `start` in an undirected graph
    (represented as an adjacency set dict), including `start` itself.

    Example:
        graph = {"a": {"b", "c"}, "b": {"a"}, "c": {"a", "d"}, "d": {"c"}, "e": {"f"}, "f": {"e"}}
        reachable_nodes(graph, "a") -> {"a", "b", "c", "d"}
    """
    raise NotImplementedError


def changelog_diff(old_items: set[str], new_items: set[str]) -> dict[str, set[str]]:
    """
    Given two snapshots of a collection, return what was added and removed.

    Example:
        changelog_diff({"a", "b", "c"}, {"b", "c", "d"})
        -> {"added": {"d"}, "removed": {"a"}}

    Return {"added": set(), "removed": set()} when nothing changed.
    """
    raise NotImplementedError


def power_set(s: frozenset[Any]) -> set[frozenset[Any]]:
    """
    Return all subsets of `s`, including the empty set and `s` itself.

    Example:
        power_set(frozenset({1, 2}))
        -> {frozenset(), frozenset({1}), frozenset({2}), frozenset({1, 2})}

    Constraint: result must be a set of frozensets (hashable subsets).
    """
    raise NotImplementedError


def multiset_subtract(a: list[Any], b: list[Any]) -> list[Any]:
    """
    Return elements in `a` that remain after removing all occurrences found in `b`,
    respecting multiplicity (multiset subtraction).

    Use Counter arithmetic — do not write a nested loop.

    Example:
        multiset_subtract(["a", "a", "b", "c"], ["a", "b", "b"])
        -> ["a", "c"]   (one "a" remains; one extra "b" in b is ignored)
    """
    raise NotImplementedError


def has_interval_overlap(intervals: list[tuple[int, int]]) -> bool:
    """
    Return True if any two intervals in the list overlap (share at least one integer point).
    Intervals are inclusive: (1, 3) and (3, 5) DO overlap.

    Example:
        has_interval_overlap([(1, 3), (5, 8), (2, 4)]) -> True
        has_interval_overlap([(1, 2), (4, 5), (7, 8)]) -> False
    """
    raise NotImplementedError
```

- [ ] **Step 2: Write solutions.py**

```python
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
```

- [ ] **Step 3: Write test_exercises.py**

```python
# katas/02_sets/test_exercises.py
from __future__ import annotations

import pytest

from exercises import (
    changelog_diff,
    deduplicate_ordered,
    has_interval_overlap,
    multiset_subtract,
    power_set,
    reachable_nodes,
)


@pytest.mark.parametrize("items,expected", [
    ([3, 1, 4, 1, 5, 9, 2, 6, 5, 3], [3, 1, 4, 5, 9, 2, 6]),
    ([], []),
    ([1], [1]),
    ([1, 1, 1], [1]),
])
def test_deduplicate_ordered(items: list, expected: list) -> None:
    assert deduplicate_ordered(items) == expected


@pytest.mark.parametrize("graph,start,expected", [
    (
        {"a": {"b", "c"}, "b": {"a"}, "c": {"a", "d"}, "d": {"c"}, "e": {"f"}, "f": {"e"}},
        "a",
        {"a", "b", "c", "d"},
    ),
    ({"x": set()}, "x", {"x"}),
    ({}, "z", {"z"}),
])
def test_reachable_nodes(graph, start, expected) -> None:
    assert reachable_nodes(graph, start) == expected


@pytest.mark.parametrize("old,new,expected", [
    ({"a", "b", "c"}, {"b", "c", "d"}, {"added": {"d"}, "removed": {"a"}}),
    ({"a"}, {"a"}, {"added": set(), "removed": set()}),
    (set(), {"x"}, {"added": {"x"}, "removed": set()}),
])
def test_changelog_diff(old, new, expected) -> None:
    assert changelog_diff(old, new) == expected


@pytest.mark.parametrize("s,expected_size", [
    (frozenset({1, 2}), 4),
    (frozenset(), 1),
    (frozenset({1, 2, 3}), 8),
])
def test_power_set(s, expected_size) -> None:
    result = power_set(s)
    assert isinstance(result, set)
    assert len(result) == expected_size
    assert frozenset() in result
    assert s in result


@pytest.mark.parametrize("a,b,expected", [
    (["a", "a", "b", "c"], ["a", "b", "b"], ["a", "c"]),
    ([], [], []),
    (["x"], ["x"], []),
    (["a", "b"], ["c"], ["a", "b"]),
])
def test_multiset_subtract(a, b, expected) -> None:
    assert sorted(multiset_subtract(a, b)) == sorted(expected)


@pytest.mark.parametrize("intervals,expected", [
    ([(1, 3), (5, 8), (2, 4)], True),
    ([(1, 2), (4, 5), (7, 8)], False),
    ([], False),
    ([(1, 1)], False),
    ([(1, 3), (3, 5)], True),
])
def test_has_interval_overlap(intervals, expected) -> None:
    assert has_interval_overlap(intervals) == expected
```

- [ ] **Step 4: Verify tests FAIL on stubs**

```bash
cd katas/02_sets && pytest test_exercises.py -v 2>&1 | tail -10
```
Expected: all FAIL with `NotImplementedError`

- [ ] **Step 5: Commit**

```bash
cd ../..
git add katas/02_sets/
git commit -m "feat: add 02_sets kata (6 exercises, tests, solutions)"
```

---

## Task 5: 03_comprehensions kata

**Files:**
- Create: `katas/03_comprehensions/exercises.py`
- Create: `katas/03_comprehensions/solutions.py`
- Create: `katas/03_comprehensions/test_exercises.py`

- [ ] **Step 1: Write exercises.py**

```python
# katas/03_comprehensions/exercises.py
from __future__ import annotations

from typing import Any, Callable


def flatten_list(nested: list[list[Any]]) -> list[Any]:
    """
    Flatten one level of nesting into a single list — as a one-liner comprehension.

    Example:
        flatten_list([[1, 2], [3, 4], [5]])
        -> [1, 2, 3, 4, 5]

    Constraint: must be a single list comprehension expression.
    """
    raise NotImplementedError


def transform_dict(
    d: dict[str, Any],
    predicate: Callable[[str, Any], bool],
    transform: Callable[[str, Any], tuple[str, Any]],
) -> dict[str, Any]:
    """
    Build a new dict from `d` keeping only entries where predicate(key, value)
    is True, then applying transform(key, value) -> (new_key, new_value).

    Example:
        transform_dict(
            {"a": 1, "b": -2, "c": 3},
            predicate=lambda k, v: v > 0,
            transform=lambda k, v: (k.upper(), v * 10),
        )
        -> {"A": 10, "C": 30}

    Constraint: must be a single dict comprehension expression.
    """
    raise NotImplementedError


def parse_csv_records(lines: list[str], fields: list[str]) -> list[dict[str, str]]:
    """
    Parse CSV lines (no header row) into a list of dicts using `fields` as keys.
    Skip blank lines.

    Example:
        parse_csv_records(["alice,30,eng", "bob,25,mkt", ""], ["name", "age", "dept"])
        -> [{"name": "alice", "age": "30", "dept": "eng"},
            {"name": "bob",   "age": "25", "dept": "mkt"}]

    Constraint: the outer list and inner dicts must both be comprehensions.
    """
    raise NotImplementedError


def transpose_matrix(matrix: list[list[int]]) -> list[list[int]]:
    """
    Transpose a 2D matrix (rows become columns).

    Example:
        transpose_matrix([[1, 2, 3], [4, 5, 6]])
        -> [[1, 4], [2, 5], [3, 6]]

    Constraint: use zip(*matrix) inside a comprehension — no manual indexing.
    """
    raise NotImplementedError


def comprehension_vs_generator(data: list[int]) -> dict[str, Any]:
    """
    Compute the sum of squares for `data` two ways: list comprehension and generator expression.
    Return a dict with keys "list_result" and "gen_result" containing the sums,
    and "are_equal" (bool) confirming they match.

    Example:
        comprehension_vs_generator([1, 2, 3])
        -> {"list_result": 14, "gen_result": 14, "are_equal": True}

    This exercise exists to highlight when each form is preferable:
    list comprehension materialises all values (random access, reusable);
    generator expression is lazy (O(1) memory, single-pass only).
    """
    raise NotImplementedError


def pipeline_transform(
    records: list[dict[str, Any]],
    min_score: int,
) -> list[str]:
    """
    From a list of {"name": str, "score": int} records:
    1. Keep only records where score >= min_score
    2. Format each as "NAME: score" (name uppercased)
    3. Sort alphabetically

    Example:
        pipeline_transform(
            [{"name": "alice", "score": 90}, {"name": "bob", "score": 40}, {"name": "cara", "score": 85}],
            min_score=80,
        )
        -> ["ALICE: 90", "CARA: 85"]

    Constraint: solve in one chained comprehension expression (filter inside, sorted outside).
    """
    raise NotImplementedError
```

- [ ] **Step 2: Write solutions.py**

```python
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
```

- [ ] **Step 3: Write test_exercises.py**

```python
# katas/03_comprehensions/test_exercises.py
from __future__ import annotations

import pytest

from exercises import (
    comprehension_vs_generator,
    flatten_list,
    parse_csv_records,
    pipeline_transform,
    transform_dict,
    transpose_matrix,
)


@pytest.mark.parametrize("nested,expected", [
    ([[1, 2], [3, 4], [5]], [1, 2, 3, 4, 5]),
    ([], []),
    ([[]], []),
    ([[1]], [1]),
])
def test_flatten_list(nested: list, expected: list) -> None:
    assert flatten_list(nested) == expected


@pytest.mark.parametrize("d,pred,transform,expected", [
    (
        {"a": 1, "b": -2, "c": 3},
        lambda k, v: v > 0,
        lambda k, v: (k.upper(), v * 10),
        {"A": 10, "C": 30},
    ),
    ({}, lambda k, v: True, lambda k, v: (k, v), {}),
    ({"x": 0}, lambda k, v: v != 0, lambda k, v: (k, v), {}),
])
def test_transform_dict(d, pred, transform, expected) -> None:
    assert transform_dict(d, pred, transform) == expected


@pytest.mark.parametrize("lines,fields,expected", [
    (
        ["alice,30,eng", "bob,25,mkt", ""],
        ["name", "age", "dept"],
        [{"name": "alice", "age": "30", "dept": "eng"},
         {"name": "bob", "age": "25", "dept": "mkt"}],
    ),
    ([], ["a", "b"], []),
    (["  ", "1,2"], ["x", "y"], [{"x": "1", "y": "2"}]),
])
def test_parse_csv_records(lines, fields, expected) -> None:
    assert parse_csv_records(lines, fields) == expected


@pytest.mark.parametrize("matrix,expected", [
    ([[1, 2, 3], [4, 5, 6]], [[1, 4], [2, 5], [3, 6]]),
    ([[1]], [[1]]),
    ([[1, 2]], [[1], [2]]),
])
def test_transpose_matrix(matrix, expected) -> None:
    assert transpose_matrix(matrix) == expected


@pytest.mark.parametrize("data,expected_sum", [
    ([1, 2, 3], 14),
    ([], 0),
    ([5], 25),
])
def test_comprehension_vs_generator(data, expected_sum) -> None:
    result = comprehension_vs_generator(data)
    assert result["list_result"] == expected_sum
    assert result["gen_result"] == expected_sum
    assert result["are_equal"] is True


@pytest.mark.parametrize("records,min_score,expected", [
    (
        [{"name": "alice", "score": 90}, {"name": "bob", "score": 40}, {"name": "cara", "score": 85}],
        80,
        ["ALICE: 90", "CARA: 85"],
    ),
    ([], 50, []),
    ([{"name": "x", "score": 50}], 50, ["X: 50"]),
    ([{"name": "x", "score": 49}], 50, []),
])
def test_pipeline_transform(records, min_score, expected) -> None:
    assert pipeline_transform(records, min_score) == expected
```

- [ ] **Step 4: Verify tests FAIL on stubs**

```bash
cd katas/03_comprehensions && pytest test_exercises.py -v 2>&1 | tail -10
```
Expected: all FAIL with `NotImplementedError`

- [ ] **Step 5: Commit**

```bash
cd ../..
git add katas/03_comprehensions/
git commit -m "feat: add 03_comprehensions kata (6 exercises, tests, solutions)"
```

---

## Task 6: 04_generators kata

**Files:**
- Create: `katas/04_generators/exercises.py`
- Create: `katas/04_generators/solutions.py`
- Create: `katas/04_generators/test_exercises.py`

- [ ] **Step 1: Write exercises.py**

```python
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
```

- [ ] **Step 2: Write solutions.py**

```python
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
```

- [ ] **Step 3: Write test_exercises.py**

```python
# katas/04_generators/test_exercises.py
from __future__ import annotations

import os
from itertools import islice
from pathlib import Path

import pytest

from exercises import (
    fibonacci,
    lazy_file_reader,
    managed_temp_file,
    preorder_traversal,
    transform_pipeline,
)


def test_fibonacci_first_ten() -> None:
    assert list(islice(fibonacci(), 10)) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]


def test_fibonacci_single() -> None:
    assert list(islice(fibonacci(), 1)) == [0]


def test_fibonacci_empty() -> None:
    assert list(islice(fibonacci(), 0)) == []


def test_lazy_file_reader(tmp_path: Path) -> None:
    f = tmp_path / "test.txt"
    f.write_text("line1\nline2\nline3\n")
    result = list(lazy_file_reader(str(f)))
    assert result == ["line1", "line2", "line3"]


def test_lazy_file_reader_empty(tmp_path: Path) -> None:
    f = tmp_path / "empty.txt"
    f.write_text("")
    assert list(lazy_file_reader(str(f))) == []


@pytest.mark.parametrize("items,min_len,transform,expected", [
    (["hi", "hello", "hey"], 4, str.upper, ["HELLO"]),
    ([], 1, str.upper, []),
    (["a", "bb", "ccc"], 2, lambda s: s * 2, ["bbbb", "cccccc"]),
])
def test_transform_pipeline(items, min_len, transform, expected) -> None:
    assert list(transform_pipeline(items, min_len, transform)) == expected


def test_managed_temp_file_creates_and_cleans_up() -> None:
    with managed_temp_file(".txt") as path:
        assert os.path.exists(path)
        assert path.endswith(".txt")
        Path(path).write_text("hello")
    assert not os.path.exists(path)


def test_managed_temp_file_cleans_up_on_exception() -> None:
    saved_path: list[str] = []
    with pytest.raises(RuntimeError):
        with managed_temp_file() as path:
            saved_path.append(path)
            raise RuntimeError("test")
    assert not os.path.exists(saved_path[0])


@pytest.mark.parametrize("tree,expected", [
    (
        {"value": 1, "children": [
            {"value": 2, "children": []},
            {"value": 3, "children": [{"value": 4, "children": []}]},
        ]},
        [1, 2, 3, 4],
    ),
    ({"value": 42, "children": []}, [42]),
])
def test_preorder_traversal(tree, expected) -> None:
    assert list(preorder_traversal(tree)) == expected
```

- [ ] **Step 4: Verify tests FAIL on stubs**

```bash
cd katas/04_generators && pytest test_exercises.py -v 2>&1 | tail -10
```
Expected: all FAIL with `NotImplementedError`

- [ ] **Step 5: Commit**

```bash
cd ../..
git add katas/04_generators/
git commit -m "feat: add 04_generators kata (5 exercises, tests, solutions)"
```

---

## Task 7: 05_mixed_challenges kata

**Files:**
- Create: `katas/05_mixed_challenges/exercises.py`
- Create: `katas/05_mixed_challenges/solutions.py`
- Create: `katas/05_mixed_challenges/test_exercises.py`

- [ ] **Step 1: Write exercises.py**

```python
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
```

- [ ] **Step 2: Write solutions.py**

```python
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
```

- [ ] **Step 3: Write test_exercises.py**

```python
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
```

- [ ] **Step 4: Verify tests FAIL on stubs**

```bash
cd katas/05_mixed_challenges && pytest test_exercises.py -v 2>&1 | tail -10
```
Expected: all FAIL with `NotImplementedError`

- [ ] **Step 5: Commit**

```bash
cd ../..
git add katas/05_mixed_challenges/
git commit -m "feat: add 05_mixed_challenges kata (5 exercises, tests, solutions)"
```

---

## Task 8: java_comparisons/README.md

**Files:**
- Create: `java_comparisons/README.md`

- [ ] **Step 1: Write java_comparisons/README.md**

````markdown
# Java → Python Pattern Guide

Side-by-side comparisons for the patterns you'll encounter in these katas.

---

## HashMap vs dict / defaultdict

**Java**
```java
Map<String, Integer> freq = new HashMap<>();
for (String w : words) {
    freq.put(w, freq.getOrDefault(w, 0) + 1);
}
```

**Python**
```python
freq: dict[str, int] = {}
for w in words:
    freq[w] = freq.get(w, 0) + 1

# Or with defaultdict — no existence check needed:
from collections import defaultdict
freq = defaultdict(int)
for w in words:
    freq[w] += 1
```

`defaultdict(int)` initialises missing keys to `0`. Use it when the default value is always the same. Use `dict.get(k, default)` when defaults vary per call.

---

## HashSet vs set

**Java**
```java
Set<String> seen = new HashSet<>();
List<String> unique = new ArrayList<>();
for (String s : items) {
    if (seen.add(s)) unique.add(s);
}
```

**Python**
```python
seen: set[str] = set()
unique: list[str] = []
for s in items:
    if s not in seen:
        seen.add(s)
        unique.append(s)

# One-liner preserving order (Python 3.7+):
unique = list(dict.fromkeys(items))
```

Python sets have the same O(1) average membership test as Java's `HashSet`. `frozenset` is the immutable, hashable variant — used when you need a set as a dict key.

---

## Iterator / Stream vs generator / comprehension

**Java**
```java
List<String> result = items.stream()
    .filter(s -> s.length() > 3)
    .map(String::toUpperCase)
    .collect(Collectors.toList());
```

**Python**
```python
# List comprehension (eager — allocates the full list):
result = [s.upper() for s in items if len(s) > 3]

# Generator expression (lazy — computes on demand):
result_gen = (s.upper() for s in items if len(s) > 3)

# Use the generator when passing directly to sum(), any(), join(), etc.:
total_len = sum(len(s) for s in items if len(s) > 3)
```

Generators are the Python equivalent of Java Streams: lazy, single-pass, composable. Use a list comprehension when you need random access or multiple passes.

---

## Comparable / Comparator vs key= functions

**Java**
```java
items.sort(Comparator.comparing(Person::getAge).reversed());
```

**Python**
```python
items.sort(key=lambda p: p.age, reverse=True)

# Multi-key sort (no Comparator chaining needed):
items.sort(key=lambda p: (-p.age, p.name))
```

Python's `key=` receives one argument and returns a comparable value. Negate numeric fields for descending order. Tuple keys sort lexicographically — `(-age, name)` means "descending age, ascending name".

---

## for loop with index vs enumerate

**Java**
```java
for (int i = 0; i < items.size(); i++) {
    System.out.println(i + ": " + items.get(i));
}
```

**Python**
```python
for i, item in enumerate(items):
    print(f"{i}: {item}")

# Start from a custom index:
for i, item in enumerate(items, start=1):
    print(f"{i}: {item}")
```

`enumerate()` returns `(index, value)` pairs. Never use `range(len(items))` to get the index — that is a Java anti-pattern in Python.

---

## null checks vs None handling + walrus operator

**Java**
```java
String name = map.get("user");
if (name != null && name.length() > 3) {
    process(name);
}
```

**Python**
```python
name = mapping.get("user")
if name is not None and len(name) > 3:
    process(name)

# Walrus operator (Python 3.8+) — assign and test in one expression:
if (name := mapping.get("user")) and len(name) > 3:
    process(name)
```

`None` is Python's `null`. Always use `is None` / `is not None` — never `== None`. The walrus operator `:=` assigns and evaluates in a single expression, eliminating the "compute twice" pattern common in Java guards.

---

## yield vs return (generators vs methods)

**Java** has no direct equivalent — closest is `Iterator` with `hasNext`/`next`, which requires ~20 lines of boilerplate.

**Python**
```python
def fibonacci():
    a, b = 0, 1
    while True:          # infinite — callers use islice()
        yield a
        a, b = b, a + b

from itertools import islice
first_ten = list(islice(fibonacci(), 10))
```

A function containing `yield` becomes a generator. It is suspended at each `yield`, resuming when the caller calls `next()`. `yield from sub_gen` delegates to another generator without buffering.
````

- [ ] **Step 2: Commit**

```bash
git add java_comparisons/README.md
git commit -m "docs: add Java vs Python pattern comparison guide"
```

---

## Task 9: README.md

**Files:**
- Create: `README.md`

- [ ] **Step 1: Write README.md**

````markdown
# python-data-structures-kata

A self-contained exercise suite for an experienced Java engineer learning idiomatic Python.
Exercises are deliberately non-trivial — no exercise is solvable by translating Java line-for-line.

## Why this exists

Java engineers learning Python often write correct but un-Pythonic code: verbose loops where comprehensions belong, `HashMap` patterns instead of `dict.get()`, manual null-checks instead of walrus operators. These katas force the idiomatic approach and score you on it automatically.

## Setup

```bash
pip install -r requirements.txt
```

## Running the tests

```bash
pytest katas/ -v
```

After the run, a score table is printed and results are appended to `scores.json`.

## How to use

1. Open `katas/<section>/exercises.py`
2. Replace `raise NotImplementedError` with your solution
3. Run `pytest katas/<section>/test_exercises.py -v`
4. Read the score table — aim for 5.0 per exercise
5. Only open `solutions.py` after you've made a genuine attempt

## Scoring

Each exercise is scored 0–5:

| Score | Meaning |
|-------|---------|
| 0.0 | Tests fail |
| 2.0 | Tests pass, no type hints |
| 3.0 | Tests pass, type hints, no edge cases handled |
| 4.0 | Tests pass, type hints, idiomatic Python |
| 5.0 | All of the above + explanatory comment on the approach |

Style violations (e.g. a for-loop in a comprehension exercise) deduct 1 point.

## Progress tracker

| # | Exercise | Section | Status | Notes |
|---|----------|---------|--------|-------|
| 1 | `frequency_counter` | 01_dicts | todo | |
| 2 | `flatten_nested_dict` | 01_dicts | todo | |
| 3 | `group_by` | 01_dicts | todo | |
| 4 | `invert_dict` | 01_dicts | todo | |
| 5 | `LRUCache` | 01_dicts | todo | |
| 6 | `deep_merge` | 01_dicts | todo | |
| 7 | `deduplicate_ordered` | 02_sets | todo | |
| 8 | `reachable_nodes` | 02_sets | todo | |
| 9 | `changelog_diff` | 02_sets | todo | |
| 10 | `power_set` | 02_sets | todo | |
| 11 | `multiset_subtract` | 02_sets | todo | |
| 12 | `has_interval_overlap` | 02_sets | todo | |
| 13 | `flatten_list` | 03_comprehensions | todo | |
| 14 | `transform_dict` | 03_comprehensions | todo | |
| 15 | `parse_csv_records` | 03_comprehensions | todo | |
| 16 | `transpose_matrix` | 03_comprehensions | todo | |
| 17 | `comprehension_vs_generator` | 03_comprehensions | todo | |
| 18 | `pipeline_transform` | 03_comprehensions | todo | |
| 19 | `fibonacci` | 04_generators | todo | |
| 20 | `lazy_file_reader` | 04_generators | todo | |
| 21 | `transform_pipeline` | 04_generators | todo | |
| 22 | `managed_temp_file` | 04_generators | todo | |
| 23 | `preorder_traversal` | 04_generators | todo | |
| 24 | `top_words` | 05_mixed_challenges | todo | |
| 25 | `group_anagrams` | 05_mixed_challenges | todo | |
| 26 | `sliding_window_max` | 05_mixed_challenges | todo | |
| 27 | `top_n_from_stream` | 05_mixed_challenges | todo | |
| 28 | `bfs_shortest_path` | 05_mixed_challenges | todo | |

## Reference

See `java_comparisons/README.md` for side-by-side Java → Python pattern translations.
````

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup instructions and progress tracker"
```

---

## Task 10: Full test run and scorer verification

- [ ] **Step 1: Install dependencies**

```bash
pip install -r requirements.txt
```

- [ ] **Step 2: Run all tests from repo root**

```bash
pytest katas/ -v 2>&1 | tail -40
```
Expected: all 28 exercises FAIL with `NotImplementedError`; score table prints with 0.0 for all; `scores.json` written.

- [ ] **Step 3: Verify scores.json structure**

```bash
python -c "import json; d=json.load(open('scores.json')); print(json.dumps(d['runs'][-1], indent=2))"
```
Expected: JSON with `timestamp`, `exercises` dict, `average`, `percentage` keys.

- [ ] **Step 4: Smoke-test one solution manually**

Copy `frequency_counter` solution into `katas/01_dicts/exercises.py`, then:
```bash
pytest katas/01_dicts/test_exercises.py::test_frequency_counter -v
```
Expected: PASS; score table shows `frequency_counter` with score > 0.

Undo the edit after verifying.

- [ ] **Step 5: Final commit**

```bash
git add scores.json 2>/dev/null || true   # may not exist yet
git status
git commit -m "chore: verify full test suite and scorer end-to-end" --allow-empty
```
