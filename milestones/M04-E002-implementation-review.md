# M04 — E002 implementation review and authorization gate

Status: implementation independently reviewed; the next locked local E002
confirmatory run is authorized; no E002 run or result exists.

## Authority and provenance

On 2026-08-25, the user supplied the following current messages as
resumption and continued-research authority:

- `exact_text_1`: "tiếp tục lúc hết quota đi"
- `exact_text_2`: "bạn đọc lại tài liêụ đi là biết mà"

The context also includes the existing recorded long-running authority:
`cả hai, nghiên cứu lâu đi, bao lâu cũng được`.

Calibrated interpretation: these current messages explicitly direct
resumption from documented state and reaffirm continued local research. They
authorize the next locked local E002 confirmatory execution and result
recording, but do not select technical design, authorize push/publication or a
public claim, or establish any result.

The detailed E002 protocol, implementation, tests, review criteria, and
remediation choices remain worker/reviewer design and verification work. They
are not attributed to the user as technical selections. This documentary task
records the authorization gate only; it does not execute the run.

## Locked protocol and implementation chain

- Protocol: [E002-v1](../experiments/E002-heterogeneous-specification-stress/protocol.md)
- Protocol lock commit: `9e39c5defc89f2c2a896b53dda529f326e9dfcf8`
- Locked protocol blob: `f7d27a069ee3fd1600f89d9271e107c197033238`
- Protocol status: unchanged and byte-identical to the locked blob.

The executable implementation chain is:

1. `42cb62374c2b94ad6c567232acdac6d7365a9d8f` — initial implementation.
2. `6df4f3bc02f5f12feb243df21ec9eeaafd53d8fc` — result-validator hardening.
3. `0977641f129d172dd4d11136197a82cb17654aeb` — independent-review
   remediation.

The implementation is standard-library-only and is documented in the
[E002 code README](../experiments/E002-heterogeneous-specification-stress/code/README.md).

## Independent implementation review

The initial independent review status was **HOLD** with four findings:

| Severity | Finding | Remediation status |
| --- | --- | --- |
| High | Staging/publication cleanup caught only `Exception`, so `KeyboardInterrupt` or `SystemExit` could bypass cleanup and invalid-run handling. | Remediated with BaseException-class cleanup and preservation of the original interrupt after the invalid-run outcome is recorded. |
| Medium | Runtime sanity did not enforce the locked local-index-to-split allocation; an H0-C00/H0-C04 split swap was accepted. | Remediated with an independent exact allocation map and mutation regression test. |
| Medium | The double-build gate compared population/oracle manifest hashes rather than the locked canonical payload bytes. | Remediated with direct canonical population/oracle byte comparison and a hash-only-equivalence regression test. |
| Low | The code README retained the stale 48-test count. | Remediated to the observed final count of 53 tests. |

Re-review returned **no findings**. The implementation is fit for the
independent-review gate, subject to the locked clean-tree preflight and all
protocol gates at execution time.

Observed development verification:

```text
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s experiments/E002-heterogeneous-specification-stress/code -p 'test_e002.py'
```

The development suite ran 53 tests and returned `OK`. This is implementation
and test evidence only; it is not confirmatory evidence and establishes no
metric, H2 outcome, external validity, novelty, safety, or generalization.

## Current state and next gate

The current E002 documentary state is:

- `implementation_reviewed: true`
- `run_authorized: true`
- `run: absent`
- `results: absent`
- `data: absent`
- `public_claim_eligibility: false`

The next gate is a clean-tree local run using run ID `e002-20260825-001` and
the exact command recorded in the code README:

```text
PYTHONDONTWRITEBYTECODE=1 python experiments/E002-heterogeneous-specification-stress/code/run_e002.py --run-id e002-20260825-001 --output-root .
```

No run is performed in this documentation task. Until that separately
executed and verified gate exists, E002 outputs, metrics, bootstrap data,
results, figures, ARA artifacts, and any H2 or external claim remain absent.
