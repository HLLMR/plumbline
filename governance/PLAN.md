# PLAN — Plumbline

**Status: RATIFIED by the Owner (HLLMR) on 2026-08-16**, for the self-adoption and 10-work-order pilot.

Scope: the **repository-development role**. Root `decisions/DR-001.md` is Plan for the distinct **methodology-source role** and ratifies Doctrine 0.6. The two do not overlap (adoption mapping, 2026-08-16).

This is should-be. As-is lives in `STATE.md`. The difference between them is drift (Doctrine 3.2.2). Amended only by ratification (7.9.1).

---

## 1. What this project is

Plumbline is a document-controlled governance methodology with a self-hosting reference implementation and project-scaffolding toolkit.

Three roles are held apart deliberately: `DOCTRINE.md` is the methodology; this repository is its distribution and reference implementation; a project-local instantiation is a governance system (5.1.2, 5.1.4).

## 2. Ratified intent inherited from the methodology decision

From `decisions/DR-001.md` (2026-08-16):

- Doctrine revision 0.6 is the first authoritative revision of the methodology.
- Revision 0.1 was a proposal only and is not a prior ratified revision.
- Ratification does not represent the methodology as empirically proven, complete, or final. It establishes the baseline needed to run governed pilots, collect real examples, measure failures and recovery costs under Part 9, and revise from evidence.

That third clause is this project's purpose in the Owner's own words.

## 3. Current phase

**Public-gate remediation before the Owner publication decision.** The repository has been governed by
Doctrine 0.6 since adoption commit
`8d5b2b3668ef626525e57028ac09661e17d44edc` (6.1.1). Self-adoption and all ten
counted maintenance work orders are complete. The Doctrine 9.3.1 fresh-agent
evaluation is complete and the Owner ratified `governance/decisions/DR-002.md`:
retain 0.6 provisionally. WO-PL-017 repaired the accepted blocking findings and
closed after fresh review. The Owner completed the licensing preconditions and
ratified DR-003; WO-PL-018 completed the disclosure and license-record boundary.
WO-PL-019 completed license mechanization and distribution integration after
fresh review and Owner disposition. WO-PL-020 completed the checked,
positive-allowlist clean-history projection gate after ACCEPT/HIGH fresh review
and Owner disposition. WO-PL-021 completed the Owner-ratified Doctrine 0.7
template/validator-alignment package after final Reviewer return and Owner
acceptance on 2026-08-21. Plumbline's repository-local governance instance
remains bound to Doctrine 0.6. WO-PL-022 completed the public projection
documentation-truth gate after final Reviewer ACCEPT/HIGH and Owner acceptance
on 2026-08-21. No publication, public Git repository, or visibility change has
occurred.

Owner amendment, 2026-08-20: the Owner ratified the Doctrine 0.7
template/validator-alignment package and queued WO-PL-021 followed by
WO-PL-022. These are blocking public-gate remediations. They do not authorize
publication, a public repository, a visibility change, a tag, a push, a
checked-in `dist/` replacement, or access to another project.

Owner amendment, 2026-08-18: this section was corrected after WO-PL-007 exposed
that its pre-adoption wording had remained in a routed authority after adoption.
The amendment changes current phase only; the pilot objective and evaluation
boundary below are unchanged.

## 4. Pilot subject

**The 10-work-order pilot runs on Plumbline itself.**

One adopting project is **not part of this pilot**. It separately adopted
Plumbline under its own Owner decision, adoption boundary, governance records,
metrics, and fresh-agent evaluation. None of those measurements count toward
Plumbline's 10-work-order pilot.

Owner amendment, 2026-08-19: that project's completed fresh-agent evaluation
identified a generic distribution defect relevant to every adopter that
protects a private read surface: the work-order template declares
`filesystem.read.deny`, while the Claude Code adapter then passed file-reading
tools through and did not enforce that declaration. The Owner authorized one
bounded, test-first Plumbline maintenance order to add and birth-test the
generic capability before the adopter installed it. This was genuine adapter
maintenance, not pooled pilot evidence or product work in the adopter. All
repository metrics remain separate.

**Evidence is never combined across repositories.** A measurement taken in one governed project says nothing about another, and pooling them would manufacture a sample that does not exist.

## 5. Phase target

The current phase completes when all seven are done, in order:

1. Complete Plumbline self-adoption.
2. Execute 10 genuine counted maintenance work orders.
3. Collect Part 9 measurements and evidence-backed examples.
4. Perform the fresh-agent pilot evaluation (9.3.1).
5. Decide whether to retain 0.6, amend the Doctrine, or retire a failed control.
6. Decide licensing.
7. Publish, only when the evidence and licensing gates are both satisfied.

**Revision 0.6 is not "done" merely because adoption succeeds.** Its evaluation boundary is completion of the 10-work-order pilot and the resulting Owner disposition. Adoption is the start of the measurement, not the result.

The boundary was reached on 2026-08-20. The evaluation falsified the one-cycle
recovery-cost prediction, preserved the no-archaeology result, and found that
the strict mechanically-enforced-surface stop rule had no domain during the
pilot. These are retained findings under 9.3.2, not retroactive edits to the
experiment. DR-002 governs the post-pilot disposition.

Step 2 says *genuine* maintenance work orders. Work invented to exercise the methodology is not evidence about the methodology (6.1.4, 3.2.7).

## 6. Falsification and stop rules

The doctrine makes falsifiable claims (9.1.1). These are the conditions under which this project stops rather than continues.

**Pilot pauses immediately when:**

1. **Any successful out-of-grant mutation occurs through a surface represented as mechanically enforced.** The pilot pauses until that surface is either reclassified as unenforced-by-declaration or fixed and birth-tested again. A wall that lets something through was never a wall for that channel (8.3.3, 8.3.4).
2. **Ratified intent changes without explicit Owner ratification.** The affected work is invalidated and the pilot pauses. Authority has a chain of custody or it has nothing (3.2.5, 7.9.1).
3. **An ordinary agent receives archived authority without the explicit authorization Doctrine 8.6.2 requires.** That is a control failure, not an inconvenience, and it pauses the pilot.

**Recorded, not concealed:**

4. A failed prediction is recorded as a finding. It causes revision rather than concealment (9.3.2). A prediction that fails and is quietly dropped would make the whole exercise ceremonial.

**Grounds for retirement:**

5. **Repetition of the same core control failure after one explicitly corrective revision** is grounds for the Owner to retire that control, or the methodology, rather than continue ceremonial compliance. One failure is a finding; the same failure twice after a fix aimed at it is evidence the control does not work.

## 7. Build only what evidence forces

There is no `plumbline validate`, no `plumbline diff`, no dashboard, and no multi-provider enforcement system. Each is worth building only if pilot data shows the manual version costs more than the tool would. Ratification explicitly rejected waiting for a platform (`decisions/DR-001.md`, rejected alternative 3).

The `filesystem.read.deny` adapter capability authorized above is not a new
platform or provider layer. It closes a mismatch between an already-distributed
grant field and the adapter's actual coverage, using the existing hook and
provider tool inventory. Shell-mediated reads remain unenforced unless the work
order denies shell execution; documentation and birth tests must state that
boundary exactly.

## 8. Standing constraints

Restated because `PLAN.md` is the authority a work order is checked against.

- The kill list in `CLAUDE.md` A.1.4 binds, in full.
- No adoption route may carry this repository's own governance records into an adopting project (5.1.5).
- The distribution archive is a source distribution, not an overlay.
- The finalized governance instance ships in the source distribution; unratified governance drafts never do, and a build fails rather than ship a partially adopted state (Owner disposition, 2026-08-16).
- Enforcement claims must match observed behavior. A provider gap is recorded, never described as a wall (8.3.4).
- Templates and bundled copies never drift from their canonical sources; this is checked, not assumed.
- Bootstrap work orders and remediation reports are pre-adoption evidence. They are never represented as counted or retroactively governed, and are not moved into live `governance/history/`.
- No agent ratifies intent, signs a decision, or changes an adoption boundary.

## 9. Owner-queued successor sequence — 2026-08-19

This section queues work; it activates nothing. Every work order still requires
an issue-time baseline, complete machine-readable manifest, pointer, applicable
provider-envelope wall proof, and separate Owner dispatch. A provider that
cannot be governed by the installed wall records that gap rather than simulating
a canary. The phase order in section 5 is unchanged.

1. **WO-PL-014 — COMPLETE, accepted 2026-08-20.** The deterministic
   pre-dispatch validator consolidated the three
   separately retained findings routed through RFI-25, RFI-27, and RFI-28. The
   validator is justified only if its bounded design catches pointer identity,
   line endings, grant/frontmatter consistency, residue, and issue-time path
   validity more cheaply than the manual dispatch corrections now recorded.
   Fresh review returned two implementation cycles before ACCEPT/HIGH closeout.
   RFI-25, RFI-27, and RFI-28 are resolved separately under bounded residuals.
2. **WO-PL-015 — COMPLETE, accepted 2026-08-20.** Source, builder, and archive
   modes now refuse an activation pointer or any regular file in the two live
   work directories before release output. Fresh review returned three
   correction cycles before ACCEPT/HIGH; final Windows and Ubuntu suites each
   passed 356 tests. **WO-PL-016 remains evidence-selected maintenance.** Use
   the final counted pilot position only for genuine maintenance taught by the
   repository's observed operation; do not invent work merely to complete the
   count.
3. **WO-PL-016 — COMPLETE, accepted 2026-08-20.** The portable adopter
   pre-dispatch validator now travels through both supported adoption routes,
   create-only and byte-identical, with generic identifier support and bundle
   gates. Fresh review required three correction cycles; final Windows and
   Ubuntu suites each passed 372 tests. This completes the ten counted work
   orders.
4. **Pilot evaluation and Owner disposition — COMPLETE, 2026-08-20.** The
   fresh Opus evaluation and Codex verification informed ratified DR-002.
   Doctrine 0.6 is retained provisionally; no control is retired; the adverse
   findings are publication obligations rather than hidden cleanup.
5. **WO-PL-017 — COMPLETE, accepted 2026-08-20.** Complete Appendix B manifests
   now fail closed; current derived records and routing materialization are
   corrected; prospective cost and Reviewer-independence rules are recorded.
   Fresh review required two correction returns before ACCEPT/HIGH. This is
   post-pilot work and adds no counted row.
6. **Owner licensing preconditions.** Outside the repository, confirm chain of
   title and obtain any desired employment, license, or naming review. Then the
   Owner may ratify a Plumbline-only licensing decision. A draft decision is not
   authority and is not stored in the packageable source tree.
7. **WO-PL-018 — COMPLETE, accepted 2026-08-20.** Applied the
   Owner-controlled private disclosure manifest to the live files eligible for
   public projection, place canonical unmodified license texts, and create the
   human-readable license, naming, contribution, and bundle maps. Sensitive
   matched text and second-project internals never enter a work order, report,
   decision, log, or commit message.
8. **WO-PL-019 — COMPLETE, accepted 2026-08-20.** Added SPDX/REUSE metadata,
   a standard-library license checker, tests, and distribution-gate
   integration. Fresh review ended CONDITIONAL ACCEPT/HIGH; the Owner accepted
   the disclosed deviations and required the deferred post-closeout archive
   gate to pass before the local closeout commit.
9. **WO-PL-020 — COMPLETE, accepted 2026-08-20.** Built and verified a
   positive-allowlist release candidate outside this repository. The candidate
   contains no inherited Git objects, private governance history, pre-adoption
   archive, stale distribution artifact, or private disclosure manifest. Fresh
   review ended ACCEPT/HIGH; the Owner accepted four disclosed deviations.
10. **WO-PL-021 — COMPLETE, accepted 2026-08-21.** Materialized the
    Owner-ratified Doctrine 0.7 Appendix B alignment: declared grant surfaces
    are classified, generated boundaries and the adopter workflow are present,
    canonical and bundled copies agree, the 0.6-to-0.7 migration guide exists,
    and the amended Windows, Ubuntu, distribution, license, projection, and
    fresh-review gates passed. Plumbline's repository-local governance instance
    remains bound to Doctrine 0.6 unless the Owner separately ratifies a
    project-side migration under DC.4.
11. **WO-PL-022 — COMPLETE, accepted 2026-08-21.** Corrected the public
    projection's repository-inventory and evidence-scope claims; foregrounded
    that WO-PL-017 through WO-PL-020 ran on Codex outside the Claude hook and
    were instruction-bounded; preserved legitimate normative adopter-path
    language; added a public-safe Plumbline self-hosting pilot example using
    only Plumbline's aggregate evidence; made the documentation-truth rule
    executable; passed full Windows and two real native-Ubuntu candidate
    suites; obtained final Reviewer ACCEPT/HIGH; and recorded 12 actual Owner
    active minutes.
12. **Owner publication decision.** Publication uses a new public repository
   with a fresh root commit derived from the accepted projection. This governed
   evidence repository remains private; changing its visibility is not the
   publication mechanism.

The durable private drafts retain their old proposal identifiers until they are
reconciled before issue. They are not authority, are not imported into this
repository, and WO-PL-017 does not open them.

The checked-in `dist/` archive is not a publication candidate. It remains stale
and private until the disclosure, licensing, mechanization, and projection
gates above have all passed. No queued item changes repository visibility,
publishes, pushes, or selects a license by itself.

## 10. Owner-ratified public-gate remediation sequence — 2026-08-21

Owner disposition, 2026-08-21: the Owner approved the following three bounded
work orders and authorized Doctrine 0.8 drafting under WO-PL-023. This
amendment records that disposition; it does not ratify Doctrine 0.8 text in
advance. The exact candidate revision returns to the Owner for a separate
ratification decision before any normative adapter implementation depends on
it.

1. **WO-PL-023 — Doctrine 0.8 and adopter contract.** Prepare an
   Owner-ratifiable Doctrine revision and methodology decision resolving the
   Appendix A enforcement overclaim, duplicate Appendix B numbering, adoption
   footprint conflict, bootstrap-work-order conflict, and protected
   control-plane semantics. Repair the adopter instructions, canonical birth
   test, pointer and prose-exception documentation, route-footprint claims,
   templates, skill assets, repository inventory, and public-projection
   retained-reference integrity. Ratified Doctrine 0.7 is not silently edited
   in place: candidate semantics return to the Owner first.
2. **WO-PL-024 — Capability-wall hardening and portability.** After the
   Doctrine 0.8 semantics are ratified, implement the protected control-plane
   floor; require ACTIVE lifecycle status; reject root-resolving or
   symlink-widened grants; establish parser equivalence or a shared
   deterministic contract; classify network tools truthfully; provide
   platform-aware startup, preflight, and timeout behavior; declare supported
   Python versions; repair the Windows test harness; add CI; run fresh Windows
   and native-POSIX birth tests; and resolve or dispose RFI-22.
3. **WO-PL-025 — Verification-only public release candidate.** Make no feature
   changes. Build reproducible clean projections; run the retained-reference,
   distribution, license, Windows, native-Ubuntu, and cold end-to-end adoption
   gates; obtain a fresh independent review; and return a separate Owner
   publication decision.

This sequence does not authorize publication, a public repository, a push, a
tag, a visibility change, replacement of checked-in `dist/`, or publication of
this governed source repository. A future public release, if separately
authorized after WO-PL-025, uses a clean projection in a new repository with a
fresh root commit.

## 11. Owner-ratified sequencing correction — 2026-08-21

This section supersedes only the uncompleted identifiers and sequence in
section 10; it preserves WO-PL-023 and the original queue as historical intent.
WO-PL-024 was prematurely activated under this project's still-operative 0.6
binding, received no implementation or test work, and was disposed **VOID
BEFORE IMPLEMENTATION**. Its identifier is consumed permanently and is not
reused.

The remaining queue is:

1. **WO-PL-025 — Project-local migration from Doctrine 0.6 directly to 0.8.**
   Prepare one cumulative DC.4 migration decision naming both revisions and
   every affected project artifact; incorporate the 0.6-to-0.7 and 0.7-to-0.8
   transitions without representing 0.7 as a separately active project
   binding; return the exact decision and work order for Owner ratification;
   and only after ratification materialize and verify the project-local
   charter, templates, binding record, dispatch contract, and observed State.
2. **WO-PL-026 — Capability-wall hardening and portability.** Perform the
   scope formerly queued as WO-PL-024: implement the protected control-plane
   floor; require ACTIVE lifecycle status; reject root-resolving or
   symlink-widened grants; establish parser equivalence or a shared
   deterministic contract; classify network tools truthfully; provide
   platform-aware startup, preflight, and timeout behavior; declare supported
   Python versions; repair the Windows test harness; add CI; run fresh Windows
   and native-POSIX birth tests; and resolve or dispose RFI-22.
3. **WO-PL-027 — Verification-only public release candidate.** Perform the
   scope formerly queued as WO-PL-025 without feature changes: build
   reproducible clean projections; run retained-reference, distribution,
   license, Windows, native-Ubuntu, and cold end-to-end adoption gates; obtain
   fresh independent review; and return a separate Owner publication decision.

This correction authorizes recovery accounting and preparation of the exact
WO-PL-025 migration package for Owner ratification. It does not ratify that
migration package in advance, activate or implement WO-PL-025, implement wall
hardening, activate WO-PL-026 or WO-PL-027, publish, replace `dist/`, tag, or
change repository visibility.

## 12. Owner-ratified post-publication polish — 2026-08-28

Plumbline 0.8 is publicly released from the accepted clean-history projection.
The Owner authorizes one concentrated front-door polish order, WO-PL-034, to
add an original README banner, concise GitHub status/navigation chrome, and a
short evidence-backed mechanism demonstration; carry the asset through the
existing license and projection machinery; and correct the private State's
observed publication status. This work may improve presentation and access to
existing evidence, but it may not enlarge enforcement, effectiveness, pilot,
provider, or operating-cost claims or revise Doctrine 0.8.

## 13. Owner-ratified first-adopter repair — 2026-08-28

The Owner authorized WO-PL-035 after the first clean public adoption exposed a
human-ramp defect: the wall locked down correctly, but the novice did not have
an executable coordinator-first path. WO-PL-035 is complete and accepted. It
delivered a human-first start page, exact prompts, safe lockout and overlay
recovery, external-fixture boundaries, and a public issue-to-PR workflow.

## 14. Owner-ratified naming correction and public case study — 2026-08-28

The Owner directs an emergency pre-promotion naming tranche after discovering
that the public release had never passed an inception name-clearance gate and
that earlier same-category and adjacent AI-agent tools already use `Plumbline`
or `plumb`. Tuesday promotion is frozen until this tranche is complete.

1. **WO-PL-036 — Name-clearance evidence and replacement selection.** Build a
   small deterministic collector/checker contract that records exact queries,
   source availability, timestamps, response evidence, category overlap, and
   Owner disposition across GitHub, major package registries, domain/RDAP,
   common-law web use, and federal trademark records. Use the incident and
   rejected replacement candidates as public evidence. Automated output is not
   a legal opinion. Return a short screened candidate set and one recommendation
   for Owner ratification.
2. **WO-PL-037 — Controlled identity migration.** Only after the Owner ratifies
   a replacement, migrate current product, documentation, code identifiers,
   package/repository references, public assets, launch copy, and release
   surfaces. Preserve old names in historical records and explicit provenance;
   do not rewrite history or imply the replacement name existed earlier.

The current public repository and release remain available as evidence, but no
new promotion, Show HN submission, replacement release, tag, or mass rebrand is
authorized before WO-PL-036 produces and the Owner ratifies the replacement
disposition. Public issue #2 is the durable public defect record.

## 15. Owner-ratified first-use and identity follow-through — 2026-08-29

The Owner accepted **Writwall** as the canonical identity, directed retirement
of the inherited plumb-line device in favor of the already-developed two-line
wall glyph, and confirmed that an IDE coding agent is a valid day-zero entry
point before the wall is registered. The first public adoption showed that the
role architecture exists but the invocation contract still fails when the wall
is installed before its bootstrap bundle and local handoff are available.

1. **WO-PL-038 — Wall-glyph identity correction.** Replace the current-use
   plumb-line device in public README/social assets with the two-line wall at
   the `writ|wall` boundary. Preserve explicit historical evidence; do not
   rewrite accepted records. Verify generated raster siblings, projection and
   license gates, and finish public issue #2 through the ordinary projection
   and pull-request path after acceptance.
2. **WO-PL-039 — Cache-safe public identity and repository hardening.**
   Correct the GitHub delivery failure recorded in public issue #4: publish
   the accepted README banner under a content-versioned path, prevent future
   current-use visual replacements from reusing a published URL, refresh the
   repository social preview, pin CI actions, establish one stable required
   check, and enable proportionate public-repository protections. This bounded
   correction precedes rather than expands the coordinator build.
3. **WO-PL-040 — Day-zero invocation and bootstrap handoff.** Make the
   IDE-first path executable from a clean repository: give the human one exact
   kickoff prompt; make the complete bootstrap bundle and a project-local
   handoff readable before wall registration; distinguish the temporary
   bootstrap coordinator from the post-adoption walled Operator; document the
   external infrastructure-operator boundary; and prove the path with a fresh
   clean-context walkthrough. Public issue #1 remains the durable defect
   record. The coordinator must explain and optionally time Owner active
   minutes: human reading, deciding, responding, authentication, and
   unavoidable UI work count; agent execution and waiting do not.

The Owner remains the source of intent and acceptance. The Owner-Agent may
draft, coordinate, record ratified decisions, and perform authorized lifecycle
mechanics. An IDE agent may serve as the bootstrap coordinator before
registration and later as the walled Operator, but those are sequential roles,
not simultaneous authority. An infrastructure agent that only changes DNS,
containers, hosts, or proxies is outside the repository's capability wall; it
receives a bounded external-operations packet and returns evidence. If it edits
repository bytes, it enters the repository as an Operator under a work order.

## 16. Writwall-native series and architect interview — 2026-08-29

The Owner corrected the post-migration identifier boundary before issuing the
next order. `WO-PL-001` through `WO-PL-040` remain immutable identifiers in the
historical Plumbline series. Current Writwall work begins at `WO-WW-001` and
increments within that series. No historical record is renamed or renumbered.

1. **WO-WW-001 — Architect interview and inception evidence.** Extend the
   accepted day-zero coordinator into the promised “I have an idea” front
   door. Qualify the idea before treating it as a project; capture the problem,
   intended user, value, evidence, constraints, risks, success and stop
   conditions; inventory the human/agent/operator environment; recommend the
   smallest credible role topology; and emit bounded setup packets. A public
   identity remains a working candidate until the existing evidenced
   name-clearance process and explicit Owner disposition complete. Name
   research therefore precedes repository/package/domain/logo/launch identity,
   not follows it. The deterministic CLI may collect, validate, package, and
   route intake; a frontier Owner-Agent performs the adaptive architect
   interview. It must not silently install extensions, modify IDE or host
   configuration, access credentials, mutate external systems, ratify intent,
   or begin implementation.

The minimum supported topology is one human Owner, one Owner-Agent, one or more
bounded Operators, and a fresh Reviewer. On small projects one capable agent
may perform coordinator, dispatcher, and recorder roles sequentially, but a
Reviewer remains a distinct fresh context and no agent receives simultaneous
unbounded authority. External infrastructure, DNS, mail, hosting, and similar
Operators receive inert packets; repository mutation remains work-order bound.
