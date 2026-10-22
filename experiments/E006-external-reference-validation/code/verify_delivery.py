"""Post-run verification of frozen E006 bytes; no source-row analysis or rerun."""
from collections import Counter, defaultdict
import csv
from fractions import Fraction
import gzip
from hashlib import sha256
import io
import json
import math
from pathlib import Path
import re

import point_reference

ROOT = Path(__file__).resolve().parents[3]
REPORT = ROOT / 'experiments/E006-external-reference-validation/results/run-e006-20261022-001.md'


def run():
    manifest = json.loads((ROOT / 'data/E006-v1-source-manifest.json').read_text())
    for item in manifest['files']:
        content = (Path(manifest['source_root']) / item['path']).read_bytes()
        assert len(content) == item['bytes'] and sha256(content).hexdigest() == item['sha256']
    artifact_hashes = re.findall(r'`(data/[^`]+)` SHA-256 `([0-9a-f]{64})`', REPORT.read_text())
    assert len(artifact_hashes) == 5
    for name, digest in artifact_hashes:
        assert sha256((ROOT / name).read_bytes()).hexdigest() == digest
    checks = json.loads((ROOT / 'data/E006-v1-checks.json').read_text())
    metrics = list(csv.DictReader((ROOT / 'data/E006-v1-metrics.csv').open()))
    intervals = list(csv.DictReader((ROOT / 'data/E006-v1-intervals.csv').open()))
    assert len(metrics) == 144 and len(intervals) == 84
    groups = defaultdict(list)
    seen, per_cell, row_columns = set(), Counter(), defaultdict(set)
    max_probability_error = 0.0
    with gzip.open(ROOT / 'data/E006-v1-predictions.csv.gz', 'rt', newline='') as stream:
        for row in csv.DictReader(stream):
            dataset, split, method = row['dataset'], row['split'], row['method']
            i, j = int(row['row_index']), int(row['column_index'])
            raw, y, decision = int(row['raw_score']), int(row['truth']), bool(int(row['decision']))
            assert 1 <= i <= checks['dataset_checks'][dataset]['source_rows']
            assert 1 <= j <= checks['dataset_checks'][dataset]['source_columns']
            assert len(row['component_id']) == 64
            key = dataset, i, j, method
            assert key not in seen
            seen.add(key)
            per_cell[dataset, i, j] += 1
            row_columns[dataset, i].add(j)
            assert y in (0, 1) and decision == (raw == 0)
            assert int(row['p_binary']) == int(decision)
            lookup = checks['dataset_checks'][dataset]['calibration_lookups'][method]
            probabilities = {entry['score']: Fraction(entry['numerator'], entry['denominator']) for entry in lookup['entries']}
            expected_p = probabilities.get(raw, Fraction(*lookup['fallback']))
            exported = Fraction(row['p_lookup'])
            difference = abs(float(exported-expected_p))
            assert difference <= 2e-12
            max_probability_error = max(max_probability_error, difference)
            column = manifest['canonical_headers'][dataset][j-1]
            endpoint_columns = {'beers': {'brewery_id', 'brewery_name', 'city', 'state'},
                                'flights': {'flight', 'sched_dep_time', 'act_dep_time', 'sched_arr_time', 'act_arr_time'},
                                'rayyan': {'jounral_abbreviation', 'journal_issn', 'journal_title'}}
            for scope in ('all_cells', 'fd_columns'):
                if scope == 'fd_columns' and column not in endpoint_columns[dataset]:
                    continue
                groups[dataset, split, scope, method].append((y, decision, exported))
                groups[dataset, split, scope, method+'-binary'].append((y, decision, Fraction(int(decision))))
    assert len(seen) == checks['prediction_rows'] == 193424
    assert set(per_cell.values()) == {4}
    for dataset, detail in checks['dataset_checks'].items():
        key_column = {'beers': 'index', 'flights': 'tuple_id', 'rayyan': 'id'}[dataset]
        expected = set(range(1, detail['source_columns']+1)) - {manifest['canonical_headers'][dataset].index(key_column)+1}
        assert all(row_columns[dataset, i] == expected for i in range(1, detail['source_rows']+1))
    metric_difference = 0.0
    for row in metrics:
        group = groups[row['dataset'], row['split'], row['scope'], row['method']]
        result = point_reference.compute([r[0] for r in group], [r[1] for r in group], tuple(r[2] for r in group))
        for field in ('support', 'tp', 'tn', 'fp', 'fn'):
            assert result[field] == int(row[field])
        for field in ('balanced_accuracy', 'fpr', 'fnr', 'brier', 'ece'):
            if result[field] is None:
                assert row[field] == 'NA'
            else:
                difference = abs(float(result[field])-float(row[field]))
                assert difference <= 2e-12
                metric_difference = max(metric_difference, difference)
    blocks = defaultdict(list)
    with gzip.open(ROOT / 'data/E006-v1-bootstrap.csv.gz', 'rt', newline='') as stream:
        for row in csv.DictReader(stream):
            key = row['dataset'], row['pair'], row['metric']
            assert int(row['replicate']) == len(blocks[key])
            blocks[key].append(None if row['status'] == 'undefined' else float(row['delta']))
    assert len(blocks) == 84 and sum(map(len, blocks.values())) == 840000
    interval_difference = 0.0
    for row in intervals:
        values = sorted(value for value in blocks[row['dataset'], row['pair'], row['metric']] if value is not None)
        assert len(values) == int(row['usable_replicates'])
        for q, field in ((.025, 'lower'), (.975, 'upper')):
            if not values:
                assert row[field] == 'NA'
                continue
            h = (len(values)-1)*q
            lo, hi = math.floor(h), math.ceil(h)
            quantile = values[lo] + (h-lo)*(values[hi]-values[lo])
            difference = abs(quantile-float(row[field]))
            assert difference <= 2e-12
            interval_difference = max(interval_difference, difference)
    return {'status': 'pass', 'scope': 'post_run_delivery_arithmetic_and_integrity_self_review',
            'source_files_hash_verified': 9, 'delivered_artifacts_hash_verified': 5,
            'prediction_rows': len(seen), 'point_rows': len(metrics), 'point_metric_comparisons': len(metrics)*5,
            'bootstrap_rows': sum(map(len, blocks.values())), 'interval_rows': len(intervals),
            'maximum_probability_serialization_error': max_probability_error,
            'maximum_exported_point_metric_difference': metric_difference,
            'maximum_exported_interval_difference': interval_difference,
            'report_sha256': sha256(REPORT.read_bytes()).hexdigest(),
            'independent_scientific_review': False}


if __name__ == '__main__':
    result = run()
    target = ROOT / 'milestones/M20-delivery-verification.json'
    with target.open('x') as stream:
        stream.write(json.dumps(result, sort_keys=True, indent=2)+'\n')
    print(json.dumps(result, sort_keys=True, indent=2))
