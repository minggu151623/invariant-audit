"""Render the manuscript figure from the frozen E005 summary."""
import csv
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/E005-v1-summary.csv"
EXPECTED = "a5d90edf854a9383bd475e956a00fc5c52f1321de11c01dd3f52c92117e48579"
assert sha256(SOURCE.read_bytes()).hexdigest() == EXPECTED
with SOURCE.open() as stream:
    rows = [r for r in csv.DictReader(stream)
            if r["split"] == "confirmatory" and r["method"] in ("B0", "M1")]
assert [(r["experiment"], r["method"]) for r in rows] == [
    ("E001", "B0"), ("E001", "M1"), ("E002", "B0"), ("E002", "M1")]
rel, res, unc, brier = (np.array([float(r[k]) for r in rows])
                         for k in ("reliability", "resolution", "uncertainty", "brier"))
plt.rcParams.update({"font.size": 12, "axes.spines.top": False,
                     "axes.spines.right": False, "pdf.fonttype": 42})
fig, (left, right) = plt.subplots(1, 2, figsize=(10, 3.7), gridspec_kw={"width_ratios": [1.35, 1]})
x = np.arange(4)
labels = [r["experiment"] + "\n" + r["method"] for r in rows]
left.bar(x, unc, width=.58, label="UNC", color="#3c6682")
left.bar(x, rel, bottom=unc, width=.58, label="REL", color="#d28232")
left.bar(x, -res, width=.58, label="minus RES", color="#b5b5b5", hatch="//")
left.scatter(x, brier, color="black", marker="D", s=32, label="Brier", zorder=4)
left.axhline(0, color="#555555", lw=.7)
left.set(xticks=x, xticklabels=labels, ylabel="Score contribution", ylim=(-.28, .31))
left.set_title("a. Full Brier decomposition", loc="left", fontsize=12)
left.legend(ncol=4, fontsize=9, loc="upper center", bbox_to_anchor=(.5, -.20), frameon=False)
right.bar(x, rel * 10**4, width=.58, color="#d28232")
right.set(xticks=x, xticklabels=labels, ylabel="REL (units of $10^{-4}$)", ylim=(0, 3.1))
right.set_title("b. Reliability loss increases", loc="left", fontsize=12)
for index, value in enumerate(rel * 10**4):
    right.text(index, value + .08, f"{value:.3f}", ha="center", fontsize=10)
fig.tight_layout(w_pad=2)
out = ROOT / "paper/arxiv/images"
out.mkdir(parents=True, exist_ok=True)
metadata = {"Title": "E005 finite evaluation Brier decomposition",
            "Author": "", "CreationDate": datetime(2026, 10, 22, tzinfo=timezone.utc),
            "ModDate": datetime(2026, 10, 22, tzinfo=timezone.utc)}
fig.savefig(out / "brier-decomposition.pdf", bbox_inches="tight", metadata=metadata)
fig.savefig(out / "brier-decomposition.png", dpi=180, bbox_inches="tight")
plt.close(fig)
