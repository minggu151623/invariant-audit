# M20 — fixed external-reference validation

Date: 2026-10-22. Status: `verified_within_fixed_external_reference_design`.
Verification scope: source identity, locked execution and numerical/delivery
self-review. Independent scientific acceptance remains absent.

## Source and protocol lineage

Source repository BigDaMa/raha at 7be1334b8c7bbdac3f47ef514fb3e1e8c5fc181c.
A1 (0177cc2) downloaded nine fixed files but correctly failed on two Beers
header names, before row/reference inspection. Its invalid record is retained.
A2 (d83c5aa) allowed exactly the two observed clean-header aliases, preserving
source bytes; metadata recovery implementation 573d2de verified all nine pins.
The canonical source manifest SHA-256 is
96e7529355eac100de47f2c957b8a1a5252d4c220c285d5fd46d871d62716342.

Evaluation E006-v1 was locked at 0a0d6ac712422192b90cda02634f8d6084bf06d3
before reading paired source rows. Implementation commit:
aa8e553580af9e368780f6c4b68a4bd8eadb7bf6; 22 synthetic tests passed.
One run e006-20261022-001 completed; all six outputs had byte-identical double
builds. No protocol, rule, split/seed, source or reference was changed after
seeing outcomes. [Run report](../experiments/E006-external-reference-validation/results/run-e006-20261022-001.md).

## Data and verification

Beers has 2410 rows/11 columns, Flights 2376/7 and Rayyan 1000/11. Excluding
only their stable alignment keys leaves 48356 source cells overall. Evaluation
uses 6040/2394/2710 cells in 137/17/243 dirty-defined components, respectively.
The setting is dirty-only transductive FD context, with group-disjoint splits;
no labels are used to select/score samples. Reference keys and positions align.
Outside corrections supply cell labels; those labels are not infallible truth.

Artifacts: 193424 coordinate-only base prediction rows, 144 point rows, 840000
bootstrap rows and 84 intervals. Post-run delivery verification recomputed 720
point-metric comparisons and all 84 quantiles from serialized artifacts, checked
all nine source pins and gzip/row inventories, and passed within 2e-12. Maximum
exported point difference: 9.180468885094939e-13; interval difference:
8.999884171245753e-13. See [verification](M20-delivery-verification.json).
All 84 blocks have 10000 usable replicates. These are fixed-design intervals.

## Observed outcomes

- H6a: supported in all three fixed datasets: Rall has reference errors.
- H6b: mixed/not supported. Rmode lookup-minus-binary Brier has paired 95% CIs
  Beers [-0.034229895120,-0.028009386577], Flights
  [-0.020856647269,0.001384390231], Rayyan
  [-0.189690415701,-0.145098822976]. Flights crosses zero despite lower point Brier.
- H6c: supported within the fixed design: Rmode reduces FNR relative to Rall
  in all three. Their delta-FNR CIs are respectively
  [-0.165432203925,-0.075701652011], [-0.708738871806,-0.605427974948], and
  [-0.023735408560,-0.004349622750]. This is not free improvement: delta FPR
  is 0, +0.122155688623 and +0.011278195488 at the point estimates.

On Flights, Rall rejects 74.4067% of correct cells; Rmode rejects 8.0180% but
accepts 12.2156% of erroneous cells. Beers Rmode BA=0.529094 and Rayyan
BA=0.444880, so these simple policies are poor cell-localization baselines in
those datasets. Rmode-minus-Rall BA on Rayyan has CI
[-0.011559901122,0.009764943889], not a demonstrated directional improvement.
All outcomes and alternative methods remain reported, including these failures.

## Interpretation boundaries

Rall is a conservative suspect set: involvement in a relation conflict is not
the same task as localization of incorrectly corrected cells. The experiment
measures attribution against the outside reference, not correctness of the FD
conflict detector itself. This general issue was already noted by the Raha
paper; the present contribution is a transparent quantitative case extension.

The methods are not E001/E002 M1 or Raha; cross-design performance differences
do not identify causal transfer failure. No new error detector, state-machine
transfer, representative error prevalence or deployment claim follows.
Published examples and headers were inspected; classification is predeclared
external-reference validation, not wholly blind confirmation. Float64 statistic
signature counts in checks are implementation diagnostics and are not used as
exact signature-equivalence or effective sample-size claims in the manuscript.

The prior two-construction paper can now be broadened with externally supplied
reference labels, an attribution tradeoff and a preserved mixed calibration
prediction. Novelty/archival-interest assessment and responsible owner review
remain open. E003-v2 remains unexecuted at its old gate. No public push or
submission occurred; public_claim_eligibility=false.
