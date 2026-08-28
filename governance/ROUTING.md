# ROUTING — Plumbline

**Status: RATIFIED by the Owner (HLLMR) on 2026-08-16; current R.12, R.13,
and R.14 wording explicitly ratified on 2026-08-20 by DR-002.**

The routing map is a governed artifact, amended only by ratification (Doctrine 8.2.3). It is part of the trusted control surface: an agent that complies perfectly with an incomplete map has been given the wrong requirements, which is worse than having ignored them (8.2.2).

Maps declared governed paths to the material an agent must receive before touching them. **The agent never chooses what to read** (2.11). Where the tooling cannot inject routed material, the Dispatcher attaches the router's result into the work order (8.2.1).

Coverage is measured against **declared** governed paths and subsystems, not against every file in the repository (8.2.4). Assets, fixtures, configuration, and build output need no route unless declared here.

Route identifiers R.1 through R.11 were stable from the original ratification.
R.12 and R.13 were added afterward and were already present before WO-PL-014.
WO-PL-014 then granted an Implementer write access to this map and let it
materialize R.14 before a separately recorded ratification step. That sequence
contradicted the stated Owner-only procedure even though the Owner later
accepted the work. DR-002 preserves the sequence as a deviation and explicitly
ratifies the current content of R.12, R.13, and R.14 on 2026-08-20. Once
assigned, an identifier's number is never reused for a different route.

---

## Routes

| # | Governed path or subsystem | Required material |
|---|---|---|
| R.1 | `DOCTRINE.md` | The affected clauses; DC.1 through DC.4; the methodology decision log (`decisions/`); every standalone template and bundled copy derived from the affected appendix |
| R.2 | `templates/**` | The corresponding appendix in `DOCTRINE.md`; the template-consistency rules in `checks/check_distribution.py` |
| R.3 | `adapters/**` | Doctrine 8.0 and 8.3; `adapters/claude-code/README.md`; the canonical adapter; applicable provider documentation; `tests/test_wo_capability_wall.py`; recorded birth-test limitations |
| R.4 | `skills/**`, `init.sh`, `ADOPTING.md` | `ADOPTING.md`; Doctrine Part 6; the applicable migration guide; the bundle's own `references/` and `assets/`; skill-bundle consistency checks |
| R.5 | `migration-guides/**` | The DC.2 entries for both revisions; every canonical artifact the guide installs, transforms, or supersedes |
| R.6 | `checks/**`, `scripts/**`, release packaging | `README.md`; `ADOPTING.md`; the canonical repository layout; packaging tests; the release manifest; the governance packaging gate |
| R.7 | `README.md`, `examples/**` | The ratified Doctrine; current distribution contents; observed evidence. Positioning may summarize; it may not enlarge the claims |
| R.8 | `governance/**`, `CLAUDE.md` | Doctrine Parts 5 through 9; this repository's ratified decisions; `SELF-HOSTING.md`. These records govern Plumbline itself and are not adoption templates |
| R.9 | `archive/**` | `archive/README.md` and the work order's explicit historical question. Archived material is evidence only; retrieval requires explicit Owner authorization recorded in the work order or an RFI resolution (8.6.2) (private governed-source reference, not present in this candidate) |
| **R.10** | **`.claude/**`** | Doctrine 8.3; `adapters/claude-code/README.md`; the canonical adapter; applicable provider documentation; installation and birth-test evidence; the active work order's enforcement declarations |
| **R.11** | **`decisions/**`** | Doctrine DC.3 and DC.4; `decisions/README.md`; the relevant existing methodology decisions; the ratified `PLAN.md` sections governing the proposed decision; the evidence and alternatives named by the active work order |
| **R.12** | **`SELF-HOSTING.md`** | Doctrine 5.1, Part 6, and Part 9; root `decisions/DR-001.md`; `governance/PLAN.md`; the adoption record and current observed state |
| **R.14** | **`checks/check_work_order_dispatch.py`, `tests/test_check_work_order_dispatch.py`** | Doctrine 8.2.5 and `SELF-HOSTING.md` "Pre-dispatch validation." **Dispatch-preparation scope only** — this checker is read-only tooling run before an Implementer session is launched; it is not part of `.claude/hooks/wo_capability_wall.py` and is never a runtime enforcement surface. Resolved RFI-25/27/28 records are provenance in governed history, not routed ordinary context |
| **R.15** | **`PUBLICATION.md`, `projection/**`, `scripts/build_public_projection.py`, `checks/check_public_projection.py`, `tests/test_public_projection.py`** | `governance/PLAN.md` post-pilot sequence; DR-003; `LICENSE-MAP.md`; current source/distribution/license gates; the Owner-controlled private pattern input supplied only at execution; the active projection work order. Projection work may derive and verify an external candidate but never authorizes publication, Git initialization, remote configuration, or visibility change |
| R.13 | Unmapped and unsure | **RFI.** Do not proceed on an inferred route |

**R.14 and R.15 sit above R.13 in this table despite being numbered after it.**
R.13, the unmapped fallback, stays the table's structurally last row by
convention regardless of numeric order, so that "last row" and "fallback
route" remain the same thing for a reader scanning the table.
R.14 and R.15 were appended following the R.12/R.13 amendment pattern noted
above; neither renumbers R.13 or changes R.13's meaning or position.

### R.11 note on authority

Agents may **draft** methodology decisions only when a work order grants it. **Only the Owner ratifies them** (2.7, 7.9.1). Receiving the routed material for `decisions/**` confers drafting context, never authority.

The same authority distinction applies to this map. An agent may draft proposed
routing text elsewhere under an explicit grant. Exact text may be materialized
here only after Owner ratification, by the Owner or an explicitly authorized
transcriber. Delegating the keystrokes does not delegate the decision.

### R.1 and R.10 note on the doctrine itself

R.1 routes `DOCTRINE.md` to methodology-maintenance work. Doctrine 1.2.3 and 1.2.4 permit exactly that and nothing more: it is never injected, never standing context, and never routed to an agent doing ordinary governed-project work. If this repository ever hosts non-methodology work, R.1 must be narrowed before that work begins.

---

## Route coverage cross-check

Every Tier-2 row in `governance/ADOPTION-MAPPING.md` cites a route identifier that exists above, and every route above points at material that mapping recognizes. Checked at ratification, 2026-08-16.

| Mapping row | Route |
|---|---|
| `DOCTRINE.md` | R.1 |
| `templates/**` | R.2 |
| `adapters/claude-code/README.md`, `wo_capability_wall.py` | R.3, R.10 |
| `ADOPTING.md`, `skills/plumbline-adopt/**`, `init.sh` | R.4 |
| `migration-guides/0.1-to-0.6.md` | R.5 |
| `checks/check_distribution.py`, `scripts/build_distribution.py` | R.6 |
| `decisions/DR-001.md`, `decisions/README.md`, `decisions/LICENSING-DIRECTION.md`, `governance/decisions/**` | R.6 for packaging concerns, **R.11** for decision drafting |
| `README.md`, `examples/README.md` | R.7 |
| `governance/**`, `CLAUDE.md` | R.8 |
| `archive/README.md`, `archive/proposed-v0.1/**` | R.9 (private governed-source reference, not present in this candidate) |
| `.claude/**` | R.10 |
| `SELF-HOSTING.md` | R.12 |
| `checks/check_work_order_dispatch.py`, `tests/test_check_work_order_dispatch.py` | R.14 |
| `PUBLICATION.md`, `projection/**`, projection builder/checker/tests | R.15 |

No mapping row cites a route that does not exist here, and no textual route name is left dangling.

**R.8 is not an orphan.** It governs `governance/**` and `CLAUDE.md`, whose mapping rows are dispositioned Charter, Plan, or Derived rather than Tier-2, so they carry no entry in the mapping's "If Tier-2: route" column. The route still applies when those paths are touched. R.15 governs publication-boundary tooling added after the adoption mapping; the active work order supplies the bounded authority and this route supplies ordinary context. R.13 is the unmapped fallback and is cited by nothing by definition.

## Deterministic checks (8.2.5)

Two checks run against this map. Both are currently **manual**, and that is a gap named rather than hidden.

1. **Unmapped governed paths.** Every path declared above must resolve to at least one required document that exists. A declared path with no valid route is a routing gap, counted under 9.2.5 at work-order activation.
2. **Orphan documents.** A Tier-2 document to which no route points is an archive candidate (8.6.1), counted separately from routing gaps.

Coverage gaps discovered during a work order are RFIs, and their remedy is a routing amendment the Owner ratifies — never a silent edit by the agent that tripped over the gap (8.2.5).

## Known limitation at ratification

**No mechanical enforcement of routing exists.** No hook resolves these routes and injects the result; the capability wall covers grants, not routing. Until such a hook exists, R.1 through R.15 are honored by Dispatcher attachment (8.2.1) and by instruction — which 8.2.2 identifies as the weaker half of the control surface. This is an unenforced control, declared as such, and it is a candidate finding for the pilot.
