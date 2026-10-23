# Structural-preprint companion

This review companion binds the M30 manuscript to frozen E008--E011 evidence.
It is local review material, not an arXiv submission, license grant, independent
scientific assessment, or a claim of priority. No raw source CSVs are bundled.

Extract `paper/context-edit-stability-companion.zip` into an empty directory.
From any working directory run:

```sh
python3 -I /path/to/extracted/reproducibility/stability/verify_companion.py
```

Only the Python standard library is needed. Git, NumPy, SciPy, TeX and network
access are not used. `-O` is also supported: validation uses explicit failures
rather than assertions. The manifest detects changed bytes; it is not a digital
signature or evidence that a scientific assertion is true.

The default check regenerates the 72 synthetic benchmark inputs, recalculates
the 2118 small E009 raw-edit optima and E010/E011 preflight optima, checks stored
synthetic witnesses, complete source-output arithmetic, dirty-stage hashes,
selection coordinates, timing medians and all censoring. It does not solve an
MILP, rerun a timing benchmark or read machine-specific source caches. Reported
solver statuses/residuals are checked for consistency with the serialized
record; absent solver primal vectors cannot be independently reconstructed
from that record. Tiny raw-oracle checks provide separate optimality checks
where stated. E010 benchmark optima rely on the retained solver certificates.

Without source files, E011 raw grouping, reference labels and witness decision
flips are explicitly unchecked. To add them, supply the original nine files
under a relocated directory preserving their manifest-relative paths:

```sh
python3 -I /path/to/extracted/reproducibility/stability/verify_companion.py \
  --source-root /path/to/raha-source
```

The manifest is `data/E006-v1-source-manifest.json`; its `files` entries give
public revision URLs, sizes and hashes. The verifier never downloads or falls
back to the original machine cache. It pins all nine supplied files, reconstructs
all 18734 E011 dirty decisions and accepted radii, and checks raw coordinate
witnesses and aligned reference labels. It reuses the frozen E011 delivery
helper, so this is computational reproduction/self-review, not independent review.

For complete deterministic mathematical reproduction of E008 and E009:

```sh
python3 -I /path/to/extracted/reproducibility/stability/verify_companion.py \
  --recheck-finite
```

This rebuilds E008's four artifacts in memory and rechecks all 18779 accepted
E009 formula cases against raw enumeration. It may take several minutes.
It never invokes guarded study runners' main functions, writes study outputs,
or repeats E009--E011 solver/timing runs. Options can be combined.

The original runners are included for inspection with their historical Git,
runtime and no-overwrite guards intact. They are not advertised as directly
runnable from this Git-free companion. Exact source/runtime/protocol identities
and full procedure descriptions remain in the original protocols and records.

`claims.json` maps theorems and numerical statements to source arguments,
artifacts and the verification layer that covers them. Finite checks are not
proofs for all inputs. Performance is bounded by the declared cases and machine.
Source reuse, unsupported H11b, zero gain in 30 exact rejected pairs, both
unresolved source timeouts and the slower E010 specialized case are retained.
The manuscript does not claim robustness equals reference correctness.

The minimal arXiv source ZIP is a separate one-file document package. This
companion is a larger code/evidence artifact for review and possible later
ancillary release after owner decisions. No license or public hosting choice
has been made on the owner's behalf.
