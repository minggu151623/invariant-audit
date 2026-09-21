# E003-v2 — Exploratory transfer with conservative exact-repeat normalization

Protocol date: 2026-09-21. ID: `E003-v2`.
Lock subject: `research(protocol): lock E003-v2 exact-repeat transfer`.
Local CPU, Python standard library, no network during implementation/evaluation,
no installs, paid compute, delegation, publication or public claims.
User instruction: `được rồi tiếp tục đi`; detailed design is AI-suggested.

## Normative base and precedence

This version consists of this amendment plus the complete immutable
[E003-v1 protocol](../E003-external-transfer-validation/protocol.md), from commit
`163e44dcabc698f101dee70dd7f3aa1bb7c8d5fb`, raw SHA-256
`8ec0ebc9b3420a2d71eebfe579ae2d1c87aa74c419dd3f38d1f0dc06c5c1e2a6`.
The runner must verify both protocol files, exact hashes and lock ancestry.
This amendment takes precedence only for the explicitly listed changes below;
otherwise the v1 source subset, filters, oracle contract, mutations, methods,
calibration formula, selection quotas, metrics, bootstrap and staging rules
are inherited. Historical v1 protocol-only/acquisition/authorization statements
describe v1's past stage, not v2 authority. No v1 artifact may be modified.

## Question and evidence classification

Can the fixed validator comparison be evaluated on the already inspected
external fixtures under a predeclared exact-repeat policy? Positive=valid:
FPR is false acceptance of invalid cases; FNR is false rejection of valid cases.

E004 run `e004-20260917-001`, implementation
`648a60759759f932a1a741a93a914115c5963a0b`, diagnosed all three raw shards.
Its aggregate JSON SHA-256 is
`d66a249c041d722d34254dcb06984ee8eb15caf5878740191a22e75510fb0d59`.
The 2021 shard has 537 identical extra occurrences and no content-conflict
groups; the other shards have no repeated IDs, and no IDs cross shards.
This policy was selected after those observations. E003-v1 remains invalid.

Classification is always `exploratory_reused_sources`, even if v2 passes its
predeclared gates. The historical split string `confirmatory` is retained for
schema compatibility but means the reused 2021 evaluation split, NOT a pristine
holdout. All references to confirmatory conclusions/untouched source in v1 are
superseded. No v2 outcome is an outcome of the original H3.

`H3-v2` uses the same numerical direction rule as v1: overall and both event
types require delta BA 95% CI lower >0, delta FPR CI upper <0, point delta FNR
<=0, and all 15 intervals have 10,000 usable replicates. Report outcome as
`supported_within_exploratory_design` or `mixed/not supported`. A gate failure
is `invalid`, not a negative hypothesis result. Brier/ECE remain secondary;
lower Brier alone cannot establish better calibration. No natural-error
prevalence, production, causal-delivery or generalization claim follows.

## Source pins and manifest identity

Reuse only the recovered original compressed bytes outside Git:
`/Users/mac/Library/Caches/InvariantAudit/E003-v1-20260917/source/`.
Do not download, rewrite, normalize on disk, or substitute raw sources in v2.

| Split | Filename | Bytes | Nonempty records | Compressed SHA-256 |
| --- | --- | ---: | ---: | --- |
| development | 2019-01-15-12.json.gz | 29278679 | 67145 | ae451576f78417d75f135b29ee67ea8e666dc5f6cb16e78cef04e20342b42b50 |
| calibration | 2020-01-15-12.json.gz | 46372480 | 90940 | 624a0d2a2fc575afb1e63bece53521e2b078ddfd1caf60026e313ad36d83cddd |
| confirmatory | 2021-01-15-12.json.gz | 61805367 | 117780 | a4a80c97153c691866d52b7e06ea0051f2449f0c6f8060dad9f441a69cd13788 |

URLs remain `https://data.gharchive.org/<filename>`. Require all byte pins before
parsing. Strictly decompress one complete gzip member, rejecting trailing or
truncated binary data. Preserve original one-based physical line coordinates.

Original acquisition manifest digest remains
`683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633`.
A separate external `source-manifest-v2.json` uses exactly its files array,
order and fields, changing only root `protocol_id` to `E003-v2`. Serialize with
sorted keys, compact separators, UTF-8 and one LF. Its required SHA-256 is
`c6c43cbbc6f069d78c56c9d7b9c45a58120574c205f059c1fe1b0086f7f3fa47`.
Create exclusively if absent or verify existing exact bytes, never overwrite.
This is a derived protocol manifest, not a new acquisition. Preserve original
manifest and recovery metadata. Record both manifest digests in the report;
v2 row-level `source_manifest_sha256` refers to the v2 manifest.

## Raw normalization — replaces v1's blanket duplicate rejection

Before projection, type/action filtering, oracle calls or repository selection:

1. Parse every nonempty LF-delimited line as strict UTF-8 JSON. A single CR
   immediately before LF/end-of-file is a line terminator; remove only that CR
   for raw comparison. Retain all other bytes. Whitespace-only lines do not
   count as records, but advance physical coordinates. Reject non-objects,
   duplicate JSON keys, nonfinite numbers (including overflowing exponents),
   and invalid Unicode strings. Require a string event type and canonical
   decimal ID: integer >=0 or ASCII string `0|[1-9][0-9]*`; reject bool,
   negative, floats, leading zeros and missing IDs, even in excluded types.
   This global fail-closed ID/type requirement is stricter than v1's adapter.
2. Scan splits in development/calibration/confirmatory order and each shard in
   original line order. Key by canonical decimal ID. For a new ID retain the
   first occurrence with original filename/line. Any occurrence of an ID in
   another shard invalidates the whole run, even if bytes match.
3. Within a shard, compare the full raw line bytes with the first occurrence,
   not projected fields, a previous repeat, or selected JSON properties. Exact
   byte equality permits omission of the extra occurrence. Any byte difference
   invalidates the run, including key order/spacing, ignored payload fields or
   integer/string ID representation. Do not collapse canonical-only equivalents,
   quarantine groups, choose the latest payload or ignore excluded-type conflicts.
4. Return no usable normalized collection until all requested shards have
   passed; a later conflict must not leave a partially accepted collection.
   Raw files are never edited. Parsing/normalization operates in memory.
5. Report per split raw count, unique count, collapsed extras, repeated groups,
   maximum multiplicity, first collision line pair and collapsed extras by type.
   Require raw=unique+collapsed and sum(type extras)=collapsed. Valid-run conflict
   and cross-shard repeated-ID counts are zero. Preserve counts before filtering;
   distinct first occurrences alone enter inherited exclusion accounting.

For the pinned real inventory require `(raw,unique,collapsed)` exactly
`(67145,67145,0)`, `(90940,90940,0)`, `(117780,117243,537)`, with 537 groups of
size two in 2021. These are E004-informed source regression gates, not new
scientific predictions. Synthetic tests need not reproduce these inventory counts.

For each split require `unique = excluded + eligible_after_repository_filter`,
where exclusions count each distinct first occurrence once by deterministic
first reason. Selection separately accounts for eligible, selected and unselected.
Collect valid canonical repository IDs from ALL normalized raw event types,
before eligibility filtering. Remove any repository present in two or more
shards from eligible bases across all three splits. Unknown/invalid repository
IDs do not enter the repository index; selected bases must have valid IDs.
No cross-shard event IDs does not by itself prove repository isolation.

## Unchanged evaluation and explicit namespace changes

Keep v1's exact 64 IssuesEvent +64 PullRequestEvent bases per split, maximum
four per (repository,type), >=24 repositories overall and >=16 per type,
S1/I1/T1 mutations, oracle separation, B0/M1/three ablations, calibration-only
Laplace lookup, 512 cases/split, 7,680 prediction rows, 54 metric rows and
150,000 bootstrap rows. Quota failure invalidates; do not search new shards.

Every computational identity literal `E003-v1` becomes `E003-v2`, including
bootstrap seed prefix, calibration no-lookup marker and base/case identity
derivations. This deliberately changes deterministic bootstrap draws; it is not
an exact v1 rerun. Do not change the sentinel mutation URL or scientific rules.
Source metadata continues pointing to ORIGINAL compressed files and lines.

New paths only:

```text
data/E003-v2-predictions.jsonl
data/E003-v2-metrics.csv
data/E003-v2-bootstrap.csv
experiments/E003-v2-exact-repeat-transfer/results/run-<run_id>.md
```

Run ID grammar: `e003v2-YYYYMMDD-NNN`, valid calendar date, new/unused ID.
Code lives in this experiment's `code/`; no runtime mutation/monkeypatch of v1
modules or bypass of v1 guards. Existing v1 code is read-only reference.
Reuse of unchanged helpers requires explicit version parameters and regression
checks; no silent import-name collision with v1. No raw payload/text in reports.

The four artifact schemas and v1 byte envelopes remain unchanged. The report
adds classification, H3-v2 identity, both manifest digests, original protocol
and v2 lock commits/hashes, normalization counts, repository exclusions for
all three splits, implementation and independent-acceptance identities, prior
source-inspection disclosure and no-public-claim limitation. Invalid reports
use v1's concise structure with v2 protocol/title/run ID; never include metrics.

## Development, review and execution gates

Lock this amendment in a dedicated commit before implementation. Test with
synthetic inputs: exact repeats including multiplicity >2, CRLF, blanks,
spacing/key order, ignored-field conflicts, A/B/B, int/string IDs, missing or
invalid IDs/types, malformed/overflowing JSON, duplicate keys, trailing/truncated
gzip, cross-shard repeats of excluded types, original coordinates, immutable
inputs, late failure atomicity, raw/unique/exclusion accounting, all-type
repository isolation, output absence and protocol/manifest drift.

Development integration may read ONLY 2019/2020, with a guard refusing access
to the 2021 file. The completed E004 diagnostic is not permission to fit/tune
methods on 2021, print its metrics or preselect its evaluation cases during
development. A two-split integration cannot certify all-three-split isolation.

Performance execution requires explicit independent acceptance against the
exact implementation commit, including unresolved M12 remediation, calibration
leakage, oracle/label separation, source accounting and output transactionality.
Self-review/differential tests are not independent acceptance. No delegation is
authorized in the current worker session; if acceptance is unavailable, finish
safe implementation/tests and hand off, do not execute performance scoring.

After acceptance, all inherited v1 clean-tree, lock ancestry, output absence,
immutability, deterministic double-build, calibration freeze, 10,000-replicate
and size gates apply with v2 identities and this normalization policy. The
runner must check both locks and a committed acceptance record before scoring.
One valid exploratory run ends v2. Invalid attempts preserve an invalid record
and require a separately reviewed remediation/new ID, not automatic retry or
protocol relaxation. No scoring/run authority is consumed by this protocol lock.

## Limits and stopping gate

This policy fits a known finite inventory, not an inferred delivery guarantee.
Selected positives are oracle-filtered; negatives are artificial mutations.
Shared-specification risk remains. Hashes and tests do not prove universal
reproducibility, absence of leakage, or real-world error rates. Even perfect
scores may reflect controlled construction, not broad external transfer.

Current stage permits protocol lock and local implementation/synthetic tests,
not performance execution without the independent review gate. E003-v1 invalid
evidence and E004 diagnostic remain unchanged. New uninspected sources and a
separate protocol would be needed for later confirmatory transfer evidence.
`public_claim_eligibility=false`. No continuity automation or epilogue writes.
