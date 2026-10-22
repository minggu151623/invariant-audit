# Auditing Invariant Validation Benchmarks: Construction, Error Attribution, and Probability Scores

**Trần Vũ Bảo Minh**\
Independent Researcher

Working manuscript, 23 October 2026. Author review and independent scientific review are pending. Scientific conclusions are restricted to the constructions described below.

## Abstract

Invariant-aware validators can outperform structural baselines on constructed errors without establishing their performance against independently supplied corrections. We audit two finite synthetic designs and add a predeclared study on three external reference datasets. A separate metric implementation reproduces 195 overall comparisons in the synthetic artifacts. Exact finite score-group Brier decomposition attributes lower Brier to higher resolution even as empirical reliability worsens; perfect binary decisions give zero Brier and ECE. One statistic signature among 64 clusters explains degenerate resampling in the first design, while the second has six signatures among 48 clusters. The external study evaluates 11,144 cells using four fixed rule-attribution policies, with calibration-only lookup and 10,000 paired component-bootstrap replicates. On Flights, flagging every participant in a dependency conflict rejects 74.4% of reference-correct cells. A minority-value policy reduces this to 8.0% while accepting 12.2% of reference-incorrect cells. The prediction that lookup improves minority-policy Brier across all three datasets is mixed: the Flights interval crosses zero. The findings distinguish constraint-conflict detection, error localization and probability scoring. They constitute a reproducible case study, not a new detector, a causal transfer experiment or population performance evidence.

## 1. Introduction

A structural validator may verify required fields and primitive types, while an invariant checker may also compare identities, conservation relations or state transitions. A benchmark that injects violations of the additional relations will often favor the invariant-aware method. The scientific question is what that comparison establishes beyond correct handling of the selected construction.

We examine our own benchmark artifacts, rather than an unrelated deployed system. The initial comparison produced large improvements and perfect invariant-aware decisions. However, benchmark truth, fault inventory and validator were developed under closely related specifications. Probability-score improvements were also easy to overinterpret: lower Brier scores appeared alongside higher expected calibration error (ECE). An attempted extension to public event fixtures later stopped before evaluation because its source contract rejected repeated IDs.

We ask four questions. RQ1: do separately recomputed metrics support the finite comparisons? RQ2: which components explain probability-score changes? RQ3: what do repeated cluster statistics imply about uncertainty? RQ4: how do rule attribution and lookup scoring behave when cell labels come from outside reference corrections? The last question adds external evidence without treating a different task and checker as a causal transfer test of the original M1.

The contribution combines a traceable case study, a standalone artifact audit and conditional explanations of the observed behavior. Invariant checking, the oracle problem, Brier decomposition and calibration caveats are established ideas. We do not present them as new. The empirical contribution is their application to these particular versioned constructions, including a negative calibration finding, external attribution tradeoffs and a preserved mixed prediction. An earlier invalid external-fixture attempt is retained in the provenance.

## 2. Related work and position

Schelter et al. [1] combine declarative data-quality constraints with user-defined checks and scalable execution. Breck et al. [2] study validation for machine-learning data pipelines. Practical validation thus extends beyond primitive record shapes; our narrow structural baseline does not represent all schema languages or data-quality systems. We make no comparative performance claim against these systems.

Barr et al. [3] examine the difficulty of deciding whether observed software behavior is correct. Our case illustrates a related distinction: separate implementations of an oracle and checker reduce shared-code risk while potentially retaining a shared specification. Agreement does not establish that this specification captures an external task.

Murphy [4] separates probability-score behavior into reliability, resolution and uncertainty. We use an exact finite binary score-group form and provide its algebra below. Guo et al. [5] study confidence calibration; Nixon et al. [6] examine how calibration-measure choices affect conclusions. Our validators are deterministic rule systems, not neural networks. These sources ground measurement terminology rather than supply evidence about our methods. Our ECE compares positive-class probability with observed positive frequency, not maximum-class confidence with classification correctness.

Raha [8] provides external dirty/reference tables and already cautions that participating in a dependency violation need not make a cell incorrect. Jung et al. [9] show that error sampling choices can change cleaning results. Those broad concerns are therefore prior work, not discoveries claimed here. Our narrower contribution joins explicit score decomposition, repeated-cluster diagnostics and predeclared rule-attribution contrasts in one traceable case study. The external policies are transparent diagnostic baselines, not competitors to the Raha system.

This is a focused comparison with relevant foundations, not a systematic literature review. The case documents an instance of known measurement concerns, with arithmetic that can be checked from frozen rows. It does not establish a new general limitation of validation systems.

## 3. Designs and evidence status

### 3.1. Methods and positive class

The positive class is **valid**. A false positive is an invalid case accepted; a false negative is a valid case rejected. We use

$$
\mathrm{BA}=\tfrac12\left(\frac{TP}{TP+FN}+\frac{TN}{TN+FP}\right),\quad
\mathrm{FPR}=\frac{FP}{TN+FP},\quad \mathrm{FNR}=\frac{FN}{TP+FN}.
$$

B0 applies each protocol's structural rules. M1 adds its selected semantic and state relations. The no-semantic and no-state ablations remove the corresponding predicates. The no-calibration ablation preserves M1's decisions and reports each binary decision as its probability. B0 is deliberately limited; the study does not show that relational validation is impossible with richer schemas or existing constraint systems.

Each calibrated method fits a calibration-only lookup on raw score $s$:

$$
\widehat p(y=1\mid s)=\frac{k_s+1}{n_s+2},
$$

where $n_s$ is the calibration score-group size and $k_s$ its positive count. An unseen score uses the formula on all calibration cases. This is Laplace-smoothed empirical lookup, not isotonic regression. It does not change classification decisions.

### 3.2. Synthetic constructions

E001 creates entity, ledger and event bundles with identity, conservation, transition-legality and revision-consistency relations. Its complete synthetic oracle is coupled to its recipes. E002 adds six heterogeneous cluster types, bounded multiple-fault recipes and a separately implemented replay/conservation oracle. Omitted conservation, overconstraints and stale transitions are deliberate specification stressors.

Table 1. Original case counts and evaluation clusters. Clusters group related cases from one constructed base or template instance.

| Design | Development | Calibration | Evaluation | Evaluation clusters |
| --- | ---: | ---: | ---: | ---: |
| E001 | 256 | 256 | 512 | 64 |
| E002 | 228 | 228 | 456 | 48 |

The evaluation split is historically named `confirmatory`. Original protocols were locked before their valid runs. E005, the audit in this paper, was locked after those results had been inspected and is explicitly exploratory. It does not create an untouched replication. E002's earlier invalid run is excluded; its valid run followed a report-validator correction preserved in the repository.

### 3.3. Earlier external-fixture attempt

E003-v1 selected three fixed GH Archive hourly files [7], with 67,145, 90,940 and 117,780 records. It planned oracle-filtered clean bases and artificial mutations. Even success would not estimate naturally occurring error prevalence. The run stopped on repeated event IDs in the 2021 file before generating predictions or performance metrics. It supplies no external hypothesis outcome.

A separately locked E004 diagnostic found 537 extra occurrences in 537 groups of size two. Every extra occurrence matched its first raw line byte for byte, excluding line endings. No conflicting repeated-ID group or cross-file repeated ID was found in these files. The cause of the duplicates is unknown. E003-v2's revised policy is informed by those observations and remains unexecuted; reused sources cannot become a pristine holdout by renaming a split. We retain the failed attempt as a limitation.

## 4. Exploratory audit protocol

E005-v1 was committed before implementation and one data execution. Its four immutable inputs contain 5,120 E001 and 7,296 E002 prediction rows, plus 75 and 243 metric rows. SHA-256 pins are verified before parsing. The audit imports neither original metric implementation and does not rerun the old experiments or bootstraps.

Serialized probabilities are parsed as exact decimal rationals. The audit rejects duplicate JSON or case/method keys, invalid types, incomplete method coverage, and per-case disagreement in truth, input hash or cluster identity. It checks split disjointness of bases/clusters and counts cross-split input-hash overlap. None was found here; that does not exclude every form of leakage.

Every overall split/method row is checked. Confusion counts must agree exactly; absolute metric tolerances are $10^{-9}$ for E001 and $2\times10^{-9}$ for E002, allowing serialization and displayed rounding. ECE uses ten equal-width bins, lower bound included and upper bound excluded, except that the final bin includes 1:

$$
\mathrm{ECE}_{10}=\sum_{b=0}^{9}\frac{N_b}{N}|\overline p_b-\overline y_b|.
$$

The audit reconstructs lookups using calibration rows only and checks every stored probability. Success establishes compatibility with that rule, not historical proof of which rows were used during fitting. Binary-ablation probabilities must equal decisions exactly.

For each distinct serialized probability $p_g$, let $w_g=N_g/N$ and let $f_g$ be its group's observed positive frequency. With overall frequency $\bar y$,

$$
\begin{aligned}
\mathrm{REL}&=\sum_g w_g(p_g-f_g)^2, &
\mathrm{RES}&=\sum_g w_g(f_g-\bar y)^2,\\
\mathrm{UNC}&=\bar y(1-\bar y), &
\mathrm{BS}&=\mathrm{REL}-\mathrm{RES}+\mathrm{UNC}.
\end{aligned}
$$

These are exact score groups, not ECE bins. Within-group mean squared error is $(p_g-f_g)^2+f_g(1-f_g)$. Weighted outcome variances satisfy

$$
\sum_g w_g f_g(1-f_g)=\bar y(1-\bar y)-\sum_g w_g(f_g-\bar y)^2.
$$

Substitution proves the stated binary Brier identity. The audit requires zero rational residual. This finite-sample identity does not make REL a consistent population-calibration estimate in arbitrary small or singleton groups.

For each method, we also count distinct cluster-statistic signatures: TP/TN/FP/FN, summed squared probability error, and each ECE bin's count, probability sum and truth sum. IDs and row order are omitted. This diagnoses statistic diversity and does not estimate effective sample size.

The implementation passed 21 synthetic tests, covering mixed-label score groups, bin boundaries, lookup fallback, rounding and late write failures. All four outputs are built twice and compared byte for byte before the report is published last. Tests and the separate implementation share an author and environment; independent scientific acceptance remains absent.

## 5. Results

### 5.1. Metric agreement and finite performance

All 195 overall split/method metric comparisons pass. Maximum absolute differences from frozen CSV values are $1.013\times10^{-15}$ for E001 and $4.706\times10^{-10}$ for E002. Confusion counts agree exactly. Alignment, split disjointness and lookup-compatibility checks pass. Every one of the 39 split/method rows satisfies the Brier identity exactly.

Table 2. Evaluation metrics recomputed from frozen rows. Binary is the no-calibration ablation with unchanged decisions.

| Design | Method | BA | FPR | FNR | Brier | ECE |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| E001 | B0 | 0.500000 | 1.000000 | 0 | 0.25000000 | 0 |
| E001 | M1 | 1.000000 | 0 | 0 | 0.00005917 | 0.00769231 |
| E001 | Binary | 1.000000 | 0 | 0 | 0 | 0 |
| E002 | B0 | 0.598039 | 0.803922 | 0 | 0.09193743 | 0.00740887 |
| E002 | M1 | 1.000000 | 0 | 0 | 0.00024790 | 0.01263163 |
| E002 | Binary | 1.000000 | 0 | 0 | 0 | 0 |

The original 10,000-replicate paired cluster bootstrap gives E001 point intervals for BA difference 0.5 and FPR difference -1. E002 intervals are [0.383254717, 0.422077922] for BA difference and [-0.844327177, -0.767281106] for FPR difference. FNR difference is zero in both designs. These are original finite-design intervals, not new E005 estimates for a sampled deployment population.

In E002, omitted conservation yields FPR 0.117647; overconstraint and stale-transition checkers each yield FNR 0.833333. These bounded failures expose dependence on the selected contract. They do not establish robustness to arbitrary incorrect specifications.

### 5.2. Resolution explains lower Brier

Table 3. Exact-score decomposition on evaluation rows. Lower REL indicates lower empirical group reliability loss; higher RES distinguishes groups with different outcome frequencies. Display rounding can obscure the exact identity.

| Design | Method | REL | RES | UNC | Brier |
| --- | --- | ---: | ---: | ---: | ---: |
| E001 | B0 | 0 | 0 | 0.250000000 | 0.250000000 |
| E001 | M1 | 0.000059172 | 0.250000000 | 0.250000000 | 0.000059172 |
| E002 | B0 | 0.000112121 | 0.002357518 | 0.094182825 | 0.091937429 |
| E002 | M1 | 0.000247903 | 0.094182825 | 0.094182825 | 0.000247903 |

E001 B0 reports 0.5 on a balanced evaluation set: ECE and REL are zero but resolution is absent. M1 separates labels perfectly, increasing RES to 0.25. Smoothed probabilities remain inside the endpoints, giving positive REL. The resolution increase dominates the Brier change.

In E002, RES increases by approximately 0.091825308 and REL by 0.000135781. The net Brier change is approximately -0.091689527. Lower Brier therefore coexists with worse empirical score-group reliability and higher ten-bin ECE. This is a result about these rows, not population calibration.

![Evaluation Brier decomposition: bars show REL, minus RES and UNC; dots mark their sum, the Brier score. A separate reliability panel reveals its small increases. Source: E005-v1-summary.csv, evaluation rows.](arxiv/images/brier-decomposition.pdf)

### 5.3. Statistic diversity and uncertainty

For every method, E001 has one distinct signature among 64 evaluation clusters. Every bootstrap draw therefore repeats the same vector in the same number of clusters. More replicates cannot introduce variation absent from the resampling units.

E002 has six signatures among 48 clusters for every method. Variation in baseline behavior permits nondegenerate paired intervals, while perfect M1 decisions persist across its constructed fault inventory. Six signatures alone do not imply six independent observations or an effective sample size of six.

## 6. External-reference validation

### 6.1. Sources, labels and fixed policies

E006 uses the Beers, Flights and Rayyan tables distributed by the Raha project [8], pinned at source commit `7be1334b8c7bbdac3f47ef514fb3e1e8c5fc181c`. They provide outside reference corrections rather than labels derived from our checker. The source paper describes manual cleaning of Beers and owner cleaning of Rayyan; Flights has a reference from earlier work. We do not assume those references are infallible or that every discrepancy arose naturally. Published examples/results and CSV headers were seen before the new protocol; local paired rows and outcomes were not inspected before its lock.

The acquisition first stopped on two differing Beers header names. A separate amendment mapped only those names in metadata, preserving original bytes. We then locked the complete evaluation before reading paired rows. The invalid acquisition record remains preserved.

Cells are normalized as in the source project's reader: HTML unescaping, collapsing tab/newline/ASCII-space runs, and stripping those characters. Reference-correct means equality between aligned normalized dirty and reference strings. This is an operational cell-correction label, distinct from whole-record conformance to a contract. Paired shapes and unique stable keys must match positionally. Only the alignment-key column is excluded; no clean-base filtering, new corruptions or outcome-based sample selection is used. Reference-correct does not imply complete or application-valid: a shared empty value is correct under equality labeling and can still violate U. Rejection of such a cell is a mismatch between task definitions, not necessarily a checker implementation bug.

Four policies use fixed checks selected from the source paper's configurations. U checks nonempty values and two Beers formats. Rall adds ten functional dependencies across the datasets and marks both endpoints in every conflicting group. Rrhs marks all dependent cells only. Rmode marks dependent values outside a unique modal value; modal ties mark all dependent cells. Empty determinants are excluded from relational groups, while empty dependents participate. Complete rules and selectors are fixed in the companion protocol. These policies are neither new methods nor the original synthetic M1.

Crucially, Rall is a conservative suspect set. Evaluating its suspects as incorrect cells tests attribution to the reference task, rather than whether the dependency-conflict detector correctly finds a conflict. A detector can find a real conflict while including correct participants in that suspect set.

Rows sharing nonempty determinant values form connected components, including transitive connections between determinant columns. A fixed hash assigns whole components to development, calibration or evaluation, without label balancing or seed search. Rules can use dirty context within their split: this is transductive, not prediction of isolated future rows. Raw scores are frozen before reference loading and uniquely determine decisions; lookups are fitted only on calibration cells and frozen before evaluation-label comparison. Each policy has a binary-probability ablation with unchanged decisions. The binary variant collapses every nonzero score to probability zero, whereas lookup retains raw-score granularity. Their Brier difference can therefore reflect both resolution and empirical reliability; it does not isolate a calibration-only causal effect.

Table 4. External table inventory and resulting evaluation groups. Only the alignment key is excluded from cells. Component identity derives from dirty values and does not guarantee true-entity isolation under corrupted keys.

| Dataset | Source rows | Columns | Eval. rows | Eval. cells | Eval. components |
| --- | ---: | ---: | ---: | ---: | ---: |
| Beers | 2410 | 11 | 604 | 6040 | 137 |
| Flights | 2376 | 7 | 399 | 2394 | 17 |
| Rayyan | 1000 | 11 | 271 | 2710 | 243 |

The study includes 144 split/scope/method point rows. A direct rational implementation checks five metrics per row. A post-run artifact audit additionally verifies 720 comparisons from exported probabilities and recomputes all 84 interval endpoints from the 840,000 serialized replicate rows. Differences remain below the locked $2\times10^{-12}$ tolerance. Source and artifact hashes, alignment, split grouping and two complete output builds pass. This remains computational self-review by one agent.

### 6.2. Attribution costs and tradeoffs

Table 5. Evaluation cell-correction performance, using the same positive=correct convention. FPR is an incorrect cell accepted; FNR is a correct cell rejected. All four policies are shown; decisions are unchanged between binary and lookup variants, and both Brier scores are reported.

| Dataset | Policy | BA | FPR | FNR | Lookup Brier | Binary Brier |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Beers | U | 0.514317 | 0.968326 | 0.003040 | 0.145639 | 0.179636 |
| Beers | Rall | 0.467899 | 0.937557 | 0.126646 | 0.143813 | 0.275000 |
| Beers | Rrhs | 0.490796 | 0.937557 | 0.080851 | 0.144985 | 0.237583 |
| Beers | Rmode | 0.529094 | 0.937557 | 0.004255 | 0.144029 | 0.175000 |
| Flights | U | 0.710180 | 0.579641 | 0 | 0.155362 | 0.202172 |
| Flights | Rall | 0.627967 | 0 | 0.744067 | 0.124562 | 0.484545 |
| Flights | Rrhs | 0.755933 | 0 | 0.488133 | 0.124562 | 0.317878 |
| Flights | Rmode | 0.898832 | 0.122156 | 0.080180 | 0.085278 | 0.094820 |
| Rayyan | U | 0.448357 | 0.928571 | 0.174714 | 0.088026 | 0.248708 |
| Rayyan | Rall | 0.443972 | 0.917293 | 0.194763 | 0.088007 | 0.265683 |
| Rayyan | Rrhs | 0.449291 | 0.917293 | 0.184124 | 0.088107 | 0.256089 |
| Rayyan | Rmode | 0.444880 | 0.928571 | 0.181669 | 0.087961 | 0.254982 |

The predeclared H6a observation holds: Rall makes at least one reference error in every dataset. On Flights, its correct-cell rejection rate is 74.4067%; Rmode lowers this to 8.0180%, but then accepts 12.2156% of incorrect cells. All three paired intervals for Rmode-minus-Rall FNR are strictly negative, supporting H6c within the fixed design. This does not give a free improvement: FPR rises on Flights and Rayyan. Beers and Rayyan BA remain poor under these limited policies. On Rayyan, U already rejects 17.47% of reference-correct cells, so the fixed nonempty assumption matters alongside FD attribution. Rayyan's paired BA difference interval includes zero.

Table 6. Paired Rmode-minus-Rall error-rate differences, with 95% component-bootstrap intervals. Point differences are proportions, not relative percentage improvements.

| Dataset | Delta FNR | 95% interval | Delta FPR |
| --- | ---: | --- | ---: |
| Beers | -0.122391 | [-0.165432, -0.075702] | 0 |
| Flights | -0.663887 | [-0.708739, -0.605428] | +0.122156 |
| Rayyan | -0.013093 | [-0.023735, -0.004350] | +0.011278 |

### 6.3. A mixed probability-score prediction

Unlike the original perfect M1 constructions, these rule decisions are imperfect relative to reference corrections. Lookup and binary Brier therefore need not follow the same ordering as in E001/E002. H6b specifically predicted a negative upper paired Brier endpoint for Rmode lookup-minus-binary in every dataset. The result is mixed: all point differences are negative, but the Flights interval crosses zero. We preserve that nonconfirmation without changing scores, grouping, lookup, seed or reference values.

Table 7. Rmode lookup-minus-binary Brier differences. All intervals have 10,000 usable paired replicates; the third column determines the predeclared per-dataset H6b criterion.

| Dataset | Point difference | 95% interval | Negative upper endpoint? |
| --- | ---: | --- | --- |
| Beers | -0.030971 | [-0.034230, -0.028009] | Yes |
| Flights | -0.009542 | [-0.020857, +0.001384] | No |
| Rayyan | -0.167021 | [-0.189690, -0.145099] | Yes |

![Paired external-reference contrasts with 95% component-bootstrap intervals. Left: Rmode lookup-minus-binary Brier; Flights crosses zero. Right: Rmode-minus-Rall false rejection of correct cells. Lower false rejection accompanies higher false acceptance on Flights and Rayyan, as Table 6 shows. Source: frozen E006 metrics and intervals.](arxiv/images/external-reference-contrasts.pdf)

These intervals resample fixed dirty-defined components, not a representative population of applications. Seventeen evaluation components in Flights limit interpretation. The study does not identify a causal synthetic-to-real performance change: its policies, task units and label definition differ from those of M1. It supplies a controlled, reproducible external-reference contrast for attribution and scoring.

## 7. Conditional explanations and falsification

### 7.1. Agreement on constructed support

Let $S$ be finite evaluated support with oracle labels $O(x)$. If checker $V$ agrees with $O$ on every $x\in S$, and both labels occur, then FP=FN=0 and BA=1 on $S$. This follows directly from the confusion definitions and makes no statement about $x\notin S$.

When one specification supplies labels and injected violations, perfect agreement may show conformance to that construction without validating the specification against external truth. This is conditional: separate oracle code does not force perfect agreement, and either implementation could be wrong. Our empirical result is rowwise agreement; attributing its limited external reach to shared design is an interpretation. Independently supplied labels exposing disagreements would falsify an extension of agreement beyond $S$.

### 7.2. Smoothing a perfect binary predictor

Suppose each raw-score group has a common label in both calibration and evaluation. With $n_g$ calibration cases, smoothing predicts $1/(n_g+2)$ or $1-1/(n_g+2)$. Each evaluation error is then $1/(n_g+2)^2$, while the perfect binary predictor has zero error:

$$
\mathrm{BS}_{\mathrm{smooth}}=
\sum_g\frac{N_g^{\mathrm{eval}}}{N^{\mathrm{eval}}}\frac{1}{(n_g+2)^2}>0.
$$

If each ECE bin combines only groups whose errors have the same sign, ECE is the corresponding weighted average of $1/(n_g+2)$. These formulas concern lookup probabilities before serialization; the audit checks stored decimals within declared tolerances. The observed pure M1 probability groups exhibit this pattern. It does not show that smoothing is harmful under noise, score overlap, sampling uncertainty or deployment shift. Hard probabilities are not justified without knowledge that agreement continues outside the evaluated support.

### 7.3. Repeated-cluster resampling

If all clusters have the same sufficient-statistic vector, drawing the original number of clusters always gives the same sum. Any statistic computed solely from that sum is constant. This explains E001's degenerate intervals without implying that deployment error is known. A distinct vector changing the aggregate would falsify this explanation; none occurs in the locked E005 measurement.

## 8. Threats to validity and implications

The study covers two hand-designed benchmark families and three fixed external reference datasets. They are not randomly sampled tasks, validators or error mechanisms. E001 truth is recipe-coupled; E002's separate oracle shares its specified world with M1. E005 questions were motivated by already inspected results. Locking E005 prevents subsequent protocol adjustment but cannot remove this exploratory selection.

Exact arithmetic addresses numerical agreement, not specification correctness or independent review. One author can reproduce a conceptual error in multiple implementations. Hashes establish identity and lookup reconstruction establishes compatibility; neither proves universal absence of leakage or historical fitting order.

REL can misleadingly suggest calibration quality in small score groups; ECE can hide within-bin heterogeneity. Their direction agrees here but both limitations remain. Class balance and selected corruption mix shape the results. Original intervals are conditional on synthetic constructions, not a deployment population.

External provenance alone does not supply correctness labels: oracle-filtering records and injecting violations, as originally planned in E003, would remain controlled-error evaluation. E006 instead uses outside reference corrections, but their completeness and semantic correctness are not independently adjudicated here. Normalization makes some formatting differences non-errors; stable keys and dirty-defined components may still imperfectly represent real entities. Rules are deliberately simple, their context is transductive, and no Raha or state-of-the-art comparison is performed. Rall's suspect-set objective must not be silently equated with precise cell localization. Neither E006 nor E003 establishes transfer performance of the original M1 or state-machine validity.

The practical implication is to report decision errors, score components, specification dependence and resampling diversity together. These are interpretive checks, not universal numeric acceptance thresholds. A wider study of independent labels and additional validator families would be needed to establish how common these effects are.

## 9. Conclusion

The synthetic B0/M1 differences survive a separate metric reimplementation, but score decomposition and repeated cluster statistics narrow their meaning. An additional locked external-reference study exposes the difference between finding a relation conflict and locating incorrect cells: reducing conservative rejection can increase false acceptance. Lookup scoring is useful at the point estimates in the selected imperfect-decision cases, yet a fixed prediction of improvement in all three datasets is not supported by all intervals. The contribution is a finite, auditable account of construction, attribution and probability scoring. Original M1 transfer, reference-label infallibility and representative deployment performance remain unestablished.

## Reproducibility and provenance

The local companion artifact preserves original predictions, metrics, protocols and valid result records. E005 protocol commit is `2e6f7c2ec236ebce2bf72f3a026b2ea6de3a80e1`; implementation commit is `167f721565d68cc80b54340a3533e3b414deedd8`; result and bounded computational verification are recorded at `8692937` and milestone M18. It produces 39 summary rows, 12 score groups and a JSON check record with 195 signed differences and input identities.

For E006, protocol commit is `0a0d6ac712422192b90cda02634f8d6084bf06d3`, implementation is `aa8e553580af9e368780f6c4b68a4bd8eadb7bf6`, and result/verification is `5adbb14` (M20). Its reference source commit, manifest and all input byte hashes are retained; predictions contain coordinates and labels but no raw cell strings. E006 has 193,424 base prediction rows, 144 point rows, 840,000 bootstrap rows and 84 intervals.

Use separate checkouts at the respective implementation commits, with the exact pinned source cache for E006. The commands are:

```
python3 experiments/E005-benchmark-evidence-audit/code/audit.py
python experiments/E006-external-reference-validation/code/run_e006.py
```

E005 uses the standard library. E006 additionally uses Python 3.13.5 and NumPy 2.1.3. Both check pinned inputs, compare two complete output builds and refuse existing destinations. Figures derive from frozen summaries and intervals; raw reference cell strings and GH Archive payloads are not included. Independent assessment, owner-reviewed author metadata and public release of the new analysis remain pending.

## Use of generative AI

Generative AI tools were used substantially for research planning, code implementation, audit analysis and manuscript drafting. The original harnesses and the separate metric audit share AI authorship and an environment; agreement is not independent human validation. This working draft still requires responsible human author review before submission.

## References

1. Sebastian Schelter, Dustin Lange, Philipp Schmidt, Meltem Celikel, Felix Biessmann and Andreas Grafberger. 2018. *Automating Large-Scale Data Quality Verification*. PVLDB 11(12), 1781-1794. DOI: 10.14778/3229863.3229867. [Publisher paper](https://www.vldb.org/pvldb/vol11/p1781-schelter.pdf).
2. Eric Breck, Marty Zinkevich, Neoklis Polyzotis, Steven Whang and Sudip Roy. 2019. *Data Validation for Machine Learning*. Proceedings of SysML. [Author organization record](https://research.google/pubs/data-validation-for-machine-learning/).
3. Earl T. Barr, Mark Harman, Phil McMinn, Muzammil Shahbaz and Shin Yoo. 2015. *The Oracle Problem in Software Testing: A Survey*. IEEE TSE 41(5), 507-525. DOI: 10.1109/TSE.2014.2372785. [Institutional record](https://discovery.ucl.ac.uk/id/eprint/1471263/).
4. Allan H. Murphy. 1973. *A New Vector Partition of the Probability Score*. Journal of Applied Meteorology 12(4), 595-600. DOI: 10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2. [Publisher record](https://journals.ametsoc.org/view/journals/apme/12/4/1520-0450_1973_012_0595_anvpot_2_0_co_2.xml).
5. Chuan Guo, Geoff Pleiss, Yu Sun and Kilian Q. Weinberger. 2017. *On Calibration of Modern Neural Networks*. PMLR 70, 1321-1330. [Proceedings paper](https://proceedings.mlr.press/v70/guo17a.html).
6. Jeremy Nixon, Mike Dusenberry, Ghassen Jerfel, Timothy Nguyen, Jeremiah Liu, Linchuan Zhang and Dustin Tran. 2020. *Measuring Calibration in Deep Learning*. arXiv:1904.01685v2 (first submitted 2019). [Author manuscript](https://arxiv.org/abs/1904.01685v2).
7. GH Archive. *Public GitHub timeline archive*. Accessed 22 October 2026. [Official project](https://www.gharchive.org/).
8. Mohammad Mahdavi, Ziawasch Abedjan, Raul Castro Fernandez, Samuel Madden, Mourad Ouzzani, Michael Stonebraker and Nan Tang. 2019. *Raha: A Configuration-Free Error Detection System*. SIGMOD, 865-882. DOI: 10.1145/3299869.3324956. [Author manuscript](https://raulcastrofernandez.com/papers/raha.pdf).
9. Philipp Jung, Sebastian Jäger, Nicholas Chandler and Felix Biessmann. 2025. *Towards Realistic Error Models for Tabular Data*. ACM Journal of Data and Information Quality 17(4), article 28, 27 pages. DOI: 10.1145/3774914. [Author record](https://foundationmodels.bht-berlin.de/publication/jung-2025-realistic-error-models/).

## Appendix A. Fixed external configuration

The three source pairs are `datasets/beers/dirty.csv` and `clean.csv`, and the analogous pairs under `datasets/flights/` and `datasets/rayyan/`, at the full Raha source commit identified above. Each pair must preserve row order and its unique stable key. Beers clean headers `beer-name` and `brewery-name` are explicitly aligned to dirty headers `beer_name` and `brewery_name`; values are never rewritten. Other original source spellings are retained.

The exact alignment keys and dependency inventory are:

- Beers: key `index`; `brewery_id` determines `brewery_name`, `city`, and `state`.
- Flights: key `tuple_id`; determinant `flight`.\
  Dependents: `sched_dep_time`, `act_dep_time`, `sched_arr_time`, and `act_arr_time`.
- Rayyan: key `id`; `jounral_abbreviation` determines `journal_title` and `journal_issn`; `journal_issn` also determines `journal_title`.

U counts one failure for an empty evaluated value. On Beers it counts an additional failure when `brewery_id` does not match ASCII digits or `state` does not match exactly two ASCII letters. No numeric range, date format, learned dependency or additional domain rule is included. A policy's raw score counts all applicable unary and dependency flags, and its decision is valid exactly when that count is zero. Rall/Rrhs/Rmode differ only in the attribution policies specified in Section 6.1.

Within each dataset, rows are joined when they share a nonempty value in any determinant column; union is transitive. Let $k$ be the lexicographically smallest normalized alignment key in a component. Its identity is SHA-256 of the UTF-8 key. The split bucket is the hexadecimal SHA-256 integer of `E006-v1|split|dataset|component_key`, modulo 4, with the actual dataset name and $k$ substituted. Buckets 0/1 are development, 2 calibration, 3 evaluation. There is no rebalancing or seed search.

Calibration pools all evaluated columns per dataset and policy; it uses only calibration labels. Each raw-score probability is $(k_s+1)/(n_s+2)$ with a calibration-wide fallback for unseen scores. The secondary scope is the union of dependency endpoint columns, using the same already-fitted probabilities. No scope-specific lookup is refitted.

For evaluation bootstrap, component identities are sorted. Draw position $j$ of replicate $r$ is the hexadecimal SHA-256 integer of `E006-v1|bootstrap|dataset|r|j`, modulo the component count. Indices start at zero; each replicate draws the original number of components with replacement. The same draw is paired across every method. Percentile intervals use linear interpolation at 0.025 and 0.975. Missing denominators are NA and counted; the stated H6 criteria require 10,000 usable replicates. There is no multiplicity correction or pooled cross-dataset interval.

The fixed interval inventory covers lookup-policy pairs Rall-U, Rrhs-U, Rmode-U and Rmode-Rall for BA, FPR, FNR, Brier and ECE, plus each policy's lookup-minus-binary pair for Brier and ECE. This yields 28 intervals per dataset. The full protocol, reference normalization, input hashes, numeric tolerances and failed acquisition lineage remain in the companion artifact.
