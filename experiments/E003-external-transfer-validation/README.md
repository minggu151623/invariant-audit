# E003 external-transfer validation

This directory contains the locked E003-v1 design and its completed, read-only
source-acquisition record. The three exact, time-separated GH Archive hourly
JSON fixtures are frozen outside Git; no raw source is placed in this
repository.

- [E003-v1 protocol](protocol.md) specifies the source contract, deterministic
  case construction, calibration/confirmatory isolation, B0/M1 methods,
  independent oracle, metrics, bootstrap, artifact schemas, invalid-run
  behavior, and the one-run stopping gate.
- The canonical acquired-source manifest and HTTP metadata are outside Git at
  `/private/tmp/invariant-audit-e003-v1/source-manifest.json` and
  `/private/tmp/invariant-audit-e003-v1/acquisition-metadata.json`.
- E003 implementation, result report, prediction, metric, and bootstrap
  artifacts remain absent. Confirmatory isolation is preserved: acquisition
  validation covered only gzip/UTF-8/JSONL format, byte hashes, byte counts,
  and line counts; no event selection or scoring was performed.

The acquisition gate is complete. The next gate requires separate authority
for independent implementation/review and one confirmatory execution. A valid
`mixed/not supported` outcome is terminal for E003-v1; the protocol does not
authorize retries or post-hoc expansion.
