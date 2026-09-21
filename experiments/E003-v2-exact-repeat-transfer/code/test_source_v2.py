"""Synthetic-only tests; no file, source-cache, network or performance I/O."""
from dataclasses import FrozenInstanceError, replace
import gzip
from hashlib import sha256
import json
import unittest
from unittest.mock import patch

import source_v2 as s


def record(i=1, **fields):
    return json.dumps({"id": i, "type": "IssuesEvent", "repo": {"id": 7}, **fields},
                      separators=(",", ":")).encode()


def fixture(lines, split="development", count=None):
    plain = b"\n".join(lines) + b"\n"
    data = gzip.compress(plain, mtime=0)
    return s.SourceInput(split, split + ".json.gz", data, len(data),
                         sha256(data).hexdigest(),
                         count if count is not None else sum(bool(x.strip()) for x in lines))


class SourceTests(unittest.TestCase):
    def test_unique_order_and_input_immutability(self):
        source = fixture([record(9), record(2)])
        before = source.compressed
        result = s.normalize_sources([source])
        self.assertEqual([r.event_id for r in result.records], ["9", "2"])
        self.assertEqual(before, source.compressed)
        with self.assertRaises(FrozenInstanceError):
            result.records[0].line = 3

    def test_exact_repeats_and_multiplicity(self):
        result = s.normalize_sources([fixture([record()] * 3)])
        x = result.summaries[0]
        self.assertEqual((x.raw_count,x.unique_count,x.collapsed_extras), (3,1,2))
        self.assertEqual((x.repeated_groups,x.maximum_multiplicity), (1,3))
        self.assertEqual(x.extras_by_type, (("IssuesEvent",2),))

    def test_crlf_blanks_coordinates(self):
        result = s.normalize_sources([fixture([b"", record()+b"\r", b"  ", record()])])
        self.assertEqual(result.records[0].line, 2)
        self.assertEqual(result.summaries[0].first_collision, (2,4))

    def test_only_one_trailing_cr_removed(self):
        with self.assertRaisesRegex(s.SourceError,"nonidentical"):
            s.normalize_sources([fixture([record()+b"\r\r",record()])])

    def test_no_final_lf(self):
        source=fixture([record()])
        data=gzip.compress(record(),mtime=0)
        source=replace(source,compressed=data,expected_bytes=len(data),expected_sha256=sha256(data).hexdigest())
        self.assertEqual(s.normalize_sources([source]).records[0].line,1)

    def test_spacing_and_key_order_are_conflicts(self):
        obj=json.loads(record())
        for different in [record()+b" ",json.dumps(obj,sort_keys=True).encode()]:
            with self.subTest(different=different), self.assertRaisesRegex(s.SourceError,"nonidentical"):
                s.normalize_sources([fixture([record(),different])])

    def test_ignored_fields_are_not_dropped(self):
        with self.assertRaisesRegex(s.SourceError,"nonidentical"):
            s.normalize_sources([fixture([record(ignored="a"),record(ignored="b")])])

    def test_a_b_b_fails_without_partial_return(self):
        with self.assertRaisesRegex(s.SourceError,":2"):
            s.normalize_sources([fixture([record(),record(x=1),record(x=1)])])

    def test_int_string_id_is_conflict(self):
        with self.assertRaisesRegex(s.SourceError,"nonidentical"):
            s.normalize_sources([fixture([record(1),record("1")])])

    def test_invalid_ids_even_excluded_types(self):
        for value in [True,-1,1.0,"01","+1","١",None]:
            with self.subTest(value=value),self.assertRaises(s.SourceError):
                s.normalize_sources([fixture([record(value,type="PushEvent")])])
        self.assertEqual(s.decimal_id("0"),"0")

    def test_missing_id_type_and_nonobject(self):
        for raw in [b'{}',b'{"id":1}',b'{"id":1,"type":1}',b'[]']:
            with self.subTest(raw=raw),self.assertRaises(s.SourceError):
                s.normalize_sources([fixture([raw])])

    def test_bad_json_numbers_keys_unicode(self):
        for extra in [b'NaN',b'Infinity',b'1e999',b'"\\ud800"']:
            with self.subTest(extra=extra),self.assertRaises(s.SourceError):
                s.parse_record(b'{"id":1,"type":"PushEvent","x":'+extra+b'}')
        for raw in [b'\xff',b'{',b'{"id":1,"id":2,"type":"PushEvent"}']:
            with self.subTest(raw=raw),self.assertRaises(s.SourceError):
                s.parse_record(raw)

    def test_cross_shard_repeat_even_excluded_type(self):
        raw=record(type="PushEvent")
        with self.assertRaisesRegex(s.SourceError,"cross-shard"):
            s.normalize_sources([fixture([raw]),fixture([raw],"calibration")])

    def test_late_conflict_has_no_callback_or_yield(self):
        with self.assertRaises(s.SourceError):
            s.normalize_sources([fixture([record(1)]),fixture([record(2),record(2,x=3)],"calibration")])

    def test_all_type_repository_isolation(self):
        result=s.normalize_sources([fixture([record(1,type="PushEvent")]),fixture([record(2)],"calibration")])
        self.assertEqual(result.shared_repository_ids,frozenset({"7"}))

    def test_invalid_repository_not_indexed(self):
        result=s.normalize_sources([fixture([record(repo={"id":True})])])
        self.assertFalse(result.summaries[0].repository_ids)

    def test_all_hashes_before_any_parser_call(self):
        bad=replace(fixture([record(2)],"calibration"),expected_sha256="0"*64)
        with patch.object(s,"parse_record",side_effect=AssertionError("parsed too soon")):
            with self.assertRaisesRegex(s.SourceError,"pin mismatch"):
                s.normalize_sources([fixture([record()]),bad])

    def test_size_and_count_mismatch(self):
        source=fixture([record()])
        for bad in [replace(source,expected_bytes=0),replace(source,expected_records=2)]:
            with self.assertRaises(s.SourceError): s.normalize_sources([bad])

    def test_gzip_truncated_trailing_multimember(self):
        source=fixture([record()])
        for data in [source.compressed[:-1],source.compressed+b'x',source.compressed*2,b'bad']:
            changed=replace(source,compressed=data,expected_bytes=len(data),expected_sha256=sha256(data).hexdigest())
            with self.assertRaises(s.SourceError): s.normalize_sources([changed])

    def test_split_order_uniqueness_and_empty(self):
        a=fixture([record()]); b=fixture([record(2)],"calibration")
        for sources in [[],[a,a],[b,a],[replace(a,split="other")]]:
            with self.assertRaises(s.SourceError): s.normalize_sources(sources)

    def test_pinned_inventory_rejects_synthetic_sources(self):
        for sources in [[],[fixture([record()])], [fixture([record(i)],split) for i,split in enumerate(s.SPLITS)]]:
            with self.assertRaises(s.SourceError): s.normalize_pinned(sources)

    def test_manifest_derivation_no_external_read(self):
        files=[]
        for split,(name,size,count,digest) in zip(s.SPLITS,s.PINS):
            files.append(dict(split=split,filename=name,bytes=size,jsonl_lines=count,
                              sha256=digest,url="https://data.gharchive.org/"+name))
        original=(json.dumps(dict(files=files,protocol_id="E003-v1"),sort_keys=True,separators=(",",":"))+"\n").encode()
        self.assertEqual(sha256(original).hexdigest(),s.V1_MANIFEST_SHA256)
        derived=s.derive_manifest_v2(original)
        self.assertEqual(sha256(derived).hexdigest(),s.V2_MANIFEST_SHA256)
        self.assertEqual(json.loads(original)["protocol_id"],"E003-v1")
        with self.assertRaises(s.SourceError): s.derive_manifest_v2(original+b' ')


if __name__ == "__main__":
    unittest.main()
