from fractions import Fraction as F
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import audit


def row(truth=1, decision=True, p=F(1), **extra):
    return dict(truth=truth, decision=decision, p_valid=p, method="M1",
                split="calibration", raw_score=0, **extra)


class MetricTests(unittest.TestCase):
    def test_confusion_and_probability_metrics_known_answer(self):
        rows = [row(1, True, F(4, 5)), row(1, False, F(1, 5)),
                row(0, True, F(4, 5)), row(0, False, F(1, 5))]
        result = audit.statistics(rows)
        self.assertEqual([result[k] for k in ("tp", "tn", "fp", "fn")], [1, 1, 1, 1])
        self.assertEqual(result["balanced_accuracy"], F(1, 2))
        self.assertEqual(result["brier"], F(17, 50))
        self.assertEqual(result["ece"], F(3, 10))
        self.assertEqual(result["reliability"], F(9, 100))
        self.assertEqual(result["resolution"], 0)
        self.assertEqual(result["uncertainty"], F(1, 4))
        self.assertEqual(result["brier_identity_residual"], 0)

    def test_brier_identity_mixed_score_group_frequencies(self):
        rows = [row(0, False, F(1, 5)), row(1, False, F(1, 5)),
                row(1, True, F(4, 5)), row(1, True, F(4, 5))]
        result = audit.statistics(rows)
        self.assertEqual(result["resolution"], F(1, 16))
        self.assertEqual(result["reliability"], F(13, 200))
        self.assertEqual(result["uncertainty"], F(3, 16))
        self.assertEqual(result["brier"], F(19, 100))

    def test_bin_edges_and_final_endpoint(self):
        self.assertEqual([audit.probability_bin(F(i, 10)) for i in range(11)], list(range(10)) + [9])
        self.assertEqual(audit.probability_bin(F(999, 10000)), 0)
        with self.assertRaises(audit.AuditError):
            audit.probability_bin(F(11, 10))

    def test_bin_cancellation_does_not_equal_score_group_reliability(self):
        rows = [row(1, True, F(51, 100)), row(0, True, F(59, 100))]
        result = audit.statistics(rows)
        self.assertEqual(result["ece"], F(1, 20))
        self.assertGreater(result["reliability"], result["ece"]**2)

    def test_perfect_binary_score_and_constant_base_rate(self):
        binary = audit.statistics([row(1, True, F(1)), row(0, False, F(0))])
        constant = audit.statistics([row(1, True, F(1, 2)), row(0, True, F(1, 2))])
        self.assertEqual((binary["brier"], binary["ece"], binary["resolution"]), (0, 0, F(1, 4)))
        self.assertEqual((constant["brier"], constant["ece"], constant["resolution"]), (F(1, 4), 0, 0))

    def test_undefined_denominators_fail_closed(self):
        for rows in ([], [row()]):
            with self.assertRaises(audit.AuditError):
                audit.statistics(rows)

    def test_cluster_signature_counts_not_identifiers_or_order(self):
        rows = [row(0, False, F(1, 5), case_id="a"), row(1, True, F(4, 5), case_id="b")]
        other = [dict(r, case_id="different") for r in reversed(rows)]
        self.assertEqual(audit.cluster_signature(rows), audit.cluster_signature(other))
        other[0]["p_valid"] = F(3, 4)
        self.assertNotEqual(audit.cluster_signature(rows), audit.cluster_signature(other))


class ParsingTests(unittest.TestCase):
    def encoded(self, **changes):
        value = dict(truth=1, decision=True, p_valid=0.8, method="M1", split="development",
                     raw_score=0, case_id="case", base_case_id="base", input_sha256="a"*64,
                     status="valid")
        value.update(changes)
        return json.dumps(value).encode() + b"\n"

    def test_probability_read_as_exact_decimal(self):
        self.assertEqual(audit.read_predictions(self.encoded(), "E001")[0]["p_valid"], F(4, 5))

    def test_duplicate_keys_and_case_keys_rejected(self):
        for content in (b'{"truth":1,"truth":0}', self.encoded() * 2):
            with self.assertRaises(audit.AuditError):
                audit.read_predictions(content, "E001")

    def test_invalid_types_ranges_and_identifiers(self):
        for changes in ({"p_valid": True}, {"p_valid": -0.1}, {"p_valid": float("nan")},
                        {"truth": True}, {"truth": 2}, {"decision": 1}, {"raw_score": -1},
                        {"input_sha256": "bad"}, {"case_id": ""}, {"method": "unknown"},
                        {"split": "test"}, {"status": "invalid"}):
            with self.subTest(changes=changes), self.assertRaises(audit.AuditError):
                audit.read_predictions(self.encoded(**changes), "E001")


class CalibrationTests(unittest.TestCase):
    def test_smoothing_and_unseen_score_fallback(self):
        calibration = [row(1, True, F(2, 3)), dict(row(0, False, F(1, 3)), raw_score=1)]
        lookup, fallback = audit.fit_lookup(calibration)
        self.assertEqual((lookup, fallback), ({0: F(2, 3), 1: F(1, 3)}, F(1, 2)))
        rows = calibration + [dict(row(1, True, F(1, 2)), raw_score=9, split="confirmatory")]
        self.assertEqual(audit.calibration_error(rows, F(1, 10**9)), 0)

    def test_reject_mixed_splits_and_probability_mismatch(self):
        with self.assertRaises(audit.AuditError):
            audit.fit_lookup([dict(row(), split="confirmatory")])
        with self.assertRaises(audit.AuditError):
            audit.calibration_error([row(1, True, F(9, 10))], F(1, 10**9))

    def test_rounding_tolerance(self):
        self.assertLess(audit.calibration_error([row(1, True, F(666666667, 10**9))], F(1, 10**9)),
                        F(1, 10**9))

    def test_binary_ablation_is_exact(self):
        rows = [dict(row(1, True, F(1)), method="M1-no-calibration")]
        self.assertEqual(audit.calibration_error(rows, F(1, 10**9)), 0)
        rows[0]["p_valid"] = F(999999999, 10**9)
        with self.assertRaises(audit.AuditError):
            audit.calibration_error(rows, F(1, 10**9))


class AlignmentTests(unittest.TestCase):
    def fixture(self):
        spec = {"methods": ("M1", "M1-no-calibration"), "cluster": "cluster", "cases": (1, 1, 1)}
        rows = [dict(row(), method=method, split=split, case_id=split, cluster=split,
                     input_sha256=str(i)*64)
                for i, split in enumerate(audit.SPLITS) for method in spec["methods"]]
        return rows, spec

    def test_alignment_and_split_checks(self):
        rows, spec = self.fixture()
        self.assertEqual(audit.alignment_checks(rows, spec)["cross_split_cluster_overlap"], 0)
        for change in ("truth", "input_sha256", "cluster", "decision"):
            broken = [dict(r) for r in rows]
            broken[0][change] = False if change == "decision" else 0 if change == "truth" else "other"
            with self.subTest(change=change), self.assertRaises(audit.AuditError):
                audit.alignment_checks(broken, spec)
        with self.assertRaises(audit.AuditError):
            audit.alignment_checks(rows[:-1], spec)

    def test_cross_split_overlap_is_reported_without_causal_claim(self):
        rows, spec = self.fixture()
        for item in rows:
            item["input_sha256"] = "same"
        self.assertEqual(set(audit.alignment_checks(rows, spec)["cross_split_input_hash_overlap"].values()), {1})
        for item in rows:
            item["cluster"] = "same"
        with self.assertRaises(audit.AuditError):
            audit.alignment_checks(rows, spec)


class PublicationTests(unittest.TestCase):
    def test_late_failure_rolls_back_only_owned_files(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "keep").write_bytes(b"original")
            outputs = {"a": b"first", "b": b"second", "result": b"valid last"}
            original_link = os.link
            calls = []

            def failing_link(source, destination):
                calls.append(destination.name)
                if destination.name == "result":
                    raise OSError("simulated late failure")
                original_link(source, destination)

            with patch.object(audit.os, "link", side_effect=failing_link), self.assertRaises(OSError):
                audit.publish(root, outputs)
            self.assertEqual(calls, ["a", "b", "result"])
            self.assertEqual(list(root.iterdir()), [root / "keep"])
            self.assertEqual((root / "keep").read_bytes(), b"original")

    def test_existing_destination_is_preserved(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "exists").write_bytes(b"old")
            with self.assertRaises(audit.AuditError):
                audit.publish(root, {"exists": b"new"})
            self.assertEqual((root / "exists").read_bytes(), b"old")

    def test_symlink_ancestor_is_refused(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "actual").mkdir()
            (root / "redirect").symlink_to(root / "actual", target_is_directory=True)
            with self.assertRaises(audit.AuditError):
                audit.publish(root, {"redirect/output": b"new"})
            self.assertEqual(list((root / "actual").iterdir()), [])

    def test_execute_refuses_existing_outputs_before_git_or_input_reads(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "data").mkdir()
            (root / audit.OUTPUTS[0]).write_bytes(b"existing")
            with patch.object(audit, "git") as git_call, self.assertRaises(audit.AuditError):
                audit.execute(root)
            git_call.assert_not_called()

    def test_bad_input_hash_refused_before_parsing(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            (root / "data").mkdir()
            source = root / "data/E001-v1-predictions.jsonl"
            source.write_bytes(b"untrusted")
            with patch.object(audit, "read_predictions") as parser, self.assertRaises(audit.AuditError):
                audit.build(root, "protocol", "implementation")
            parser.assert_not_called()
            self.assertEqual(source.read_bytes(), b"untrusted")


if __name__ == "__main__":
    unittest.main()
