"""One locked E006 execution with source pins and deterministic staged artifacts."""
from __future__ import annotations

import csv
import gzip
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile

import numpy as np

import evaluate as e

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path('/Users/mac/Library/Caches/InvariantAudit/E006-v1-20261022/source')
PROTOCOL = 'experiments/E006-external-reference-validation/protocol.md'
PROTOCOL_LOCK = '0a0d6ac'
MANIFEST = 'data/E006-v1-source-manifest.json'
MANIFEST_SHA256 = '96e7529355eac100de47f2c957b8a1a5252d4c220c285d5fd46d871d62716342'
RUN_ID = 'e006-20261022-001'
REPORT = f'experiments/E006-external-reference-validation/results/run-{RUN_ID}.md'
OUTPUTS = ('data/E006-v1-predictions.csv.gz', 'data/E006-v1-metrics.csv',
           'data/E006-v1-bootstrap.csv.gz', 'data/E006-v1-intervals.csv', 'data/E006-v1-checks.json', REPORT)


def git(root, *arguments):
    return subprocess.check_output(['git', *arguments], cwd=root, stderr=subprocess.PIPE)


def guard(root):
    e.require(all(not (root / p).exists() and not (root / p).is_symlink() for p in OUTPUTS), 'outputs exist; no retry')
    lock = git(root, 'rev-parse', PROTOCOL_LOCK).decode().strip()
    protocol_bytes = git(root, 'show', f'{lock}:{PROTOCOL}')
    e.require(protocol_bytes == (root / PROTOCOL).read_bytes(), 'locked evaluation protocol drift')
    git(root, 'merge-base', '--is-ancestor', lock, 'HEAD')
    implementation = git(root, 'rev-parse', 'HEAD').decode().strip()
    for path in sorted((root / 'experiments/E006-external-reference-validation/code').glob('*.py')):
        relative = path.relative_to(root).as_posix()
        e.require(path.read_bytes() == git(root, 'show', f'HEAD:{relative}'), 'uncommitted implementation')
    return lock, sha256(protocol_bytes).hexdigest(), implementation


def source_bytes(root):
    manifest_bytes = (root / MANIFEST).read_bytes()
    e.require(sha256(manifest_bytes).hexdigest() == MANIFEST_SHA256, 'manifest pin mismatch')
    e.require((SOURCE.parent / 'source-manifest.json').read_bytes() == manifest_bytes, 'external manifest drift')
    manifest = json.loads(manifest_bytes)
    e.require(manifest['source_commit'] == '7be1334b8c7bbdac3f47ef514fb3e1e8c5fc181c', 'source revision mismatch')
    content = {}
    for item in manifest['files']:
        payload = (SOURCE / item['path']).read_bytes()
        e.require(len(payload) == item['bytes'] and sha256(payload).hexdigest() == item['sha256'], 'source hash/size mismatch')
        content[item['path']] = payload
    expected = {f'datasets/{d}/{k}.csv' for d in e.DATASETS for k in ('dirty', 'clean')} | {'README.md', 'LICENSE.md', 'raha/dataset.py'}
    e.require(set(content) == expected, 'source inventory mismatch')
    return manifest, content


def value(item):
    if item is None or isinstance(item, (float, np.floating)) and not np.isfinite(item):
        return 'NA'
    if isinstance(item, (float, np.floating)):
        return f'{item:.12f}'
    if isinstance(item, bool):
        return int(item)
    return item


def csv_bytes(rows, fields):
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(fields)
    for row in rows:
        writer.writerow([value(row[field]) for field in fields])
    return stream.getvalue().encode()


def prediction_rows(results):
    for result in results:
        for k, (i, j) in enumerate(result['cells']):
            for base, method in enumerate(e.BASES):
                yield {'dataset': result['dataset'], 'split': result['assignments'][k],
                       'component_id': result['components'][k], 'row_index': i+1, 'column_index': j+1,
                       'method': method, 'truth': int(result['labels'][k]), 'raw_score': int(result['raw'][k, base]),
                       'decision': bool(result['decisions'][k, 2*base]),
                       'p_lookup': float(result['probabilities'][2*base][k]),
                       'p_binary': int(result['decisions'][k, 2*base])}


def replicate_rows(results):
    for result in results:
        for replicate in range(e.BOOTSTRAP_REPLICATES):
            for pair, metric, deltas in result['blocks']:
                delta = float(deltas[replicate])
                yield {'dataset': result['dataset'], 'replicate': replicate, 'pair': pair,
                       'metric': metric, 'delta': delta, 'status': 'available' if np.isfinite(delta) else 'undefined'}


def hypotheses(results):
    outcomes = {}
    for result in results:
        primary = {row['method']: row for row in result['metrics'] if row['split'] == 'evaluation' and row['scope'] == 'all_cells'}
        intervals = {(row['pair'], row['metric']): row for row in result['intervals']}

        def upper_negative(pair, metric):
            row = intervals[pair, metric]
            return row['usable_replicates'] == e.BOOTSTRAP_REPLICATES and row['upper'] is not None and float(value(row['upper'])) < 0

        outcomes[result['dataset']] = {'H6a': primary['Rall']['fp']+primary['Rall']['fn'] > 0,
                                      'H6b': upper_negative('Rmode-lookup-minus-binary', 'brier'),
                                      'H6c': upper_negative('Rmode-Rall', 'fnr')}
    return {'per_dataset': outcomes,
            'combined': {hypothesis: 'supported_within_fixed_external_reference_design' if all(row[hypothesis] for row in outcomes.values())
                        else 'mixed/not supported' for hypothesis in ('H6a', 'H6b', 'H6c')}}


def build(root, lock, protocol_sha, implementation):
    manifest, payloads = source_bytes(root)
    results = []
    for dataset in e.DATASETS:
        headers = manifest['canonical_headers'][dataset]
        dirty = e.parse_table(payloads[f'datasets/{dataset}/dirty.csv'], manifest['original_headers'][dataset]['dirty'])

        def reference_reader(dataset=dataset):
            return e.parse_table(payloads[f'datasets/{dataset}/clean.csv'], manifest['original_headers'][dataset]['clean'])

        results.append(e.evaluate_dataset(dataset, headers, dirty, reference_reader))
    metrics = [row for result in results for row in result['metrics']]
    intervals = [row for result in results for row in result['intervals']]
    e.require(len(metrics) == 144 and len(intervals) == 84, 'aggregate row inventory')
    prediction_fields = ('dataset', 'split', 'component_id', 'row_index', 'column_index', 'method', 'truth',
                         'raw_score', 'decision', 'p_lookup', 'p_binary')
    predictions = csv_bytes(prediction_rows(results), prediction_fields)
    bootstrap = csv_bytes(replicate_rows(results), ('dataset', 'replicate', 'pair', 'metric', 'delta', 'status'))
    e.require(predictions.count(b'\n')-1 == sum(result['checks']['cell_count'] for result in results)*4, 'prediction rows')
    e.require(bootstrap.count(b'\n')-1 == 840000, 'bootstrap replicate rows')
    e.require(len(predictions) < 150_000_000 and len(bootstrap) < 150_000_000, 'uncompressed size limit')
    checks = {'protocol_id': 'E006-v1', 'run_id': RUN_ID, 'classification': 'predeclared_external_reference_validation',
              'protocol_commit': lock, 'protocol_sha256': protocol_sha, 'implementation_commit': implementation,
              'python': platform.python_version(), 'numpy': np.__version__, 'source_manifest_sha256': MANIFEST_SHA256,
              'source_commit': manifest['source_commit'], 'dataset_checks': {r['dataset']: r['checks'] for r in results},
              'hypotheses': hypotheses(results), 'independent_review': False, 'public_claim_eligibility': False,
              'labels': 'equality_to_normalized_external_reference_not_infallible_world_truth',
              'setting': 'dirty_only_transductive_FD_context_group_disjoint_splits',
              'prediction_rows': predictions.count(b'\n')-1, 'metric_rows': 144,
              'bootstrap_rows': 840000, 'interval_rows': 84}
    outputs = {OUTPUTS[0]: gzip.compress(predictions, mtime=0), OUTPUTS[1]: csv_bytes(metrics, tuple(metrics[0])),
               OUTPUTS[2]: gzip.compress(bootstrap, mtime=0), OUTPUTS[3]: csv_bytes(intervals, tuple(intervals[0])),
               OUTPUTS[4]: e.canonical(checks)}
    lines = [f'# E006-v1 external reference validation — {RUN_ID}', '', 'status: valid',
             'classification: predeclared_external_reference_validation', f'protocol_commit: {lock}',
             f'implementation_commit: {implementation}', f'source_manifest_sha256: {MANIFEST_SHA256}',
             'independent_review: absent', 'public_claim_eligibility: false', '', '## Evaluation/all-cell metrics', '',
             '| Dataset | Method | N | BA | FPR | FNR | Brier | ECE | REL | RES |',
             '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for row in metrics:
        if row['split'] == 'evaluation' and row['scope'] == 'all_cells':
            fields = [row[k] for k in ('dataset', 'method', 'support', 'balanced_accuracy', 'fpr', 'fnr', 'brier', 'ece', 'reliability', 'resolution')]
            lines.append('| ' + ' | '.join(str(value(item)) for item in fields) + ' |')
    lines += ['', '## Fixed outcomes', '', '```json', json.dumps(checks['hypotheses'], sort_keys=True, indent=2), '```',
              '', '## Design and numerical checks', '',
              'All source hashes, paired row keys/shapes, dirty-only component splits, raw-score freeze,',
              'calibration-only lookup freeze, rational point-metric cross-checks, Brier identities and',
              'artifact counts/size gates pass. Detailed signed uncertainty and any partial bootstrap',
              'blocks are preserved in the interval/check artifacts. Final publication requires the',
              'two full byte-identical builds enforced by the runner.', '',
              '## Limitations', '', 'These are simple fixed rule baselines, not Raha or the original E001/E002 M1.',
              'Dirty context is transductive within splits. External reference corrections are not',
              'infallible semantic truth. The grouping uses dirty determinants and may not isolate',
              'true-world entities under erroneous keys. No natural-error prevalence, deployment,',
              'causal-transfer, state-machine-transfer or new-algorithm claim follows. Published examples',
              'and source headers were seen before the lock; this is not wholly blind discovery.',
              'Intervals describe the fixed datasets and grouping, not a population sample. The same',
              'author wrote both point-metric implementations; no independent acceptance is implied.',
              'A1 remains invalid and A2 header metadata recovery remains disclosed. E003 gates unchanged.',
              '', '## Artifacts', '']
    lines.extend(f'- `{path}` SHA-256 `{sha256(content).hexdigest()}`' for path, content in outputs.items())
    lines += ['', 'deviations: none', 'stopping: one valid fixed-source run; no retry or post-hoc rule change', '']
    outputs[REPORT] = '\n'.join(lines).encode()
    for path, content in outputs.items():
        limit = 20_000_000 if path.endswith('.gz') else 100_000 if path == REPORT else 1_000_000
        e.require(len(content) < limit, 'artifact size limit')
    return outputs


def publish(root, outputs):
    owned = []
    try:
        with tempfile.TemporaryDirectory(prefix='.e006-stage-', dir=root) as name:
            for index, (relative, content) in enumerate(outputs.items()):
                path = root / relative
                e.require(not Path(relative).is_absolute() and '..' not in Path(relative).parts, 'unsafe output path')
                for parent in path.parents:
                    if parent == root:
                        break
                    e.require(not parent.is_symlink(), 'symlink output ancestor')
                e.require(path.parent.is_dir() and not path.exists() and not path.is_symlink(), 'existing/unsafe destination')
                staged = Path(name) / str(index)
                staged.write_bytes(content)
                e.require(staged.read_bytes() == content, 'staged byte mismatch')
                identity = (staged.stat().st_dev, staged.stat().st_ino)
                os.link(staged, path)
                owned.append((path, identity))
                e.require((path.stat().st_dev, path.stat().st_ino) == identity and path.read_bytes() == content,
                          'published byte/ownership mismatch')
    except BaseException:
        for path, identity in reversed(owned):
            e.require(not path.is_symlink(), 'replaced published destination')
            if path.exists():
                e.require((path.stat().st_dev, path.stat().st_ino) == identity, 'replaced published destination')
                path.unlink()
        raise


def execute(root=ROOT):
    lock, protocol_sha, implementation = guard(root)
    try:
        first = build(root, lock, protocol_sha, implementation)
        second = build(root, lock, protocol_sha, implementation)
        e.require(first == second, 'two-build artifact bytes differ')
        publish(root, first)
    except BaseException:
        e.require(all(not (root / path).exists() for path in OUTPUTS), 'unresolved partial/external output')
        with (root / REPORT).open('x') as stream:
            stream.write(f'# E006-v1 invalid run — {RUN_ID}\nstatus: invalid\nprotocol_commit: {lock}\n'
                         f'implementation_commit: {implementation}\nNo valid performance evidence. Preserve failure; no automatic retry.\n')
        raise
    return {path: sha256(content).hexdigest() for path, content in first.items()}


if __name__ == '__main__':
    print(json.dumps(execute(), indent=2, sort_keys=True))
