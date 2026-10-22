# E005-v1 — Exploratory audit of finite validation benchmarks

Date: 2026-10-22. Classification: `exploratory_reanalysis`.
Lock subject: `research(protocol): lock E005 benchmark evidence audit`.
This protocol is locked before implementation/results. E001/E002 outcomes and
selected example rows have already been read. No pristine confirmation, new
performance run, independent acceptance, or production evidence is implied.

## Question and predictions

Which reported improvements reflect finite test construction, and which
probability-score differences can be explained by score-group reliability and
resolution? Expected directions, informed by old reports: M1 decisions are
perfect, M1-no-calibration has zero Brier/ECE, E001 cluster statistics are
identical, and B0-to-M1 lowers Brier while raising ECE. These are post-hoc
replication predictions, not new confirmatory hypotheses.

Falsifiers: recomputed statistics outside declared tolerances, any mismatch in
M1 decisions/truth, any binary-ablation error, nonzero Brier identity residual,
or a calibration prediction inconsistent with calibration-only fitting. Report
these as discrepancies; never change old artifacts or select different inputs.

## Frozen inputs

| Artifact | SHA-256 | Rows |
| --- | --- | ---: |
| data/E001-v1-predictions.jsonl | be5e5e2a6c3f33778a34af69d79ec4f14e3b2c0cba2f371ecc004310b7c9559a | 5120 |
| data/E001-v1-metrics.csv | ae7c32be651b5dfe175ca0537aa3cb8283acbd7063b14e15b8ec386f0d6a20cb | 75 |
| data/E002-v1-predictions.jsonl | bcb34aad4338fdfbffe07be1843769b360bf4e8c422d855a9ce605350fad13b7 | 7296 |
| data/E002-v1-metrics.csv | f000348d385550745480066fce2d691686728ebe2bfcf7bd96e7231e4b1e5ca3 | 243 |

Inputs are read-only. Preserve unrelated files, old protocols/runs and the
E003-v2 review gate. Standard-library Python on local CPU; no network, paid
services, source-cache reads, raw event publication or new source acquisition.

## Measurements fixed in advance

- Parse serialized probabilities exactly as decimal rational numbers. Reject
  malformed/duplicate JSON keys, nonfinite/out-of-range probabilities, missing
  fields, invalid decision/truth types, unknown methods/splits and duplicate
  (split,case_id,method) keys. Validate all pinned input hashes before parsing.
- For every split/method overall row, recompute n, TP/TN/FP/FN, BA, FPR, FNR,
  Brier and ECE independently, with positive=valid and ten equal-width bins
  [i/10,(i+1)/10), with p=1 in the final bin.
- Compare confusion counts exactly and metrics to their frozen CSV values.
  Absolute tolerance: E001 1e-9, E002 2e-9, allowing displayed decimal rounding.
  Export differences, not only pass flags. Unavailable denominators fail closed.
- Group by each distinct serialized probability p. For n_g, event frequency
  f_g and overall frequency ybar, compute
  reliability=sum(n_g/N*(p_g-f_g)^2),
  resolution=sum(n_g/N*(f_g-ybar)^2), uncertainty=ybar*(1-ybar).
  Assert exact Brier = reliability-resolution+uncertainty. No bins are used
  for this identity; finite score-group decomposition is not population calibration.
- Audit calibration-only smoothed lookup: for each calibrated method, use
  calibration rows only and p=(positive_count+1)/(count+2) by raw_score, with
  global fallback (positive_total+1)/(N+2). Compare every serialized prediction
  to this probability using the experiment tolerance. M1-no-calibration must
  equal its binary decision. This can establish compatibility, not historical
  proof of no leakage or that fitting actually occurred in the correct order.
- Require per-case truth/input hash alignment across methods and full method
  coverage; require paired M1/binary-ablation decisions. Check disjoint base
  IDs (E001) or cluster IDs (E002) across splits and report any cross-split
  input-hash overlap. Do not label an overlap leakage without inspecting its cause.
- On the confirmatory split, count cluster statistic signatures separately per
  method: (TP,TN,FP,FN,sum squared probability error, ten bin counts,
  ten sums of p, ten sums of truth). E001 unit is base_case_id; E002 unit
  is cluster_id. This is a diagnostic, not an effective sample-size estimate.
- For B0/M1/binary ablation, export score-group counts and observed frequencies
  for a figure. Do not run a new bootstrap or make population significance claims.

## Outputs, validity and stopping

New artifacts only: data/E005-v1-summary.csv, data/E005-v1-score-groups.csv,
data/E005-v1-checks.json, and
experiments/E005-benchmark-evidence-audit/results/run-e005-20261022-001.md.
Each includes or references protocol and input identities, classification,
implementation identity and limitations. Deterministic UTF-8/LF, sorted rows;
refuse existing destinations. Build twice and compare bytes, check all audits
before publication, and clean owned outputs on failure. Preserve an invalid
record for an attempted data audit that fails; do not silently retry. Synthetic
test failures before data execution are development, not invalid study attempts.

A valid run requires all input/schema/accounting/alignment/calibration/metric
agreement/decomposition checks. Signature diversity and predicted scientific
directions are descriptive outcomes, not validity gates. Record a valid null
or discrepancy outcome if an expected direction is absent after all validity
checks pass. No automatic extra analyses, bin changes or new sources.

Tests before data execution: known confusion metrics, boundary bins, exact
Brier identity with mixed-label groups, conflicting labels/keys, rounding,
calibration fallback and mismatch, signature equivalence and late write failure.
Tests and another implementation by this author do not constitute independent
review. One audited result, then outer-loop reflection.
