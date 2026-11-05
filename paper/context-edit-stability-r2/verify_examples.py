"""Raw-destination checks for M32's analytical illustrations, not a benchmark."""
import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


def accepts(table, rules):
    target = table[0]
    for rule in rules:
        counts = {}
        for row in table:
            if all(row[j] == target[j] for j in rule):
                counts[row[-1]] = counts.get(row[-1], 0) + 1
        if any(count >= counts.get(target[-1], 0)
               for value, count in counts.items() if value != target[-1]):
            return False
    return True


def satisfies_fds(table, rules):
    for rule in rules:
        values = {}
        for row in table:
            key = tuple(row[j] for j in rule)
            if key in values and values[key] != row[-1]:
                return False
            values[key] = row[-1]
    return True


def edits(original, destination):
    return [dict(row=i, column=j, before=x, after=y)
            for i, (a, b) in enumerate(zip(original, destination))
            for j, (x, y) in enumerate(zip(a, b)) if x != y]


def enumerate_case(name, table, rules, domains, fixed=False, repair=True):
    initial = accepts(table, rules)
    row_domain = tuple(product(*domains))
    choices = [tuple(row[:-1] + (y,) for y in domains[-1]) if fixed else row_domain
               for row in table[1:]]
    best_flip = best_repair = None
    flip_table = repair_table = None
    total = 0
    for context in product(*choices):
        candidate = (table[0],) + context
        total += 1
        cost = sum(x != y for a, b in zip(table, candidate) for x, y in zip(a, b))
        if accepts(candidate, rules) != initial and (best_flip is None or cost < best_flip):
            best_flip, flip_table = cost, candidate
        if repair and satisfies_fds(candidate, rules) and (best_repair is None or cost < best_repair):
            best_repair, repair_table = cost, candidate
    record = dict(name=name, original=table, rules=rules, domains=domains,
                  fixed_keys=fixed, initial_accept=initial,
                  destinations_enumerated=total, radius=best_flip,
                  flip_destination=flip_table, flip_edits=edits(table, flip_table))
    if repair:
        record.update(repair_distance=best_repair, repair_destination=repair_table,
                      repair_edits=edits(table, repair_table))
    for dest, expected, test in [(flip_table, best_flip, lambda t: accepts(t, rules) != initial)] + (
            [(repair_table, best_repair, lambda t: satisfies_fds(t, rules))] if repair else []):
        if dest is None or dest[0] != table[0] or len(edits(table, dest)) != expected or not test(dest):
            raise ValueError(f'Invalid exhaustive witness for {name}')
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    cases = []
    for h in (1, 2, 3):
        table = ((0, 0),) * (2 * h + 1) + ((0, 1),)
        case = enumerate_case(f'A-h{h}', table, ((0,),), ((0, 1), (0, 1)))
        case['prediction_matches'] = case['repair_distance'] == 1 and case['radius'] == h
        cases.append(case)
    for k in (1, 2, 3):
        table = ((0, 0),) + tuple((i, y) for i in range(1, k + 1) for y in (0, 1))
        case = enumerate_case(f'B-k{k}', table, ((0,),), (tuple(range(k + 1)), (0, 1)))
        case['prediction_matches'] = case['repair_distance'] == k and case['radius'] == 1
        cases.append(case)
    coupled = ((0, 0, 0, 0), (0, 0, 1, 1), (0, 1, 0, 1), (1, 0, 0, 0))
    for fixed, expected in ((True, 2), (False, 1)):
        case = enumerate_case(f'coupled-fixed-{fixed}', coupled, ((0, 1), (0, 2)),
                              ((0, 1),) * 4, fixed=fixed, repair=False)
        case['prediction_matches'] = not case['initial_accept'] and case['radius'] == expected
        cases.append(case)
    outcome = dict(scope='finite_checks_of_analytically_derived_examples_not_new_empirical_benchmark',
                   implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                   case_count=len(cases), destinations_enumerated=sum(c['destinations_enumerated'] for c in cases),
                   all_predictions_match=all(c['prediction_matches'] for c in cases), cases=cases)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x') as stream:
        json.dump(outcome, stream, indent=2, sort_keys=True)
        stream.write('\n')
    if not outcome['all_predictions_match']:
        raise ValueError('Example mismatch; preserved outcome requires investigation')
    print(json.dumps({k: v for k, v in outcome.items() if k != 'cases'}, indent=2))


if __name__ == '__main__':
    main()
