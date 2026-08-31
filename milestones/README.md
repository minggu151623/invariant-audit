# Milestones

Milestone records and verification evidence; Markdown records are the source of truth and YAML mirrors status.

## Current milestones

- [M10 — E003 external-transfer protocol design](M10-E003-protocol-design.md):
  current protocol-only design after the M09 **BROADEN** decision. The source
  snapshot is staged but unacquired; no E003 implementation, run, result, data,
  code, or public claim exists.
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
