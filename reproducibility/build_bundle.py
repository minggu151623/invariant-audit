"""Package a fixed, explicit research-evidence inventory; exclude raw source CSVs."""
from hashlib import sha256
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    'reproducibility/README.md', 'reproducibility/verify_evidence.py',
    'reproducibility/build_bundle.py',
    'experiments/E005-benchmark-evidence-audit/protocol.md',
    'experiments/E005-benchmark-evidence-audit/code/audit.py',
    'experiments/E005-benchmark-evidence-audit/results/run-e005-20261022-001.md',
    'experiments/E006-external-reference-validation/protocol.md',
    'experiments/E006-external-reference-validation/code/point_reference.py',
    'experiments/E006-external-reference-validation/code/verify_delivery.py',
    'experiments/E006-external-reference-validation/results/run-e006-20261022-001.md',
    'milestones/M18-arxiv-evidence-audit.md',
    'milestones/M20-external-reference-results.md',
    'milestones/M20-delivery-verification.json',
    'milestones/M21-external-reference-manuscript.md',
    'paper/main.md', 'paper/arxiv-preview.pdf', 'paper/arxiv-source-draft.zip',
    'paper/render-verification.json', 'paper/submission-metadata.json',
    'paper/owner-review-vi.md', 'paper/review-status.md',
]
for experiment in ('E001', 'E002'):
    FILES.extend([f'data/{experiment}-v1-predictions.jsonl', f'data/{experiment}-v1-metrics.csv'])
for pattern in ('E005-v1-*', 'E006-v1-*'):
    FILES.extend(str(path.relative_to(ROOT)) for path in sorted((ROOT / 'data').glob(pattern)))
FILES = sorted(FILES)
assert len(FILES) == len(set(FILES))
manifest = {'schema_version': 1, 'date': '2026-10-23',
            'scope': 'owner_review_evidence_bundle_not_full_experiment_reexecution',
            'scientific_baseline': 'M20 at 5adbb14', 'manuscript_baseline': 'M21 at a31d01b',
            'independent_scientific_review': False, 'files': {}}
for relative in FILES:
    path = ROOT / relative
    assert path.is_file() and not path.is_symlink(), relative
    content = path.read_bytes()
    manifest['files'][relative] = {'bytes': len(content), 'sha256': sha256(content).hexdigest()}
manifest_path = 'reproducibility/bundle-manifest.json'
(ROOT / manifest_path).write_text(json.dumps(manifest, sort_keys=True, indent=2)+'\n')
destination = ROOT / 'paper/evidence-review-bundle.zip'
with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for relative in sorted(FILES + [manifest_path]):
        info = zipfile.ZipInfo(relative, date_time=(2026, 10, 23, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, (ROOT / relative).read_bytes())
with zipfile.ZipFile(destination) as archive:
    assert archive.testzip() is None
print(json.dumps({'path': str(destination), 'bytes': destination.stat().st_size,
                  'sha256': sha256(destination.read_bytes()).hexdigest(),
                  'members': len(FILES)+1}, indent=2))
