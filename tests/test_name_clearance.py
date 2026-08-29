# SPDX-FileCopyrightText: 2026 HLLMR Ventures LLC
# SPDX-License-Identifier: Apache-2.0
"""Public-interface tests for the name-clearance evidence gate."""

from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.parse import quote, quote_plus

from scripts import collect_name_clearance as collector


REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "checks" / "check_name_clearance.py"
COLLECTOR = REPO_ROOT / "scripts" / "collect_name_clearance.py"
REQUIRED_SOURCES = (
    "github",
    "pypi",
    "npm",
    "crates_io",
    "com_rdap",
    "web_common_law",
    "uspto",
)


class NameClearanceProcessTests(unittest.TestCase):
    def valid_ledger(self) -> dict:
        now = datetime.now(timezone.utc).replace(microsecond=0)
        sources = []
        for source_id in REQUIRED_SOURCES:
            human = source_id in {"web_common_law", "uspto"}
            exact_queries = ["Example"]
            similar_queries = (
                ["Ex ample"]
                if source_id == "uspto"
                else ["Example software", "Example AI agent", "Ex ample"]
                if source_id == "web_common_law"
                else ["Example software", "Example AI agent"]
            )
            if human:
                evidence = {
                    "result_count": 0,
                    "notes": "Named reviewer found no conflicting result.",
                    "queries": exact_queries + similar_queries,
                    "reviewed_at": now.isoformat().replace("+00:00", "Z"),
                }
                response_sha256 = hashlib.sha256(
                    json.dumps(
                        evidence, sort_keys=True, separators=(",", ":")
                    ).encode("utf-8")
                ).hexdigest()
                requests = None
            else:
                requests = []
                for query_kind, query in (
                    [("exact", query) for query in exact_queries]
                    + [("similar", query) for query in similar_queries]
                ):
                    request_kinds = {
                        "github": ("repository_search", "organization_search"),
                        "pypi": ("exact_lookup",),
                        "npm": ("exact_lookup", "search"),
                        "crates_io": ("exact_lookup", "search"),
                        "com_rdap": ("domain_lookup",),
                    }[source_id]
                    for request_kind in request_kinds:
                        query_slug = collector.slugify(query)
                        if source_id == "github" and request_kind == "repository_search":
                            request_url = (
                                "https://api.github.com/search/repositories?q="
                                f"{quote(query + ' in:name')}&per_page=100"
                            )
                        elif source_id == "github":
                            request_url = (
                                "https://api.github.com/search/users?q="
                                f"{quote(query + ' in:login type:org')}&per_page=100"
                            )
                        elif source_id == "pypi":
                            request_url = f"https://pypi.org/pypi/{quote(query_slug)}/json"
                        elif source_id == "npm" and request_kind == "exact_lookup":
                            request_url = f"https://registry.npmjs.org/{quote(query_slug)}"
                        elif source_id == "npm":
                            request_url = (
                                "https://registry.npmjs.org/-/v1/search?size=100&text="
                                + quote(query)
                            )
                        elif source_id == "crates_io" and request_kind == "exact_lookup":
                            request_url = f"https://crates.io/api/v1/crates/{quote(query_slug)}"
                        elif source_id == "crates_io":
                            request_url = (
                                "https://crates.io/api/v1/crates?q="
                                f"{quote(query)}&per_page=100"
                            )
                        else:
                            request_url = (
                                "https://rdap.verisign.com/com/v1/domain/"
                                f"{quote(query_slug)}.com"
                            )
                        request = {
                            "url": request_url,
                            "http_status": 200,
                            "body_sha256": "b" * 64,
                            "query": query,
                            "query_kind": query_kind,
                            "request_kind": request_kind,
                        }
                        requests.append(request)
                response_sha256 = hashlib.sha256(
                    json.dumps(
                        requests, sort_keys=True, separators=(",", ":")
                    ).encode("utf-8")
                ).hexdigest()
                evidence = None
            sources.append(
                {
                    "id": source_id,
                    "mode": "human_review" if human else "automated",
                    "queries": {
                        "exact": exact_queries,
                        "similar": similar_queries,
                    },
                    "url": (
                        "https://www.google.com/search?q="
                        + quote_plus('"Example" OR "example" software AI agent')
                        if source_id == "web_common_law"
                        else "https://tmsearch.uspto.gov/search/search-results"
                        if source_id == "uspto"
                        else requests[0]["url"]
                    ),
                    "checked_at": now.isoformat().replace("+00:00", "Z"),
                    "status": "clear",
                    "response_sha256": response_sha256,
                    **({"evidence": evidence} if human else {
                        "requests": requests
                    }),
                    "findings": [],
                    "reviewed_by": "Owner" if source_id in {
                        "web_common_law", "uspto"
                    } else None,
                    **({"reviewer_kind": "human"} if human else {}),
                }
            )
        return {
            "schema": 1,
            "candidate": {
                "display_name": "Example",
                "slug": "example",
                "variants": ["example"],
            },
            "collected_at": now.isoformat().replace("+00:00", "Z"),
            "expires_at": (now + timedelta(days=7)).isoformat().replace(
                "+00:00", "Z"
            ),
            "sources": sources,
            "limitations": [
                "This bounded search does not prove legal clearance or "
                "noninfringement."
            ],
            "disposition": {
                "decision": "accept",
                "decided_by": "Owner",
                "decided_at": (now + timedelta(seconds=1)).isoformat().replace(
                    "+00:00", "Z"
                ),
                "rationale": "All required evidence reviewed.",
            },
        }

    def run_checker(self, ledger: dict) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ledger.json"
            path.write_text(
                json.dumps(ledger, indent=2) + "\n", encoding="utf-8"
            )
            return subprocess.run(
                [sys.executable, str(CHECKER), str(path)],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_missing_required_source_fails_closed(self):
        ledger = self.valid_ledger()
        ledger["sources"] = [
            source for source in ledger["sources"]
            if source["id"] != "uspto"
        ]

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[source] required source 'uspto' is missing", result.stdout)

    def test_schema_and_candidate_identity_are_required(self):
        ledger = self.valid_ledger()
        ledger.pop("schema")
        ledger.pop("candidate")

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[ledger] schema must be 1", result.stdout)
        self.assertIn("[candidate] candidate identity is incomplete", result.stdout)

    def test_boolean_schema_is_not_schema_one(self):
        ledger = self.valid_ledger()
        ledger["schema"] = True

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[ledger] schema must be 1", result.stdout)

    def test_limitations_must_retain_the_legal_clearance_caveat(self):
        ledger = self.valid_ledger()
        ledger["limitations"] = []

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[ledger] limitations must disclaim legal clearance",
            result.stdout,
        )

    def test_limitations_cannot_claim_legal_clearance(self):
        ledger = self.valid_ledger()
        ledger["limitations"] = ["This ledger provides legal clearance."]

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[ledger] limitations must disclaim legal clearance",
            result.stdout,
        )

    def test_candidate_identity_must_match_declared_queries(self):
        ledger = self.valid_ledger()
        ledger["candidate"] = {
            "display_name": "Different Name",
            "slug": "different-name",
            "variants": ["different name", "different-name"],
        }

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[query] github exact query 'Example' does not identify candidate 'Different Name'",
            result.stdout,
        )

    def test_candidate_variant_cannot_self_authorize_an_unrelated_alias(self):
        ledger = self.valid_ledger()
        ledger["candidate"]["variants"].append(
            "example-totally-unrelated-alias"
        )

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[candidate] variant 'example-totally-unrelated-alias' is not derived",
            result.stdout,
        )

    def test_candidate_variants_must_include_the_canonical_identity(self):
        ledger = self.valid_ledger()
        ledger["candidate"]["variants"] = ["examp"]

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[candidate] variants must include the canonical identity",
            result.stdout,
        )

    def test_automated_queries_cannot_substitute_a_prefix_variant(self):
        ledger = self.valid_ledger()
        ledger["candidate"]["variants"].append("examp")
        source = next(
            item for item in ledger["sources"] if item["id"] == "pypi"
        )
        replacements = {
            "Example software": "Examp software",
            "Example AI agent": "Examp AI agent",
        }
        source["queries"]["similar"] = list(replacements.values())
        for request in source["requests"]:
            if request["query_kind"] == "similar":
                request["query"] = replacements[request["query"]]
                request["url"] = (
                    "https://pypi.org/pypi/"
                    f"{collector.slugify(request['query'])}/json"
                )
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["requests"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[query] pypi similar query 'Examp software' does not identify "
            "candidate 'Example'",
            result.stdout,
        )

    def test_automated_queries_require_candidate_at_a_leading_boundary(self):
        ledger = self.valid_ledger()
        source = next(
            item for item in ledger["sources"] if item["id"] == "pypi"
        )
        replacements = {
            "Example software": "NotExample software",
            "Example AI agent": "NotExample AI agent",
        }
        source["queries"]["similar"] = list(replacements.values())
        for request in source["requests"]:
            if request["query_kind"] == "similar":
                request["query"] = replacements[request["query"]]
                request["url"] = (
                    "https://pypi.org/pypi/"
                    f"{collector.slugify(request['query'])}/json"
                )
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["requests"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[query] pypi similar query 'NotExample software' does not identify "
            "candidate 'Example'",
            result.stdout,
        )

    def test_duplicate_source_id_fails_closed(self):
        ledger = self.valid_ledger()
        ledger["sources"].append(dict(ledger["sources"][0]))

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[source] duplicate source id 'github'", result.stdout)

    def test_non_object_source_entry_fails_closed(self):
        ledger = self.valid_ledger()
        ledger["sources"].append(7)

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[source] source entry 8 must be an object", result.stdout)

    def test_non_string_source_id_fails_closed_without_exception(self):
        ledger = self.valid_ledger()
        ledger["sources"].append({"id": []})

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[source] source entry 8 has an invalid id", result.stdout)

    def test_unavailable_required_source_fails_closed(self):
        ledger = self.valid_ledger()
        ledger["sources"][0]["status"] = "unavailable"

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[source] github is unavailable; no clearance can be inferred",
            result.stdout,
        )

    def test_unknown_source_mode_and_status_fail_closed(self):
        ledger = self.valid_ledger()
        source = ledger["sources"][0]
        source["mode"] = "bogus"
        source["status"] = "failed"
        source.pop("url")
        source.pop("checked_at")
        source.pop("requests")

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[source] github mode must be", result.stdout)
        self.assertIn("[source] github status must be", result.stdout)
        self.assertIn("[source] github requires a source URL", result.stdout)
        self.assertIn("[source] github requires checked_at", result.stdout)

    def test_non_string_source_enums_fail_without_exception(self):
        ledger = self.valid_ledger()
        ledger["sources"][0]["mode"] = []
        ledger["sources"][0]["status"] = []

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[source] github mode must be", result.stdout)
        self.assertIn("[source] github status must be", result.stdout)

    def test_expired_evidence_fails_closed(self):
        ledger = self.valid_ledger()
        ledger["expires_at"] = "2000-01-01T00:00:00Z"

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[freshness] evidence expired", result.stdout)

    def test_expiry_cannot_extend_beyond_seven_days(self):
        ledger = self.valid_ledger()
        collected = datetime.fromisoformat(
            ledger["collected_at"].replace("Z", "+00:00")
        )
        ledger["expires_at"] = (collected + timedelta(days=8)).isoformat().replace(
            "+00:00", "Z"
        )

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[freshness] expires_at must be no later than seven days after collected_at",
            result.stdout,
        )

    def test_collection_cannot_be_future_dated(self):
        ledger = self.valid_ledger()
        ledger["collected_at"] = (
            datetime.now(timezone.utc) + timedelta(days=1)
        ).isoformat().replace("+00:00", "Z")

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[freshness] collected_at cannot be in the future",
            result.stdout,
        )

    def test_source_timestamp_must_fall_inside_ledger_window(self):
        ledger = self.valid_ledger()
        ledger["sources"][0]["checked_at"] = "2000-01-01T00:00:00Z"

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[freshness] github checked_at falls outside the ledger window",
            result.stdout,
        )

    def test_source_timestamp_must_be_utc(self):
        ledger = self.valid_ledger()
        checked = datetime.fromisoformat(
            ledger["sources"][0]["checked_at"].replace("Z", "+00:00")
        )
        ledger["sources"][0]["checked_at"] = checked.astimezone(
            timezone(timedelta(hours=1))
        ).isoformat()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[source] github requires checked_at as an ISO-8601 UTC timestamp",
            result.stdout,
        )

    def test_finding_without_category_comparison_fails_closed(self):
        ledger = self.valid_ledger()
        ledger["sources"][0]["status"] = "finding"
        ledger["sources"][0]["findings"] = [
            {
                "name": "Example",
                "url": "https://example.invalid/collision",
                "relationship": "exact",
            }
        ]

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[finding] github finding 1 lacks category_overlap",
            result.stdout,
        )

    def test_clear_source_cannot_contain_findings(self):
        ledger = self.valid_ledger()
        ledger["sources"][0]["findings"] = [
            {
                "name": "Example-like",
                "url": "https://example.invalid/collision",
                "relationship": "similar",
                "category_overlap": "unrelated",
            }
        ]

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[source] github status clear contradicts retained findings",
            result.stdout,
        )

    def test_source_must_explicitly_record_findings(self):
        ledger = self.valid_ledger()
        ledger["sources"][0].pop("findings")

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[finding] github requires an explicit findings list",
            result.stdout,
        )

    def test_exact_same_category_prior_use_blocks_acceptance(self):
        ledger = self.valid_ledger()
        ledger["sources"][0]["status"] = "finding"
        ledger["sources"][0]["findings"] = [
            {
                "name": "Example",
                "url": "https://example.invalid/collision",
                "relationship": "exact",
                "category_overlap": "same",
                "first_public_use": "2026-01-01",
            }
        ]

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[collision] exact same-category prior use blocks acceptance",
            result.stdout,
        )

    def test_unknown_finding_relationship_cannot_evade_collision_block(self):
        ledger = self.valid_ledger()
        ledger["sources"][0]["status"] = "finding"
        ledger["sources"][0]["findings"] = [
            {
                "name": "Example",
                "url": "https://prior.invalid/example",
                "relationship": "bogus",
                "category_overlap": "same",
                "first_public_use": "2020-01-01",
            }
        ]

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[finding] github finding 1 has invalid relationship",
            result.stdout,
        )

    def test_finding_url_requires_a_real_http_hostname(self):
        ledger = self.valid_ledger()
        ledger["sources"][0]["status"] = "finding"
        ledger["sources"][0]["findings"] = [
            {
                "name": "Example-like",
                "url": "https://",
                "relationship": "similar",
                "category_overlap": "unrelated",
                "first_public_use": None,
            }
        ]

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[finding] github finding 1 lacks name or URL",
            result.stdout,
        )

    def test_acceptance_fails_with_unreviewed_finding(self):
        ledger = self.valid_ledger()
        ledger["sources"][0]["status"] = "finding"
        ledger["sources"][0]["findings"] = [
            {
                "name": "Example-like",
                "url": "https://example.invalid/collision",
                "relationship": "similar",
                "category_overlap": "unreviewed",
            }
        ]

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[finding] github finding 1 remains unreviewed",
            result.stdout,
        )

    def test_rejected_candidate_may_retain_unreviewed_nonblocking_hits(self):
        ledger = self.valid_ledger()
        ledger["disposition"] = {
            "decision": "reject",
            "decided_by": "Owner",
            "decided_at": ledger["disposition"]["decided_at"],
            "rationale": "A separately classified same-category collision blocks use.",
        }
        ledger["sources"][0]["status"] = "finding"
        ledger["sources"][0]["findings"] = [
            {
                "name": "Blocking exact use",
                "url": "https://example.invalid/blocker",
                "relationship": "exact",
                "category_overlap": "same",
            },
            {
                "name": "Unreviewed remainder",
                "url": "https://example.invalid/remainder",
                "relationship": "exact",
                "category_overlap": "unreviewed",
            },
        ]

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_pending_owner_disposition_fails_closed(self):
        ledger = self.valid_ledger()
        ledger["disposition"] = {"decision": "pending"}

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[disposition] Owner decision must be accept or reject",
            result.stdout,
        )

    def test_malformed_disposition_with_findings_fails_without_exception(self):
        ledger = self.valid_ledger()
        ledger["disposition"] = []
        ledger["sources"][0]["status"] = "finding"
        ledger["sources"][0]["findings"] = [
            {
                "name": "Example",
                "url": "https://example.invalid/finding",
                "relationship": "similar",
                "category_overlap": "unreviewed",
                "first_public_use": None,
            }
        ]

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[disposition] Owner decision must be accept or reject",
            result.stdout,
        )

    def test_owner_disposition_cannot_predate_collection(self):
        ledger = self.valid_ledger()
        ledger["disposition"]["decided_at"] = "2000-01-01T00:00:00Z"

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[disposition] decided_at cannot predate collected_at",
            result.stdout,
        )

    def test_owner_disposition_must_follow_latest_source_evidence(self):
        ledger = self.valid_ledger()
        collected = datetime.fromisoformat(
            ledger["collected_at"].replace("Z", "+00:00")
        )
        ledger["sources"][0]["checked_at"] = (
            collected + timedelta(hours=1)
        ).isoformat().replace("+00:00", "Z")

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[disposition] decided_at must follow the latest source evidence",
            result.stdout,
        )

    def test_owner_disposition_timestamp_must_be_strictly_later(self):
        ledger = self.valid_ledger()
        ledger["disposition"]["decided_at"] = ledger["sources"][0]["checked_at"]

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[disposition] decided_at must follow the latest source evidence",
            result.stdout,
        )

    def test_human_review_timestamp_must_fall_inside_the_ledger_window(self):
        ledger = self.valid_ledger()
        source = ledger["sources"][-1]
        source["evidence"]["reviewed_at"] = "2099-01-01T00:00:00Z"
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["evidence"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[freshness] uspto reviewed_at falls outside the ledger window",
            result.stdout,
        )

    def test_missing_similar_name_query_fails_closed(self):
        ledger = self.valid_ledger()
        ledger["sources"][1]["queries"]["similar"] = []

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[query] pypi requires non-empty exact and similar queries",
            result.stdout,
        )

    def test_exact_plan_requires_a_canonical_name_query(self):
        ledger = self.valid_ledger()
        source = next(
            item for item in ledger["sources"] if item["id"] == "pypi"
        )
        source["queries"]["exact"] = ["Example software"]
        for request in source["requests"]:
            if request["query_kind"] == "exact":
                request["query"] = "Example software"
                request["url"] = (
                    "https://pypi.org/pypi/example-software/json"
                )
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["requests"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[query] pypi exact plan lacks canonical candidate identity",
            result.stdout,
        )

    def test_similar_plan_requires_category_variation_coverage(self):
        ledger = self.valid_ledger()
        source = next(
            item for item in ledger["sources"] if item["id"] == "pypi"
        )
        source["queries"]["similar"] = ["Example zzznotasimilarsearch"]
        for request in source["requests"]:
            if request["query_kind"] == "similar":
                request["query"] = "Example zzznotasimilarsearch"
                request["url"] = (
                    "https://pypi.org/pypi/"
                    "example-zzznotasimilarsearch/json"
                )
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["requests"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[query] pypi query plan must cover AI, software, and agent variations",
            result.stdout,
        )

    def test_uspto_similar_plan_requires_an_alternative_spelling(self):
        ledger = self.valid_ledger()
        source = next(
            item for item in ledger["sources"] if item["id"] == "uspto"
        )
        source["queries"]["similar"] = ["Example zzz"]
        source["evidence"]["queries"] = ["Example", "Example zzz"]
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["evidence"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[query] uspto similar plan requires an alternative spelling",
            result.stdout,
        )

    def test_web_similar_plan_requires_a_name_variation(self):
        ledger = self.valid_ledger()
        source = next(
            item for item in ledger["sources"]
            if item["id"] == "web_common_law"
        )
        source["queries"]["exact"] = [
            "Example", "Example AI software agent"
        ]
        source["queries"]["similar"] = ["Example zzz"]
        source["evidence"]["queries"] = (
            source["queries"]["exact"] + source["queries"]["similar"]
        )
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["evidence"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[query] web_common_law similar plan requires a name variation",
            result.stdout,
        )

    def test_human_queries_require_a_bounded_candidate_term(self):
        ledger = self.valid_ledger()
        source = next(
            item for item in ledger["sources"]
            if item["id"] == "web_common_law"
        )
        source["queries"]["similar"] = [
            "NotExample software", "NotExample AI agent", "Ex ample"
        ]
        source["evidence"]["queries"] = (
            source["queries"]["exact"] + source["queries"]["similar"]
        )
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["evidence"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[query] web_common_law similar query 'NotExample software' "
            "does not identify candidate 'Example'",
            result.stdout,
        )

    def test_declared_queries_must_all_be_nonempty_strings(self):
        ledger = self.valid_ledger()
        ledger["sources"][1]["queries"]["similar"].append(42)

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[query] pypi exact and similar queries must be non-empty strings",
            result.stdout,
        )

    def test_declared_query_without_bound_evidence_fails_closed(self):
        ledger = self.valid_ledger()
        source = ledger["sources"][1]
        source["requests"] = [
            request for request in source["requests"]
            if request["query_kind"] != "similar"
        ]
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["requests"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[query] pypi has no evidence bound to similar query 'Example software'",
            result.stdout,
        )

    def test_github_requires_repository_and_organization_searches(self):
        ledger = self.valid_ledger()
        source = ledger["sources"][0]
        source["requests"] = [
            request for request in source["requests"]
            if request["request_kind"] != "organization_search"
        ]
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["requests"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[query] github query 'Example' lacks organization_search evidence",
            result.stdout,
        )

    def test_package_search_sources_require_each_request_kind_per_query(self):
        for source_id in ("npm", "crates_io"):
            with self.subTest(source_id=source_id):
                ledger = self.valid_ledger()
                source = next(
                    item for item in ledger["sources"]
                    if item["id"] == source_id
                )
                source["requests"] = [
                    request for request in source["requests"]
                    if request["request_kind"] != "exact_lookup"
                ]
                source["response_sha256"] = hashlib.sha256(
                    json.dumps(
                        source["requests"],
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest()

                result = self.run_checker(ledger)

                self.assertEqual(
                    result.returncode, 1, result.stdout + result.stderr
                )
                self.assertIn(
                    f"[query] {source_id} query 'Example' lacks "
                    "exact_lookup evidence",
                    result.stdout,
                )

    def test_required_source_cannot_change_its_evidence_mode(self):
        ledger = self.valid_ledger()
        source = ledger["sources"][0]
        evidence = {
            "queries": source["queries"]["exact"] + source["queries"]["similar"],
            "notes": "Self-asserted replacement evidence.",
        }
        source["mode"] = "human_review"
        source["reviewed_by"] = "Example Human"
        source["evidence"] = evidence
        source.pop("requests")
        source["response_sha256"] = hashlib.sha256(
            json.dumps(evidence, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("[source] github mode must be automated", result.stdout)

    def test_checker_rejects_failed_search_response_as_clear(self):
        ledger = self.valid_ledger()
        source = ledger["sources"][0]
        source["requests"][0]["http_status"] = 404
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["requests"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[evidence] github request 1 has an unsuccessful HTTP status",
            result.stdout,
        )

    def test_checker_rejects_unknown_request_kind(self):
        ledger = self.valid_ledger()
        source = ledger["sources"][1]
        source["requests"][0]["request_kind"] = "bogus"
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["requests"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[evidence] pypi request 1 has an invalid request_kind",
            result.stdout,
        )

    def test_non_string_request_enums_fail_without_exception(self):
        ledger = self.valid_ledger()
        source = ledger["sources"][1]
        source["requests"][0]["query_kind"] = []
        source["requests"][1]["request_kind"] = []
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["requests"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("is not bound to a declared query", result.stdout)
        self.assertIn("has an invalid request_kind", result.stdout)

    def test_non_string_finding_enums_fail_without_exception(self):
        ledger = self.valid_ledger()
        ledger["sources"][0]["status"] = "finding"
        ledger["sources"][0]["findings"] = [
            {
                "name": "Example",
                "url": "https://prior.invalid/example",
                "relationship": [],
                "category_overlap": [],
                "first_public_use": None,
            }
        ]

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("lacks category_overlap", result.stdout)

    def test_checker_requires_request_body_digest(self):
        ledger = self.valid_ledger()
        source = ledger["sources"][2]
        source["requests"][0]["body_sha256"] = "not-a-digest"
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["requests"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[evidence] npm request 1 body_sha256 must be 64 lowercase hex digits",
            result.stdout,
        )

    def test_request_url_must_derive_from_its_declared_query(self):
        ledger = self.valid_ledger()
        source = ledger["sources"][1]
        source["requests"][0]["url"] = (
            "https://example.invalid/executed-a-different-query"
        )
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["requests"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[query] pypi request 1 URL does not match its declared query",
            result.stdout,
        )

    def test_automated_source_url_must_match_its_first_request(self):
        ledger = self.valid_ledger()
        ledger["sources"][1]["url"] = "https://example.invalid/relabelled"

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[source] pypi URL does not match its first request",
            result.stdout,
        )

    def test_human_review_source_requires_named_reviewer(self):
        ledger = self.valid_ledger()
        ledger["sources"][-1]["reviewed_by"] = None

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[review] uspto human review requires reviewed_by",
            result.stdout,
        )

    def test_human_review_source_requires_human_attestation(self):
        ledger = self.valid_ledger()
        ledger["sources"][-1].pop("reviewer_kind")

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[review] uspto requires reviewer_kind human",
            result.stdout,
        )

    def test_human_review_sources_require_their_canonical_endpoints(self):
        ledger = self.valid_ledger()
        web_source = next(
            item for item in ledger["sources"]
            if item["id"] == "web_common_law"
        )
        web_source["url"] = "https://tmsearch.uspto.gov/search/search-results"
        uspto_source = next(
            item for item in ledger["sources"] if item["id"] == "uspto"
        )
        uspto_source["url"] = "https://example.invalid/not-uspto"

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[source] web_common_law URL does not match its canonical endpoint",
            result.stdout,
        )
        self.assertIn(
            "[source] uspto URL does not match its canonical endpoint",
            result.stdout,
        )

    def test_source_requires_verifiable_response_digest(self):
        ledger = self.valid_ledger()
        ledger["sources"][2]["response_sha256"] = "not-a-digest"

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[evidence] npm response_sha256 must be 64 lowercase hex digits",
            result.stdout,
        )

    def test_automated_response_digest_must_match_recorded_requests(self):
        ledger = self.valid_ledger()
        ledger["sources"][0]["response_sha256"] = "a" * 64

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[evidence] github response_sha256 does not match requests",
            result.stdout,
        )

    def test_human_response_digest_must_match_recorded_evidence(self):
        ledger = self.valid_ledger()
        ledger["sources"][-1]["response_sha256"] = "a" * 64

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[evidence] uspto response_sha256 does not match evidence",
            result.stdout,
        )

    def test_human_review_queries_must_match_digested_evidence(self):
        ledger = self.valid_ledger()
        source = ledger["sources"][-1]
        source["evidence"]["queries"] = ["Example"]
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["evidence"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[query] uspto has no evidence bound to similar query 'Ex ample'",
            result.stdout,
        )

    def test_human_review_requires_structured_result_count_and_notes(self):
        ledger = self.valid_ledger()
        source = ledger["sources"][-1]
        source["evidence"]["result_count"] = "none"
        source["evidence"]["notes"] = ""
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["evidence"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[evidence] uspto human evidence requires a nonnegative result_count",
            result.stdout,
        )
        self.assertIn(
            "[evidence] uspto human evidence requires notes",
            result.stdout,
        )

    def test_human_result_count_must_agree_with_clear_status(self):
        ledger = self.valid_ledger()
        source = ledger["sources"][-1]
        source["evidence"]["result_count"] = 1
        source["response_sha256"] = hashlib.sha256(
            json.dumps(
                source["evidence"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()

        result = self.run_checker(ledger)

        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn(
            "[source] uspto status clear contradicts human result_count",
            result.stdout,
        )

    def test_offline_collector_emits_complete_fail_closed_template(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "candidate.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(COLLECTOR),
                    "--candidate",
                    "Example Name",
                    "--output",
                    str(output),
                    "--no-network",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            ledger = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(ledger["candidate"]["slug"], "example-name")
            self.assertEqual(
                {source["id"] for source in ledger["sources"]},
                set(REQUIRED_SOURCES),
            )
            self.assertEqual(ledger["disposition"]["decision"], "pending")
            self.assertTrue(all(
                source["status"] == "unavailable"
                for source in ledger["sources"]
            ))

    def test_search_endpoint_404_is_unavailable_not_clear(self):
        response = {
            "url": "https://example.invalid/search",
            "http_status": 404,
            "body_sha256": "a" * 64,
            "body": b"{}",
        }
        with patch.object(collector, "fetch", return_value=response):
            statuses = {
                source_id: collector.collect_automated(
                    source_id,
                    "Example",
                    "example",
                    "2026-08-28T00:00:00Z",
                    1.0,
                )["status"]
                for source_id in ("github", "npm", "crates_io")
            }

        self.assertEqual(
            statuses,
            {"github": "unavailable", "npm": "unavailable", "crates_io": "unavailable"},
        )

    def test_github_collector_executes_declared_repo_and_org_queries(self):
        response = {
            "url": "https://example.invalid/search",
            "http_status": 200,
            "body_sha256": "a" * 64,
            "body": b'{"items": []}',
        }
        with patch.object(collector, "fetch", return_value=response):
            source = collector.collect_automated(
                "github",
                "Example",
                "example",
                "2026-08-28T00:00:00Z",
                1.0,
            )

        expected = {
            (kind, query, request_kind)
            for kind in ("exact", "similar")
            for query in source["queries"][kind]
            for request_kind in ("repository_search", "organization_search")
        }
        actual = {
            (request.get("query_kind"), request.get("query"), request.get("request_kind"))
            for request in source["requests"]
        }
        self.assertEqual(actual, expected)

    def test_unexpected_success_body_is_unavailable_not_clear(self):
        response = {
            "url": "https://example.invalid/search",
            "http_status": 200,
            "body_sha256": "a" * 64,
            "body": b"{}",
        }
        with patch.object(collector, "fetch", return_value=response):
            source = collector.collect_automated(
                "github",
                "Example",
                "example",
                "2026-08-28T00:00:00Z",
                1.0,
            )

        self.assertEqual(source["status"], "unavailable")

    def test_non_object_success_json_is_unavailable_not_exception(self):
        response = {
            "url": "https://example.invalid/search",
            "http_status": 200,
            "body_sha256": "a" * 64,
            "body": b"[]",
        }
        with patch.object(collector, "fetch", return_value=response):
            source = collector.collect_automated(
                "github",
                "Example",
                "example",
                "2026-08-28T00:00:00Z",
                1.0,
            )

        self.assertEqual(source["status"], "unavailable")

    def test_malformed_nested_success_json_is_unavailable_not_exception(self):
        bodies = {
            "github": b'{"items": [1]}',
            "pypi": b'{"info": []}',
            "npm": b'{"name": "example", "objects": [1]}',
            "crates_io": b'{"crate": {}, "crates": [1]}',
        }
        for source_id, body in bodies.items():
            with self.subTest(source_id=source_id):
                response = {
                    "url": "https://example.invalid/search",
                    "http_status": 200,
                    "body_sha256": "a" * 64,
                    "body": body,
                }
                with patch.object(collector, "fetch", return_value=response):
                    source = collector.collect_automated(
                        source_id,
                        "Example",
                        "example",
                        "2026-08-28T00:00:00Z",
                        1.0,
                    )

                self.assertEqual(source["status"], "unavailable")

    def test_malformed_nested_field_types_are_unavailable_not_exception(self):
        bodies = {
            "github": b'{"items": [{"name": []}]}',
            "pypi": b'{"info": {"name": []}}',
            "npm": b'{"name": "example", "objects": '
                   b'[{"package": {"name": []}}]}',
            "crates_io": b'{"crate": {}, "crates": [{"name": []}]}',
        }
        for source_id, body in bodies.items():
            with self.subTest(source_id=source_id):
                response = {
                    "url": "https://example.invalid/search",
                    "http_status": 200,
                    "body_sha256": "a" * 64,
                    "body": body,
                }
                with patch.object(collector, "fetch", return_value=response):
                    source = collector.collect_automated(
                        source_id,
                        "Example",
                        "example",
                        "2026-08-28T00:00:00Z",
                        1.0,
                    )

                self.assertEqual(source["status"], "unavailable")

    def test_empty_success_identity_fields_are_unavailable(self):
        bodies = {
            "github": (
                b'{"items": [{"name": "", "full_name": "", '
                b'"login": "", "html_url": ""}]}'
            ),
            "pypi": b'{"info": {"name": ""}}',
            "npm": b'{"name": "", "objects": '
                   b'[{"package": {"name": ""}}]}',
            "crates_io": b'{"crate": {"name": ""}, '
                         b'"crates": [{"name": ""}]}',
            "com_rdap": b'{"ldhName": ""}',
        }
        for source_id, body in bodies.items():
            with self.subTest(source_id=source_id):
                response = {
                    "url": "https://example.invalid/search",
                    "http_status": 200,
                    "body_sha256": "a" * 64,
                    "body": body,
                }
                with patch.object(collector, "fetch", return_value=response):
                    source = collector.collect_automated(
                        source_id,
                        "Example",
                        "example",
                        "2026-08-28T00:00:00Z",
                        1.0,
                    )

                self.assertEqual(source["status"], "unavailable")


if __name__ == "__main__":
    unittest.main()
