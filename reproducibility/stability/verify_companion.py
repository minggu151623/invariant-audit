"""Verify the structural preprint companion without Git, solvers, TeX or network."""
import argparse
from collections import Counter
import csv
from hashlib import sha256
import gzip
import importlib.util
from itertools import product
import json
import math
from pathlib import Path, PurePosixPath
import re
from statistics import median
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]


def need(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def read_json(path):
    content = (ROOT / path).read_bytes()
    return json.loads(gzip.decompress(content) if path.endswith('.gz') else content)


def json_lines(path):
    return [json.loads(line) for line in gzip.decompress((ROOT / path).read_bytes()).splitlines()]


def csv_rows(path):
    with (ROOT / path).open(newline='') as f:
        return list(csv.DictReader(f))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def inventory():
    path = ROOT / 'reproducibility/stability/companion-manifest.json'
    need(not path.is_symlink(), 'Symlinked manifest')
    manifest = json.loads(path.read_bytes())
    for relative, pin in manifest['files'].items():
        parts = PurePosixPath(relative)
        need(not parts.is_absolute() and '..' not in parts.parts and '\\' not in relative, 'Unsafe member path')
        member = ROOT / relative
        need(member.is_file() and not member.is_symlink() and ROOT in member.resolve().parents, f'Missing/unsafe member: {relative}')
        payload = member.read_bytes()
        need(len(payload) == pin['bytes'] and sha256(payload).hexdigest() == pin['sha256'], f'Member hash mismatch: {relative}')
    return manifest


def accepts(table, rules):
    for columns in rules:
        counts = Counter(row[-1] for row in table if all(row[j] == table[0][j] for j in columns))
        if any(count >= counts[table[0][-1]] for value, count in counts.items() if value != table[0][-1]):
            return False
    return True


def witness(table, rules, changed, cost, keys, rhs, fixed=False):
    need(changed is not None and len(changed) == len(table) and list(changed[0]) == list(table[0]), 'Witness shape/target')
    for row in changed:
        need(len(row) == len(table[0]) and all(isinstance(v, int) and 0 <= v < (rhs if j == len(row)-1 else keys)
                                             for j, v in enumerate(row)), 'Witness domain')
    if fixed:
        need(all(tuple(a[:-1]) == tuple(b[:-1]) for a, b in zip(table, changed)), 'Protected keys changed')
    need(sum(a != b for r, s in zip(table, changed) for a, b in zip(r, s)) == cost, 'Witness cell cost')
    need(accepts(table, rules) != accepts(changed, rules), 'Witness does not flip raw decision')
    return 1


def fixed_raw(table, rules, rhs):
    initial, best = accepts(table, rules), None
    for values in product(range(rhs), repeat=len(table)-1):
        changed = (tuple(table[0]),)+tuple(tuple(row[:-1])+(v,) for row, v in zip(table[1:], values))
        cost = sum(a[-1] != b[-1] for a, b in zip(table, changed))
        if (best is None or cost < best) and accepts(changed, rules) != initial:
            best = cost
    return best


def result_witness(case, result, fixed=False):
    need(not result['verification_errors'], 'Stored witness errors')
    if result['witness'] is None:
        need(result['status'] != 0, 'Missing optimal witness')
        return 0
    count = witness(case['table'], case['rules'], result['witness'], result['cost'], case['keys'], case['rhs'], fixed)
    if result.get('objective') is not None:
        need(abs(result['objective']-result['cost']) <= 1e-7, 'Stored objective mismatch')
        need(result['maximum_integrality_error'] <= 1e-7 and result['maximum_constraint_residual'] <= 1e-7, 'Stored residual outside tolerance')
        if result['status'] == 0 and 'dual_bound' in result:
            gap = result.get('gap', result.get('mip_gap'))
            need(gap is not None and gap <= 1e-7 and result['dual_bound'] is not None
                 and abs(result['dual_bound']-result['cost']) <= 1e-7, 'Stored optimal bound mismatch')
    return count


def synthetic_checks():
    e008 = read_json('data/E008-v1-checks.json')
    rows8 = csv_rows('data/E008-v1-domain-summary.csv')
    need(len(rows8) == 66, 'E008 summary coverage')
    for field, key in [('tables', 'comparisons'), ('finite_witnesses', 'finite_witnesses'),
                       ('strict_reductions', 'strict_reductions'), ('protected_INF_to_finite', 'protected_INF_to_finite')]:
        need(sum(int(r[field]) for r in rows8) == e008[key], f'E008 aggregate: {field}')
    need(sum(int(r['accepted'])+int(r['rejected']) for r in rows8) == 30642, 'E008 decision count')
    need(sum(int(r['mismatches']) for r in rows8) == 0 and not e008['row_dominance_failures'], 'E008 recorded failures')
    n = 0
    examples = read_json('data/E008-v1-witnesses.json')
    for case in examples.values():
        for field in ('witness', 'reference_witness'):
            n += witness(case['table'], case['rules'], case[field], case['mutable_key_radius'], 2, 2)
    reference = load('companion_raw_reference', 'experiments/E008-mutable-key-certificates/code/exhaustive_reference.py')
    families = dict(load('companion_e008', 'experiments/E008-mutable-key-certificates/code/certificate.py').FAMILIES)
    checks9 = read_json('data/E009-v1-checks.json')
    rows9 = csv_rows('data/E009-v1-formula-summary.csv')
    for key, value in checks9['formula_totals'].items():
        need(sum(int(r[key]) for r in rows9) == value, f'E009 aggregate: {key}')
    baseline = json_lines('data/E009-v1-baseline-cases.jsonl.gz')
    statuses = Counter()
    for index, case in enumerate(baseline):
        need(case['case_index'] == index and not case['errors'], 'E009 case order/errors')
        rules, result = families[case['family']], case['MILP']
        truth, _ = reference.radius(tuple(map(tuple, case['table'])), rules, case['keys'], case['rhs'])
        need(truth == case['reference_radius'] == result['cost'], 'E009 raw optimum mismatch')
        need(result['status'] == (2 if truth is None else 0), 'E009 optimum/infeasibility mismatch')
        statuses[str(result['status'])] += 1
        n += result_witness(dict(case, rules=rules), result)
    need(len(baseline) == 2118 and dict(statuses) == checks9['baseline_status_counts'], 'E009 baseline coverage')
    for case in read_json('data/E009-v1-witnesses.json').values():
        n += witness(case['table'], case['rules'], case['witness'], case['formula_radius'], 2, 2)
    return dict(serialized_witnesses=n, E008_comparisons_recorded=e008['comparisons'],
                E008_aggregate_checks=True, E009_raw_optima_recomputed=len(baseline),
                E009_complete_formula_reexecution='see_separate_finite_reexecution_layer')


def computational_checks():
    design = load('companion_design', 'experiments/E010-directional-scaling/code/design.py')
    cases = read_json('data/E010-v1-cases.json.gz')
    expected = list(design.cases())
    for case in expected:
        case['table_sha256'] = sha256(canonical(case['table'])).hexdigest()
    need(canonical(cases) == canonical(expected), 'E010 input generator mismatch')
    fixtures = read_json('data/E010-v1-preflight.json.gz')
    verified, oracle_cache = 0, {}
    for case in fixtures:
        table, rules = tuple(map(tuple, case['table'])), tuple(map(tuple, case['rules']))
        key = canonical([table, rules, case['keys'], case['rhs']])
        truth = design.raw_radius(table, rules, case['keys'], case['rhs'])
        oracle_cache[key] = truth
        need(truth == case['reference_radius'], 'E010 preflight raw optimum')
        for method in ('generic', 'specialized'):
            need(case[method]['status'] == 0 and case[method]['cost'] == truth, 'E010 preflight method optimum')
            verified += result_witness(case, case[method])
    observations = json_lines('data/E010-v1-observations.jsonl.gz')
    lookup = {c['case_id']: c for c in cases}
    seen, by_case = set(), {}
    for obs in observations:
        identity = (obs['case_id'], obs['method'], obs['repetition'])
        need(identity not in seen and obs['method'] in ('generic', 'specialized') and obs['repetition'] in (1, 2), 'E010 observation coverage')
        seen.add(identity)
        r = obs['result']
        need(r['status'] in (0, 1), 'E010 unexpected status')
        need(math.isfinite(r['total_seconds']) and r['total_seconds'] > 0 and r['total_seconds'] >= r['build_seconds']+r['solve_seconds'], 'E010 timing invalid')
        verified += result_witness(lookup[obs['case_id']], r)
        by_case.setdefault(obs['case_id'], {}).setdefault(obs['method'], []).append(obs)
    rows = csv_rows('data/E010-v1-summary.csv')
    need((len(cases), len(rows), len(observations)) == (72, 72, 288), 'E010 counts')
    need(len({r['case_id'] for r in rows}) == 72, 'Duplicate E010 summaries')
    for row in rows:
        exact, medians = {}, {}
        for method in ('generic', 'specialized'):
            values = sorted(by_case[row['case_id']][method], key=lambda o: o['repetition'])
            need(len(values) == 2, 'E010 repetitions')
            results = [v['result'] for v in values]
            statuses = '|'.join(str(r['status']) for r in results)
            exact[method] = all(r['status'] == 0 for r in results)
            medians[method] = median(r['total_seconds'] for r in results)
            need(row[f'{method}_statuses'] == statuses and float(row[f'{method}_median_total_seconds']) == medians[method], 'E010 status/time summary')
            need(int(row[f'{method}_exact_repetitions']) == sum(r['status'] == 0 for r in results), 'E010 exact denominator')
            if exact[method]:
                need(len({r['cost'] for r in results}) == 1 and int(row[f'{method}_exact_cost']) == results[0]['cost'], 'E010 exact cost summary')
        paired = all(exact.values())
        need((row['paired_exact'] == 'True') == paired, 'E010 paired censoring')
        if paired:
            need(row['generic_exact_cost'] == row['specialized_exact_cost'], 'E010 paired optimum agreement')
            need(float(row['paired_generic_over_specialized_time']) == medians['generic']/medians['specialized'], 'E010 ratio arithmetic')
        else:
            need(row['paired_generic_over_specialized_time'] == '', 'Censored speedup reported')
    checks = read_json('data/E010-v1-checks.json')
    for regime, aggregate in checks['regimes'].items():
        selected = [r for r in rows if r['regime'] == regime]
        paired = [r for r in selected if r['paired_exact'] == 'True']
        ratios = [float(r['paired_generic_over_specialized_time']) for r in paired]
        need(len(selected) == aggregate['cases'] and len(paired) == aggregate['paired_exact_cases'], 'E010 regime denominators')
        need(median(ratios) == aggregate['median_paired_time_ratio'] and sum(r < 1 for r in ratios) == aggregate['slower_specialized_cases'], 'E010 regime ratio/slower count')
        for method in ('generic', 'specialized'):
            statuses = Counter(str(o['result']['status']) for o in observations if o['method'] == method and lookup[o['case_id']]['regime'] == regime)
            need(dict(statuses) == aggregate['statuses'][method], 'E010 status aggregate')
    pre11 = read_json('data/E011-v1-preflight.json.gz')
    for case in pre11:
        table, rules = tuple(map(tuple, case['table'])), tuple(map(tuple, case['rules']))
        key = canonical([table, rules, case['keys'], case['rhs']])
        need(key in oracle_cache and case['full_truth'] == oracle_cache[key], 'E011 preflight fixture/raw optimum')
        need(case['fixed_truth'] == fixed_raw(table, rules, case['rhs']), 'E011 fixed raw optimum')
        for method in ('full', 'fixed'):
            truth = case[f'{method}_truth']
            need(case[method]['status'] == (2 if truth is None else 0) and case[method]['cost'] == truth, 'E011 preflight method optimum')
            verified += result_witness(case, case[method], method == 'fixed')
    need(len(fixtures) == len(pre11) == 162, 'Preflight coverage')
    return dict(E010_cases_regenerated=72, E010_observations_verified=288,
                E010_preflight_optima_recomputed=162, E011_preflight_optima_recomputed=162,
                serialized_witnesses=verified, timing_rerun=False)


def decreases(record):
    return record['full']['cost'] is not None and (record['fixed']['cost'] is None or record['full']['cost'] < record['fixed']['cost'])


def source_output_checks():
    checks = read_json('data/E011-v1-checks.json')
    targets = json_lines('data/E011-v1-targets.jsonl.gz')
    solves = json_lines('data/E011-v1-rejected-solves.jsonl.gz')
    need(len(targets) == checks['targets'] == 18734, 'E011 complete target count')
    need(len({(r['dataset'], r['rhs'], r['row_index']) for r in targets}) == len(targets), 'E011 duplicate target')
    dirty = [{k: v for k, v in r.items() if k != 'reference_correct'} for r in targets]
    need(sha256(canonical(dirty)).hexdigest() == checks['accepted_double_build_hashes'][0] == checks['accepted_double_build_hashes'][1], 'Accepted freeze hash')
    need(sha256(canonical(dict(targets=dirty, solves=solves))).hexdigest() == checks['dirty_stage_sha256_before_reference'], 'Dirty/reference freeze hash')
    tasks = {(t['dataset'], t['rhs']): t for t in checks['tasks']}
    universe_sizes = Counter((r['dataset'], r['rhs']) for r in targets)
    for key, size in universe_sizes.items():
        need({r['row_index'] for r in targets if (r['dataset'], r['rhs']) == key} == set(range(1, size+1)), 'Source row universe incomplete')
    coordinate_witnesses = 0
    def coordinate_cost(record, result, fixed):
        nonlocal coordinate_witnesses
        need(not result['verification_errors'], 'E011 stored error')
        if result['edits'] is None:
            need(result['status'] != 0, 'Missing source witness')
            return
        task = tasks[record['dataset'], record['rhs']]
        columns = {v+1: j for j, v in enumerate(task['columns'])}
        cells = set()
        for row, col, value in result['edits']:
            need(isinstance(row, int) and 1 <= row <= universe_sizes[record['dataset'], record['rhs']]
                 and row != record['row_index'] and col in columns, 'Source edit coordinate')
            need((row, col) not in cells, 'Duplicate source edit'); cells.add((row, col))
            j = columns[col]
            need(isinstance(value, int) and 0 <= value < task['sizes'][j], 'Source edit domain code')
            need(not fixed or j == len(task['sizes'])-1, 'Source protected key edit')
        need(len(cells) == result['cost'], 'Source coordinate edit count')
        coordinate_witnesses += 1
    accepted = [r for r in targets if r['initial_accepted']]
    need(len(accepted) == checks['accepted'] == 13762 and len(targets)-len(accepted) == checks['rejected'] == 4972, 'Source decision aggregate')
    for r in targets:
        need(isinstance(r['initial_accepted'], bool) and isinstance(r['reference_correct'], bool), 'Source decision/label type')
        need(r['has_singleton'] == (1 in r['group_sizes']), 'Singleton metadata')
        if r['initial_accepted']:
            need(r['full']['status'] == 0 and r['fixed']['status'] == (2 if r['fixed']['cost'] is None else 0), 'Source accepted exactness status')
            for method in ('full', 'fixed'):
                coordinate_cost(r, r[method], method == 'fixed')
            need(r['full']['cost'] is not None, 'Source accepted full INF unexpected')
            need(r['fixed']['cost'] is None or r['full']['cost'] <= r['fixed']['cost'], 'Accepted nesting')
            need(r['has_singleton'] or not decreases(r), 'No-singleton reduction')
        else:
            need('full' not in r and 'fixed' not in r, 'Unsampled rejected radius mislabeled')
    selected_ids = set()
    for selection in checks['selection']:
        rejected = [r for r in targets if r['dataset'] == selection['dataset'] and r['rhs'] == selection['rhs'] and not r['initial_accepted']]
        hashes = sorted((sha256(f'E011-v1|rejected|{r["dataset"]}|{r["rhs"]}|{r["row_index"]}'.encode()).hexdigest(), r['row_index']) for r in rejected)[:4]
        need(len(rejected) == selection['total_rejected'], 'Rejected source denominator')
        need(hashes == [(r['sha256'], r['row_index']) for r in selection['selected']], 'Source selection hash')
        selected_ids.update((selection['dataset'], selection['rhs'], i) for h, i in hashes)
    need(selected_ids == {(r['dataset'], r['rhs'], r['row_index']) for r in solves} and len(solves) == 32, 'Selected solve coverage')
    for pair in solves:
        for method in ('full', 'fixed'):
            r = pair[method]
            need(r['status'] in (0, 1), 'Source status')
            coordinate_cost(pair, r, method == 'fixed')
            if r['status'] == 0:
                need(r['gap'] <= 1e-7 and abs(r['objective']-r['cost']) <= 1e-7
                     and abs(r['dual_bound']-r['cost']) <= 1e-7, 'Source recorded bound')
        if pair['full']['status'] == pair['fixed']['status'] == 0:
            need(pair['full']['cost'] <= pair['fixed']['cost'], 'Source rejected nesting')
    for method in ('full', 'fixed'):
        need(dict(Counter(str(r[method]['status']) for r in solves)) == checks['rejected_statuses'][method], 'Source status aggregate')
    summary = csv_rows('data/E011-v1-summary.csv')
    need(len(summary) == 9, 'Source summary coverage')
    for row in summary:
        selected = [r for r in targets if r['dataset'] == row['dataset'] and r['rhs'] == row['rhs']]
        a = [r for r in selected if r['initial_accepted']]
        s = [r for r in solves if r['dataset'] == row['dataset'] and r['rhs'] == row['rhs']]
        p = [r for r in s if r['full']['status'] == r['fixed']['status'] == 0]
        expected = dict(rows=len(selected), accepted=len(a), rejected=len(selected)-len(a),
                        accepted_with_singleton=sum(r['has_singleton'] for r in a),
                        accepted_strict_finite_decreases=sum(decreases(r) and r['fixed']['cost'] is not None for r in a),
                        accepted_fixed_INF_to_finite=sum(decreases(r) and r['fixed']['cost'] is None for r in a),
                        accepted_without_reduction=sum(not decreases(r) for r in a),
                        accepted_reference_incorrect=sum(not r['reference_correct'] for r in a),
                        selected_rejected=len(s), selected_rejected_exact_pairs=len(p),
                        selected_rejected_strict_decreases=sum(decreases(r) for r in p),
                        full_timeouts=sum(r['full']['status'] == 1 for r in s), fixed_timeouts=sum(r['fixed']['status'] == 1 for r in s))
        for k, value in expected.items():
            need(int(row[k]) == value, f'Source summary arithmetic: {k}')
    buckets = csv_rows('data/E011-v1-reference-buckets.csv')
    need(len(buckets) == 36, 'Source bucket coverage')
    for row in buckets:
        def belongs(r):
            cost, bucket = r['full']['cost'], row['bucket']
            return cost is None if bucket == 'INF' else cost is not None and (cost >= 3 if bucket == '>=3' else cost == int(bucket))
        selected = [r for r in accepted if r['dataset'] == row['dataset'] and r['rhs'] == row['rhs'] and belongs(r)]
        need(int(row['accepted']) == len(selected) and int(row['reference_correct']) == sum(r['reference_correct'] for r in selected)
             and int(row['reference_incorrect']) == sum(not r['reference_correct'] for r in selected), 'Reference bucket arithmetic')
    distribution = Counter((r['dataset'], r['rhs'], method, 'INF' if r[method]['cost'] is None else str(r[method]['cost']))
                           for r in accepted for method in ('full', 'fixed'))
    recorded = {(r['dataset'], r['rhs'], r['method'], r['radius']): int(r['accepted_targets']) for r in csv_rows('data/E011-v1-radius-distribution.csv')}
    need(dict(distribution) == recorded, 'Radius histogram arithmetic')
    need(sum(decreases(r) for r in accepted) == checks['accepted_strict_reductions'] == 1134, 'Source strict reductions')
    need(sum(decreases(r) and r['fixed']['cost'] is None for r in accepted) == 1133, 'Source INF transitions')
    need(sum(decreases(r) and r['fixed']['cost'] is not None for r in accepted) == 1, 'Source finite decreases')
    pairs = [r for r in solves if r['full']['status'] == r['fixed']['status'] == 0]
    need(len(pairs) == checks['selected_rejected_exact_pairs'] == 30 and sum(decreases(r) for r in pairs) == 0, 'Source negative exact-pair result')
    need(sum(not r['reference_correct'] for r in accepted) == 1816, 'Source accepted reference disagreements')
    need(sum(not r['reference_correct'] and r['full']['cost'] >= 2 for r in accepted) == 1493, 'Robust reference disagreements')
    return dict(targets=len(targets), accepted=len(accepted), selected_rejected=len(solves),
                coordinate_costs_checked=coordinate_witnesses, source_raw_decisions_checked=False,
                source_reference_labels_checked=False, source_bytes_checked=False,
                statement='Raw source radii, witness flips and reference labels require --source-root.')


def verify_sources(source_root):
    manifest = read_json('data/E006-v1-source-manifest.json')
    payloads = {}
    for item in manifest['files']:
        path = source_root / item['path']
        need(path.is_file() and not path.is_symlink(), f'Missing/nonregular source: {item["path"]}')
        payload = path.read_bytes()
        need(len(payload) == item['bytes'] and sha256(payload).hexdigest() == item['sha256'], f'Source pin mismatch: {item["path"]}')
        payloads[item['path']] = payload
    helper = load('companion_source_checker', 'experiments/E011-reused-source-stability/verify_delivery.py')
    parser = helper.sources
    dirty, tasks = parser.dirty_tasks(manifest, {k: v for k, v in payloads.items() if k.endswith('/dirty.csv')})
    clean = parser.references(manifest, payloads, dirty)
    task_lookup = {(t['dataset'], t['rhs']): (t, helper.prepare(t)) for t in tasks}
    targets = json_lines('data/E011-v1-targets.jsonl.gz')
    count = 0
    for r in targets:
        task, groups = task_lookup[r['dataset'], r['rhs']]
        i = r['row_index']-1
        initial, sizes, full, fixed = helper.direct_radii(task, groups, i)
        need(initial == r['initial_accepted'] and sizes == r['group_sizes'], 'Source raw decision/groups')
        j = manifest['canonical_headers'][r['dataset']].index(r['rhs'])
        need(r['reference_correct'] == (dirty[r['dataset']][i][j] == clean[r['dataset']][i][j]), 'Source raw reference label')
        if initial:
            need((full, fixed) == (r['full']['cost'], r['fixed']['cost']), 'Source raw radius')
            for method in ('full', 'fixed'):
                count += helper.verify_coordinate_witness(task, groups, i, r[method], method == 'fixed')
    for pair in json_lines('data/E011-v1-rejected-solves.jsonl.gz'):
        task, groups = task_lookup[pair['dataset'], pair['rhs']]
        for method in ('full', 'fixed'):
            count += helper.verify_coordinate_witness(task, groups, pair['row_index']-1, pair[method], method == 'fixed')
    return dict(source_bytes_checked=9, raw_target_decisions_checked=len(targets),
                accepted_radii_reconstructed=sum(r['initial_accepted'] for r in targets),
                raw_coordinate_witnesses_checked=count, reference_labels_checked=len(targets),
                solvers_rerun=False, scope='Reuses frozen source-delivery helper; self-review, not independent assessment.')


def finite_recheck():
    path = 'experiments/E008-mutable-key-certificates/code'
    sys.path.insert(0, str(ROOT / path))
    runner = load('companion_e008_runner', path+'/run_e008.py')
    saved = read_json('data/E008-v1-checks.json')
    rebuilt = runner.build(saved['protocol_commit'], saved['implementation_commit'])
    for relative, content in rebuilt.items():
        need(content == (ROOT / relative).read_bytes(), f'E008 full reconstruction differs: {relative}')
    formula = load('companion_formula', 'experiments/E009-singleton-characterization/code/closed_form.py')
    fixed = runner.load_baseline()
    count, finite = 0, 0
    for keys, rhs, maximum in runner.DOMAINS:
        symbols = tuple(product(range(keys), range(keys), range(keys), range(rhs)))
        for n in range(1, maximum+1):
            for tail in product(symbols, repeat=n-1):
                table = ((0, 0, 0, 0),)+tail
                for name, rules in runner.candidate.FAMILIES:
                    if not runner.reference.accepts(table, rules):
                        continue
                    count += 1
                    cost, changed, groups = formula.radius(table, rules, rhs)
                    truth, _ = runner.reference.radius(table, rules, keys, rhs)
                    need(cost == truth, 'E009 complete formula/raw mismatch')
                    protected = runner.fixed_radius(table, rules, rhs, fixed)
                    need(any(g['size'] == 1 for g in groups) or cost == protected, 'E009 no-singleton characterization')
                    if cost is not None:
                        finite += witness(table, rules, changed, cost, keys, rhs)
    need((count, finite) == (18779, 18755), 'E009 full finite coverage')
    return dict(E008_artifacts_reconstructed_byte_identically=len(rebuilt), E008_radius_comparisons=30642,
                E008_dominance_comparisons=61854, E009_formula_cases_recomputed=count,
                E009_formula_witnesses_checked=finite, original_study_outputs_written=False)


def manuscript_checks(manifest):
    claims = read_json('reproducibility/stability/claims.json')
    need(not claims['worldwide_priority_claim'] and not claims['independent_scientific_review'], 'Unestablished priority/review claim')
    need(len({c['id'] for c in claims['claims']}) == len(claims['claims']) == 8, 'Claim map coverage')
    tex = (ROOT / claims['manuscript']).read_text()
    flat = re.sub(r'\s+', ' ', tex)
    for claim in claims['claims']:
        for field in ('arguments', 'evidence'):
            for path in claim.get(field, []):
                need(path in manifest['files'], f'Claim evidence not bundled: {path}')
        for anchor in claim.get('manuscript_anchors', []):
            need('\\label{'+anchor+'}' in tex, f'Missing proof anchor: {anchor}')
    render = read_json('paper/context-edit-stability/render-verification.json')
    for path, digest in render['artifact_sha256'].items():
        need(sha256((ROOT / path).read_bytes()).hexdigest() == digest, f'M30 render identity drift: {path}')
    for r in csv_rows('data/E011-v1-summary.csv'):
        label = r['dataset'].capitalize()+' '+r['rhs'].replace('_', r'\_')
        fragment = f"{label}&{r['accepted']}&{r['accepted_fixed_INF_to_finite']}&{r['accepted_strict_finite_decreases']}"
        need(fragment in tex, f'Manuscript source table binding: {label}')
    for fragment in ('all 30,642 radii, 30,618 finite witnesses and 61,854 dominance checks agree',
                     '18,779 accepted cases', '18,755 finite witnesses', '2,118 cases',
                     '18 infeasible instances', '18,734 target cells', '13,762 accepted',
                     '4,972 rejected', '1,816 differ', '1,493 of these',
                     'Their full optima remain unknown', 'no worldwide priority claim is made'):
        need(fragment in flat, f'Manuscript required fact/caveat missing: {fragment}')
    ratio = read_json('data/E010-v1-checks.json')['regimes']['rejected_coupled']['median_paired_time_ratio']
    need(f'{ratio:.3f}' in flat, 'Rounded manuscript runtime ratio')
    need(render['pages'] == 7 and render['owner_approval'] == 'not_given', 'M30 review/page identity')
    fields = read_json('paper/context-edit-stability/submission-fields-draft.json')
    abstract = re.sub(r'\s+', ' ', re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', tex, re.S).group(1)).strip()
    need(fields['abstract'] == abstract and fields['abstract_characters'] == len(abstract) <= 1920
         and abstract.isascii() and fields['title'].isascii(), 'Submission abstract identity/format')
    need(fields['artifact_sha256'] == render['artifact_sha256'] and fields['license'] is None
         and fields['actual_submission'] == 'absent' and fields['owner_content_approval'] == 'not_given', 'Unapproved submission state')
    need(fields['authors_display'] == ['Trần Vũ Bảo Minh'] and not fields['authors_form_proposal_approved'], 'Author identity/form status')
    return dict(claims_mapped=8, proof_anchors_present=4, E011_table_rows_bound=9,
                source_preview_hashes_bound=True, submission_abstract_characters=len(abstract),
                scope='Text/artifact correspondence; mathematical proof and originality are not automatically certified.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path, help='Optional relocated root with the nine pinned Raha files')
    parser.add_argument('--recheck-finite', action='store_true', help='Rebuild deterministic finite E008/E009 evidence in memory; no solver/timing run')
    args = parser.parse_args()
    manifest = inventory()
    result = dict(status='pass', bundle_members_hash_verified=len(manifest['files']),
                  synthetic=synthetic_checks(), computation=computational_checks(), source_outputs=source_output_checks(),
                  manuscript=manuscript_checks(manifest),
                  finite_reexecution=finite_recheck() if args.recheck_finite else 'not_requested',
                  raw_source_verification=verify_sources(args.source_root.resolve()) if args.source_root else 'not_checked_no_source_root',
                  scientific_independent_review=False, proof_or_novelty_certification=False,
                  original_MILP_and_timing_runs_reexecuted=False, optimized_python=not __debug__)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
