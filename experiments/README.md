# Experiments

Protocols, runs, results, and linked data; Markdown is narrative source and
CSV/JSONL is row-data source.

## Current boundary

- [E001 synthetic invariant calibration protocol](E001-synthetic-invariant-calibration/protocol.md)
  is the M01 documentary protocol, locked by commit
  `d8b26d21e9692ace19436d78461460940043f5c7` with subject
  `research(protocol): lock E001 synthetic invariant calibration`. The protocol
  commit is published as an ancestor of result commit
  `31071ddf65ad9a1f0e5b28eb0d501899253cd17b`.
- The authorized run `e001-20260825-001` is valid. Its published result is
  [run Markdown](E001-synthetic-invariant-calibration/results/run-e001-20260825-001.md)
  in result commit `31071ddf65ad9a1f0e5b28eb0d501899253cd17b`; linked row data
  is indexed in [data/README.md](../data/README.md).
- M02 verifies this result only within the finite synthetic E001 design. It is
  not production, external-validity, novelty, safety, or generalization
  evidence, and it does not authorize a future E002 run.
- [E002 heterogeneous specification stress protocol](E002-heterogeneous-specification-stress/protocol.md)
  is the protocol locked at M03. The historical M03 record was protocol-only;
  the executable implementation now exists in
  [the E002 code directory](E002-heterogeneous-specification-stress/code/README.md)
  and is recorded by the implementation chain
  `42cb62374c2b94ad6c567232acdac6d7365a9d8f` ->
  `6df4f3bc02f5f12feb243df21ec9eeaafd53d8fc` ->
  `0977641f129d172dd4d11136197a82cb17654aeb`.
- [M04 implementation review and authorization gate](../milestones/M04-E002-implementation-review.md)
  records the independent-review approval and authorization for the next
  locked local run. The 53-test development suite is `OK`; no E002 run,
  experimental data, result/output, figure, or ARA artifact exists.
- This index is not experimental evidence and establishes no E002 metric,
  H2 outcome, external validity, novelty, safety, generalization, or public
  claim.
