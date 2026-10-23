"""One locked structural check and raw-cell MILP baseline verification."""
from collections import Counter
import csv
from hashlib import sha256
import gzip
import importlib.util
import io
from itertools import product
import json
from pathlib import Path
import platform
import subprocess

import numpy as np
import scipy

import closed_form
import generic_milp

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = 'experiments/E009-singleton-characterization/protocol.md'
LOCK = '96962be'
RUN = 'e009-20261023-001'
REPORT = f'experiments/E009-singleton-characterization/results/run-{RUN}.md'
OUTPUTS = ('data/E009-v1-checks.json', 'data/E009-v1-formula-summary.csv',
           'data/E009-v1-baseline-cases.jsonl.gz', 'data/E009-v1-witnesses.json', REPORT)
PINS = {
    'reference': ('experiments/E008-mutable-key-certificates/code/exhaustive_reference.py',
                  'a9955309307a1c10388f750494c2546312c3cfa568ff90834a031bec189beac2'),
    'fixed': ('experiments/E007-fd-decision-stability/code/certificate.py',
              'aad95f5c6bed01e8741750f9d1d8ea792f97922c37ae01d27f255ca7a3eec70c'),
}
FAMILIES = (
    ('unary_disjoint', ((0,), (1,))), ('shared_compound', ((0, 1), (0, 2))),
    ('nested', ((0,), (0, 1))), ('single_triple', ((0, 1, 2),)),
    ('triangle', ((0, 1), (0, 2), (1, 2))), ('unary_compound', ((0,), (1, 2))),
)
DOMAINS_A = ((2, 2, 4), (2, 3, 3), (3, 2, 2), (3, 3, 2))
DOMAINS_B = ((2, 2, 3), (2, 3, 2), (3, 2, 2))


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def load_pinned(name):
    relative, digest = PINS[name]
    if sha256((ROOT / relative).read_bytes()).hexdigest() != digest:
        raise ValueError(f'Pinned module drift: {relative}')
    spec = importlib.util.spec_from_file_location(f'e009_pinned_{name}', ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def guard():
    environment = {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__}
    if environment != {'python': '3.13.5', 'numpy': '2.1.3', 'scipy': '1.17.1'}:
        raise ValueError(f'Locked runtime differs: {environment}')
    if any((ROOT / name).exists() or (ROOT / name).is_symlink() for name in OUTPUTS):
        raise ValueError('Existing output; no repeat under this identity')
    lock = git('rev-parse', LOCK).decode().strip()
    if (ROOT / PROTOCOL).read_bytes() != git('show', f'{lock}:{PROTOCOL}'):
        raise ValueError('Protocol drift')
    git('merge-base', '--is-ancestor', lock, 'HEAD')
    implementation = git('rev-parse', 'HEAD').decode().strip()
    for path in Path(__file__).parent.glob('*.py'):
        relative = path.relative_to(ROOT).as_posix()
        if path.read_bytes() != git('show', f'{implementation}:{relative}'):
            raise ValueError(f'Uncommitted implementation: {relative}')
    for name in PINS:
        load_pinned(name)
    return lock, implementation, environment


def blocks(domains):
    for keys, rhs, maximum in domains:
        symbols = tuple(product(range(keys), range(keys), range(keys), range(rhs)))
        for n in range(1, maximum+1):
            yield keys, rhs, n, symbols


def fixed_radius(table, rules, rhs, fixed):
    projected = tuple((sum(1 << i for i, columns in enumerate(rules)
                           if all(row[column] == 0 for column in columns)), row[-1]) for row in table)
    return fixed.radius(projected, tuple(range(len(rules))), rhs)[0]


def witness_errors(table, changed, cost, rules, keys, rhs, reference):
    if changed is None or len(changed) != len(table) or changed[0] != table[0]:
        return ['witness_shape_or_target']
    errors = []
    if any(len(row) != 4 or any(not 0 <= row[j] < (keys if j < 3 else rhs) for j in range(4)) for row in changed):
        errors.append('witness_outside_domain')
    actual = sum(a != b for before, after in zip(table, changed) for a, b in zip(before, after))
    if actual != cost:
        errors.append('raw_cell_cost')
    if reference.accepts(table, rules) == reference.accepts(changed, rules):
        errors.append('raw_decision_not_flipped')
    return errors


def build(lock, implementation, environment):
    reference, fixed = load_pinned('reference'), load_pinned('fixed')
    formula_rows, formula_failures, structure_failures = [], [], []
    formula_totals = Counter(cases=0, no_singleton=0, singleton_containing=0,
                             strict_finite_reduction=0, protected_INF_to_finite=0,
                             singleton_without_reduction=0, finite_witnesses=0)
    for keys, rhs, n, symbols in blocks(DOMAINS_A):
        aggregates = {name: Counter(cases=0, no_singleton=0, singleton_containing=0,
                                    strict_finite_reduction=0, protected_INF_to_finite=0,
                                    singleton_without_reduction=0, finite_witnesses=0)
                      for name, _rules in FAMILIES}
        for tail in product(symbols, repeat=n-1):
            table = ((0, 0, 0, 0),)+tail
            for name, rules in FAMILIES:
                if not reference.accepts(table, rules):
                    continue
                cost, changed, _groups = closed_form.radius(table, rules, rhs)
                truth, _witness = reference.radius(table, rules, keys, rhs)
                protected = fixed_radius(table, rules, rhs, fixed)
                has_singleton = any(sum(all(row[column] == 0 for column in columns) for row in table) == 1
                                    for columns in rules)
                errors = []
                if cost != truth:
                    errors.append('formula_radius')
                if cost is not None:
                    errors.extend(witness_errors(table, changed, cost, rules, keys, rhs, reference))
                elif changed is not None:
                    errors.append('infinite_radius_with_witness')
                if errors:
                    formula_failures.append({'keys': keys, 'rhs': rhs, 'table': table, 'family': name,
                                             'cost': cost, 'reference': truth, 'errors': errors, 'witness': changed})
                if not has_singleton and cost != protected:
                    structure_failures.append({'table': table, 'family': name, 'cost': cost,
                                               'protected': protected, 'error': 'no_singleton_inequality'})
                strict = cost is not None and protected is not None and cost < protected
                transition = cost is not None and protected is None
                if (strict or transition) and not has_singleton:
                    structure_failures.append({'table': table, 'family': name, 'error': 'strict_reduction_without_singleton'})
                for destination in (aggregates[name], formula_totals):
                    destination['cases'] += 1
                    destination['singleton_containing' if has_singleton else 'no_singleton'] += 1
                    destination['finite_witnesses'] += cost is not None
                    destination['strict_finite_reduction'] += strict
                    destination['protected_INF_to_finite'] += transition
                    destination['singleton_without_reduction'] += has_singleton and not strict and not transition
        for name, _rules in FAMILIES:
            formula_rows.append({'key_alphabet': keys, 'rhs_alphabet': rhs, 'rows': n,
                                 'family': name, **dict(aggregates[name])})
    baseline_cases, baseline_failures = [], []
    baseline_statuses = Counter()
    max_integrality = max_residual = 0.0
    for keys, rhs, n, symbols in blocks(DOMAINS_B):
        for tail in product(symbols, repeat=n-1):
            table = ((0, 0, 0, 0),)+tail
            for name, rules in FAMILIES:
                result = generic_milp.solve(table, rules, keys, rhs)
                expected, _witness = reference.radius(table, rules, keys, rhs)
                errors = list(result['verification_errors'])
                required_status = 2 if expected is None else 0
                if result['status'] != required_status or result['cost'] != expected:
                    errors.append('status_or_objective_differs_from_reference')
                if result['status'] == 0 and result['cost'] is not None:
                    errors.extend(witness_errors(table, result['witness'], result['cost'], rules, keys, rhs, reference))
                    max_integrality = max(max_integrality, result['maximum_integrality_error'])
                    max_residual = max(max_residual, result['maximum_constraint_residual'])
                item = {'case_index': len(baseline_cases), 'keys': keys, 'rhs': rhs,
                        'table': table, 'family': name, 'reference_radius': expected,
                        'initial_accepted': reference.accepts(table, rules), 'MILP': result,
                        'errors': errors}
                baseline_cases.append(item)
                baseline_statuses[str(result['status'])] += 1
                if errors:
                    baseline_failures.append(item)
    examples = {}
    for name, table, rules in (
        ('triple_singleton', ((0, 0, 0, 0), (1, 1, 1, 0)), ((0, 1, 2),)),
        ('shared_singleton', ((0, 0, 0, 0), (1, 0, 0, 1)), ((0, 1), (0, 2))),
    ):
        cost, changed, groups = closed_form.radius(table, rules, 2)
        expected = reference.radius(table, rules, 2, 2)[0]
        examples[name] = {'table': table, 'rules': rules, 'formula_radius': cost,
                          'reference_radius': expected, 'protected_radius': fixed_radius(table, rules, 2, fixed),
                          'witness': changed, 'groups': groups}
    h9a = formula_totals['cases'] == 18779 and not formula_failures
    h9b = not structure_failures
    h9c = (examples['triple_singleton']['formula_radius'], examples['shared_singleton']['formula_radius']) == (4, 1)
    h9c = h9c and all(value['protected_radius'] is None and value['formula_radius'] == value['reference_radius']
                      for value in examples.values())
    h9d = len(baseline_cases) == 2118 and not baseline_failures
    status = 'valid' if all((h9a, h9b, h9c, h9d)) else 'failed_mathematical_or_baseline_validation'
    checks = {'status': status, 'classification': 'finite_mathematical_validation_and_baseline_verification',
              'run_id': RUN, 'protocol_commit': lock, 'implementation_commit': implementation,
              'protocol_sha256': sha256((ROOT / PROTOCOL).read_bytes()).hexdigest(),
              'environment': environment, 'pinned_modules': PINS,
              'formula_totals': dict(formula_totals), 'formula_failures': formula_failures,
              'structure_failures': structure_failures, 'baseline_cases': len(baseline_cases),
              'baseline_status_counts': dict(baseline_statuses), 'baseline_failures': baseline_failures,
              'maximum_MILP_integrality_error': max_integrality, 'maximum_MILP_constraint_residual': max_residual,
              'H9a_formula': h9a, 'H9b_singleton_characterization': h9b,
              'H9c_scope_examples': h9c, 'H9d_generic_baseline': h9d,
              'runtime_comparison': False, 'novelty_established': False, 'independent_review': False}
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(formula_rows[0]))
    writer.writeheader()
    writer.writerows(formula_rows)
    cases = ''.join(json.dumps(row, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n'
                    for row in baseline_cases).encode()
    outputs = {OUTPUTS[0]: canonical(checks), OUTPUTS[1]: stream.getvalue().encode(),
               OUTPUTS[2]: gzip.compress(cases, mtime=0), OUTPUTS[3]: canonical(examples)}
    lines = [f'# E009-v1 — {RUN}', '', f'status: {status}',
             f'protocol_commit: {lock}', f'implementation_commit: {implementation}', '',
             f"Initially accepted formula cases: {formula_totals['cases']}; formula failures: {len(formula_failures)}.",
             f"No-singleton cases: {formula_totals['no_singleton']}; singleton-containing: {formula_totals['singleton_containing']}.",
             f'Structural failures: {len(structure_failures)}.',
             f'Generic raw-cell MILP cases: {len(baseline_cases)}; failures: {len(baseline_failures)}.',
             f'H9a: {h9a}; H9b: {h9b}; H9c: {h9c}; H9d: {h9d}.', '',
             'The formula concerns only initially accepted target cells under the locked same-RHS unit-cell-cost model.',
             'The generic baseline uses raw cell choices, conjunction linearizations and group count margins, not specialized actions.',
             'Optimality/infeasibility is compared with unrestricted edit enumeration; finite witnesses and linear residuals are checked.',
             'This verifies the formula and baseline formulation; no runtime speedup, representative-data performance or novelty follows.', '',
             '## Artifacts', '']
    for name, content in outputs.items():
        lines.append(f'- `{name}` SHA-256 `{sha256(content).hexdigest()}`')
    outputs[REPORT] = ('\n'.join(lines)+'\n').encode()
    return outputs


if __name__ == '__main__':
    lock, implementation, environment = guard()
    first = build(lock, implementation, environment)
    second = build(lock, implementation, environment)
    identical = first == second
    if not identical:
        checks = json.loads(first[OUTPUTS[0]])
        checks['status'] = 'failed_double_build_agreement'
        checks['double_build_disagreements'] = {
            name: {'first_sha256': sha256(first[name]).hexdigest(), 'second_sha256': sha256(second[name]).hexdigest(),
                   'second_content': (gzip.decompress(second[name]) if name.endswith('.gz') else second[name]).decode()}
            for name in OUTPUTS if first[name] != second[name]}
        first[OUTPUTS[0]] = canonical(checks)
        first[REPORT] = ('# E009 failed double-build agreement\n\nstatus: failed_double_build_agreement\n'
                         'See checks JSON for all differing second-build content; first-build other artifacts are retained.\n').encode()
    created = []
    try:
        for name in OUTPUTS:
            path = ROOT / name
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as stream:
                created.append(path)
                stream.write(first[name])
    except BaseException:
        for path in created:
            path.unlink()
        raise
    print(json.dumps({'status': json.loads(first[OUTPUTS[0]])['status'],
                      'double_build_byte_identical': identical, 'run_id': RUN}))
