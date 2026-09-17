# M15 — Recovered-source diagnosis and outer-loop decision

Date: 2026-09-17. Status: `valid_source_diagnostic_only`.
Exploratory follow-up to M13, not external performance validation.
User authorized continued research; the detailed design is AI-suggested.

## Evidence chain

- Corrections: `a0a5053` (M14).
- E004-v1 protocol lock: `1bf1a4a9a7f73c0ce1cc7aad4e4c74eaf3e03c51`.
- Protocol SHA-256: `51cf34b8ca31e96e44a8b1f5b779817fd68de96e38060d4b81e2dd435b4688bb`.
- Implementation: `648a60759759f932a1a741a93a914115c5963a0b`.
- Exactly one diagnostic run: `e004-20260917-001`; exit 0; completed
  `2026-09-17T07:43:18.692285+00:00`, Python 3.14.5.
- [Run report](../experiments/E004-source-duplicate-diagnosis/results/e004-20260917-001.md),
  SHA-256 `f0288495190c2beebe3de99272596f0e8cf21395cd3818c6602d80e0dc6a8813`.
- [Aggregate JSON](../experiments/E004-source-duplicate-diagnosis/results/e004-20260917-001.json),
  SHA-256 `d66a249c041d722d34254dcb06984ee8eb15caf5878740191a22e75510fb0d59`.

Command (already executed; do not reuse its run ID):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 experiments/E004-source-duplicate-diagnosis/code/audit.py --run-id e004-20260917-001 --cache /Users/mac/Library/Caches/InvariantAudit/E003-v1-20260917
```

## Recovery, not a backdated freeze

The original temporary cache was absent. The three exact pinned public URLs
were reacquired with HTTP 200 on 2026-09-17 between 07:40:19 and 07:40:47 UTC.
All original compressed SHA-256 values, byte sizes and decompressed record
counts match. Raw data remain outside Git in
`/Users/mac/Library/Caches/InvariantAudit/E003-v1-20260917/source/`.
The adjacent reconstructed `source-manifest.json` matches historical digest
`683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633`.
New acquisition provenance is in adjacent `recovery-metadata.json`, SHA-256
`23869daec458361c6e5d055542b41b88e2230f72e08043a1aa16c856cd6f8a2c`.
This does not recover original acquisition timestamps/HTTP headers. Cache
recovery is reproducible via pins, not a guaranteed permanent archive.

## Observed result

| Split | Records | Unique IDs | Extra occurrences | Conflicting ID groups |
| --- | ---: | ---: | ---: | ---: |
| development | 67,145 | 67,145 | 0 | 0 |
| calibration | 90,940 | 90,940 | 0 | 0 |
| confirmatory | 117,780 | 117,243 | 537 | 0 |

All 537 extras match their first occurrence's full raw-line SHA-256 (excluding
line terminators); 537 repeated-ID groups each have multiplicity two. No
formatting-only equivalent or conflicting full canonical object was found.
The first collision is at lines 16450/16491, reproducing E003-v1's failure.
No event IDs are shared across any pair of shards. This does not establish
repository/entity independence. Of the extras, 19 are IssuesEvent and 34
PullRequestEvent; these are source occurrences, not selected-case counts.
537/117780 is approximately 0.455935% of confirmatory source records, not a
naturally invalid-case prevalence estimate.

## Validation and evidence limits

- Protocol ancestry, clean-tree, byte pins, strict JSON/gzip, exact counts and
  source immutability gates passed.
- Dictionary/sort aggregation agreed exactly. Shared parser and single author
  mean this is not independent reviewer acceptance or external replication.
- Synthetic development suite: 19 tests PASS before implementation commit;
  post-run verification again passed 19 tests in 0.050 s without real-source
  analysis or rerunning the diagnostic.
- Post-run report/JSON hash binding and aggregate accounting passed: 275,865
  raw records and 275,328 unique IDs.
- E001/E002 result/data hashes and E003 invalid-report hash remain unchanged.
- No causal delivery explanation, E003 scoring, H3 result, external validity
  or public-claim eligibility is established.

## Outer-loop decision and exact next gates

Continue **BROADEN**, with source-policy repair supported by E004. Propose
byte-identical first-occurrence collapse within each shard; reject every
non-byte-identical repeated ID and every cross-shard repeated ID. This is more
conservative than collapsing canonical-only equivalents, for which these shards
provide no observed example. E003-v1 and its invalid report stay unchanged.

1. Draft and separately lock E003-v2 before implementation. Disclose prior
   inspection of all three shards; a reused-source run is exploratory, not
   pristine holdout confirmation. Preserve v1 raw pins, selection, methods and
   metric rules unless each change is explicit in the new protocol.
2. Normalize before type filtering; preserve original line coordinates/raw
   counts. Freeze deterministic retained-occurrence rules, duplicate accounting,
   all-three-split repository isolation, new protocol/manifest identities,
   output namespace and fresh run ID. A conflicting duplicate invalidates the
   whole run; do not choose a preferred payload.
3. Implement v2 separately. Test exact repeats, formatting-only differences,
   payload conflicts, A/B/B, ID representation differences, cross-split
   collisions, ordering, exclusions and immutability. The v1 scanner rejects
   every repeated ID (`experiments/E003-external-transfer-validation/code/e003.py:1050`);
   do not bypass its guard. Obtain explicit independent acceptance of v2 and
   unresolved M12 remediation before performance execution.
4. After the lock/readiness gate, execute one separately identified exploratory
   external-fixture evaluation. Later confirmation requires newly preselected
   uninspected sources and a separate protocol. Artificial negative mutations
   still cannot estimate naturally occurring error prevalence.

One completed audit ends E004 under its protocol. No E003-v2 protocol lock,
implementation or performance run is claimed by this milestone.

## Documentary boundary

README, paper, findings and canonical state now distinguish this diagnostic
from E001/E002 performance and E003 invalidation. Historical M13 causal text is
explicitly withdrawn. ARA and older human-facing summaries remain historical,
not current claim authority; no epilogue writes were made. Independent
manuscript review remains open.
