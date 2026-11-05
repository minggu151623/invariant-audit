# E012 result

The complete locked finite grid passed: 111 coverable Set Cover multisets,
222 exact radius checks (fixed and editable keys), 147523 destination checks.
These comprise 2901 fixed-key and 144622 full-edit destinations; counts across
models overlap and are not unique destination tables or independent replications.
The two exact radii equal the independently enumerated minimum cover in every case.

Reverse extraction passed on every accepting destination: 601 fixed-key and
24889 full-edit destinations. Of the latter, 24288 contain key edits, 18170
contain support-row edits and 1041 contain a support RHS zero-to-one flip.
These categories overlap. Thus the check exercises the proposed converse beyond
only the forward witnesses. All 222 minimum witnesses and 111 forward cover
witnesses pass direct cost/decision checks. No mismatch or execution failure.

Protocol commit: `9f14171`; implementation commit: `65ad518`. The actual run used
Python 3.14.5 with `-I -S`, without third-party imports. Code/protocol SHA-256 and
every constructed case, cost-level denominator and minimum witness appear in
`results.json`. Execution time was not an outcome and is not a speed result.

`theory.md` gives a separate proof of the universal optimum-preserving reduction
and NP-completeness claim. The finite results check this small implementation
domain, not that proof, scientific significance or originality. The fixed-schema
DP observation is analytical and was not implemented/tested in E012.

The construction never gives a full-key advantage; that is a feature of its
lower bound, not an omitted unfavorable result. It establishes worst-case
accepting complexity in both models. No source dataset, solver benchmark or
cleaning accuracy measurement was repeated. The previous E011 results remain
negative for strict accepting-direction savings on its 30 exact pairs, with
two unresolved full-model timeouts.
