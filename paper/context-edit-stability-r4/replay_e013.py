"""Read-only replay of the frozen E013 records (Python standard library only).

Run from an extracted R4 supplement:   python3 -I -S replay_e013.py
Add --reenumerate to repeat the frozen raw enumeration of every grid with the
archived implementation and compare it with the stored case records line by
line. Nothing is written to disk in either mode.

The record checks below are written separately from the archived code: they
decode rows, count votes, compute Hamming costs and widths directly. They are
delivery checks of the same finite cases, not new research evidence.
"""
from collections import Counter
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, product
import gzip
import importlib.util
import io
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
E013 = HERE / 'E013'
if not E013.is_dir():  # running inside the research repository
    E013 = HERE.parent.parent / 'experiments' / 'E013-schema-width'
RESULTS = E013 / 'results'


def need(ok, detail):
    if not ok:
        raise SystemExit('REPLAY FAILURE: ' + str(detail))


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def width_of(q, rules):
    """Largest inclusion antichain among rules containing a common key."""
    best = 0
    for j in range(q):
        incident = [r for r in rules if r >> j & 1]
        for size in range(len(incident), best, -1):
            if any(all(a & b not in (a, b) for a, b in combinations(c, 2))
                   for c in combinations(incident, size)):
                best = size
                break
    return best


def laminar(rules):
    return all(not a & b or a & b in (a, b) for a, b in combinations(rules, 2))


def accepts(rows, rules, d):
    for rule in rules:
        votes = [0] * d
        votes[0] = 1  # protected all-zero target
        for row in rows:
            if all(row[j] == 0 for j in range(len(row) - 1) if rule >> j & 1):
                votes[row[-1]] += 1
        if votes[0] <= max(votes[1:]):
            return False
    return True


def hamming(a, b):
    return sum(x != y for ra, rb in zip(a, b) for x, y in zip(ra, rb))


def main():
    summary = json.loads((RESULTS / 'summary.json').read_text())
    need(summary['all_predictions_match'] and summary['failure'] is None, 'Stored run failed')
    need(digest(E013 / 'protocol.md') == summary['protocol_sha256'], 'Protocol hash')
    need(digest(E013 / 'verify_width.py') == summary['implementation_sha256'], 'Code hash')
    need(digest(RESULTS / 'cases.jsonl.gz') == summary['case_records_sha256'], 'Cases hash')

    grids = {tuple(g['grid']): g for g in summary['grids']}
    alphabets = {key: [tuple(r) for r in g['row_alphabet']] for key, g in grids.items()}
    for (q, k, d, n), alphabet in alphabets.items():
        need(alphabet == list(product(*([range(k)] * q + [range(d)]))), 'Alphabet order')

    # Which (source, family) pairs must appear: every initially rejected pair.
    expected = {}
    for (q, k, d, n), alphabet in alphabets.items():
        families = range(1, 1 << ((1 << q) - 1))
        for source in combinations_with_replacement(range(len(alphabet)), n):
            rows = [alphabet[i] for i in source]
            for family in families:
                rules = [r for r in range(1, 1 << q) if family >> (r - 1) & 1]
                if not accepts(rows, rules, d):
                    expected[(q, k, d, n, source, family)] = False

    totals = Counter()
    per_grid = Counter()
    with gzip.open(RESULTS / 'cases.jsonl.gz', 'rt', encoding='utf-8') as stream:
        for line in stream:
            rec = json.loads(line)
            q, k, d, n = rec['grid']
            alphabet = alphabets[(q, k, d, n)]
            key = (q, k, d, n, tuple(rec['source']), rec['family'])
            need(key in expected and not expected[key], ('Unexpected or repeated pair', key))
            expected[key] = True
            rules = [r for r in range(1, 1 << q) if rec['family'] >> (r - 1) & 1]
            w = width_of(q, rules)
            need(w == rec['width'] and (w == 1) == laminar(rules), ('Width', key))
            before = [alphabet[i] for i in rec['source']]
            full_cost, fixed_cost = rec['full'][0], rec['fixed'][0]
            full = [alphabet[i] for i in rec['full'][1]]
            fixed = [alphabet[i] for i in rec['fixed'][1]]
            conv = [alphabet[i] for i in rec['converted']]
            need(hamming(before, full) == full_cost and accepts(full, rules, d), ('Full', key))
            need(hamming(before, fixed) == fixed_cost and accepts(fixed, rules, d)
                 and all(a[:-1] == b[:-1] for a, b in zip(before, fixed)), ('Fixed', key))
            need(accepts(conv, rules, d) and all(a[:-1] == b[:-1] for a, b in zip(before, conv))
                 and hamming(before, conv) <= rec['conversion']['weighted_bound']
                 <= w * full_cost, ('Converted', key))
            need(1 <= full_cost <= fixed_cost <= w * full_cost, ('Ratio', key))
            need(w > 1 or full_cost == fixed_cost, ('Laminar equality', key))
            totals['rejected_pairs_checked'] += 1
            totals['laminar_pairs_checked'] += w == 1
            totals['strict_key_gains'] += fixed_cost > full_cost
            totals['conversion_imports'] += rec['conversion']['imports']
            totals['conversion_replacement_flips'] += rec['conversion']['replacement_flips']
            per_grid[(q, k, d, n)] += 1
    need(all(expected.values()), 'Some rejected pair has no record')
    for key in totals:
        need(totals[key] == summary['totals'][key], ('Total', key))
    for key, g in grids.items():
        need(per_grid[key] == g['totals']['rejected_pairs_checked'], ('Grid count', key))

    for c in summary['construction_checks']:
        q, rules, w = c['q'], c['rules'], c['width']
        rows = [tuple(r) for r in c['context_rows']]
        need(width_of(q, rules) == w, 'Construction width')
        need(not accepts(rows, rules, 2), 'Construction initially accepts')
        for i, a in enumerate(c['antichain']):
            members = [r for r in rows if all(r[j] == 0 for j in range(q) if a >> j & 1)]
            need(members == [rows[i]] and rows[i][-1] == 1, 'Critical group not isolated')
        for witness, cost in ((c['full_witness'], 1), (c['fixed_witness'], w)):
            witness = [tuple(r) for r in witness]
            need(hamming(rows, witness) == cost and accepts(witness, rules, 2), 'Construction witness')
        need(all(a[:-1] == b[:-1] for a, b in zip(rows, map(tuple, c['fixed_witness']))),
             'Construction fixed witness changes keys')

    report = dict(totals=dict(totals), constructions=len(summary['construction_checks']),
                  hashes_match=True, reenumerated=False)
    if '--reenumerate' in sys.argv:
        spec = importlib.util.spec_from_file_location('frozen_e013', E013 / 'verify_width.py')
        frozen = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(frozen)
        buffer = io.StringIO()
        for (q, k, d, n) in grids:
            frozen.run_grid(q, k, d, n, buffer)
        with gzip.open(RESULTS / 'cases.jsonl.gz', 'rt', encoding='utf-8') as stream:
            need(buffer.getvalue() == stream.read(), 'Re-enumeration differs from records')
        report['reenumerated'] = True
    print(json.dumps(report, indent=2, sort_keys=True))
    print('E013 replay passed.')


if __name__ == '__main__':
    main()
