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
