# M13 — E003 run 001 invalid evidence record

Status: `invalid_run_recorded`. The authorized local run is recorded as
invalid; protocol assumption revision or alternative fixture selection is
pending; no valid E003 result exists.

## Scope and provenance

M13 records the local execution authorized by user directive
`user-2026-09-03-e003-goal` (`"nhưng mà nghiên cứu tôi nghĩ chưa xong, bạn có thể tiếp tục được không? /goal"`).
The run was executed under the locked local command with clean working tree.
This record is documentary evidence of an invalid execution, not an E003
scientific result.

The user authority authorized continuation of the research workspace under
autonomous guidance. It did not alter the locked protocol design, authorize
push or publication, authorize a public claim, or establish an outcome. The
empirical diagnosis below is worker/reviewer verification work, not user-selected
technical design.

## Locked protocol and implementation context

- Protocol: [E003-v1](../experiments/E003-external-transfer-validation/protocol.md)
- Protocol lock commit: `163e44dcabc698f101dee70dd7f3aa1bb7c8d5fb`
- Protocol blob SHA-256: `8ec0ebc9b3420a2d71eebfe579ae2d1c87aa74c419dd3f38d1f0dc06c5c1e2a6`
- Protocol status: unchanged and byte-identical to the locked blob.
- Implementation commit: `915448450702d849fafe39b23b5c777e48b30dcf`
- Implementation subject: `research(impl): remediate E003 implementation review findings`
- Audited source manifest: `/private/tmp/invariant-audit-e003-v1/source-manifest.json` (SHA-256 `683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633`)
- Audited source cache: `/private/tmp/invariant-audit-e003-v1/source/`
- Prior milestones: M11 recorded the frozen source snapshot; M12 recorded implementation readiness and development/calibration preflight evidence.

## Observed invalid run

- Run ID: `e003-20260903-001`
- Command: `python3 experiments/E003-external-transfer-validation/code/run_e003.py --run-id e003-20260903-001 --output-root . --source-manifest /private/tmp/invariant-audit-e003-v1/source-manifest.json`
- Started at: `2026-09-03T20:35:54+07:00`
- Exit code: `2`
- Runner failure: `pre-staging pipeline failure: duplicate event ID across source: confirmatory:16450 and confirmatory:16491`
- Invalid report: [run report](../experiments/E003-external-transfer-validation/results/run-e003-20260903-001.md)
- Invalid report SHA-256: `5bf6c545f43333a6a3cc0d8ea8a8b2d3f7adfb4be0c0358d1cd75c17a8254305`
- Invalid report size: 258 bytes; 8 lines.
- Result status: `invalid`; failure class: `invalid-run`.
- No metrics, evidence, or data outputs exist.
- `corrected_run_requires_new_id: true`.

The concise invalid report records the protocol commit and run ID, states that
no metrics or evidence exist, and requires a new ID for any corrected run. No H3
outcome or scientific metric is established.

## Independent empirical diagnosis

The independent empirical investigation of the external fixtures revealed:

| Shard | File | Records | Duplicate event IDs |
| --- | --- | ---: | ---: |
| development | `2019-01-15-12.json.gz` | 67,145 | 0 |
| calibration | `2020-01-15-12.json.gz` | 90,940 | 0 |
| confirmatory | `2021-01-15-12.json.gz` | 117,780 | 537 |

Key findings:

1. **Cross-split duplicates:** Cross-shard duplicate event ID count across 2019, 2020, and 2021 is exactly `0`.
2. **Confirmatory intra-shard duplicates:** The confirmatory shard (`2021-01-15-12.json.gz`) contains exactly 537 duplicate event IDs (representing duplicate lines in the hourly stream).
3. **First collision:** The first collision occurs between line 16450 and line 16491: `id=14832202395`, type `PushEvent` on repository `La-Z-fandy/Personalsite.github.io`.
4. **Distribution across event types:** Duplicates span multiple event types: PushEvent (289), CreateEvent (68), WatchEvent (38), PullRequestEvent (34), IssueCommentEvent (26), IssuesEvent (19), and other events (63).
5. **Root cause:** In upstream production telemetry, GH Archive and GitHub API event feeds are subject to at-least-once delivery semantics, where network retries or polling window overlap cause repeated event delivery.
6. **Protocol conflict:** Locked protocol E003-v1 lines 150-153 and 201-202 explicitly mandated:
   > *"The source record's raw `id` is the canonical `event_id` and must be unique across all three shards. Any duplicate event ID, including a duplicate with different bytes, is a source-integrity failure; no deduplication choice is permitted."*
   > *"1. Parse one JSON object per nonempty line; reject the entire run if a line is malformed, duplicated by event ID, or not an object."*
7. **Scientific classification:** This is an **authentic external transfer mismatch**: the synthetic protocol assumed clean, duplicate-free event streams, while real-world production software telemetry contains at-least-once duplicate delivery. The runner correctly executed fail-closed enforcement and rejected the run.

## Current state and next gate

M13 is the current milestone.

- `run_authorized: false`
- `authorization_consumed: true`
- `run: invalid` for `e003-20260903-001`, exit code `2`
- `results: invalid_report_only`
- `metrics: absent`
- `evidence: absent`
- `data: absent`
- `public_claim_eligibility: false`

The next gate requires an outer-loop decision:
1. Formulate and lock `E003-v2` with realistic streaming deduplication (e.g., deduplicate upon first occurrence in line order or record duplicate delivery as an explicit natural exclusion class).
2. Or acquire an alternative public hourly snapshot that happens to possess zero duplicates.
Any future run requires a protocol lock, new run ID, and clean preflight.
