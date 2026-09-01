"""Independent, fail-closed reference oracle for the locked E003 contract.

This module intentionally does not import the E003 method implementation.  Its
field paths, URL parsing, and action/state rules are transcribed separately so
that the oracle can serve as an evaluator boundary rather than a second call
through a validator helper.
"""

from __future__ import annotations

import datetime as _datetime
import json
import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping
from urllib.parse import urlsplit


ORACLE_FAMILY_ORDER = ("schema", "identity", "state")
_EVENT_KINDS = frozenset(("IssuesEvent", "PullRequestEvent"))
_STATUS_ACTIONS = frozenset(("opened", "closed", "reopened"))
_RESOURCE_STATES = frozenset(("open", "closed"))
_TOP_LEVEL_FIELDS = frozenset(
    ("id", "type", "actor", "repo", "payload", "public", "created_at")
)
_ACTOR_FIELDS = frozenset(("id", "login"))
_REPOSITORY_FIELDS = frozenset(("id", "name", "url"))
_ISSUE_FIELDS = frozenset(("id", "number", "state", "url", "repository_url"))
_PULL_REQUEST_FIELDS = frozenset(("id", "number", "state", "merged", "url"))
_ISSUE_ACTION_STATE = MappingProxyType(
    {"opened": ("open",), "reopened": ("open",), "closed": ("closed",)}
)
_PULL_REQUEST_ACTION_STATE = MappingProxyType(
    {
        "opened": (("open", False),),
        "reopened": (("open", False),),
        "closed": (("closed", True), ("closed", False)),
    }
)
_REPOSITORY_HOST = "api.github.com"
_REPOSITORY_PREFIX = ("", "repos")
_ISSUE_RESOURCE = "issues"
_PULL_REQUEST_RESOURCE = "pulls"


@dataclass(frozen=True)
class OracleResult:
    """The only information returned by the independent reference oracle."""

    schema_valid: bool
    truth: int
    oracle_failure_set: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_valid": self.schema_valid,
            "truth": self.truth,
            "oracle_failure_set": list(self.oracle_failure_set),
        }


def _strict_decimal_id(value: Any) -> str | None:
    if type(value) is int:
        return str(value) if value >= 0 else None
    if type(value) is str and re.fullmatch(r"(?:0|[1-9][0-9]*)", value):
        return value
    return None


def _positive_integer(value: Any) -> bool:
    return type(value) is int and value > 0


def _utc_timestamp(value: Any) -> bool:
    if type(value) is not str:
        return False
    if re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?Z",
        value,
    ) is None:
        return False
    try:
        _datetime.datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError:
        return False
    return True


def _repo_components(url: Any) -> tuple[str, str] | None:
    if type(url) is not str:
        return None
    try:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.netloc != _REPOSITORY_HOST:
            return None
        if parsed.query or parsed.fragment or parsed.username or parsed.password:
            return None
        if parsed.port is not None:
            return None
    except ValueError:
        return None
    parts = parsed.path.split("/")
    if len(parts) != 4 or tuple(parts[:2]) != _REPOSITORY_PREFIX:
        return None
    if not parts[2] or not parts[3] or any("/" in part for part in parts[2:]):
        return None
    return parts[2], parts[3]


def _resource_components(url: Any, resource: str) -> tuple[str, str, int] | None:
    if type(url) is not str:
        return None
    try:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.netloc != _REPOSITORY_HOST:
            return None
        if parsed.query or parsed.fragment or parsed.username or parsed.password:
            return None
        if parsed.port is not None:
            return None
    except ValueError:
        return None
    parts = parsed.path.split("/")
    if len(parts) != 6 or tuple(parts[:2]) != _REPOSITORY_PREFIX:
        return None
    if parts[4] != resource or not parts[2] or not parts[3]:
        return None
    if re.fullmatch(r"[1-9][0-9]*", parts[5]) is None:
        return None
    return parts[2], parts[3], int(parts[5])


def _has_fields(value: Any, fields: frozenset[str]) -> bool:
    return type(value) is dict and fields.issubset(value)


def _common_schema(candidate: Any) -> bool:
    if type(candidate) is not dict or not _TOP_LEVEL_FIELDS.issubset(candidate):
        return False
    if _strict_decimal_id(candidate.get("id")) is None:
        return False
    if candidate.get("type") not in _EVENT_KINDS:
        return False
    actor = candidate.get("actor")
    if not _has_fields(actor, _ACTOR_FIELDS):
        return False
    if _strict_decimal_id(actor.get("id")) is None or type(actor.get("login")) is not str:
        return False
    repository = candidate.get("repo")
    if not _has_fields(repository, _REPOSITORY_FIELDS):
        return False
    if (
        _strict_decimal_id(repository.get("id")) is None
        or type(repository.get("name")) is not str
        or not repository.get("name")
        or _repo_components(repository.get("url")) is None
    ):
        return False
    if type(candidate.get("public")) is not bool:
        return False
    if not _utc_timestamp(candidate.get("created_at")):
        return False
    return type(candidate.get("payload")) is dict


def _event_schema(candidate: Mapping[str, Any]) -> bool:
    event_type = candidate.get("type")
    payload = candidate.get("payload")
    if type(payload) is not dict or type(payload.get("action")) is not str:
        return False
    if payload.get("action") not in _STATUS_ACTIONS:
        return False
    if event_type == "IssuesEvent":
        issue = payload.get("issue")
        if not _has_fields(issue, _ISSUE_FIELDS):
            return False
        return (
            _strict_decimal_id(issue.get("id")) is not None
            and _positive_integer(issue.get("number"))
            and issue.get("state") in _RESOURCE_STATES
            and _resource_components(issue.get("url"), _ISSUE_RESOURCE) is not None
            and _repo_components(issue.get("repository_url")) is not None
        )
    if event_type == "PullRequestEvent":
        pull_request = payload.get("pull_request")
        if not _has_fields(pull_request, _PULL_REQUEST_FIELDS):
            return False
        return (
            _positive_integer(payload.get("number"))
            and _strict_decimal_id(pull_request.get("id")) is not None
            and _positive_integer(pull_request.get("number"))
            and pull_request.get("state") in _RESOURCE_STATES
            and type(pull_request.get("merged")) is bool
            and _resource_components(pull_request.get("url"), _PULL_REQUEST_RESOURCE)
            is not None
        )
    return False


def _identity_relation(candidate: Mapping[str, Any]) -> bool:
    repository = candidate["repo"]
    top_components = _repo_components(repository["url"])
    if top_components is None:
        return False
    payload = candidate["payload"]
    if candidate["type"] == "IssuesEvent":
        issue = payload["issue"]
        nested_repository = _repo_components(issue["repository_url"])
        issue_url = _resource_components(issue["url"], _ISSUE_RESOURCE)
        return (
            nested_repository == top_components
            and issue_url is not None
            and issue_url[:2] == top_components
            and issue_url[2] == issue["number"]
        )
    pull_request = payload["pull_request"]
    pull_url = _resource_components(pull_request["url"], _PULL_REQUEST_RESOURCE)
    return (
        pull_url is not None
        and pull_url[:2] == top_components
        and pull_url[2] == pull_request["number"] == payload["number"]
    )


def _state_relation(candidate: Mapping[str, Any]) -> bool:
    action = candidate["payload"]["action"]
    if candidate["type"] == "IssuesEvent":
        allowed = _ISSUE_ACTION_STATE.get(action)
        return allowed is not None and candidate["payload"]["issue"]["state"] in allowed
    pull_request = candidate["payload"]["pull_request"]
    allowed_pairs = _PULL_REQUEST_ACTION_STATE.get(action)
    return allowed_pairs is not None and (
        pull_request["state"], pull_request["merged"]
    ) in allowed_pairs


def evaluate(candidate: Any) -> OracleResult:
    """Evaluate only a candidate payload and fail closed on every bad shape."""

    if not _common_schema(candidate) or not _event_schema(candidate):
        return OracleResult(False, 0, ("schema",))
    failures: list[str] = []
    if not _identity_relation(candidate):
        failures.append("identity")
    if not _state_relation(candidate):
        failures.append("state")
    return OracleResult(True, int(not failures), tuple(failures))


def reference_oracle(candidate: Any) -> OracleResult:
    return evaluate(candidate)
