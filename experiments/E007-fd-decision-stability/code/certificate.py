"""Prototype exact RHS-edit radius for protected-determinant FD plurality rules."""
from collections import Counter
from itertools import combinations


def groups(table, rules):
    return tuple(tuple(i for i, (mask, _value) in enumerate(table) if mask & (1 << g))
                 for g in rules)


def accepts(table, rules):
    for indices in groups(table, rules):
        counts = Counter(table[i][1] for i in indices)
        if any(counts[0] <= count for value, count in counts.items() if value != 0):
            return False
    return True


def repair_to_accept(table, rules, alphabet):
    blocks = groups(table, rules)
    counts = tuple(Counter(table[i][1] for i in block) for block in blocks)
    editable = tuple(i for i, (_mask, value) in enumerate(table)
                     if i and value != 0 and any(i in block for block in blocks))
    for cost in range(len(editable)+1):
        for chosen in combinations(editable, cost):
            if all(sum(i in block for i in chosen) +
                   sum(i in block and table[i][1] == value for i in chosen)
                   >= count[value] - count[0] + 1
                   for block, count in zip(blocks, counts)
                   for value in range(1, alphabet)):
                return cost, tuple((i, 0) for i in chosen)
    raise ValueError('All-to-target repair should be feasible under the stated model')


def radius(table, rules, alphabet):
    if not accepts(table, rules):
        return repair_to_accept(table, rules, alphabet)
    candidates = []
    for block in groups(table, rules):
        if len(block) < 2:
            continue
        counts = Counter(table[i][1] for i in block)
        rival = max(range(1, alphabet), key=lambda value: (counts[value], -value))
        cost = (counts[0] - counts[rival] + 1) // 2
        chosen = tuple(i for i in block if i and table[i][1] == 0)[:cost]
        if len(chosen) != cost:
            raise ValueError('Insufficient editable target-value cells for witness')
        candidates.append((cost, tuple((i, rival) for i in chosen)))
    return min(candidates) if candidates else (None, ())
