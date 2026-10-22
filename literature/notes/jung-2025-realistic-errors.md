# Closely related work: realistic tabular error models

Checked 2026-10-22. Philipp Jung, Sebastian Jäger, Nicholas Chandler and Felix
Biessmann (2025), Towards Realistic Error Models for Tabular Data.
ACM Journal of Data and Information Quality 17(4), article 28, 27 pages.
DOI: 10.1145/3774914.
Primary author record: https://foundationmodels.bht-berlin.de/publication/jung-2025-realistic-error-models/
Official code: https://github.com/calgo-lab/error-paper

The authors model error occurrence separately from error type and demonstrate
that changes in error sampling can substantially change cleaning performance.
This directly overlaps a broad version of our benchmark-construction concern.
The present project must not claim to discover generally that synthetic error
choices affect benchmark results. A narrower possible distinction is the joint
analysis of exact score decomposition, finite repeated-cluster statistics and
rule-to-cell attribution against outside reference labels. This distinction is
an AI-proposed research direction, not established novelty or an observed result.
No tab_err experiment, code installation or runtime comparison was performed.
