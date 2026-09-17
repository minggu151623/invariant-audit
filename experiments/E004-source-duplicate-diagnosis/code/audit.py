"""E004-v1 aggregate source diagnosis. No E003 imports or performance scoring."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, groupby
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import zlib

ROOT = Path(__file__).resolve().parents[3]
PROTOCOL_PATH = "experiments/E004-source-duplicate-diagnosis/protocol.md"
PROTOCOL_COMMIT = "1bf1a4a9a7f73c0ce1cc7aad4e4c74eaf3e03c51"
PROTOCOL_SHA256 = "51cf34b8ca31e96e44a8b1f5b779817fd68de96e38060d4b81e2dd435b4688bb"
MANIFEST_SHA256 = "683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633"
SOURCES = (
    ("development", "2019-01-15-12.json.gz", 29278679, 67145,
     "ae451576f78417d75f135b29ee67ea8e666dc5f6cb16e78cef04e20342b42b50"),
    ("calibration", "2020-01-15-12.json.gz", 46372480, 90940,
     "624a0d2a2fc575afb1e63bece53521e2b078ddfd1caf60026e313ad36d83cddd"),
    ("confirmatory", "2021-01-15-12.json.gz", 61805367, 117780,
     "a4a80c97153c691866d52b7e06ea0051f2449f0c6f8060dad9f441a69cd13788"),
)
CATEGORIES = (
    "raw_identical_to_first", "canonical_only_identical_to_first",
    "canonical_different_from_first",
)
DEFINITIONS = {
    CATEGORIES[0]: "Extra occurrence with raw line SHA-256 equal to first occurrence",
    CATEGORIES[1]: "Raw line differs but full canonical JSON SHA-256 equals first occurrence",
    CATEGORIES[2]: "Full canonical JSON SHA-256 differs from first occurrence",
    "duplicate_extra_occurrences": "nonempty records minus unique canonical event IDs",
    "conflict_id_groups": "ID groups with more than one full canonical JSON digest",
}


class AuditError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def original_manifest():
    return canonical({"protocol_id": "E003-v1", "files": [
        {"split": s, "filename": n, "bytes": b, "jsonl_lines": c,
         "sha256": h, "url": "https://data.gharchive.org/" + n}
        for s, n, b, c, h in SOURCES]}) + b"\n"


def verify_bytes(data, size, digest):
    if len(data) != size or sha256(data).hexdigest() != digest:
        raise AuditError("source compressed size/hash mismatch")


def decompress(data):
    decoder = zlib.decompressobj(16 + zlib.MAX_WBITS)
    try:
        plain = decoder.decompress(data) + decoder.flush()
    except zlib.error as error:
        raise AuditError("malformed gzip") from error
    if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:
        raise AuditError("truncated gzip or trailing data")
    return plain


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise AuditError("duplicate JSON object key")
        result[key] = value
    return result


def reject_constant(value):
    raise AuditError("non-finite JSON constant")


def id_key(value):
    if type(value) is int and value >= 0:
        return str(value)
    if type(value) is str and re.fullmatch(r"(?:0|[1-9][0-9]*)", value):
        return value
    raise AuditError("invalid event ID")


def records(plain, expected_count):
    rows = []
    # Split only at JSONL LF delimiters; preserve original physical line numbers.
    for line_number, raw in enumerate(plain.split(b"\n"), 1):
        raw = raw.rstrip(b"\r")
        if not raw.strip():
            continue
        try:
            obj = json.loads(raw.decode("utf-8"), object_pairs_hook=object_pairs,
                             parse_constant=reject_constant)
            if not isinstance(obj, dict) or type(obj.get("type")) is not str:
                raise AuditError("record must be object with event type")
            key = id_key(obj.get("id"))
            normal = canonical(obj)
        except (ValueError, UnicodeError, RecursionError) as error:
            raise AuditError(f"invalid source object at line {line_number}") from error
        rows.append((key, line_number, sha256(raw).hexdigest(),
                     sha256(normal).hexdigest(), obj["type"]))
    if len(rows) != expected_count:
        raise AuditError("source record count mismatch")
    return rows


def aggregate_dictionary(rows):
    groups = {}
    counts = Counter({name: 0 for name in CATEGORIES})
    extras_by_type = Counter()
    first_collision = None
    for key, line, raw, normal, kind in rows:
        if key not in groups:
            groups[key] = {"first": (line, raw, normal), "n": 1,
                           "digests": {normal}, "types": {kind}}
            continue
        group = groups[key]
        first_line, first_raw, first_normal = group["first"]
        if first_collision is None:
            first_collision = [first_line, line]
        group["n"] += 1
        group["digests"].add(normal)
        group["types"].add(kind)
        counts[CATEGORIES[0] if raw == first_raw else
               CATEGORIES[1] if normal == first_normal else CATEGORIES[2]] += 1
        extras_by_type[kind] += 1
    conflicts = [g for g in groups.values() if len(g["digests"]) > 1]
    return {
        "records": len(rows), "unique_ids": len(groups),
        "duplicate_extra_occurrences": len(rows) - len(groups),
        "duplicate_id_groups": sum(g["n"] > 1 for g in groups.values()),
        "conflict_id_groups": len(conflicts),
        "occurrence_categories": dict(counts),
        "maximum_multiplicity": max((g["n"] for g in groups.values()), default=0),
        "first_collision_lines": first_collision,
        "duplicate_extras_by_type": dict(sorted(extras_by_type.items())),
        "conflict_groups_touching_selected_types": {
            t: sum(t in g["types"] for g in conflicts)
            for t in ("IssuesEvent", "PullRequestEvent")},
    }


def aggregate_sorted(rows):
    # Independent grouping/counting path; never calls the dictionary aggregator.
    ordered = sorted(rows, key=lambda r: (r[0], r[1]))
    sizes, conflicts, categories, extras, candidates = [], [], [0, 0, 0], [], []
    for _, members in groupby(ordered, key=lambda r: r[0]):
        group = list(members)
        sizes.append(len(group))
        if len({r[3] for r in group}) > 1:
            conflicts.append({r[4] for r in group})
        if len(group) > 1:
            candidates.append((group[1][1], group[0][1]))
        for row in group[1:]:
            extras.append(row[4])
            if row[2] == group[0][2]:
                categories[0] += 1
            elif row[3] == group[0][3]:
                categories[1] += 1
            else:
                categories[2] += 1
    earliest = min(candidates) if candidates else None
    return {
        "records": sum(sizes), "unique_ids": len(sizes),
        "duplicate_extra_occurrences": sum(n - 1 for n in sizes),
        "duplicate_id_groups": len([n for n in sizes if n > 1]),
        "conflict_id_groups": len(conflicts),
        "occurrence_categories": dict(zip(CATEGORIES, categories)),
        "maximum_multiplicity": max(sizes, default=0),
        "first_collision_lines": [earliest[1], earliest[0]] if earliest else None,
        "duplicate_extras_by_type": dict(sorted(Counter(extras).items())),
        "conflict_groups_touching_selected_types": {
            t: len([types for types in conflicts if t in types])
            for t in ("IssuesEvent", "PullRequestEvent")},
    }


def cross_shard_overlap(by_split):
    result = {}
    for a, b in combinations(by_split, 2):
        dictionary_count = len({r[0] for r in by_split[a]} & {r[0] for r in by_split[b]})
        tagged = sorted([(r[0], a) for r in by_split[a]] +
                        [(r[0], b) for r in by_split[b]])
        sorted_count = sum(len({tag for _, tag in rows}) > 1
                           for _, rows in groupby(tagged, key=lambda x: x[0]))
        if dictionary_count != sorted_count:
            raise AuditError("cross-shard differential verification failed")
        result[a + "__" + b] = dictionary_count
    return result


def git(*args, root=ROOT):
    return subprocess.check_output(["git", *args], cwd=root).decode().strip()


def gate(root=ROOT, lock=PROTOCOL_COMMIT, digest=PROTOCOL_SHA256):
    if git("status", "--porcelain=v1", "--untracked-files=all", root=root):
        raise AuditError("dirty worktree")
    head = git("rev-parse", "HEAD", root=root)
    if subprocess.run(["git", "merge-base", "--is-ancestor", lock, head],
                      cwd=root, capture_output=True).returncode:
        raise AuditError("protocol lock not ancestor")
    committed = subprocess.check_output(["git", "show", f"{lock}:{PROTOCOL_PATH}"], cwd=root)
    if (root / PROTOCOL_PATH).read_bytes() != committed or sha256(committed).hexdigest() != digest:
        raise AuditError("protocol identity drift")
    return head


def publish_pair(json_path, report_path, encoded, markdown):
    if json_path.exists() or report_path.exists():
        raise AuditError("output already exists")
    # Exclusive creation and owned-file cleanup; result Markdown is finalized last.
    made = []
    try:
        for path, content in ((json_path, encoded), (report_path, markdown)):
            with path.open("xb") as output:
                made.append(path)
                output.write(content)
                output.flush()
                os.fsync(output.fileno())
    except BaseException:
        for path in reversed(made):
            path.unlink()
        raise


def execute(run_id, cache):
    if not re.fullmatch(r"e004-[0-9]{8}-[0-9]{3}", run_id):
        raise AuditError("invalid run ID")
    datetime.strptime(run_id[5:13], "%Y%m%d")
    implementation = gate()
    result_dir = ROOT / "experiments/E004-source-duplicate-diagnosis/results"
    json_path, md_path = result_dir / f"{run_id}.json", result_dir / f"{run_id}.md"
    if json_path.exists() or md_path.exists():
        raise AuditError("output already exists")
    cache = cache.resolve()
    if cache == ROOT or ROOT in cache.parents:
        raise AuditError("raw cache must remain outside repository")
    manifest = (cache / "source-manifest.json").read_bytes()
    if manifest != original_manifest() or sha256(manifest).hexdigest() != MANIFEST_SHA256:
        raise AuditError("manifest mismatch")
    # Check every payload before parsing any source content.
    for _, name, size, _, digest in SOURCES:
        verify_bytes((cache / "source" / name).read_bytes(), size, digest)
    by_split, summaries = {}, {}
    for split, name, size, count, digest in SOURCES:
        compressed = (cache / "source" / name).read_bytes()
        verify_bytes(compressed, size, digest)
        rows = records(decompress(compressed), count)
        a, b = aggregate_dictionary(rows), aggregate_sorted(rows)
        if a != b:
            raise AuditError("dictionary/sorted differential verification failed")
        if sum(a["occurrence_categories"].values()) != a["duplicate_extra_occurrences"]:
            raise AuditError("category accounting mismatch")
        summaries[split] = {"filename": name, "bytes": size, "sha256": digest, **a}
        by_split[split] = rows
        print(f"verified {split}: {count} records", flush=True)
    overlap = cross_shard_overlap(by_split)
    conflict_count = sum(s["conflict_id_groups"] for s in summaries.values())
    result = {
        "protocol_id": "E004-v1", "protocol_commit": PROTOCOL_COMMIT,
        "protocol_sha256": PROTOCOL_SHA256, "implementation_commit": implementation,
        "run_id": run_id, "status": "valid_source_diagnostic_only",
        "classification": "exploratory_followup_to_M13",
        "python": platform.python_version(), "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_manifest_sha256": MANIFEST_SHA256,
        "definitions": DEFINITIONS, "sources": summaries,
        "cross_shard_shared_id_groups": overlap,
        "validation": {"source_pins": "pass", "counts_and_json": "pass",
                       "dictionary_sort_differential": "pass", "clean_tree_and_lock": "pass"},
        "interpretation": ("conflicting_full_objects_require_separate_policy" if conflict_count
                           else "first_occurrence_collapse_candidate_on_these_shards_only"),
        "limitations": ["known prior duplicate counts; exploratory source diagnosis",
                        "shared parser and single-agent differential check; no independent reviewer",
                        "no delivery-mechanism causal inference", "no E003 performance or H3 evidence",
                        "finite three-shard inventory; no population generalization"],
        "public_claim_eligibility": False,
    }
    encoded = canonical(result) + b"\n"
    lines = [f"# E004 source diagnosis — {run_id}", "",
             f"Status: {result['status']}. Exploratory follow-up to M13.",
             f"Protocol: E004-v1, commit {PROTOCOL_COMMIT}, SHA-256 {PROTOCOL_SHA256}.",
             f"Implementation: {implementation}. Python: {result['python']}.",
             f"Manifest SHA-256: {MANIFEST_SHA256}.",
             f"Aggregate JSON SHA-256: {sha256(encoded).hexdigest()}.", "",
             "| Split | Records | Unique IDs | Extra occurrences | Duplicate groups | Conflict groups | Raw identical | Canonical only | Different canonical | Max multiplicity |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for split, s in summaries.items():
        cats = s["occurrence_categories"]
        vals = [s[k] for k in ("records", "unique_ids", "duplicate_extra_occurrences",
                              "duplicate_id_groups", "conflict_id_groups")]
        vals += [cats[k] for k in CATEGORIES] + [s["maximum_multiplicity"]]
        lines.append("| " + split + " | " + " | ".join(map(str, vals)) + " |")
    lines += ["", "## Sources and first collisions", ""]
    for split, s in summaries.items():
        lines += [f"- {split}: {s['filename']}, {s['bytes']} bytes, SHA-256 {s['sha256']}; "
                  f"first collision lines: {s['first_collision_lines']}; "
                  f"duplicate extras by type: {json.dumps(s['duplicate_extras_by_type'], sort_keys=True)}; "
                  f"conflict groups touching selected types: {json.dumps(s['conflict_groups_touching_selected_types'], sort_keys=True)}."]
    lines += ["", "## Definitions and verification", ""]
    lines += [f"- {key}: {value}." for key, value in DEFINITIONS.items()]
    lines += ["", f"Cross-shard shared ID groups: {json.dumps(overlap, sort_keys=True)}.",
              "All source pins, strict parsing/counts, protocol ancestry and clean-tree gates passed.",
              "Dictionary and separate sorted aggregation match exactly; this is single-agent",
              "differential verification with a shared parser, not independent reviewer acceptance.",
              "", "## Interpretation and limitations", "", result["interpretation"] + ".", ""]
    lines += ["- " + item + "." for item in result["limitations"]]
    lines += ["", "E003-v1 remains invalid. No performance result or H3 outcome. public_claim_eligibility=false."]
    markdown = ("\n".join(lines) + "\n").encode()
    # Recheck tree and inputs at finalization, without rerunning the analysis.
    if gate() != implementation:
        raise AuditError("HEAD changed during audit")
    if (cache / "source-manifest.json").read_bytes() != manifest:
        raise AuditError("manifest changed during audit")
    for _, name, size, _, digest in SOURCES:
        verify_bytes((cache / "source" / name).read_bytes(), size, digest)
    result_dir.mkdir(parents=True, exist_ok=True)
    publish_pair(json_path, md_path, encoded, markdown)
    return {"status": result["status"], "json": str(json_path), "report": str(md_path)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--cache", type=Path, required=True)
    options = parser.parse_args()
    try:
        print(json.dumps(execute(options.run_id, options.cache)))
    except (AuditError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(json.dumps({"status": "failed_no_diagnostic_result", "reason": str(error)}))
        raise SystemExit(2)
