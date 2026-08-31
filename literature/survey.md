# Literature survey — E001 foundation

## Scope and provenance

This is a concise documentary foundation for M01/E001, prepared on 2026-08-20
from papers and official technical documentation. It is not a systematic review
and contains no experiment result, benchmark result, novelty claim, or
performance claim. Statements in **Sourced fact** sections describe the linked
source; statements in **Proposed E001 choice** sections are this repository's
design decisions.

## Sourced technical foundation

### Property-based generation and explicit properties

**Sourced fact.** Claessen and Hughes describe QuickCheck as a tool for stating
properties, generating random inputs, and defining custom generators. Their
paper also discusses generator and coverage pitfalls; it does not establish
that a particular synthetic generator is sufficient for this project.

- Claessen, K. and Hughes, J. (2000), *QuickCheck: A Lightweight Tool for
  Random Testing of Haskell Programs*, ICFP 2000,
  [ACM DOI](https://doi.org/10.1145/351240.351266).

### Transformations and metamorphic relations

**Sourced fact.** Segura et al. describe metamorphic testing as checking a
relation induced by transforming a source test input and observing the related
follow-up behavior. This supplies terminology for E001's paired
valid-preserving transformations and fault injections; it is not evidence that
the proposed transformations are valid for any production system.

- Segura, S., Fraser, G., Sanchez, A. B., and Ruiz-Cortes, A. (2016), *A
  Survey on Metamorphic Testing*, IEEE Transactions on Software Engineering,
  [author manuscript and metadata](https://eprints.whiterose.ac.uk/id/eprint/110335/)
  and [IEEE DOI](https://doi.org/10.1109/TSE.2016.2532875).

### Stateful actions and invariants

**Sourced fact.** The official Hypothesis documentation presents stateful
testing as generating sequences of actions and checking state-machine behavior;
it distinguishes chained stateful rules from independent generated examples.
This supports treating legal transitions and revision constraints as a separate
invariant family. The documentation is not evidence about E001's validator.

- Hypothesis documentation, *Stateful tests*,
  [official documentation](https://hypothesis.readthedocs.io/en/latest/stateful.html).

### Probability confidence and calibration

**Sourced fact.** Guo et al. define confidence calibration in terms of
probability estimates representing correctness likelihood. The official
scikit-learn documentation describes calibration curves/reliability diagrams
and warns that Brier score reflects more than calibration alone, including
resolution and uncertainty. These sources motivate reporting Brier score with a
bin-based calibration diagnostic rather than treating one number as proof of
calibration.

- Guo, C., Pleiss, G., Sun, Y., and Weinberger, K. Q. (2017), *On Calibration
  of Modern Neural Networks*, ICML/PMLR 70,
  [paper and citation](https://proceedings.mlr.press/v70/guo17a.html).
- scikit-learn, *Probability calibration*,
  [official documentation](https://scikit-learn.org/stable/modules/calibration.html),
  and [calibration curve API](https://scikit-learn.org/stable/modules/generated/sklearn.calibration.calibration_curve.html).

### Probability score and uncertainty intervals

**Sourced fact.** Brier's original paper introduced a probability-forecast
verification score. NIST describes bootstrap resampling with replacement and
percentile limits as a way to estimate uncertainty when analytic intervals are
inconvenient. E001 adapts that idea to base-case clusters; that adaptation is a
proposed design choice, not a result.

- Brier, G. W. (1950), *Verification of Forecasts Expressed in Terms of
  Probability*, Monthly Weather Review,
  [publisher record and DOI](https://doi.org/10.1175/1520-0493%281950%29078%3C0001%3AVOFEIT%3E2.0.CO%3B2).
- National Institute of Standards and Technology, *Bootstrap Plot*,
  [NIST/SEMATECH e-Handbook](https://www.itl.nist.gov/div898/handbook/eda/section3/bootplot.htm).

### Classification metric definitions

**Sourced fact.** The official scikit-learn metric documentation provides
implementations and definitions for confusion matrices, precision, recall,
specificity-related quantities, Brier score, and balanced accuracy; in the
binary case it gives balanced accuracy as the mean of sensitivity and
specificity. E001 writes the formulas explicitly so its positive class and
undefined-denominator policy are reviewable without depending on a library.

- scikit-learn, *Metrics and scoring* and `sklearn.metrics` API,
  [official user guide](https://scikit-learn.org/stable/modules/model_evaluation.html)
  and [official API reference](https://scikit-learn.org/stable/api/sklearn.metrics.html).

## Proposed E001 design choices

These are not sourced claims. E001 uses a small, deterministic, synthetic
record/state bundle; a complete generator oracle; four semantic/state invariant
families; schema-only baseline B0; invariant-aware method M1; a disjoint
calibration split and confirmatory split; fixed seeds and counts; and paired
cluster-bootstrap intervals. The protocol defines all transformations,
fault injections, metrics, stopping rules, invalid-run rules, and limitations in
[the E001 protocol](../experiments/E001-synthetic-invariant-calibration/protocol.md).

The oracle is deliberately used to establish exact synthetic truth and to
evaluate outputs, not exposed to either validator. The design is intended to
calibrate measurement behavior and false-positive/false-negative bookkeeping;
it does not imply validity, robustness, calibration, or generalization on a
real system.

## Literature boundary

The cited sources ground terminology and measurement choices only. They do not
verify M01, E001, or any future method. No source here supplies observed E001
results, and no content or public claim may be derived from this survey alone.

## E002 source foundation — primary and official sources

This section was added for the E002 outer-loop protocol on 2026-08-25. New
technical claims below are restricted to direct primary research papers or
official technical documentation. The E002 parameters, regimes, recipes,
subgroups, co-primary diagnostics, thresholds, serialization, and gates in the
following sections are reviewer/design inference, not sourced facts and not
user-selected technical design.

### Specification-based testing and specification mutation

**Sourced fact.** Stocks and Carrington present a specification-based testing
framework in which model-based specifications structure test data, test
purposes, and test oracles. Their framework is a research method, not evidence
that any particular specification is correct for E002.

**Sourced fact.** Robert M. Hierons and Mercedes G. Merayo present a primary
study of mutation testing for probabilistic and stochastic finite-state-machine
specifications. It describes mutating the specification and deriving tests
that distinguish the mutated specification from the original, and treats
mutation operators as models of incorrect specifications. This motivates
testing bounded omission, overconstraint, and stale-transition regimes as
deliberate misspecifications, not as accidental post-hoc changes.

- Stocks, P. and Carrington, D. (1996), *A Framework for Specification-Based
  Testing*, IEEE Transactions on Software Engineering 22(11):777–793,
  [IEEE DOI](https://doi.org/10.1109/32.553698).
- Hierons, R. M. and Merayo, M. G. (2009), *Mutation testing from
  probabilistic and stochastic finite state machines*, Journal of Systems and
  Software 82(11):1804–1818,
  [publisher DOI](https://doi.org/10.1016/j.jss.2009.06.030) and
  [ScienceDirect article](https://www.sciencedirect.com/science/article/pii/S0164121209001356).

### Independent and differential oracle mechanisms

**Sourced fact.** McKeeman’s original differential-testing paper frames
differential testing as comparing independently produced program results to
reduce the cost of deciding whether generated tests expose a behavioral
difference. This supports treating an independent reference implementation as
a separate oracle mechanism; it does not prove that two implementations agree
with an external specification.

- McKeeman, W. M. (1998), *Differential Testing for Software*, Digital
  Technical Journal 10(1),
  [official Hewlett-Packard Journal paper](https://www.hpl.hp.com/hpjournal/dtj/vol10num1/vol10num1art9.pdf).

### Heterogeneous clustered evaluation and bootstrap inference

**Sourced fact.** Cameron, Gelbach, and Miller study inference with clustered
errors, including within-cluster dependence and the limitations of ordinary
asymptotics when the number of clusters is small. They evaluate cluster
bootstrap-t procedures in simulations; this is evidence about that statistical
setting, not a guarantee for E002.

**Sourced fact.** Hagemann develops a cluster-robust bootstrap for a setting
with small, heterogeneous clusters and studies its behavior relative to the
number and size of clusters. E002 therefore treats the cluster as the
resampling unit and makes cluster heterogeneity an explicit design dimension;
the exact pairs-bootstrap implementation below remains a repository choice.

- Cameron, A. C., Gelbach, J. B., and Miller, D. L. (2008), *Bootstrap-Based
  Improvements for Inference with Clustered Errors*, Review of Economics and
  Statistics 90(3):414–427,
  [MIT Press record and DOI](https://doi.org/10.1162/REST.90.3.414).
- Hagemann, A. (2017), *Cluster-Robust Bootstrap Inference in Quantile
  Regression Models*, Journal of the American Statistical Association
  112(517):446–456,
  [publisher DOI](https://doi.org/10.1080/01621459.2016.1148610).

### Interaction-triggered and multi-fault behavior

**Sourced fact.** Kuhn, Wallace, and Gallo report an empirical study of
software failures caused by combinations of conditions and discuss the
relationship between bounded interaction strength and combinatorial testing.
The conditional assumptions in their result are not assumed for E002.

**Sourced fact.** Yan, Liu, and Li report an empirical study of multi-fault
programs in which dominant/recessive fault interactions can produce unexpected
failure behavior. This motivates recording intended fault sets separately from
the independently recomputed failure set instead of treating multi-faults as
the sum of isolated single-fault outcomes.

**Sourced fact.** NIST’s official combinatorial-testing record describes
exercising all combinations up to a pre-specified interaction strength as a
way to expose faults triggered by unusual combinations. E002 uses a small,
explicitly bounded interaction recipe set rather than claiming exhaustive
coverage.

- Kuhn, D. R., Wallace, D. R., and Gallo, A. M. (2004), *Software Fault
  Interactions and Implications for Software Testing*, IEEE Transactions on
  Software Engineering 30:418–421,
  [IEEE DOI](https://doi.org/10.1109/TSE.2004.24).
- Yan, X., Liu, B., and Li, J. (2017), *The Failure Behaviors of Multi-Faults
  Programs: An Empirical Study*, 2017 IEEE International Conference on
  Software Quality, Reliability and Security Companion,
  [IEEE DOI](https://doi.org/10.1109/QRS-C.2017.11).
- Kuhn, D. R., Kacker, R. N., Lei, Y., and Hunter, J. (2009), *Combinatorial
  Software Testing*, Computer 42(8),
  [official NIST publication](https://www.nist.gov/publications/combinatorial-software-testing).

## E002 source-to-choice boundary

The sources above support only the bounded concepts named in their respective
source-fact paragraphs: specification-based testing/mutation, differential
comparison, cluster-aware inference under heterogeneity, and interaction-aware
fault testing. The following E002 choices are not sourced conclusions:

- six deterministic heterogeneous cluster templates and 96 total clusters;
- the valid, single-fault, multi-fault, and schema-visible recipe inventory;
- the independent replay/conservation oracle implementation boundary;
- B0, exact-spec M1, three misspecified checker regimes, three ablations, and
  three co-primary specification-stress diagnostics;
- split allocation, metrics, H2 rule, 10,000-replicate pairs cluster bootstrap
  with 530,000 replicate rows and 53 interval rows, schemas, size budget, and
  invalid-run behavior.

The E002 implementation, run, result, and data are recorded elsewhere in the
verified repository history. This survey section adds no E002 executable
implementation or result; it records the source-to-design boundary only.

## E003 source foundation — capped primary and official sources

E003 literature discovery was capped at three directly relevant
primary/official sources. The following sourced facts are intentionally narrow;
the fixture dates, filtering, mutations, methods, oracle, metrics, and gates in
the E003 protocol are worker/reviewer design choices, not conclusions supplied
by these sources.

### GH Archive fixture boundary

**Sourced fact.** The official GH Archive site describes a public GitHub event
timeline and provides timestamped hourly archive files containing raw event
records. It also warns that event payload shape can change. This supports
freezing exact archive URLs and recording byte hashes before parsing; it does
not make a selected shard representative or establish E003 truth.

- GH Archive, official project site, <https://www.gharchive.org/>.

### GitHub event contract

**Sourced fact.** GitHub's official event-types documentation describes common
event fields and per-event-type payloads, including action fields for
`IssuesEvent` and `PullRequestEvent`. E003 uses only a deliberately narrow
subset of those documented shapes; the documentation does not validate the
subset or any future E003 result.

- GitHub, *GitHub event types*, official REST API documentation,
  <https://docs.github.com/en/rest/using-the-rest-api/github-event-types>.

### GitHub-mining validity caution

**Sourced fact.** Kalliamvakou et al. present an empirical study of the
promises and perils of mining GitHub. This motivates explicit source alignment,
selection, and validity checks for an externally sourced fixture; it is not an
E003 dataset, oracle, or result.

- Kalliamvakou, E., Gousios, G., Spinellis, D., et al. (2015), *An in-depth
  study of the promises and perils of mining GitHub*, Empirical Software
  Engineering, DOI <https://doi.org/10.1007/s10664-015-9393-5>.

## E003 source-to-choice boundary

The three sources above ground only the archive/event-contract context and the
need for explicit GitHub-mining validity checks. E003-v1's exact shards
(`2019-01-15-12`, `2020-01-15-12`, and `2021-01-15-12`), staged acquisition
manifest and SHA-256 plan, strict subset contract, repository-isolated
64+64-base quotas, clean/S1/I1/T1 probes, B0/M1 methods, calibration split,
independent oracle, repository bootstrap, artifact schemas, invalid-run rules,
and one-run stopping rule are protocol design choices.

The exact planned fixture URLs are:

- <https://data.gharchive.org/2019-01-15-12.json.gz>
- <https://data.gharchive.org/2020-01-15-12.json.gz>
- <https://data.gharchive.org/2021-01-15-12.json.gz>

The three source files are not acquired in this stage. No source hash, byte
count, line count, HTTP metadata, manifest, E003 implementation, run, result,
prediction, metric, bootstrap, or public claim is asserted. See [the E003-v1
protocol](../experiments/E003-external-transfer-validation/protocol.md) and
[M10](../milestones/M10-E003-protocol-design.md) for the protocol-only gate.
