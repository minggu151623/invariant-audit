# M22 — portable frozen-evidence verification

Date: 2026-10-23. Status: `verified_portable_evidence_audit`.
This is artifact and arithmetic self-review, not independent acceptance.

Prepared a 35-member, 8,690,119-byte owner-review evidence ZIP, separate from
the minimal arXiv source ZIP. It contains the named M21 manuscript, frozen
synthetic inputs, E005/E006 outputs, relevant protocols/reports and a portable
standard-library verifier. No raw Raha source tables, private event payloads,
unrelated user CSVs, Git directory or cache contents are included.

Bundle SHA-256:
`5ae2c2f6f5a80c7a7f047daa7d58c176003f85ffc3579afd1d9e7f82bc17c7cb`.

Verified after extracting to a fresh temporary directory, with no `.git`, from
a different working directory. The default offline invocation checks 34 member
hashes, reconstructs all four E005 audit artifacts byte-identically (including
195 point comparisons), and verifies E006's 720 point comparisons, calibration
serialization, coordinate coverage and 84 interval endpoints from frozen rows.
Its output explicitly says the external source bytes were not checked.

A second extracted invocation with an explicit relocated `--source-root`
additionally verifies all nine original external-file pins. The historical
absolute source path is not required by the portable command. A controlled
one-byte member change is rejected by the hash inventory. Optimized Python
(`-O`) is rejected because the historical delivery audit uses assertions.
See [verification record](M22-portable-verification.json).

The original experiment implementation and result files are unchanged. The
post-run E006 delivery checker alone gains optional source-root/skip-source
arguments, preserving its default full-source verification behavior. The
portable driver reuses the existing audit implementations; it is not a new
independent numerical implementation or a full E001/E002/E006 execution. The
bundle manifest detects drift, not fraudulent provenance or incorrect science.

Artifacts: [instructions](../reproducibility/README.md),
[verifier](../reproducibility/verify_evidence.py),
[manifest](../reproducibility/bundle-manifest.json),
[evidence ZIP](../paper/evidence-review-bundle.zip).

M20 remains the latest scientific result and M21 the current rendered paper.
The research goal stays active. Next needs are substantive owner review,
scientific assessment of the case's archival interest, category/license and
eventual account/submission steps. No push, upload or account creation occurred.
