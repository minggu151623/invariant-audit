"""Exact target-relative action prototype for same-RHS plurality FD decisions."""
from itertools import product

FAMILIES = (
    ('unary_disjoint', ((0,), (1,))),
    ('shared_compound', ((0, 1), (0, 2))),
    ('nested', ((0,), (0, 1))),
    ('single_triple', ((0, 1, 2),)),
    ('triangle', ((0, 1), (0, 2), (1, 2))),
    ('unary_compound', ((0,), (1, 2))),
)


def key_mask(row):
    return sum(1 << column for column in range(3) if row[column] == 0)


def group_masks(rules):
    return tuple(sum(1 << column for column in rule) for rule in rules)


def hamming(left, right):
    return sum(a != b for a, b in zip(left, right))


def reconstruct(original, mask, value):
    return tuple(0 if mask & (1 << column) else (original[column] or 1)
                 for column in range(3)) + (value,)


def contribution(row, rules, alphabet):
    mask = key_mask(row)
    return tuple((1 if row[3] == 0 else -1 if row[3] == rival else 0)
                 if mask & group == group else 0
                 for group in group_masks(rules) for rival in range(1, alphabet))


def accepts(table, rules, alphabet):
    margins = [1] * (len(rules)*(alphabet-1))
    for row in table[1:]:
        margins = [a+b for a, b in zip(margins, contribution(row, rules, alphabet))]
    return all(margin >= 1 for margin in margins)


def canonical_actions(original, rules, alphabet):
    old = key_mask(original)
    destinations = set()
    for mask in range(8):
        if original[3] == 0:
            if mask | old == mask:
                destinations.add(reconstruct(original, mask, 0))
        else:
            if mask & old == mask:
                destinations.add(reconstruct(original, mask, original[3]))
            if mask | old == mask:
                destinations.add(reconstruct(original, mask, 0))
    return tuple((hamming(original, row), row, contribution(row, rules, alphabet))
                 for row in sorted(destinations))


def accepting_minimum(table, rules, alphabet):
    start = (1,) * (len(rules)*(alphabet-1))
    states = {start: (0, ())}
    maximum_states = 1
    for original in table[1:]:
        following = {}
        for margins, (cost, path) in states.items():
            for step, row, vector in canonical_actions(original, rules, alphabet):
                destination = tuple(a+b for a, b in zip(margins, vector))
                proposal = (cost+step, path+(row,))
                if destination not in following or proposal < following[destination]:
                    following[destination] = proposal
        states = following
        maximum_states = max(maximum_states, len(states))
    feasible = [item for margins, item in states.items() if all(margin >= 1 for margin in margins)]
    if not feasible:
        raise ValueError('Changing all context RHS cells to zero must allow acceptance')
    cost, path = min(feasible)
    return cost, (table[0],)+path, maximum_states


def rejecting_minimum(table, rules, alphabet):
    candidates = []
    maximum_states = 1
    for group in group_masks(rules):
        for rival in range(1, alphabet):
            states = {1: (0, ())}
            for original in table[1:]:
                options = {}
                for mask, value in product(range(8), range(alphabet)):
                    row = reconstruct(original, mask, value)
                    amount = (1 if value == 0 else -1 if value == rival else 0) if mask & group == group else 0
                    action = (hamming(original, row), row)
                    if amount not in options or action < options[amount]:
                        options[amount] = action
                following = {}
                for margin, (cost, path) in states.items():
                    for amount, (step, row) in options.items():
                        proposal = (cost+step, path+(row,))
                        if margin+amount not in following or proposal < following[margin+amount]:
                            following[margin+amount] = proposal
                states = following
                maximum_states = max(maximum_states, len(states))
            candidates.extend(item for margin, item in states.items() if margin <= 0)
    if not candidates:
        return None, None, maximum_states
    cost, path = min(candidates)
    return cost, (table[0],)+path, maximum_states


def radius(table, rules, alphabet):
    if accepts(table, rules, alphabet):
        return rejecting_minimum(table, rules, alphabet)
    return accepting_minimum(table, rules, alphabet)
