"""Exercise the extracted companion and record scoped delivery evidence."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / 'paper/context-edit-stability-companion.zip'


def need(value, message):
    if not value:
        raise ValueError(message)


def main():
    scratch = Path(tempfile.mkdtemp(prefix='invariantaudit-companion-'))
    extracted = scratch / 'extracted'
    extracted.mkdir()
    manifest = json.loads((ROOT / 'reproducibility/stability/companion-manifest.json').read_text())
    expected = sorted(list(manifest['files'])+['reproducibility/stability/companion-manifest.json'])
    with zipfile.ZipFile(ARCHIVE) as archive:
        need(archive.namelist() == expected and archive.testzip() is None, 'ZIP membership/CRC')
        for name in archive.namelist():
            need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'Unsafe ZIP name')
            need(archive.read(name) == (ROOT / name).read_bytes(), f'ZIP member differs: {name}')
        archive.extractall(extracted)
    foreign = scratch / 'foreign-working-directory'
    foreign.mkdir()
    results = {}
    output = ROOT / 'reproducibility/stability/verification'
    output.mkdir(exist_ok=True)
    def invoke(label, base, flags=(), arguments=(), success=True):
        command = [sys.executable, '-I', '-S', *flags, str(base / 'reproducibility/stability/verify_companion.py'), *arguments]
        print(json.dumps(dict(stage=label, running=True)), flush=True)
        run = subprocess.run(command, cwd=foreign, capture_output=True, text=True, timeout=1800)
        if success:
            need(run.returncode == 0, f'{label}: {run.stderr}')
            parsed = json.loads(run.stdout)
            need(parsed['status'] == 'pass', label)
            (output / f'{label}.json').write_text(json.dumps(parsed, indent=2, sort_keys=True)+'\n')
            results[label] = dict(returncode=0, output_sha256=sha256((output / f'{label}.json').read_bytes()).hexdigest())
            return parsed
        need(run.returncode != 0 and 'ValueError' in run.stderr, f'Negative control did not reject: {label}')
        results[label] = dict(returncode=run.returncode, rejected=True, error=run.stderr.strip().splitlines()[-1])
        return run.stderr
    ordinary = invoke('isolated_offline', extracted)
    optimized = invoke('isolated_optimized', extracted, flags=('-O',))
    need(ordinary['source_outputs']['source_raw_decisions_checked'] is False
         and ordinary['raw_source_verification'] == 'not_checked_no_source_root', 'Offline overclaim')
    ordinary.pop('optimized_python'); optimized.pop('optimized_python')
    need(ordinary == optimized, '-O semantic mismatch')
    source_manifest = json.loads((ROOT / 'data/E006-v1-source-manifest.json').read_text())
    relocated = scratch / 'relocated-raha-source'
    original = Path(source_manifest['source_root'])
    for item in source_manifest['files']:
        target = relocated / item['path']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(original / item['path'], target)
    full = invoke('finite_and_relocated_source', extracted,
                  arguments=('--recheck-finite', '--source-root', str(relocated)))
    need(full['finite_reexecution']['E008_artifacts_reconstructed_byte_identically'] == 4
         and full['finite_reexecution']['E009_formula_cases_recomputed'] == 18779, 'Incomplete finite reproduction')
    need(full['raw_source_verification']['source_bytes_checked'] == 9
         and full['raw_source_verification']['raw_coordinate_witnesses_checked'] == 26453, 'Incomplete source check')
    altered = scratch / 'altered-member'
    shutil.copytree(extracted, altered)
    member = altered / 'data/E011-v1-summary.csv'
    member.write_bytes(member.read_bytes()+b'\n')
    error = invoke('tampered_member_optimized', altered, flags=('-O',), success=False)
    need('Member hash mismatch' in error, 'Wrong tamper rejection')
    unsafe = scratch / 'unsafe-manifest'
    shutil.copytree(extracted, unsafe)
    p = unsafe / 'reproducibility/stability/companion-manifest.json'
    m = json.loads(p.read_text()); m['files']['../outside'] = dict(bytes=0, sha256='0'*64)
    p.write_text(json.dumps(m))
    need('Unsafe member path' in invoke('unsafe_manifest_path', unsafe, success=False), 'Unsafe path not rejected')
    empty = scratch / 'empty-source'
    empty.mkdir()
    need('Missing/nonregular source' in invoke('missing_source_no_cache_fallback', extracted,
                                              arguments=('--source-root', str(empty)), success=False), 'Missing source not rejected')
    item = source_manifest['files'][0]
    changed = relocated / item['path']
    changed.write_bytes(changed.read_bytes()+b'\n')
    need('Source pin mismatch' in invoke('wrong_source_pin', extracted,
                                        arguments=('--source-root', str(relocated)), success=False), 'Wrong source pin not rejected')
    previous = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', '5fe6d32'], cwd=ROOT).decode().splitlines()
    preserve = [name for name in previous if name.startswith(('experiments/', 'data/', 'paper/', 'reproducibility/'))
                and name not in ('experiments/README.md', 'data/README.md', 'paper/README.md', 'paper/context-edit-stability/README.md', 'paper/context-edit-stability/owner-guide-vi.md')]
    for name in preserve:
        need((ROOT / name).read_bytes() == subprocess.check_output(['git', 'show', f'5fe6d32:{name}'], cwd=ROOT), f'Previous artifact changed: {name}')
    report = dict(date='2026-10-23', status='pass', scope='extracted_portable_companion_reproduction_integrity_and_preservation_self_review',
                  archive_sha256=sha256(ARCHIVE.read_bytes()).hexdigest(), archive_bytes=ARCHIVE.stat().st_size,
                  archive_members=len(expected), verifier_sha256=sha256((ROOT / 'reproducibility/stability/verify_companion.py').read_bytes()).hexdigest(),
                  tested_from_foreign_cwd=True, isolated_python_with_site_disabled=True, optimized_python_passes=True,
                  original_study_files_unchanged=len(preserve), original_MILP_or_timing_runs_reexecuted=False,
                  all_18779_formula_cases_rechecked=True, E008_four_artifacts_rebuilt_in_memory=True,
                  source_files_relocated_and_pinned=9, original_code_source_witnesses_checked=26453,
                  negative_controls_rejected=4, checks=results, independent_scientific_review=False,
                  proof_or_novelty_certification=False, actual_submission='absent')
    destination = ROOT / 'milestones/M31-delivery-verification.json'
    with destination.open('x') as f:
        json.dump(report, f, indent=2, sort_keys=True); f.write('\n')
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)


if __name__ == '__main__':
    main()
