# M14 — Evidence correction and source-diagnosis design

Date: 2026-09-17. Status: documentary corrections and E004 protocol design.
User authority: continued research in the current conversation. The suggestion
that a different model caused past errors is unverified; errors are attributed
to artifact mismatches, not to a particular model or provider.

## Corrections

The original paper at commit 265bd55 contained incorrect E002 Brier/ECE values
and four intervals; false-alarm terminology inconsistent with positive=valid;
isotonic calibration instead of Laplace-smoothed lookup; percentage-point
ambiguity; overbroad interpretation of the two-split preflight; and unsupported
delivery-mechanism/external-performance conclusions. paper/main.md and its
outline are corrected against the immutable protocols/results. The historical
LinkedIn draft is marked withdrawn. E001/E002 artifacts and E003-v1 are unchanged.

Evidence remains two valid finite synthetic performance results and E003-v1's
invalid source-gate attempt. Lower Brier but higher ECE is not general calibration
improvement. Duplicate IDs do not establish their cause. Independent E003
post-remediation re-review acceptance is not documented.

## Follow-up design

[E004-v1](../experiments/E004-source-duplicate-diagnosis/protocol.md) asks whether
duplicates are identical records or conflicting objects. It is exploratory,
informed by M13's recorded counts; lock it before implementation and source
analysis. Dictionary/sort differential verification is by one agent, not an
independent reviewer.

The old temporary cache/manifest is missing. Recovery must match historical
compressed hashes and the canonical manifest digest; new acquisition timestamps
must not be backdated. Raw data stay outside Git. No new source count or valid
external-performance result is established by M14. The next gate is source
recovery, implementation/test commit, one E004 audit, and outer-loop synthesis.
