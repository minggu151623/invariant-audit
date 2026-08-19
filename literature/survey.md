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
