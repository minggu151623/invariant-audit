# M03 — E002 heterogeneous specification stress protocol

Status: protocol locked locally; implementation and execution are not
authorized by this milestone record.

## Authority and provenance

The user message on 2026-08-25 authorizes high-level continuation to design
and locally lock the next outer-loop protocol. It does not select the E002
technical design. The exact continuation text recorded for provenance is:

Design and locally lock the next outer-loop protocol E002

The detailed cluster templates, recipes, independent-oracle boundary,
checker regimes, splits, metrics, H2 rule, bootstrap, size gate, invalid-run
behavior, and stopping rule are reviewer/design inference. They are not
sourced facts, user choices, or E002 observations.

## Locked protocol

- Protocol: [E002-v1](../experiments/E002-heterogeneous-specification-stress/protocol.md)
- Lock subject: research(protocol): lock E002 heterogeneous specification stress
- Required parent: 4494ed80af0dec9b57b183877cb5ed3a8270c3db
- Lock commit: the dedicated self-containing lock commit, whose full hash is
  reported by the final git evidence because the protocol cannot self-embed
  its own commit hash.
- Prior result/reflection: E001 result commit
  31071ddf65ad9a1f0e5b28eb0d501899253cd17b and published reflection commit
  4494ed80af0dec9b57b183877cb5ed3a8270c3db.

The protocol predeclares heterogeneous H0-H5 clusters, valid/single/multi
cases, an independent replay/conservation oracle, schema-only B0, exact-spec
M1, omission/overconstraint/stale-transition regimes, semantic/state and
calibration ablations, disjoint development/calibration/confirmatory splits,
paired cluster bootstrap, metric and output schemas, determinism/leakage/
footprint/size gates, safe staging, invalid-run records, and a finite
stopping rule. It requires no implementation or result in this milestone.

## Source boundary

New technical concepts are grounded only in direct primary or official
sources, with claim mapping in [literature/survey.md](../literature/survey.md):

- specification-based testing and specification mutation:
  Stocks and Carrington at https://doi.org/10.1109/32.553698 and
  Hierons and Merayo at https://doi.org/10.1016/j.jss.2009.06.030
  (direct publisher record:
  https://www.sciencedirect.com/science/article/pii/S0164121209001356)
- independent differential testing:
  https://www.hpl.hp.com/hpjournal/dtj/vol10num1/vol10num1art9.pdf
- heterogeneous clustered inference:
  https://doi.org/10.1162/REST.90.3.414 and
  https://doi.org/10.1080/01621459.2016.1148610
- interaction and multi-fault motivation:
  https://doi.org/10.1109/TSE.2004.24,
  https://doi.org/10.1109/QRS-C.2017.11, and
  https://www.nist.gov/publications/combinatorial-software-testing

Those sources do not supply E002 parameters or results. No source is treated
as evidence that E002 will support H2.

## Verification and absence claims

This is a protocol-only milestone:

- no executable E002 code or implementation exists;
- no E002 run has been executed;
- no E002 experimental data, results/output, figure, or ARA artifact exists;
- this lock does create the documentary protocol, M03 milestone, state,
  research-state pointer, research log, findings, literature notes, and README
  index updates;
- future output paths are reserved by the protocol but absent now;
- run_authorized is false and public_claim_eligibility is false;
- the protocol is synthetic-only and carries no production, external-validity,
  novelty, safety, or generalization claim.

The remediation makes specification stress co-primary with the M1-B0 anchor:
d1 omit-M1 FPR on schema-valid truth-negative conservation cases, d2 over-M1
FNR on valid active-active cases, and d3 stale-M1 FNR on valid pending-closed
cases. d1 uses 48 eligible confirmatory clusters; d2 uses 40 (H0-H4); and
d3 uses 40 (H1-H5). Each
requires a strictly positive lower paired-bootstrap interval. Standard method
rows are 240; diagnostic rows add 3. Bootstrap output is 530,000 replicate
rows plus 53 interval rows and a header, or 530,054 lines, with a
47,710,564-byte upper estimate. Single-class case-kind intervals are
descriptive and may be partial/undefined without blocking H2.

The exact UTF-8/LF serialization, canonical JSON/CSV/Markdown dialect,
nine-place numbers, NA/bool/list/fault-set encodings, row order, manifests,
hash inputs, six known-answer signature vectors, two-build byte gate, and
non-self-embedded final result hash are locked in the protocol. Overconstraint
rejects active-active; stale-transition accepts active-active but omits
pending-closed. The generated H0-C00 valid-base payload has SHA-256
8ddb5fbd84a64ef811a261ad72359f647d0757e8c83c864bd206bbb03b8dd07b and must
yield M1=true, over=false, stale=true; H5-C00 valid-base has SHA-256
97935beb48f281d1d1fe8317d8ee7f300089bd2e6ad523fc06aaaaf47d4c6db3 and must
yield M1=true, over=true, stale=false. Structural signature distinctness
excludes type, and split leakage gates require pairwise-disjoint base-hash,
cluster-ID, and case-ID sets plus within-split uniqueness. The complete
H0-H5 type-to-tuple, cases, signature, and recipe manifest is mandatory at
runtime, including rejection of label, recipe, count, and signature drift.

The next gate is an independently reviewed implementation commit descended
from the lock commit. Any later run requires a new explicit authorization and
must obey the protocol's preflight, determinism, staging, overwrite, and
stopping rules.

The third review remediation removes the result-draft hash from the result
template and internal hash list. Two independent builds compare the complete
rendered report bytes directly, while the finalized report SHA-256 is computed
only externally after finalization; no redacted/preimage form is serialized.
The valid and invalid templates now have a closed placeholder vocabulary with
strict ASCII grammars, fixed semantic sources, exact interval-key membership,
list and empty-list rules, Markdown cell-safety, and static/render gates.
Confirmatory deviations are invalid, so the valid report uses literal `none`,
and the invalid report uses literal `failure_class: invalid-run`.
