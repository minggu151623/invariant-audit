"""Synthetic-only E004 boundary and differential tests; never opens real shards."""
import gzip
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess
import tempfile
import unittest
from unittest import mock

import audit


def row(i, value=0, kind="IssuesEvent"):
    return {"id": i, "type": kind, "payload": {"value": value}}


def encode(objects):
    return b"\n".join(audit.canonical(x) for x in objects) + b"\n"


class AggregationTests(unittest.TestCase):
    def check(self, raw, count):
        rows = audit.records(raw, count)
        first, second = audit.aggregate_dictionary(rows), audit.aggregate_sorted(rows)
        self.assertEqual(first, second)
        self.assertEqual(sum(first["occurrence_categories"].values()),
                         first["duplicate_extra_occurrences"])
        return first

    def test_no_duplicates(self):
        result = self.check(encode([row(1), row(2)]), 2)
        self.assertEqual(result["unique_ids"], 2)
        self.assertEqual(result["duplicate_extra_occurrences"], 0)
        self.assertIsNone(result["first_collision_lines"])

    def test_byte_repeats_blank_lines_and_crlf(self):
        raw = audit.canonical(row(1))
        result = self.check(b"\n" + raw + b"\r\n\n" + raw + b"\n", 2)
        self.assertEqual(result["first_collision_lines"], [2, 4])
        self.assertEqual(result["occurrence_categories"], dict(zip(audit.CATEGORIES, (1, 0, 0))))
        self.assertEqual(result["duplicate_id_groups"], 1)
        self.assertEqual(result["maximum_multiplicity"], 2)

    def test_reordered_keys_and_whitespace(self):
        a = b'{"id":1,"type":"WatchEvent","payload":{"value":0}}'
        b = b'{ "payload": {"value": 0}, "type": "WatchEvent", "id": 1 }'
        result = self.check(a + b"\n" + b + b"\n", 2)
        self.assertEqual(result["occurrence_categories"], dict(zip(audit.CATEGORIES, (0, 1, 0))))
        self.assertEqual(result["conflict_id_groups"], 0)

    def test_a_b_b_compares_to_first_not_previous(self):
        result = self.check(encode([row(1, "A"), row(1, "B"), row(1, "B")]), 3)
        self.assertEqual(result["occurrence_categories"], dict(zip(audit.CATEGORIES, (0, 0, 2))))
        self.assertEqual(result["conflict_id_groups"], 1)
        self.assertEqual(result["duplicate_id_groups"], 1)
        self.assertEqual(result["maximum_multiplicity"], 3)

    def test_id_normalization_preserves_full_object_types(self):
        result = self.check(encode([row(1), row("1")]), 2)
        self.assertEqual(result["unique_ids"], 1)
        self.assertEqual(result["conflict_id_groups"], 1)

    def test_conflict_types_and_earliest_collision(self):
        objs = [row(9, kind="WatchEvent"), row(1), row(9, 1, "PullRequestEvent"),
                row(1, 2), row(2, kind="CreateEvent")]
        result = self.check(encode(objs), 5)
        self.assertEqual(result["first_collision_lines"], [1, 3])
        self.assertEqual(result["conflict_id_groups"], 2)
        self.assertEqual(result["conflict_groups_touching_selected_types"],
                         {"IssuesEvent": 1, "PullRequestEvent": 1})
        self.assertEqual(result["duplicate_extras_by_type"], {"IssuesEvent": 1, "PullRequestEvent": 1})

    def test_array_order_and_unknown_fields_are_significant(self):
        result = self.check(encode([row(1, [1, 2]), row(1, [2, 1]),
                                   {**row(1, [1, 2]), "unknown": 1}]), 3)
        self.assertEqual(result["occurrence_categories"][audit.CATEGORIES[2]], 2)

    def test_cross_shard_ids_count_groups_not_occurrences(self):
        by_split = {"a": audit.records(encode([row(1), row(1), row(2)]), 3),
                    "b": audit.records(encode([row("1"), row(3)]), 2),
                    "c": audit.records(encode([row(4)]), 1)}
        self.assertEqual(audit.cross_shard_overlap(by_split), {"a__b": 1, "a__c": 0, "b__c": 0})

    def test_randomized_differential(self):
        rng = random.Random(184)
        for _ in range(40):
            objects = [row(rng.randrange(12), rng.randrange(4), rng.choice(
                ["IssuesEvent", "PullRequestEvent", "WatchEvent"])) for _ in range(100)]
            self.check(encode(objects), 100)


class InputTests(unittest.TestCase):
    def test_manifest_reconstruction(self):
        self.assertEqual(sha256(audit.original_manifest()).hexdigest(), audit.MANIFEST_SHA256)

    def test_invalid_ids_and_types(self):
        for value in [True, False, None, -1, 1.0, "01", "-1", "+1", "1.0", "", "１"]:
            with self.subTest(value=value), self.assertRaises(audit.AuditError):
                audit.records(encode([row(value)]), 1)
        with self.assertRaises(audit.AuditError):
            audit.records(encode([row(1, kind=4)]), 1)

    def test_malformed_json_objects(self):
        bad = [b'[]', b'null', b'{', b'\xff', b'{"id":1,"id":2,"type":"X"}',
               b'{"id":1,"type":"X","payload":{"a":1,"a":2}}',
               b'{"id":1,"type":"X","x":NaN}',
               b'{"id":1,"type":"X","x":1e999}']
        for raw in bad:
            with self.subTest(raw=raw), self.assertRaises(audit.AuditError):
                audit.records(raw, 1)

    def test_hash_size_and_count_gates(self):
        data = b"hello"
        audit.verify_bytes(data, 5, sha256(data).hexdigest())
        for size, digest in [(4, sha256(data).hexdigest()), (5, "0" * 64)]:
            with self.assertRaises(audit.AuditError):
                audit.verify_bytes(data, size, digest)
        with self.assertRaises(audit.AuditError):
            audit.records(encode([row(1)]), 2)

    def test_strict_gzip(self):
        data = gzip.compress(b"hello")
        self.assertEqual(audit.decompress(data), b"hello")
        for bad in [data[:-1], data + b"junk", data + data, b"junk"]:
            with self.assertRaises(audit.AuditError):
                audit.decompress(bad)


class OutputAndGateTests(unittest.TestCase):
    def test_existing_output_is_preserved(self):
        with tempfile.TemporaryDirectory() as name:
            a, b = Path(name) / "a.json", Path(name) / "b.md"
            a.write_bytes(b"original")
            with self.assertRaises(audit.AuditError):
                audit.publish_pair(a, b, b"new", b"new")
            self.assertEqual(a.read_bytes(), b"original")
            self.assertFalse(b.exists())

    def test_partial_publication_is_cleaned(self):
        with tempfile.TemporaryDirectory() as name:
            a, b = Path(name) / "a.json", Path(name) / "b.md"
            real_open = Path.open
            def fail_second(path, *args, **kwargs):
                if path == b:
                    raise OSError("simulated failure")
                return real_open(path, *args, **kwargs)
            with mock.patch.object(Path, "open", fail_second), self.assertRaises(OSError):
                audit.publish_pair(a, b, b"json", b"markdown")
            self.assertFalse(a.exists())
            self.assertFalse(b.exists())

    def test_publish_complete_pair(self):
        with tempfile.TemporaryDirectory() as name:
            a, b = Path(name) / "a.json", Path(name) / "b.md"
            audit.publish_pair(a, b, b"json", b"markdown")
            self.assertEqual((a.read_bytes(), b.read_bytes()), (b"json", b"markdown"))

    def test_gate_dirty_tree_and_ancestry(self):
        with mock.patch.object(audit, "git", return_value=" M dirty"):
            with self.assertRaisesRegex(audit.AuditError, "dirty"):
                audit.gate()
        with mock.patch.object(audit, "git", side_effect=["", "head"]), mock.patch.object(
            audit.subprocess, "run", return_value=subprocess.CompletedProcess([], 1)
        ):
            with self.assertRaisesRegex(audit.AuditError, "ancestor"):
                audit.gate()

    def test_protocol_drift(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            path = root / audit.PROTOCOL_PATH
            path.parent.mkdir(parents=True)
            path.write_bytes(b"changed")
            with mock.patch.object(audit, "git", side_effect=["", "head"]), mock.patch.object(
                audit.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)
            ), mock.patch.object(audit.subprocess, "check_output", return_value=b"locked"):
                with self.assertRaisesRegex(audit.AuditError, "identity"):
                    audit.gate(root=root)


if __name__ == "__main__":
    unittest.main()
