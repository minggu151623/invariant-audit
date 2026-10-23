"""Unrestricted raw-coordinate edit search; no candidate masks/actions/DP imports."""
from itertools import combinations, product


def accepts(table, rules):
    target = table[0]
    for columns in rules:
        frequencies = {}
        for row in table:
            if all(row[column] == target[column] for column in columns):
                frequencies[row[3]] = frequencies.get(row[3], 0)+1
        if any(number >= frequencies[target[3]] for value, number in frequencies.items()
               if value != target[3]):
            return False
    return True


def radius(table, rules, key_alphabet, rhs_alphabet):
    if len(table) == 1:
        return None, None
    initial = accepts(table, rules)
    coordinates = tuple((row, column) for row in range(1, len(table)) for column in range(4))
    upper = 4 if initial else len(table)-1
    for cost in range(1, upper+1):
        for selected in combinations(coordinates, cost):
            alternatives = [tuple(value for value in range(key_alphabet if column < 3 else rhs_alphabet)
                                  if value != table[row][column]) for row, column in selected]
            for values in product(*alternatives):
                changed = [list(row) for row in table]
                for (row, column), value in zip(selected, values):
                    changed[row][column] = value
                if accepts(changed, rules) != initial:
                    return cost, tuple(tuple(row) for row in changed)
    raise ValueError('Reference feasible upper bound was violated')
