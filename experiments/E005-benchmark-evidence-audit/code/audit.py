"""Recompute the frozen E001/E002 evidence without importing either harness."""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from decimal import Decimal, localcontext
from fractions import Fraction
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

PROTOCOL_COMMIT = "2e6f7c2"
PROTOCOL_PATH = "experiments/E005-benchmark-evidence-audit/protocol.md"
RUN_ID = "e005-20261022-001"
SPLITS = ("development", "calibration", "confirmatory")
EXPERIMENTS = {
    "E001": {
        "predictions": ("be5e5e2a6c3f33778a34af69d79ec4f14e3b2c0cba2f371ecc004310b7c9559a", 5120),
        "metrics": ("ae7c32be651b5dfe175ca0537aa3cb8283acbd7063b14e15b8ec386f0d6a20cb", 75),
        "methods": ("B0", "M1", "M1-no-semantic", "M1-no-state", "M1-no-calibration"),
        "cases": (256, 256, 512),
        "cluster": "base_case_id",
        "tolerance": Fraction(1, 10**9),
    },
    "E002": {
        "predictions": ("bcb34aad4338fdfbffe07be1843769b360bf4e8c422d855a9ce605350fad13b7", 7296),
        "metrics": ("f000348d385550745480066fce2d691686728ebe2bfcf7bd96e7231e4b1e5ca3", 243),
        "methods": ("B0", "M1", "M1-omit-conservation", "M1-overconstraint",
                    "M1-stale-transition", "M1-no-semantic", "M1-no-state", "M1-no-calibration"),
        "cases": (228, 228, 456),
        "cluster": "cluster_id",
        "tolerance": Fraction(2, 10**9),
    },
}
METRICS = ("balanced_accuracy", "fpr", "fnr", "brier", "ece")
RESULT_PATH = f"experiments/E005-benchmark-evidence-audit/results/run-{RUN_ID}.md"
OUTPUTS = ("data/E005-v1-summary.csv", "data/E005-v1-score-groups.csv",
           "data/E005-v1-checks.json", RESULT_PATH)


class AuditError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise AuditError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def reject_constant(_token):
    raise AuditError("nonfinite JSON number")


def read_predictions(content, experiment):
    spec = EXPERIMENTS[experiment]
    rows, seen = [], set()
    for line in content.decode("utf-8").splitlines():
        row = json.loads(line, parse_float=Decimal, object_pairs_hook=unique_object,
                         parse_constant=reject_constant)
        require(type(row) is dict, "prediction must be an object")
        require(row.get("split") in SPLITS and row.get("method") in spec["methods"],
                "unknown split/method")
        for field in ("case_id", spec["cluster"]):
            require(type(row.get(field)) is str and bool(row[field]), "missing case/cluster ID")
        require(type(row.get("truth")) is int and row["truth"] in (0, 1), "invalid truth")
        require(type(row.get("decision")) is bool, "invalid decision")
        require(type(row.get("raw_score")) is int and row["raw_score"] >= 0, "invalid score")
        require(type(row.get("p_valid")) in (int, Decimal), "invalid probability type")
        probability = Fraction(row["p_valid"])
        require(0 <= probability <= 1, "invalid probability range")
        require(type(row.get("input_sha256")) is str and
                re.fullmatch(r"[0-9a-f]{64}", row["input_sha256"]), "invalid input hash")
        require(row.get("status") == "valid", "invalid source row status")
        key = (row["split"], row["case_id"], row["method"])
        require(key not in seen, "duplicate prediction key")
        seen.add(key)
        rows.append(dict(row, p_valid=probability))
    return rows


def number(value):
    with localcontext() as context:
        context.prec = 60
        result = Decimal(value.numerator) / Decimal(value.denominator)
        return format(result, ".18f")


def probability_bin(probability):
    require(0 <= probability <= 1, "probability outside bins")
    return min(9, int(probability * 10))


def statistics(rows):
    require(bool(rows), "empty metric support")
    counts = Counter((int(row["decision"]), row["truth"]) for row in rows)
    tp, tn, fp, fn = (counts[1, 1], counts[0, 0], counts[1, 0], counts[0, 1])
    require(tp + fn > 0 and tn + fp > 0, "undefined confusion denominator")
    groups, bins = defaultdict(list), defaultdict(list)
    for row in rows:
        groups[row["p_valid"]].append(row["truth"])
        bins[probability_bin(row["p_valid"])].append(row)
    total = len(rows)
    prevalence = Fraction(tp + fn, total)
    brier = sum((row["p_valid"] - row["truth"])**2 for row in rows) / total
    ece = sum(abs(sum(row["p_valid"] - row["truth"] for row in block))
              for block in bins.values()) / total
    reliability = sum(Fraction(len(truth), total) * (p - Fraction(sum(truth), len(truth)))**2
                      for p, truth in groups.items())
    resolution = sum(Fraction(len(truth), total) * (Fraction(sum(truth), len(truth)) - prevalence)**2
                     for truth in groups.values())
    uncertainty = prevalence * (1 - prevalence)
    residual = brier - reliability + resolution - uncertainty
    require(residual == 0, "Brier decomposition identity failed")
    return {"support": total, "tp": tp, "tn": tn, "fp": fp, "fn": fn,
            "balanced_accuracy": (Fraction(tp, tp + fn) + Fraction(tn, tn + fp)) / 2,
            "fpr": Fraction(fp, tn + fp), "fnr": Fraction(fn, tp + fn),
            "brier": brier, "ece": ece, "reliability": reliability,
            "resolution": resolution, "uncertainty": uncertainty,
            "brier_identity_residual": residual, "score_groups": len(groups)}


def fit_lookup(rows):
    require(bool(rows) and all(row["split"] == "calibration" for row in rows),
            "lookup fitting requires calibration only")
    require(len({row["method"] for row in rows}) == 1, "mixed-method lookup")
    groups = defaultdict(list)
    for row in rows:
        groups[row["raw_score"]].append(row["truth"])
    lookup = {score: Fraction(sum(truth) + 1, len(truth) + 2)
              for score, truth in groups.items()}
    fallback = Fraction(sum(row["truth"] for row in rows) + 1, len(rows) + 2)
    return lookup, fallback


def calibration_error(rows, tolerance):
    method = rows[0]["method"]
    require(all(row["method"] == method for row in rows), "mixed calibration audit")
    if method == "M1-no-calibration":
        errors = [abs(row["p_valid"] - int(row["decision"])) for row in rows]
        require(max(errors) == 0, "binary ablation probability mismatch")
    else:
        lookup, fallback = fit_lookup([row for row in rows if row["split"] == "calibration"])
        errors = [abs(row["p_valid"] - lookup.get(row["raw_score"], fallback)) for row in rows]
        require(max(errors) <= tolerance, "calibration-only reconstruction mismatch")
    return max(errors)


def alignment_checks(rows, spec):
    cases, split_clusters, split_hashes = defaultdict(list), defaultdict(set), defaultdict(set)
    for row in rows:
        cases[row["split"], row["case_id"]].append(row)
        split_clusters[row["split"]].add(row[spec["cluster"]])
        split_hashes[row["split"]].add(row["input_sha256"])
    counts = Counter()
    ablation_disagreements = 0
    for (split, _case), block in cases.items():
        require(len(block) == len(spec["methods"]) and
                {row["method"] for row in block} == set(spec["methods"]), "incomplete method coverage")
        require(len({(row["truth"], row["input_sha256"], row[spec["cluster"]]) for row in block}) == 1,
                "case truth/input/cluster mismatch across methods")
        decisions = {row["method"]: row["decision"] for row in block}
        ablation_disagreements += decisions["M1"] != decisions["M1-no-calibration"]
        counts[split] += 1
    require(ablation_disagreements == 0, "binary ablation decision mismatch")
    require(tuple(counts[s] for s in SPLITS) == spec["cases"], "split case counts mismatch")
    overlaps = {}
    for i, split in enumerate(SPLITS):
        for other in SPLITS[i + 1:]:
            require(not split_clusters[split] & split_clusters[other], "cross-split cluster overlap")
            overlaps[f"{split}:{other}"] = len(split_hashes[split] & split_hashes[other])
    return {"case_counts": dict(counts), "cross_split_cluster_overlap": 0,
            "cross_split_input_hash_overlap": overlaps, "binary_ablation_decision_mismatches": 0}


def cluster_signature(rows):
    counts = Counter((int(row["decision"]), row["truth"]) for row in rows)
    bins = [[] for _ in range(10)]
    for row in rows:
        bins[probability_bin(row["p_valid"])].append(row)
    return (tuple(counts[key] for key in ((1, 1), (0, 0), (1, 0), (0, 1))),
            sum((row["p_valid"] - row["truth"])**2 for row in rows),
            tuple((len(block), sum(row["p_valid"] for row in block), sum(row["truth"] for row in block))
                  for block in bins))


def metric_reference_rows(content, experiment):
    rows = list(csv.DictReader(io.StringIO(content.decode("utf-8"))))
    require(len(rows) == EXPERIMENTS[experiment]["metrics"][1], "metric input row count")
    result = {}
    for row in rows:
        if row["subgroup"] != "overall" or row["method"] not in EXPERIMENTS[experiment]["methods"]:
            continue
        if experiment == "E002" and row["row_kind"] != "method":
            continue
        key = row["split"], row["method"]
        require(key not in result, "duplicate metric reference")
        result[key] = row
    require(set(result) == {(s, m) for s in SPLITS for m in EXPERIMENTS[experiment]["methods"]},
            "metric reference coverage")
    return result


def audit_experiment(predictions, metrics_content, experiment):
    spec = EXPERIMENTS[experiment]
    rows = read_predictions(predictions, experiment)
    require(len(rows) == spec["predictions"][1], "prediction input row count")
    checks = alignment_checks(rows, spec)
    references = metric_reference_rows(metrics_content, experiment)
    summary, score_groups, comparisons = [], [], []
    for method in spec["methods"]:
        method_rows = [row for row in rows if row["method"] == method]
        max_lookup_error = calibration_error(method_rows, spec["tolerance"])
        for split in SPLITS:
            block = [row for row in method_rows if row["split"] == split]
            stats = statistics(block)
            reference = references[split, method]
            for field in ("support", "tp", "tn", "fp", "fn"):
                ref_field = field.upper() if experiment == "E001" and field != "support" else field
                require(stats[field] == int(reference[ref_field]), "confusion/reference mismatch")
            for field in METRICS:
                ref_field = ({"fpr": "FPR", "fnr": "FNR", "brier": "Brier", "ece": "ECE"}.get(field, field)
                             if experiment == "E001" else field)
                difference = stats[field] - Fraction(reference[ref_field])
                require(abs(difference) <= spec["tolerance"], "metric/reference rounding mismatch")
                comparisons.append({"experiment": experiment, "split": split, "method": method,
                                    "metric": field, "signed_difference": number(difference)})
            clusters = defaultdict(list)
            for row in block:
                clusters[row[spec["cluster"]]].append(row)
            item = {"experiment": experiment, "split": split, "method": method,
                    **{k: number(v) if isinstance(v, Fraction) else v for k, v in stats.items()},
                    "clusters": len(clusters),
                    "distinct_cluster_signatures": len({cluster_signature(c) for c in clusters.values()}),
                    "calibration_reconstruction_max_error": number(max_lookup_error)}
            summary.append(item)
            if split == "confirmatory" and method in ("B0", "M1", "M1-no-calibration"):
                groups = defaultdict(list)
                for row in block:
                    groups[row["p_valid"]].append(row["truth"])
                for p, truth in sorted(groups.items()):
                    score_groups.append({"experiment": experiment, "split": split, "method": method,
                                         "probability": number(p), "count": len(truth),
                                         "positive_count": sum(truth),
                                         "observed_frequency": number(Fraction(sum(truth), len(truth)))})
    checks.update({"metric_comparisons": comparisons, "metric_agreement": True,
                   "calibration_compatible_with_calibration_only_fit": True,
                   "historical_no_leakage_proven": False,
                   "brier_identity_exact": True})
    return summary, score_groups, checks


def csv_bytes(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=tuple(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def git(root, *arguments):
    return subprocess.check_output(["git", *arguments], cwd=root, stderr=subprocess.PIPE)


def build(root, protocol_commit, implementation_commit):
    inputs = {}
    inventory = []
    for experiment, spec in EXPERIMENTS.items():
        for kind, extension in (("predictions", "jsonl"), ("metrics", "csv")):
            path = f"data/{experiment}-v1-{kind}.{extension}"
            content = (root / path).read_bytes()
            digest = sha256(content).hexdigest()
            require(digest == spec[kind][0], "frozen input hash mismatch")
            inputs[experiment, kind] = content
            inventory.append({"path": path, "sha256": digest, "bytes": len(content)})
    summary, groups, audit_checks = [], [], {}
    for experiment in EXPERIMENTS:
        result = audit_experiment(inputs[experiment, "predictions"], inputs[experiment, "metrics"], experiment)
        summary.extend(result[0])
        groups.extend(result[1])
        audit_checks[experiment] = result[2]
    checks = {"protocol_id": "E005-v1", "protocol_commit": protocol_commit,
              "protocol_sha256": sha256((root / PROTOCOL_PATH).read_bytes()).hexdigest(),
              "implementation_commit": implementation_commit, "run_id": RUN_ID,
              "classification": "exploratory_reanalysis", "inputs": inventory,
              "checks": audit_checks, "independent_review": False,
              "public_claim_eligibility": False}
    outputs = {OUTPUTS[0]: csv_bytes(summary), OUTPUTS[1]: csv_bytes(groups),
               OUTPUTS[2]: (json.dumps(checks, sort_keys=True, indent=2) + "\n").encode("utf-8")}
    lines = [f"# E005-v1 evidence audit — {RUN_ID}", "", "status: valid",
             "classification: exploratory_reanalysis", f"protocol_commit: {protocol_commit}",
             f"implementation_commit: {implementation_commit}", "independent_review: absent",
             "public_claim_eligibility: false", "", "## Confirmatory-split descriptive audit", "",
             "| Design | Method | N | BA | FPR | FNR | Brier | ECE | Reliability | Resolution | Uncertainty | Cluster signatures / clusters |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for row in summary:
        if row["split"] == "confirmatory":
            fields = [row[k] for k in ("experiment", "method", "support", "balanced_accuracy", "fpr", "fnr",
                                       "brier", "ece", "reliability", "resolution", "uncertainty")]
            lines.append("| " + " | ".join(map(str, fields)) +
                         f" | {row['distinct_cluster_signatures']} / {row['clusters']} |")
    lines += ["", "## Audit checks", "",
              "All four input hashes match. Every overall split/method confusion count agrees exactly;",
              "all five metrics agree with immutable CSVs within the locked rounding tolerances.",
              "Every Brier score satisfies reliability - resolution + uncertainty exactly before display rounding.",
              "Calibration probabilities are compatible with fitting the smoothed lookup on calibration rows only.",
              "Case/method alignment, complete coverage, split cluster disjointness and paired binary-ablation",
              "decisions pass. Cross-split input-hash overlap counts are recorded in the checks JSON.",
              "", "## Interpretation and limits", "",
              "This is a post-hoc audit of previously inspected synthetic artifacts, not a new confirmatory",
              "benchmark. Distinct cluster signatures are not an effective sample size. Exact score-group",
              "reliability is an empirical finite-sample quantity, distinct from ten-bin ECE and population",
              "calibration. Reconstructing probabilities cannot prove historical fitting order or no leakage.",
              "Perfect agreement and zero binary Brier do not show external validity. Original bootstrap",
              "intervals were not rerun or altered. Self-review is not independent acceptance.",
              "", "## Outputs", ""]
    for path, content in outputs.items():
        lines.append(f"- `{path}` SHA-256 `{sha256(content).hexdigest()}`")
    lines += ["", "Reproduce: `PYTHONDONTWRITEBYTECODE=1 python3 experiments/E005-benchmark-evidence-audit/code/audit.py`",
              "(refuses existing destinations; use a separate clean checkout to reproduce).", "",
              "deviations: none", ""]
    outputs[RESULT_PATH] = "\n".join(lines).encode("utf-8")
    return outputs


def publish(root, outputs):
    owned = []
    try:
        with tempfile.TemporaryDirectory(prefix=".e005-stage-", dir=root) as staging:
            for index, (path, content) in enumerate(outputs.items()):
                destination = root / path
                require(destination.parent.is_dir() and not destination.is_symlink(), "unsafe output parent")
                require(not Path(path).is_absolute() and ".." not in Path(path).parts, "unsafe output path")
                for parent in destination.parents:
                    if parent == root:
                        break
                    require(not parent.is_symlink(), "symlink output ancestor")
                require(not destination.exists(), "output already exists")
                staged = Path(staging) / str(index)
                staged.write_bytes(content)
                require(staged.read_bytes() == content, "staged bytes mismatch")
                os.link(staged, destination)
                stat = staged.stat()
                owned.append((destination, (stat.st_dev, stat.st_ino)))
                require(destination.read_bytes() == content, "published bytes mismatch")
    except BaseException:
        for destination, identity in reversed(owned):
            if destination.is_symlink():
                raise AuditError("refusing cleanup of replaced destination")
            stat = destination.stat()
            require((stat.st_dev, stat.st_ino) == identity, "refusing cleanup of replaced destination")
            destination.unlink()
        raise


def execute(root):
    root = Path(root).resolve()
    require(all(not (root / path).exists() and not (root / path).is_symlink() for path in OUTPUTS),
            "output exists; do not retry")
    protocol_commit = git(root, "rev-parse", PROTOCOL_COMMIT).decode().strip()
    require(git(root, "show", f"{protocol_commit}:{PROTOCOL_PATH}") == (root / PROTOCOL_PATH).read_bytes(),
            "locked protocol drift")
    git(root, "merge-base", "--is-ancestor", protocol_commit, "HEAD")
    implementation_commit = git(root, "rev-parse", "HEAD").decode().strip()
    for path in sorted((root / "experiments/E005-benchmark-evidence-audit/code").glob("*.py")):
        relative = path.relative_to(root).as_posix()
        require(git(root, "show", f"HEAD:{relative}") == path.read_bytes(), "implementation uncommitted")
    try:
        first = build(root, protocol_commit, implementation_commit)
        second = build(root, protocol_commit, implementation_commit)
        require(first == second, "two-build byte determinism failed")
        publish(root, first)
    except BaseException:
        require(all(not (root / path).exists() for path in OUTPUTS), "partial audit outputs remain")
        invalid = (f"# E005-v1 invalid audit — {RUN_ID}\nstatus: invalid\n"
                   f"protocol_commit: {protocol_commit}\nimplementation_commit: {implementation_commit}\n"
                   "No valid audit result. A reviewed remediation and new run ID are required.\n").encode()
        with (root / RESULT_PATH).open("xb") as stream:
            stream.write(invalid)
        raise
    return {path: sha256(content).hexdigest() for path, content in first.items()}


if __name__ == "__main__":
    print(json.dumps(execute(Path(__file__).resolve().parents[3]), sort_keys=True, indent=2))
