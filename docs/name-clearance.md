# Name clearance before identity work

Run this gate before a project adopts a public name, package name, repository
slug, domain, logo, or launch campaign. Run it again within seven days of a
public-release decision that selects or changes the identity. It is cheaper to reject a name here than to migrate an
entire release later.

This process produces evidence of what was searched, when, and with what
result. It **does not prove legal clearance**, exclusivity, or
noninfringement. The Owner makes the product-risk decision; qualified counsel
makes any legal determination the Owner requires.

## Preserved examples versus new decisions

The four named ledgers shipped under `examples/name-clearance-ledgers/` record
completed accept/reject decisions. The distribution check validates their
evidence at each recorded disposition time, including the requirement that the
decision preceded expiry and followed the source reviews. It does not renew
those searches or claim current clearance. Evidence bytes and dates stay intact.

All other ledger files and the ordinary `check_name_clearance.py` command use
current-time freshness. Historical validation is an explicit library context,
not a CLI shortcut for approving a new name with expired evidence. A subsequent
decision to select or change identity requires fresh collection and human review.

## Roles

- A coordinator generates candidates and runs the public collector.
- A named human reviews general-web/common-law results and the official USPTO
  federal trademark search. Human-reviewed entries carry
  `reviewer_kind: human`; a model may assist but may not be named as the human
  reviewer or invent a clear result for an unavailable source.
- The Owner accepts or rejects the exact candidate after reviewing the ledger.
- The offline checker verifies completeness, freshness, evidence digests,
  classifications, and the Owner's recorded disposition.

## Collect

From the repository root:

```text
python -B scripts/collect_name_clearance.py \
  --candidate "Candidate Name" \
  --output candidate-name.json \
  --network
```

The standard-library collector executes every declared exact and similar query
and binds each one to digested request evidence. It queries:

- GitHub repository and organization names;
- exact and similar PyPI, npm, and crates.io package identities or searches;
- exact and similar `.com` identities through Verisign RDAP; and
- two deliberately incomplete human-review entries for common-law web use and
  the official USPTO search.

Network failure, rate limiting, malformed or structurally unexpected
successful JSON, or a source the collector cannot inspect becomes
`unavailable`, never `clear`. Search
endpoints require HTTP 200; only identity/domain lookup endpoints may treat
HTTP 404 as evidence that the exact lookup is unoccupied. `--no-network`
creates the complete schema with every source unavailable so an offline user
can inspect the contract without manufacturing evidence.

## Review the two human sources

For general web/common-law use, record the exact name, spaced and hyphenated
variants, and combinations with `software`, `AI`, `agent`, and the product's
category. Preserve the search terms, source URL, UTC time, reviewer name,
bounded findings, and a digest of the structured evidence. The canonical web
source URL is derived from the candidate display name and slug; relabeling a
different page as the reviewed endpoint fails the checker.
The structured evidence records a nonnegative result count, nonempty notes,
the exact reviewed queries, and its own UTC `reviewed_at`. A `clear` source has
zero reviewed results; a source with reviewed results is retained as a
`finding` even when every retained result is later classified unrelated.

For federal marks, use the [official USPTO search](https://tmsearch.uspto.gov/)
and follow the USPTO's exact, expanded, and alternative-spelling search
guidance. Record live and dead results separately and classify goods/services
overlap. The ledger must retain the canonical USPTO search endpoint and the
human evidence's own `reviewed_at` timestamp. Federal search is only one part
of a comprehensive clearance search.

Every finding is classified as `same`, `adjacent`, `unrelated`, or
`unreviewed`. An accepted candidate may contain no unreviewed finding. An exact
same-category prior use blocks acceptance by default. A rejected candidate may
stop after a real blocker is classified; remaining hits may stay unreviewed
because they cannot make the rejected candidate safer.

## Decide and check

After the latest source evidence is collected, the Owner records `accept` or
`reject`, their identity, UTC decision time, and rationale in `disposition`.
The decision timestamp must be strictly later than both automated collection
and human-review evidence. Candidate variants may only be the canonical
identity or a meaningful prefix of it, and the canonical identity itself must
remain present. Automated queries must begin with the canonical name at a word
boundary; human queries must contain the canonical name or an explicitly
declared bounded variant. A ledger cannot invent an extended alias or embedded
look-alike name to make unrelated queries appear in scope. Similar-name plans
must cover `AI`, `software`, and `agent` category variations; USPTO review must
include an alternative spelling. For every declared query,
GitHub requires repository and organization searches, npm and crates.io
require exact lookup plus search, PyPI requires exact lookup, and `.com`
requires RDAP lookup.
Then run:

```text
python -B checks/check_name_clearance.py candidate-name.json
```

The checker is offline. It fails on a missing, duplicate, malformed, or
unavailable required source; unknown modes, statuses, or request kinds; a
candidate identity absent from any declared query;
unsuccessful endpoint responses; expired evidence; malformed or mismatched
evidence digests; a declared query without matching digested request or review
evidence; unreviewed findings on an accepted name; blocking same-category
collisions; or a missing Owner disposition. `expires_at` may be no later than
seven days after `collected_at`; collection, source, review, and decision times
must be UTC, cannot be materially future-dated, and must preserve their strict
order inside that window. Every source explicitly retains a findings list, and
the ledger retains a negative legal-clearance limitation. Rerun rather than
extending timestamps by hand.

## What proof means here

The ledger retains exact queries, source URLs, timestamps, HTTP status and body
digests for automated requests, structured notes and digests for human review,
findings, classifications, and the Owner decision. A third party can rerun the
collector and compare the record. Search results can change, indexes can omit
uses, and a digest is not the response body. Those limits belong in the record,
not in fine print after launch.

The first worked example is the project's own missed-name incident:
[name-clearance incident, August 2026](../examples/name-clearance-incident-2026-08.md).
