#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Validate a recorded name-clearance evidence ledger offline."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, quote_plus, urlsplit


REQUIRED_SOURCES = {
    "github",
    "pypi",
    "npm",
    "crates_io",
    "com_rdap",
    "web_common_law",
    "uspto",
}
ALLOWED_MODES = {"automated", "human_review"}
ALLOWED_STATUSES = {"clear", "finding", "unavailable"}
SOURCE_MODES = {
    "github": "automated",
    "pypi": "automated",
    "npm": "automated",
    "crates_io": "automated",
    "com_rdap": "automated",
    "web_common_law": "human_review",
    "uspto": "human_review",
}
REQUEST_KINDS = {
    "github": {"repository_search", "organization_search"},
    "pypi": {"exact_lookup"},
    "npm": {"exact_lookup", "search"},
    "crates_io": {"exact_lookup", "search"},
    "com_rdap": {"domain_lookup"},
}


def allowed_string(value: object, allowed: set[str]) -> bool:
    return isinstance(value, str) and value in allowed


def parse_utc_timestamp(value: object) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise ValueError("UTC timezone is required")
    return parsed


def valid_http_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def begins_with_candidate(query: str, display_name: str, slug: str) -> bool:
    folded = query.casefold().strip()
    for prefix in (display_name.casefold(), slug.casefold()):
        if folded.startswith(prefix) and (
            len(folded) == len(prefix)
            or not folded[len(prefix)].isalnum()
        ):
            return True
    return False


def contains_bounded_candidate_term(query: str, terms: list[str]) -> bool:
    for term in terms:
        chunks = re.findall(r"[a-z0-9]+", term.casefold())
        if not chunks:
            continue
        pattern = (
            r"(?<![a-z0-9])"
            + r"[^a-z0-9]*".join(re.escape(chunk) for chunk in chunks)
            + r"(?![a-z0-9])"
        )
        if re.search(pattern, query.casefold()):
            return True
    return False


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def normalize_identity(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def expected_request_url(source_id: str, request_kind: str, query: str) -> str | None:
    query_slug = slugify(query)
    if source_id == "github" and request_kind == "repository_search":
        return (
            "https://api.github.com/search/repositories?q="
            f"{quote(query + ' in:name')}&per_page=100"
        )
    if source_id == "github" and request_kind == "organization_search":
        return (
            "https://api.github.com/search/users?q="
            f"{quote(query + ' in:login type:org')}&per_page=100"
        )
    if source_id == "pypi" and request_kind == "exact_lookup":
        return f"https://pypi.org/pypi/{quote(query_slug)}/json"
    if source_id == "npm" and request_kind == "exact_lookup":
        return f"https://registry.npmjs.org/{quote(query_slug)}"
    if source_id == "npm" and request_kind == "search":
        return (
            "https://registry.npmjs.org/-/v1/search?size=100&text="
            + quote(query)
        )
    if source_id == "crates_io" and request_kind == "exact_lookup":
        return f"https://crates.io/api/v1/crates/{quote(query_slug)}"
    if source_id == "crates_io" and request_kind == "search":
        return (
            "https://crates.io/api/v1/crates?q="
            f"{quote(query)}&per_page=100"
        )
    if source_id == "com_rdap" and request_kind == "domain_lookup":
        return (
            "https://rdap.verisign.com/com/v1/domain/"
            f"{quote(query_slug)}.com"
        )
    return None


def expected_human_source_url(
    source_id: str, display_name: str, slug: str
) -> str | None:
    if source_id == "web_common_law":
        query = quote_plus(
            f'"{display_name}" OR "{slug}" software AI agent'
        )
        return f"https://www.google.com/search?q={query}"
    if source_id == "uspto":
        return "https://tmsearch.uspto.gov/search/search-results"
    return None


def canonical_digest(value: object) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def check_ledger(path: Path) -> list[str]:
    failures: list[str] = []
    future_limit = datetime.now(timezone.utc) + timedelta(minutes=5)
    try:
        ledger = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"[ledger] cannot read canonical JSON: {exc}"]

    if not isinstance(ledger, dict):
        return ["[ledger] top level must be an object"]
    if type(ledger.get("schema")) is not int or ledger.get("schema") != 1:
        failures.append("[ledger] schema must be 1")
    candidate = ledger.get("candidate")
    candidate_valid = (
        isinstance(candidate, dict)
        and isinstance(candidate.get("display_name"), str)
        and candidate["display_name"].strip()
        and isinstance(candidate.get("slug"), str)
        and candidate["slug"].strip()
        and candidate["slug"] == slugify(candidate["display_name"])
        and isinstance(candidate.get("variants"), list)
        and candidate["variants"]
        and all(isinstance(item, str) and item.strip()
                for item in candidate["variants"])
    )
    candidate_identities: set[str] = set()
    if not candidate_valid:
        failures.append("[candidate] candidate identity is incomplete")
    else:
        primary_identity = normalize_identity(candidate["display_name"])
        candidate_identities.add(primary_identity)
        canonical_variant_present = False
        for variant in candidate["variants"]:
            variant_identity = normalize_identity(variant)
            if variant_identity == primary_identity:
                canonical_variant_present = True
            if not (
                variant_identity == primary_identity
                or (
                    len(variant_identity) >= 5
                    and primary_identity.startswith(variant_identity)
                )
            ):
                failures.append(
                    f"[candidate] variant {variant!r} is not derived from "
                    f"{candidate['display_name']!r}"
                )
                continue
            candidate_identities.add(variant_identity)
        if not canonical_variant_present:
            failures.append(
                "[candidate] variants must include the canonical identity"
            )

    limitations = ledger.get("limitations")
    limitations_valid = (
        isinstance(limitations, list)
        and bool(limitations)
        and all(isinstance(item, str) and item.strip() for item in limitations)
    )
    limitation_text = " ".join(limitations).casefold() if limitations_valid else ""
    clearance_disclaimed = any(
        phrase in limitation_text
        for phrase in (
            "not legal clearance",
            "does not prove legal clearance",
            "cannot establish legal clearance",
        )
    )
    if not limitations_valid or not clearance_disclaimed:
        failures.append("[ledger] limitations must disclaim legal clearance")

    collected_raw = ledger.get("collected_at")
    collected_at: datetime | None = None
    try:
        collected_at = parse_utc_timestamp(collected_raw)
        if collected_at > future_limit:
            failures.append("[freshness] collected_at cannot be in the future")
    except (TypeError, ValueError):
        failures.append("[freshness] collected_at must be an ISO-8601 UTC timestamp")

    expires_raw = ledger.get("expires_at")
    expires_at: datetime | None = None
    try:
        expires_at = parse_utc_timestamp(expires_raw)
        if expires_at <= datetime.now(timezone.utc):
            failures.append(f"[freshness] evidence expired at {expires_raw}")
    except (TypeError, ValueError):
        failures.append("[freshness] expires_at must be an ISO-8601 UTC timestamp")
    if (
        collected_at is not None
        and expires_at is not None
        and expires_at > collected_at + timedelta(days=7)
    ):
        failures.append(
            "[freshness] expires_at must be no later than seven days after collected_at"
        )

    decided_at: datetime | None = None
    disposition = ledger.get("disposition", {})
    disposition_decision = (
        disposition.get("decision") if isinstance(disposition, dict) else None
    )
    if not allowed_string(disposition_decision, {
        "accept", "reject"
    }):
        failures.append("[disposition] Owner decision must be accept or reject")
    elif not all(
        isinstance(disposition.get(key), str) and disposition.get(key).strip()
        for key in ("decided_by", "decided_at", "rationale")
    ):
        failures.append(
            "[disposition] decision requires decided_by, decided_at, and rationale"
        )
    else:
        try:
            decided_at = parse_utc_timestamp(disposition["decided_at"])
            if collected_at is not None and decided_at < collected_at:
                failures.append(
                    "[disposition] decided_at cannot predate collected_at"
                )
            if decided_at > future_limit:
                failures.append(
                    "[disposition] decided_at cannot be in the future"
                )
        except (TypeError, ValueError):
            failures.append(
                "[disposition] decided_at must be an ISO-8601 UTC timestamp"
            )

    sources = ledger.get("sources", [])
    valid_sources: list[dict] = []
    present: set[str] = set()
    if not isinstance(sources, list):
        failures.append("[source] sources must be a list")
    else:
        source_ids: list[str] = []
        for source_index, source in enumerate(sources, start=1):
            if not isinstance(source, dict):
                failures.append(
                    f"[source] source entry {source_index} must be an object"
                )
                continue
            source_id = source.get("id")
            if not isinstance(source_id, str):
                failures.append(
                    f"[source] source entry {source_index} has an invalid id"
                )
                continue
            valid_sources.append(source)
            source_ids.append(source_id)
            if source_id in REQUIRED_SOURCES:
                present.add(source_id)
        for source_id in sorted(set(source_ids)):
            if source_ids.count(source_id) > 1:
                failures.append(f"[source] duplicate source id {source_id!r}")
            if source_id not in REQUIRED_SOURCES:
                failures.append(f"[source] unexpected source id {source_id!r}")
    for source_id in sorted(REQUIRED_SOURCES - present):
        failures.append(f"[source] required source '{source_id}' is missing")
    latest_source_at = collected_at
    if isinstance(sources, list):
        for source in valid_sources:
            source_id = source.get("id", "<unknown>")
            mode = source.get("mode")
            status = source.get("status")
            if not allowed_string(mode, ALLOWED_MODES):
                failures.append(
                    f"[source] {source_id} mode must be automated or human_review"
                )
            elif source_id in SOURCE_MODES and mode != SOURCE_MODES[source_id]:
                failures.append(
                    f"[source] {source_id} mode must be {SOURCE_MODES[source_id]}"
                )
            if not allowed_string(status, ALLOWED_STATUSES):
                failures.append(
                    f"[source] {source_id} status must be clear, finding, or unavailable"
                )
            url = source.get("url")
            if not valid_http_url(url):
                failures.append(f"[source] {source_id} requires a source URL")
            elif mode == "human_review" and candidate_valid:
                expected_url = expected_human_source_url(
                    source_id,
                    candidate["display_name"],
                    candidate["slug"],
                )
                if expected_url is not None and url != expected_url:
                    failures.append(
                        f"[source] {source_id} URL does not match its "
                        "canonical endpoint"
                    )
            checked_raw = source.get("checked_at")
            checked_at: datetime | None = None
            try:
                checked_at = parse_utc_timestamp(checked_raw)
            except (TypeError, ValueError):
                failures.append(
                    f"[source] {source_id} requires checked_at as an "
                    "ISO-8601 UTC timestamp"
                )
            if (
                checked_at is not None
                and collected_at is not None
                and expires_at is not None
                and not (collected_at <= checked_at <= expires_at)
            ):
                failures.append(
                    f"[freshness] {source_id} checked_at falls outside the ledger window"
                )
            if checked_at is not None and checked_at > future_limit:
                failures.append(
                    f"[freshness] {source_id} checked_at cannot be in the future"
                )
            if (
                checked_at is not None
                and (latest_source_at is None or checked_at > latest_source_at)
            ):
                latest_source_at = checked_at
            if source_id in REQUIRED_SOURCES and source.get("status") == "unavailable":
                failures.append(
                    f"[source] {source_id} is unavailable; "
                    "no clearance can be inferred"
                )
            if (
                source.get("mode") == "human_review"
                and not (
                    isinstance(source.get("reviewed_by"), str)
                    and source["reviewed_by"].strip()
                )
            ):
                failures.append(
                    f"[review] {source_id} human review requires reviewed_by"
                )
            if (
                source.get("mode") == "human_review"
                and source.get("reviewer_kind") != "human"
            ):
                failures.append(
                    f"[review] {source_id} requires reviewer_kind human"
                )
            queries = source.get("queries", {})
            query_lists_present = (
                isinstance(queries, dict)
                and isinstance(queries.get("exact"), list)
                and bool(queries["exact"])
                and isinstance(queries.get("similar"), list)
                and bool(queries["similar"])
            )
            queries_valid = query_lists_present and all(
                isinstance(item, str) and item.strip()
                for query_kind in ("exact", "similar")
                for item in queries[query_kind]
            )
            if not query_lists_present:
                failures.append(
                    f"[query] {source_id} requires non-empty exact and "
                    "similar queries"
                )
            elif not queries_valid:
                failures.append(
                    f"[query] {source_id} exact and similar queries must be "
                    "non-empty strings"
                )
            if queries_valid and candidate_valid:
                primary_identity = normalize_identity(
                    candidate["display_name"]
                )
                slug_identity = normalize_identity(candidate["slug"])
                canonical_exact = any(
                    normalize_identity(query) in {
                        primary_identity, slug_identity
                    }
                    or (
                        mode == "human_review"
                        and f'"{candidate["display_name"].casefold()}"'
                        in query.casefold()
                    )
                    for query in queries["exact"]
                )
                if not canonical_exact:
                    failures.append(
                        f"[query] {source_id} exact plan lacks canonical "
                        "candidate identity"
                    )
                exact_folded = {
                    query.casefold().strip() for query in queries["exact"]
                }
                similar_folded = {
                    query.casefold().strip() for query in queries["similar"]
                }
                if exact_folded & similar_folded:
                    failures.append(
                        f"[query] {source_id} exact and similar plans must "
                        "be distinct"
                    )
                if source_id != "uspto":
                    variation_queries = (
                        queries["similar"]
                        if mode == "automated"
                        else queries["exact"] + queries["similar"]
                    )
                    query_text = " ".join(variation_queries).casefold()
                    missing_variations = [
                        token for token in ("ai", "software", "agent")
                        if re.search(
                            rf"(?<![a-z0-9]){token}(?![a-z0-9])",
                            query_text,
                        ) is None
                    ]
                    if missing_variations:
                        failures.append(
                            f"[query] {source_id} query plan must cover AI, "
                            "software, and agent variations"
                        )
                elif not any(
                    normalize_identity(query) == primary_identity
                    and query.casefold().strip() not in exact_folded
                    for query in queries["similar"]
                ):
                    failures.append(
                        "[query] uspto similar plan requires an alternative "
                        "spelling"
                    )
                if source_id == "web_common_law" and not any(
                    normalize_identity(query) == primary_identity
                    or any(
                        identity != primary_identity
                        and identity in normalize_identity(query)
                        for identity in candidate_identities
                    )
                    for query in queries["similar"]
                ):
                    failures.append(
                        "[query] web_common_law similar plan requires a "
                        "name variation"
                    )
            if queries_valid and candidate_valid:
                candidate_name = candidate.get("display_name", "")
                query_identities = (
                    {primary_identity}
                    if mode == "automated"
                    else candidate_identities
                )
                for query_kind in ("exact", "similar"):
                    for query in queries[query_kind]:
                        query_identity = normalize_identity(query)
                        identifies_candidate = (
                            begins_with_candidate(
                                query,
                                candidate["display_name"],
                                candidate["slug"],
                            )
                            if mode == "automated"
                            else (
                                query_identity == primary_identity
                                or contains_bounded_candidate_term(
                                    query,
                                    [
                                        candidate["display_name"],
                                        candidate["slug"],
                                        *candidate["variants"],
                                    ],
                                )
                            )
                        )
                        if not identifies_candidate:
                            failures.append(
                                f"[query] {source_id} {query_kind} query {query!r} "
                                f"does not identify candidate {candidate_name!r}"
                            )
            digest = source.get("response_sha256")
            if not isinstance(digest, str) or re.fullmatch(
                r"[0-9a-f]{64}", digest
            ) is None:
                failures.append(
                    f"[evidence] {source_id} response_sha256 must be "
                    "64 lowercase hex digits"
                )
            elif source.get("mode") == "automated":
                requests = source.get("requests")
                if not isinstance(requests, list) or not requests:
                    failures.append(
                        f"[evidence] {source_id} automated source requires requests"
                    )
                elif canonical_digest(requests) != digest:
                    failures.append(
                        f"[evidence] {source_id} response_sha256 does not "
                        "match requests"
                    )
                if (
                    isinstance(requests, list)
                    and requests
                    and isinstance(requests[0], dict)
                    and source.get("url") != requests[0].get("url")
                ):
                    failures.append(
                        f"[source] {source_id} URL does not match its first request"
                    )
                if isinstance(requests, list) and queries_valid:
                    coverage: set[tuple[str, str]] = set()
                    for request_index, request in enumerate(requests, start=1):
                        if not isinstance(request, dict):
                            failures.append(
                                f"[evidence] {source_id} request {request_index} "
                                "must be an object"
                            )
                            continue
                        request_url = request.get("url")
                        if (
                            not valid_http_url(request_url)
                        ):
                            failures.append(
                                f"[evidence] {source_id} request {request_index} "
                                "requires a URL"
                            )
                        body_digest = request.get("body_sha256")
                        if (
                            not isinstance(body_digest, str)
                            or re.fullmatch(r"[0-9a-f]{64}", body_digest) is None
                        ):
                            failures.append(
                                f"[evidence] {source_id} request {request_index} "
                                "body_sha256 must be 64 lowercase hex digits"
                            )
                        query_kind = request.get("query_kind")
                        query = request.get("query")
                        if (
                            not allowed_string(
                                query_kind, {"exact", "similar"}
                            )
                            or not isinstance(query, str)
                            or query not in queries[query_kind]
                        ):
                            failures.append(
                                f"[query] {source_id} request {request_index} "
                                "is not bound to a declared query"
                            )
                            continue
                        coverage.add((query_kind, query))
                        request_kind = request.get("request_kind")
                        if not allowed_string(
                            request_kind,
                            REQUEST_KINDS.get(source_id, set()),
                        ):
                            failures.append(
                                f"[evidence] {source_id} request {request_index} "
                                "has an invalid request_kind"
                            )
                        elif isinstance(query, str):
                            expected_url = expected_request_url(
                                source_id, request_kind, query
                            )
                            if request_url != expected_url:
                                failures.append(
                                    f"[query] {source_id} request {request_index} "
                                    "URL does not match its declared query"
                                )
                        request_status = request.get("http_status")
                        allowed_statuses = (
                            {200, 404}
                            if request_kind == "exact_lookup"
                            or request_kind == "domain_lookup"
                            else {200}
                        )
                        if not (
                            isinstance(request_status, int)
                            and not isinstance(request_status, bool)
                            and request_status in allowed_statuses
                        ):
                            failures.append(
                                f"[evidence] {source_id} request {request_index} "
                                "has an unsuccessful HTTP status"
                            )
                    for query_kind in ("exact", "similar"):
                        for query in queries[query_kind]:
                            if (
                                isinstance(query, str)
                                and query.strip()
                                and (query_kind, query) not in coverage
                            ):
                                failures.append(
                                    f"[query] {source_id} has no evidence bound to "
                                    f"{query_kind} query {query!r}"
                                )
                    if source_id in REQUEST_KINDS:
                        for query_kind in ("exact", "similar"):
                            for query in queries[query_kind]:
                                for request_kind in sorted(
                                    REQUEST_KINDS[source_id]
                                ):
                                    if not any(
                                        isinstance(request, dict)
                                        and request.get("query_kind") == query_kind
                                        and request.get("query") == query
                                        and request.get("request_kind") == request_kind
                                        for request in requests
                                    ):
                                        failures.append(
                                            f"[query] {source_id} query {query!r} lacks "
                                            f"{request_kind} evidence"
                                        )
            elif source.get("mode") == "human_review":
                evidence = source.get("evidence")
                if not isinstance(evidence, dict) or not evidence:
                    failures.append(
                        f"[evidence] {source_id} human review requires evidence"
                    )
                elif canonical_digest(evidence) != digest:
                    failures.append(
                        f"[evidence] {source_id} response_sha256 does not "
                        "match evidence"
                    )
                reviewed_at: datetime | None = None
                if isinstance(evidence, dict):
                    result_count = evidence.get("result_count")
                    if not (
                        isinstance(result_count, int)
                        and not isinstance(result_count, bool)
                        and result_count >= 0
                    ):
                        failures.append(
                            f"[evidence] {source_id} human evidence requires "
                            "a nonnegative result_count"
                        )
                    elif status == "clear" and result_count != 0:
                        failures.append(
                            f"[source] {source_id} status clear contradicts "
                            "human result_count"
                        )
                    elif status == "finding" and result_count == 0:
                        failures.append(
                            f"[source] {source_id} status finding contradicts "
                            "human result_count"
                        )
                    if not (
                        isinstance(evidence.get("notes"), str)
                        and evidence["notes"].strip()
                    ):
                        failures.append(
                            f"[evidence] {source_id} human evidence requires notes"
                        )
                    try:
                        reviewed_at = parse_utc_timestamp(
                            evidence.get("reviewed_at")
                        )
                    except (TypeError, ValueError):
                        failures.append(
                            f"[review] {source_id} evidence requires reviewed_at "
                            "as an ISO-8601 UTC timestamp"
                        )
                    if (
                        reviewed_at is not None
                        and collected_at is not None
                        and expires_at is not None
                        and not (collected_at <= reviewed_at <= expires_at)
                    ):
                        failures.append(
                            f"[freshness] {source_id} reviewed_at falls outside "
                            "the ledger window"
                        )
                    if reviewed_at is not None and reviewed_at > future_limit:
                        failures.append(
                            f"[freshness] {source_id} reviewed_at cannot be "
                            "in the future"
                        )
                    if (
                        reviewed_at is not None
                        and (
                            latest_source_at is None
                            or reviewed_at > latest_source_at
                        )
                    ):
                        latest_source_at = reviewed_at
                if isinstance(evidence, dict) and queries_valid:
                    reviewed_queries = evidence.get("queries")
                    if not isinstance(reviewed_queries, list):
                        failures.append(
                            f"[query] {source_id} human evidence requires queries"
                        )
                    else:
                        for query_kind in ("exact", "similar"):
                            for query in queries[query_kind]:
                                if query not in reviewed_queries:
                                    failures.append(
                                        f"[query] {source_id} has no evidence bound to "
                                        f"{query_kind} query {query!r}"
                                    )
            findings = source.get("findings")
            if "findings" not in source:
                failures.append(
                    f"[finding] {source_id} requires an explicit findings list"
                )
            if not isinstance(findings, list):
                failures.append(f"[finding] {source_id} findings must be a list")
            elif status == "clear" and findings:
                failures.append(
                    f"[source] {source_id} status clear contradicts retained findings"
                )
            elif status == "finding" and not findings:
                failures.append(
                    f"[source] {source_id} status finding requires a retained finding"
                )
            if isinstance(findings, list):
                for index, finding in enumerate(findings, start=1):
                    if not isinstance(finding, dict):
                        failures.append(
                            f"[finding] {source_id} finding {index} must be "
                            "an object"
                        )
                        continue
                    if not allowed_string(finding.get("category_overlap"), {
                        "same", "adjacent", "unrelated", "unreviewed"
                    }):
                        failures.append(
                            f"[finding] {source_id} finding {index} "
                            "lacks category_overlap"
                        )
                        continue
                    if not allowed_string(
                        finding.get("relationship"), {"exact", "similar"}
                    ):
                        failures.append(
                            f"[finding] {source_id} finding {index} has "
                            "invalid relationship"
                        )
                        continue
                    if not (
                        isinstance(finding.get("name"), str)
                        and finding["name"].strip()
                        and valid_http_url(finding.get("url"))
                    ):
                        failures.append(
                            f"[finding] {source_id} finding {index} lacks "
                            "name or URL"
                        )
                        continue
                    if (
                        finding.get("category_overlap") == "unreviewed"
                        and disposition_decision == "accept"
                    ):
                        failures.append(
                            f"[finding] {source_id} finding {index} "
                            "remains unreviewed"
                        )
                    if (
                        finding.get("relationship") == "exact"
                        and finding.get("category_overlap") == "same"
                        and disposition_decision == "accept"
                    ):
                        failures.append(
                            "[collision] exact same-category prior use blocks "
                            f"acceptance: {source_id} finding {index}"
                        )
    if (
        decided_at is not None
        and latest_source_at is not None
        and decided_at <= latest_source_at
    ):
        failures.append(
            "[disposition] decided_at must follow the latest source evidence"
        )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check a name-clearance evidence ledger offline."
    )
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()

    failures = check_ledger(args.ledger)
    if failures:
        print(f"FAIL: {len(failures)} problem(s)\n")
        for failure in failures:
            print(f"  {failure}")
        return 1
    print("OK: name-clearance evidence ledger is complete and current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
