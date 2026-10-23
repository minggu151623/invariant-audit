"""Execute the locked exhaustive mathematical pilot, preserving all mismatches."""
from collections import Counter
import csv
from hashlib import sha256
import io
from itertools import product
import json
from pathlib import Path
import subprocess

import certificate as c
import exhaustive_reference as reference

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL = 'experiments/E007-fd-decision-stability/protocol.md'
LOCK = '2599ec2'
RUN = 'e007-20261023-001'
REPORT = f'experiments/E007-fd-decision-stability/results/run-{RUN}.md'
OUTPUTS = ('data/E007-v1-checks.json', 'data/E007-v1-domain-summary.csv',
           'data/E007-v1-witnesses.json', REPORT)


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def guard():
    if any((ROOT / name).exists() or (ROOT / name).is_symlink() for name in OUTPUTS):
        raise ValueError('Output exists; one locked run only')
    lock = git('rev-parse', LOCK).decode().strip()
    if (ROOT / PROTOCOL).read_bytes() != git('show', f'{lock}:{PROTOCOL}'):
        raise ValueError('Protocol drift')
    git('merge-base', '--is-ancestor', lock, 'HEAD')
    commit = git('rev-parse', 'HEAD').decode().strip()
    for path in Path(__file__).parent.glob('*.py'):
        relative = path.relative_to(ROOT).as_posix()
        if path.read_bytes() != git('show', f'{commit}:{relative}'):
            raise ValueError(f'Uncommitted implementation: {relative}')
    return lock, commit


def example(table, alphabet, joint, locals_):
    return {'table_mask_value': table, 'alphabet': alphabet, 'joint_minimum': joint,
            'single_rule_repair_minima': locals_, 'gap_over_max_local': joint-max(locals_)}


def build(lock, commit):
    summaries, mismatches = [], []
    first_gap = max_gap = None
    total_tables = total_comparisons = total_witnesses = 0
    bound_failures = []
    for alphabet, maximum_n in ((2, 6), (3, 4)):
        symbols = tuple(product(range(4), range(alphabet)))
        for n in range(1, maximum_n+1):
            aggregates = {rules: Counter(tables=0, accepted=0, rejected=0, infinite=0,
                                        finite_witnesses=0, mismatches=0, strict_joint_gap=0)
                          for rules in reference.RULE_SETS}
            for tail in product(symbols, repeat=n-1):
                table = ((3, 0),) + tail
                total_tables += 1
                oracle = reference.all_radii(table, alphabet)
                for rules in reference.RULE_SETS:
                    aggregate = aggregates[rules]
                    aggregate['tables'] += 1
                    total_comparisons += 1
                    initial = c.accepts(table, rules)
                    aggregate['accepted' if initial else 'rejected'] += 1
                    cost, edits = c.radius(table, rules, alphabet)
                    errors = []
                    if initial != reference.decisions(table, [value for _mask, value in table])[reference.RULE_SETS.index(rules)]:
                        errors.append('initial_decision_mismatch')
                    if cost != oracle[rules][0]:
                        errors.append('radius_mismatch')
                    if cost is None:
                        aggregate['infinite'] += 1
                    else:
                        total_witnesses += 1
                        aggregate['finite_witnesses'] += 1
                        values = [value for _mask, value in table]
                        for index, value in edits:
                            if index == 0:
                                errors.append('target_was_edited')
                            values[index] = value
                        distance = sum(value != row[1] for value, row in zip(values, table))
                        if distance != cost or len(set(index for index, _value in edits)) != cost:
                            errors.append('witness_cost')
                        original_values = [value for _mask, value in table]
                        rule_index = reference.RULE_SETS.index(rules)
                        if reference.decisions(table, values)[rule_index] == reference.decisions(table, original_values)[rule_index]:
                            errors.append('witness_does_not_flip_direct_decision')
                    if errors:
                        aggregate['mismatches'] += 1
                        mismatches.append({'table': table, 'alphabet': alphabet, 'rules': rules,
                                           'proposed': cost, 'reference': oracle[rules][0], 'errors': errors})
                    if rules == (0, 1) and not initial:
                        locals_ = [c.repair_to_accept(table, (g,), alphabet)[0] for g in (0, 1)]
                        if not max(locals_) <= cost <= sum(locals_):
                            bound_failures.append(example(table, alphabet, cost, locals_))
                        if cost > max(locals_):
                            aggregate['strict_joint_gap'] += 1
                            item = example(table, alphabet, cost, locals_)
                            if first_gap is None:
                                first_gap = item
                            if max_gap is None or item['gap_over_max_local'] > max_gap['gap_over_max_local']:
                                max_gap = item
            for rules in reference.RULE_SETS:
                summaries.append({'alphabet': alphabet, 'rows': n,
                                  'rules': '+'.join(map(str, rules)), **dict(aggregates[rules])})
    scope_table = ((3, 0), (0, 1))
    scope_changed = ((3, 0), (1, 1))
    scope = {'original': scope_table, 'determinant_edited': scope_changed,
             'RHS_only_radius': c.radius(scope_table, (0, 1), 2)[0],
             'determinant_edit_cost': 1,
             'decision_before': c.accepts(scope_table, (0, 1)),
             'decision_after': c.accepts(scope_changed, (0, 1))}
    inventory_ok = total_tables == 39334 and total_comparisons == 118002
    h7a = not mismatches and inventory_ok
    h7b = first_gap is not None
    h7c = scope['RHS_only_radius'] is None and scope['decision_before'] and not scope['decision_after']
    status = 'valid' if h7a and h7b and h7c and not bound_failures else 'failed_mathematical_check'
    checks = {'status': status, 'classification': 'finite_constructed_mathematical_validation',
              'run_id': RUN, 'protocol_commit': lock, 'implementation_commit': commit,
              'protocol_sha256': sha256((ROOT / PROTOCOL).read_bytes()).hexdigest(),
              'tables': total_tables, 'radius_comparisons': total_comparisons,
              'finite_witnesses_verified': total_witnesses, 'mismatches': mismatches,
              'compositional_bound_failures': bound_failures,
              'H7a_all_radii_and_witnesses': h7a, 'H7b_strict_joint_gap_exists': h7b,
              'H7c_determinant_edit_scope_counterexample': h7c,
              'novelty_established': False, 'performance_result': False,
              'independent_scientific_review': False}
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(summaries[0]))
    writer.writeheader()
    writer.writerows(summaries)
    outputs = {OUTPUTS[0]: canonical(checks), OUTPUTS[1]: stream.getvalue().encode(),
               OUTPUTS[2]: canonical({'first_strict_gap': first_gap, 'maximum_gap': max_gap,
                                      'scope_counterexample': scope})}
    lines = [f'# E007-v1 — {RUN}', '', f'status: {status}',
             'classification: finite_constructed_mathematical_validation',
             f'protocol_commit: {lock}', f'implementation_commit: {commit}', '',
             f'Tables: {total_tables}; radius comparisons: {total_comparisons}; verified finite witnesses: {total_witnesses}.',
             f'H7a: {h7a}; H7b: {h7b}; H7c: {h7c}.',
             f'Mismatches: {len(mismatches)}; compositional bound failures: {len(bound_failures)}.', '',
             'This is a complete enumeration of the locked finite domain, not a performance benchmark.',
             'The proposed formulation uses RHS-only edits with protected determinants and target row.',
             'Stability does not establish correctness. The scope control demonstrates this threat-model boundary.',
             'Mathematical agreement is not novelty; related voting/repair certification must still be compared.',
             'No external source data, E003 execution, independent scientific acceptance or publication is claimed.', '',
             '## Artifacts', '']
    for path, content in outputs.items():
        lines.append(f'- `{path}` SHA-256 `{sha256(content).hexdigest()}`')
    outputs[REPORT] = ('\n'.join(lines)+'\n').encode()
    return outputs


if __name__ == '__main__':
    lock, commit = guard()
    first = build(lock, commit)
    second = build(lock, commit)
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
