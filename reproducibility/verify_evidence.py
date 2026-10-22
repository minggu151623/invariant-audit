"""Verify the extracted review bundle without Git, NumPy or a TeX installation."""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]


def load_module(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verify_inventory():
    manifest = json.loads((ROOT / 'reproducibility/bundle-manifest.json').read_text())
    for relative, pin in manifest['files'].items():
        path = ROOT / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f'Missing or symlinked bundle member: {relative}')
        content = path.read_bytes()
        if len(content) != pin['bytes'] or sha256(content).hexdigest() != pin['sha256']:
            raise ValueError(f'Bundle member hash mismatch: {relative}')
    return len(manifest['files'])


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: the historical delivery audit requires assertions.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-root', type=Path,
                        help='Optional directory containing the nine original Raha files at manifest paths')
    options = parser.parse_args()
    members = verify_inventory()
    audit = load_module('e005_audit', 'experiments/E005-benchmark-evidence-audit/code/audit.py')
    checks = json.loads((ROOT / 'data/E005-v1-checks.json').read_text())
    rebuilt = audit.build(ROOT, checks['protocol_commit'], checks['implementation_commit'])
    for relative, content in rebuilt.items():
        if content != (ROOT / relative).read_bytes():
            raise ValueError(f'E005 reconstructed artifact differs: {relative}')
    code = ROOT / 'experiments/E006-external-reference-validation/code'
    sys.path.insert(0, str(code))
    verifier = load_module('e006_verifier', str(code.relative_to(ROOT) / 'verify_delivery.py'))
    result = verifier.run(source_root=options.source_root,
                          verify_sources=options.source_root is not None)
    print(json.dumps({
        'status': 'pass', 'bundle_members_hash_verified': members,
        'E005_artifacts_reconstructed_byte_identically': len(rebuilt),
        'E005_point_metric_comparisons': 195,
        'E006_delivery_verification': result,
        'E006_source_bytes_status': 'nine_pins_verified' if options.source_root else 'not_checked_no_source_root',
        'verification_scope': 'frozen_evidence_arithmetic_and_integrity_not_new_performance_run',
        'independent_scientific_review': False,
    }, ensure_ascii=False, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
