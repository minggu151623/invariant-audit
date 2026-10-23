"""Post-run figure of exact paired latencies; no experiment is reexecuted."""
import csv
from hashlib import sha256
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

root = Path(__file__).resolve().parents[2]
source = root / 'data/E010-v1-summary.csv'
rows = list(csv.DictReader(source.open()))
fig, axes = plt.subplots(1, 3, figsize=(11, 3.7))
panels = [('accepted_dense', 'Accepted: dense groups', 24),
          ('accepted_singleton', 'Accepted: singleton groups', 24),
          ('rejected_coupled', 'Rejected: coupled groups', 24)]
for ax, (regime, title, total) in zip(axes, panels):
    paired = [r for r in rows if r['regime'] == regime and r['paired_exact'] == 'True']
    for q, marker, color in [(2, 'o', '#285c88'), (4, 's', '#b16b24'), (6, '^', '#42774b')]:
        selected = [r for r in paired if int(r['q']) == q]
        ax.scatter([1000*float(r['generic_median_total_seconds']) for r in selected],
                   [1000*float(r['specialized_median_total_seconds']) for r in selected],
                   label=f'{q} keys', marker=marker, color=color, s=28, alpha=.85)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_title(f'{title}\n{len(paired)}/{total} cases exact twice in both methods', fontsize=10)
    ax.set_xlabel('Generic median total time (ms)', fontsize=9)
    if ax is axes[0]:
        ax.set_ylabel('Specialized median total time (ms)', fontsize=9)
    ax.tick_params(labelsize=8)
    ax.grid(alpha=.15)
    if regime == 'rejected_coupled':
        low = min(ax.get_xlim()[0], ax.get_ylim()[0]); high = max(ax.get_xlim()[1], ax.get_ylim()[1])
        line = np.geomspace(low, high, 50)
        ax.plot(line, line, '--', color='#777777', linewidth=.8, label='Equal time')
    ax.legend(fontsize=7, loc='best')
fig.text(.5, .015, 'E010: constructed tables, n=16/128; two repetitions per case. Seven generic timeout cases excluded from paired plots; retained in data.',
         ha='center', fontsize=8)
fig.tight_layout(rect=(0, .06, 1, 1))
folder = root / 'figures/E010'
folder.mkdir(exist_ok=True)
metadata = {'Description': f'Post-run exact-pair latency figure. Source SHA-256: {sha256(source.read_bytes()).hexdigest()}'}
fig.savefig(folder / 'paired-latencies.png', dpi=180, metadata=metadata)
fig.savefig(folder / 'paired-latencies.svg', metadata=metadata)
plt.close(fig)
print(folder)
