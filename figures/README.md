# Figures

Figure specifications and artifacts; source Markdown and result/data commits
are the source of truth.

The M09 progress presentation at
`to_human/progress-M09.html` is a self-contained documentary report using
embedded CSS and inline SVG. It contains only verified E001/E002 numbers and
does not constitute an E003 figure or result. No E003 figure artifact exists.

## E010 exact-pair latencies

[E010/paired-latencies.png](E010/paired-latencies.png) and the SVG counterpart
plot all 65/72 cases exact in both methods and repetitions. Seven censored
cases remain in the underlying results. Generated post-run by
`experiments/E010-directional-scaling/plot_results.py` from the frozen summary;
the plot embeds its source hash. Axes are log milliseconds, with regimes
separated because the accepted formula and rejecting-target MILP differ.
