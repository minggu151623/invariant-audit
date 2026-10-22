# Data

Reviewable row data and metadata; CSV/JSONL is the source of truth and
interpretation stays in Markdown.

## Published E001-v1 artifacts

These artifacts belong to run `e001-20260825-001`, use protocol commit
`d8b26d21e9692ace19436d78461460940043f5c7`, and were published in result commit
`31071ddf65ad9a1f0e5b28eb0d501899253cd17b`.

| Path | SHA-256 | Size | Count |
| --- | --- | ---: | ---: |
| [Predictions](E001-v1-predictions.jsonl) | `be5e5e2a6c3f33778a34af69d79ec4f14e3b2c0cba2f371ecc004310b7c9559a` | 2,966,528 B | 5,120 rows |
| [Metrics](E001-v1-metrics.csv) | `ae7c32be651b5dfe175ca0537aa3cb8283acbd7063b14e15b8ec386f0d6a20cb` | 162,200 B | 75 rows + header |
| [Bootstrap](E001-v1-bootstrap.csv) | `63b86d44f3425f0c2a43c53191d13ce614b0d0726ff1e941da98d11ee545ede5` | 32,920,126 B | 450,270 rows + header |

The result Markdown records the method intervals, paired M1-minus-B0 deltas,
ablations, validity, limitations, and zero deviations. The bootstrap intervals
are degenerate because the locked 64-cluster signatures were identical across
all 10,000 replicates; they are not evidence of external uncertainty.

The E001 oracle is coupled to its synthetic recipes. These data do not support
production validity, external validity, generalization, novelty, safety, or a
public claim; `public_claim_eligibility` is `false`.

## E005-v1 exploratory reanalysis

The audit reuses hash-pinned E001/E002 inputs and preserves all original files.
Run `e005-20261022-001`, implementation 167f721, result/verification 8692937.
The four artifacts are one provenance-linked audit set; CSV identities are
resolved through the companion checks JSON and result report.

- [Summary](E005-v1-summary.csv): 39 split/method rows with exact-score
  decomposition, metric values and cluster-statistic diversity.
- [Score groups](E005-v1-score-groups.csv): 12 evaluation probability groups.
- [Checks](E005-v1-checks.json): input hashes, protocol/implementation identity,
  195 signed metric comparisons and bounded alignment/lookup checks.
- [Result](../experiments/E005-benchmark-evidence-audit/results/run-e005-20261022-001.md).

No row or source cache was used as a new pristine holdout. Same-author
reimplementation is self-review, not independent acceptance.
