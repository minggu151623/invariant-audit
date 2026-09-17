# E004-v1 — Duplicate structure in the frozen E003 source shards

## Identity, authority and provenance

Protocol date: 2026-09-17. Dedicated lock subject:
`research(protocol): lock E004 duplicate structure diagnosis`.
Protocol commit must precede implementation and result commits. The committed
protocol is immutable. Local CPU, standard library only; no paid API/GPU.
User authorized continued research in this conversation on 2026-09-17.
The design below is AI-suggested, not a user-selected technical design.
No recursive delegation, publication, public messages or E003 performance run.

This is an exploratory diagnostic follow-up to M13, not a fresh confirmatory
test: the previous investigation already reported 537 duplicate occurrences in
2021 and zero in 2019/2020. Their payload equivalence has not been established.
The original external temporary cache/manifest is currently absent. E003-v1 and
its invalid report remain unchanged; E004 cannot retroactively validate it.

## Question and decision rule

Are repeated canonical event IDs associated with identical full record bytes,
equivalent JSON objects with different formatting, or conflicting full objects?
Report all three categories and multiplicities, including excluded event types.
This does not identify the upstream cause and does not evaluate B0/M1 or H3.

If every duplicate ID group has one full canonical JSON digest, first-occurrence
collapse is a candidate policy for these particular shards, with no evidence of
content ambiguity under this equivalence definition. Any conflicting group
requires a separately designed policy (e.g. reject/quarantine the whole group);
do not choose a preferred payload here. A conflict-free result still does not
prove a production deduplication policy safe or a delivery mechanism causal.

## Fixed source inventory and recovery

Recover exactly the following URLs with HTTP GET, no source substitution:

| Split | URL | Bytes | Nonempty JSONL records | SHA-256 of compressed bytes |
| --- | --- | ---: | ---: | --- |
| development | https://data.gharchive.org/2019-01-15-12.json.gz | 29278679 | 67145 | ae451576f78417d75f135b29ee67ea8e666dc5f6cb16e78cef04e20342b42b50 |
| calibration | https://data.gharchive.org/2020-01-15-12.json.gz | 46372480 | 90940 | 624a0d2a2fc575afb1e63bece53521e2b078ddfd1caf60026e313ad36d83cddd |
| confirmatory | https://data.gharchive.org/2021-01-15-12.json.gz | 61805367 | 117780 | a4a80c97153c691866d52b7e06ea0051f2449f0c6f8060dad9f441a69cd13788 |

Store raw payloads outside Git under a durable local cache directory:
`/Users/mac/Library/Caches/InvariantAudit/E003-v1-20260917/source/`.
Never overwrite an existing file; verify matching existing bytes or stop.
Record actual acquisition UTC, URL, status, HTTP headers, bytes and SHA-256;
recovery is a new acquisition, not the old freeze event or original metadata.
Reconstruct the original E003 manifest from recorded fields using sorted keys,
compact separators, UTF-8 and LF. Require the previously recorded digest
683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633.
If reconstruction or any source hash/count fails, stop and record acquisition
failure without a diagnostic result. Do not silently update pins. The old v1
runner's fixed manifest path is not used or modified.

## Parsing and equivalence

Verify all compressed sizes and hashes before parsing. Strictly decompress one
complete gzip member; reject trailing binary data, malformed/truncated gzip,
invalid UTF-8, non-object nonempty lines, duplicate JSON object keys, and
NaN/Infinity. Reject records without a valid decimal canonical event ID or
string event type. Permit an integer or canonical decimal string ID; exclude
booleans, negative IDs, leading zeros except zero, and nondecimal forms.

Within each shard preserve one-based original source line numbers and order.
Ignore blank lines. Raw record digest hashes the line bytes without CR/LF
terminators, preserving every other byte. Canonical full-record digest hashes
`json.dumps(object, sort_keys=True, separators=(',', ':'), ensure_ascii=False,
allow_nan=False)` encoded as UTF-8, without LF. Do not project away any fields.
Array order and primitive JSON types remain significant. This serialization
uses Python's finite JSON number representation, not an external JSON standard.
Record Python version. The same event ID in integer and string form is one ID
key but different full JSON content. SHA-256 collisions are assumed negligible.

For each ID, the first occurrence in source line order is the reference.
Every subsequent occurrence is exactly one of:

1. raw-identical-to-first (same raw digest);
2. canonical-only-identical-to-first (different raw digest, same canonical digest);
3. canonical-different-from-first (different canonical digest).

Report per shard: records, unique IDs, duplicate extra occurrences (N minus
unique IDs), duplicate-ID groups, conflict-ID groups (>1 canonical digest),
the three occurrence categories, maximum multiplicity, first collision line
pair, duplicate-extra counts by event type, and conflict-group counts touching
IssuesEvent or PullRequestEvent. Also report shared ID groups for every pair of
shards. Do not emit event IDs, repository names, actor data, payloads, or text.
Percentages use duplicate extras divided by raw nonempty records, not naturally
invalid-event prevalence.

## Validation and artifact gates

Implement a streaming dictionary accumulator and a separate sort/groupby
reduction over line-number/digest tuples. They may share input parsing, but must
not call each other's aggregation implementation. Require exact equality of all
counts and collision coordinates. This is differential algorithm verification
by one agent, not an independent reviewer or an external replication.

Synthetic tests must cover: no duplicates, byte repeats, whitespace/key-order
variants, content conflicts, A/B/B triplets, integer/string ID normalization,
cross-shard overlap, relevant/nonrelevant types, malformed IDs/JSON/gzip, changed
hash/size/count, existing outputs, and clean-tree/protocol ancestry gates.
No development test reads recovered real source content. After tests and an
implementation commit, run one explicit CLI on a clean worktree, with a new
run ID `e004-YYYYMMDD-NNN` and explicit source root. Lock/source verification
precedes analysis. No E003 harness or metric computation may be invoked.

Output exactly one aggregate JSON report and one Markdown report under this
experiment's results directory. Both contain run/protocol identity, protocol
and implementation commits, source hashes/counts, Python version, category
definitions, validation status, bounded interpretation, and SHA-256 binding
from Markdown to JSON. Refuse existing paths; serialize complete outputs before
exclusive creation. An output/analysis failure is recorded separately and
must not leave a valid-looking report. No raw records are committed.

One completed source audit ends E004. Stop on mismatch or acquisition failure;
do not switch shards, relax equality, relabel a conflict, or tune a validator.
Use its result in an outer-loop reflection to propose a separately locked
E003-v2. Reuse of already inspected source must be disclosed in that protocol;
a pristine holdout claim is unavailable for these shards.
