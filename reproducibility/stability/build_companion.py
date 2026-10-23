"""Build a fixed allowlist of structural-preprint evidence, excluding raw CSVs."""
from hashlib import sha256
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS = {
    'E008-mutable-key-certificates': 'e008-20261023-001',
    'E009-singleton-characterization': 'e009-20261023-001',
    'E010-directional-scaling': 'e010-20261023-001',
    'E011-reused-source-stability': 'e011-20261023-001',
}
FILES = [
    'reproducibility/stability/plan.md', 'reproducibility/stability/README.md',
    'reproducibility/stability/verify_companion.py', 'reproducibility/stability/build_companion.py',
    'reproducibility/stability/claims.json',
    'experiments/E007-fd-decision-stability/protocol.md',
    'experiments/E007-fd-decision-stability/code/certificate.py',
    'data/E006-v1-source-manifest.json',
    'literature/structural-theorem-comparison-20261023.md',
    'literature/mutable-key-novelty-20261023.md', 'literature/singleton-collision-20261023.md',
    'literature/novelty-reset-20261023.md', 'literature/novelty-sources-20261023.json',
    'paper/context-edit-stability/main.tex', 'paper/context-edit-stability/README.md',
    'paper/context-edit-stability/owner-guide-vi.md', 'paper/context-edit-stability/render-verification.json',
    'paper/context-edit-stability/prepare_fields.py', 'paper/context-edit-stability/submission-fields-draft.json',
    'paper/context-edit-stability/abstract.txt', 'paper/context-edit-stability/submission-guide-vi.md',
    'paper/context-edit-stability-preview.pdf', 'paper/context-edit-stability-source.zip',
]
for experiment, run in EXPERIMENTS.items():
    folder = ROOT / 'experiments' / experiment
    FILES.extend([f'experiments/{experiment}/protocol.md', f'experiments/{experiment}/results/run-{run}.md'])
    FILES.extend(str(p.relative_to(ROOT)) for p in sorted((folder / 'code').glob('*.py')))
    for name in ('theory.md', 'analysis.md', 'sparse-rivals-proof.md', 'verify_delivery.py'):
        if (folder / name).is_file():
            FILES.append(str((folder / name).relative_to(ROOT)))
for prefix in ('E008', 'E009', 'E010', 'E011'):
    FILES.extend(str(p.relative_to(ROOT)) for p in sorted((ROOT / 'data').glob(f'{prefix}-v1-*')))
for path in ('milestones/M26-E008-mutable-key-pilot.md', 'milestones/M26-delivery-verification.json',
             'milestones/M27-E009-singleton-characterization.md', 'milestones/M27-delivery-verification.json',
             'milestones/M28-E010-directional-scaling.md', 'milestones/M28-delivery-verification.json',
             'milestones/M29-E011-source-stability.md', 'milestones/M29-delivery-verification.json',
             'milestones/M30-structural-preprint-draft.md'):
    FILES.append(path)
FILES = sorted(FILES)
if len(FILES) != len(set(FILES)):
    raise ValueError('Duplicate allowlist member')
manifest = dict(schema_version=1, date='2026-10-23', scope='portable_structural_preprint_evidence_not_new_solver_or_timing_run',
                manuscript_baseline='M30 at 5fe6d32', source_CSVs_included=False,
                independent_scientific_review=False, files={})
for relative in FILES:
    p = ROOT / relative
    if not p.is_file() or p.is_symlink():
        raise ValueError(f'Nonregular/missing member: {relative}')
    payload = p.read_bytes()
    manifest['files'][relative] = dict(bytes=len(payload), sha256=sha256(payload).hexdigest())
manifest_name = 'reproducibility/stability/companion-manifest.json'
(ROOT / manifest_name).write_text(json.dumps(manifest, indent=2, sort_keys=True)+'\n')
destination = ROOT / 'paper/context-edit-stability-companion.zip'
with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
    for relative in sorted(FILES+[manifest_name]):
        info = zipfile.ZipInfo(relative, date_time=(2026, 10, 23, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, (ROOT / relative).read_bytes())
with zipfile.ZipFile(destination) as archive:
    if archive.testzip() is not None or archive.namelist() != sorted(FILES+[manifest_name]):
        raise ValueError('ZIP membership/CRC failure')
print(json.dumps(dict(path=str(destination), members=len(FILES)+1, bytes=destination.stat().st_size,
                      sha256=sha256(destination.read_bytes()).hexdigest()), indent=2))
