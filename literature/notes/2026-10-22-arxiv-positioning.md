# Focused source verification for the arXiv case study

Checked 2026-10-22. This is a focused set, not a systematic survey. Statements
about this repository are E005 observations or author interpretations, not
findings from the cited papers.

## Schelter et al. (2018)

Title: Automating Large-Scale Data Quality Verification.
Authors: Sebastian Schelter, Dustin Lange, Philipp Schmidt, Meltem Celikel,
Felix Biessmann, Andreas Grafberger. PVLDB 11(12):1781-1794.
DOI: 10.14778/3229863.3229867.
Primary source: https://www.vldb.org/pvldb/vol11/p1781-schelter.pdf
Verified PDF title, authors, citation block and abstract. The system combines
common quality constraints and user-defined validation code, with scalable
aggregation on Spark. Relevance: relational checking is established practice;
our B0 is a deliberately weak baseline, not a representative state of the art.
No experiment here compares with this system.

## Breck et al. (2019)

Title: Data Validation for Machine Learning. Authors: Eric Breck, Marty
Zinkevich, Neoklis Polyzotis, Steven Whang, Sudip Roy. Proceedings of SysML.
Primary source: https://research.google/pubs/data-validation-for-machine-learning/
Verified author list, year and abstract. The work describes detecting data
anomalies in ML pipelines and production use. Relevance: data validation is an
established research area; it does not supply performance evidence for our method.

## Barr et al. (2015)

Title: The Oracle Problem in Software Testing: A Survey. Authors: Earl T. Barr,
Mark Harman, Phil McMinn, Muzammil Shahbaz, Shin Yoo. IEEE TSE 41(5):507-525.
DOI: 10.1109/TSE.2014.2372785.
Primary/institutional sources: https://discovery.ucl.ac.uk/id/eprint/1471263/
and author manuscript https://philmcminn.com/publications/barr2015.pdf
Verified metadata and abstract/intro. The oracle problem concerns deciding if
observed behavior is correct, with specification/model/contract and other
approaches. Relevance: separate code implementations do not by themselves
establish an external truth specification. The latter sentence is our inference.

## Murphy (1973)

Title: A New Vector Partition of the Probability Score. Author: Allan H. Murphy.
Journal of Applied Meteorology 12(4):595-600.
DOI: 10.1175/1520-0450(1973)012<0595:ANVPOT>2.0.CO;2.
Primary source: https://journals.ametsoc.org/view/journals/apme/12/4/1520-0450_1973_012_0595_anvpot_2_0_co_2.xml
The publisher search index verifies metadata and the three components:
uncertainty, reliability and resolution. Direct full-page fetch returned 403;
full-text verification was unavailable. The manuscript supplies its own binary
finite-group derivation, not an asserted verbatim equation from the vector paper.
No claim to originality of that decomposition.

## Guo et al. (2017)

Title: On Calibration of Modern Neural Networks. Authors: Chuan Guo, Geoff
Pleiss, Yu Sun, Kilian Q. Weinberger. PMLR 70:1321-1330.
Primary source: https://proceedings.mlr.press/v70/guo17a.html
Verified metadata, BibTeX and abstract. Calibration concerns correspondence of
probabilities and correctness frequency; this work studies neural networks and
postprocessing. Relevance: terminology only, not evidence about our rule systems.

## Nixon et al. (2020 version, first submitted 2019)

Title: Measuring Calibration in Deep Learning. Authors: Jeremy Nixon, Mike
Dusenberry, Ghassen Jerfel, Timothy Nguyen, Jeremiah Liu, Linchuan Zhang,
Dustin Tran. arXiv:1904.01685v2.
Primary sources: https://arxiv.org/abs/1904.01685v2 and
https://arxiv.org/html/1904.01685v2
Verified version-specific author list and abstract/measurement discussion.
Metric design choices can alter calibration conclusions. Our positive-class ECE
is explicitly distinguished from maximum-confidence ECE; the paper does not
verify E005 or justify adding calibration diagnostics after seeing results as
confirmatory analysis.

## GH Archive

Official source: https://www.gharchive.org/, checked 2026-10-22.
The project archives the public GitHub timeline. Specific record counts and
exact-repeat observations in the manuscript come from local E003/E004 pinned
artifacts, not the website. Source provenance is not ground-truth validation.

## Novelty boundary

The proposed paper does not introduce invariants, oracle separation, the Brier
identity or calibration metrics. Its candidate contribution is an auditable
negative-finding case study joining these concerns in two explicit designs.
Whether that narrow contribution meets arXiv archival-interest expectations
remains a substantive review question. No comprehensive novelty search was done.
