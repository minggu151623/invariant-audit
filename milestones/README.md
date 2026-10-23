# Milestones

Milestone records and verification evidence; Markdown records are the source of truth and YAML mirrors status.

## Current milestones

- [M17 — E003-v2 adapter integration](M17-E003-v2-adapter.md):
  current milestone; source filtering and selection adapter integrated and verified
  (39 total synthetic tests passing: 22 normalizer + 17 adapter). Remaining pipeline stages
  (evaluation/calibration/bootstrap versioning, transactionality guards, guarded 2019/2020 integration)
  and independent acceptance remain pending; no v2 run/result.

- [M16 — E003-v2 lock and source component](M16-E003-v2-protocol-and-normalizer.md):
  preceding milestone; separately locked exploratory protocol and source normalizer
  with 22 passing synthetic tests. Superseded by M17.

- [M15 — E004 recovered-source diagnosis](M15-E004-source-diagnosis.md):
  preceding milestone; one valid exploratory diagnostic found 537 byte-identical
  extra occurrences, no conflicting groups, and no cross-shard repeated IDs.
  No external performance result. E003-v2 is proposed, not locked or run.

- [M14 — Evidence correction and E004 design](M14-evidence-correction-and-source-diagnosis.md):
  preceding correction/design milestone; completed source audit is in M15.

- [M13 — E003 run 001 invalid evidence record](M13-E003-run-001-invalid.md):
  historical invalid-run milestone; records the executed run e003-20260903-001,
  its invalid status (exit code 2), runner failure on duplicate event IDs
  (537 duplicate lines in GH Archive 2021), concise invalid report, and
  empirical diagnosis. No metrics, data, or E003 results exist.
- [M12 — E003 implementation-readiness](M12-E003-implementation-readiness.md):
  preceding milestone; records the standard-library implementation, guarded
  development/calibration-only integration, exact selected/repository counts,
  calibration lookup hashes, deterministic preflight, and 29-test suite.
- [M11 — E003 source acquisition freeze](M11-E003-source-acquisition.md):
  preceding milestone; records the audited three-file GH Archive cache, exact
  payload/manifest hashes, local-only freeze event, reversible sidecar archive,
  chronology caveat, and preserved confirmatory isolation. No E003
  implementation, run, result, data, code, or public claim exists.
- [M10 — E003 external-transfer protocol design](M10-E003-protocol-design.md):
  historical protocol design after the M09 **BROADEN** decision. The locked
  protocol remains unchanged.
- [M09 — outer-loop reflection after E002](M09-outer-loop-after-E002.md):
  synthesizes the verified finite-synthetic E001/E002 records and identifies
  external transfer as the largest unresolved gap.
- [M08 — E002 corrected run 002 valid result](M08-E002-run-002-valid.md): records exactly one valid locked local confirmatory run for
  `e002-20260825-002`, its four runner-produced artifacts, and H2 `supported`
  within the finite synthetic protocol. The authorization is consumed and
  `public_claim_eligibility` remains `false`.
- [M07 — E002 corrected-run technical-readiness gate](M07-E002-corrected-run-readiness.md): records technical readiness for candidate
  `e002-20260825-002` subject to the locked runtime preflight. M07 is the
  historical pre-run gate; M08 records the subsequent valid run.
- [M06 — E002 validator remediation and independent-review gate](M06-E002-validator-remediation.md): records complete validator remediation and
  independent acceptance; M07 records the subsequent technical-readiness
  audit, while the M05 execution remains invalid and
  `public_claim_eligibility` remains `false`.
- [M05 — E002 run 001 invalid evidence](M05-E002-run-001-invalid.md): records
  the authorized local run `e002-20260825-001` as invalid with exit code 2 and
  failure `result semantic field drift: D9_OR_NA`; no metrics, evidence, or
  data outputs exist; remediation is closed by M06, and
  `public_claim_eligibility` is `false`.
- [M00 — Research direction](M00-research-direction.md): verified documentary
  direction and provenance only.
- [M01 — Protocol design](M01-protocol-design.md): the documentary protocol
  lock is complete and published as an ancestor of the E001 result; M01 is not
  experimental evidence.
- [M02 — E001 results](M02-E001-results.md): verified only within the finite
  synthetic E001 design; `public_claim_eligibility` is `false`.
- [M04 — E002 implementation review and authorization](M04-E002-implementation-review.md):
  the executable implementation was independently reviewed and one locked
  local run was authorized; M05 records that run as invalid and M06 records
  the completed remediation, while `public_claim_eligibility` remains
  `false`.
- [M03 — E002 protocol design](M03-E002-protocol-design.md) is the historical
  protocol-only record for the preceding stage. Its statement that no
  implementation or execution existed is retained as the M03-at-that-time
  state, not the current M06 state.

## 2026-10-22 continuation

- [M18: arXiv destination and E005 evidence audit](M18-arxiv-evidence-audit.md):
  verified within exploratory numerical/artifact self-review. Independent
  scientific acceptance and submission remain pending.

- [M19: rendered arXiv-directed draft](M19-arxiv-working-manuscript.md):
  verified PDF/source artifacts; scientific and owner review remain open.

- [M20: external-reference results](M20-external-reference-results.md): fixed
  three-dataset study and delivery verification; independent review remains absent.

- [M21: named external-reference manuscript](M21-external-reference-manuscript.md):
  current 12-page PDF and four-file source ZIP; artifact checks pass, substantive
  review and submission remain open.

- [M22: portable evidence verification](M22-portable-evidence-bundle.md):
  extracted offline/relocated-source checks pass; frozen-evidence self-review,
  not full experiment reexecution or independent acceptance.

- [M23: owner reading and submission preparation](M23-owner-reading-and-submission-preparation.md):
  Vietnamese walkthrough, concrete fields and current official-guidance check;
  owner-review request pending, goal not achieved.

- [M24: novelty reset](M24-novelty-reset-and-E007-design.md): owner requests
  an original contribution; primary-source collision check and protocol lock.
- [M25: E007 finite pilot](M25-E007-finite-certificate-pilot.md): exhaustive
  mathematical agreement; novelty remains unestablished, mutable-key work next.

- [M26: mutable-key certificate pilot](M26-E008-mutable-key-pilot.md): raw-edit
  agreement, action-dominance checks and a scoped theorem draft; novelty open.

- [M27: accepted-target characterization](M27-E009-singleton-characterization.md):
  exact singleton/import condition, complete finite verification and generic
  baseline equivalence; novelty and larger-scale usefulness remain open.

- [M28: bounded directional algorithm study](M28-E010-directional-scaling.md):
  exact specialized results on all 72 constructed cases, 14 generic timeout
  observations and one slower specialized case retained; real-data work next.

- [M29: reused-source stability](M29-E011-source-stability.md): complete accepted
  radii, bounded rejected subset with no observed strict gain, two timeouts and
  a narrowed novelty claim after theorem-level prior-work comparison.

- [M30: structural preprint](M30-structural-preprint-draft.md): seven-page
  contribution-centered manuscript, standalone source ZIP and visual/font/
  numeric QA; new evidence companion and owner review remain open.

- [M31: portable structural companion](M31-portable-structural-companion.md):
  81-member packet, complete finite reconstruction, relocated-source checks,
  four negative controls and exact claim/field audit; owner decisions pending.
