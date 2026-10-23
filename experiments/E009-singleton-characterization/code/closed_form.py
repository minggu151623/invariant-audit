"""Accepted-target flip radius from non-singleton margins and singleton imports."""
from collections import Counter


def radius(table, rules, alphabet):
    target = table[0]
    candidates = []
    groups = []
    for columns in rules:
        indices = tuple(i for i, row in enumerate(table)
                        if all(row[column] == target[column] for column in columns))
        counts = Counter(table[i][-1] for i in indices)
        rival = max(range(1, alphabet), key=lambda value: (counts[value], -value))
        if counts[0] <= counts[rival]:
            raise ValueError('Closed form requires an initially accepted target')
        groups.append({'columns': columns, 'size': len(indices), 'target_count': counts[0],
                       'largest_rival_count': counts[rival]})
        if len(indices) > 1:
            cost = (counts[0]-counts[rival]+1)//2
            chosen = tuple(i for i in indices if i and table[i][-1] == 0)[:cost]
            if len(chosen) != cost:
                raise ValueError('Protected target leaves insufficient RHS witness cells')
            changed = [list(row) for row in table]
            for i in chosen:
                changed[i][-1] = rival
            candidates.append((cost, tuple(tuple(row) for row in changed)))
        else:
            for i in range(1, len(table)):
                changed = [list(row) for row in table]
                for column in columns:
                    changed[i][column] = target[column]
                if changed[i][-1] == 0:
                    changed[i][-1] = 1
                cost = sum(a != b for a, b in zip(table[i], changed[i]))
                candidates.append((cost, tuple(tuple(row) for row in changed)))
    result = min(candidates) if candidates else (None, None)
    return result[0], result[1], groups
