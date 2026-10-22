"""One fixed nine-file acquisition; inspect CSV headers only."""
from concurrent.futures import ThreadPoolExecutor
import csv
from hashlib import sha256
import io
import json
from pathlib import Path
import subprocess
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path('/Users/mac/Library/Caches/InvariantAudit/E006-v1-20261022/source')
REVISION = '7be1334b8c7bbdac3f47ef514fb3e1e8c5fc181c'
ACQUISITION_LOCK = '0177cc2'
PROTOCOL = 'experiments/E006-external-reference-validation/acquisition-protocol.md'
MANIFEST = ROOT / 'data/E006-v1-source-manifest.json'
REPORT = ROOT / 'experiments/E006-external-reference-validation/results/source-acquisition-e006-20261022-001.md'
PATHS = tuple(f'datasets/{name}/{kind}.csv' for name in ('beers', 'flights', 'rayyan')
              for kind in ('dirty', 'clean')) + ('README.md', 'LICENSE.md', 'raha/dataset.py')
LIMIT = 20_000_000


def fetch(path):
    url = f'https://raw.githubusercontent.com/BigDaMa/raha/{REVISION}/{path}'
    with urllib.request.urlopen(url, timeout=40) as response:
        if response.status != 200 or response.url != url:
            raise ValueError('unexpected source response')
        content = response.read(LIMIT + 1)
    if len(content) > LIMIT:
        raise ValueError('source exceeds fixed limit')
    destination = SOURCE / path
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as stream:
        stream.write(content)
    if destination.read_bytes() != content:
        raise ValueError('cache write mismatch')
    return {'path': path, 'url': url, 'status': 200, 'bytes': len(content),
            'sha256': sha256(content).hexdigest()}


def run():
    if SOURCE.exists() or MANIFEST.exists() or REPORT.exists():
        raise ValueError('existing acquisition/cache; no retry')
    lock = subprocess.check_output(['git', 'rev-parse', ACQUISITION_LOCK], cwd=ROOT, text=True).strip()
    original = subprocess.check_output(['git', 'show', f'{lock}:{PROTOCOL}'], cwd=ROOT)
    if original != (ROOT / PROTOCOL).read_bytes():
        raise ValueError('acquisition protocol drift')
    subprocess.run(['git', 'merge-base', '--is-ancestor', lock, 'HEAD'], cwd=ROOT, check=True)
    SOURCE.mkdir(parents=True)
    try:
        with ThreadPoolExecutor(max_workers=6) as executor:
            files = list(executor.map(fetch, PATHS))
        headers = {}
        for name in ('beers', 'flights', 'rayyan'):
            pair = []
            for kind in ('dirty', 'clean'):
                with (SOURCE / f'datasets/{name}/{kind}.csv').open(encoding='utf-8', newline='') as stream:
                    header = next(csv.reader(stream, strict=True))
                if not header or any(not field for field in header) or len(set(header)) != len(header):
                    raise ValueError('invalid or duplicate header')
                pair.append(header)
            if pair[0] != pair[1]:
                raise ValueError('paired headers mismatch')
            headers[name] = pair[0]
        manifest = {'stage': 'E006-A1', 'status': 'valid_acquisition_metadata_only',
                    'source_repository': 'https://github.com/BigDaMa/raha',
                    'source_commit': REVISION, 'acquisition_protocol_commit': lock,
                    'acquisition_protocol_sha256': sha256(original).hexdigest(),
                    'implementation_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                    'source_root': str(SOURCE), 'files': files, 'headers': headers,
                    'csv_rows_or_reference_differences_inspected': False}
        content = (json.dumps(manifest, sort_keys=True, separators=(',', ':'), ensure_ascii=False) + '\n').encode()
        for destination in (SOURCE.parent / 'source-manifest.json', MANIFEST):
            with destination.open('xb') as stream:
                stream.write(content)
        digest = sha256(content).hexdigest()
        lines = ['# E006 external reference source acquisition', '', 'status: valid_acquisition_metadata_only',
                 f'acquisition_protocol_commit: {lock}', f'source_commit: {REVISION}',
                 f'manifest_sha256: {digest}', 'csv_rows_or_reference_differences_inspected: false',
                 'performance_result: absent', '', '## Header inventory', '']
        for name, header in headers.items():
            lines.append(f'- {name}: {json.dumps(header)}')
        lines += ['', 'Nine pinned files acquired; each HTTP response, byte count and hash is recorded',
                  'in data/E006-v1-source-manifest.json. Raw cells remain outside Git.',
                  'Only first logical CSV header records were parsed. No error rates, label differences,',
                  'row counts, method outputs or source examples were computed. Lock the evaluation',
                  'protocol before any table-row access. No source substitution or retry occurred.', '']
        with REPORT.open('x') as stream:
            stream.write('\n'.join(lines))
        return {'manifest_sha256': digest, 'headers': headers, 'files': len(files)}
    except BaseException:
        if not REPORT.exists():
            with REPORT.open('x') as stream:
                stream.write('# E006 invalid source acquisition\nstatus: invalid_acquisition\nNo evaluation evidence. Preserve downloaded bytes; no automatic retry.\n')
        raise


if __name__ == '__main__':
    print(json.dumps(run(), sort_keys=True, indent=2))
