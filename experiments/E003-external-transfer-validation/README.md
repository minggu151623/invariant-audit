# E003 external-transfer validation

Current-status correction (2026-09-17): the acquisition/M12 descriptions below
are historical. M13 records run e003-20260903-001 as invalid at the duplicate-ID
source gate, with an invalid report and no performance metrics. The temporary
source cache/manifest were absent at resumption. E004 tracks recovery and source
diagnosis separately; E003-v1 remains unchanged and invalid. Accepted independent
post-remediation implementation review is not recorded.

## Historical M11/M12 record

This directory contains the locked E003-v1 design and its completed, audited
read-only source-acquisition record. The three exact, time-separated GH Archive
hourly JSON fixtures are frozen outside Git; no raw source is placed in this
repository.

- [E003-v1 protocol](protocol.md) specifies the source contract, deterministic
  case construction, calibration/confirmatory isolation, B0/M1 methods,
  independent oracle, metrics, bootstrap, artifact schemas, invalid-run
  behavior, and the one-run stopping gate.
- The canonical source manifest and HTTP metadata are outside Git at
  `/private/tmp/invariant-audit-e003-v1/source-manifest.json` and
  `/private/tmp/invariant-audit-e003-v1/acquisition-metadata.json`.
  The manifest SHA-256 is
  `683eef39cd26d2a7f6622689adc2cd9e357e78a770f77bf91e98513b859e4633`; the
  post-remediation metadata SHA-256 is
  `5937fbf7d8583ed3954b7d107146af331d29f2a14e224d883e892c74ce52388a`; and
  the canonical local-freeze-event SHA-256 is
  `17ac5e9eb4386ef2d6f4f34996f240e600b16d7521fdcc6b91dfd10630c27ed7`.
- The audited source inventory is exactly the three manifest-listed `.json.gz`
  files under `/private/tmp/invariant-audit-e003-v1/source/`; the three
  pre-remediation `.headers` sidecars were reversibly moved to
  `/private/tmp/invariant-audit-e003-v1-remediation-archive-20260901/`.
- The [M12 implementation-readiness record](../../milestones/M12-E003-implementation-readiness.md)
  indexes the standard-library implementation and its guarded
  development/calibration-only preflight. It proves 64 IssuesEvent + 64
  PullRequestEvent bases and 512 cases in each non-confirmatory split, with
  lookup hashes and repeated-preflight determinism recorded there. Independent
  review remains pending.
- E003 run, result report, prediction, metric, bootstrap, and production output
  artifacts remain absent. Confirmatory isolation is preserved: the 2021 gzip
  was not opened by implementation tests or preflight, and no event selection
  or scoring was performed on it.

The authoritative local-only freeze event occurred at
`2026-08-31T19:59:22Z` UTC, after local manifest and payload verification, with
starting Git HEAD `b68424e756fb86f05c866647b2471d36e24da716`; remediation used
no network. The prior `network_frozen_at_utc` value
`2026-08-31T19:06:24Z` predates the observed manifest mtime
`2026-08-31T19:07:45Z`, so that original chronology is retained only as a
historical caveat and is not treated as independently supported.

The acquisition gate is complete. The next gate requires separate authority
for independent implementation/review and one confirmatory execution. A valid
`mixed/not supported` outcome is terminal for E003-v1; the protocol does not
authorize retries or post-hoc expansion.
