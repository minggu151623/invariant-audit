"""Pinned CSV parsing and deterministic task encodings; no reference in scoring."""
import csv
from hashlib import sha256
import html
import io
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = 'data/E006-v1-source-manifest.json'
MANIFEST_SHA = '96e7529355eac100de47f2c957b8a1a5252d4c220c285d5fd46d871d62716342'
TASKS = (('beers', ('brewery_id',), 'brewery_name', ((0,),)),
         ('beers', ('brewery_id',), 'city', ((0,),)),
         ('beers', ('brewery_id',), 'state', ((0,),)),
         ('flights', ('flight',), 'sched_dep_time', ((0,),)),
         ('flights', ('flight',), 'act_dep_time', ((0,),)),
         ('flights', ('flight',), 'sched_arr_time', ((0,),)),
         ('flights', ('flight',), 'act_arr_time', ((0,),)),
         ('rayyan', ('jounral_abbreviation',), 'journal_issn', ((0,),)),
         ('rayyan', ('jounral_abbreviation', 'journal_issn'), 'journal_title', ((0,), (1,))))
ALIGNMENT = dict(beers='index', flights='tuple_id', rayyan='id')


def payloads():
    content = (ROOT / MANIFEST).read_bytes()
    if sha256(content).hexdigest() != MANIFEST_SHA:
        raise ValueError('Manifest pin drift')
    manifest = json.loads(content)
    source = Path('/Users/mac/Library/Caches/InvariantAudit/E006-v1-20261022/source')
    if (source.parent / 'source-manifest.json').read_bytes() != content:
        raise ValueError('External manifest drift')
    values = {}
    for item in manifest['files']:
        b = (source / item['path']).read_bytes()
        if len(b) != item['bytes'] or sha256(b).hexdigest() != item['sha256']:
            raise ValueError(f'Source drift: {item["path"]}')
        values[item['path']] = b
    if len(values) != 9:
        raise ValueError('Source inventory drift')
    return manifest, values


def parse(payload, expected, aliases=None):
    reader = csv.reader(io.StringIO(payload.decode('utf-8'), newline=''), strict=True)
    header = next(reader)
    header = [(aliases or {}).get(h, h) for h in header]
    if header != expected:
        raise ValueError('Header mismatch')
    rows = []
    for row in reader:
        if not row:
            continue
        if len(row) != len(header):
            raise ValueError('Ragged source')
        rows.append(tuple(re.sub('[\t\n ]+', ' ', html.unescape(v)).strip('\t\n ') for v in row))
    key = header.index(ALIGNMENT[next(d for d in ALIGNMENT if ALIGNMENT[d] in header)])
    ids = [row[key] for row in rows]
    if len(rows) < 100 or not all(ids) or len(set(ids)) != len(ids):
        raise ValueError('Alignment key/size failure')
    return tuple(rows)


def dirty_tasks(manifest, payload):
    tables = {d: parse(payload[f'datasets/{d}/dirty.csv'], manifest['canonical_headers'][d]) for d in ALIGNMENT}
    tasks = []
    for dataset, keys, rhs, rules in TASKS:
        header = manifest['canonical_headers'][dataset]
        columns = tuple(header.index(c) for c in keys+(rhs,))
        original = tables[dataset]
        vocab = [sorted({row[j] for row in original}) for j in columns]
        mappings = [{value: i for i, value in enumerate(values)} for values in vocab]
        encoded = tuple(tuple(mapping[row[j]] for mapping, j in zip(mappings, columns)) for row in original)
        tasks.append(dict(dataset=dataset, rhs=rhs, columns=columns, key_columns=keys,
                          rules=rules, encoded=encoded, sizes=tuple(max(2, len(v)) for v in vocab)))
    return tables, tasks


def target_table(task, target):
    source = task['encoded']
    order = (target,)+tuple(i for i in range(len(source)) if i != target)
    values = source[target]
    def swap(v, j):
        return 0 if v == values[j] else values[j] if v == 0 else v
    table = tuple(tuple(swap(v, j) for j, v in enumerate(source[i])) for i in order)
    return table, order


def coordinate_result(task, table, order, result):
    public = {key: value for key, value in result.items() if key not in
              ('witness', 'total_seconds', 'build_seconds', 'solve_seconds')}
    public['edits'] = None if result['witness'] is None else [
        (order[i]+1, task['columns'][j]+1, after)
        for i, (old, new) in enumerate(zip(table, result['witness']))
        for j, (before, after) in enumerate(zip(old, new)) if before != after]
    return public


def references(manifest, payload, dirty):
    result = {}
    for d in ALIGNMENT:
        aliases = manifest['beers_clean_header_aliases'] if d == 'beers' else None
        clean = parse(payload[f'datasets/{d}/clean.csv'], manifest['canonical_headers'][d], aliases)
        if len(clean) != len(dirty[d]):
            raise ValueError('Reference shape mismatch')
        j = manifest['canonical_headers'][d].index(ALIGNMENT[d])
        if any(a[j] != b[j] for a, b in zip(dirty[d], clean)):
            raise ValueError('Reference alignment mismatch')
        result[d] = clean
    return result
