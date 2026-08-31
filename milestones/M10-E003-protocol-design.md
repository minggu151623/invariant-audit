# M10 — E003 external-transfer protocol design

## Status and boundary

M10 is a verified documentary protocol-design milestone. It records the
post-E002 outer-loop decision and a protocol-only E003-v1 design; it is not an
execution, result, dataset acquisition, implementation, or public-claim gate.
`public_claim_eligibility` remains `false`.

M09 synthesized the verified E001 and E002 finite-synthetic records and chose
**BROADEN** because externally authored records and source/schema behavior are
the largest unresolved gap. The detailed E003 technical design is
worker/reviewer inference, not user-selected technical design. The
protocol-only local documentation lock is current; source acquisition,
implementation, execution, publication, and public claims remain outside this
gate.

## Frozen source plan

The source set is capped at three directly relevant primary/official sources:

| Role | Source | Exact URL | Protocol use |
| --- | --- | --- | --- |
| Archive source | GH Archive official site | <https://www.gharchive.org/> | Public hourly JSON event archives and their timestamped fixture naming. |
| Event contract | GitHub official event-types documentation | <https://docs.github.com/en/rest/using-the-rest-api/github-event-types> | Common event fields and IssuesEvent/PullRequestEvent action vocabulary. |
| Validity caution | Kalliamvakou et al., *An in-depth study of the promises and perils of mining GitHub* | <https://doi.org/10.1007/s10664-015-9393-5> | Primary empirical caution that GitHub mining requires validity and data-alignment checks. |

The three planned fixture URLs are `2019-01-15-12.json.gz`,
`2020-01-15-12.json.gz`, and `2021-01-15-12.json.gz` at
`https://data.gharchive.org/`. Their byte hashes, byte counts, line counts,
HTTP metadata, and acquisition manifest are intentionally absent because no
download is authorized or performed here. The protocol requires a separately
acquired, externally stored manifest before any scoring.

## Protocol lock summary

E003-v1 asks whether M1 retains a reduction in false positives without
increasing false negatives relative to B0 on externally authored GitHub event
records plus deterministic probes. It selects exactly 64 `IssuesEvent` and 64
`PullRequestEvent` clean bases per development, calibration, and confirmatory
shard, with at most four bases per repository/type and strict repository
disjointness across shards. Each base yields `clean`, `S1-missing-resource`,
`I1-wrong-repository`, and `T1-status-contradiction`, for 512 cases per split.

The primary methods are schema-only B0 and invariant-aware M1. Descriptive
ablations remove identity, state, or calibration. Calibration is fit only on
the calibration split; the confirmatory split remains untouched until source
hashes, lookups, and all preflight checks are frozen. A separately maintained,
fail-closed oracle establishes the documented subset contract and recomputes
the failure family for every mutation without receiving method metadata.

The primary comparison is paired M1-minus-B0 balanced accuracy, FPR, and FNR
with 10,000 deterministic repository-cluster bootstrap replicates. H3 is
supported only if overall and both event-type subgroups meet the predeclared
interval/guardrail rule. A valid `mixed/not supported` outcome is terminal;
source, oracle, isolation, determinism, calibration, size, or schema failures
produce an invalid run with no evidence-like metrics.

## Verification and next gate

- `run_authorized: false`
- `acquisition_authorized: false`
- `implementation: absent`
- `run: absent`
- `results: absent`
- `data: absent`
- `code: absent`
- `public_claim_eligibility: false`

The E003 protocol-only lock is recorded by the current two-commit handoff with
subject `research(protocol): lock E003 external transfer validation`. The full
commit hash is available from Git history and is intentionally not
self-embedded in this milestone. Separate authority is still required for
acquisition, implementation/review, and the single confirmatory run. The
protocol itself does not claim that the snapshot exists or that E003 has been
executed.
