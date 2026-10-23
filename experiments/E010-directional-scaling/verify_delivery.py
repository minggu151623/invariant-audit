"""Read-only post-run checks; writes a separate audit, never reruns the study."""
from collections import Counter
import csv
from hashlib import sha256
import gzip
import json
from pathlib import Path
import re
from statistics import median
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def require(condition, description):
    if not condition:
        raise ValueError(description)


def accepts(table, rules):
    for columns in rules:
        votes = Counter(row[-1] for row in table if all(row[j] == table[0][j] for j in columns))
        if any(count >= votes[table[0][-1]] for value, count in votes.items() if value != table[0][-1]):
            return False
    return True


def verify_witness(case, result):
    table, rules, witness = case['table'], case['rules'], result['witness']
    require(not result['verification_errors'], 'Recorded validation errors')
    if witness is None:
        require(result['status'] != 0, 'Missing exact witness')
        return 0
    require(len(witness) == len(table) and witness[0] == table[0], 'Target/shape changed')
    for row in witness:
        require(len(row) == len(table[0]), 'Width changed')
        require(all(isinstance(v, int) and 0 <= v < (case['rhs'] if j == len(row)-1 else case['keys'])
                    for j, v in enumerate(row)), 'Out-of-domain witness')
    cost = sum(a != b for r, s in zip(table, witness) for a, b in zip(r, s))
    require(cost == result['cost'], 'Wrong Hamming cost')
    require(accepts(table, rules) != accepts(witness, rules), 'Decision not flipped')
    if result.get('objective') is not None:
        require(abs(result['objective']-cost) <= 1e-7, 'Objective mismatch')
        require(result['maximum_constraint_residual'] <= 1e-7, 'Constraint residual')
        require(result['maximum_integrality_error'] <= 1e-7, 'Integrality error')
        if result['status'] == 0:
            require(result['mip_gap'] <= 1e-7 and abs(result['dual_bound']-cost) <= 1e-7, 'Optimal bound mismatch')
    return 1


def main():
    checks = json.loads((ROOT / 'data/E010-v1-checks.json').read_text())
    require(checks['status'] == 'valid_bounded_study', 'Study not valid')
    report = (ROOT / 'experiments/E010-directional-scaling/results/run-e010-20261023-001.md').read_text()
    pins = dict(re.findall(r'- `([^`]+)` SHA-256 `([a-f0-9]{64})`', report))
    require(len(pins) == 5, 'Missing report hashes')
    for path, digest in pins.items():
        require(sha256((ROOT / path).read_bytes()).hexdigest() == digest, f'Artifact drift: {path}')
    fixtures = json.loads(gzip.decompress((ROOT / 'data/E010-v1-preflight.json.gz').read_bytes()))
    cases = json.loads(gzip.decompress((ROOT / 'data/E010-v1-cases.json.gz').read_bytes()))
    obs = [json.loads(line) for line in gzip.decompress((ROOT / 'data/E010-v1-observations.jsonl.gz').read_bytes()).splitlines()]
    rows = list(csv.DictReader((ROOT / 'data/E010-v1-summary.csv').open()))
    require((len(fixtures), len(cases), len(obs), len(rows)) == (162, 72, 288, 72), 'Unexpected counts')
    verified = 0
    for fixture in fixtures:
        for method in ('generic', 'specialized'):
            result = fixture[method]
            require(result['status'] == 0 and result['cost'] == fixture['reference_radius'], 'Preflight mismatch')
            verified += verify_witness(fixture, result)
    lookup = {case['case_id']: case for case in cases}
    require(len(lookup) == 72, 'Duplicate IDs')
    seen = set()
    for o in obs:
        identity = (o['case_id'], o['method'], o['repetition'])
        require(identity not in seen, 'Duplicate observation'); seen.add(identity)
        case, result = lookup[o['case_id']], o['result']
        require(o['method'] in ('generic', 'specialized') and o['repetition'] in (1, 2), 'Bad method/repetition')
        require(result['status'] in (0, 1), 'Unexpected status')
        require(result['total_seconds'] > 0 and result['total_seconds'] >= result['build_seconds']+result['solve_seconds'], 'Bad timing')
        verified += verify_witness(case, result)
    for row in rows:
        case = lookup[row['case_id']]
        require(sha256((json.dumps(case['table'], sort_keys=True, separators=(',', ':'))+'\n').encode()).hexdigest() == case['table_sha256'], 'Table hash')
        medians, statuses, exact = {}, {}, {}
        for method in ('generic', 'specialized'):
            values = sorted((o for o in obs if o['case_id'] == row['case_id'] and o['method'] == method), key=lambda o: o['repetition'])
            require(len(values) == 2, 'Missing repetitions')
            results = [o['result'] for o in values]
            statuses[method] = '|'.join(str(v['status']) for v in results)
            medians[method] = median(v['total_seconds'] for v in results)
            exact[method] = all(v['status'] == 0 for v in results)
            require(row[f'{method}_statuses'] == statuses[method], 'Status summary')
            require(float(row[f'{method}_median_total_seconds']) == medians[method], 'Median summary')
            require(int(row[f'{method}_variables']) == results[0]['variables'], 'Variable summary')
            if exact[method]:
                require(len({v['cost'] for v in results}) == 1, 'Repeated optimal cost differs')
                require(int(row[f'{method}_exact_cost']) == results[0]['cost'], 'Cost summary')
        paired = all(exact.values())
        require((row['paired_exact'] == 'True') == paired, 'Paired status')
        if paired:
            require(row['generic_exact_cost'] == row['specialized_exact_cost'], 'Optimal methods disagree')
            require(float(row['paired_generic_over_specialized_time']) == medians['generic']/medians['specialized'], 'Ratio summary')
        else:
            require(row['paired_generic_over_specialized_time'] == '', 'Censored ratio included')
    for regime, aggregate in checks['regimes'].items():
        selected = [r for r in rows if r['regime'] == regime]
        paired = [r for r in selected if r['paired_exact'] == 'True']
        require(len(selected) == aggregate['cases'] and len(paired) == aggregate['paired_exact_cases'], 'Denominator summary')
        ratios = [float(r['paired_generic_over_specialized_time']) for r in paired]
        require(median(ratios) == aggregate['median_paired_time_ratio'], 'Regime ratio')
        require(sum(r < 1 for r in ratios) == aggregate['slower_specialized_cases'], 'Slower count')
    previous = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', 'c794125'], cwd=ROOT).decode().splitlines()
    preserve = [p for p in previous if p.startswith(('experiments/', 'data/', 'paper/', 'reproducibility/'))
                and p not in ('experiments/README.md', 'data/README.md')]
    for path in preserve:
        require((ROOT / path).read_bytes() == subprocess.check_output(['git', 'show', f'c794125:{path}'], cwd=ROOT), f'Previous artifact changed: {path}')
    with zipfile.ZipFile(ROOT / 'paper/evidence-review-bundle.zip') as z:
        require(z.testzip() is None, 'ZIP CRC')
        for name in z.namelist():
            require(z.read(name) == (ROOT / name).read_bytes(), f'Bundle member changed: {name}')
    result = dict(date='2026-10-23', status='pass', scope='serialized_post_run_witness_arithmetic_hash_and_preservation_self_review',
                  preflight_cases=162, benchmark_cases=72, observations=288, independently_rechecked_witnesses=verified,
                  prior_files_unchanged=len(preserve), preservation_base='c794125', M22_bundle_members_unchanged=True,
                  independent_review=False, novelty_established=False, artifact_sha256=pins)
    destination = ROOT / 'milestones/M28-delivery-verification.json'
    with destination.open('x') as f:
        json.dump(result, f, indent=2, sort_keys=True); f.write('\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
