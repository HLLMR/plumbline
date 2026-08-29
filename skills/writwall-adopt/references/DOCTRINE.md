# THE DOCTRINE
## Document-Controlled AI-Assisted Development

---

## DOCUMENT CONTROL

### DC.1 Identification

| Field | Value |
|---|---|
| Document | The Doctrine: Document-Controlled AI-Assisted Development |
| Revision | 0.8 |
| Status | Ratified |
| Amendment authority | The Owner of the methodology repository |
| Supersedes | 0.7 |
| Effective | 2026-08-21, ratified by DR-005 (`decisions/DR-005.md`) |

### DC.2 Revision History

| Rev | Date | Summary of change | Ratified |
|---|---|---|---|
| 0.1 | 2026-08 | Initial charter draft, pilot-specific | No |
| 0.2 | 2026-08 | Generalized for a software audience; definitions added; record architecture corrected to project-is-root; charter separated from doctrine | No |
| 0.3 | 2026-08 | Determinism classes; observed and interpreted state; routing governed as code; capability grants; brief escalation; tightened continuity claim; positioning | No |
| 0.4 | 2026-08 | Seven wording and control fixes from external review; enforcement-coverage metric | No |
| 0.5 | 2026-08 | Formal clause structure and change control; adoption procedure (Part 6); mutation-channel completeness (8.3); instrument circularity rule (8.4); human-voice rewrite | Returned |
| 0.6 | 2026-08 | Corrections from formal review: baseline versus adoption commit; two-level birth test; transactional record category; archive semantics; Dispatcher and Reviewer inputs; Owner disposition; control taxonomy; instrument qualification event; operational definitions moved to adoption record. Pre-ratification touch-ups: 2.18, 6.2.1.1, 7.6.1; bootstrap-agent exception and post-adoption role inputs (1.2.2-1.2.4); provider configuration at adoption (5.1.3); repository roles versus physical repositories, permitting a segregated self-hosted instance (5.1.1, 5.1.4-5.1.6); charter current-state updated by the Owner and never by agents (Appendix A A.3); qualification cross-references corrected to 8.4.4 (Appendix D D.5, 9.2.8); methodology-maintenance exception preserved after adoption (1.2.4); methodology repository described as distribution and reference implementation rather than documentation alone (5.1.2) | Yes |
| 0.7 | 2026-08 | Align Appendix B with the shipped pre-dispatch validator: classify every declared grant surface exactly once in `enforced_by` or `unenforced_boundaries`; default the provider-neutral template to no mechanically enforced whole surfaces; add generated-boundary markers and the checker-emission workflow. No other Doctrine clause changes. | Yes |
| 0.8 | 2026-08-21 | Corrected Appendix A's unqualified "blocked and logged" claim to be provider-contingent, matching this repository's own already-corrected charter; corrected Appendix B's B.4/B.7 numbering defect (see erratum below); added `governance/templates/` to the Part 5.2.1 reference layout with invariant 5.3.8 governing its refresh, and revised 5.1.3 to affirmatively require whatever deterministic dispatch-preparation tooling the revision's workflow needs (described generically, never naming a product) while stating plainly that a scaffolded skeleton without populated governance records, that tooling, and a ratified adoption record with the adoption commit containing it is not itself adoption; defined the birth-test instrument (2.28), narrowed to the active-scope, per-surface birth test only, and cross-referenced it from 6.1.3; and added Part 8.7, Protected Control Plane, governing mutation authority (not read-deny) over the active-work-order pointer, installed enforcement configuration, the active work order or instrument itself, and the denial-evidence log — unconditionally, with no exception for an Owner-authored grant — treating activation, retirement, recorder actions that themselves mutate a control-plane artifact, and the specifically defined adoption-recorder action as Owner lifecycle actions outside any capability grant while leaving ordinary Part 7 closeout governed and requiring durable pre-execution authorization; and defining a labeled `instrument_kind: birth-test` / `control_plane_probes` dispatch exception whose exact protected-path entries confer no authority and must still be denied by the runtime wall, with enforcement remaining provider-contingent and birth-test-gated (8.7.4), resolving RFI-22's Doctrine-level question without closing the RFI itself | Yes |

**Erratum, recorded 2026-08-21.** Revision 0.7's addition of "B.4 Generated
boundaries" collided with the pre-existing B.4 ("BOUNDARIES") identity
established since revision 0.5, in violation of DC.3.1 and DC.3.3. Revision
0.8 corrects this: B.4 is restored to its sole original identity, and the
generated-boundaries workflow is relocated to B.7, the lawful
next-available top-level letter in Appendix B at the time of 0.7's drafting.
No other content of 0.5 through 0.7 is altered by this correction.

### DC.3 Change Control Rules

DC.3.1 Clause identifiers are stable. A clause, once published in a ratified revision, keeps its number for the life of the document. Content may be amended in place; numbers are never reassigned.

DC.3.2 A withdrawn clause is marked "Reserved" with a pointer to the revision that withdrew it and, where applicable, the clause that replaces it. It is not deleted and its number is not reused.

DC.3.3 New material takes the next available number at its level. Insertions between existing clauses are not permitted; if ordering matters, the new clause states its logical position in its text.

DC.3.4 Every revision records, in DC.2, a one-line summary and its ratification status. Substantive changes are additionally logged in the methodology repository's decision log with reasoning and rejected alternatives, per the same rule the doctrine imposes on projects.

DC.3.5 A revision becomes authoritative only upon ratification by the amendment authority. Drafts and candidates carry no authority over projects that have adopted an earlier ratified revision.

DC.3.6 The doctrine imposes no schedule on its own revision. The amendment authority may revise at any time, for any reason, and is encouraged but not required to wait for pilot evidence before doing so.

### DC.4 Supersession and Project Binding

DC.4.1 A project binds to a specific ratified revision at adoption (Part 6). It remains bound to that revision until the project's Owner ratifies a decision record moving it to a later revision.

DC.4.2 Moving a project to a later revision is a change-controlled event. The decision record names both revisions and lists every project artifact affected by the difference.

DC.4.3 A superseded revision remains available in the methodology repository, marked superseded, for as long as any known project is bound to it.

---

## PART 1. PURPOSE AND SCOPE

### 1.1 Purpose

1.1.1 The doctrine is a governance methodology for building software with AI agents without losing control of intent, scope, or truth.

1.1.2 It addresses a failure pattern that is nearly universal in AI-assisted development. Work begins well, then diverges quietly from what was intended. The divergence is discovered late, reconstructed at great cost, and repeated. The doctrine holds that this failure is structural rather than behavioral, and that its remedy is also structural.

### 1.2 Audience

1.2.1 The doctrine is written for anyone directing AI agents to build software: individual developers delegating to coding agents, teams running multiple agents against a shared codebase, and organizations that need agent output to be trustworthy enough to ship.

1.2.2 The doctrine is written for humans. It is not standing context for the agents working on a governed project. Those agents receive a short, project-specific charter derived from it (Appendix A) together with mechanically routed excerpts of the project's own records. That separation is itself a rule of the doctrine (8.1).

1.2.3 One narrow exception exists. A bootstrap agent or a methodology-maintenance agent may receive this document as an implementation specification, under direct Owner supervision, before adoption or while working on the methodology repository itself. Such an agent is building or migrating the governance apparatus rather than executing project work under it. The exception is bounded by that purpose and does not make the doctrine project context.

1.2.4 After adoption, ordinary Dispatcher, Implementer, and Reviewer invocations do not receive this document as standing or routed project context. They receive the project charter, the work order and other open transactional records, the relevant plan sections, the Tier-2 material the routing map attaches, prior reports, and the output of any empirical instrument, as applicable to the role (7.2.1, 7.4.1, 7.6.1). The single exception is 1.2.3, which survives adoption: an invocation working specifically as a methodology-maintenance agent on the methodology repository may receive the affected clauses of this document as implementation material. That exception is bounded by that work and never reaches an agent performing ordinary governed-project work.

### 1.3 Scope

1.3.1 The doctrine governs the relationship between human intent, the project's canonical record, and the agents that act on both. It does not prescribe programming practice, architecture, or tooling beyond what is needed to make its controls real.

1.3.2 The doctrine assumes nothing about which models or products are used. It expects to sit on top of whatever enforcement primitives exist and to adapt to better ones as they appear.

---

## PART 2. DEFINITIONS

Terms are defined for use within the doctrine. Where a term has a wider industry meaning, the doctrine's meaning governs.

2.1 **AI-assisted development (AIAD).** Software development in which AI agents perform substantial implementation, analysis, or review work under human direction.

2.2 **Agent.** An LLM-based worker (coding agent, chat model, review model) operating within a session. The doctrine treats agents as having no trusted continuity across sessions and as degrading within them.

2.3 **Session.** One continuous agent conversation or run. Sessions are finite. The doctrine treats them as disposable processes and never as stores of truth.

2.4 **Context degradation.** The decline in an agent's effective attention and reliability as its context window fills. Degradation is a property of the technology rather than a defect to be instructed away. Compliance with any standing instruction is probabilistic per turn and decays with context pressure.

2.5 **Canonical record.** The set of version-controlled files that constitute the project's truth: intent, decisions, plan, state, work orders, reports, and their supporting artifacts. The record, not any agent or session or human memory, is the durable actor in an AIAD project.

2.6 **Intent.** What the Owner has ratified the project to be and to do. Intent exists only in the record and changes only by ratification.

2.7 **Ratification.** Explicit human approval of an intent-bearing artifact: charter, plan, decision record, routing map, or amendment to any of these. Agents may draft and propose. Only the Owner ratifies. An unratified proposal carries no authority however persuasive it is.

2.8 **Drift.** Divergence between layers that should agree. Execution drift is work that no longer matches its work order. Intent drift is a plan or task that no longer matches ratified intent. Documentation drift is a record that no longer matches the code. The doctrine's controls exist to make each kind detectable when it occurs and survivable when it does.

2.9 **Tier-1 and Tier-2 documents (standing context).** Tier-1 is the small set injected into every agent session automatically, under a hard token budget. Tier-2 is everything routed on demand. Together they are the standing context. A standing document that is neither injected nor routed is outside the live corpus and must be archived (8.6.2) rather than left in normal retrieval paths.

2.10 **Injection.** Forcing a document into an agent's context automatically at session start. Injection cannot be skipped by the agent. An instruction to go and read something can.

2.11 **Routing.** A deterministic mapping from what an agent is about to touch to the documents it must receive first. The agent never chooses what to read. The routing map is itself a governed artifact (8.2).

2.12 **Capability grant.** The explicit set of actions a work order authorizes, expressed as a manifest across surfaces such as filesystem paths, shell, network, secrets, version-control operations, and package installation (Appendix B).

2.13 **Capability wall.** The enforcement of a capability grant by mechanism (hooks, permission systems, sandboxes) rather than by instruction. A rule is complied with probabilistically. A wall is physics.

2.14 **Mutation channel.** Any means by which an agent can change the state of the repository, the environment, or an external system: file-edit tools, shell commands, subprocesses, version-control operations, network calls, package managers, and any tool that writes. A wall for a given surface must cover every mutation channel that can reach that surface (8.3.3).

2.15 **Fail closed.** When a control cannot verify that an action is permitted, the action is blocked. Ambiguity halts work. It never authorizes it.

2.16 **Work order (WO).** The unit of delegated work: a scoped, bounded, falsifiable task issued to an agent, carrying its own capability grant and acceptance criteria.

2.17 **Work report.** The implementing agent's structured account of what was done, addressed to the Reviewer and never to the Owner.

2.18 **Owner brief.** The Reviewer's distillation of a work report for the Owner: conformance verdict, decisions needed, risks, in owner language and within the Owner-load ceiling fixed by the project's adoption record (9.1.3), with mandatory escalation to evidence under the conditions of 7.6.3.

2.19 **Decision record (DR).** A dated record of one ratified decision: the decision, the reasoning, and the alternatives rejected. The reasoning is the load-bearing part. It is what allows a fresh agent or human to reconstruct the rationale instead of merely inheriting the conclusion. Knowledge transfers by reading. Authority does not.

2.20 **Request for information (RFI).** A formal halt-and-ask filed by any agent that encounters ambiguity, contradiction, or a need for authority it does not hold. Filing an RFI is mandatory behavior, not a courtesy.

2.21 **Conformance gate.** A blocking check that work matches its work order and the plan before it merges. The gate's blocking is deterministic. The judgment behind it may not be (8.0).

2.22 **Observed state and interpreted state.** Two classes of as-is knowledge with unequal epistemic status. Observed state is mechanically derived from the repository: commit, test results, dependency versions, open work orders, changed files. Interpreted state is model-produced synthesis, each claim tagged with its source.

2.23 **Empirical instrument.** A tool that independently tests an implementer's claim of completion against the task, rather than trusting the report. Where qualified, it occupies the hard slot in the conformance gate (8.4).

2.24 **Adoption.** The change-controlled event at which a project binds to a ratified revision of the doctrine (Part 6). History before adoption is pre-doctrine history and is never retroactively represented as governed.

2.25 **Baseline commit and adoption commit.** The baseline commit is the last wholly pre-doctrine state of the project, selected by the Owner and recorded by hash in the adoption record. The adoption commit is the commit that first contains the ratified adoption record and the completed bootstrap artifacts. Adoption is effective with the adoption commit, which is identified by its content and is not recorded by hash inside itself.

2.26 **Transactional record.** Work orders, work reports, owner briefs, RFIs, and similar artifacts produced by the workflow. Transactional records are neither Tier-1 nor Tier-2. While open they are supplied to agents by the workflow itself. When closed they leave the live agent-visible corpus and are retained as durable history (5.3.7, 8.6.3). Durable does not mean permanently contextual.

2.27 **Live corpus.** The set of documents an agent can receive through injection, routing, open transactional records, and the configured search and retrieval paths of the project. Archived and closed-historical material is outside it.

2.28 **Birth-test instrument.** A capability-grant-bearing artifact, sharing the work-order frontmatter and pointer-activation mechanism (Appendix B, 8.3.5) for engineering convenience, used only for the active-scope, per-surface birth test (8.3.5.2), where an Owner-directed test mechanically requires an active pointer and grant to exercise scoped enforcement. It is not a work order (2.16): it carries no Part 7 disposition cycle and is never counted under Part 9 (6.1.3). This does not forbid a Dispatcher-equivalent function from drafting one or a Reviewer-equivalent function from inspecting its outcome; the boundary that matters is that it never carries or ratifies intent (2.6-2.7) and never substitutes for a counted work order. Like any work order, its own capability grant is bound by 8.7.2 and never reaches a control-plane artifact — except that its manifest may name an exact control-plane path solely as a falsification probe under the schema at 8.7.4, which confers no authority under 8.7.2; it is validation metadata, never a grant. It is distinct from the no-work-order lockout (8.3.5.1), which is not an instrument at all: that test observes the absence of any active pointer, and its pass condition is precisely that nothing is active to grant anything. It is also distinct from an Owner lifecycle action (8.7.6), including the adoption-recorder lifecycle action: neither is ever performed under a birth-test instrument's or any work order's capability grant.

---

## PART 3. THESIS AND PRINCIPLES

### 3.1 The Thesis

3.1.1 AIAD failure is not a documentation problem. It is the combination of two conditions.

3.1.2 First, there is no durable integrator. The roles that hold a project together, the people who remember why, presume actors with continuity. Agents have none. Staffing those roles with agents produces confident amnesia.

3.1.3 Second, boundaries are soft. Humans respect role boundaries because of incentive, identity, and liability. Agents have none of these. Boundaries expressed as instructions are complied with probabilistically and fail silently.

3.1.4 Therefore the durable integrator is replaced by the canonical record plus deterministic mechanism, with a human as sole ratifier of intent, and role separation is enforced by capability restriction rather than instruction.

### 3.2 Principles

3.2.1 **Sessions are disposable; the record is not.** Any control that depends on a session surviving, or on an agent remembering, is invalid by definition.

3.2.2 **Plan and state are different documents.** The plan says what should be, as ratified. The state says what is, as derived from the code. Drift is the difference between them. Regenerating a plan from the code does not fix drift. It ratifies it.

3.2.3 **Reasoning is the asset.** Decisions recorded without reasoning and rejected alternatives transfer conclusions without the ability to judge new situations against them. A fresh reader of a well-kept decision log can reconstruct the architectural rationale. The reader does not thereby acquire authority, which never leaves the Owner, but does acquire the understanding needed to recognize when work violates it.

3.2.4 **Consumption is the constraint, not production.** Agents sample large document sets; they do not read them. A corpus grows until full ingestion is impossible, at which point partial ingestion, and the misses it guarantees, becomes certain. The doctrine budgets and routes what agents receive rather than trusting them to retrieve.

3.2.5 **Authority has a chain of custody.** An authoritative specification is necessary but not sufficient. Because the actor interpreting it is probabilistic and transient, who may change intent, by what procedure, and on what evidence must be defined as strictly as what the intent says.

3.2.6 **Zero drift is not the target.** Context degradation is real and uncured in present technology. The target is a change of ratio: drift caught in the same work order in which it occurs, and recovered at the cost of one revert.

3.2.7 **The methodology adapts to the project.** A project adopting the doctrine does not reshape its roadmap, priorities, or engineering practice to make the doctrine look good. Where governance makes the work worse, that is a finding about the doctrine, to be recorded, not a reason to alter the work.

---

## PART 4. ROLES

### 4.1 Roles as Functions

4.1.1 The doctrine defines roles as functions rather than as persistent processes or personas. Any function may be performed by any capable model. What matters is what each function receives, what it is permitted to do, and what it must produce.

4.1.2 There is no manager-agent, architect-agent, or orchestrator-agent. Continuity lives in the record. Enforcement lives in mechanism. Judgment about intent lives in the Owner. Every agent invocation begins from the record as if it had never seen the project, because it has not.

4.1.3 Where practical, the Implementer and Reviewer functions should be performed by different model vendors. Independent failure modes make agreement-by-shared-blindspot less likely.

### 4.2 Role Table

| Clause | Role | Performed by | Continuity | Authority |
|---|---|---|---|---|
| 4.2.1 | Owner | Human | Durable | Sole ratifier of intent: charter, plan, routing map, decisions, amendments. Reads owner briefs by default and evidence on escalation. |
| 4.2.2 | Dispatcher | Agent, fresh per invocation | None | Drafts work orders from ratified intent. Self-checks each for internal contradiction before issue. Never writes code. |
| 4.2.3 | Implementer | Agent, fresh per work order | None | Executes exactly one work order inside its capability grant. Halts and files RFIs on ambiguity. Never amends intent-bearing documents. |
| 4.2.4 | Reviewer | Agent, fresh per artifact | None | Diffs work reports against the work order and plan. Produces owner briefs. Never writes code, never amends intent. |

---

## PART 5. RECORD ARCHITECTURE

### 5.1 Repository Roles

5.1.1 Two repository roles exist: the methodology source and the governed project. The roles are never merged. For ordinary adoption they are also two physically distinct repositories, and the governed project holds no link of any kind back to the methodology source.

5.1.2 The methodology repository, of which there is one, holds this doctrine, its templates, and reference implementations of enforcement adapters. It is the versioned methodology distribution and reference implementation: documentation together with the supporting tooling that instantiates and checks it. It is not a runtime, a package dependency, an import, a submodule, or an automatic update source for any governed project. No project repository depends on it. Adoption is by instantiation, meaning templates are copied and filled, never by import or submodule. A project must remain fully governable if the methodology repository ceases to exist.

5.1.3 The project repository, of which there is one per project, is the project. Its root is the project root. Adopting the doctrine adds one injectable file, one governance directory, the minimum provider-specific configuration required to inject and enforce them (such as the hook script and settings entries a coding tool needs to load the charter and apply the capability wall), and whatever deterministic dispatch-preparation tooling the adopted revision's own workflow requires — at minimum, a means to generate and validate Appendix B's generated-boundaries block from frontmatter before a candidate is activated (8.3.5, Appendix B). It does not otherwise reshape how the project is laid out, and no clause here names a specific tool or product for that required function. Completed adoption populates the governance directory's records — `PLAN.md`, `STATE.md`, `ROUTING.md`, and the ratified adoption record — and installs that required tooling, together with the adoption commit containing it. A partially assembled skeleton produced before those records exist, before the required tooling is installed, or before the adoption commit, is preparatory material under 6.1.3, not adoption; adoption remains exactly the discrete event 6.1.1-6.1.2 define, never a degree of completeness of this footprint.

5.1.4 Self-hosting. The methodology repository may additionally carry a repository-local governance instance that governs its own maintenance under this doctrine. That instance occupies the governed-project role for the methodology repository itself, so a single physical repository carries both roles. This is the only case in which one repository may hold both, and it is permitted because a methodology that cannot govern its own development is asserting something it has not demonstrated.

5.1.5 Segregation of the self-hosted instance. The distribution artifacts, meaning the doctrine, templates, adapters, adoption skills, migration guides, checks, and packaging, are what an adopting project instantiates. The methodology repository's own charter, governance directory, plan, state, routing map, decisions, work orders, reports, briefs, and history are its working records. Those records are a readable reference example and nothing more. They are never an adoption template, never inherited by an adopting project, never copied into one by any adoption route, and never represented as something a project must reproduce.

5.1.6 Self-hosting creates no dependency. 5.1.2 is unchanged by it: adoption remains instantiation, never import, submodule, package dependency, or automatic update, and a governed project must remain fully governable if the methodology repository ceases to exist. A project is bound to a ratified revision (DC.4.1), never to this repository's current contents.

### 5.2 Project Layout

5.2.1 The reference layout is as follows. Names may be adapted; the invariants in 5.3 may not.

```
<project-repo>/
├── CHARTER.md                    Tier-1 injectable (Appendix A), wired into
│                                 the agent tooling's auto-loaded context.
│                                 If the tooling already auto-loads a file
│                                 (for example an instructions file), that
│                                 file may serve as the charter; do not create
│                                 a second file that merely points to it.
├── governance/
│   ├── PLAN.md                   Should-be. Owner-ratified only.
│   ├── STATE.md                  As-is. Two labeled sections: OBSERVED
│   │                             (mechanically derived) and INTERPRETED
│   │                             (fresh-agent synthesis with provenance).
│   ├── ROUTING.md                Declared governed paths and their required
│   │                             documents. Governed like code (8.2).
│   ├── decisions/DR-001.md ...   Ratified decisions with reasoning.
│   ├── work-orders/WO-001.md ... Issued work orders (Appendix B).
│   ├── reports/                  Work reports, filed for reviewers.
│   ├── briefs/                   Owner briefs (Appendix C).
│   ├── rfis/                     Open RFIs.
│   ├── history/                  Closed transactional records (work orders,
│   │                             reports, briefs, resolved RFIs). Durable
│   │                             audit history, outside the live corpus.
│   ├── LOG.md                    Per-work-order metrics (Part 9).
│   ├── templates/                Project-local copies of Appendices A-E,
│   │                             instantiated once at adoption (6.4.1) and
│   │                             refreshed only by explicit Owner action
│   │                             (5.3.8). Distinct from the methodology
│   │                             repository's own template distribution
│   │                             (5.1.2): this copy is the project's
│   │                             working artifact.
│   └── archive/                  Superseded standing documents, outside the
│                                 live corpus (8.6.2).
├── src/ ...                      The actual project.
└── (everything the project already is; provider-specific enforcement
    configuration and any deterministic dispatch-preparation tooling live
    wherever the adopted provider adapter's own documentation places them —
    5.1.3 — and are not fixed by this reference layout)
```

### 5.3 Invariants

5.3.1 The charter is injected, budgeted, and lives at the project root.

5.3.2 The plan and the state are separate files with separate update authorities. The plan is amended only by ratification. The state is regenerated only by the procedure in 7.8.

5.3.3 Observed and interpreted state are separately labeled, and every interpreted claim carries provenance.

5.3.4 Superseded standing documents are archived out of the live corpus, meaning excluded from injection, routing, configured search and indexes, and normal retrieval, and are not left in the paths agents ordinarily read. The doctrine does not claim archived material is inaccessible; a repository's history is what it is. It claims that reaching it requires deliberate action, and that such action requires explicit Owner authorization (8.6.2). Stale truth that remains in ordinary retrieval paths is worse than no documentation, because it manufactures confident wrong answers.

5.3.5 Governance artifacts live in the repository's version history with the same durability as code.

5.3.6 The doctrine defines no cross-project layer in revisions 0.x. A portfolio is governed as independent projects plus the Owner.

5.3.7 Closed transactional records move to governance/history/ on closure and are retained indefinitely. They are outside the live corpus unless a current route or an active work order explicitly references one, in which case only the referenced record is supplied.

5.3.8 A project's instantiated `governance/templates/` copy is refreshed only by explicit Owner-ratified migration (DC.4.2). It is never automatically updated from the methodology repository (5.1.2, 5.1.6): self-hosting or distribution changes there create no obligation and no drift charge against a project until its Owner ratifies moving to the revision that changed it.

---

## PART 6. ADOPTION

### 6.1 The Adoption Boundary

6.1.1 Adoption is a discrete, dated, change-controlled event. A project is either pre-doctrine or governed. It is never retroactively represented as having been governed before its adoption commit.

6.1.2 The Owner selects a baseline commit, the last wholly pre-doctrine state. History through the baseline commit is pre-doctrine history. Adoption becomes effective with the adoption commit, which is the commit that first contains the ratified adoption record and the completed bootstrap artifacts (2.25). The first counted work order begins after the adoption commit.

6.1.3 The bootstrap work of instantiating the governance structure is Owner work performed once at adoption. It is not itself a work order and its outputs are not counted in Part 9 measurements. Where the capability wall is already installed, the active-scope, per-surface birth test (8.3.5.2) uses a birth-test instrument (2.28) rather than a work order. Any adoption-recorder lifecycle action that records already-ratified Owner decisions is an Owner lifecycle action (8.7.6), never a birth-test instrument and never performed under any capability grant.

6.1.4 Adoption does not alter the project's roadmap. The first counted work order is whatever the project genuinely needed next, not work invented to exercise the methodology (3.2.7).

### 6.2 The Adoption Record

6.2.1 The first decision record of every adopting project (conventionally DR-001) is the adoption record. Appendix D gives its template. It states, at minimum:

6.2.1.1 the baseline commit and the doctrine revision bound to (2.25);

6.2.1.2 which enforcement surfaces are mechanically enforced at adoption and which are unenforced-by-declaration, with the tooling relied on for each;

6.2.1.3 how the conformance gate operates during the pilot period, including whether any empirical instrument is in use and, if so, its qualification status under 8.4;

6.2.1.4 which existing project documents are recognized as controlling sources at adoption and how each is mapped under 6.3;

6.2.1.5 the pilot duration or work-order count after which the Part 9 evaluation will be performed;

6.2.1.6 the operational definition of every Part 9 metric for this pilot, fixed before the first counted work order (9.1.3).

### 6.3 Adoption Mapping

6.3.1 An adopting project with an existing document corpus produces an adoption mapping (Appendix E) before its first counted work order. The mapping assigns every existing intent-bearing or reference document to exactly one of four dispositions.

6.3.2 **Plan.** Content that constitutes current ratified intent is materialized into governance/PLAN.md. Where a pre-existing master plan or specification exists, its live content moves to PLAN.md and the original is archived, so that two documents never both appear authoritative.

6.3.3 **Tier-2 reference.** Documents that inform work but do not carry intent (protocol specifications, principles, design notes) are retained and assigned a route in ROUTING.md. A document with no route is not tier-2; it is archive.

6.3.4 **Charter content.** Prohibitions, standing constraints, and rejected directions that agents must see every session are extracted into the charter's project-specific kill list. Only what earns its token budget goes here.

6.3.5 **Archive.** Superseded, exploratory, or duplicative material is moved to governance/archive/ and excluded from routing and agent search paths.

6.3.6 Historical decisions are not backfilled as decision records. Only past decisions that still materially constrain future work are recorded, and they are recorded once, at adoption, with the reasoning as best it can be recovered and a note that they predate the adoption boundary.

### 6.4 Bootstrap Sequence

6.4.1 The Owner performs the following once, in order, before the first counted work order: confirm that the selected doctrine revision has been ratified by the methodology repository's amendment authority (DC.3.5); record the baseline commit; produce the adoption mapping (6.3); materialize PLAN.md; write or prune the charter to template; write the initial ROUTING.md over declared governed paths only; bootstrap STATE.md from the repository as it exists; install enforcement and perform the birth test (8.3.5); write the adoption record naming the baseline commit; and make the adoption commit containing the governance directory and the adoption record.

6.4.2 The birth test has two levels with different consequences. The no-work-order lockout (8.3.5.1) is an adoption precondition: if any mutation channel available to the Implementer can mutate anything with no active work order, the project has not adopted the doctrine. Active-work-order scope enforcement (8.3.5.2) is tested per surface: a surface that fails through any channel is downgraded to unenforced-by-declaration for that project, which does not invalidate adoption unless the Owner judges the resulting risk unacceptable under 8.3.4.

---

## PART 7. THE WORKFLOW

### 7.0 Overview

7.0.1 One cycle proceeds through the steps below. Every step produces or consumes a file in the governance directory. Steps 7.1 through 7.7 are sequential. Step 7.8 runs on its own triggers.

### 7.1 Intent Is Ratified

7.1.1 The Owner establishes or amends the plan, recording decisions as decision records with reasoning and rejected alternatives.

7.1.2 Exploration may occur anywhere, including in freeform agent conversation. Nothing from exploration carries authority until it is written into the plan or a decision record and ratified.

7.1.3 Ratification happens at the moment a decision closes, not at the end of the session that produced it. The end of a session is where reconstruction quality is worst.

### 7.2 A Work Order Is Dispatched

7.2.1 The Dispatcher receives the charter, the relevant plan sections, the Owner's objective, and the routing resolution for the proposed scope together with the Tier-2 material that resolution requires. All of these are supplied fresh in the invocation. None is assumed from the Dispatcher's own history. The Dispatcher does not choose context; the router does, and the Dispatcher carries the router's result into the work order where runtime injection is unavailable (8.2.1).

7.2.2 The Dispatcher drafts one work order stating scope, capability grant, boundaries, falsifiable acceptance criteria, and the required report format.

7.2.3 The Dispatcher self-checks the draft for internal contradiction between the grant, the required work, and the stated prohibitions, and resolves any contradiction before issue.

7.2.4 The Owner activates the work order.

### 7.3 The Wall Goes Up

7.3.1 Activation configures enforcement from the work order's capability grant. The Implementer's permitted actions are mechanically limited to what the manifest allows.

7.3.2 With no active work order, all mutation channels are denied.

### 7.4 Work Executes Inside the Wall

7.4.1 A fresh Implementer session receives the charter by injection, the work order, and whatever tier-2 documents the routing map attaches to the paths in scope.

7.4.2 The Implementer executes. On ambiguity, contradiction, or a genuine need for authority outside its grant, it halts and files an RFI.

7.4.3 The Implementer does not invent intent, improvise scope, or self-authorize. Interpretation of how is its job. Interpretation of whether and what is not.

### 7.5 Work Is Reported

7.5.1 The Implementer files a work report stating what changed and why, the exact verification commands and their results, the boundaries confirmed respected, any deviations, and one recommended next work order.

7.5.2 The report is addressed to the Reviewer. Completeness is preferred to brevity.

### 7.6 Work Is Reviewed

7.6.1 A fresh Reviewer receives the charter, the work order, the report, the relevant plan sections, the same routed Tier-2 material the Implementer was supplied under the routing resolution, and the output of any empirical instrument that ran (8.4), all supplied fresh. A Reviewer without the Implementer's routed context can be blind to requirements the Implementer was bound by. It produces the owner brief: a one-sentence verdict of PASS, FAIL, or DEVIATION; decisions needed, expressed as binary questions with one-line consequences; risks in owner language; and a sanity check of the recommended next work order.

7.6.2 Nonconformance blocks by default. Only the Owner may waive it.

7.6.3 The Reviewer is an information-loss boundary. The brief is the Owner's default read, but the Reviewer must attach or link supporting evidence, and the Owner must read it, whenever any of the following holds: the verdict is DEVIATION; the Reviewer rates its own confidence LOW on the fixed HIGH/MEDIUM/LOW scale of Appendix C, which threshold is not the Reviewer's to set; the change is security-relevant or irreversible; or the Implementer's claims, the Reviewer's findings, and any empirical instrument's results disagree.

### 7.7 Owner Disposition

7.7.1 Reading the brief, and the evidence when escalated, the Owner disposes of the work: acceptance, rework, or ratification of a deviation. Acceptance and rework are ordinary dispositions. Ratification is reserved for dispositions that change intent (2.7).

7.7.2 Any disposition that changes intent becomes a decision record at that moment.

7.7.3 The cycle's metrics are appended to LOG.md and the next work order dispatches.

### 7.8 State Is Regenerated

7.8.1 On deterministic triggers (session end, work-order acceptance, or a scheduled hook), STATE.md is rebuilt. The OBSERVED section is derived mechanically. The INTERPRETED section is written by a fresh agent from the repository, each claim tagged to its source.

7.8.2 Implementers never maintain documentation mid-task. A degrading agent updating its own record is the least reliable writer at the worst moment.

### 7.9 Prohibited Events

7.9.1 No agent amends the charter, the plan, a decision record, or the routing map.

7.9.2 No action is taken outside an active work order's capability grant.

7.9.3 No scope is expanded within a work order because it seemed convenient. Such needs are RFIs or new work orders.

7.9.4 No pending Owner decision lives in a chat thread. Proposals are extracted to the governance directory and decided from the record. Threads die. Files do not.

7.9.5 No control depends on an agent remembering an instruction.

---

## PART 8. ENFORCEMENT

### 8.0 Classes of Control

8.0.1 The doctrine distinguishes three classes of control and is explicit about which is which.

8.0.2 Deterministic enforcement is mechanism that agent behavior cannot bypass: injection, walls, blocking gates, and the triggers that invoke derivation and regeneration.

8.0.3 Controlled inference is model judgment operating under deterministic constraint: review, interpreted state, work-order drafting. Its invocation is guaranteed. Its correctness is not.

8.0.4 Deterministic derivation is fact computed from the repository with no model in the loop once triggered: observed state, metrics, routing coverage.

8.0.5 The conformance gate illustrates the distinction. No review therefore no merge is deterministic. Reviewer pass therefore actual conformance is not, and the doctrine does not claim it is. That gap is exactly where an empirical instrument belongs (8.4).

### 8.1 Charter Injection

8.1.1 The charter auto-loads into every agent session through the tooling's native mechanism, whether project instruction files or session hooks.

8.1.2 The charter's budget is small enough to survive every session's context pressure. As a rule of thumb, it does not exceed 2,500 tokens. Content that would push it over is demoted to tier-2, never accommodated by expansion.

8.1.3 The charter's order is fixed: prohibitions first, then authority order, then current state, then routing, then reporting, then environment. Prohibitions lead because agents act on the top of context under pressure, and the most expensive failures are plausible actions on the kill list.

### 8.2 Document Routing, Governed Like Code

8.2.1 ROUTING.md maps declared governed paths and subsystems to required tier-2 documents. It is enforced by pre-action hooks where the tooling allows and by Dispatcher attachment into the work order otherwise.

8.2.2 The router is part of the trusted control surface. An agent that complies perfectly with an incomplete map has been given the wrong requirements, which is worse than having ignored them.

8.2.3 The map is version-controlled, change-reviewed like code, and amended only by ratification.

8.2.4 Routing coverage is measured against declared governed paths and subsystems, which ROUTING.md itself names, and not against every file in the repository. Assets, fixtures, and configuration need no route unless declared.

8.2.5 Two deterministic checks run against the map: unmapped governed paths, and orphan documents, meaning tier-2 documents to which no route points. Orphans are archive candidates. Coverage gaps discovered during a work order are RFIs, and their remedy is a routing amendment the Owner ratifies.

### 8.3 Capability Walls

8.3.1 A work order's capability grant is a manifest across, at minimum, filesystem write (a path allowlist), filesystem read (exclusions for protected material), shell execution, network egress, secrets access, package installation, version-control commit, version-control push, and any project-specific surfaces such as database mutation, infrastructure changes, or model runs.

8.3.2 The doctrine defines what authority the work order grants. An enforcement provider makes it physical. Today that provider is the coding tool's own hook, permission, and sandbox system. Later it may be a dedicated agent-governance product. Adapters translate the manifest into the provider's primitives. The manifest is a protocol boundary, not a product.

8.3.3 A wall for a given surface must cover every mutation channel that can reach that surface. A hook that intercepts the file-edit tools but leaves the shell free to write files has not walled the filesystem. It has walled one tool. Where the file-edit tools are hooked and the shell is not, either the shell and its subprocesses are contained by the provider's sandbox with the same path constraints, or filesystem write is declared unenforced for that work order.

8.3.4 Where a provider cannot enforce a surface, the work order lists it under unenforced boundaries. An unenforced boundary is honored by instruction alone and is never represented as a wall. If inability to enforce that surface creates unacceptable risk, the work order does not execute under that provider.

8.3.5 Birth test. A wall that has never been observed denying an action is an assumption, not a wall. On installation, and after any tooling change, the Owner performs both levels below. Each denial is logged. The log is the wall's birth certificate.

8.3.5.1 No-work-order lockout. With no active work order, the Owner attempts a mutation through every mutation channel available to the Implementer: file-edit tools, shell, subprocesses, version-control operations, and any other writing tool. Every attempt must be denied. This level is absolute (7.3.2) and is an adoption precondition (6.4.2).

8.3.5.2 Active-work-order scope. With a deliberately minimal work order active, for every surface the work order claims as mechanically enforced, the Owner attempts an out-of-grant action through every mutation channel that can reach that surface, and confirms the block on each. Where any channel succeeds, that surface is not walled and is recorded as unenforced-by-declaration until fixed and retested.

8.3.6 Denials from enforced surfaces return the RFI instruction, so that the wall teaches correct behavior at the moment of refusal.

### 8.4 Conformance Gates and Empirical Instruments

8.4.1 Review is blocking. Where a qualified empirical instrument exists, it occupies the gate's hard slot, the Reviewer adjudicates its findings, and disagreement between instrument and Implementer is an escalation condition under 7.6.3.

8.4.2 Where no qualified instrument exists, the Reviewer's diff against the work order and plan is the gate, and the record states that this is controlled inference rather than proof.

8.4.3 Circularity. An empirical instrument may not serve as the sole hard gate for the project that is building it. Doing so is circular: the instrument would be certifying the work that produces the instrument. Such an instrument may be introduced into selected work orders as an experimental gate, running alongside the Reviewer, once it has reached independently demonstrated milestones. Disagreements between the experimental instrument and the Reviewer are logged and resolved by the Owner, and the record of who was right is itself a measurement of both the doctrine and the instrument.

8.4.4 Qualification event. An instrument is qualified only by an Owner-ratified decision record that names the instrument version, names the class of claims it is qualified to gate, cites evidence independent of the instrument's own assertions, and states the conditions under which the qualification lapses. A material change to the instrument, or to the evidence relied on, invalidates the qualification until re-ratified. Absent such a record, no instrument is qualified, whatever anyone says of it.

### 8.5 State Derivation

8.5.1 Deterministic trigger. Observed section derived mechanically. Interpreted section written by fresh context from the repository with provenance. Plan untouched.

### 8.6 Corpus Ceiling

8.6.1 Tier-1 has a hard budget. Tier-2 exists only where a route points. Standing documents that are neither are archived. The live corpus is pruned the way a drawing set is superseded: old revisions leave the set.

8.6.2 Archive semantics. Archived material is excluded from injection, routing, configured search and indexes, and normal retrieval paths. It is retained as controlled historical material. Retrieval of an archived document into any agent session requires explicit Owner authorization recorded in the work order or an RFI resolution. The doctrine claims exclusion from ordinary reach, not inaccessibility.

8.6.3 Transactional lifecycle. Open transactional records are supplied to agents by the workflow. On closure they move to governance/history/ and leave the live corpus (5.3.7). History is durable and auditable and is not counted toward live corpus size.

### 8.7 Protected Control Plane

8.7.1 The control plane is the set of artifacts that establish which capability grant is active and record the wall's own behavior: the active-work-order pointer (8.3.5), the installed enforcement configuration (the adapter and its registration or settings entries, 8.3.2), the currently active work order's or birth-test instrument's own frontmatter and body (2.16, 2.28), and the denial-evidence log (8.3.5, 8.3.6).

8.7.2 No work order's or birth-test instrument's own capability grant ever authorizes its executing agent to mutate a control-plane artifact named in 8.7.1, through any mutation channel (2.14) the grant reaches — filesystem write, shell execution, version control, or any other surface — regardless of who drafted or authorized that grant, **including the Owner**. This governs mutation authority only: a grant's `filesystem.read.deny` naming a control-plane path is an ordinary read restriction and raises no such concern. A capability wall implementing this doctrine denies control-plane mutation categorically and without exception, a property of the wall rather than of how carefully or by whom a grant is drafted, distinct from the ordinary declared-surface rules of 8.3.3-8.3.4.

8.7.3 8.7.2 does not restrict the enforcement mechanism's own narrowly scoped act of appending to the denial-evidence log (8.3.6). That act is the mechanism recording its own behavior; no work order's or instrument's grant authorizes or reaches it, and no grant field confers it. The log remains append-only and is never rewritten.

8.7.4 Compliance with 8.7.2 is itself subject to the birth test (8.3.5): it is never claimed enforced until an Owner-authorized live-wall canary specifically targets a control-plane path named in the active grant and observes the categorical denial. Until that birth test passes for the provider in use, protection of control-plane paths remains dependent on dispatch-time grant construction and is stated as such, never as a wall (8.3.4).

8.7.4.1 Naming that canary target requires a narrow, machine-readable exception to ordinary dispatch validation, defined here rather than left ad hoc. A candidate whose frontmatter does not declare `instrument_kind: birth-test` fails pre-dispatch validation outright if any control-plane path (8.7.1) appears anywhere in its capability grant, through any mutation channel. No label or Owner authorship changes this for such a candidate.

8.7.4.2 A birth-test instrument (2.28) may declare `instrument_kind: birth-test` and a `control_plane_probes` list, each entry naming one exact, non-wildcard repository-relative path and the role `control_plane_falsification_probe`:

```yaml
instrument_kind: birth-test
grant:
  filesystem.write:
    - .claude/active-wo.txt
control_plane_probes:
  - path: .claude/active-wo.txt
    role: control_plane_falsification_probe
```

Pre-dispatch validation passes such an instrument only when every control-plane path named anywhere in its grant has a matching `control_plane_probes` entry with an identical exact path; every entry's path matches a real grant target; no control-plane path in the grant is left unlabeled; and the instrument's emitted generated-boundaries block (Appendix B, B.7) lists each such entry under its own heading, stating plainly that it is an expected-denial falsification probe and confers no authority.

8.7.4.3 Passing validation under 8.7.4.2 is a structural precondition for running the canary, never a substitute for it and never authority. The runtime wall still denies every one of those probes exactly as 8.7.2 requires; the birth test fails if any probe is not denied, regardless of how the candidate was labeled.

8.7.5 Before the control plane exists — meaning before any enforcement mechanism is installed and registered (8.3.2) — there is nothing for 8.7 to protect. That is not an exemption from 8.7.2; it is outside 8.7's scope entirely, and installing the control plane is itself Owner work under 6.1.3 and 6.4.1, performed before any wall exists to enforce anything. Once the control plane exists, any need to change it is governed by 8.7.6, never by a work order's or birth-test instrument's own capability grant.

8.7.6 Activating or retiring the active-work-order pointer; changing the installed enforcement configuration; amending the active work order's or birth-test instrument's own frontmatter or body; and, narrowly, any recorder action that itself mutates a control-plane artifact, together with the adoption-recorder lifecycle action defined in Part 6 (the Owner-directed recorder closeout that records already-ratified adoption decisions), are Owner lifecycle actions. Ordinary Part 7 work-order reporting, review, acceptance, history retirement, State and metrics update, and closeout remain inside the governed Part 7 cycle (7.5-7.8) and are not reclassified under this clause merely because they record an already-ratified Owner disposition; 8.7.6 reaches only control-plane mutation itself and the named adoption-recorder action. None is performed under a work order's or birth-test instrument's own capability grant, and none is self-authorized by the artifact being changed. The Owner may delegate the clerical keystrokes of such an action to a separately authorized recorder or mechanism acting on exact, already-ratified Owner instructions, but authority over the action stays with the Owner, never with the Implementer or the instrument executing it, and no active Implementer uses its own capability grant to perform one. That separate Owner lifecycle authorization is recorded before execution in a durable Owner disposition or lifecycle packet in the canonical record; a chat exchange alone is not authorization.

---

## PART 9. MEASUREMENT

### 9.1 Requirement

9.1.1 The doctrine makes falsifiable claims. A project that does not instrument them is practicing a ritual, not a method.

9.1.2 Metrics are logged per work order as counts, not impressions.

9.1.3 The doctrine states each metric's direction of prediction. It does not fix numerical thresholds, because these vary by project. The adoption record fixes the operational definition of every metric for its pilot before the first counted work order (6.2.1.6): what constitutes a rework cycle, what same-work-order detection means, which artifacts count toward live corpus size, and how Owner load is measured (in words or another typesetting-independent unit). Definitions fixed after the fact are not evidence.

### 9.2 Metrics and Predictions

| Clause | Metric | Prediction |
|---|---|---|
| 9.2.1 | Out-of-grant actions denied | Violations occur but are blocked; the count is visible and the damage is zero |
| 9.2.2 | RFIs filed | Ambiguities halt work early instead of being improvised through |
| 9.2.3 | Drift caught at review within the same work order, versus discovered later | Detection latency collapses to the current work order |
| 9.2.4 | Recovery cost when drift is caught | One rework cycle, not archaeology |
| 9.2.5 | Live corpus size (2.27), and routing gaps over declared governed paths | Live corpus flat over time while history grows; gaps trend to zero and each is a logged RFI |
| 9.2.6 | Declared versus mechanically enforced grant surfaces | Reported per work order; the gap is itself a finding about available tooling |
| 9.2.7 | Owner reading load per work order, briefs versus escalations | Below the adoption record's stated ceiling by default; escalations rare and always tied to a 7.6.3 condition |
| 9.2.8 | Where an experimental instrument runs alongside the Reviewer: disagreements and their resolution | Logged with outcome; the record of who was right feeds a later qualification event under 8.4.4 |

### 9.3 Evaluation

9.3.1 Evaluation occurs after the pilot period stated in the adoption record, and is performed by a fresh agent reading the record, never by asking a long-lived session how it went.

9.3.2 If the predictions fail, the log will say which control failed and how. That is a finding. The instantiation or the doctrine is revised accordingly, and the failure is stated publicly if the results are published.

---

## PART 10. LIMITS

10.1 **In-session degradation.** Agents still degrade inside long sessions. The doctrine makes sessions short and their deaths free. It does not make them immortal.

10.2 **Judgment.** A vacuous plan yields vacuous conformance. Gates verify work against intent. They cannot supply intent.

10.3 **Model limitations.** No governance makes an agent understand a domain it cannot understand. The doctrine bounds the blast radius of misunderstanding. It does not eliminate it.

10.4 **Authoritative continuity.** Memory systems, retrieval, and persistent agent state exist and are useful. What no presently available system provides is independently trustworthy, authoritative continuity of intent across sessions, meaning memory that can safely carry authority. The doctrine does not care whether an agent can remember. It cares whether what the agent remembers may be trusted to govern. Until the answer is yes, the record governs. The doctrine should be revised or retired the day that changes.

---

## PART 11. POSITIONING

11.1 None of the parts are new. Specifications, decision records, role-based permissions, review, human approval, and hooks all predate this document. Adjacent work in specification-driven development tooling, agent governance and permission platforms, and specification-governance reference models is active and converging on overlapping fragments of the same problem.

11.2 What is claimed is the architecture connecting the parts: authority with a defined chain of custody, exercised through a canonical record and deterministic mechanism, because the actor interpreting the specification is probabilistic and transient. In sequence: human-ratified intent, a plan that says should-be, an independently derived state that says as-is, decisions carrying their reasoning, disposable sessions, routed and budgeted context, bounded work orders with explicit capability grants, mandatory RFI on ambiguity, independent review with escalation, and measured drift and recovery.

11.3 The doctrine is a methodology, not a platform. Its proper competitor is not any product but the untested default: a human, a large prompt, an agent, hope, and the later discovery of divergence. Its proper evidence is not the elegance of this document but the measurements of Part 9.

---

## APPENDIX A. CHARTER TEMPLATE (TIER-1 INJECTABLE)

Copy to the project root (or adopt the tooling's existing auto-loaded file), fill every bracket, and keep under budget.

```markdown
# [PROJECT] Session Charter
Injected every session. Budget: 2,500 tokens. Doctrine rev [x.y], DR-001.

## A.1 PROHIBITIONS (binding; violations are blocked and logged where enforcement exists)
A.1.1 You never amend this charter, governance/PLAN.md, governance/ROUTING.md,
      or any decision record. You propose; the Owner ratifies.
A.1.2 You act only inside the active work order's capability grant. With no
      active work order, no mutating action is permitted.
A.1.3 Needs outside your grant are RFIs, not improvisations.
A.1.4 [PROJECT KILL LIST: the plausible-but-rejected directions unique to
      this project. Dead approaches agents keep resurrecting. Forbidden
      dependencies. Out-of-scope features. Systems and data that must never
      be touched. Name each specifically. This list is where drift dies.]

## A.2 AUTHORITY ORDER
A.2.1 governance/PLAN.md (ratified intent). Conflicts are surfaced as RFIs,
      never silently resolved.
A.2.2 The active work order.
A.2.3 Documents attached by governance/ROUTING.md.

## A.3 CURRENT STATE (one line each; updated by the Owner at work-order
acceptance, never by agents)
A.3.1 [plan version, phase, what is frozen]
A.3.2 [current sequencing: what is next and what it is blocked on]
A.3.3 [pending owner decisions]

## A.4 ROUTING (read the mapped document before touching the path)
A.4.1 [path or subsystem] -> [document]
A.4.2 Unmapped and unsure -> RFI.

## A.5 REPORTING
End every work order with the report format specified in the work order,
addressed to the Reviewer. Completeness over brevity.

## A.6 ENVIRONMENT
[build and test commands, platform notes: the minimum an agent needs
every session]
```

## APPENDIX B. WORK ORDER TEMPLATE

```markdown
---
id: WO-[n]
status: ACTIVE                 # ACTIVE | COMPLETE | RFI-BLOCKED
doctrine_rev: [x.y]
grant:                         # capability manifest, enforced by adapter
  filesystem.write: [path, path]
  filesystem.read.deny: [protected paths, if any]
  shell.execute: restricted    # denied | restricted | allowed
  network.egress: denied
  package.install: denied
  secrets.read: denied
  git.commit: denied
  git.push: denied
  # project-specific surfaces (db.write, infra.apply, model.run) as needed
enforced_by: {}                # which mechanism walls each enforced surface;
                               # empty by default. An Owner moves a surface
                               # here only after naming and validating the
                               # mechanism that covers the whole surface.
unenforced_boundaries:         # every declared surface not in enforced_by,
  - filesystem.write            # classified exactly once. Honored by
  - filesystem.read.deny        # instruction only; never called walls. If
  - shell.execute                # that risk is unacceptable this WO does
  - network.egress               # not run under this provider (8.3.4).
  - package.install
  - secrets.read
  - git.commit
  - git.push
---
# WO-[n]: [title]

## B.1 CONTEXT
[Two to four sentences. Cite plan sections by number. Paste routed excerpts
here if the tooling cannot inject them.]

## B.2 OBJECTIVE
[The falsifiable goal.]

## B.3 REQUIRED WORK
[Numbered. Each item verifiable.]

## B.4 BOUNDARIES
[Restate the grant in prose where it matters, plus any unenforced boundaries
the implementer must honor on instruction alone. Those are the weakest part
of this work order and the report must confirm each was respected. See B.7
for the checker-generated classification, which is authoritative for exact
grant classification; this section is human-readable elaboration and never
contradicts it.]

## B.5 ACCEPTANCE
[Exact commands and expected results. What the Reviewer verifies from the
report alone.]

## B.6 REPORT FORMAT
[Sections required in the work report.]

<!-- BEGIN GENERATED BOUNDARIES -->
## B.7 Generated boundaries

[Placeholder. After completing the frontmatter above, run the project's
pre-dispatch boundary generator and replace only the content between the
BEGIN and END marker comments above and below with its exact output, keeping
both marker comments in place exactly as they appear. Validate the resulting
work order before activation. This block is machine-generated solely from
frontmatter; B.4 is its human-readable prose counterpart and never
contradicts it.]
<!-- END GENERATED BOUNDARIES -->
```

## APPENDIX C. OWNER BRIEF TEMPLATE

```markdown
# Brief: WO-[n] [title]
C.1 CONFORMANCE: PASS | FAIL | DEVIATION. [One sentence.]
C.2 RATIFICATION NEEDED: [Binary questions only, each with a one-line
    consequence per option. "None" if none.]
C.3 DEVIATIONS AND RISKS: [Owner language. No file paths unless
    decision-relevant.]
C.4 NEXT WORK ORDER: [Endorse the implementer's recommendation, or state the
    objection in one sentence.]
C.5 ESCALATION: NONE | REQUIRED. [If REQUIRED, which 7.6.3 condition applies
    and a link or attachment to the evidence the Owner must read.]
C.6 REVIEWER CONFIDENCE: HIGH | MEDIUM | LOW. [LOW triggers C.5.]
---
Reviewer notes, for the record and not the Owner: [anything longer]
```

## APPENDIX D. ADOPTION RECORD TEMPLATE (DR-001)

```markdown
# DR-001: Adoption of the Doctrine
D.1 Date and Owner.
D.2 Pre-adoption baseline commit: [hash]. History through this commit is
    pre-doctrine. Adoption becomes effective with the commit that first
    contains this ratified record and the completed bootstrap artifacts.
D.3 Doctrine revision bound: [x.y], ratified [date].
D.4 Enforcement at adoption.
    D.4.1 Mechanically enforced surfaces, each with the mechanism relied on
          and the date of its birth test (8.3.5).
    D.4.2 Unenforced surfaces, declared per 8.3.4, and the mutation channels
          known to remain open.
D.5 Conformance gate during pilot: Reviewer-only controlled inference, or an
    empirical instrument and its qualification status under 8.4.4.
D.6 Recognized controlling sources at adoption and their disposition per the
    adoption mapping (Appendix E).
D.7 Pilot period: [n work orders or n days], after which Part 9 evaluation
    is performed by a fresh agent reading the record.
    D.7.1 Operational definitions for each Part 9 metric, fixed now (9.1.3):
          rework cycle, same-work-order detection, live corpus contents,
          Owner load unit and ceiling, and any project-specific measures.
D.8 Reasoning: why adopt, and why now.
D.9 Rejected alternatives.
D.10 Historical decisions carried forward (6.3.6), each with a note that it
     predates the boundary.
```

## APPENDIX E. ADOPTION MAPPING WORKSHEET

For each existing document in the project, record one row.

| Document | Disposition (6.3.2 Plan / 6.3.3 Tier-2 / 6.3.4 Charter / 6.3.5 Archive) | If Tier-2: route in ROUTING.md | If Charter: the extracted line(s) | Notes |
|---|---|---|---|---|
| | | | | |

Rules: every intent-bearing document lands in exactly one row; a Tier-2 row without a route is an Archive row; two documents may not both be assigned to Plan for the same scope; the completed worksheet is attached to DR-001.

---

*Revision 0.8. Ratified 2026-08-21 by DR-005. See DC.2 for history and DC.3 for the rules under which this document changes.*
