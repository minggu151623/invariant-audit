# Paper outline and claim-evidence map

Updated 2026-10-23 after E006/M20. A methods case study combining two finite
synthetic designs and three fixed external-reference tables. No new validation
algorithm, Brier identity, general error-model insight or causal M1 transfer is
claimed. The latter broad ideas have close prior work, now explicitly credited.

1. Motivation and four questions: arithmetic, scores, resampling, attribution.
2. Prior data-validation/oracle/calibration work plus Raha and Jung 2025.
3. Original synthetic designs and the preserved earlier invalid source attempt.
4. Locked exploratory E005 audit and finite Brier identity.
5. Recomputed synthetic metrics, score components and statistic diversity.
6. Locked E006 external-reference design, attribution tradeoffs and mixed H6b.
7. Conditional finite explanations with explicit assumptions.
8. Task/label semantics, transductive setting, common-author and scope limits.
9. Bounded conclusions, exact provenance and generative-AI disclosure.

| Claim | Evidence | Scope |
| --- | --- | --- |
| Original overall metrics reproduce | E005/M18 at 8692937 | 195 comparisons, finite synthetic artifacts |
| Lower Brier coexists with higher finite REL/ECE | E005 summary and exact identity | Score-group arithmetic, not population calibration |
| One statistic signature/64 clusters; six/48 | E005 summary | Exact finite diagnostics, not effective sample size |
| Outside-reference study passes delivery checks | E006/M20 at 5adbb14 | 720 exported point comparisons, 84 quantiles |
| Rmode reduces Rall false rejection | E006 fixed H6c and intervals | Three fixed datasets; FPR tradeoffs retained |
| Lookup benefits all three under fixed H6b | Flights interval crosses zero | Mixed/not supported despite lower point scores |
| Rayyan BA direction improves | Paired CI crosses zero | Not established |
| Reference-correct implies application-valid | Shared blanks can match while violating U | Explicitly rejected inference |
| Lookup/binary comparison isolates calibration | Raw-score resolution also changes | Explicitly rejected causal interpretation |
| External study measures original M1 transfer | Different policies/tasks/units | Not established or claimed |
| New general insight about error-model/attribution effects | Raha/Jung prior work | Not claimed as novel |

Figure 1 maps to E005 summary; Figure 2 maps to E006 fixed primary intervals.
All original protocols, failed attempts and source metadata are preserved.
See review-status.md for archival-interest and owner/public-release gates.
