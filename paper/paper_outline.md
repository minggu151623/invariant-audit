# InvariantAudit Paper Outline & Claim-Evidence Mapping

## Paper Title
**Calibrating Semantic and State Invariants for Software Telemetry: From Synthetic Guarantees to Real-World Stream Irregularities**

## 1. Compact Section Outline

- **Abstract:** Motivation (schema validation is blind to cross-field semantic inconsistencies), proposed methodology (calibrated semantic and state invariants with bounded uncertainty), synthetic results (E001/E002: +40.2% to +50.0% balanced accuracy, -80.4% to -100.0% FPR, 0.0% FNR inflation), real-world empirical transfer finding (E003: GH Archive telemetry contains 0.45% duplicate event delivery, invalidating idealized synthetic uniqueness assumptions), and core insight.
- **Section 1 — Introduction:** The challenge of silent semantic corruption in event-driven architectures. Why structural schema checks (JSON Schema) fail to catch state or identity violations. The dilemma of false alarms vs. false negatives. Contributions of this work.
- **Section 2 — Related Work:** Metamorphic testing, runtime invariant detection (Daikon, DIDUCE), software telemetry verification, and statistical calibration (Platt scaling, isotonic regression).
- **Section 3 — Methodology & Invariant Formulation:**
  - Common schema invariants vs. semantic identity and state invariants.
  - Candidate checkers: B0 (schema-only baseline), M1 (calibrated multi-predicate invariant checker), and ablation variants (M1-no-identity, M1-no-state, M1-no-calibration).
  - Non-parametric isotonic calibration with cluster-aware bootstrap estimation.
  - Fail-closed execution harness with clean-tree and audit reproducibility gates.
- **Section 4 — Experiments & Empirical Findings:**
  - *Experiment 1 (E001):* Finite synthetic baseline under balanced single-fault conditions (M02 evidence).
  - *Experiment 2 (E002):* Heterogeneous specification stress across 96 non-identical clusters and multi-fault regimes (M08 evidence).
  - *Experiment 3 (E003):* Real-world transfer validation on 275,000+ public GitHub Archive events across three annual hourly snapshots (2019, 2020, 2021) (M13 evidence).
- **Section 5 — Discussion, Transfer Gap & Practical Implications:**
  - The "Lab-to-Wild" transfer gap: Why strict synthetic uniqueness assumptions collapse under at-least-once message delivery.
  - The architectural need for two-tier invariant verification: transport/idempotency tier and semantic state tier.
- **Section 6 — Threats to Validity & Limitations:**
  - Known limits: Single-source public telemetry (GH Archive), finite mutation operators, dependence on reference oracle separation.
- **Section 7 — Conclusion:** Summary of findings and roadmap for calibrated runtime invariant monitoring.

## 2. Claim-Evidence Mapping

| Claim | Verified Evidence Source | Status |
|---|---|---|
| **C1:** Schema validation (B0) alone yields high false positive rates (up to 100% on negative cases) and low balanced accuracy (0.50). | E001 confirmatory run `e001-20260825-001` (M02) and E002 confirmatory run `e002-20260825-002` (M08) | **Supported** |
| **C2:** Calibrated semantic and state invariants (M1) improve balanced accuracy by +50.0% (E001) and +40.2% (E002) over B0. | E001 metrics `data/E001-v1-metrics.csv` & E002 metrics `data/E002-v1-metrics.csv` | **Supported** |
| **C3:** M1 eliminates or drastically reduces false positive rate (-100.0% in E001, -80.4% in E002) without increasing false negative rate (point delta FNR = 0.000). | Confirmatory run reports `run-e001-20260825-001.md` and `run-e002-20260825-002.md` | **Supported** |
| **C4:** Ablating identity or state predicates degrades detection power and increases Brier calibration error. | E001 ablation results (M1-no-semantic/state Brier: 0.1667 vs M1: 0.000059) and E002 ablations | **Supported** |
| **C5:** Real-world software event telemetry (GH Archive) exhibits at-least-once delivery duplicates (0.45% in 2021 confirmatory shard), violating idealized synthetic uniqueness assumptions. | E003 confirmatory run `e003-20260903-001` diagnostic audit of 117,780 records in `2021-01-15-12.json.gz` (M13) | **Supported** |
| **C6:** Rigorous fail-closed harness guarantees reproducibility and prevents silent execution contamination. | Automated deterministic two-build byte comparison and hash gates across all experimental harnesses (M01-M13) | **Supported** |

## 3. Five-Dimension Review Checklist

1. **Contribution:** Does the paper introduce a clear, significant conceptual and practical contribution? -> Yes, the synthesis of calibrated semantic invariants with empirical measurement of the synthetic-to-real transfer gap.
2. **Writing Clarity:** Is each paragraph focused on a single clear message with topic sentences? -> Yes, following `research-paper-writing` guidelines.
3. **Experimental Strength:** Are claims supported by locked, reproducible data without overreach? -> Yes, all numbers match verified repository artifacts.
4. **Evaluation Completeness:** Are baselines, ablations, and negative/invalid findings reported honestly? -> Yes, includes B0 baseline, multiple ablations, and full invalid-run analysis of E003.
5. **Method Design Soundness:** Are mathematical formulations (balanced accuracy, Brier score, ECE, isotonic regression) standard and clearly defined? -> Yes.
