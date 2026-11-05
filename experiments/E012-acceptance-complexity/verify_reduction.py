"""Raw binary-cell checks for the E012 protocol; standard library only."""
from collections import Counter
from functools import reduce
from hashlib import sha256
from itertools import combinations, combinations_with_replacement
import json
from operator import or_
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent


def need(condition, detail):
    if not condition:
        raise ValueError(detail)


def union(masks):
    return reduce(or_, masks, 0)


def minimum_cover(q, sets):
    for cost in range(len(sets) + 1):
        for indices in combinations(range(len(sets)), cost):
            if union(sets[i] for i in indices) == (1 << q) - 1:
                return indices
    raise ValueError('Uncoverable input')


def construct(q, sets):
    rows = [[0] * (q + 1)]
    rows.extend([[0 if mask & (1 << g) else 1 for g in range(q)] + [1]
                 for mask in sets])
    for g in range(q):
        incidence = sum(bool(mask & (1 << g)) for mask in sets)
        for _ in range(incidence - 1):
            rows.append([0 if h == g else 1 for h in range(q)] + [0])
    return rows


def counts(rows, q):
    return [[sum(row[g] == 0 and row[q] == value for row in rows)
             for value in (0, 1)] for g in range(q)]


def accepts(rows, q):
    return all(a > b for a, b in counts(rows, q))


def changed_cells(before, after):
    return [(r, c) for r in range(len(before)) for c in range(len(before[0]))
            if before[r][c] != after[r][c]]


def extract_cover(q, sets, before, after):
    selected = set()
    for _, col in changed_cells(before, after):
        if col < q:
            selected.add(next(i for i, mask in enumerate(sets) if mask & (1 << col)))
    for i in range(len(sets)):
        if after[i + 1][q] == 0:
            selected.add(i)
    return sorted(selected)


def enumerate_destinations(q, sets, original, fixed):
    editable = [(r, c) for r in range(1, len(original))
                for c in ([q] if fixed else range(q + 1))]
    evaluated = successful = key_success = support_success = harmful_rhs_success = 0
    optimal_cost = None
    witness = None
    by_cost = []
    for cost in range(q + 1):
        level_count = level_accept = 0
        for edits in combinations(editable, cost):
            destination = [row.copy() for row in original]
            for row, col in edits:
                destination[row][col] ^= 1
            evaluated += 1
            level_count += 1
            if not accepts(destination, q):
                continue
            successful += 1
            level_accept += 1
            actual_edits = changed_cells(original, destination)
            need(destination[0] == original[0] and len(actual_edits) == cost,
                 'Wrong Hamming cost or changed protected row')
            extracted = extract_cover(q, sets, original, destination)
            need(union(sets[i] for i in extracted) == (1 << q) - 1,
                 dict(reason='Extraction not a cover', q=q, sets=sets, edits=edits))
            need(len(extracted) <= cost, 'Extraction exceeds edit budget')
            key_success += any(col < q for _, col in edits)
            support_success += any(row > len(sets) for row, _ in edits)
            harmful_rhs_success += any(col == q and original[row][col] == 0
                                       for row, col in edits)
            if optimal_cost is None:
                optimal_cost = cost
                witness = dict(edits=actual_edits, rows=destination,
                               extracted_cover_indices=extracted)
        by_cost.append(dict(cost=cost, destinations=level_count, accepting=level_accept))
    need(witness is not None, 'No accepting destination within universe-size bound')
    need(accepts(witness['rows'], q)
         and len(changed_cells(original, witness['rows'])) == optimal_cost,
         'Minimum witness fails direct recheck')
    return dict(radius=optimal_cost, witness=witness, evaluated=evaluated,
                accepting=successful, accepting_with_key_edits=key_success,
                accepting_with_support_edits=support_success,
                accepting_with_zero_to_one_rhs_edits=harmful_rhs_success,
                by_cost=by_cost)


def main():
    records = []
    totals = Counter()
    failed = None
    try:
        for q in range(1, 4):
            for size in range(1, 4):
                for sets in combinations_with_replacement(range(1 << q), size):
                    if union(sets) != (1 << q) - 1:
                        continue
                    cover = minimum_cover(q, sets)
                    rows = construct(q, sets)
                    initial = counts(rows, q)
                    need(all(a == b and a > 0 for a, b in initial),
                         dict(reason='Initial group not tied', q=q, sets=sets))
                    forward = [row.copy() for row in rows]
                    for i in cover:
                        forward[i + 1][q] = 0
                    need(accepts(forward, q)
                         and len(changed_cells(rows, forward)) == len(cover),
                         'Forward cover witness fails')
                    record = dict(q=q, set_masks=sets, table=rows, initial_counts=initial,
                                  cover_optimum=len(cover), cover_witness=cover)
                    for mode in ('fixed', 'full'):
                        result = enumerate_destinations(q, sets, rows, mode == 'fixed')
                        record[mode] = result
                        need(result['radius'] == len(cover),
                             dict(reason='Radius mismatch', case=record))
                        for field in ('evaluated', 'accepting', 'accepting_with_key_edits',
                                      'accepting_with_support_edits',
                                      'accepting_with_zero_to_one_rhs_edits'):
                            totals[mode + '_' + field] += result[field]
                    records.append(record)
    except Exception as exc:
        failed = str(exc)
    report = dict(experiment='E012', date='2026-11-05',
                  classification='confirmatory_finite_consistency_check_not_universal_proof',
                  python=sys.version, implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  protocol_sha256=sha256((HERE / 'protocol.md').read_bytes()).hexdigest(),
                  implementation_commit=subprocess.check_output(
                      ['git', 'rev-parse', 'HEAD'], cwd=HERE, text=True).strip(),
                  case_count=len(records), totals=dict(totals),
                  all_predictions_match=failed is None, failure=failed, cases=records)
    output = HERE / 'results.json'
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({key: value for key, value in report.items() if key != 'cases'}, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
