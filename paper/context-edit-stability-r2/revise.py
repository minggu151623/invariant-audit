"""Build the dated R2 source without changing the M30/M31 review packet."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
old = (ROOT.parent / 'context-edit-stability/main.tex').read_text()
text = old.replace(r'\newtheorem{corollary}{Corollary}',
                   r'\newtheorem{corollary}{Corollary}'+'\n'+r'\newtheorem{proposition}{Proposition}')
text = text.replace('Working preprint draft -- October 23, 2026',
                    'Revised working preprint -- November 5, 2026')
intro = r'''
The intended use is an edit-budget sensitivity audit, not a repair prescription.
For a declared context-edit budget $B$, a radius greater than $B$ certifies that
the present decision survives every permitted edit within that budget; a radius
at most $B$ supplies an explicit counterexample to that certificate. This lets
an auditor distinguish trusting determinant cells from allowing them to be
wrong. It does not establish which cells are actually wrong, or validate the
choice of budget and unit costs. We position the result as a restricted
theory/algorithm note, rather than an accuracy-improving cleaning system.
'''
text = text.replace(r'\section{Model and edit semantics}', intro+'\n'+r'\section{Model and edit semantics}')
example = r'''
\paragraph{A coupled example.}
Consider the binary table below, with rules $(a,b)\to y$ and $(a,c)\to y$.
The first row is protected. Each target group initially has one zero and one
one, so both checks reject.
\begin{table}[H]
\centering\small
\begin{tabular}{lrrrr}
\toprule
Row & $a$ & $b$ & $c$ & $y$\\
\midrule
Target &0&0&0&0\\
$r_1$ &0&0&1&1\\
$r_2$ &0&1&0&1\\
$r_3$ &1&0&0&0\\
\bottomrule
\end{tabular}
\caption{Constructed illustration of a shared key edit, not a source-data result.}
\end{table}
With fixed keys, both $r_1.y$ and $r_2.y$ must change to zero: editing either
alone leaves the other check tied. Thus $\rho_{\rm fixed}=2$.
Changing only $r_3.a$ to zero joins both groups simultaneously; each then has
two zeros and one one, so $\rho_{\rm full}=1$. This example explains why
rowwise group membership matters for accepting a rejected target. It does not
show that such savings are prevalent in real tables.
'''
text = text.replace(r'\section{Making an accepted target reject}', example+'\n'+r'\section{Making an accepted target reject}')
separation = r'''
\section{Decision distance versus whole-table repair}
For comparison within our identified-row model, let $R(T)$ be the minimum
context-cell cost making the entire edited table satisfy every FD as an
agreement constraint, still protecting $t$. This comparison protects the same
target in both objectives; it is not a redefinition of prior repair semantics.
\begin{proposition}[No constant-factor substitution]\label{prop:separation}
Even with one rule $x\to y$ and binary $y$, the ratios
$\rho_{\rm full}/R(T)$ and $R(T)/\rho_{\rm full}$ can each be arbitrarily large
on instances where both costs are positive and finite.
\end{proposition}
\begin{proof}
For any $h\geq1$, use target $(0,0)$, $2h$ additional $(0,0)$ rows and one
$(0,1)$ row, with binary domains. Changing the lone one to zero repairs the
table; since it initially violates the FD, $R(T)=1$.
Theorem~\ref{thm:reject} gives $\rho_{\rm full}=h$ from counts $2h+1$ and one.
Thus the first ratio is $h$.

For any $k\geq1$, use target $(0,0)$ and pairs $(i,0),(i,1)$ for
$i=1,\ldots,k$, with key domain $\{0,\ldots,k\}$.
Each original conflicting pair requires an edit in one of its own cells;
otherwise that pair still violates the FD. The disjoint pairs require at
least $k$ edits, and changing each pair's one to zero attains $R(T)=k$.
The target's group is initially singleton. Changing the key of $(1,1)$ to
zero creates a tie with one edit, so $\rho_{\rm full}=1$.
The second ratio is $k$.
\end{proof}
These elementary families clarify the objective, rather than serve as another
priority claim. A whole-table repair optimum cannot simply be reported as this
decision radius. They do not exclude reductions between computational problems
or the use of general repair/constraint machinery with a different encoding.
For $h,k\in\{1,2,3\}$, unrestricted raw-destination enumeration checks both
costs; together with the coupled example in both edit models, eight checks
cover 285,032 destinations. These small illustrative checks are separate from
the E008--E011 studies and are not additional source validation.
'''
text = text.replace(r'\section{Making a rejected target accept}', separation+'\n'+r'\section{Making a rejected target accept}')
start = text.index('View-conditioned causality already provides')
end = text.index('The same-RHS restriction permits', start)
related = r'''Cell-level repair and intervention objectives substantially predate this work.
Debosschere and Geerts~\cite{cellcauses}, Section 2, define cell modifications,
their cardinality distance and repairs satisfying the FD set. Their
Propositions 1--3 concern responsibility complexity and repair/cause
correspondence. Our edited table may violate FDs: the goal is a protected
target's plurality-decision flip, not consistency restoration.
Proposition~\ref{prop:separation} makes the numerical distinction explicit.
Bertossi~\cite{bertossi}, Sections 3.1 and 4, gives abstract repair semantics
and an attribute-cause instantiation using NULL replacements. We instead allow
arbitrary domain values, do not assign causal responsibility to a particular
cell, and need not preserve other outputs.

Meliou et al.~\cite{vcc}, Sections 4.1--4.4 and Theorems 14, 15 and 17,
give predicate partitions, cause/responsibility equivalence and SAT-based
reasoning about changed inputs. General vote operations already optimize
constructive/destructive goals with score constraints~\cite{xia},
Definitions 2--3 and Section 4. Those generic frameworks motivate an encoding;
they are not claimed as new here. Our accepting proof additionally constructs
a no-more-expensive row destination dominating every relevant margin, and our
rejection proof constructs a witness attaining the margin/import lower bound.
These are the specialized statements being presented; their absence from the
inspected theorem statements is not a systematic originality certificate.

FD repairs with immutable trusted cells are established~\cite{repairs}.
Certified k-NN over FD repairs~\cite{knn} uses different possible worlds and
edit semantics. Recent work distinguishes AFD strength from detection
utility~\cite{wan}; our radius likewise must not be interpreted as accuracy.
The practical evidence here concerns sensitivity and bounded computation,
not a demonstrated improvement to a deployed auditing workflow.

'''
text = text[:start]+related+text[end:]
text = text.replace('Source reuse,\nsmall synthetic sizes, sparse rejected sampling, two solver timeouts and the',
                    'Source reuse,\nsmall synthetic sizes, sparse rejected sampling, two solver timeouts and the')
text = text.replace('The local companion repository preserves protocols, code, source manifests,',
'''The frozen M31 companion preserves the original E008--E011 protocols, code,
source manifests,''')
text = text.replace('all outcomes, witnesses and separate delivery checks. No public code URL or',
'''all outcomes, witnesses and separate delivery checks. Its manuscript snapshot
predates this revision. A separate R2 supplement provides the raw enumerator
and all records for the new analytical examples, the comparison notes and
revision verification. The original source CSV cache was unavailable at this
revision; no new raw-source reconstruction or solver/timing run is claimed.
No public code URL or''')
text = text.replace(r'\begin{thebibliography}{9}',r'\begin{thebibliography}{9}')
refs = r'''\bibitem{cellcauses} M. Debosschere and F. Geerts.
Cell-Based Causality for Data Repairs. TaPP, 2015.
\href{https://www.usenix.org/conference/tapp15/workshop-program/presentation/debosschere}{USENIX proceedings}.
\bibitem{bertossi} L. Bertossi. Specifying and Computing Causes for Query
Answers in Databases via Database Repairs and Repair Programs.
\href{https://arxiv.org/abs/1712.01001v7}{arXiv:1712.01001v7}, 2020.
'''
text = text.replace(r'\bibitem{vcc}',refs+r'\bibitem{vcc}')
(ROOT / 'tex/main.tex').write_text(text)
print('Wrote R2 source:', len(text), 'characters; M30 unchanged')
