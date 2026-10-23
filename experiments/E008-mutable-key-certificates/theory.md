# Target-relative action reduction: theorem draft and limitations

Date: 2026-10-23. Same-agent mathematical derivation. E008 verifies a finite
domain; the argument below is separate from that enumeration. The scientific
originality of the reduction remains to be established against prior work.

## Setup

There are q>=1 categorical key columns and one RHS y, with y excluded from all
determinants. The protected target row has value 0 in each column after a
columnwise relabeling. Key domains contain 0 and at least one nonzero value;
the RHS domain is a fixed finite set {0,...,d-1}, d>=2. Every other row is
editable with unit cell-Hamming cost. No missing-value semantics, domain
dependencies, insertion/deletion or constraints on simultaneous edits apply.

For context row r define M(r)={j:r_j=0}. Rule g with nonempty determinant X_g
contains r iff X_g is a subset of M(r). The target is accepted iff, in every
such group, its RHS value 0 strictly outnumbers each individual competitor v.
This is unique plurality, not necessarily an absolute majority.

Define the row contribution A_gv(r) as 1 if r is in group g with y=0, -1 if it
is in g with y=v, and 0 otherwise. The final margin is 1+sum_r A_gv(r), since
the protected target contributes 1. Acceptance is equivalent to all margins>=1.

## Lemma 1: finite quotient of key domains

For a fixed original row r, any destination row u can be replaced by a row u'
having the same key match mask and RHS value, with cost no greater. If a key
remains nonmatching, retain its original nonzero value when possible; if it
changes from matching to nonmatching, choose one fixed allowed nonzero value.
All group memberships are preserved. Thus the minimum cost of a key-mask change
is exactly |M(r) symmetric-difference M(u)|. The identities of other nonmatching
key values do not affect the optimum under this model.

This reduction does not merge nonzero RHS values: they remain distinct rivals.
It also does not apply if rules compare context rows with each other independently
of target membership, or if nonmatching key values have additional semantics.

## Lemma 2: dominance of canonical accepting actions

For every original row r and arbitrary edited row u, there exists a canonical
row c of no greater cost such that A_gv(c)>=A_gv(u) for every rule and rival.
Let M0=M(r) and M*=M(u). Three constructions cover all cases:

1. If r_y=0, take c_y=0 and M(c)=M0 union M*. Restoring original matching bits
   removes edits; keeping y=0 removes any RHS edit. Its group memberships include
   every group containing u. It has positive rather than zero/negative
   contributions there and never adds a negative contribution elsewhere.
2. If r_y!=0 and u_y=r_y, take c_y=r_y and M(c)=M0 intersection M*. Restoring
   original nonmatching bits removes edits. Its memberships are a subset of u's;
   removing a negative rival contribution weakly increases the margin, and no
   positive contribution is lost because its RHS is nonzero.
3. If r_y!=0 and u_y!=r_y, take c_y=0 and M(c)=M0 union M*. It uses one RHS edit,
   just as u does, and no more key edits. If u_y=0, its positive memberships
   are expanded. Otherwise its zero/negative contributions become zero/positive.

Concrete raw values are reconstructed as in Lemma 1, so abstract action costs
are attainable actual cell costs. This is a componentwise dominance statement,
not a statement about independent rule probabilities or reference correctness.

## Corollary: exact accepting counterfactual over reduced actions

Apply Lemma 2 independently to every context row in any accepting counterfactual.
All margins weakly increase while total cost weakly decreases. The resulting
table still accepts and uses only canonical actions. Conversely, every canonical
action is an allowed raw edit. Therefore their minimum accepting costs agree.

For an original match mask of size p, an original-0 row has 2^(q-p) canonical
actions. An original-nonzero row has 2^p+2^(q-p) actions, since the unchanged-RHS
submasks and changed-to-0 supermasks have distinct RHS labels. This is at most
2^q+1. The bound is independent of key-domain cardinality and of d; the decision
margin dimension still depends on d. It does not make the entire optimization
small or independent of the number of rules.

## Exact dynamic programs and their cost

For a rejected target, process context rows and retain, for each reachable
margin vector, the least action cost and a witness. Start at the all-ones vector
and finish at any vector with all coordinates>=1. Lemma 2 makes this restricted
program exact. With L=m(d-1) margins, there are at most (2n-1)^L possible margin
vectors for n total rows. A direct value-only program has an upper bound
O(n (2n-1)^L (2^q+1) L) on scalar operations, excluding witness-storage costs.
This is polynomial in n for fixed q,m,d but can be impractical as m or d grows.
The prototype stores concrete paths and is not an optimized implementation.

For an accepted target, rejection is a disjunction: some rule/rival margin must
be <=0. For each selected pair, reduce each row's destinations to the cheapest
action giving contribution -1,0 or +1. A scalar-margin program computes the
minimum cost for that pair; taking the minimum across pairs is exact. No
cross-rule independence assumption is used. E008 enumerates quotient actions
when constructing the three per-row choices.

An analytic implementation can obtain the same three costs directly. Let e be
the number of currently nonmatching keys in X_g, and let l=0 when e>0, else 1.
Then costs for contribution +1 and -1 are e+1[r_y!=0] and e+1[r_y!=v]. Cost for
0 is min(l, e+min_{w not in {0,v}} 1[r_y!=w]), with an empty minimum=INF. This
uses nonempty determinants and an available nonmatching key value. This closed
form is a derived optimization proposal; the frozen E008 implementation uses
enumeration, and no speed claim about a new implementation is made here.

## Checked evidence and what remains open

E008 matches raw unrestricted edit search on 30642 comparisons over 5107 ordered
tables, spanning six FD families and binary/ternary key/RHS domains. All 30618
finite witnesses verify. Its 61854 row-pair/family dominance checks pass. These
are finite checks supporting implementation, distinct from the general proof.

Allowing keys changes the threat model: 210 cases have a strict finite-radius
reduction, and 7290 change from protected-key INF to a finite radius. Those are
counts in the constructed domain, not prevalence estimates. They do not refute
protected-key certificates under the assumptions those certificates stated.

Generic counterfactual interventions, voting certification, repair optimization
and SAT explanations predate this work. The candidate contribution would have
to be a substantively distinct structural reduction or useful specialized method.
Before claiming it: compare against the strongest generic formulation, test
scaling beyond the finite correctness domain and examine meaningful source
tables under a separately locked design. Do not require external peer review
to do that local research; do not infer novelty from the absence of an exact
search phrase or from all tests passing.
