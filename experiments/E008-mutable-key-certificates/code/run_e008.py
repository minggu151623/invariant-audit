"""One locked mutable-key finite check with an unrestricted raw-cell reference."""
from collections import Counter
import csv
from hashlib import sha256
import importlib.util
import io
from itertools import product
import json
from pathlib import Path
import subprocess

import certificate as candidate
import exhaustive_reference as reference

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = 'experiments/E008-mutable-key-certificates/protocol.md'
LOCK = 'efc1365'
BASELINE = 'experiments/E007-fd-decision-stability/code/certificate.py'
BASELINE_SHA = 'aad95f5c6bed01e8741750f9d1d8ea792f97922c37ae01d27f255ca7a3eec70c'
RUN = 'e008-20261023-001'
REPORT = f'experiments/E008-mutable-key-certificates/results/run-{RUN}.md'
OUTPUTS = ('data/E008-v1-checks.json', 'data/E008-v1-domain-summary.csv',
           'data/E008-v1-witnesses.json', REPORT)
DOMAINS = ((2, 2, 4), (2, 3, 3), (3, 2, 2), (3, 3, 2))


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def load_baseline():
    if sha256((ROOT / BASELINE).read_bytes()).hexdigest() != BASELINE_SHA:
        raise ValueError('Pinned E007 baseline changed')
    spec = importlib.util.spec_from_file_location('e007_fixed_certificate', ROOT / BASELINE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fixed_radius(table, rules, alphabet, baseline):
    converted = tuple((sum(1 << g for g, columns in enumerate(rules)
                           if all(row[column] == 0 for column in columns)), row[3]) for row in table)
    return baseline.radius(converted, tuple(range(len(rules))), alphabet)[0]


def guard():
    if any((ROOT / path).exists() or (ROOT / path).is_symlink() for path in OUTPUTS):
        raise ValueError('Existing output; one locked execution only')
    lock = git('rev-parse', LOCK).decode().strip()
    if (ROOT / PROTOCOL).read_bytes() != git('show', f'{lock}:{PROTOCOL}'):
        raise ValueError('Protocol drift')
    git('merge-base', '--is-ancestor', lock, 'HEAD')
    implementation = git('rev-parse', 'HEAD').decode().strip()
    for path in Path(__file__).parent.glob('*.py'):
        name = path.relative_to(ROOT).as_posix()
        if path.read_bytes() != git('show', f'{implementation}:{name}'):
            raise ValueError(f'Uncommitted implementation: {name}')
    load_baseline()
    return lock, implementation


def row_dominance():
    count = 0
    failures = []
    for key_alphabet, rhs_alphabet, _maximum_n in DOMAINS:
        symbols = tuple(product(range(key_alphabet), range(key_alphabet), range(key_alphabet), range(rhs_alphabet)))
        for family, rules in candidate.FAMILIES:
            for original in symbols:
                actions = candidate.canonical_actions(original, rules, rhs_alphabet)
                for destination in symbols:
                    count += 1
                    budget = sum(a != b for a, b in zip(original, destination))
                    vector = candidate.contribution(destination, rules, rhs_alphabet)
                    if not any(cost <= budget and all(a >= b for a, b in zip(result, vector))
                               for cost, _row, result in actions):
                        failures.append({'keys': key_alphabet, 'rhs': rhs_alphabet, 'family': family,
                                         'original': original, 'destination': destination, 'cost': budget})
    return count, failures


def check_witness(table, witness, cost, rules, key_alphabet, rhs_alphabet):
    errors = []
    if witness is None or len(witness) != len(table) or witness[0] != table[0]:
        return ['witness_shape_or_target']
    if any(len(row) != 4 or any(not 0 <= row[column] < (key_alphabet if column < 3 else rhs_alphabet)
                                for column in range(4)) for row in witness):
        errors.append('witness_outside_raw_domain')
    distance = sum(a != b for old, new in zip(table, witness) for a, b in zip(old, new))
    if distance != cost:
        errors.append('witness_cost')
    if reference.accepts(table, rules) == reference.accepts(witness, rules):
        errors.append('witness_does_not_flip_raw_decision')
    return errors


def inspect_example(table, rules, key_alphabet, rhs_alphabet, baseline):
    full, witness, _states = candidate.radius(table, rules, rhs_alphabet)
    direct, direct_witness = reference.radius(table, rules, key_alphabet, rhs_alphabet)
    return {'table': table, 'rules': rules,
            'protected_key_radius': fixed_radius(table, rules, rhs_alphabet, baseline),
            'mutable_key_radius': full, 'reference_radius': direct,
            'witness': witness, 'reference_witness': direct_witness}


def build(lock, implementation):
    baseline = load_baseline()
    summaries, mismatches, nesting_failures = [], [], []
    first_strict = first_infinite = None
    totals = Counter(tables=0, comparisons=0, finite_witnesses=0, strict_reductions=0,
                     protected_INF_to_finite=0)
    for key_alphabet, rhs_alphabet, maximum_n in DOMAINS:
        symbols = tuple(product(range(key_alphabet), range(key_alphabet), range(key_alphabet), range(rhs_alphabet)))
        for n in range(1, maximum_n+1):
            aggregates = {name: Counter(tables=0, accepted=0, rejected=0, infinite=0,
                                        finite_witnesses=0, mismatches=0, strict_reductions=0,
                                        protected_INF_to_finite=0, maximum_DP_states=0)
                          for name, _rules in candidate.FAMILIES}
            for tail in product(symbols, repeat=n-1):
                table = ((0, 0, 0, 0),)+tail
                totals['tables'] += 1
                for family, rules in candidate.FAMILIES:
                    aggregate = aggregates[family]
                    aggregate['tables'] += 1
                    totals['comparisons'] += 1
                    initial = candidate.accepts(table, rules, rhs_alphabet)
                    aggregate['accepted' if initial else 'rejected'] += 1
                    cost, witness, states = candidate.radius(table, rules, rhs_alphabet)
                    aggregate['maximum_DP_states'] = max(aggregate['maximum_DP_states'], states)
                    truth, _direct_witness = reference.radius(table, rules, key_alphabet, rhs_alphabet)
                    errors = []
                    if initial != reference.accepts(table, rules):
                        errors.append('initial_decision_mismatch')
                    if cost != truth:
                        errors.append('minimum_radius_mismatch')
                    if cost is None:
                        aggregate['infinite'] += 1
                    else:
                        errors.extend(check_witness(table, witness, cost, rules, key_alphabet, rhs_alphabet))
                        aggregate['finite_witnesses'] += 1
                        totals['finite_witnesses'] += 1
                    if errors:
                        aggregate['mismatches'] += 1
                        mismatches.append({'keys': key_alphabet, 'rhs': rhs_alphabet, 'table': table,
                                           'family': family, 'candidate': cost, 'reference': truth,
                                           'errors': errors, 'witness': witness})
                    protected = fixed_radius(table, rules, rhs_alphabet, baseline)
                    if protected is not None and (cost is None or cost > protected):
                        nesting_failures.append({'table': table, 'family': family,
                                                  'protected': protected, 'mutable': cost})
                    if cost is not None and protected is None:
                        aggregate['protected_INF_to_finite'] += 1
                        totals['protected_INF_to_finite'] += 1
                        if first_infinite is None:
                            first_infinite = inspect_example(table, rules, key_alphabet, rhs_alphabet, baseline)
                    elif cost is not None and protected is not None and cost < protected:
                        aggregate['strict_reductions'] += 1
                        totals['strict_reductions'] += 1
                        if first_strict is None:
                            first_strict = inspect_example(table, rules, key_alphabet, rhs_alphabet, baseline)
            for family, _rules in candidate.FAMILIES:
                summaries.append({'key_alphabet': key_alphabet, 'rhs_alphabet': rhs_alphabet,
                                  'rows': n, 'family': family, **dict(aggregates[family])})
    dominance_count, dominance_failures = row_dominance()
    rules = ((0, 1), (0, 2))
    shared = inspect_example(((0, 0, 0, 0), (0, 0, 1, 1), (0, 1, 0, 1), (1, 0, 0, 0)), rules, 2, 2, baseline)
    singleton = inspect_example(((0, 0, 0, 0), (1, 0, 0, 1)), rules, 2, 2, baseline)
    h8a = not mismatches and totals['tables'] == 5107 and totals['comparisons'] == 30642
    h8b = not nesting_failures and totals['strict_reductions']+totals['protected_INF_to_finite'] > 0
    h8c = not dominance_failures and dominance_count == 61854
    h8d = (shared['protected_key_radius'], shared['mutable_key_radius'], shared['reference_radius']) == (2, 1, 1)
    h8d = h8d and (singleton['protected_key_radius'], singleton['mutable_key_radius'], singleton['reference_radius']) == (None, 1, 1)
    status = 'valid' if all((h8a, h8b, h8c, h8d)) else 'failed_mathematical_check'
    checks = {'status': status, 'classification': 'finite_constructed_mathematical_validation',
              'run_id': RUN, 'protocol_commit': lock, 'implementation_commit': implementation,
              'protocol_sha256': sha256((ROOT / PROTOCOL).read_bytes()).hexdigest(),
              'E007_baseline_sha256': BASELINE_SHA, **dict(totals),
              'row_dominance_comparisons': dominance_count, 'row_dominance_failures': dominance_failures,
              'radius_and_witness_mismatches': mismatches, 'edit_space_nesting_failures': nesting_failures,
              'H8a_exact_radii_and_witnesses': h8a, 'H8b_key_edit_reductions': h8b,
              'H8c_canonical_action_dominance': h8c, 'H8d_shared_key_examples': h8d,
              'novelty_established': False, 'performance_result': False, 'independent_review': False}
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(summaries[0]))
    writer.writeheader()
    writer.writerows(summaries)
    outputs = {OUTPUTS[0]: canonical(checks), OUTPUTS[1]: stream.getvalue().encode(),
               OUTPUTS[2]: canonical({'first_strict_finite_reduction': first_strict,
                                      'first_protected_INF_to_finite': first_infinite,
                                      'shared_key_synergy': shared, 'singleton_key_import': singleton})}
    lines = [f'# E008-v1 — {RUN}', '', f'status: {status}',
             'classification: finite_constructed_mathematical_validation',
             f'protocol_commit: {lock}', f'implementation_commit: {implementation}', '',
             f"Tables: {totals['tables']}; radius comparisons: {totals['comparisons']}; finite witnesses: {totals['finite_witnesses']}.",
             f'Row-action dominance checks: {dominance_count}; failures: {len(dominance_failures)}.',
             f'H8a: {h8a}; H8b: {h8b}; H8c: {h8c}; H8d: {h8d}.',
             f"Strict finite-radius reductions: {totals['strict_reductions']}; protected-INF to finite: {totals['protected_INF_to_finite']}.", '',
             'The raw-coordinate oracle permits all locked key/RHS replacements and protects the entire target row.',
             'Counterfactual cost is changed cells, not changed rows or abstract group assignments.',
             'This is finite mathematical verification, not real-data usefulness or algorithmic novelty evidence.',
             'Generic counterfactual explanations and optimization have direct prior work; further comparison is required.', '',
             '## Artifacts', '']
    for path, content in outputs.items():
        lines.append(f'- `{path}` SHA-256 `{sha256(content).hexdigest()}`')
    outputs[REPORT] = ('\n'.join(lines)+'\n').encode()
    return outputs


if __name__ == '__main__':
    lock, implementation = guard()
    first = build(lock, implementation)
    second = build(lock, implementation)
    if first != second:
        raise ValueError('Two complete builds differ')
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
                      'double_build_byte_identical': True, 'run_id': RUN}))
