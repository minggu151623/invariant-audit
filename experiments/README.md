# Experiments

Protocols, runs, results, and linked data; Markdown is narrative source and
CSV/JSONL is row-data source.

## Current boundary

- [E003-v2 exact-repeat transfer](E003-v2-exact-repeat-transfer/protocol.md)
  is locked at b9cae97 with exploratory reused-source classification. The
  [source component](E003-v2-exact-repeat-transfer/code/README.md) passes 22
  synthetic tests; full pipeline and independent acceptance remain pending.
  No v2 performance run/result exists. Current milestone is
  [M16](../milestones/M16-E003-v2-protocol-and-normalizer.md).

- [E001 synthetic invariant calibration protocol](E001-synthetic-invariant-calibration/protocol.md)
  is the M01 documentary protocol, locked by commit
  `d8b26d21e9692ace19436d78461460940043f5c7` with subject
  `research(protocol): lock E001 synthetic invariant calibration`. The protocol
  commit is published as an ancestor of result commit
  `31071ddf65ad9a1f0e5b28eb0d501899253cd17b`.
- The authorized run `e001-20260825-001` is valid. Its published result is
  [run Markdown](E001-synthetic-invariant-calibration/results/run-e001-20260825-001.md)
  in result commit `31071ddf65ad9a1f0e5b28eb0d501899253cd17b`; linked row data
  is indexed in [data/README.md](../data/README.md).
- M02 verifies this result only within the finite synthetic E001 design. It is
  not production, external-validity, novelty, safety, or generalization
  evidence, and it does not authorize a future E002 run.
- [E002 heterogeneous specification stress protocol](E002-heterogeneous-specification-stress/protocol.md)
  is the protocol locked at M03. The historical M03 record was protocol-only;
  the executable implementation now exists in
  [the E002 code directory](E002-heterogeneous-specification-stress/code/README.md)
  and is recorded by the implementation chain
  `42cb62374c2b94ad6c567232acdac6d7365a9d8f` ->
  `6df4f3bc02f5f12feb243df21ec9eeaafd53d8fc` ->
  `0977641f129d172dd4d11136197a82cb17654aeb` ->
  `1fe42a7ebc6a9ce69d8a16654e068c0a9a891d08`.
- [M04 implementation review and authorization gate](../milestones/M04-E002-implementation-review.md)
  records the independent-review approval and bounded authorization for one
  locked local run. The 54-test development suite is `OK`; the subsequent run
  is recorded as invalid in [M05](../milestones/M05-E002-run-001-invalid.md),
  and validator remediation is recorded in
  [M06](../milestones/M06-E002-validator-remediation.md).
- [M05 E002 run 001 invalid evidence](../milestones/M05-E002-run-001-invalid.md)
  records run `e002-20260825-001`, exit code 2, and the
  `D9_OR_NA` semantic-field drift. No metrics, evidence, or data outputs
  exist; implementation remediation is complete in M06 and
  `public_claim_eligibility` is `false`.
- [M06 E002 validator-remediation gate](../milestones/M06-E002-validator-remediation.md)
  records the exact-delta fix and independent acceptance. The invalid run
  was the only E002 execution at M06; M08 subsequently records the valid
  corrected run.
- [M07 E002 corrected-run technical-readiness gate](../milestones/M07-E002-corrected-run-readiness.md)
  records the final development-test-boundary remediation and technical
  readiness for candidate `e002-20260825-002`, subject to runtime preflight at
  that historical gate. M08 records the subsequent separately authorized
  execution.
- [M08 E002 corrected run 002 valid result](../milestones/M08-E002-run-002-valid.md)
  records exactly one valid locked local confirmatory run,
  `e002-20260825-002`, with the four runner-produced artifacts. The result
  reports H2 `supported` within the finite synthetic E002-v1 design; its
  primary anchor is delta M1-B0 BA `0.401960784`, FPR `-0.803921569`, FNR
  `0.000000000`, Brier `-0.091689527`, and ECE `0.005222762`. The FNR
  guardrail passed and multi-fault relations had `equals=272`, `contains=160`,
  and `differs=0`. This is confirmatory evidence for the locked synthetic
  design only, not production, external-validity, novelty, safety,
  generalization, or a public claim; `public_claim_eligibility` remains
  `false`.
- The M08 result report is
  [run-e002-20260825-002.md](E002-heterogeneous-specification-stress/results/run-e002-20260825-002.md).
  Its linked data artifacts are
  [predictions](../data/E002-v1-predictions.jsonl),
  [metrics](../data/E002-v1-metrics.csv), and
  [bootstrap](../data/E002-v1-bootstrap.csv). The prior M05 invalid report
  remains preserved and is not replaced by this corrected run.
- This index is not experimental evidence and establishes no E002 metric,
  H2 outcome, external validity, novelty, safety, generalization, or public
  claim beyond the explicitly bounded M08 result record.
- [E003 external-transfer validation protocol](E003-external-transfer-validation/protocol.md)
  is the M10 protocol design following the M09 **BROADEN** decision. M11
  records completion of the exact read-only acquisition: the three raw
  fixtures and canonical source manifest are frozen outside Git with hashes,
  byte counts, decompressed JSONL line counts, and HTTP metadata. M12 records
  the scoped implementation and development/calibration-only preflight; the
  implementation re-review acceptance is not documented. M13 records the later
  invalid run, rejected before scoring for duplicate source IDs. Only an
  invalid report exists; no E003 performance result or metric exists. The
  temporary cache was missing at 2026-09-17 resumption and recovered under E004.
- [E004 source diagnosis](E004-source-duplicate-diagnosis/results/e004-20260917-001.md)
  completed one exploratory audit on hash-matched recovered sources: 537
  byte-identical extra occurrences, no conflicting ID groups and no cross-shard
  repeated IDs. Nineteen synthetic tests and dictionary/sort differential checks
  pass; no independent review or performance result is implied. See
  [M15](../milestones/M15-E004-source-diagnosis.md) for evidence and E003-v2 gates.

## E005 — benchmark evidence audit (2026-10-22)

[Locked protocol](E005-benchmark-evidence-audit/protocol.md) and
[valid exploratory result](E005-benchmark-evidence-audit/results/run-e005-20261022-001.md).
This audits existing E001/E002 rows with an independent metric implementation;
it is not a new performance experiment or independent reviewer acceptance.

## E006 — fixed external-reference validation

[Protocol](E006-external-reference-validation/protocol.md) locked before paired
row inspection; [valid result](E006-external-reference-validation/results/run-e006-20261022-001.md).
Four simple attribution policies and binary/lookup probabilities on three fixed
reference tables. H6b is mixed; task and FPR/FNR tradeoffs are retained.
This is not Raha replication, original M1 transfer or an E003 gate bypass.

- [E007 FD decision stability](E007-fd-decision-stability/protocol.md): locked
  finite formulation check; [analysis](E007-fd-decision-stability/analysis.md)
  records validity, prior-work collision and the mutable-key next question.

- [E008 mutable-key certificates](E008-mutable-key-certificates/protocol.md):
  exact finite validation and [theorem draft](E008-mutable-key-certificates/theory.md);
  originality and efficiency need further comparison.

- [E009 accepted-target characterization](E009-singleton-characterization/protocol.md):
  [proof](E009-singleton-characterization/theory.md), 18779 formula/oracle cases
  and 2118 independently formulated raw-cell MILP comparisons; no runtime claim.

- [E010 directional algorithm comparison](E010-directional-scaling/protocol.md):
  162 raw-oracle preflight fixtures and 72 constructed cases, both directions
  analyzed separately; [analysis](E010-directional-scaling/analysis.md) retains
  timeouts, a slower case and the limited generator scope.

- [E011 reused-source stability](E011-reused-source-stability/protocol.md):
  18734 source targets; [analysis](E011-reused-source-stability/analysis.md) keeps
  the single finite decrease, fixed-INF transitions, negative rejected-subset
  outcome and two timeouts. This is reused evidence, not a blind holdout.
