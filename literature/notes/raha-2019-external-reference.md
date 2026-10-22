# Raha (2019): external-reference selection

Checked 2026-10-22. Authors: Mohammad Mahdavi, Ziawasch Abedjan, Raul Castro
Fernandez, Samuel Madden, Mourad Ouzzani, Michael Stonebraker and Nan Tang.
Title: Raha: A Configuration-Free Error Detection System. SIGMOD 2019:865-882.
DOI: 10.1145/3299869.3324956.
Primary author manuscript: https://raulcastrofernandez.com/papers/raha.pdf
Official source repository: https://github.com/BigDaMa/raha
Pinned repository HEAD: 7be1334b8c7bbdac3f47ef514fb3e1e8c5fc181c.

Source fact (section 6.1): Beers was scraped and manually cleaned; Rayyan was
cleaned by its owners. Flights was obtained with reference data from earlier
work. The paper provides dataset-specific checks in Appendix A/Table 8, and
warns that cells participating in a violated dependency are not necessarily
incorrect (Appendix C). This limits novelty of the same general observation.

Source-code fact: `raha/dataset.py` minimally normalizes strings using HTML
unescaping, collapsing runs of tab/newline/space and stripping those characters;
reference errors are differences between aligned dirty and clean tables.
Pinned code: https://raw.githubusercontent.com/BigDaMa/raha/7be1334b8c7bbdac3f47ef514fb3e1e8c5fc181c/raha/dataset.py

Design inference: use three fixed datasets to test simple rule-attribution and
probability variants against independently supplied reference corrections.
Do not call those references infallible truth, claim a new rule-based algorithm,
or describe this as a direct replication of Raha. No performance outcome has
been measured at the source-selection stage. Published example rows and old
Raha performance tables have been seen; this is predeclared external validation,
not a wholly blind discovery. The new methods and calibration rule must be
locked before inspecting the local paired values/outcomes.
