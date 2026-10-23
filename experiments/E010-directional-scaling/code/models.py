"""General-q exact specializations and a pinned raw-cell comparison model."""
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
import sys
from time import perf_counter

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csc_array

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'E009-singleton-characterization/code'))
import generic_milp as baseline


def accepted_formula(table, rules, rhs):
    start = perf_counter()
    candidates = []
    for columns in rules:
        members = [i for i, row in enumerate(table) if all(row[j] == 0 for j in columns)]
        counts = Counter(table[i][-1] for i in members)
        rival = max(range(1, rhs), key=lambda v: (counts[v], -v))
        if counts[0] <= counts[rival]:
            raise ValueError('Formula requires initial acceptance')
        if len(members) > 1:
            cost = (counts[0]-counts[rival]+1)//2
            indices = tuple(i for i in members if i and table[i][-1] == 0)[:cost]
            candidates.append((cost, ('rhs', rival, indices)))
        else:
            best = min(((sum(table[i][j] != 0 for j in columns)+(table[i][-1] == 0), i)
                        for i in range(1, len(table))), default=None)
            if best is not None:
                candidates.append((best[0], ('import', best[1], tuple(columns))))
    if not candidates:
        return {'status': 2, 'cost': None, 'witness': None, 'verification_errors': [],
                'build_seconds': 0.0, 'solve_seconds': 0.0,
                'total_seconds': perf_counter()-start, 'variables': 0, 'constraints': 0}
    cost, description = min(candidates, key=lambda x: x[0])
    changed = [list(row) for row in table]
    if description[0] == 'rhs':
        for i in description[2]:
            changed[i][-1] = description[1]
    else:
        i = description[1]
        for j in description[2]:
            changed[i][j] = 0
        if changed[i][-1] == 0:
            changed[i][-1] = 1
    return {'status': 0, 'cost': cost, 'witness': tuple(map(tuple, changed)),
            'verification_errors': [], 'build_seconds': 0.0, 'solve_seconds': 0.0,
            'total_seconds': perf_counter()-start, 'variables': 0, 'constraints': 0}


@dataclass
class ActionModel:
    objective: np.ndarray
    matrix: object
    lower: np.ndarray
    upper: np.ndarray
    choices: dict


def canonical_build(table, rules, rhs):
    q = len(table[0])-1
    costs, choices, row_indices, col_indices, coefficients = [], {}, [], [], []
    lower, upper = [], []
    margins = [dict() for _ in range(len(rules)*(rhs-1))]
    for i, original in enumerate(table[1:], 1):
        old = sum(1 << j for j in range(q) if original[j] == 0)
        destinations = []
        for mask in range(1 << q):
            if original[-1] == 0:
                values = (0,) if mask | old == mask else ()
            else:
                values = ((original[-1],) if mask & old == mask else ()) + ((0,) if mask | old == mask else ())
            for value in values:
                row = tuple(0 if mask & (1 << j) else (original[j] or 1) for j in range(q))+(value,)
                index = len(costs)
                costs.append(sum(a != b for a, b in zip(original, row)))
                destinations.append((index, row))
                for g, columns in enumerate(rules):
                    if all(row[j] == 0 for j in columns):
                        for v in range(1, rhs):
                            contribution = 1 if value == 0 else -1 if value == v else 0
                            if contribution:
                                margins[g*(rhs-1)+v-1][index] = contribution
        choices[i] = destinations
        r = len(lower)
        for index, _row in destinations:
            row_indices.append(r); col_indices.append(index); coefficients.append(1)
        lower.append(1); upper.append(1)
    for margin in margins:
        r = len(lower)
        for index, value in margin.items():
            row_indices.append(r); col_indices.append(index); coefficients.append(value)
        lower.append(0); upper.append(np.inf)
    matrix = csc_array((np.array(coefficients, dtype=float),
                        (np.array(row_indices, dtype=np.int32), np.array(col_indices, dtype=np.int32))),
                       shape=(len(lower), len(costs)))
    return ActionModel(np.array(costs, dtype=float), matrix, np.array(lower), np.array(upper), choices)


def finite_number(value):
    return float(value) if value is not None and np.isfinite(value) else None


def solve(table, rules, keys, rhs, method):
    start = perf_counter()
    if method == 'canonical' and baseline.accepts(table, rules):
        raise ValueError('Canonical accepting MILP requires initial rejection')
    model = baseline.build(table, rules, keys, rhs) if method == 'generic' else canonical_build(table, rules, rhs)
    built = perf_counter()
    result = milp(model.objective, integrality=np.ones(len(model.objective), dtype=np.int32),
                  bounds=Bounds(0, 1), constraints=LinearConstraint(model.matrix, model.lower, model.upper),
                  options={'presolve': True, 'mip_rel_gap': 0.0, 'time_limit': 1.0})
    solved = perf_counter()
    record = {'status': int(result.status), 'message': str(result.message), 'cost': None,
              'witness': None, 'variables': len(model.objective), 'constraints': len(model.lower),
              'build_seconds': built-start, 'solve_seconds': solved-built, 'verification_errors': [],
              'objective': finite_number(result.fun),
              'dual_bound': finite_number(getattr(result, 'mip_dual_bound', None)),
              'mip_gap': finite_number(getattr(result, 'mip_gap', None))}
    if result.x is not None and np.all(np.isfinite(result.x)):
        rounded = np.rint(result.x)
        raw_lhs, rounded_lhs = model.matrix @ result.x, model.matrix @ rounded
        integrality = float(np.max(np.abs(result.x-rounded)))
        residual = max(float(np.max(np.maximum(model.lower-raw_lhs, 0))),
                       float(np.max(np.maximum(raw_lhs-model.upper, 0))),
                       float(np.max(np.maximum(model.lower-rounded_lhs, 0))),
                       float(np.max(np.maximum(rounded_lhs-model.upper, 0))),
                       float(np.max(np.maximum(-result.x, 0))), float(np.max(np.maximum(result.x-1, 0))))
        record.update(maximum_integrality_error=integrality, maximum_constraint_residual=residual)
        if integrality > 1e-7 or residual > 1e-7:
            record['verification_errors'].append('linear_or_integer_residual')
        changed = [list(row) for row in table]
        if method == 'generic':
            for (i, column), alternatives in model.cells.items():
                selected = [v for v, index in enumerate(alternatives) if rounded[index] == 1]
                if len(selected) != 1:
                    record['verification_errors'].append('non_onehot_cell')
                else:
                    changed[i][column] = selected[0]
        else:
            for i, alternatives in model.choices.items():
                selected = [row for index, row in alternatives if rounded[index] == 1]
                if len(selected) != 1:
                    record['verification_errors'].append('non_onehot_row')
                else:
                    changed[i] = list(selected[0])
        record['witness'] = tuple(map(tuple, changed))
        record['cost'] = sum(a != b for r, s in zip(table, changed) for a, b in zip(r, s))
        if record['objective'] is None or abs(record['objective']-record['cost']) > 1e-7:
            record['verification_errors'].append('raw_cost_differs_from_objective')
    elif result.status == 0:
        record['verification_errors'].append('missing_optimal_primal')
    record['total_seconds'] = perf_counter()-start
    return record
