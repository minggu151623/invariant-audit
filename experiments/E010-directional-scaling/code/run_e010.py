"""One locked comparison, with all timeouts and complete case-level outcomes."""
from collections import Counter
import csv
from hashlib import sha256
import gzip
import io
import json
from pathlib import Path
import platform
from statistics import median
import subprocess

import numpy as np
import scipy

import design
import models

ROOT = Path(__file__).resolve().parents[3]
LOCK = 'fbd04cb'
PROTOCOL = 'experiments/E010-directional-scaling/protocol.md'
PIN_PATH = 'experiments/E009-singleton-characterization/code/generic_milp.py'
PIN = '2be4637ab7b58efea07495fedba3da1ed678c719df0008bce0ac54e4699bfebb'
RUN = 'e010-20261023-001'
REPORT = f'experiments/E010-directional-scaling/results/run-{RUN}.md'
OUTPUTS = ('data/E010-v1-preflight.json.gz', 'data/E010-v1-cases.json.gz',
           'data/E010-v1-observations.jsonl.gz', 'data/E010-v1-summary.csv',
           'data/E010-v1-checks.json', REPORT)


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def guard():
    if any((ROOT / p).exists() or (ROOT / p).is_symlink() for p in OUTPUTS):
        raise ValueError('Existing output; identity may not be repeated')
    environment = {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__}
    if environment != {'python': '3.13.5', 'numpy': '2.1.3', 'scipy': '1.17.1'}:
        raise ValueError(f'Runtime drift: {environment}')
    if sha256((ROOT / PIN_PATH).read_bytes()).hexdigest() != PIN:
        raise ValueError('Generic baseline source drift')
    lock = git('rev-parse', LOCK).decode().strip()
    implementation = git('rev-parse', 'HEAD').decode().strip()
    if (ROOT / PROTOCOL).read_bytes() != git('show', f'{lock}:{PROTOCOL}'):
        raise ValueError('Protocol drift')
    git('merge-base', '--is-ancestor', lock, implementation)
    for p in Path(__file__).parent.glob('*.py'):
        if p.read_bytes() != git('show', f'{implementation}:{p.relative_to(ROOT)}'):
            raise ValueError(f'Uncommitted implementation: {p.name}')
    return lock, implementation, environment


def checked(table, rules, keys, rhs, result):
    result['verification_errors'].extend(design.witness_errors(table, rules, keys, rhs, result))
    return result


def specialized(case):
    table, rules, rhs = case['table'], case['rules'], case['rhs']
    if design.accepts(table, rules):
        return models.accepted_formula(table, rules, rhs)
    return models.solve(table, rules, case['keys'], rhs, 'canonical')


def preflight():
    records, failures = [], []
    for index, (keys, rhs, family, rules, table) in enumerate(design.fixtures()):
        truth = design.raw_radius(table, rules, keys, rhs)
        generic = checked(table, rules, keys, rhs, models.solve(table, rules, keys, rhs, 'generic'))
        candidate = checked(table, rules, keys, rhs, specialized(dict(table=table, rules=rules, rhs=rhs, keys=keys)))
        record = dict(index=index, keys=keys, rhs=rhs, family=family, rules=rules, table=table,
                      reference_radius=truth, generic=generic, specialized=candidate)
        records.append(record)
        for method in ('generic', 'specialized'):
            r = record[method]
            if r['status'] != 0 or r['cost'] != truth or r['verification_errors']:
                failures.append(dict(index=index, method=method, status=r['status'], expected=truth,
                                     cost=r['cost'], errors=r['verification_errors']))
    if len(records) != 162:
        raise ValueError('Fixture count differs from protocol')
    return records, failures


def summarize(cases, observations):
    rows = []
    for case in cases:
        subsets = {method: [o['result'] for o in observations if o['case_id'] == case['case_id'] and o['method'] == method]
                   for method in ('generic', 'specialized')}
        exact = {method: len(values) == 2 and all(v['status'] == 0 and not v['verification_errors'] for v in values)
                 for method, values in subsets.items()}
        paired = all(exact.values())
        row = {key: case[key] for key in ('case_id', 'q', 'n', 'rhs', 'family', 'regime')}
        row['paired_exact'] = paired
        for method, values in subsets.items():
            row[f'{method}_statuses'] = '|'.join(str(v['status']) for v in values)
            row[f'{method}_exact_repetitions'] = sum(v['status'] == 0 and not v['verification_errors'] for v in values)
            row[f'{method}_median_total_seconds'] = median(v['total_seconds'] for v in values) if values else ''
            row[f'{method}_variables'] = values[0]['variables'] if values else ''
            row[f'{method}_constraints'] = values[0]['constraints'] if values else ''
            row[f'{method}_exact_cost'] = values[0]['cost'] if exact[method] else ''
        row['paired_generic_over_specialized_time'] = (row['generic_median_total_seconds']/row['specialized_median_total_seconds']) if paired else ''
        rows.append(row)
    return rows


def publish(contents):
    written = []
    try:
        for relative, content in contents.items():
            p = ROOT / relative
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('xb') as handle:
                handle.write(content)
            written.append(p)
    except Exception:
        for p in written:
            p.unlink()
        raise


def run():
    lock, implementation, environment = guard()
    fixtures, failures = preflight()
    print(encode({'stage': 'preflight', 'cases': len(fixtures), 'failures': failures}).decode(), flush=True)
    cases, observations, benchmark_errors = [], [], []
    if not failures:
        cases = list(design.cases())
        if len(cases) != 72 or encode(cases) != encode(list(design.cases())):
            raise ValueError('Generator count/determinism failure')
        for case in cases:
            case['table_sha256'] = sha256(encode(case['table'])).hexdigest()
        warm_table, warm_rules = ((0, 0, 0), (0, 0, 1)), ((0, 1),)
        for method in ('generic', 'canonical'):
            warm = checked(warm_table, warm_rules, 4, 2, models.solve(warm_table, warm_rules, 4, 2, method))
            if warm['status'] != 0 or warm['cost'] != 1 or warm['verification_errors']:
                raise ValueError(f'Warmup failure: {method}')
        warm = models.accepted_formula(((0, 0, 0), (0, 0, 0)), warm_rules, 2)
        if warm['status'] != 0 or warm['cost'] != 1:
            raise ValueError('Formula warmup failure')
        for case in cases:
            for repetition in range(2):
                order = ('generic', 'specialized') if repetition == 0 else ('specialized', 'generic')
                for method in order:
                    result = models.solve(case['table'], case['rules'], case['keys'], case['rhs'], 'generic') if method == 'generic' else specialized(case)
                    checked(case['table'], case['rules'], case['keys'], case['rhs'], result)
                    observations.append(dict(case_id=case['case_id'], repetition=repetition+1, method=method, result=result))
                    if result['verification_errors'] or result['status'] not in (0, 1):
                        benchmark_errors.append(dict(case_id=case['case_id'], repetition=repetition+1, method=method,
                                                     status=result['status'], errors=result['verification_errors']))
            exact = [o['result']['cost'] for o in observations if o['case_id'] == case['case_id'] and o['result']['status'] == 0 and not o['result']['verification_errors']]
            if len(set(exact)) > 1:
                benchmark_errors.append(dict(case_id=case['case_id'], error='optimal_cost_disagreement', costs=exact))
            print(encode({'stage': 'benchmark', 'case': case['case_id'], 'observations': len(observations)}).decode(), flush=True)
    rows = summarize(cases, observations)
    stream = io.StringIO(newline='')
    if rows:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    regimes = {}
    for regime in ('accepted_dense', 'accepted_singleton', 'rejected_coupled'):
        selected = [r for r in rows if r['regime'] == regime]
        paired = [r for r in selected if r['paired_exact']]
        counts = {method: dict(Counter(str(o['result']['status']) for o in observations
                                       if o['method'] == method and any(c['case_id'] == o['case_id'] for c in cases if c['regime'] == regime)))
                  for method in ('generic', 'specialized')}
        regimes[regime] = dict(cases=len(selected), paired_exact_cases=len(paired), statuses=counts,
                              slower_specialized_cases=sum(r['paired_generic_over_specialized_time'] < 1 for r in paired),
                              median_paired_time_ratio=median(r['paired_generic_over_specialized_time'] for r in paired) if paired else None)
    checks = dict(run_id=RUN, protocol_commit=lock, implementation_commit=implementation,
                  protocol_sha256=sha256((ROOT / PROTOCOL).read_bytes()).hexdigest(),
                  generic_source_sha256=PIN, environment=environment,
                  machine=dict(system=platform.system(), release=platform.release(), machine=platform.machine()),
                  classification='constructed_direction_separated_computational_study',
                  status='failed_preflight' if failures else 'failed_validation' if benchmark_errors else 'valid_bounded_study',
                  preflight_cases=len(fixtures), preflight_failures=failures, benchmark_cases=len(cases),
                  observations=len(observations), benchmark_errors=benchmark_errors, regimes=regimes,
                  H10a=not failures, H10b=not failures and not benchmark_errors,
                  H10c_exact_agreement=not failures and not benchmark_errors,
                  timing_repetitions=2, time_limit_seconds=1.0,
                  novelty_established=False, real_data_validation=False, independent_review=False)
    contents = {OUTPUTS[0]: gzip.compress(encode(fixtures), mtime=0),
                OUTPUTS[1]: gzip.compress(encode(cases), mtime=0),
                OUTPUTS[2]: gzip.compress(b''.join(encode(o) for o in observations), mtime=0),
                OUTPUTS[3]: stream.getvalue().encode(), OUTPUTS[4]: encode(checks)}
    report = f'# E010-v1 — {RUN}\n\nStatus: {checks["status"]}.\n\nProtocol: {lock}. Implementation: {implementation}.\n\n'
    report += f'Preflight: {len(fixtures)} cases, {len(failures)} failures. Benchmark: {len(cases)} cases, {len(observations)} method observations, {len(benchmark_errors)} validation errors.\n\n'
    report += '| Regime | Cases | Both exact twice | Specialized slower | Median paired time ratio, generic/specialized |\n|---|---:|---:|---:|---:|\n'
    for regime, result in regimes.items():
        report += f'| {regime} | {result["cases"]} | {result["paired_exact_cases"]} | {result["slower_specialized_cases"]} | {result["median_paired_time_ratio"]} |\n'
    report += '\nAll solver statuses, including timeouts, are retained in the checks and observation files. Ratios use only pairs exact in both repetitions; see denominators above. The one-second limit bounds solver search, not complete method execution. These synthetic cases do not establish representative speed, detector accuracy or novelty.\n\n## Artifacts\n\n'
    for p, content in contents.items():
        report += f'- `{p}` SHA-256 `{sha256(content).hexdigest()}`\n'
    contents[REPORT] = report.encode()
    publish(contents)
    print(encode(checks).decode(), flush=True)


if __name__ == '__main__':
    run()
