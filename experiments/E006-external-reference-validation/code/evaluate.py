"""Fixed external-reference diagnostic; rule decisions receive dirty strings only."""
from __future__ import annotations

from collections import Counter, defaultdict
import csv
from fractions import Fraction
from hashlib import sha256
import html
import io
import json
import re

import numpy as np

import point_reference

DATASETS = ('beers', 'flights', 'rayyan')
SPLITS = ('development', 'calibration', 'evaluation')
BASES = ('U', 'Rall', 'Rrhs', 'Rmode')
METHODS = tuple(item for base in BASES for item in (base, base + '-binary'))
METRICS = ('balanced_accuracy', 'fpr', 'fnr', 'brier', 'ece')
SPECS = {
    'beers': {'key': 'index', 'fds': (('brewery_id', 'brewery_name'), ('brewery_id', 'city'), ('brewery_id', 'state'))},
    'flights': {'key': 'tuple_id', 'fds': tuple(('flight', col) for col in ('sched_dep_time', 'act_dep_time', 'sched_arr_time', 'act_arr_time'))},
    'rayyan': {'key': 'id', 'fds': (('jounral_abbreviation', 'journal_title'),
                                   ('jounral_abbreviation', 'journal_issn'), ('journal_issn', 'journal_title'))},
}
BOOTSTRAP_REPLICATES = 10_000
TOLERANCE = 2e-12


class EvaluationError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise EvaluationError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False) + '\n').encode()


def normalize(value):
    return re.sub('[\t\n ]+', ' ', html.unescape(value)).strip('\t\n ')


def parse_table(content, headers):
    reader = csv.reader(io.StringIO(content.decode('utf-8'), newline=''), strict=True)
    actual = next(reader)
    require(actual == headers, 'header changed')
    rows = []
    for row in reader:
        if not row:
            continue
        require(len(row) == len(headers), 'ragged CSV table')
        rows.append(tuple(normalize(cell) for cell in row))
    return tuple(rows)


def validate_keys(headers, rows, key):
    require(bool(rows) and len(rows) >= 100, 'insufficient source rows')
    column = headers.index(key)
    keys = tuple(row[column] for row in rows)
    require(all(keys) and len(set(keys)) == len(keys), 'missing/duplicate alignment key')
    return keys


def components(dataset, headers, dirty, spec):
    keys = validate_keys(headers, dirty, spec['key'])
    parent = list(range(len(dirty)))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left, right):
        lroot, rroot = find(left), find(right)
        if lroot != rroot:
            parent[max(lroot, rroot)] = min(lroot, rroot)

    for determinant in sorted({left for left, _right in spec['fds']}):
        seen = {}
        column = headers.index(determinant)
        for index, row in enumerate(dirty):
            if row[column]:
                if row[column] in seen:
                    union(index, seen[row[column]])
                else:
                    seen[row[column]] = index
    members = defaultdict(list)
    for index in range(len(dirty)):
        members[find(index)].append(index)
    identities, splits = [None] * len(dirty), [None] * len(dirty)
    for indices in members.values():
        key = min(keys[index] for index in indices)
        identity = sha256(key.encode()).hexdigest()
        bucket = int(sha256(f'E006-v1|split|{dataset}|{key}'.encode()).hexdigest(), 16) % 4
        split = 'development' if bucket < 2 else 'calibration' if bucket == 2 else 'evaluation'
        for index in indices:
            identities[index], splits[index] = identity, split
    require(len({identities[indices[0]] for indices in members.values()}) == len(members), 'component identity collision')
    for split in ('calibration', 'evaluation'):
        require(len({identity for identity, assigned in zip(identities, splits) if assigned == split}) >= 8,
                'insufficient split components')
    for left, _right in spec['fds']:
        column = headers.index(left)
        seen = {}
        for row, split in zip(dirty, splits):
            if row[column]:
                require(row[column] not in seen or seen[row[column]] == split, 'determinant crosses splits')
                seen[row[column]] = split
    return tuple(identities), tuple(splits)


def score_dirty(dataset, headers, dirty, splits, spec):
    unary = np.zeros((len(dirty), len(headers)), dtype=np.int16)
    key_column = headers.index(spec['key'])
    for i, row in enumerate(dirty):
        for j, value in enumerate(row):
            if j == key_column:
                continue
            unary[i, j] += not value
            if dataset == 'beers' and headers[j] in ('brewery_id', 'state'):
                pattern = '[0-9]+' if headers[j] == 'brewery_id' else '[A-Za-z]{2}'
                unary[i, j] += re.fullmatch(pattern, value) is None
    scores = np.repeat(unary[:, :, None], len(BASES), axis=2)
    for left, right in spec['fds']:
        lhs, rhs = headers.index(left), headers.index(right)
        groups = defaultdict(list)
        for i, row in enumerate(dirty):
            if row[lhs]:
                groups[splits[i], row[lhs]].append(i)
        for indices in groups.values():
            counts = Counter(dirty[i][rhs] for i in indices)
            if len(counts) < 2:
                continue
            maximum = max(counts.values())
            modes = {value for value, count in counts.items() if count == maximum}
            for i in indices:
                scores[i, lhs, 1] += 1
                scores[i, rhs, 1] += 1
                scores[i, rhs, 2] += 1
                if len(modes) > 1 or dirty[i][rhs] not in modes:
                    scores[i, rhs, 3] += 1
    require(np.all(scores[:, key_column, :] == 0), 'alignment key entered decisions')
    scores.flags.writeable = False
    return scores


def fit_lookup(scores, labels):
    require(len(scores) == len(labels) and len(scores) > 0, 'missing calibration support')
    counts, positives = Counter(), Counter()
    for score, truth in zip(scores, labels):
        require(type(truth) is int and truth in (0, 1), 'invalid calibration truth')
        counts[int(score)] += 1
        positives[int(score)] += truth
    lookup = {score: Fraction(positives[score] + 1, count + 2) for score, count in counts.items()}
    fallback = Fraction(sum(positives.values()) + 1, sum(counts.values()) + 2)
    record = {'entries': [{'score': score, 'count': counts[score], 'positives': positives[score],
                           'numerator': lookup[score].numerator, 'denominator': lookup[score].denominator}
                          for score in sorted(counts)],
              'fallback': [fallback.numerator, fallback.denominator]}
    return lookup, fallback, record


def point_metrics(labels, decisions, probabilities):
    n = len(labels)
    require(n > 0, 'empty point scope')
    truth = np.asarray(labels, dtype=np.int64)
    decision = np.asarray(decisions, dtype=bool)
    probability = np.array([float(p) for p in probabilities])
    require(len(probability) == n and len(decision) == n, 'unaligned point input')
    require(np.all((truth == 0) | (truth == 1)) and np.all(np.isfinite(probability)) and
            np.all((0 <= probability) & (probability <= 1)), 'invalid point inputs')
    tp, tn = int(np.sum(decision & (truth == 1))), int(np.sum(~decision & (truth == 0)))
    fp, fn = int(np.sum(decision & (truth == 0))), int(np.sum(~decision & (truth == 1)))
    fpr = fp/(fp+tn) if fp+tn else None
    fnr = fn/(fn+tp) if fn+tp else None
    bins = np.array([min(9, int(p*10)) for p in probabilities])
    brier = float(np.mean((probability-truth)**2))
    ece = sum(abs(float(np.sum(probability[bins == b])-np.sum(truth[bins == b]))) for b in range(10))/n
    groups = defaultdict(lambda: [0, 0])
    for p, y in zip(probabilities, labels):
        groups[p][0] += 1
        groups[p][1] += int(y)
    prevalence = Fraction(int(truth.sum()), n)
    rel = sum(Fraction(count, n)*(p-Fraction(positive, count))**2 for p, (count, positive) in groups.items())
    res = sum(Fraction(count, n)*(Fraction(positive, count)-prevalence)**2 for count, positive in groups.values())
    unc = prevalence*(1-prevalence)
    residual = brier-float(rel-res+unc)
    require(abs(residual) <= 1e-12, 'Brier decomposition residual')
    result = {'support': n, 'positive_count': int(truth.sum()), 'negative_count': n-int(truth.sum()),
              'tp': tp, 'tn': tn, 'fp': fp, 'fn': fn, 'balanced_accuracy': (2-fpr-fnr)/2 if fpr is not None and fnr is not None else None,
              'fpr': fpr, 'fnr': fnr, 'brier': brier, 'ece': ece, 'reliability': float(rel),
              'resolution': float(res), 'uncertainty': float(unc), 'brier_identity_residual': residual}
    direct = point_reference.compute([int(y) for y in labels], [bool(d) for d in decisions], probabilities)
    largest = 0.0
    for field in ('support', 'tp', 'tn', 'fp', 'fn'):
        require(result[field] == direct[field], 'direct confusion audit disagreement')
    for field in METRICS:
        if direct[field] is None:
            require(result[field] is None, 'direct undefined metric disagreement')
        else:
            difference = abs(result[field]-float(direct[field]))
            require(difference <= TOLERANCE, 'direct point metric disagreement')
            largest = max(largest, difference)
    return result, largest


def bootstrap_index(dataset, replicate, position, cluster_count):
    require(dataset in DATASETS and replicate >= 0 and position >= 0 and cluster_count > 0, 'invalid bootstrap coordinate')
    return int(sha256(f'E006-v1|bootstrap|{dataset}|{replicate}|{position}'.encode()).hexdigest(), 16) % cluster_count


def sufficient_statistics(cluster_indices, labels, decisions, probabilities, cluster_count):
    stats = np.zeros((cluster_count, len(METHODS), 35))
    truth = np.asarray(labels, dtype=np.int64)
    for m in range(len(METHODS)):
        decision = decisions[:, m]
        fractions = probabilities[m]
        p = np.array([float(value) for value in fractions])
        bins = np.array([min(9, int(value*10)) for value in fractions])
        for column, values in enumerate((decision & (truth == 1), ~decision & (truth == 0),
                                         decision & (truth == 0), ~decision & (truth == 1), (p-truth)**2)):
            stats[:, m, column] = np.bincount(cluster_indices, weights=values, minlength=cluster_count)
        for b in range(10):
            mask = bins == b
            for offset, values in ((5, mask), (15, p*mask), (25, truth*mask)):
                stats[:, m, offset+b] = np.bincount(cluster_indices, weights=values, minlength=cluster_count)
    return stats


def metrics_from_totals(totals):
    tp, tn, fp, fn = (totals[:, :, i] for i in range(4))
    support = tp+tn+fp+fn
    fpr = np.divide(fp, tn+fp, out=np.full_like(fp, np.nan), where=(tn+fp) > 0)
    fnr = np.divide(fn, tp+fn, out=np.full_like(fn, np.nan), where=(tp+fn) > 0)
    return {'balanced_accuracy': (2-fpr-fnr)/2, 'fpr': fpr, 'fnr': fnr,
            'brier': totals[:, :, 4]/support,
            'ece': np.abs(totals[:, :, 15:25]-totals[:, :, 25:35]).sum(axis=2)/support}


def comparison_inventory():
    pairs = [(f'{left}-{right}', left, right, METRICS)
             for left, right in (('Rall', 'U'), ('Rrhs', 'U'), ('Rmode', 'U'), ('Rmode', 'Rall'))]
    pairs.extend((f'{base}-lookup-minus-binary', base, base+'-binary', ('brier', 'ece')) for base in BASES)
    return tuple((name, METHODS.index(left), METHODS.index(right), metric)
                 for name, left, right, metrics in pairs for metric in metrics)


def bootstrap(dataset, cell_components, labels, decisions, probabilities, *, replicates=BOOTSTRAP_REPLICATES):
    identities = sorted(set(cell_components))
    require(len(identities) >= 8 and replicates > 0, 'insufficient bootstrap support')
    index = {identity: i for i, identity in enumerate(identities)}
    cell_indices = np.array([index[identity] for identity in cell_components])
    stats = sufficient_statistics(cell_indices, labels, decisions, probabilities, len(identities))
    weights = np.zeros((replicates, len(identities)), dtype=np.int32)
    draw_hash = sha256()
    for r in range(replicates):
        draw = [bootstrap_index(dataset, r, j, len(identities)) for j in range(len(identities))]
        draw_hash.update((','.join(map(str, draw))+'\n').encode())
        weights[r] = np.bincount(draw, minlength=len(identities))
    totals = (weights @ stats.reshape(len(identities), -1)).reshape(replicates, len(METHODS), 35)
    metrics = metrics_from_totals(totals)
    blocks, intervals = [], []
    for name, left, right, metric in comparison_inventory():
        delta = metrics[metric][:, left]-metrics[metric][:, right]
        usable = delta[np.isfinite(delta)]
        if not len(usable):
            lower = upper = None
            status = 'undefined'
        else:
            lower, upper = (float(value) for value in np.quantile(usable, [.025, .975], method='linear'))
            status = 'partial' if len(usable) != replicates else 'degenerate' if lower == upper else 'valid'
        intervals.append({'dataset': dataset, 'pair': name, 'metric': metric, 'lower': lower, 'upper': upper,
                          'usable_replicates': len(usable), 'replicates': replicates, 'status': status})
        blocks.append((name, metric, delta))
    diversity = {method: len({stats[i, m].tobytes() for i in range(len(identities))})
                 for m, method in enumerate(METHODS)}
    return tuple(blocks), intervals, {'draws_sha256': draw_hash.hexdigest(), 'components': len(identities),
                                      'statistic_signatures_float64': diversity}


def evaluate_dataset(dataset, headers, dirty, reference_reader, *, replicates=BOOTSTRAP_REPLICATES):
    spec = SPECS[dataset]
    keys = validate_keys(headers, dirty, spec['key'])
    component_ids, splits = components(dataset, headers, dirty, spec)
    scores = score_dirty(dataset, headers, dirty, splits, spec)
    raw_hash = sha256(canonical({'headers': headers, 'components': component_ids, 'splits': splits}) +
                      scores.astype('<i2').tobytes()).hexdigest()
    reference = reference_reader()
    require(len(reference) == len(dirty), 'paired row count mismatch')
    reference_keys = validate_keys(headers, reference, spec['key'])
    require(reference_keys == keys, 'paired stable row-key mismatch')
    columns = [j for j in range(len(headers)) if headers[j] != spec['key']]
    cells = [(i, j) for i in range(len(dirty)) for j in columns]
    assignments = tuple(splits[i] for i, _j in cells)
    cell_components = tuple(component_ids[i] for i, _j in cells)
    raw = np.array([scores[i, j, :] for i, j in cells], dtype=np.int16)
    calibration_indices = [k for k, (i, _j) in enumerate(cells) if splits[i] == 'calibration']
    calibration_truth = [int(dirty[cells[k][0]][cells[k][1]] == reference[cells[k][0]][cells[k][1]])
                         for k in calibration_indices]
    probabilities, lookups = [], {}
    decisions = np.zeros((len(cells), len(METHODS)), dtype=bool)
    for m, base in enumerate(BASES):
        lookup, fallback, record = fit_lookup(raw[calibration_indices, m], calibration_truth)
        lookups[base] = record
        decisions[:, 2*m] = decisions[:, 2*m+1] = raw[:, m] == 0
        probabilities.extend((tuple(lookup.get(int(s), fallback) for s in raw[:, m]),
                              tuple(Fraction(int(decision)) for decision in decisions[:, 2*m])))
    lookup_hash = sha256(canonical(lookups)).hexdigest()
    labels = np.array([int(dirty[i][j] == reference[i][j]) for i, j in cells], dtype=np.int64)
    require(set(labels[k] for k, split in enumerate(assignments) if split == 'evaluation') == {0, 1},
            'evaluation lacks a truth class')
    endpoints = {column for fd in spec['fds'] for column in fd}
    metrics, maximum_audit_error, scope_counts = [], 0.0, {}
    for split in SPLITS:
        for scope in ('all_cells', 'fd_columns'):
            indices = [k for k, (i, j) in enumerate(cells) if splits[i] == split and
                       (scope == 'all_cells' or headers[j] in endpoints)]
            scope_counts[split+':'+scope] = len(indices)
            for m, method in enumerate(METHODS):
                result, error = point_metrics([int(labels[k]) for k in indices], decisions[indices, m],
                                              tuple(probabilities[m][k] for k in indices))
                maximum_audit_error = max(maximum_audit_error, error)
                metrics.append({'dataset': dataset, 'split': split, 'scope': scope, 'method': method, **result})
    evaluation_indices = [k for k, split in enumerate(assignments) if split == 'evaluation']
    blocks, intervals, bootstrap_checks = bootstrap(
        dataset, tuple(cell_components[k] for k in evaluation_indices), labels[evaluation_indices],
        decisions[evaluation_indices], tuple(tuple(p[k] for k in evaluation_indices) for p in probabilities),
        replicates=replicates)
    checks = {'source_rows': len(dirty), 'source_columns': len(headers), 'evaluated_columns': len(columns),
              'cell_count': len(cells), 'scope_counts': scope_counts,
              'raw_scores_sha256_before_reference_read': raw_hash, 'calibration_lookups_sha256': lookup_hash,
              'calibration_lookups': lookups, 'point_audit_max_difference': maximum_audit_error,
              'alignment': 'paired_unique_stable_keys_equal_at_each_position',
              'reference_loaded_after_raw_score_freeze': True, 'bootstrap': bootstrap_checks,
              'split_counts': {split: {'rows': sum(s == split for s in splits),
                            'components': len({component_ids[i] for i, s in enumerate(splits) if s == split}),
                            'valid_cells': int(sum(labels[k] for k, s in enumerate(assignments) if s == split)),
                            'invalid_cells': int(sum(1-labels[k] for k, s in enumerate(assignments) if s == split))}
                              for split in SPLITS}}
    return {'dataset': dataset, 'cells': cells, 'assignments': assignments, 'components': cell_components,
            'raw': raw, 'labels': labels, 'probabilities': tuple(probabilities), 'decisions': decisions,
            'metrics': metrics, 'blocks': blocks, 'intervals': intervals, 'checks': checks}
