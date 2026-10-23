"""Direct table recount across every replacement assignment; no certificate imports."""
from itertools import product

RULE_SETS = ((0,), (1,), (0, 1))


def decisions(table, values):
    local = []
    for bit in (1, 2):
        frequency = {}
        for i in range(len(table)):
            if table[i][0] & bit:
                frequency[values[i]] = frequency.get(values[i], 0) + 1
        target_count = frequency.get(0, 0)
        others = [number for value, number in frequency.items() if value != 0]
        local.append(all(target_count > number for number in others))
    return (local[0], local[1], local[0] and local[1])


def all_radii(table, alphabet):
    original = tuple(value for _mask, value in table)
    initial = decisions(table, original)
    best = [None, None, None]
    witnesses = [None, None, None]
    for tail in product(range(alphabet), repeat=len(table)-1):
        values = (0,) + tail
        distance = sum(a != b for a, b in zip(original, values))
        if not distance or all(cost is not None and cost <= distance for cost in best):
            continue
        counterfactual = decisions(table, values)
        for index in range(3):
            if counterfactual[index] != initial[index] and (best[index] is None or distance < best[index]):
                best[index] = distance
                witnesses[index] = values
    return {rules: (best[i], witnesses[i]) for i, rules in enumerate(RULE_SETS)}
