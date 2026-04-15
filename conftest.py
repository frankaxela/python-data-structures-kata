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

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_call(item: pytest.Item) -> Any:
    outcome = yield
    if outcome.excinfo and outcome.excinfo[0] is NotImplementedError:
        pytest.xfail("not implemented yet")


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
