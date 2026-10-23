"""Cell-factorized raw-domain MILP; no canonical actions, masks or radius formulas."""
from dataclasses import dataclass

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import csc_array


def accepts(table, rules):
    target = table[0]
    for columns in rules:
        counts = {}
        for row in table:
            if tuple(row[column] for column in columns) == tuple(target[column] for column in columns):
                counts[row[-1]] = counts.get(row[-1], 0)+1
        if any(number >= counts[target[-1]] for value, number in counts.items() if value != target[-1]):
            return False
    return True


@dataclass
class Model:
    objective: np.ndarray
    matrix: object
    lower: np.ndarray
    upper: np.ndarray
    cells: dict
    table: tuple
    rules: tuple


def build(table, rules, key_alphabet, rhs_alphabet):
    objective, rows, lower, upper = [], [], [], []

    def variable(cost=0):
        index = len(objective)
        objective.append(float(cost))
        return index

    def constraint(coefficients, lo=-np.inf, hi=np.inf):
        rows.append(coefficients)
        lower.append(float(lo))
        upper.append(float(hi))

    def conjunction(output, inputs):
        for index in inputs:
            constraint({output: 1, index: -1}, hi=0)
        coefficients = {index: -1 for index in inputs}
        coefficients[output] = 1
        constraint(coefficients, lo=1-len(inputs))

    cells = {}
    for i in range(1, len(table)):
        for column in range(len(table[i])):
            size = key_alphabet if column < len(table[i])-1 else rhs_alphabet
            choices = tuple(variable(value != table[i][column]) for value in range(size))
            cells[i, column] = choices
            constraint({index: 1 for index in choices}, lo=1, hi=1)
    joined = {}
    for i in range(1, len(table)):
        for g, columns in enumerate(rules):
            membership = variable()
            conjunction(membership, tuple(cells[i, column][table[0][column]] for column in columns))
            for value in range(rhs_alphabet):
                combined = variable()
                conjunction(combined, (membership, cells[i, len(table[i])-1][value]))
                joined[i, g, value] = combined
    margin_coefficients = []
    for g in range(len(rules)):
        for value in range(1, rhs_alphabet):
            coefficients = {}
            for i in range(1, len(table)):
                coefficients[joined[i, g, 0]] = 1
                coefficients[joined[i, g, value]] = -1
            margin_coefficients.append(coefficients)
    if accepts(table, rules):
        selectors = []
        for coefficients in margin_coefficients:
            selected = variable()
            selectors.append(selected)
            coefficients[selected] = len(table)
            constraint(coefficients, hi=len(table)-1)
        constraint({index: 1 for index in selectors}, lo=1, hi=1)
    else:
        for coefficients in margin_coefficients:
            constraint(coefficients, lo=0)
    row_indices, column_indices, values = [], [], []
    for row, coefficients in enumerate(rows):
        for column, value in coefficients.items():
            row_indices.append(row)
            column_indices.append(column)
            values.append(value)
    matrix = csc_array((np.array(values, dtype=float),
                        (np.array(row_indices, dtype=np.int32), np.array(column_indices, dtype=np.int32))),
                       shape=(len(rows), len(objective)))
    return Model(np.array(objective), matrix, np.array(lower), np.array(upper),
                 cells, table, rules)


def solve(table, rules, key_alphabet, rhs_alphabet):
    model = build(table, rules, key_alphabet, rhs_alphabet)
    result = milp(model.objective, integrality=np.ones(len(model.objective), dtype=np.int32),
                  bounds=Bounds(np.zeros(len(model.objective)), np.ones(len(model.objective))),
                  constraints=LinearConstraint(model.matrix, model.lower, model.upper),
                  options={'presolve': True, 'mip_rel_gap': 0.0, 'time_limit': 10.0})
    record = {'status': int(result.status), 'message': str(result.message),
              'variables': len(model.objective), 'constraints': len(model.lower),
              'cost': None, 'witness': None, 'verification_errors': []}
    if result.status != 0:
        return record
    if result.x is None or result.fun is None:
        record['verification_errors'].append('missing_optimal_primal')
        return record
    rounded = np.rint(result.x)
    integrality_error = float(np.max(np.abs(result.x-rounded)))
    raw_lhs = model.matrix @ result.x
    rounded_lhs = model.matrix @ rounded
    residual = max(float(np.max(np.maximum(model.lower-raw_lhs, 0))),
                   float(np.max(np.maximum(raw_lhs-model.upper, 0))),
                   float(np.max(np.maximum(model.lower-rounded_lhs, 0))),
                   float(np.max(np.maximum(rounded_lhs-model.upper, 0))),
                   float(np.max(np.maximum(-result.x, 0))),
                   float(np.max(np.maximum(result.x-1, 0))))
    if integrality_error > 1e-7 or residual > 1e-7:
        record['verification_errors'].append('linear_or_integer_residual')
    changed = [list(row) for row in table]
    for (i, column), choices in model.cells.items():
        selected = [value for value, index in enumerate(choices) if rounded[index] == 1]
        if len(selected) != 1:
            record['verification_errors'].append('non_onehot_cell')
            continue
        changed[i][column] = selected[0]
    witness = tuple(tuple(row) for row in changed)
    cost = sum(a != b for old, new in zip(table, witness) for a, b in zip(old, new))
    if abs(float(result.fun)-cost) > 1e-7:
        record['verification_errors'].append('raw_cost_differs_from_objective')
    if witness[0] != table[0] or accepts(table, rules) == accepts(witness, rules):
        record['verification_errors'].append('target_changed_or_decision_not_flipped')
    record.update(cost=cost, witness=witness, maximum_integrality_error=integrality_error,
                  maximum_constraint_residual=residual, objective=float(result.fun),
                  mip_gap=None if getattr(result, 'mip_gap', None) is None else float(result.mip_gap))
    return record
