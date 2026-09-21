"""Synthetic-only tests for E003-v2 adapter; no file, source-cache, network, or performance I/O."""
from dataclasses import FrozenInstanceError
import gzip
import hashlib
import json
import unittest
from types import SimpleNamespace

import adapter_v2 as a
import source_v2 as s


def make_issue(
    event_id: int | str = 1,
    repo_id: int | str = 10,
    number: int = 1,
    action: str = "opened",
    state: str | None = None,
    owner: str = "owner",
    repo_name: str = "repo",
    **extra,
) -> bytes:
    state = state or ("closed" if action == "closed" else "open")
    repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    data = {
        "id": event_id,
        "type": "IssuesEvent",
        "actor": {"id": 900, "login": "actor"},
        "repo": {"id": repo_id, "name": repo_name, "url": repo_url},
        "payload": {
            "action": action,
            "issue": {
                "id": int(event_id) * 10,
                "number": number,
                "state": state,
                "url": f"{repo_url}/issues/{number}",
                "repository_url": repo_url,
            },
        },
        "public": True,
        "created_at": "2020-01-15T12:00:00Z",
    }
    data.update(extra)
    return json.dumps(data, separators=(",", ":")).encode("utf-8")


def make_pr(
    event_id: int | str = 2,
    repo_id: int | str = 20,
    number: int = 1,
    action: str = "opened",
    state: str | None = None,
    merged: bool = False,
    owner: str = "owner",
    repo_name: str = "repo",
    **extra,
) -> bytes:
    state = state or ("closed" if action == "closed" else "open")
    repo_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    data = {
        "id": event_id,
        "type": "PullRequestEvent",
        "actor": {"id": 901, "login": "pr-actor"},
        "repo": {"id": repo_id, "name": repo_name, "url": repo_url},
        "payload": {
            "action": action,
            "number": number,
            "pull_request": {
                "id": int(event_id) * 10,
                "number": number,
                "state": state,
                "merged": merged,
                "url": f"{repo_url}/pulls/{number}",
            },
        },
        "public": True,
        "created_at": "2020-01-15T12:01:00Z",
    }
    data.update(extra)
    return json.dumps(data, separators=(",", ":")).encode("utf-8")


def make_push(
    event_id: int | str = 3,
    repo_id: int | str = 30,
    **extra,
) -> bytes:
    data = {
        "id": event_id,
        "type": "PushEvent",
        "actor": {"id": 902, "login": "pusher"},
        "repo": {"id": repo_id, "name": "repo", "url": "https://api.github.com/repos/owner/repo"},
        "payload": {"push_id": 123},
        "public": True,
        "created_at": "2020-01-15T12:02:00Z",
    }
    data.update(extra)
    return json.dumps(data, separators=(",", ":")).encode("utf-8")


def fixture(lines: list[bytes], split: str = "development", count: int | None = None) -> s.SourceInput:
    plain = b"\n".join(lines) + b"\n"
    data = gzip.compress(plain, mtime=0)
    return s.SourceInput(
        split=split,
        filename=f"{split}.json.gz",
        compressed=data,
        expected_bytes=len(data),
        expected_sha256=hashlib.sha256(data).hexdigest(),
        expected_records=count if count is not None else sum(bool(x.strip()) for x in lines),
    )


def generate_valid_split_records(
    split_index: int = 0,
    num_issues: int = 64,
    num_prs: int = 64,
    issues_repo_offset: int = 1000,
    prs_repo_offset: int = 2000,
    event_id_offset: int = 10_000,
) -> list[bytes]:
    """Generates valid issues and PR records satisfying all base selection quotas."""
    records = []
    base_id = split_index * 100_000 + event_id_offset

    # 25 repos for issues (each repo gets at most 3 issues <= cap 4)
    for i in range(num_issues):
        ev_id = base_id + i
        repo_id = issues_repo_offset + (i % 25)
        owner = f"owner_{repo_id}"
        repo_name = f"repo_{repo_id}"
        records.append(make_issue(
            event_id=ev_id,
            repo_id=repo_id,
            number=i + 1,
            owner=owner,
            repo_name=repo_name,
        ))

    # 25 repos for PRs (total 50 unique repos in split >= 24 min overall, 25 >= 16 min per type)
    for i in range(num_prs):
        ev_id = base_id + num_issues + i
        repo_id = prs_repo_offset + (i % 25)
        owner = f"owner_{repo_id}"
        repo_name = f"repo_{repo_id}"
        records.append(make_pr(
            event_id=ev_id,
            repo_id=repo_id,
            number=i + 1,
            owner=owner,
            repo_name=repo_name,
        ))

    return records


class AdapterV2Tests(unittest.TestCase):
    def test_duplicates_and_coordinates(self):
        """Exact repeats collapse, preserving first occurrence coordinates and source digest."""
        iss1 = make_issue(event_id=1, repo_id=10, number=1)
        iss2 = make_issue(event_id=2, repo_id=11, number=2)

        # Blank line at line 1, iss1 at line 2, iss2 at line 3, exact iss1 duplicate at line 4
        lines = [b"", iss1, iss2, iss1]
        valid_extras = generate_valid_split_records(
            split_index=0, num_issues=63, num_prs=64, issues_repo_offset=1000, prs_repo_offset=2000
        )
        source = fixture(lines + valid_extras, split="development")
        result = a.adapt_sources([source])

        scan = result.scan_for("development")
        self.assertEqual(scan.raw_count, 2 + 1 + len(valid_extras))  # 3 non-empty + extras
        self.assertEqual(scan.collapsed_extras, 1)
        self.assertEqual(scan.unique_count, scan.raw_count - 1)

        # Event 1 was at line 2 (first occurrence)
        ev1 = next(e for e in scan.eligible if e.event_id == "1")
        self.assertEqual(ev1.source_line, 2)
        self.assertEqual(ev1.source_file, "development.json.gz")
        self.assertEqual(ev1.source_sha256, source.expected_sha256)

    def test_excluded_type_shared_repos(self):
        """Repository from excluded type (PushEvent) in split A excludes eligible event in split B."""
        shared_repo_id = 9999
        # Split 1 (development): has PushEvent with repo 9999
        push_event = make_push(event_id=1, repo_id=shared_repo_id)
        dev_records = [push_event] + generate_valid_split_records(
            split_index=0, num_issues=64, num_prs=64, issues_repo_offset=1000, prs_repo_offset=2000
        )

        # Split 2 (calibration): has IssuesEvent with repo 9999
        shared_issue = make_issue(event_id=2, repo_id=shared_repo_id, number=1,
                                  owner=f"owner_{shared_repo_id}", repo_name=f"repo_{shared_repo_id}")
        cal_records = [shared_issue] + generate_valid_split_records(
            split_index=1, num_issues=64, num_prs=64, issues_repo_offset=3000, prs_repo_offset=4000
        )

        source_dev = fixture(dev_records, split="development")
        source_cal = fixture(cal_records, split="calibration")

        result = a.adapt_sources([source_dev, source_cal])

        # Shared repository index covers ALL raw types
        self.assertIn(str(shared_repo_id), result.shared_repo_ids)

        # In split 1, PushEvent is excluded under raw_type_action
        dev_scan = result.scan_for("development")
        self.assertEqual(dev_scan.exclusions()["raw_type_action:[\"PushEvent\",\"<missing>\"]"], 1)

        # In split 2, shared_issue passed projection and oracle, but is excluded under cross_split_repository
        cal_scan = result.scan_for("calibration")
        self.assertEqual(cal_scan.exclusions()["cross_split_repository"], 1)
        self.assertTrue(all(e.repo_id != str(shared_repo_id) for e in cal_scan.eligible))

    def test_three_splits_full_synthetic_pipeline(self):
        """Full 3-split run (development, calibration, confirmatory) passes all quotas and accounting."""
        sources = [
            fixture(generate_valid_split_records(0, 64, 64, 1000, 2000), split="development"),
            fixture(generate_valid_split_records(1, 64, 64, 3000, 4000), split="calibration"),
            fixture(generate_valid_split_records(2, 64, 64, 5000, 6000), split="confirmatory"),
        ]
        result = a.adapt_sources(sources)

        self.assertEqual(len(result.scans), 3)
        self.assertEqual(result.shared_repo_ids, frozenset())

        for split in ("development", "calibration", "confirmatory"):
            scan = result.scan_for(split)
            # Accounting equations
            self.assertEqual(scan.raw_count, scan.unique_count + scan.collapsed_extras)
            self.assertEqual(scan.unique_count, sum(scan.exclusions().values()) + len(scan.eligible))
            self.assertEqual(len(scan.eligible), len(scan.selected) + len(scan.unselected))

            # Exactly 64 issues + 64 prs selected
            self.assertEqual(len(scan.selected), 128)
            issues_selected = [e for e in scan.selected if e.event_type == "IssuesEvent"]
            prs_selected = [e for e in scan.selected if e.event_type == "PullRequestEvent"]
            self.assertEqual(len(issues_selected), 64)
            self.assertEqual(len(prs_selected), 64)

            # Diversity quotas
            self.assertGreaterEqual(len({e.repo_id for e in scan.selected}), 24)
            self.assertGreaterEqual(len({e.repo_id for e in issues_selected}), 16)
            self.assertGreaterEqual(len({e.repo_id for e in prs_selected}), 16)

    def test_first_reason_accounting(self):
        """Verify each deterministic first-reason exclusion bucket and exact accounting."""
        records = []

        # 1. raw_type_action: non-status action
        records.append(make_issue(event_id=101, repo_id=501, action="labeled"))
        # 2. raw_type_action: unknown type
        records.append(make_push(event_id=102, repo_id=502))
        # 3. common_schema: actor not dict
        records.append(make_issue(event_id=103, repo_id=503, actor="not-a-dict"))
        # 4. event_specific_schema: missing issue.repository_url
        bad_issue = json.loads(make_issue(event_id=104, repo_id=504))
        del bad_issue["payload"]["issue"]["repository_url"]
        records.append(json.dumps(bad_issue).encode())
        # 5. identity: repository_url does not match repo.url
        bad_ident = json.loads(make_issue(event_id=105, repo_id=505))
        bad_ident["payload"]["issue"]["repository_url"] = "https://api.github.com/repos/other/repo"
        records.append(json.dumps(bad_ident).encode())
        # 6. state: opened but state closed
        records.append(make_issue(event_id=106, repo_id=506, action="opened", state="closed"))

        # Add valid quota bases so selection can succeed
        valid_bases = generate_valid_split_records(0, 64, 64, 1000, 2000)
        source = fixture(records + valid_bases, split="development")

        result = a.adapt_sources([source])
        scan = result.scan_for("development")
        ex = scan.exclusions()

        self.assertEqual(ex.get("raw_type_action:[\"IssuesEvent\",\"labeled\"]"), 1)
        self.assertEqual(ex.get("raw_type_action:[\"PushEvent\",\"<missing>\"]"), 1)
        self.assertEqual(ex.get("common_schema"), 1)
        self.assertEqual(ex.get("event_specific_schema"), 1)
        self.assertEqual(ex.get("identity"), 1)
        self.assertEqual(ex.get("state"), 1)

        # Accounting validation
        self.assertEqual(scan.raw_count, scan.unique_count + scan.collapsed_extras)
        self.assertEqual(scan.unique_count, sum(ex.values()) + len(scan.eligible))

    def test_oracle_rejection(self):
        """Oracle schema rejection and failure sets are accounted under deterministic oracle_* reasons."""
        iss_oracle_schema = make_issue(event_id=201, repo_id=601)
        iss_oracle_id = make_issue(event_id=202, repo_id=602)
        iss_oracle_state = make_issue(event_id=203, repo_id=603)

        valid_bases = generate_valid_split_records(0, 64, 64, 1000, 2000)
        source = fixture([iss_oracle_schema, iss_oracle_id, iss_oracle_state] + valid_bases, split="development")

        def mock_oracle(candidate):
            cid = str(candidate.get("id"))
            if cid == "201":
                return SimpleNamespace(schema_valid=False, truth=0, oracle_failure_set=())
            if cid == "202":
                return SimpleNamespace(schema_valid=True, truth=0, oracle_failure_set=("identity",))
            if cid == "203":
                return SimpleNamespace(schema_valid=True, truth=0, oracle_failure_set=("state",))
            return a.reference_oracle(candidate)

        result = a.adapt_sources([source], oracle_fn=mock_oracle)
        scan = result.scan_for("development")
        ex = scan.exclusions()

        self.assertEqual(ex.get("oracle_schema"), 1)
        self.assertEqual(ex.get("oracle_identity"), 1)
        self.assertEqual(ex.get("oracle_state"), 1)
        self.assertEqual(len(scan.eligible), 128)

    def test_selection_cap_four_per_repo(self):
        """Repository with 6 eligible events selects only 4, leaving 2 in unselected."""
        repo_extra = 999
        # Generate 6 issues for repo 999
        extras = [
            make_issue(event_id=500 + i, repo_id=repo_extra, number=i + 1,
                       owner=f"owner_{repo_extra}", repo_name=f"repo_{repo_extra}")
            for i in range(6)
        ]
        valid_bases = generate_valid_split_records(0, 64, 64, 1000, 2000)
        source = fixture(extras + valid_bases, split="development")

        result = a.adapt_sources([source])
        scan = result.scan_for("development")

        selected_from_extra = [e for e in scan.selected if e.repo_id == str(repo_extra)]
        unselected_from_extra = [e for e in scan.unselected if e.repo_id == str(repo_extra)]

        self.assertEqual(len(selected_from_extra), 4)
        self.assertEqual(len(unselected_from_extra), 2)

    def test_quota_failure_clean_error(self):
        """Clean failure when split cannot reach exact 64 base quota."""
        # 63 issues instead of 64
        records = generate_valid_split_records(0, 63, 64, 1000, 2000)
        source = fixture(records, split="development")
        with self.assertRaisesRegex(a.AdapterError, "cannot reach exact IssuesEvent base quota"):
            a.adapt_sources([source])

    def test_min_repos_overall_failure(self):
        """Clean failure when split has fewer than 24 selected repositories overall."""
        # 64 issues and 64 PRs explicitly constructed on the SAME 16 repo IDs (repo_id=1000+i%16)
        records = []
        for i in range(64):
            repo_id = 1000 + (i % 16)
            records.append(make_issue(event_id=i + 1, repo_id=repo_id, number=i + 1,
                                      owner=f"o_{repo_id}", repo_name=f"r_{repo_id}"))
        for i in range(64):
            repo_id = 1000 + (i % 16)
            records.append(make_pr(event_id=1000 + i, repo_id=repo_id, number=i + 1,
                                   owner=f"o_{repo_id}", repo_name=f"r_{repo_id}"))
        source = fixture(records, split="development")
        with self.assertRaisesRegex(a.AdapterError, "fewer than 24 selected repositories"):
            a.adapt_sources([source])

    def test_min_repos_per_type_failure(self):
        """15 repos times cap 4 yields 60 < 64; cannot reach exact IssuesEvent base quota.

        Because MAX_BASES_PER_REPOSITORY_EVENT_TYPE is 4, reaching the 64-base quota
        mathematically entails at least ceil(64 / 4) = 16 distinct repositories.
        With only 15 repositories, quota fails closed before the per-type repository check.
        Never change cap or quota.
        """
        records = []
        # 64 issues across 15 repos (at most 15 * 4 = 60 can be selected)
        for i in range(64):
            repo_id = 1000 + (i % 15)
            records.append(make_issue(event_id=i + 1, repo_id=repo_id, number=i + 1,
                                      owner=f"o_{repo_id}", repo_name=f"r_{repo_id}"))
        # 64 PRs across 20 repos
        for i in range(64):
            repo_id = 2000 + (i % 20)
            records.append(make_pr(event_id=100 + i, repo_id=repo_id, number=i + 1,
                                   owner=f"o_{repo_id}", repo_name=f"r_{repo_id}"))

        source = fixture(records, split="development")
        with self.assertRaisesRegex(a.AdapterError, "cannot reach exact IssuesEvent base quota"):
            a.adapt_sources([source])

    def test_malformed_oracle_rejected(self):
        """Malformed oracle missing failure_set and truth=0 on valid schema are rejected."""
        valid_bases = generate_valid_split_records(0, 64, 64, 1000, 2000)
        source = fixture(valid_bases, split="development")

        # Missing oracle_failure_set rejected
        def oracle_missing_failure_set(candidate):
            return SimpleNamespace(schema_valid=True, truth=1)

        with self.assertRaisesRegex(a.AdapterError, "missing oracle_failure_set"):
            a.adapt_sources([source], oracle_fn=oracle_missing_failure_set)

        # truth=0 with schema_valid=True and empty failure set rejected
        def oracle_truth_zero(candidate):
            return SimpleNamespace(schema_valid=True, truth=0, oracle_failure_set=())

        with self.assertRaisesRegex(a.AdapterError, "truth != 1"):
            a.adapt_sources([source], oracle_fn=oracle_truth_zero)

    def test_confirmatory_pushevent_repo_removes_eligible_development_record(self):
        """3 synthetic splits with excluded PushEvent repo in confirmatory removing an eligible dev record."""
        shared_repo_id = 9999
        # Confirmatory has PushEvent on shared_repo_id plus 64 issues and 64 PRs on disjoint repos
        conf_records = [make_push(event_id=500_000, repo_id=shared_repo_id)] + generate_valid_split_records(
            split_index=2, num_issues=64, num_prs=64, issues_repo_offset=5000, prs_repo_offset=6000
        )
        # Calibration has 64 issues and 64 PRs on disjoint repos
        cal_records = generate_valid_split_records(
            split_index=1, num_issues=64, num_prs=64, issues_repo_offset=3000, prs_repo_offset=4000
        )
        # Development has eligible issue on shared_repo_id PLUS surplus (64 issues and 64 PRs) so quotas pass
        dev_shared_issue = make_issue(
            event_id=99_999,
            repo_id=shared_repo_id,
            number=1,
            owner=f"o_{shared_repo_id}",
            repo_name=f"r_{shared_repo_id}",
        )
        dev_records = [dev_shared_issue] + generate_valid_split_records(
            split_index=0, num_issues=64, num_prs=64, issues_repo_offset=1000, prs_repo_offset=2000
        )

        sources = [
            fixture(dev_records, split="development"),
            fixture(cal_records, split="calibration"),
            fixture(conf_records, split="confirmatory"),
        ]
        result = a.adapt_sources(sources)

        # Cross-split index detects repo 9999 shared between confirmatory and development
        self.assertIn(str(shared_repo_id), result.shared_repo_ids)

        # Confirmatory excludes PushEvent under raw_type_action
        conf_scan = result.scan_for("confirmatory")
        self.assertEqual(conf_scan.exclusions()["raw_type_action:[\"PushEvent\",\"<missing>\"]"], 1)
        self.assertEqual(len(conf_scan.selected), 128)

        # Development excludes the otherwise-eligible issue under cross_split_repository
        dev_scan = result.scan_for("development")
        self.assertEqual(dev_scan.exclusions()["cross_split_repository"], 1)
        self.assertTrue(all(e.repo_id != str(shared_repo_id) for e in dev_scan.eligible))

        # With surplus valid records, quotas in all 3 splits still pass
        for split in ("development", "calibration", "confirmatory"):
            scan = result.scan_for(split)
            self.assertEqual(len(scan.selected), 128)
            self.assertEqual(scan.raw_count, scan.unique_count + scan.collapsed_extras)
            self.assertEqual(scan.unique_count, sum(scan.exclusions().values()) + len(scan.eligible))

    def test_deterministic_selection_across_reversed_raw_order(self):
        """Deterministic full selection across reversed raw order comparing selected event IDs."""
        dev_records = generate_valid_split_records(0, 70, 70, 1000, 2000)
        cal_records = generate_valid_split_records(1, 70, 70, 3000, 4000)
        conf_records = generate_valid_split_records(2, 70, 70, 5000, 6000)

        fwd_sources = [
            fixture(dev_records, split="development"),
            fixture(cal_records, split="calibration"),
            fixture(conf_records, split="confirmatory"),
        ]
        rev_sources = [
            fixture(list(reversed(dev_records)), split="development"),
            fixture(list(reversed(cal_records)), split="calibration"),
            fixture(list(reversed(conf_records)), split="confirmatory"),
        ]

        res_fwd = a.adapt_sources(fwd_sources)
        res_rev = a.adapt_sources(rev_sources)

        for split in ("development", "calibration", "confirmatory"):
            fwd_selected_ids = [e.event_id for e in res_fwd.selected(split)]
            rev_selected_ids = [e.event_id for e in res_rev.selected(split)]
            self.assertEqual(fwd_selected_ids, rev_selected_ids)
            self.assertEqual(len(fwd_selected_ids), 128)

            # Coordinates (source lines) differ due to reversed input order
            fwd_lines = [e.source_line for e in res_fwd.selected(split)]
            rev_lines = [e.source_line for e in res_rev.selected(split)]
            self.assertNotEqual(fwd_lines, rev_lines)

    def test_pinned_helper_hash_mismatch_rejected(self):
        """Pinned helper hash mismatch rejected using existing helper path with deliberately wrong expected digest."""
        wrong_digest = "0" * 64
        with self.assertRaisesRegex(a.AdapterError, "SHA-256 mismatch"):
            a._load_pinned_v1_module("test_helper_mismatch", a.V1_E003_PATH, wrong_digest)

    def test_numeric_deterministic_selection_order(self):
        """Selection sorts repositories by numeric value, not lexicographic string order."""
        # Repos 100, 20, 3: string sort is '100', '20', '3'; numeric sort is 3, 20, 100
        eligible = [
            a.SourceEvent(
                split="development", source_file="dev.json.gz", source_sha256="a" * 64,
                source_line=1, repo_id="100", event_id="1", event_type="IssuesEvent",
                action="opened", payload={}, input_sha256="h1",
            ),
            a.SourceEvent(
                split="development", source_file="dev.json.gz", source_sha256="a" * 64,
                source_line=2, repo_id="20", event_id="2", event_type="IssuesEvent",
                action="opened", payload={}, input_sha256="h2",
            ),
            a.SourceEvent(
                split="development", source_file="dev.json.gz", source_sha256="a" * 64,
                source_line=3, repo_id="3", event_id="3", event_type="IssuesEvent",
                action="opened", payload={}, input_sha256="h3",
            ),
        ]
        sorted_events = sorted(eligible, key=a.selection_sort_key)
        self.assertEqual([e.repo_id for e in sorted_events], ["3", "20", "100"])

    def test_no_partial_return_on_late_failure(self):
        """Failure in a later split (quota or pin) raises without partial return."""
        dev_source = fixture(generate_valid_split_records(0, 64, 64, 1000, 2000), split="development")
        # Calibration has quota failure (only 10 issues)
        cal_source = fixture(generate_valid_split_records(1, 10, 64, 3000, 4000), split="calibration")

        with self.assertRaises(a.AdapterError):
            a.adapt_sources([dev_source, cal_source])

    def test_pinned_adapter_rejects_synthetic(self):
        """adapt_pinned enforces pinned production inventory, rejecting synthetic source inputs."""
        dev_source = fixture(generate_valid_split_records(0, 64, 64, 1000, 2000), split="development")
        with self.assertRaises(s.SourceError):
            a.adapt_pinned([dev_source])

    def test_immutability(self):
        """Shallow frozen attributes; mutable nested dicts aren't immutable."""
        source = fixture(generate_valid_split_records(0, 64, 64, 1000, 2000), split="development")
        result = a.adapt_sources([source])
        scan = result.scan_for("development")
        ev = scan.selected[0]

        with self.assertRaises(FrozenInstanceError):
            ev.split = "calibration"

        with self.assertRaises(FrozenInstanceError):
            scan.raw_count = 999

        with self.assertRaises(FrozenInstanceError):
            result.scans = ()


if __name__ == "__main__":
    unittest.main()
