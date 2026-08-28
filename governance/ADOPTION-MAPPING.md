# ADOPTION MAPPING

**Status: DISPOSED by the Owner (HLLMR) on 2026-08-16.**

Doctrine 6.3 requires every existing intent-bearing or reference document to be assigned exactly one disposition before the first counted work order. The implementing agent prepared the worksheet; the Owner disposed it. This file records the dispositions, not proposals.

Appendix E format. Dispositions: **Plan** (6.3.2), **Tier-2** with a route (6.3.3), **Charter** kill-list content (6.3.4), **Archive** (6.3.5).

A complication specific to this repository: it holds both repository roles (5.1.4). Most files here are **distribution artifacts** — the product — rather than governance records of the project that builds them. A distribution artifact is not automatically Tier-2 context for the agents maintaining it. Rows below distinguish the two, and where a file is both, the row says so.

---

## Owner dispositions of record

### Two Plan documents, two distinct scopes

`decisions/DR-001.md` and `governance/PLAN.md` are **both Plan, for distinct scopes**:

- root `decisions/DR-001.md` governs the **methodology-source role** and ratifies Doctrine 0.6;
- `governance/PLAN.md` governs the **repository-development role**.

They do not duplicate authority over the same scope, so Appendix E's prohibition on two Plan documents for one scope is not engaged. This is settled and is not an open question.

### `PLAN.md` was correctly written fresh

No prior master plan or equivalent controlling document existed to materialize or archive, so 6.3.2's materialize-and-archive path did not apply. `PLAN.md` properly consolidates the applicable intent from the ratified methodology decision, Owner directions, `README.md`, and `SELF-HOSTING.md`.

### Pre-adoption records stay pre-adoption

The bootstrap work orders (`bootstrap/WO-PL-001` through `WO-PL-004`) and the remediation reports are **pre-adoption evidence, not governed transactional history**. They are never represented as counted or retroactively governed (6.1.1).

They remain **outside the live corpus**, keep their existing package exclusions, and are **not** moved into live `governance/history/` at adoption. `governance/history/` is for transactional records produced under governance; these predate it.

---

## Rows

| Document | Disposition | If Tier-2: route | If Charter: extracted line(s) | Notes |
|---|---|---|---|---|
| `CLAUDE.md` | **Charter** | — | The whole file is the Tier-1 injectable | 5.2 permits the tooling's auto-loaded file to serve as the charter. Owner-authored. Layout adaptation recorded in the adoption record D.6 |
| `governance/PLAN.md` | **Plan** (repository-development scope) | — | — | Owner-ratified 2026-08-16 |
| `decisions/DR-001.md` | **Plan** (methodology-source scope) | R.11 | — | Ratifies Doctrine 0.6. Distinct scope from `PLAN.md`; see dispositions above |
| `DOCTRINE.md` | **Tier-2** | R.1 | — | The product *and* the specification for maintaining it. Routed only for methodology-maintenance work (1.2.3, 1.2.4). Never injected, never routed for ordinary project work |
| `README.md` | **Tier-2** | R.7 | — | Positioning. May summarize; may not enlarge claims |
| `ADOPTING.md` | **Tier-2** | R.4 | — | The adoption routes it documents change when those paths change |
| `SELF-HOSTING.md` | **Tier-2** | R.12 | — | This repository's own adoption sequence. A working record, not a distribution template |
| `decisions/README.md` | **Tier-2** | R.11 | — | States the two decision series are separate |
| `decisions/LICENSING-DIRECTION.md` | **Tier-2** | R.11 | — | Superseded nonbinding direction, retained as history. RFI-03 resolved by DR-003 |
| `governance/ROUTING.md` | Governed artifact | — | — | Owner-ratified 2026-08-16. Amended only by ratification (8.2.3) |
| `governance/STATE.md` | Derived | — | — | Rebuilt on deterministic triggers (7.8.1). Never ratified; it is measurement, not intent |
| `governance/LOG.md` | Derived | — | — | Part 9 metrics. No rows until the pilot begins |
| `governance/decisions/**` | Project decisions | R.11 | — | Project-side series, separate from root `decisions/` (5.1.5) |
| `migration-guides/0.1-to-0.6.md` | **Tier-2** | R.5 | — | Companion for one revision transition |
| `adapters/claude-code/README.md` | **Tier-2** | R.3, R.10 | — | The maintained operational statement of what the wall does and does not enforce |
| `adapters/claude-code/wo_capability_wall.py` | **Tier-2** | R.3, R.10 | — | The canonical adapter |
| `templates/A-charter.md` … `E-adoption-mapping.md` | **Tier-2** | R.2 | — | Distribution artifacts extracted verbatim from Doctrine appendices; routed with `DOCTRINE.md` because they must change together |
| `skills/plumbline-adopt/**` | **Tier-2** | R.4 | — | Self-contained bootstrap bundle; bundled copies checked byte-for-byte against canonical sources |
| `checks/check_distribution.py` | **Tier-2** | R.6 | — | Part of the trusted control surface |
| `scripts/build_distribution.py` | **Tier-2** | R.6 | — | Source-distribution builder |
| `init.sh` | **Tier-2** | R.4 | — | Scaffolder, an adoption route |
| `.claude/**` | Governed path | R.10 | — | Enforcement installation. Route added at Owner direction 2026-08-16 |
| `tests/**` | Not intent-bearing | — | — | Verification, not context. Read when changing the code they cover; no route declared (8.2.4) |
| `examples/README.md` | **Tier-2** | R.7 | — | States there is no example yet. Must not acquire a fictional one |
| `archive/README.md` | **Archive** | R.9 | — | Provenance record. Retrieval requires explicit Owner authorization (8.6.2) (private governed-source reference, not present in this candidate) |
| `archive/proposed-v0.1/**` | **Archive** | R.9 | — | v0.1 charter, playbook, proposal, templates. Never ratified. Outside the live corpus |
| `bootstrap/WO-PL-001` … `WO-PL-004` | **Pre-adoption evidence** | — | — | Not governed transactional history. Outside the live corpus; package-excluded; **not** moved to `governance/history/` |
| `REMEDIATION-REPORT*.md` | **Pre-adoption evidence** | — | — | Same disposition. Never edited to describe a later state |
| `.gitattributes`, `.gitignore` | Not intent-bearing | — | — | Configuration. No route (8.2.4) |
| `dist/**` | Not intent-bearing | — | — | Build output, gitignored |

---

## Rules check (Appendix E)

- **Every intent-bearing document lands in exactly one row.** Satisfied.
- **A Tier-2 row without a route is an Archive row.** Every Tier-2 row above carries a route identifier that exists in `governance/ROUTING.md`. Cross-checked at disposition; a later mismatch is a routing gap under 9.2.5 and an RFI.
- **Two documents may not both be Plan for the same scope.** Satisfied: the two Plan rows govern distinct scopes, per the Owner disposition above.
- **The completed worksheet is attached to the adoption record.** Referenced from D.6 of the adoption record.

## Not proposed, deliberately

No document is materialized into `PLAN.md` with the original archived (6.3.2): none existed to materialize. Confirmed correct by the Owner.

No historical decisions are backfilled (6.3.6). The only prior decision is the v0.1 proposal, never ratified, constraining nothing.
