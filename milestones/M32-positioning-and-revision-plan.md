# M32 plan: direct positioning and a bounded theoretical revision

Date: 2026-11-05. Owner resumed the original arXiv goal and said
"được rồi tiếp đi" after the internal revise-before-submission assessment.
The previous substantive turn was progress: it identified a missing close
reference and produced an actionable scientific self-assessment. The resumed
blocked audit starts fresh; no current local-work blocker is established.

Use autoresearch's outer-loop reflection. This is local research/revision
authority, not content approval, license selection or authority to publish.
No subagents, paid calls, external messages or submission actions.

## Work and deliverables

1. Compare definitions and named results in Debosschere/Geerts (TaPP 2015),
   Bertossi v7 (2020), Xia v3 and Meliou et al. (2011) using primary sources.
   Distinguish generic representability from an explicit specialization theorem.
2. Derive illustrative families separating whole-table FD repair distance from
   protected-target plurality decision distance. They are analytical examples,
   not a claim that separation itself is new or a substitute for usefulness.
3. Check the small instances below by raw categorical destination enumeration,
   separately checking global FD consistency and the target's plurality decision.
   Freeze this plan before implementation, and implementation before execution.
4. Revise the manuscript as a new dated local project. Preserve M30/M31 source,
   PDF, ZIP, companion and all frozen E008--E011 results byte for byte. Add close
   citations, exact scope comparison, a worked example and an explicit bounded
   use (edit-budget sensitivity audit). Keep all negative/censored results.
5. Compile and visually inspect every revised PDF page; check fonts, text,
   source ZIP and original-artifact preservation. State which scientific gaps
   remain. Update findings/canonical state and a Vietnamese progress note.

## Analytical-example check declared before code/run

One rule x -> y, target (0,0), all other rows editable, unit Hamming cost.
Let R be the minimum cost of satisfying x -> y in the entire edited table,
also protecting the target (a restricted comparison with ordinary repair).
Let rho be the minimum cost to flip the target's initial plurality decision.

- Family A, h=1,2,3: target plus 2h context (0,0) rows and one (0,1) row;
  x/y domains both {0,1}. Prediction from the derivation: R=1, rho=h.
  Extending h arbitrarily should make rho/R arbitrarily large.
- Family B, k=1,2,3: target plus (i,0),(i,1) for every i=1..k;
  x domain {0,..,k}, y domain {0,1}. Prediction: R=k, rho=1.
  Extending k arbitrarily should make R/rho arbitrarily large.
- A four-row coupled example: t=(0,0,0,0), context (0,0,1,1),
  (0,1,0,1),(1,0,0,0), rules {a,b}->y and {a,c}->y, binary domains.
  Predict initial rejection, fixed-key radius 2, full radius 1. Verify a
  changed a in the final context row makes both groups accept; this is an
  illustration, not a new source-data result or population estimate.

For each instance enumerate every permitted destination with target unchanged;
retain true minimum costs and concrete witnesses. Require predicted costs,
flipped decisions/valid repairs, no changed target, and exact counted costs.
Write all case records and enumeration denominators to an exclusive output.
On a mismatch, retain it, investigate and correct the derivation; do not replace
cases. Code must not call the paper's formula or existing canonical solver.

The universal family arguments must stand separately from the finite check.
No new claim of accuracy improvement, independence, worldwide originality or
general speed superiority follows. A novelty collision triggers claim revision,
not relabeling prior art. Missing original source CSV cache at resumption is
recorded; no fresh source reconstruction is claimed or required for this work.
