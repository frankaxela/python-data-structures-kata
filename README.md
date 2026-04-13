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
