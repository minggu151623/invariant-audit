"""Post-run verification using original categorical codes and incremental counts."""
from collections import Counter, defaultdict
import csv
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).parent / 'code'))
import sources


def require(value, message):
    if not value:
        raise ValueError(message)


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def group_key(row, columns):
    return tuple(row[j] for j in columns)


def prepare(task):
    groups = []
    for columns in task['rules']:
        group = defaultdict(list)
        for i, row in enumerate(task['encoded']):
            group[group_key(row, columns)].append(i)
        groups.append(dict(group))
    return groups


def direct_radii(task, groups, i):
    table, rules = task['encoded'], task['rules']
    target = table[i]
    sizes, full, fixed = [], [], []
    accepted = True
    for columns, group in zip(rules, groups):
        indices = group[group_key(target, columns)]
        sizes.append(len(indices))
        counts = Counter(table[j][-1] for j in indices)
        rival = max((count for value, count in counts.items() if value != target[-1]), default=0)
        if counts[target[-1]] <= rival:
            accepted = False
        if len(indices) > 1:
            cost = (counts[target[-1]]-rival+1)//2
            full.append(cost); fixed.append(cost)
        else:
            full.append(min(sum(row[j] != target[j] for j in columns)+(row[-1] == target[-1])
                            for r, row in enumerate(table) if r != i))
    return accepted, sizes, min(full) if accepted else None, min(fixed) if accepted and fixed else None


def verify_coordinate_witness(task, groups, target_index, result, fixed=False):
    require(not result['verification_errors'], 'Recorded verification error')
    edits = result['edits']
    if edits is None:
        require(result['status'] != 0, 'Missing optimal edits')
        return 0
    table, target = task['encoded'], task['encoded'][target_index]
    changed, seen = {}, set()
    columns = {original+1: j for j, original in enumerate(task['columns'])}
    for row_number, original_column, relative_value in edits:
        require(isinstance(relative_value, int), 'Noninteger destination')
        require(1 <= row_number <= len(table) and row_number != target_index+1, 'Row/target coordinate')
        require(original_column in columns, 'Irrelevant column')
        j, i = columns[original_column], row_number-1
        require(0 <= relative_value < task['sizes'][j], 'Domain violation')
        require((i, j) not in seen, 'Duplicate cell edit'); seen.add((i, j))
        if fixed:
            require(j == len(target)-1, 'Fixed determinant changed')
        value = target[j] if relative_value == 0 else 0 if relative_value == target[j] else relative_value
        changed.setdefault(i, list(table[i]))[j] = value
        require(value != table[i][j], 'Edit does not change value')
    cost = sum(a != b for i, row in changed.items() for a, b in zip(table[i], row))
    require(cost == result['cost'] == len(edits), 'Cost mismatch')
    final_accepts = True
    for determinant, group in zip(task['rules'], groups):
        key = group_key(target, determinant)
        counts = Counter(table[i][-1] for i in group[key])
        for i, row in changed.items():
            if group_key(table[i], determinant) == key:
                counts[table[i][-1]] -= 1
            if group_key(row, determinant) == key:
                counts[row[-1]] += 1
        if any(n >= counts[target[-1]] for value, n in counts.items() if value != target[-1]):
            final_accepts = False
    initial, _, _, _ = direct_radii(task, groups, target_index)
    require(initial != final_accepts, 'Witness does not flip raw decision')
    if 'objective' in result:
        require(abs(result['objective']-cost) <= 1e-7, 'Objective mismatch')
        require(result['maximum_integrality_error'] <= 1e-7 and result['maximum_constraint_residual'] <= 1e-7, 'Solver residual')
        if result['status'] == 0:
            require(result['gap'] <= 1e-7 and abs(result['dual_bound']-cost) <= 1e-7, 'Optimal bound mismatch')
    return 1


def main():
    checks = json.loads((ROOT / 'data/E011-v1-checks.json').read_text())
    require(checks['status'] == 'valid_exploratory_reused_source_study', 'Study not valid')
    report = (ROOT / 'experiments/E011-reused-source-stability/results/run-e011-20261023-001.md').read_text()
    pins = dict(re.findall(r'- `([^`]+)` SHA-256 `([a-f0-9]{64})`', report))
    require(len(pins) == 6, 'Incomplete artifact pins')
    for path, digest in pins.items():
        require(sha256((ROOT / path).read_bytes()).hexdigest() == digest, f'Hash drift: {path}')
    manifest, payload = sources.payloads()
    dirty, tasks = sources.dirty_tasks(manifest, {k: v for k, v in payload.items() if k.endswith('/dirty.csv')})
    clean = sources.references(manifest, payload, dirty)
    lookup = {(t['dataset'], t['rhs']): (t, prepare(t)) for t in tasks}
    targets = [json.loads(line) for line in gzip.decompress((ROOT / 'data/E011-v1-targets.jsonl.gz').read_bytes()).splitlines()]
    solves = [json.loads(line) for line in gzip.decompress((ROOT / 'data/E011-v1-rejected-solves.jsonl.gz').read_bytes()).splitlines()]
    dirty_targets = [{k: v for k, v in r.items() if k != 'reference_correct'} for r in targets]
    require(sha256(encode(dirty_targets)).hexdigest() == checks['accepted_double_build_hashes'][0] == checks['accepted_double_build_hashes'][1], 'Accepted stage freeze mismatch')
    require(sha256(encode(dict(targets=dirty_targets, solves=solves))).hexdigest() == checks['dirty_stage_sha256_before_reference'], 'Dirty/reference boundary hash')
    require(len(targets) == sum(len(t['encoded']) for t in tasks) == checks['targets'], 'Universe incomplete')
    seen, witnesses, distribution = set(), 0, Counter()
    for record in targets:
        key = (record['dataset'], record['rhs'], record['row_index'])
        require(key not in seen, 'Duplicate target'); seen.add(key)
        task, groups = lookup[key[:2]]
        i = record['row_index']-1
        accepted, sizes, full, fixed = direct_radii(task, groups, i)
        require(accepted == record['initial_accepted'] and sizes == record['group_sizes'] and record['has_singleton'] == (1 in sizes), 'Decision/group metadata')
        j = manifest['canonical_headers'][key[0]].index(key[1])
        require(record['reference_correct'] == (dirty[key[0]][i][j] == clean[key[0]][i][j]), 'Reference label mismatch')
        if accepted:
            require(record['full']['cost'] == full and record['fixed']['cost'] == fixed, 'Independent direct radius mismatch')
            for method in ('full', 'fixed'):
                witnesses += verify_coordinate_witness(task, groups, i, record[method], method == 'fixed')
                cost = record[method]['cost']
                distribution[key[0], key[1], method, 'INF' if cost is None else str(cost)] += 1
        else:
            require('full' not in record and 'fixed' not in record, 'Unsampled rejected radius mislabeled')
    require(sum(r['initial_accepted'] for r in targets) == checks['accepted'], 'Accepted aggregate')
    for selection in checks['selection']:
        d, rhs = selection['dataset'], selection['rhs']
        rejected = [r for r in targets if r['dataset'] == d and r['rhs'] == rhs and not r['initial_accepted']]
        hashes = sorted((sha256(f'E011-v1|rejected|{d}|{rhs}|{r["row_index"]}'.encode()).hexdigest(), r['row_index']) for r in rejected)[:4]
        require(selection['total_rejected'] == len(rejected), 'Rejected denominator')
        require([(r['sha256'], r['row_index']) for r in selection['selected']] == hashes, 'Selection differs')
        require({r['row_index'] for r in solves if r['dataset'] == d and r['rhs'] == rhs} == {i for h, i in hashes}, 'Selected solve coverage')
    for pair in solves:
        task, groups = lookup[pair['dataset'], pair['rhs']]
        for method in ('full', 'fixed'):
            require(pair[method]['status'] in (0, 1), 'Unexpected solver status')
            witnesses += verify_coordinate_witness(task, groups, pair['row_index']-1, pair[method], method == 'fixed')
        if pair['full']['status'] == pair['fixed']['status'] == 0:
            require(pair['full']['cost'] <= pair['fixed']['cost'], 'Edit-space nesting')
    buckets = list(csv.DictReader((ROOT / 'data/E011-v1-reference-buckets.csv').open()))
    require(len(buckets) == 36, 'Bucket coverage')
    for row in buckets:
        def belongs(r):
            cost, b = r['full']['cost'], row['bucket']
            return cost is None if b == 'INF' else cost is not None and (cost >= 3 if b == '>=3' else cost == int(b))
        selected = [r for r in targets if r['dataset'] == row['dataset'] and r['rhs'] == row['rhs'] and r['initial_accepted'] and belongs(r)]
        require(int(row['accepted']) == len(selected) and int(row['reference_correct']) == sum(r['reference_correct'] for r in selected)
                and int(row['reference_incorrect']) == sum(not r['reference_correct'] for r in selected), 'Bucket arithmetic')
    previous = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', '36b5c05'], cwd=ROOT).decode().splitlines()
    preserve = [p for p in previous if p.startswith(('experiments/', 'data/', 'paper/', 'reproducibility/')) and p not in ('experiments/README.md', 'data/README.md')]
    for p in preserve:
        require((ROOT / p).read_bytes() == subprocess.check_output(['git', 'show', f'36b5c05:{p}'], cwd=ROOT), f'Earlier file changed: {p}')
    with zipfile.ZipFile(ROOT / 'paper/evidence-review-bundle.zip') as z:
        require(z.testzip() is None, 'Bundle CRC')
        for name in z.namelist():
            require(z.read(name) == (ROOT / name).read_bytes(), f'Bundle member changed: {name}')
    stream = io.StringIO(newline=''); writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(('dataset', 'rhs', 'method', 'radius', 'accepted_targets'))
    for key, count in sorted(distribution.items()):
        writer.writerow((*key, count))
    hist_path = ROOT / 'data/E011-v1-radius-distribution.csv'
    with hist_path.open('x') as f:
        f.write(stream.getvalue())
    audit = dict(date='2026-10-23', status='pass', scope='post_run_original_code_radius_witness_label_selection_and_preservation_self_review',
                 targets=len(targets), independently_checked_source_witnesses=witnesses, selected_rejected=len(solves),
                 source_files_pinned=9, previous_files_unchanged=len(preserve), M22_bundle_members_unchanged=True,
                 accepted_stage_hash_match=True, reference_stage_hash_match=True,
                 radius_distribution_sha256=sha256(hist_path.read_bytes()).hexdigest(), artifact_sha256=pins,
                 independent_review=False, novelty_established=False)
    with (ROOT / 'milestones/M29-delivery-verification.json').open('x') as f:
        json.dump(audit, f, indent=2, sort_keys=True); f.write('\n')
    print(json.dumps(audit))


if __name__ == '__main__':
    main()
