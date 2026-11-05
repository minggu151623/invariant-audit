"""Replay frozen E012 cases without Git or third-party dependencies."""
from hashlib import sha256
import importlib.util
from itertools import combinations_with_replacement
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
E012 = HERE / 'E012'
if not E012.exists():
    E012 = HERE.parents[1] / 'experiments/E012-acceptance-complexity'


def main():
    source = E012 / 'verify_reduction.py'
    saved = json.loads((E012 / 'results.json').read_text())
    if sha256(source.read_bytes()).hexdigest() != saved['implementation_sha256']:
        raise ValueError('Frozen implementation changed')
    if sha256((E012 / 'protocol.md').read_bytes()).hexdigest() != saved['protocol_sha256']:
        raise ValueError('Frozen protocol changed')
    spec = importlib.util.spec_from_file_location('e012_frozen', source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    expected_inputs = [(q, list(sets)) for q in range(1, 4) for size in range(1, 4)
                       for sets in combinations_with_replacement(range(1 << q), size)
                       if module.union(sets) == (1 << q) - 1]
    actual_inputs = [(record['q'], record['set_masks']) for record in saved['cases']]
    module.need(actual_inputs == expected_inputs and len(actual_inputs) == 111,
                'Stored input grid differs')
    totals = module.Counter()
    for record in saved['cases']:
        q, sets = record['q'], record['set_masks']
        rows = module.construct(q, sets)
        module.need(rows == record['table'], 'Constructed table differs')
        initial = module.counts(rows, q)
        module.need(initial == record['initial_counts'] and all(a == b and a > 0 for a,b in initial),
                    'Initial counts differ or are not tied')
        cover = module.minimum_cover(q, sets)
        module.need(list(cover) == record['cover_witness']
                    and len(cover) == record['cover_optimum'], 'Cover optimum differs')
        forward = [row.copy() for row in rows]
        for i in cover:
            forward[i + 1][q] = 0
        module.need(module.accepts(forward, q)
                    and len(module.changed_cells(rows, forward)) == len(cover),
                    'Forward witness failed')
        for mode in ('fixed', 'full'):
            fresh = module.enumerate_destinations(q, sets, rows, mode == 'fixed')
            module.need(json.loads(json.dumps(fresh)) == record[mode], 'Raw replay differs')
            for field in ('evaluated', 'accepting', 'accepting_with_key_edits',
                          'accepting_with_support_edits', 'accepting_with_zero_to_one_rhs_edits'):
                totals[mode + '_' + field] += fresh[field]
    module.need(dict(totals) == saved['totals'] and saved['all_predictions_match']
                and saved['failure'] is None, 'Stored totals/outcome differ')
    print(json.dumps(dict(cases=111, radii=222, destinations=147523,
                         exact_replay=True, new_scientific_replication=False)))


if __name__ == '__main__':
    main()
