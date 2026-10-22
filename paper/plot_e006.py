"""Plot only the locked E006 primary contrasts from immutable delivered tables."""
import csv
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
METRICS = ROOT / 'data/E006-v1-metrics.csv'
INTERVALS = ROOT / 'data/E006-v1-intervals.csv'
assert sha256(METRICS.read_bytes()).hexdigest() == 'd0cefb17e137310417654e076e2fe4e41d93f367a71a4377911d86b0e3305bcd'
assert sha256(INTERVALS.read_bytes()).hexdigest() == '1e219f173e3ffaf52a0aa036f8b9cdfe5af9cbc6b16594a662f3863886ffc07b'
with METRICS.open() as stream:
    metrics = {(r['dataset'], r['method']): r for r in csv.DictReader(stream)
               if r['split'] == 'evaluation' and r['scope'] == 'all_cells'}
with INTERVALS.open() as stream:
    intervals = {(r['dataset'], r['pair'], r['metric']): r for r in csv.DictReader(stream)}
plt.rcParams.update({'font.size': 12, 'axes.spines.top': False, 'axes.spines.right': False, 'pdf.fonttype': 42})
fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
for axis, pair, metric, before, after, color, title in (
        (axes[0], 'Rmode-lookup-minus-binary', 'brier', 'Rmode', 'Rmode-binary', '#3c6682', 'a. Lookup minus binary Brier'),
        (axes[1], 'Rmode-Rall', 'fnr', 'Rmode', 'Rall', '#bc762d', 'b. Rmode minus Rall false rejection')):
    for y, dataset in enumerate(('beers', 'flights', 'rayyan')):
        point = float(Decimal(metrics[dataset, before][metric])-Decimal(metrics[dataset, after][metric]))
        interval = intervals[dataset, pair, metric]
        assert interval['usable_replicates'] == '10000'
        lower, upper = float(interval['lower']), float(interval['upper'])
        axis.errorbar(point, y, xerr=[[point-lower], [upper-point]], fmt='o', capsize=4, color=color, markersize=6)
    axis.axvline(0, color='black', linestyle='--', linewidth=.8)
    axis.set(yticks=[0, 1, 2], yticklabels=['Beers', 'Flights', 'Rayyan'], ylim=(2.5, -.5), xlabel='Paired difference')
    axis.set_title(title, loc='left', fontsize=11)
    axis.grid(axis='x', color='#dedede', linewidth=.6)
    axis.set_axisbelow(True)
axes[0].set_xlim(-.205, .012)
axes[1].set_xlim(-.74, .02)
fig.tight_layout(w_pad=2)
out = ROOT / 'paper/arxiv/images'
metadata = {'Title': 'E006 fixed external-reference contrasts', 'Author': '',
            'CreationDate': datetime(2026, 10, 22, tzinfo=timezone.utc),
            'ModDate': datetime(2026, 10, 22, tzinfo=timezone.utc)}
fig.savefig(out / 'external-reference-contrasts.pdf', bbox_inches='tight', metadata=metadata)
fig.savefig(out / 'external-reference-contrasts.png', bbox_inches='tight', dpi=180)
plt.close(fig)
