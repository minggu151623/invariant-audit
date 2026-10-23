# M28 — bounded computation beyond raw enumeration

Date: 2026-10-23. Status: valid constructed algorithm study. Goal remains active.
The preceding E009/M27 result made scientific progress; this continues it.

E010 protocol fbd04cbe13bd9d71cc84a4a97a278b4739c910bc precedes implementation
2212b58b9be55536417765e96ae93ac7242c54cf and single run e010-20261023-001.
All 162 raw-domain oracle preflight cases pass. The 72 fixed benchmark tables
give 288 method observations with two order-balanced repetitions.

All specialized calls certify exact answers. The generic raw-cell-factorized
MILP certifies 130/144 observations; 14 hit its one-second search limit across
seven dense-accepted cases. All 14 timeout incumbents are retained and feasible;
none is labeled exact. There is no optimal-cost disagreement or validation
failure. This is a constructed computational result, not external validation.

The accepted formula is much cheaper than building/solving the generic model.
For rejected cases, all 24 pairs are exact twice; median case-level time ratio
generic/specialized is 2.9967. One specialized case is slower (124.92 vs
81.27 ms). Larger action spaces can still be unfavorable. See the complete
[analysis](../experiments/E010-directional-scaling/analysis.md),
[run record](../experiments/E010-directional-scaling/results/run-e010-20261023-001.md)
and [checks](../data/E010-v1-checks.json).

The [figure](../figures/E010/paired-latencies.png) displays all 65 cases where
both methods certify exact answers in both repetitions; its caption explicitly
retains the seven censored cases in the source data. It is a post-run plot,
not another study execution.

Current candidate contribution: the exact canonical accepting-action reduction
and singleton-bottleneck rejection theorem for same-RHS plurality decisions
with editable context keys. Useful performance in this narrow design supports
continuing; it does not establish originality, data correctness or practical
prevalence. Next lock a source-table study and compare closest prior theorems,
then prepare a contribution-centered manuscript. Do not use old-draft owner
review or peer-review acceptance to block that research.
