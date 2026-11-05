"""Post-result analytical reanalysis of frozen E011 records; no solver or source CSV reads."""
import ast
import csv
import gzip
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    relative_inputs = [
        'experiments/E011-reused-source-stability/code/sources.py',
        'data/E006-v1-source-manifest.json',
        'data/E011-v1-checks.json',
        'data/E011-v1-summary.csv',
        'data/E011-v1-rejected-solves.jsonl.gz',
    ]
    preserved = json.loads((ROOT / 'milestones/M33-preserved-artifacts.json').read_text())
    hashes = {}
    for relative in relative_inputs:
        hashes[relative] = digest(ROOT / relative)
        require(hashes[relative] == preserved[relative], f'Frozen input drift: {relative}')

    tree = ast.parse((ROOT / relative_inputs[0]).read_text())
    definitions = [node.value for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'TASKS' for t in node.targets)]
    require(len(definitions) == 1, 'Ambiguous task definitions')
    tasks = ast.literal_eval(definitions[0])
    manifest = json.loads((ROOT / relative_inputs[1]).read_text())
    historical_checks = json.loads((ROOT / relative_inputs[2]).read_text())
    require(historical_checks['validation_errors'] == [], 'Archived validation errors')
    with (ROOT / relative_inputs[3]).open(newline='') as handle:
        census = {(r['dataset'], r['rhs']): r for r in csv.DictReader(handle)}
    require(len(census) == len(tasks), 'Task/census mismatch')
    schemas = []
    for dataset, keys, rhs, rules in tasks:
        family = [frozenset(rule) for rule in rules]
        require(all(family), 'Empty determinant')
        require(all(all(0 <= j < len(keys) for j in rule) for rule in family), 'Bad key index')
        laminar = all(not a.intersection(b) or a <= b or b <= a
                      for a, b in combinations(family, 2))
        require(laminar, 'Nonlaminar E011 family: theorem does not force equality')
        row = census[(dataset, rhs)]
        schemas.append(dict(dataset=dataset, rhs=rhs, keys=keys, rules=rules, width=1,
                            rows=int(row['rows']), rejected=int(row['rejected']),
                            all_rejected_radii_equal_by_corollary=True))
    rejected = sum(row['rejected'] for row in schemas)
    require(rejected == historical_checks['rejected'], 'Rejected count mismatch')
    task_sizes = {(s['dataset'], s['rhs']): s['rows'] for s in schemas}

    with gzip.open(ROOT / relative_inputs[4], 'rt') as handle:
        pairs = [json.loads(line) for line in handle]
    require(len(pairs) == historical_checks['selected_rejected'], 'Solve count mismatch')
    derived = []
    old_exact = 0
    for pair in pairs:
        key = (pair['dataset'], pair['rhs'])
        require(key in task_sizes, 'Unknown solve task')
        fixed = pair['fixed']
        cost = fixed['cost']
        require(fixed['status'] == 0 and isinstance(cost, int) and cost > 0,
                'No archived fixed optimum')
        require(fixed['verification_errors'] == [] and abs(fixed['gap']) <= 1e-7,
                'Archived fixed certificate failure')
        require(abs(fixed['objective'] - cost) <= 1e-7
                and abs(fixed['dual_bound'] - cost) <= 1e-7, 'Archived optimum disagreement')
        require(abs(fixed['maximum_integrality_error']) <= 1e-7
                and abs(fixed['maximum_constraint_residual']) <= 1e-7, 'Archived feasibility failure')
        rhs_column = manifest['canonical_headers'][pair['dataset']].index(pair['rhs']) + 1
        edits = fixed['edits']
        require(len(edits) == cost and len({(r, c) for r, c, _ in edits}) == cost,
                'Archived edit cost mismatch')
        require(all(1 <= r <= task_sizes[key] and r != pair['row_index']
                    and c == rhs_column and value == 0 for r, c, value in edits),
                'Witness is not protected-target RHS-to-zero only')
        full = pair['full']
        if full['status'] == 0:
            require(full['cost'] == cost, 'Previously exact pair contradicts equality')
            old_exact += 1
        else:
            require(full['status'] == 1 and 'Time limit' in full['message'], 'Unexpected full status')
            require(full['cost'] is None and full['dual_bound'] is None, 'Unexpected timeout certificate')
            derived.append(dict(dataset=pair['dataset'], rhs=pair['rhs'],
                                row_index_one_based=pair['row_index'],
                                archived_full_solver_status=full['status'],
                                archived_full_solver_message=full['message'],
                                archived_fixed_optimum=cost, derived_full_optimum=cost,
                                inference='Corollary 4 equality plus archived certified fixed optimum',
                                fixed_edit_list_sha256=sha256(json.dumps(edits, separators=(',', ':')).encode()).hexdigest()))
    require(old_exact == historical_checks['selected_rejected_exact_pairs'], 'Exact pair count mismatch')
    source_cache = Path('/Users/mac/Library/Caches/InvariantAudit/E006-v1-20261022/source')
    result = dict(
        date='2026-11-05', classification='exploratory_post_result_analytical_reanalysis',
        theorem='experiments/E013-schema-width/theory.md, Corollary 4',
        theorem_sha256=digest(HERE / 'theory.md'), script_sha256=digest(Path(__file__)),
        frozen_input_sha256=hashes, schemas=schemas, rejected_targets_with_analytical_equality=rejected,
        archived_fixed_certificates_checked=len(pairs), previously_exact_pairs=old_exact,
        newly_deduced_full_optima=derived,
        source_cache_present_at_check=source_cache.exists(), source_rows_reconstructed=False,
        raw_source_witnesses_reverified=False, solver_runs=0, historical_timeout_records_modified=False,
        limitation='Numeric deductions rely on archived E011 fixed certificates and the internal E013 proof. '
                   'Only record structure, stored bounds and hashes are freshly checked; source votes are not replayed.',
    )
    output = HERE / 'results/e011-analytical-reanalysis.json'
    with output.open('x') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps(dict(schema_count=len(schemas), rejected_equal=rejected,
                          archived_fixed_checked=len(pairs), old_exact=old_exact,
                          deductions=[(d['row_index_one_based'], d['derived_full_optimum']) for d in derived])))


if __name__ == '__main__':
    main()
