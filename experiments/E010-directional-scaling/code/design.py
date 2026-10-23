"""Frozen synthetic generators, with direct raw-count and raw-destination checks."""
from collections import Counter
from hashlib import sha256
from itertools import product
import random


def families(q):
    return (('star', tuple((0, j) for j in range(1, q))),
            ('pairs', tuple((j, j+1) for j in range(0, q, 2))))


def accepts(table, rules):
    for columns in rules:
        votes = Counter(row[-1] for row in table if all(row[j] == table[0][j] for j in columns))
        if any(count >= votes[table[0][-1]] for value, count in votes.items() if value != table[0][-1]):
            return False
    return True


def witness_errors(table, rules, keys, rhs, result):
    w = result['witness']
    if w is None:
        return ['missing_optimal_witness'] if result['status'] == 0 else []
    if len(w) != len(table) or tuple(w[0]) != tuple(table[0]):
        return ['shape_or_target']
    if any(len(row) != len(table[0]) or any(not 0 <= v < (rhs if j == len(row)-1 else keys)
                                           for j, v in enumerate(row)) for row in w):
        return ['domain']
    errors = []
    if sum(a != b for r, s in zip(table, w) for a, b in zip(r, s)) != result['cost']:
        errors.append('cell_cost')
    if accepts(table, rules) == accepts(w, rules):
        errors.append('not_flipped')
    return errors


def raw_radius(table, rules, keys, rhs):
    symbols = tuple(product(*(tuple(range(keys)) for _ in table[0][:-1]), range(rhs)))
    initial, best = accepts(table, rules), None
    for rows in product(symbols, repeat=len(table)-1):
        changed = (table[0],)+rows
        cost = sum(a != b for r, s in zip(table, changed) for a, b in zip(r, s))
        if (best is None or cost < best) and accepts(changed, rules) != initial:
            best = cost
    return best


def fixtures():
    for q, keys, rhs in product((2, 4, 6), (2, 3), (2, 3)):
        rows = ((0,)*q+(0,), (0,)*q+(1,), (1,)*q+(0,), (1,)*q+(1,),
                tuple(0 if j % 2 == 0 else keys-1 for j in range(q))+(rhs-1,),
                (keys-1,)*q+(rhs-1,))
        for name, rules in families(q):
            for row in rows:
                yield keys, rhs, name, rules, ((0,)*(q+1), row)
    for q in (2, 4, 6):
        alternating = tuple(j % 2 for j in range(q))
        pairs = (((0,)*q+(1,), (0,)*q+(1,)),
                 (alternating+(1,), tuple(1-j for j in alternating)+(1,)),
                 ((1,)*q+(0,), (0,)*q+(1,)))
        for name, rules in families(q):
            for rows in pairs:
                yield 2, 2, name, rules, ((0,)*(q+1),)+rows


def cases():
    for q, n, rhs in product((2, 4, 6), (16, 128), (2, 4)):
        for name, rules in families(q):
            for regime in ('accepted_dense', 'accepted_singleton', 'rejected_coupled'):
                identity = f'q{q}-n{n}-d{rhs}-{name}-{regime}'
                rng = random.Random(int.from_bytes(sha256(identity.encode()).digest(), 'big'))
                rows = [(0,)*(q+1)]
                for i in range(n-1):
                    if regime == 'accepted_dense':
                        block, offset = divmod(i, 4)
                        if offset == 0:
                            keys = (0,)*q if block == 0 else tuple(0 if rng.random() < .65 else rng.randrange(1, 4) for _ in range(q))
                        value = 0 if offset < 3 else 1+block % (rhs-1)
                    elif regime == 'accepted_singleton':
                        keys = tuple(rng.randrange(1, 4) for _ in range(q))
                        value = rng.randrange(rhs)
                        if i == 0:
                            value = 1
                    else:
                        keys = (0,)*q if i < 4 else tuple(0 if rng.random() < .65 else rng.randrange(1, 4) for _ in range(q))
                        value = 1 if i < 4 else rng.randrange(1, rhs)
                    rows.append(keys+(value,))
                table = tuple(rows)
                expected = regime.startswith('accepted')
                if accepts(table, rules) != expected:
                    raise ValueError(f'Declared decision mismatch: {identity}')
                sizes = [sum(all(row[j] == 0 for j in columns) for row in table) for columns in rules]
                if regime == 'accepted_dense' and min(sizes) < 2:
                    raise ValueError(f'Unexpected singleton: {identity}')
                if regime == 'accepted_singleton' and set(sizes) != {1}:
                    raise ValueError(f'Unexpected nonsingleton: {identity}')
                yield {'case_id': identity, 'q': q, 'n': n, 'rhs': rhs, 'keys': 4,
                       'family': name, 'regime': regime, 'rules': rules, 'table': table}
