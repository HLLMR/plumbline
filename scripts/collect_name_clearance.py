#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Collect a bounded, reviewable name-clearance evidence ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, quote_plus, urlsplit
from urllib.request import Request, urlopen


SOURCE_SPECS = (
    ("github", "automated", "https://api.github.com/search/repositories?q={query}"),
    ("pypi", "automated", "https://pypi.org/pypi/{slug}/json"),
    ("npm", "automated", "https://registry.npmjs.org/{slug}"),
    ("crates_io", "automated", "https://crates.io/api/v1/crates/{slug}"),
    ("com_rdap", "automated", "https://rdap.verisign.com/com/v1/domain/{slug}.com"),
    ("web_common_law", "human_review", "https://www.google.com/search?q={query}"),
    ("uspto", "human_review", "https://tmsearch.uspto.gov/search/search-results"),
)


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def source_entry(
    source_id: str, mode: str, template: str, candidate: str, slug: str,
    checked_at: str,
) -> dict:
    queries = query_plan(candidate, slug)
    query = quote_plus(f'"{candidate}" OR "{slug}" software AI agent')
    url = template.format(query=query, slug=slug)
    evidence = b"network collection deliberately disabled"
    return {
        "id": source_id,
        "mode": mode,
        "queries": queries,
        "url": url,
        "checked_at": checked_at,
        "status": "unavailable",
        "response_sha256": hashlib.sha256(evidence).hexdigest(),
        "findings": [],
        "reviewed_by": None,
        "error": evidence.decode("ascii"),
    }


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def valid_http_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def fetch(url: str, timeout: float) -> dict:
    request = Request(url, headers={"User-Agent": "name-clearance-ledger/1"})
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            status = response.status
    except HTTPError as exc:
        body = exc.read()
        status = exc.code
    except (OSError, URLError) as exc:
        return {"url": url, "error": str(exc)}
    return {
        "url": url,
        "http_status": status,
        "body_sha256": hashlib.sha256(body).hexdigest(),
        "body": body,
    }


def response_digest(requests: list[dict]) -> str:
    public = [
        {key: value for key, value in request.items() if key != "body"}
        for request in requests
    ]
    canonical = json.dumps(public, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


def json_body(request: dict) -> dict:
    try:
        value = json.loads(request.get("body", b"{}"))
    except (UnicodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def response_shape_valid(source_id: str, request: dict) -> bool:
    """Reject HTTP success whose JSON does not match the endpoint contract."""
    if request.get("http_status") != 200:
        return True
    data = json_body(request)
    request_kind = request.get("request_kind")
    if source_id == "github":
        items = data.get("items")
        return isinstance(items, list) and all(
            isinstance(item, dict)
            and isinstance(
                item.get(
                    "name" if request_kind == "repository_search" else "login"
                ),
                str,
            )
            and bool(
                item.get(
                    "name" if request_kind == "repository_search" else "login"
                )
            )
            and valid_http_url(item.get("html_url"))
            and (
                request_kind != "repository_search"
                or (
                    isinstance(item.get("full_name"), str)
                    and bool(item["full_name"])
                )
            )
            for item in items
        )
    if source_id == "pypi":
        return (
            isinstance(data.get("info"), dict)
            and isinstance(data["info"].get("name"), str)
            and bool(data["info"]["name"])
        )
    if source_id == "npm" and request_kind == "search":
        objects = data.get("objects")
        return isinstance(objects, list) and all(
            isinstance(item, dict)
            and isinstance(item.get("package"), dict)
            and isinstance(item["package"].get("name"), str)
            and bool(item["package"]["name"])
            and (
                "links" not in item["package"]
                or isinstance(item["package"]["links"], dict)
            )
            and (
                "links" not in item["package"]
                or "npm" not in item["package"]["links"]
                or valid_http_url(item["package"]["links"]["npm"])
            )
            for item in objects
        )
    if source_id == "npm":
        return any(
            isinstance(data.get(key), str) and bool(data[key])
            for key in ("name", "_id")
        )
    if source_id == "crates_io" and request_kind == "search":
        crates = data.get("crates")
        return isinstance(crates, list) and all(
            isinstance(item, dict) and isinstance(item.get("name"), str)
            and bool(item["name"])
            for item in crates
        )
    if source_id == "crates_io":
        return (
            isinstance(data.get("crate"), dict)
            and isinstance(data["crate"].get("name"), str)
            and bool(data["crate"]["name"])
        )
    if source_id == "com_rdap":
        return any(
            isinstance(data.get(key), str) and bool(data[key])
            for key in ("ldhName", "unicodeName", "objectClassName")
        )
    return False


def finding(name: str, url: str, relationship: str = "exact") -> dict:
    return {
        "name": name,
        "url": url,
        "relationship": relationship,
        "category_overlap": "unreviewed",
        "first_public_use": None,
    }


def request_succeeded(source_id: str, index: int, request: dict) -> bool:
    """Apply endpoint-specific HTTP semantics; search endpoints require 200."""
    if "error" in request:
        return False
    status = request.get("http_status")
    if request.get("request_kind") in {"exact_lookup", "domain_lookup"}:
        return status in {200, 404}
    return status == 200


def successful_shape(source_id: str, request: dict) -> bool:
    return (
        request.get("http_status") == 200
        and response_shape_valid(source_id, request)
    )


def query_plan(candidate: str, slug: str) -> dict[str, list[str]]:
    exact = list(dict.fromkeys(value.casefold() for value in (candidate, slug)))
    return {
        "exact": exact,
        "similar": [
            f"{candidate} AI",
            f"{candidate} software",
            f"{candidate} agent",
        ],
    }


def query_request(
    url: str, timeout: float, query_kind: str, query: str, request_kind: str,
) -> dict:
    request = dict(fetch(url, timeout))
    request.update({
        "query_kind": query_kind,
        "query": query,
        "request_kind": request_kind,
    })
    return request


def collect_automated(
    source_id: str, candidate: str, slug: str, checked_at: str, timeout: float,
) -> dict:
    queries = query_plan(candidate, slug)
    requests: list[dict] = []
    findings: list[dict] = []
    seen_findings: set[tuple[str, str]] = set()

    def add_finding(name: str, url: str, query_kind: str) -> None:
        key = (name.casefold(), url)
        if key not in seen_findings:
            findings.append(finding(
                name,
                url,
                "exact" if query_kind == "exact" else "similar",
            ))
            seen_findings.add(key)

    if source_id == "github":
        for query_kind in ("exact", "similar"):
            for query in queries[query_kind]:
                repo_url = (
                    "https://api.github.com/search/repositories?q="
                    f"{quote(query + ' in:name')}&per_page=100"
                )
                org_url = (
                    "https://api.github.com/search/users?q="
                    f"{quote(query + ' in:login type:org')}&per_page=100"
                )
                repo_request = query_request(
                    repo_url, timeout, query_kind, query, "repository_search"
                )
                org_request = query_request(
                    org_url, timeout, query_kind, query, "organization_search"
                )
                requests.extend((repo_request, org_request))
                if successful_shape(source_id, repo_request):
                    for item in json_body(repo_request)["items"]:
                        name = item.get("name", "")
                        if normalize_name(name) == normalize_name(query):
                            add_finding(
                                item.get("full_name", name),
                                item.get("html_url", repo_url),
                                query_kind,
                            )
                if successful_shape(source_id, org_request):
                    for item in json_body(org_request)["items"]:
                        name = item.get("login", "")
                        if normalize_name(name) == normalize_name(query):
                            add_finding(
                                name, item.get("html_url", org_url), query_kind
                            )
    elif source_id == "pypi":
        for query_kind in ("exact", "similar"):
            for query in queries[query_kind]:
                query_slug = slugify(query)
                url = f"https://pypi.org/pypi/{quote(query_slug)}/json"
                request = query_request(
                    url, timeout, query_kind, query, "exact_lookup"
                )
                requests.append(request)
                if successful_shape(source_id, request):
                    data = json_body(request)
                    name = data["info"].get("name", query_slug)
                    add_finding(
                        name,
                        f"https://pypi.org/project/{quote(query_slug)}/",
                        query_kind,
                    )
    elif source_id == "npm":
        for query_kind in ("exact", "similar"):
            for query in queries[query_kind]:
                query_slug = slugify(query)
                exact_url = f"https://registry.npmjs.org/{quote(query_slug)}"
                search_url = (
                    "https://registry.npmjs.org/-/v1/search?size=100&text="
                    + quote(query)
                )
                exact_request = query_request(
                    exact_url, timeout, query_kind, query, "exact_lookup"
                )
                search_request = query_request(
                    search_url, timeout, query_kind, query, "search"
                )
                requests.extend((exact_request, search_request))
                if successful_shape(source_id, exact_request):
                    add_finding(
                        query_slug,
                        f"https://www.npmjs.com/package/{quote(query_slug)}",
                        query_kind,
                    )
                if successful_shape(source_id, search_request):
                    for item in json_body(search_request)["objects"]:
                        package = item["package"]
                        name = package.get("name", "")
                        if normalize_name(name) == normalize_name(query):
                            add_finding(
                                name,
                                package.get("links", {}).get(
                                    "npm", search_url
                                ),
                                query_kind,
                            )
    elif source_id == "crates_io":
        for query_kind in ("exact", "similar"):
            for query in queries[query_kind]:
                query_slug = slugify(query)
                exact_url = f"https://crates.io/api/v1/crates/{quote(query_slug)}"
                search_url = (
                    "https://crates.io/api/v1/crates?q="
                    f"{quote(query)}&per_page=100"
                )
                exact_request = query_request(
                    exact_url, timeout, query_kind, query, "exact_lookup"
                )
                search_request = query_request(
                    search_url, timeout, query_kind, query, "search"
                )
                requests.extend((exact_request, search_request))
                if successful_shape(source_id, exact_request):
                    add_finding(
                        query_slug,
                        f"https://crates.io/crates/{quote(query_slug)}",
                        query_kind,
                    )
                if successful_shape(source_id, search_request):
                    for item in json_body(search_request)["crates"]:
                        name = item.get("name", "")
                        if normalize_name(name) == normalize_name(query):
                            add_finding(
                                name,
                                f"https://crates.io/crates/{quote(name)}",
                                query_kind,
                            )
    elif source_id == "com_rdap":
        for query_kind in ("exact", "similar"):
            for query in queries[query_kind]:
                query_slug = slugify(query)
                url = (
                    "https://rdap.verisign.com/com/v1/domain/"
                    f"{quote(query_slug)}.com"
                )
                request = query_request(
                    url, timeout, query_kind, query, "domain_lookup"
                )
                requests.append(request)
                if successful_shape(source_id, request):
                    add_finding(f"{query_slug}.com", url, query_kind)
    else:
        raise ValueError(f"unsupported automated source: {source_id}")

    unavailable = any(
        not request_succeeded(source_id, index, request)
        or not response_shape_valid(source_id, request)
        for index, request in enumerate(requests)
    )
    public_requests = [
        {key: value for key, value in request.items() if key != "body"}
        for request in requests
    ]
    return {
        "id": source_id,
        "mode": "automated",
        "queries": queries,
        "url": public_requests[0]["url"],
        "checked_at": checked_at,
        "status": "unavailable" if unavailable else (
            "finding" if findings else "clear"
        ),
        "response_sha256": response_digest(requests),
        "requests": public_requests,
        "findings": findings,
        "reviewed_by": None,
        "error": "one or more requests failed" if unavailable else None,
    }


def build_ledger(candidate: str, no_network: bool, timeout: float) -> dict:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    slug = slugify(candidate)
    if not slug:
        raise ValueError("candidate must contain at least one letter or digit")
    checked_at = utc_text(now)
    if no_network:
        sources = [
            source_entry(source_id, mode, template, candidate, slug, checked_at)
            for source_id, mode, template in SOURCE_SPECS
        ]
    else:
        sources = []
        for source_id, mode, template in SOURCE_SPECS:
            if mode == "automated":
                sources.append(
                    collect_automated(
                        source_id, candidate, slug, checked_at, timeout
                    )
                )
            else:
                sources.append(
                    source_entry(
                        source_id, mode, template, candidate, slug, checked_at
                    )
                )
    return {
        "schema": 1,
        "candidate": {
            "display_name": candidate,
            "slug": slug,
            "variants": sorted({candidate.casefold(), slug}),
        },
        "collected_at": checked_at,
        "expires_at": utc_text(now + timedelta(days=7)),
        "sources": sources,
        "disposition": {"decision": "pending"},
        "limitations": [
            "The ledger proves the recorded search procedure, not legal clearance.",
            "Unavailable or unreviewed sources cannot be interpreted as clear.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Collect name-clearance evidence into canonical JSON."
    )
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--network", action="store_true")
    mode.add_argument("--no-network", action="store_true")
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    try:
        ledger = build_ledger(args.candidate, args.no_network, args.timeout)
    except ValueError as exc:
        parser.error(str(exc))
    args.output.write_text(
        json.dumps(ledger, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"wrote fail-closed clearance ledger: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
