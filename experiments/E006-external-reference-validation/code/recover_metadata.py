"""Apply only the locked Beers header aliases; inspect no CSV data rows."""
import csv
from hashlib import sha256
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / 'experiments/E006-external-reference-validation'
SOURCE = Path('/Users/mac/Library/Caches/InvariantAudit/E006-v1-20261022/source')
REVISION = '7be1334b8c7bbdac3f47ef514fb3e1e8c5fc181c'
ALIASES = {'beer-name': 'beer_name', 'brewery-name': 'brewery_name'}


def run():
    destinations = (SOURCE.parent / 'source-manifest.json', ROOT / 'data/E006-v1-source-manifest.json')
    report = EXP / 'results/source-recovery-e006-20261022-002.md'
    if any(p.exists() for p in (*destinations, report)):
        raise ValueError('existing recovery outputs')
    lock = subprocess.check_output(['git', 'rev-parse', 'd83c5aa'], cwd=ROOT, text=True).strip()
    for path in ('acquisition-amendment-a2.md', 'source-pins-a2.json'):
        relative = (EXP / path).relative_to(ROOT).as_posix()
        original = subprocess.check_output(['git', 'show', f'{lock}:{relative}'], cwd=ROOT)
        if original != (EXP / path).read_bytes():
            raise ValueError('metadata recovery lock drift')
    subprocess.run(['git', 'merge-base', '--is-ancestor', lock, 'HEAD'], cwd=ROOT, check=True)
    inventory = json.loads((EXP / 'source-pins-a2.json').read_text())
    for item in inventory['files']:
        content = (SOURCE / item['path']).read_bytes()
        if len(content) != item['bytes'] or sha256(content).hexdigest() != item['sha256']:
            raise ValueError('pinned original bytes mismatch')
    headers, canonical = {}, {}
    for name in ('beers', 'flights', 'rayyan'):
        headers[name] = {}
        for kind in ('dirty', 'clean'):
            with (SOURCE / f'datasets/{name}/{kind}.csv').open(encoding='utf-8', newline='') as stream:
                header = next(csv.reader(stream, strict=True))
            headers[name][kind] = header
        dirty, clean = headers[name]['dirty'], headers[name]['clean']
        mapped = [ALIASES.get(h, h) for h in clean] if name == 'beers' else clean
        if dirty != mapped or not dirty or any(not h for h in dirty) or len(set(dirty)) != len(dirty):
            raise ValueError('unexpected paired header mismatch')
        canonical[name] = dirty
    manifest = {'stage': 'E006-A2', 'status': 'valid_metadata_recovery_A1_still_invalid',
                'source_repository': 'https://github.com/BigDaMa/raha', 'source_commit': REVISION,
                'source_root': str(SOURCE), 'acquisition_lock': '0177cc2', 'recovery_lock': lock,
                'files': [dict(item, url=f"https://raw.githubusercontent.com/BigDaMa/raha/{REVISION}/{item['path']}")
                          for item in inventory['files']], 'original_headers': headers,
                'canonical_headers': canonical, 'beers_clean_header_aliases': ALIASES,
                'csv_rows_or_reference_differences_inspected': False,
                'A1_result': 'source-acquisition-e006-20261022-001.md',
                'implementation_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}
    content = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()
    for destination in destinations:
        with destination.open('xb') as stream:
            stream.write(content)
    text = ('# E006 metadata recovery\n\nstatus: valid_metadata_recovery\n'
            f'recovery_lock: {lock}\nmanifest_sha256: {sha256(content).hexdigest()}\n'
            'A1_status: preserved_invalid\ncsv_rows_or_reference_differences_inspected: false\n'
            'performance_evidence: absent\n\nNine original files match locked hashes. Only the two predeclared\n'
            'Beers header aliases were applied to metadata. Raw CSV bytes were not\n'
            'changed, re-downloaded or traversed as data rows. Evaluation requires\n'
            'a separate protocol lock. This is author verification, not independent review.\n')
    with report.open('x') as stream:
        stream.write(text)
    return {'sha256': sha256(content).hexdigest(), 'headers': canonical}


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
