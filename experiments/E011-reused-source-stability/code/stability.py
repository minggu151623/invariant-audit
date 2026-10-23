"""Fixed/full radii with sparse canonical accepting constraints."""
from collections import Counter
from itertools import product
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csc_array

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'E010-directional-scaling/code'))
import models as e010_models
import design as e010_design


def accepts(table, rules):
    for columns in rules:
        counts = Counter(row[-1] for row in table if all(row[j] == 0 for j in columns))
        if any(n >= counts[0] for v, n in counts.items() if v != 0):
            return False
    return True


def accepted_fixed(table, rules):
    choices = []
    for columns in rules:
        members = [i for i, row in enumerate(table) if all(row[j] == 0 for j in columns)]
        counts = Counter(table[i][-1] for i in members)
        if len(members) > 1:
            rival = max((v for v in counts if v), key=lambda v: (counts[v], -v), default=1)
            cost = (counts[0]-counts[rival]+1)//2
            indices = tuple(i for i in members if i and table[i][-1] == 0)[:cost]
            if len(indices) != cost:
                raise ValueError('Insufficient protected-key witness cells')
            choices.append((cost, rival, indices))
    if not choices:
        return dict(status=2, cost=None, witness=None, verification_errors=[])
    cost, rival, indices = min(choices)
    changed = [list(row) for row in table]
    for i in indices:
        changed[i][-1] = rival
    return dict(status=0, cost=cost, witness=tuple(map(tuple, changed)), verification_errors=[])


def check_witness(table, rules, sizes, result, fixed=False):
    errors = list(result['verification_errors'])
    witness = result['witness']
    if witness is None:
        if result['status'] == 0:
            errors.append('missing_optimal_witness')
        return errors
    if len(witness) != len(table) or tuple(witness[0]) != tuple(table[0]):
        return errors+['target_or_shape']
    if any(len(row) != len(sizes) or any(not isinstance(v, (int, np.integer)) or not 0 <= v < sizes[j]
                                        for j, v in enumerate(row)) for row in witness):
        return errors+['domain']
    if fixed and any(r[:-1] != s[:-1] for r, s in zip(table, witness)):
        errors.append('fixed_keys_changed')
    if sum(a != b for r, s in zip(table, witness) for a, b in zip(r, s)) != result['cost']:
        errors.append('cell_cost')
    if accepts(table, rules) == accepts(witness, rules):
        errors.append('decision_not_flipped')
    return errors


def active_model(table, rules, fixed):
    q = len(table[0])-1
    active = []
    for g, columns in enumerate(rules):
        values = sorted({row[-1] for row in table if row[-1] != 0 and all(row[j] == 0 for j in columns)})
        active.extend((g, value) for value in values)
    margins = {pair: {} for pair in active}
    objective, choices, constraints, lower, upper = [], {}, [], [], []
    for i, original in enumerate(table[1:], 1):
        old = sum(1 << j for j in range(q) if original[j] == 0)
        alternatives = []
        for mask in ((old,) if fixed else range(1 << q)):
            if original[-1] == 0:
                values = (0,) if mask | old == mask else ()
            else:
                values = ((original[-1],) if mask & old == mask else ()) + ((0,) if mask | old == mask else ())
            for value in values:
                row = tuple(0 if mask & (1 << j) else (original[j] or 1) for j in range(q))+(value,)
                index = len(objective)
                objective.append(sum(a != b for a, b in zip(original, row)))
                alternatives.append((index, row))
                for g, columns in enumerate(rules):
                    if all(row[j] == 0 for j in columns):
                        for group, rival in active:
                            if group == g:
                                amount = 1 if value == 0 else -1 if value == rival else 0
                                if amount:
                                    margins[group, rival][index] = amount
        choices[i] = alternatives
        constraints.append({index: 1 for index, row in alternatives}); lower.append(1); upper.append(1)
    for pair in active:
        constraints.append(margins[pair]); lower.append(0); upper.append(np.inf)
    rows, columns, values = [], [], []
    for i, constraint in enumerate(constraints):
        for j, value in constraint.items():
            rows.append(i); columns.append(j); values.append(value)
    matrix = csc_array((np.array(values, dtype=float),
                        (np.array(rows, dtype=np.int32), np.array(columns, dtype=np.int32))),
                       shape=(len(lower), len(objective)))
    return np.array(objective, dtype=float), matrix, np.array(lower), np.array(upper), choices, active


def solve_accepting(table, rules, fixed=False):
    if accepts(table, rules):
        raise ValueError('Accepting solve requires initial rejection')
    objective, matrix, lower, upper, choices, active = active_model(table, rules, fixed)
    answer = milp(objective, integrality=np.ones(len(objective), dtype=np.int32),
                  bounds=Bounds(0, 1), constraints=LinearConstraint(matrix, lower, upper),
                  options=dict(presolve=True, mip_rel_gap=0.0, time_limit=5.0))
    number = e010_models.finite_number
    result = dict(status=int(answer.status), message=str(answer.message), cost=None, witness=None,
                  objective=number(answer.fun), dual_bound=number(getattr(answer, 'mip_dual_bound', None)),
                  gap=number(getattr(answer, 'mip_gap', None)), variables=len(objective), constraints=len(lower),
                  active_rival_constraints=len(active), verification_errors=[])
    if answer.x is not None and np.all(np.isfinite(answer.x)):
        rounded = np.rint(answer.x)
        raw_lhs, rounded_lhs = matrix @ answer.x, matrix @ rounded
        integrality = float(np.max(np.abs(answer.x-rounded)))
        residual = max(float(np.max(np.maximum(lower-raw_lhs, 0))),
                       float(np.max(np.maximum(raw_lhs-upper, 0))),
                       float(np.max(np.maximum(lower-rounded_lhs, 0))),
                       float(np.max(np.maximum(rounded_lhs-upper, 0))),
                       float(np.max(np.maximum(-answer.x, 0))), float(np.max(np.maximum(answer.x-1, 0))))
        result.update(maximum_integrality_error=integrality, maximum_constraint_residual=residual)
        if integrality > 1e-7 or residual > 1e-7:
            result['verification_errors'].append('linear_or_integer_residual')
        changed = [table[0]]
        for i in range(1, len(table)):
            selected = [row for index, row in choices[i] if rounded[index] == 1]
            if len(selected) != 1:
                result['verification_errors'].append('non_onehot_action')
            changed.append(selected[0] if selected else table[i])
        result['witness'] = tuple(changed)
        result['cost'] = sum(a != b for r, s in zip(table, changed) for a, b in zip(r, s))
        if result['objective'] is None or abs(result['objective']-result['cost']) > 1e-7:
            result['verification_errors'].append('objective_cost_mismatch')
        if answer.status == 0 and (result['gap'] is None or result['gap'] > 1e-7 or
                                   result['dual_bound'] is None or abs(result['dual_bound']-result['cost']) > 1e-7):
            result['verification_errors'].append('optimal_bound_mismatch')
    elif answer.status == 0:
        result['verification_errors'].append('missing_optimal_primal')
    return result


def fixed_raw_radius(table, rules, rhs):
    initial, best = accepts(table, rules), None
    for values in product(range(rhs), repeat=len(table)-1):
        changed = (table[0],)+tuple(row[:-1]+(v,) for row, v in zip(table[1:], values))
        cost = sum(a[-1] != b[-1] for a, b in zip(table, changed))
        if (best is None or cost < best) and accepts(changed, rules) != initial:
            best = cost
    return best


def preflight():
    records, errors = [], []
    for i, (keys, rhs, family, rules, table) in enumerate(e010_design.fixtures()):
        sizes = (keys,)*(len(table[0])-1)+(rhs,)
        full_truth = e010_design.raw_radius(table, rules, keys, rhs)
        fixed_truth = fixed_raw_radius(table, rules, rhs)
        accepted = accepts(table, rules)
        full = e010_models.accepted_formula(table, rules, rhs) if accepted else solve_accepting(table, rules)
        fixed = accepted_fixed(table, rules) if accepted else solve_accepting(table, rules, True)
        for name, result, truth in (('full', full, full_truth), ('fixed', fixed, fixed_truth)):
            result['verification_errors'] = check_witness(table, rules, sizes, result, name == 'fixed')
            if result['status'] != (2 if truth is None else 0) or result['cost'] != truth or result['verification_errors']:
                errors.append(dict(index=i, method=name, expected=truth, status=result['status'],
                                   cost=result['cost'], errors=result['verification_errors']))
        records.append(dict(index=i, keys=keys, rhs=rhs, family=family, table=table, rules=rules,
                            full_truth=full_truth, fixed_truth=fixed_truth, full=full, fixed=fixed))
    if len(records) != 162:
        raise ValueError('Preflight fixture count')
    return records, errors
