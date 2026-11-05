"""E013 raw-coordinate oracles and constructive exchange checks (stdlib only)."""
from collections import Counter
from functools import lru_cache
import gzip
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def need(ok, detail):
    if not ok:
        raise ValueError(detail)


def subset(a, b):
    return a & b == a


def comparable(a, b):
    return subset(a, b) or subset(b, a)


def zero_mask(row):
    return sum(1 << j for j, value in enumerate(row[:-1]) if value == 0)


def distance(a, b):
    return sum(x != y for ra, rb in zip(a, b) for x, y in zip(ra, rb))


def group_counts(rows, rule, d):
    counts = [0] * d
    counts[0] = 1
    for row in rows:
        if subset(rule, zero_mask(row)):
            counts[row[-1]] += 1
    return counts


def margins(rows, rules, d):
    result = []
    for rule in rules:
        counts = group_counts(rows, rule, d)
        result.extend(counts[0] - counts[v] for v in range(1, d))
    return result


def decision_mask(rows, q, d):
    result = 0
    for rule in range(1, 1 << q):
        c = group_counts(rows, rule, d)
        if c[0] > max(c[1:]):
            result |= 1 << (rule - 1)
    return result


def normalize(before, after):
    result = []
    for original, destination in zip(before, after):
        if original[-1] != 0 and destination[-1] == original[-1]:
            if original[:-1] == destination[:-1]:
                result.append(tuple(original))
            else:
                result.append(tuple(original[:-1]) + (0,))
        else:
            result.append(tuple(0 if a == 0 or b == 0 else a
                                for a, b in zip(original[:-1], destination[:-1])) + (0,))
    return result


@lru_cache(None)
def antichain(items):
    for size in range(len(items), -1, -1):
        for chosen in combinations(items, size):
            if all(not comparable(a, b) for a, b in combinations(chosen, 2)):
                return chosen


@lru_cache(None)
def chain_partition(items):
    if not items:
        return ()
    first = items[0]
    best = None
    for size in range(len(items)):
        for rest in combinations(items[1:], size):
            chain = (first,) + rest
            if not all(comparable(a, b) for a, b in combinations(chain, 2)):
                continue
            remaining = tuple(x for x in items if x not in chain)
            candidate = (chain,) + chain_partition(remaining)
            if best is None or len(candidate) < len(best):
                best = candidate
    return best


def schema_info(q, rules):
    chains = []
    widths = []
    witnesses = []
    for j in range(q):
        incident = tuple(r for r in rules if r & (1 << j))
        ac = antichain(incident)
        partition = chain_partition(incident)
        need(len(ac) == len(partition), 'Independent width/chain count mismatch')
        flat = [r for chain in partition for r in chain]
        need(sorted(flat) == sorted(incident) and len(set(flat)) == len(flat), 'Not a partition')
        need(all(all(comparable(a,b) for a,b in combinations(c,2)) for c in partition),
             'Non-chain in partition')
        chains.append(partition)
        widths.append(len(ac))
        witnesses.append(ac)
    laminar = all(not (a & b) or comparable(a,b) for a,b in combinations(rules,2))
    need((max(widths) == 1) == laminar, 'Width/laminar equivalence failed')
    return dict(rules=rules, widths=widths, width=max(widths), chains=chains,
                antichains=witnesses, laminar=laminar)


def convert(before, destination, info, d):
    rules = info['rules']
    normalized = normalize(before, destination)
    need(distance(before, normalized) <= distance(before, destination), 'Normalization cost')
    need(all(a >= b for a,b in zip(margins(normalized,rules,d), margins(destination,rules,d))),
         'Normalization margin domination')
    reference = [tuple(row[:-1]) + (end[-1],) for row,end in zip(before,normalized)]
    simulated = [list(row) for row in reference]
    rhs_cost = sum(a[-1] != b[-1] for a,b in zip(before,normalized))
    bound = rhs_cost
    imports = flips = 0
    for row, end in enumerate(normalized):
        for j in range(len(end)-1):
            if simulated[row][j] == end[j]:
                continue
            need(simulated[row][-1] == 0 and end[j] == 0, 'Non-monotone key action')
            prior = zero_mask(simulated[row])
            simulated[row][j] = 0
            posterior = zero_mask(simulated[row])
            affected = {r for r in rules if not subset(r,prior) and subset(r,posterior)}
            imports += 1
            bound += info['widths'][j]
            for chain in info['chains'][j]:
                eligible = [r for r in chain if r in affected
                            and any(v[-1] != 0 and subset(r,zero_mask(v)) for v in reference)]
                if not eligible:
                    continue
                smallest_group_rule = max(eligible, key=int.bit_count)
                index = next(i for i,v in enumerate(reference)
                             if v[-1] != 0 and subset(smallest_group_rule,zero_mask(v)))
                reference[index] = reference[index][:-1] + (0,)
                flips += 1
            need(all(min(a,1) >= min(b,1) for a,b in
                     zip(margins(reference,rules,d), margins(simulated,rules,d))),
                 dict(reason='Capped margin invariant', before=before, destination=destination,
                      rules=rules, reference=reference, simulated=simulated))
    need(all(x >= 1 for x in margins(reference,rules,d)), 'Converted table rejects')
    need(all(a[:-1] == b[:-1] for a,b in zip(before,reference)), 'Converted keys changed')
    need(distance(before,reference) <= bound <= info['width'] * distance(before,destination),
         'Exchange cost bound fails')
    return reference, dict(imports=imports, replacement_flips=flips, weighted_bound=bound)


def normalization_check(q, k, d):
    rows = list(product(*([range(k)]*q + [range(d)])))
    rules = tuple(range(1,1 << q))
    count = 0
    for a,b in product(rows,repeat=2):
        c = normalize([a],[b])
        need(distance([a],c) <= distance([a],[b]), 'Single-row normalization cost')
        need(all(x >= y for x,y in zip(margins(c,rules,d),margins([b],rules,d))),
             dict(reason='Single-row domination', original=a, raw=b, normalized=c))
        count += 1
    return count


def construction(q, info):
    width = info['width']
    key = info['widths'].index(width)
    ac = info['antichains'][key]
    def row(mask, rhs):
        return tuple(0 if mask & (1 << j) else 1 for j in range(q)) + (rhs,)
    rows = [row(a,1) for a in ac]
    rows.append(row(((1 << q)-1) ^ (1 << key),0))
    for rule in info['rules']:
        if not any(subset(a,rule) for a in ac):
            rows.extend([row(rule,0)] * width)
    for index,a in enumerate(ac):
        matching = [i for i,r in enumerate(rows) if subset(a,zero_mask(r))]
        need(matching == [index] and rows[index][-1] == 1, 'Critical group not isolated tie')
    initial = {rule:group_counts(rows,rule,2) for rule in info['rules']}
    need(all(c[0] > c[1] for rule,c in initial.items() if rule not in ac),
         'Non-critical group rejects')
    full = list(rows)
    full[width] = tuple(0 for _ in range(q+1))
    fixed = [r[:-1]+(0,) if i < width else r for i,r in enumerate(rows)]
    need(distance(rows,full) == 1 and all(x >= 1 for x in margins(full,info['rules'],2)),
         'Cost-one construction fails')
    need(distance(rows,fixed) == width and all(x >= 1 for x in margins(fixed,info['rules'],2)),
         'Cost-width construction fails')
    return dict(q=q,rules=info['rules'],key=key,width=width,antichain=ac,
                context_rows=rows,initial_counts=initial,full_witness=full,fixed_witness=fixed,
                full_optimum=1,fixed_optimum=width,
                lower_bound_type='distinct_isolated_critical_groups_not_raw_enumeration')


def run_grid(q,k,d,n,stream):
    alphabet = list(product(*([range(k)]*q+[range(d)])))
    lookup = {r:i for i,r in enumerate(alphabet)}
    all_destinations = list(product(range(len(alphabet)),repeat=n))
    raw_masks = [decision_mask([alphabet[i] for i in dest],q,d) for dest in all_destinations]
    distinct_masks = sorted(set(raw_masks))
    distances = [[sum(x != y for x,y in zip(a,b)) for b in alphabet] for a in alphabet]
    schemas = [(family,schema_info(q,tuple(r for r in range(1,1 << q)
                                         if family & (1 << (r-1)))))
               for family in range(1,1 << ((1 << q)-1))]
    eligible = {f:[m for m in distinct_masks if m & f == f] for f,_ in schemas}
    totals = Counter()
    for original in combinations_with_replacement(range(len(alphabet)),n):
        before = [alphabet[i] for i in original]
        initial = decision_mask(before,q,d)
        full_best = {}
        for destination,mask in zip(all_destinations,raw_masks):
            cost = sum(distances[a][b] for a,b in zip(original,destination))
            if mask not in full_best or cost < full_best[mask][0]:
                full_best[mask] = (cost,destination)
        fixed_best = {}
        for values in product(range(d),repeat=n):
            after = [r[:-1]+(v,) for r,v in zip(before,values)]
            mask = decision_mask(after,q,d)
            cost = distance(before,after)
            if mask not in fixed_best or cost < fixed_best[mask][0]:
                fixed_best[mask] = (cost,tuple(lookup[r] for r in after))
        totals['source_tables'] += 1
        totals['full_raw_destinations'] += len(all_destinations)
        totals['fixed_raw_destinations'] += d**n
        for family,info in schemas:
            if initial & family == family:
                totals['initially_accepted_pairs_skipped'] += 1
                continue
            full_cost,full_codes = min(full_best[m] for m in eligible[family])
            fixed_cost,fixed_codes = min(value for m,value in fixed_best.items() if m & family == family)
            need(1 <= full_cost <= fixed_cost <= info['width']*full_cost,
                 dict(reason='Exact ratio bound',q=q,k=k,d=d,n=n,source=original,
                      family=family,full=full_cost,fixed=fixed_cost,width=info['width']))
            full_rows = [alphabet[i] for i in full_codes]
            fixed_rows = [alphabet[i] for i in fixed_codes]
            need(distance(before,full_rows)==full_cost and decision_mask(full_rows,q,d)&family==family,
                 'Full optimum witness failed')
            need(distance(before,fixed_rows)==fixed_cost and decision_mask(fixed_rows,q,d)&family==family
                 and all(a[:-1]==b[:-1] for a,b in zip(before,fixed_rows)), 'Fixed witness failed')
            converted,detail = convert(before,full_rows,info,d)
            totals['rejected_pairs_checked'] += 1
            totals['laminar_pairs_checked'] += info['laminar']
            totals['strict_key_gains'] += fixed_cost > full_cost
            totals['conversion_imports'] += detail['imports']
            totals['conversion_replacement_flips'] += detail['replacement_flips']
            stream.write(json.dumps(dict(grid=[q,k,d,n],source=list(original),family=family,
                                        width=info['width'],full=[full_cost,list(full_codes)],
                                        fixed=[fixed_cost,list(fixed_codes)],
                                        converted=[lookup[r] for r in converted],conversion=detail),
                                    separators=(',',':'))+'\n')
    return dict(grid=[q,k,d,n],row_alphabet=alphabet,totals=dict(totals))


def main():
    output = HERE / 'results'
    output.mkdir(exist_ok=True)
    need(not (output/'summary.json').exists(), 'Preserve previous run; output already exists')
    report = dict(date='2026-11-05',experiment='E013',python=sys.version,
                  protocol_sha256=sha256((HERE/'protocol.md').read_bytes()).hexdigest(),
                  implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  implementation_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=HERE,text=True).strip(),
                  classification='confirmatory_finite_checks_not_universal_proof_or_novelty_certificate',
                  grids=[],normalization_checks=[],construction_checks=[],failure=None)
    try:
        configs = [(q,2,2) for q in (1,2,3)] + [(3,2,3),(2,3,3)]
        for q,k,d in configs:
            report['normalization_checks'].append(dict(q=q,k=k,d=d,checked=normalization_check(q,k,d)))
        with gzip.open(output/'cases.jsonl.gz','wt',encoding='utf-8') as stream:
            for q,k,d in configs:
                for n in range(1,4 if d==2 else 3):
                    result = run_grid(q,k,d,n,stream)
                    report['grids'].append(result)
                    print(json.dumps(result['totals'] | dict(grid=result['grid'])),flush=True)
        for q in (1,2,3):
            for family in range(1,1 << ((1 << q)-1)):
                rules = tuple(r for r in range(1,1 << q) if family & (1 << (r-1)))
                report['construction_checks'].append(construction(q,schema_info(q,rules)))
        extra = [(4,(1,2,4,8)),(4,tuple(range(1,16))),
                 (4,tuple(sorted({3,5,9,1,15,2}))),
                 (5,tuple(sorted({1|sum(1 << j for j in pair) for pair in combinations(range(1,5),2)}
                                 | {1,31,2})))]
        for q,rules in extra:
            report['construction_checks'].append(construction(q,schema_info(q,rules)))
        report['all_predictions_match'] = True
    except Exception as exc:
        report['failure'] = str(exc)
        report['all_predictions_match'] = False
    totals = Counter()
    for grid in report['grids']:
        totals.update(grid['totals'])
    report['totals'] = dict(totals)
    report['case_records_sha256'] = sha256((output/'cases.jsonl.gz').read_bytes()).hexdigest() if (output/'cases.jsonl.gz').exists() else None
    (output/'summary.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(all_predictions_match=report['all_predictions_match'],failure=report['failure'],
                         totals=dict(totals),constructions=len(report['construction_checks'])),indent=2))
    if report['failure']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
