#!/usr/bin/env python3
"""E014: finite check of the width factor at larger optima.

Protocol: protocol.md in this directory (committed before this file).
Standard library only. No randomness.

A context row is a pair (mask, y). Bit j of mask is set iff key j equals the
target's value 0; keys are binary, so the key Hamming distance of two rows is
the popcount of the XOR of their masks. The protected target is all zero and
is never stored as a row; its vote is added inside the evaluators.

Usage:
  python3 verify_scale.py            run and write results/summary.json
  python3 verify_scale.py --verify   recompute and compare with the stored
                                     summary (provenance fields excluded)
"""
import hashlib
import itertools
import json
import subprocess
import sys
import time
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW_LIMIT = 10**7
INF = float("inf")


class Mismatch(Exception):
    """A locked prediction failed; the payload is kept as a counterexample."""


# --------------------------------------------------------------------------
# Direct evaluation from the definition
# --------------------------------------------------------------------------

def rule_accepts(rows, rule, d):
    """Count votes in the target's group for one rule; ties reject."""
    counts = [0] * d
    counts[0] = 1  # the protected target
    for mask, y in rows:
        if mask & rule == rule:
            counts[y] += 1
    zero = counts[0]
    for v in range(1, d):
        if counts[v] >= zero:
            return False
    return True


def accepts(rows, rules, d):
    for rule in rules:
        if not rule_accepts(rows, rule, d):
            return False
    return True


def hamming(rows_a, rows_b):
    return sum(bin(a[0] ^ b[0]).count("1") + (a[1] != b[1])
               for a, b in zip(rows_a, rows_b))


# --------------------------------------------------------------------------
# Width by exhaustive antichain search
# --------------------------------------------------------------------------

def is_antichain(sets):
    return all(not (a <= b or b <= a) for a, b in itertools.combinations(sets, 2))


def width_data(family, q):
    """Return (w, j, antichain): smallest key j with w_j = w and the
    lexicographically first maximum antichain of F_j."""
    best = (0, None, None)
    for j in range(q):
        fj = sorted(tuple(sorted(x)) for x in family if j in x)
        found = None
        for size in range(len(fj), 0, -1):
            for cand in itertools.combinations(fj, size):
                if is_antichain([frozenset(c) for c in cand]):
                    found = cand
                    break
            if found:
                break
        wj = len(found) if found else 0
        if wj > best[0]:
            best = (wj, j, found)
    return best


def mask_of(keys):
    m = 0
    for j in keys:
        m |= 1 << j
    return m


# --------------------------------------------------------------------------
# Solver 1: row dynamic program over all destinations
# --------------------------------------------------------------------------

def contribution(mask, y, rules, d):
    vec = [0] * (len(rules) * (d - 1))
    for xi, rule in enumerate(rules):
        if mask & rule == rule:
            base = xi * (d - 1)
            if y == 0:
                for v in range(d - 1):
                    vec[base + v] = 1
            else:
                vec[base + y - 1] = -1
    return tuple(vec)


def row_options(row, rules, d, q, edit_keys):
    """Every destination of one row, merged by contribution vector."""
    mask, y = row
    best = {}
    masks = range(1 << q) if edit_keys else (mask,)
    for m2 in masks:
        key_cost = bin(mask ^ m2).count("1")
        for y2 in range(d):
            cost = key_cost + (y2 != y)
            vec = contribution(m2, y2, rules, d)
            if cost < best.get(vec, INF):
                best[vec] = cost
    return sorted(best.items())


def dp_step(states, options, bound):
    new = {}
    for state, cost in states.items():
        for vec, c in options:
            nc = cost + c
            if bound is not None and nc > bound:
                continue
            ns = tuple(a + b for a, b in zip(state, vec))
            if nc < new.get(ns, INF):
                new[ns] = nc
    return new


def dp_best(states):
    best = None
    for state, cost in states.items():
        if min(state) >= 1 and (best is None or cost < best):
            best = cost
    return best


def dp_radius(rows, rules, d, q, edit_keys, bound):
    states = {tuple([1] * (len(rules) * (d - 1))): 0}
    peak = 1
    cache = {}
    for row in rows:
        if row not in cache:
            cache[row] = row_options(row, rules, d, q, edit_keys)
        states = dp_step(states, cache[row], bound)
        peak = max(peak, len(states))
    return dp_best(states), peak


# --------------------------------------------------------------------------
# Solver 2: raw bounded enumeration of edit sets
# --------------------------------------------------------------------------

def raw_count(n_rows, q, d, limit, edit_keys):
    """Number of edited tables with at most `limit` changed cells."""
    key_cells = n_rows * q if edit_keys else 0
    total = 0
    for size in range(limit + 1):
        for y_cells in range(size + 1):
            total += (comb(key_cells, size - y_cells) * comb(n_rows, y_cells)
                      * (d - 1) ** y_cells)
    return total


def raw_bounded(rows, rules, d, q, limit, edit_keys):
    """Evaluate every table within `limit` changed cells. Returns the number
    of evaluated tables and the least cost of an accepting one (or None)."""
    work = [list(r) for r in rows]
    cells = []
    for i in range(len(rows)):
        if edit_keys:
            cells.extend((i, j) for j in range(q))
        cells.append((i, q))
    n_cells = len(cells)
    result = {"evaluated": 0, "least": None}

    def rec(start, depth):
        result["evaluated"] += 1
        if accepts(work, rules, d):
            if result["least"] is None or depth < result["least"]:
                result["least"] = depth
        if depth == limit:
            return
        for ci in range(start, n_cells):
            i, c = cells[ci]
            if c < q:
                work[i][0] ^= 1 << c
                rec(ci + 1, depth + 1)
                work[i][0] ^= 1 << c
            else:
                old = work[i][1]
                for v in range(d):
                    if v != old:
                        work[i][1] = v
                        rec(ci + 1, depth + 1)
                work[i][1] = old

    rec(0, 0)
    return result["evaluated"], result["least"]


# --------------------------------------------------------------------------
# Part A: the construction of H14a
# --------------------------------------------------------------------------

PART_A = [
    ("A1", [(0, 1), (0, 2)], 3, 1, 2),
    ("A2", [(0, 1), (0, 2)], 3, 2, 3),
    ("A3", [(0, 1), (0, 2)], 3, 2, 4),
    ("A4", [(0, 1), (0, 2)], 3, 3, 4),
    ("A5", [(0,), (0, 1), (0, 2)], 3, 2, 3),
    ("A6", [(0, 1), (0, 2), (0, 1, 2)], 3, 2, 3),
    ("A7", [(0, 1), (0, 2), (1, 2)], 3, 2, 3),
    ("A8", [(0, 1), (0, 2), (0, 3)], 4, 2, 3),
    ("A9", [(0,), (1,), (2,), (0, 1), (0, 2), (1, 2), (0, 1, 2)], 3, 2, 3),
]


def build_construction(family, q, k, d):
    if d < k + 1:
        raise ValueError("construction needs d >= k+1")
    fam = [frozenset(x) for x in family]
    w, j, antichain = width_data(fam, q)
    full = (1 << q) - 1
    rows = []
    critical = []  # per antichain member: {value: [row indexes]}
    for a in antichain:
        by_value = {}
        for v in range(1, k + 1):
            by_value[v] = list(range(len(rows), len(rows) + k))
            rows.extend([(mask_of(a), v)] * k)
        critical.append(by_value)
    p_rows = list(range(len(rows), len(rows) + k))
    rows.extend([(full & ~(1 << j), 0)] * k)
    anti_sets = [frozenset(a) for a in antichain]
    for c in sorted(tuple(sorted(x)) for x in fam):
        if not any(a <= frozenset(c) for a in anti_sets):
            rows.extend([(mask_of(c), 0)] * (w * k))
    return {"w": w, "j": j, "antichain": [list(a) for a in antichain],
            "rows": rows, "critical": critical, "p_rows": p_rows}


def check_case(name, family, q, k, d, rows, w, expected, witness_full,
               witness_fixed, critical_rules):
    rules = [mask_of(x) for x in family]
    out = {"case": name, "family": [list(x) for x in family], "q": q, "k": k,
           "d": d, "width": w, "context_rows": len(rows),
           "rows_mask_y": [list(r) for r in rows],
           "expected": list(expected)}

    per_rule = [rule_accepts(rows, r, d) for r in rules]
    out["initially_accepting_rules"] = [list(x) for x, ok in zip(family, per_rule) if ok]
    rejecting = sorted(tuple(x) for x, ok in zip(family, per_rule) if not ok)
    if rejecting != sorted(tuple(x) for x in critical_rules):
        raise Mismatch({"case": name, "reason": "initial rule decisions",
                        "rejecting": rejecting})

    radii = {}
    for label, edit_keys, witness, limit in (
            ("full", True, witness_full, expected[0] - 1),
            ("fixed", False, witness_fixed, expected[1] - 1)):
        cost = hamming(rows, witness)
        keys_kept = all(a[0] == b[0] for a, b in zip(rows, witness))
        if not accepts(witness, rules, d) or (not edit_keys and not keys_kept):
            raise Mismatch({"case": name, "reason": "witness invalid", "model": label})
        value, peak = dp_radius(rows, rules, d, q, edit_keys, cost)
        count = raw_count(len(rows), q, d, limit, edit_keys)
        entry = {"witness_cost": cost, "dp_radius": value, "dp_peak_states": peak,
                 "raw_limit": limit, "raw_tables": count}
        if count <= RAW_LIMIT:
            evaluated, least = raw_bounded(rows, rules, d, q, limit, edit_keys)
            entry.update(raw_run=True, raw_evaluated=evaluated,
                         raw_least_accepting=least)
            if evaluated != count or least is not None:
                raise Mismatch({"case": name, "reason": "raw enumeration",
                                "model": label, "entry": entry})
        else:
            entry.update(raw_run=False)
        radii[label] = entry
        if value != cost:
            raise Mismatch({"case": name, "reason": "dp differs from witness",
                            "model": label, "entry": entry})
    out["radii"] = radii
    observed = (radii["full"]["dp_radius"], radii["fixed"]["dp_radius"])
    out["observed"] = list(observed)
    if observed != tuple(expected):
        raise Mismatch({"case": name, "reason": "prediction", "observed": observed})
    return out


def part_a():
    results = []
    for name, family, q, k, d in PART_A:
        built = build_construction(family, q, k, d)
        rows, w, j = built["rows"], built["w"], built["j"]
        witness_full = list(rows)
        for i in built["p_rows"]:
            witness_full[i] = (rows[i][0] | (1 << j), rows[i][1])
        witness_fixed = list(rows)
        for by_value in built["critical"]:
            for v, idx in by_value.items():
                witness_fixed[idx[0]] = (rows[idx[0]][0], 0)
        out = check_case(name, family, q, k, d, rows, w, (k, w * k),
                         witness_full, witness_fixed, built["antichain"])
        out["key_j"] = j
        out["antichain"] = built["antichain"]
        results.append(out)
    return results


def control():
    family = [(0, 1), (0, 2)]
    rows = ([(mask_of((0, 1)), 1)] * 2 + [(mask_of((0, 2)), 1)] * 2
            + [(mask_of((1, 2)), 0)] * 2)
    witness = list(rows)
    witness[0] = (rows[0][0], 0)
    witness[2] = (rows[2][0], 0)
    return check_case("control-d2-k2", family, 3, 2, 2, rows, 2, (2, 2),
                      witness, witness, family)


# --------------------------------------------------------------------------
# Part B: binary two-rule family, every multiset of one to six rows
# --------------------------------------------------------------------------

def raw_full(rows, rules, q, d):
    """Least cost over every destination table, both edit models."""
    universe = [(m, y) for m in range(1 << q) for y in range(d)]
    best_full = best_fixed = None
    evaluated = 0
    for dest in itertools.product(universe, repeat=len(rows)):
        evaluated += 1
        if not accepts(dest, rules, d):
            continue
        cost = hamming(rows, dest)
        if best_full is None or cost < best_full:
            best_full = cost
        if all(a[0] == b[0] for a, b in zip(rows, dest)):
            if best_fixed is None or cost < best_fixed:
                best_fixed = cost
    return best_full, best_fixed, evaluated


def part_b(max_rows=6, raw_rows=3):
    q, d = 3, 2
    rules = [mask_of((0, 1)), mask_of((0, 2))]
    codes = [(m, y) for m in range(1 << q) for y in range(d)]
    opts_full = [row_options(r, rules, d, q, True) for r in codes]
    opts_fixed = [row_options(r, rules, d, q, False) for r in codes]
    stats = {"tables": 0, "by_rows": {}, "rejected": 0, "crosstab": {},
             "raw_checked_tables": 0, "raw_evaluated": 0,
             "max_fixed_minus_full": 0, "strict_gap_tables": 0}

    def rec(start, rows, st_full, st_fixed):
        if rows:
            n = len(rows)
            stats["tables"] += 1
            stats["by_rows"][n] = stats["by_rows"].get(n, 0) + 1
            r_full, r_fixed = dp_best(st_full), dp_best(st_fixed)
            rejected = not accepts(rows, rules, d)
            if n <= raw_rows:
                raw_f, raw_x, evaluated = raw_full(rows, rules, q, d)
                stats["raw_checked_tables"] += 1
                stats["raw_evaluated"] += evaluated
                if (raw_f, raw_x) != (r_full, r_fixed):
                    raise Mismatch({"part": "B", "reason": "dp differs from raw",
                                    "rows": rows, "dp": [r_full, r_fixed],
                                    "raw": [raw_f, raw_x]})
            if rejected:
                stats["rejected"] += 1
                key = f"{r_full},{r_fixed}"
                stats["crosstab"][key] = stats["crosstab"].get(key, 0) + 1
                ok = (r_full is not None and r_fixed is not None
                      and 1 <= r_full <= r_fixed <= r_full + 1
                      and r_fixed <= 2 * r_full
                      and (r_fixed != 2 * r_full or r_full == 1))
                if not ok:
                    raise Mismatch({"part": "B", "reason": "prediction",
                                    "rows": rows, "radii": [r_full, r_fixed]})
                gap = r_fixed - r_full
                stats["max_fixed_minus_full"] = max(stats["max_fixed_minus_full"], gap)
                if gap:
                    stats["strict_gap_tables"] += 1
            elif (r_full, r_fixed) != (0, 0):
                raise Mismatch({"part": "B", "reason": "accepted table radius",
                                "rows": rows, "radii": [r_full, r_fixed]})
        if len(rows) == max_rows:
            return
        for code in range(start, len(codes)):
            rec(code, rows + [codes[code]],
                dp_step(st_full, opts_full[code], None),
                dp_step(st_fixed, opts_fixed[code], None))

    start_state = {(1, 1): 0}
    rec(0, [], start_state, start_state)
    stats["by_rows"] = {str(k): v for k, v in sorted(stats["by_rows"].items())}
    stats["crosstab"] = dict(sorted(stats["crosstab"].items(),
                                    key=lambda kv: tuple(map(int, kv[0].split(",")))))
    expected_tables = sum(comb(16 + n - 1, n) for n in range(1, max_rows + 1))
    if stats["tables"] != expected_tables:
        raise Mismatch({"part": "B", "reason": "table count", "tables": stats["tables"]})
    stats.update(q=q, d=d, family=[[0, 1], [0, 2]], max_rows=max_rows,
                 raw_rows=raw_rows)
    return stats


# --------------------------------------------------------------------------

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compute():
    return {"part_a": part_a(), "control": control(), "part_b": part_b()}


def git(*args):
    return subprocess.run(["git", *args], cwd=HERE, capture_output=True,
                          text=True, check=True).stdout.strip()


def main():
    verify = "--verify" in sys.argv[1:]
    summary_path = HERE / "results" / "summary.json"
    started = time.time()
    try:
        body = compute()
    except Mismatch as exc:
        if not verify:
            (HERE / "results").mkdir(exist_ok=True)
            (HERE / "results" / "counterexample.json").write_text(
                json.dumps(exc.args[0], indent=2, default=list) + "\n")
        print("MISMATCH", json.dumps(exc.args[0], default=list))
        return 1
    elapsed = round(time.time() - started, 1)
    if verify:
        stored = json.loads(summary_path.read_text())
        same = all(stored[k] == json.loads(json.dumps(body[k])) for k in body)
        hashes = (stored["protocol_sha256"] == sha256(HERE / "protocol.md")
                  and stored["code_sha256"] == sha256(__file__))
        print(json.dumps({"status": "passed" if same and hashes else "failed",
                          "results_match": same, "hashes_match": hashes,
                          "elapsed_seconds": elapsed}))
        return 0 if same and hashes else 1
    rel = "experiments/E014-scale-sharpness/verify_scale.py"
    if git("status", "--porcelain", "--", "verify_scale.py", "protocol.md"):
        print("refusing to run: protocol or implementation is not committed")
        return 1
    summary = {
        "experiment": "E014-scale-sharpness",
        "status": "passed",
        "protocol_sha256": sha256(HERE / "protocol.md"),
        "code_sha256": sha256(__file__),
        "implementation_commit": git("log", "-1", "--format=%H", "--", "verify_scale.py"),
        "protocol_commit": git("log", "-1", "--format=%H", "--", "protocol.md"),
        "implementation_path": rel,
        "python": sys.version.split()[0],
        "elapsed_seconds": elapsed,
        **body,
    }
    (HERE / "results").mkdir(exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({"status": "passed", "elapsed_seconds": elapsed,
                      "part_a": [[c["case"], c["observed"]] for c in body["part_a"]],
                      "control": body["control"]["observed"],
                      "part_b_crosstab": body["part_b"]["crosstab"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
