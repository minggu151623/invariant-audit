"""Single locked reused-source stability study, with staged reference access."""
from collections import Counter
import csv
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import platform
import subprocess

import numpy as np
import scipy

import sources
import stability

ROOT = Path(__file__).resolve().parents[3]
LOCK = '86dad7d'
PROTOCOL = 'experiments/E011-reused-source-stability/protocol.md'
RUN = 'e011-20261023-001'
REPORT = f'experiments/E011-reused-source-stability/results/run-{RUN}.md'
OUTPUTS = ('data/E011-v1-preflight.json.gz', 'data/E011-v1-targets.jsonl.gz',
           'data/E011-v1-rejected-solves.jsonl.gz', 'data/E011-v1-summary.csv',
           'data/E011-v1-reference-buckets.csv', 'data/E011-v1-checks.json', REPORT)
PINS = {'experiments/E010-directional-scaling/code/models.py': 'c99a7b0bb17929891aa71eb48d8fa59300f7d87b7286707063217f143e8a58f6',
        'experiments/E010-directional-scaling/code/design.py': 'f895ed89623919b1e4a952f236133de4d13207e77057cca045da74fff8d87b9b',
        'experiments/E009-singleton-characterization/code/generic_milp.py': '2be4637ab7b58efea07495fedba3da1ed678c719df0008bce0ac54e4699bfebb'}


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def guard():
    if any((ROOT / p).exists() or (ROOT / p).is_symlink() for p in OUTPUTS):
        raise ValueError('Output identity already exists')
    environment = dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__)
    if environment != dict(python='3.13.5', numpy='2.1.3', scipy='1.17.1'):
        raise ValueError('Locked runtime drift')
    lock = git('rev-parse', LOCK).decode().strip()
    implementation = git('rev-parse', 'HEAD').decode().strip()
    git('merge-base', '--is-ancestor', lock, implementation)
    if (ROOT / PROTOCOL).read_bytes() != git('show', f'{lock}:{PROTOCOL}'):
        raise ValueError('Protocol drift')
    for p in Path(__file__).parent.glob('*.py'):
        if p.read_bytes() != git('show', f'{implementation}:{p.relative_to(ROOT)}'):
            raise ValueError(f'Uncommitted implementation: {p}')
    for path, digest in PINS.items():
        if sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise ValueError(f'Imported module drift: {path}')
    return lock, implementation, environment


def accepted_stage(tasks, stage):
    records, errors = [], []
    for task in tasks:
        for target in range(len(task['encoded'])):
            table, order = sources.target_table(task, target)
            accepted = stability.accepts(table, task['rules'])
            group_sizes = [sum(all(row[j] == 0 for j in columns) for row in table) for columns in task['rules']]
            record = dict(dataset=task['dataset'], rhs=task['rhs'], row_index=target+1,
                          initial_accepted=accepted, group_sizes=group_sizes, has_singleton=1 in group_sizes)
            if accepted:
                full = stability.e010_models.accepted_formula(table, task['rules'], task['sizes'][-1])
                fixed = stability.accepted_fixed(table, task['rules'])
                for name, result in (('full', full), ('fixed', fixed)):
                    result['verification_errors'] = stability.check_witness(table, task['rules'], task['sizes'], result, name == 'fixed')
                    if result['verification_errors'] or result['status'] not in (0, 2):
                        errors.append(dict(dataset=task['dataset'], rhs=task['rhs'], row_index=target+1,
                                           method=name, errors=result['verification_errors'], status=result['status']))
                    record[name] = sources.coordinate_result(task, table, order, result)
                if not record['has_singleton'] and full['cost'] != fixed['cost']:
                    errors.append(dict(dataset=task['dataset'], rhs=task['rhs'], row_index=target+1, error='no_singleton_reduction'))
                if full['cost'] is None or fixed['cost'] is not None and full['cost'] > fixed['cost']:
                    errors.append(dict(dataset=task['dataset'], rhs=task['rhs'], row_index=target+1, error='edit_space_nesting'))
            records.append(record)
        print(encode(dict(stage=stage, dataset=task['dataset'], rhs=task['rhs'], targets=len(task['encoded']))).decode(), flush=True)
    return records, errors


def rejected_stage(tasks, targets):
    solves, errors, selection = [], [], []
    for task in tasks:
        rejected = [r for r in targets if r['dataset'] == task['dataset'] and r['rhs'] == task['rhs'] and not r['initial_accepted']]
        def digest(record):
            message = f'E011-v1|rejected|{task["dataset"]}|{task["rhs"]}|{record["row_index"]}'
            return sha256(message.encode()).hexdigest()
        selected = sorted(rejected, key=lambda r: (digest(r), r['row_index']))[:4]
        selection.append(dict(dataset=task['dataset'], rhs=task['rhs'], total_rejected=len(rejected),
                              selected=[dict(row_index=r['row_index'], sha256=digest(r)) for r in selected]))
        for record in selected:
            table, order = sources.target_table(task, record['row_index']-1)
            pair = dict(dataset=task['dataset'], rhs=task['rhs'], row_index=record['row_index'], selection_sha256=digest(record))
            for name, fixed_keys in (('full', False), ('fixed', True)):
                result = stability.solve_accepting(table, task['rules'], fixed_keys)
                result['verification_errors'] = stability.check_witness(table, task['rules'], task['sizes'], result, fixed_keys)
                if result['verification_errors'] or result['status'] not in (0, 1):
                    errors.append(dict(dataset=task['dataset'], rhs=task['rhs'], row_index=record['row_index'],
                                       method=name, status=result['status'], errors=result['verification_errors']))
                pair[name] = sources.coordinate_result(task, table, order, result)
            if pair['full']['status'] == pair['fixed']['status'] == 0 and pair['full']['cost'] > pair['fixed']['cost']:
                errors.append(dict(dataset=task['dataset'], rhs=task['rhs'], row_index=record['row_index'], error='rejected_edit_space_nesting'))
            solves.append(pair)
            print(encode(dict(stage='rejected_solves', dataset=task['dataset'], rhs=task['rhs'], row_index=record['row_index'],
                              full_status=pair['full']['status'], fixed_status=pair['fixed']['status'])).decode(), flush=True)
    return solves, errors, selection


def strict(record):
    return record['full']['cost'] is not None and (record['fixed']['cost'] is None or record['full']['cost'] < record['fixed']['cost'])


def summaries(tasks, targets, solves):
    rows, buckets = [], []
    for task in tasks:
        selected = [r for r in targets if r['dataset'] == task['dataset'] and r['rhs'] == task['rhs']]
        accepted = [r for r in selected if r['initial_accepted']]
        sampled = [r for r in solves if r['dataset'] == task['dataset'] and r['rhs'] == task['rhs']]
        paired = [r for r in sampled if r['full']['status'] == r['fixed']['status'] == 0]
        row = dict(dataset=task['dataset'], rhs=task['rhs'], rows=len(selected), accepted=len(accepted), rejected=len(selected)-len(accepted),
                   accepted_with_singleton=sum(r['has_singleton'] for r in accepted),
                   accepted_strict_finite_decreases=sum(strict(r) and r['fixed']['cost'] is not None for r in accepted),
                   accepted_fixed_INF_to_finite=sum(strict(r) and r['fixed']['cost'] is None for r in accepted),
                   accepted_without_reduction=sum(not strict(r) for r in accepted),
                   accepted_reference_incorrect=sum(not r['reference_correct'] for r in accepted),
                   selected_rejected=len(sampled), selected_rejected_exact_pairs=len(paired),
                   selected_rejected_strict_decreases=sum(strict(r) for r in paired),
                   full_timeouts=sum(r['full']['status'] == 1 for r in sampled), fixed_timeouts=sum(r['fixed']['status'] == 1 for r in sampled))
        rows.append(row)
        for bucket in ('1', '2', '>=3', 'INF'):
            def belongs(record):
                value = record['full']['cost']
                return value is None if bucket == 'INF' else value is not None and (value >= 3 if bucket == '>=3' else value == int(bucket))
            group = [r for r in accepted if belongs(r)]
            buckets.append(dict(dataset=task['dataset'], rhs=task['rhs'], bucket=bucket,
                                accepted=len(group), reference_correct=sum(r['reference_correct'] for r in group),
                                reference_incorrect=sum(not r['reference_correct'] for r in group)))
    return rows, buckets


def csv_encode(rows):
    stream = io.StringIO(newline='')
    if rows:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)
    return stream.getvalue().encode()


def publish(contents):
    written = []
    try:
        for relative, payload in contents.items():
            path = ROOT / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            with path.open('xb') as handle:
                handle.write(payload)
            written.append(path)
    except Exception:
        for path in written:
            path.unlink()
        raise


def run():
    lock, implementation, environment = guard()
    manifest, payload = sources.payloads()
    preflight, preflight_errors = stability.preflight()
    print(encode(dict(stage='preflight', cases=len(preflight), errors=preflight_errors)).decode(), flush=True)
    targets, solves, errors, selection, tasks = [], [], [], [], []
    dirty_stage_hash = None
    accepted_hashes = []
    if not preflight_errors:
        dirty, tasks = sources.dirty_tasks(manifest, {k: v for k, v in payload.items() if k.endswith('/dirty.csv')})
        targets, first_errors = accepted_stage(tasks, 'accepted_first')
        second, second_errors = accepted_stage(tasks, 'accepted_second')
        accepted_hashes = [sha256(encode(v)).hexdigest() for v in (targets, second)]
        errors.extend(first_errors+second_errors)
        if accepted_hashes[0] != accepted_hashes[1]:
            errors.append(dict(error='accepted_double_build_differs'))
        if not errors:
            solves, solve_errors, selection = rejected_stage(tasks, targets)
            errors.extend(solve_errors)
        dirty_stage_hash = sha256(encode(dict(targets=targets, solves=solves))).hexdigest()
        clean = sources.references(manifest, payload, dirty)
        for record in targets:
            d, row = record['dataset'], record['row_index']-1
            j = manifest['canonical_headers'][d].index(record['rhs'])
            record['reference_correct'] = dirty[d][row][j] == clean[d][row][j]
    summary, buckets = summaries(tasks, targets, solves)
    accepted = [r for r in targets if r['initial_accepted']]
    exact_pairs = [r for r in solves if r['full']['status'] == r['fixed']['status'] == 0]
    rayyan_pairs = [r for r in exact_pairs if r['dataset'] == 'rayyan' and r['rhs'] == 'journal_title']
    checks = dict(run_id=RUN, protocol_commit=lock, implementation_commit=implementation,
                  protocol_sha256=sha256((ROOT / PROTOCOL).read_bytes()).hexdigest(),
                  manifest_sha256=sources.MANIFEST_SHA, imported_source_pins=PINS, environment=environment,
                  classification='exploratory_reused_source_stability_study',
                  status='failed_preflight' if preflight_errors else 'failed_validation' if errors else 'valid_exploratory_reused_source_study',
                  preflight_cases=len(preflight), preflight_errors=preflight_errors, validation_errors=errors,
                  targets=len(targets), accepted=len(accepted), rejected=len(targets)-len(accepted),
                  accepted_strict_reductions=sum(strict(r) for r in accepted),
                  accepted_double_build_hashes=accepted_hashes, dirty_stage_sha256_before_reference=dirty_stage_hash,
                  reference_parsed_after_dirty_freeze=dirty_stage_hash is not None,
                  tasks=[{k: t[k] for k in ('dataset', 'rhs', 'columns', 'key_columns', 'rules', 'sizes')} for t in tasks],
                  selection=selection, selected_rejected=len(solves), selected_rejected_exact_pairs=len(exact_pairs),
                  selected_rejected_strict_reductions=sum(strict(r) for r in exact_pairs),
                  rejected_statuses={name: dict(Counter(str(r[name]['status']) for r in solves)) for name in ('full', 'fixed')},
                  H11a=any(strict(r) for r in accepted), H11b=any(strict(r) for r in rayyan_pairs),
                  H11b_exact_pair_denominator=len(rayyan_pairs), H11c=not preflight_errors and not errors,
                  H11d=any(not r['reference_correct'] and r['full']['cost'] is not None and r['full']['cost'] >= 2 for r in accepted),
                  novelty_established=False, independent_review=False, detector_accuracy_improvement=False)
    contents = {OUTPUTS[0]: gzip.compress(encode(preflight), mtime=0),
                OUTPUTS[1]: gzip.compress(b''.join(encode(r) for r in targets), mtime=0),
                OUTPUTS[2]: gzip.compress(b''.join(encode(r) for r in solves), mtime=0),
                OUTPUTS[3]: csv_encode(summary), OUTPUTS[4]: csv_encode(buckets), OUTPUTS[5]: encode(checks)}
    report = f'# E011-v1 — {RUN}\n\nStatus: {checks["status"]}.\n\nProtocol {lock}; implementation {implementation}.\n\n'
    report += f'{len(targets)} complete-universe target decisions; {len(accepted)} accepted. Accepted key-radius reductions: {checks["accepted_strict_reductions"]}. Selected rejected targets: {len(solves)}; exact full/fixed pairs: {len(exact_pairs)}; strict reductions: {checks["selected_rejected_strict_reductions"]}.\n\n'
    report += f'H11a: {checks["H11a"]}; H11b: {checks["H11b"]} (Rayyan title exact pairs: {len(rayyan_pairs)}); H11c: {checks["H11c"]}; H11d: {checks["H11d"]}.\n\n'
    report += 'The source tables were previously inspected. No pristine holdout, representative rejected sample, factual correctness certificate or accuracy improvement is claimed. Empty strings are ordinary categories; this detector differs from E006. All target rows use the full dirty-table context. Reference labels are attached only after the dirty-stage hash is frozen. Failed empirical predictions and timeouts remain in the outputs.\n\n## Artifacts\n\n'
    for path, b in contents.items():
        report += f'- `{path}` SHA-256 `{sha256(b).hexdigest()}`\n'
    contents[REPORT] = report.encode()
    publish(contents)
    print(encode(checks).decode(), flush=True)


if __name__ == '__main__':
    run()
