"""Recover the exact recorded source bytes; never overwrite or substitute a shard."""
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
from hashlib import sha256
import audit

CACHE = Path("/Users/mac/Library/Caches/InvariantAudit/E003-v1-20260917")


def recover():
    # A repeated acquisition must be audited explicitly, not overwrite prior metadata.
    metadata_path = CACHE / "recovery-metadata.json"
    if metadata_path.exists():
        raise audit.AuditError("recovery metadata already exists")
    (CACHE / "source").mkdir(parents=True, exist_ok=True)
    entries = []
    for split, name, size, count, digest in audit.SOURCES:
        target = CACHE / "source" / name
        headers = CACHE / (name + ".headers")
        if target.exists() or headers.exists():
            raise audit.AuditError("acquisition target already exists")
        started = datetime.now(timezone.utc).isoformat()
        response = subprocess.run([
            "curl", "--fail", "--location", "--silent", "--show-error",
            "--connect-timeout", "20", "--max-time", "180", "--no-clobber",
            "--dump-header", str(headers), "--output", str(target),
            "--write-out", "%{http_code}", "https://data.gharchive.org/" + name,
        ], check=True, capture_output=True, text=True)
        finished = datetime.now(timezone.utc).isoformat()
        audit.verify_bytes(target.read_bytes(), size, digest)
        entries.append({"split": split, "filename": name, "sha256": digest,
                        "bytes": size, "record_count_pin": count,
                        "url": "https://data.gharchive.org/" + name,
                        "http_status": int(response.stdout), "started_at_utc": started,
                        "finished_at_utc": finished, "headers_file": headers.name,
                        "headers_sha256": sha256(headers.read_bytes()).hexdigest()})
        print(f"recovered {split}: compressed bytes/hash match", flush=True)
    manifest = audit.original_manifest()
    if sha256(manifest).hexdigest() != audit.MANIFEST_SHA256:
        raise audit.AuditError("reconstructed manifest digest differs")
    with (CACHE / "source-manifest.json").open("xb") as output:
        output.write(manifest)
    metadata = {"kind": "new_recovery_not_original_freeze", "files": entries,
                "source_manifest_sha256": audit.MANIFEST_SHA256,
                "format_and_counts": "to_be_verified_by_E004_before_result",
                "old_cache_restored": False, "network_after_recovery": False}
    with metadata_path.open("xb") as output:
        output.write(audit.canonical(metadata) + b"\n")
    print(json.dumps({"cache": str(CACHE), "manifest_sha256": audit.MANIFEST_SHA256}))


if __name__ == "__main__":
    recover()
