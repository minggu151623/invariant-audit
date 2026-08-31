# E003 external-transfer validation

This directory contains the protocol-only E003-v1 design. The protocol uses
three exact, time-separated GH Archive hourly JSON fixtures as a staged future
source; no fixture has been acquired, hashed, or placed in this repository.

- [E003-v1 protocol](protocol.md) specifies the source contract, deterministic
  case construction, calibration/confirmatory isolation, B0/M1 methods,
  independent oracle, metrics, bootstrap, artifact schemas, invalid-run
  behavior, and the one-run stopping gate.
- There is no E003 implementation, result report, prediction, metric,
  bootstrap, raw source, or acquired-source manifest in this directory or the
  repository.

The next gate requires separate authority for read-only acquisition, an
independent implementation/review, and one confirmatory execution. A valid
`mixed/not supported` outcome is terminal for E003-v1; the protocol does not
authorize retries or post-hoc expansion.
