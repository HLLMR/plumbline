# Adopting Writwall

Writwall is a document-controlled governance methodology with a self-hosting reference implementation and project-scaffolding toolkit. This is the complete on-ramp. If you do not yet know which agent to open, where it should run, or what to say first, begin with [`START-HERE.md`](START-HERE.md); it requires no prior Doctrine knowledge.

**Before anything else: do not unpack the distribution archive into your project.** `writwall-<revision>.zip` is a source distribution, not an overlay. Adoption instantiates a small set of project-side artifacts, listed in section 0. Writwall's own charter, governance directory, decisions, plan, state, and work history are its working records under Doctrine 5.1.4 and 5.1.5. They are readable as an example and are never copied into your project by any route below.

If the archive may already have been unpacked into the target, stop before
deleting or continuing. Follow `START-HERE.md`'s accidental-overlay recovery
path with a separate clean distribution and its manifest. Exact matches are
only proposed residue; differing or pre-existing files are unknown until the
Owner ratifies an exact disposition.

---

## 0. What adoption actually puts in your repository

```
<your-project>/
├── CHARTER.md (or your tooling's existing auto-loaded file, e.g. CLAUDE.md)
├── .claude/hooks/wo_capability_wall.py       (or your provider's adapter)
├── checks/check_work_order_dispatch.py       deterministic pre-dispatch validator
└── governance/
    ├── PLAN.md  STATE.md  ROUTING.md  LOG.md
    ├── decisions/  work-orders/  reports/  briefs/  rfis/
    ├── history/    archive/      templates/
```

That is the whole footprint. Every route below produces exactly this, filled in to differing degrees. `DOCTRINE.md` itself is not copied into your project: after adoption your agents receive your charter and your routed records, never the methodology (Doctrine 1.2.4).

`checks/check_work_order_dispatch.py` is a deterministic, read-only checker: it validates the lockout state (`--lockout`), a candidate work order before you create the activation pointer (`--work-order <path>`), or the currently active pointer and the work order it names (`--active`). It catches a missing, malformed, or mistargeted pointer, CRLF/non-UTF-8 work-order bytes, and an unsafe or malformed grant, before you launch a mutating session. It is a convenience check, not enforcement: it never repairs anything, and passing it makes no claim about the capability wall, which is a separate, provider-specific mechanism.

Adoption is an Owner event with a defined boundary (Doctrine Part 6). Every route below ends the same way: a baseline commit is chosen, a governance directory exists, the charter is injected, the wall has been observed denying writes through every mutation channel, an adoption record (DR-001) is ratified, and an adoption commit contains it. Until DR-001 exists, nothing is governed and nothing counts.

---

## 1. Choose your route

Choose the human operating model in `START-HERE.md` before choosing the
mechanical route below. In particular, make the self-contained adoption bundle
and these instructions local **before the wall is registered**. A correctly
locked session may deny the network request that would otherwise retrieve them.

For a first adoption, the default is the day-zero coordinator:

Release `v0.10.0` packages the conversation-first Architect handoff,
canonical-root enforcement, and corrected lifecycle classification described
below.

```text
python -m pip install "https://github.com/HLLMR/writwall/archive/refs/tags/v0.10.0.zip"

# Installed command
writwall start --project-root /path/to/your-project

# Source-tree fallback on Windows
py -3 scripts/start_writwall.py --project-root C:\path\to\your-project

# Source-tree fallback on macOS or Linux
python3 scripts/start_writwall.py --project-root /path/to/your-project
```

It classifies the target from repository bytes, copies the complete skill bundle
into a temporary `.writwall-bootstrap/` directory only for a clean/new target,
and emits the exact next prompt. It is lifecycle-aware bootstrap and routing
tooling, not an authority or installer. Non-clean valid states skip intake and
change no target bytes. Only clean/new mode initializes a durable project-
specific privacy screen in per-user local state outside the repository. The
bootstrap handoff records only ready status and entry count, never its location
or contents. Its clean/new branch remains create-only bootstrap tooling. See
[`docs/privacy-screen.md`](docs/privacy-screen.md).
Contradictory active state stops before output.

For a clean/new target, the ordinary invocation is conversation-first: it
asks nothing on the command line and hands off to a fresh Architect with a
bounded, local, non-secret inventory for an existing project, or one open
invitation for an empty one. The former full questionnaire remains available
verbatim behind `--structured-intake`; deterministic automation keeps using
`--non-interactive`. Full interface and external-
Operator packet behavior are documented in
[`docs/day-zero-coordinator.md`](docs/day-zero-coordinator.md).
The idea-first qualification and identity gate are documented in
[`docs/architect-interview.md`](docs/architect-interview.md).

| Route | Use when | Tooling | What it produces |
|---|---|---|---|
| A. Chat prompt | You want to think it through with a model before touching the repo, or your project has an existing document corpus that needs mapping | Any capable chat model | Draft DR-001, draft adoption mapping, draft charter kill list, a checklist of manual steps |
| B. Coding-agent skill | You are in Claude Code (or a coding agent that supports skills) inside the target repository | `skills/writwall-adopt/`, a self-contained bundle | Bootstrap: inventory, scaffolded `governance/`, installed adapter, installed pre-dispatch validator, birth-test evidence, proposals for the Owner, no commits. Then, only if you explicitly direct it, an Owner-directed recorder closeout that records the decisions you have ratified and makes the one local adoption commit. |
| C. Scaffolder | You already know the layout and only want the directories, templates, and dispatch checker | `init.sh` | Empty `governance/` structure, template copies, and a create-only pre-dispatch validator. Nothing project-specific. |

Routes combine. A common path for an existing project is A (mapping conversation) followed by B (mechanical bootstrap) followed by the Owner steps in section 5.

The coordinator selects among these routes; it does not replace them. Its
handoff is temporary and must be removed before the adoption commit.

| Human command | Observed state | Fresh role receiving output | Prior session stops | Target bytes |
|---|---|---|---|---|
| `writwall start --project-root <project>` | Clean/new (ordinary invocation) | Architect (conversation-first) | Launcher returns; the Architect stops before adoption mechanics until the Owner promotes | Create-only bootstrap may be added |
| `... --structured-intake` | Clean/new | Adoption coordinator | Launcher returns; coordinator stops at adoption closeout | Create-only bootstrap may be added |
| Same command | Partial/recovery | Recovery coordinator | Incomplete or locked session | Unchanged |
| Same command | Adopted/retired lockout | Fresh General | Onboarding or prior work session | Unchanged |
| Same command | Active work order | Bounded Operator/Implementer | Prior coordinator or Implementer context | Unchanged |
| Same command | Malformed/contradictory | No role; fail-closed diagnostic | Invoking session | Unchanged |

---

## 2. Route A: the adoption prompt

Open your chat companion. Attach or paste `DOCTRINE.md`. Then paste this:

```
You are helping me adopt the Doctrine (attached) into a software project as its
Owner. Act as a bootstrap interviewer, not as an implementer. You draft; I ratify.
Ask one question at a time. Do not summarize the doctrine back to me.

Ground rules for you:
- Everything you produce is a PROPOSAL until I say "ratified." Label drafts as such.
- Never invent facts about my project. If you need to know something (what
  documents exist, what the plan is, which tools my agents use), ask.
- Cite the doctrine clause for every recommendation.
- If I ask you to skip a step the doctrine requires (baseline commit, birth test,
  adoption mapping, DR-001), refuse and explain which clause requires it.

Walk me through, in order:
1. Baseline commit selection (Doctrine 2.25, 6.1.2). Ask what my last wholly
   pre-doctrine commit is.
2. Adoption mapping (6.3, Appendix E). Ask me to list every intent-bearing or
   reference document in the project. For each, propose PLAN / Tier-2 with route /
   Charter kill-list line / Archive, with a one-line reason. Two documents may not
   both be PLAN for the same scope. A Tier-2 document without a route is Archive.
3. Charter kill list (Appendix A, A.1.4). Ask me what plausible-but-rejected
   directions my agents keep resurrecting. Draft the lines.
4. Routing (8.2). From the mapping, draft ROUTING.md over declared governed paths
   only. Do not map assets, fixtures, or configuration.
5. Enforcement (8.3). Ask which agent tooling I use. State which surfaces the
   available adapter can make physical and which will be unenforced-by-declaration.
   Draft the D.4 section of DR-001 accordingly. Remind me the birth test (8.3.5) is
   mine to run and that level 1 is an adoption precondition.
6. Pilot definitions (9.1.3, D.7.1). Ask me to fix, now, what counts as a rework
   cycle, same-work-order detection, live corpus contents, and the Owner-load unit
   and ceiling. Refuse to leave these blank.
7. DR-001 (Appendix D). Assemble the draft from the above. Leave D.8 reasoning and
   D.9 rejected alternatives for me to write in my own words; do not write them.

When we are done, give me one compact decision packet: every decision I made, in
my own words where I wrote them, in the order of Doctrine 6.4.1, with the
repository operations each one implies listed beside it. Do not give me a
checklist of edits to type. Then stop.
```

That conversation produces drafts and a decision packet. Move them into your repository yourself, or hand the packet to Route B, which can record ratified decisions for you.

---

## 3. Route B: the coding-agent skill

Copy `skills/writwall-adopt/` from this repository into your target project's skills location (Claude Code: `.claude/skills/writwall-adopt/`). Copy the whole directory: it is a self-contained bootstrap bundle carrying its own copy of the doctrine, the migration guides, the adapter and its README, the pre-dispatch validator, and templates A through E under `references/` and `assets/`. It reads nothing from this repository, so the target project never depends on Writwall (Doctrine 5.1.2).

Confirm that complete directory is locally readable before any project hook is
registered. Keep it available through whichever bootstrap or recorder step
still needs it; remove it before the adoption commit, never earlier merely
because the wall has entered lockout.

Open a fresh session in the target repository and say:

```
Use the writwall-adopt skill. Bootstrap this repository for Doctrine adoption.
Baseline commit candidate: [hash or "determine and propose"].
```

The skill follows the standing rules of the remediation companion (inventory first, move rather than delete, propose rather than dispose, no source changes, no commits, RFI list for unknowns). It inventories the mutation channels your installation actually exposes rather than a fixed list, installs the adapter with matcher `*`, and runs both doctrinal birth-test levels through the adapter's more detailed procedure: Level 1 no-work-order lockout, Level 2 ordinary active scope, Level 3 protected-control-plane falsification where claimed, and the conditional Level 4 read-deny procedure. Bootstrap ends with a report and the repository in lockout, and it does not create DR-001 for you. That is yours to ratify.

Before registration or Level 1, the coordinator must copy
`assets/bootstrap-charter-addendum.md` verbatim into the
engine-visible pre-adoption charter. Ordinary no-pointer work remains forbidden.
The addendum permits only exact calls named by a durably Owner-ratified
birth-test lifecycle, solely so the installed wall can deny them; it confers no
mutation authority, denial is the only valid outcome, and any success stops
adoption. Remove the temporary addendum before the adoption commit.

**The optional second step: an Owner-directed recorder closeout.** After you have read the bootstrap report, you may either finish section 5 yourself or explicitly direct the skill to record your decisions. That second mode exists because ratifying and typing are different things. You remain the only source of intent: the baseline, the plan content, the mapping dispositions, the routing, the operational definitions, your adoption reasoning and rejected alternatives, your acceptance of every unenforced surface, and the decision to adopt at all. What the recorder may do, once you have supplied those and ratified them explicitly, is the clerical remainder — materialize `PLAN.md`, archive the superseded original, finalize labels, write or rename DR-001 transcribing your words verbatim, clear the bootstrap markers, remove bootstrap-only residue, stage the adoption set, and make the one local adoption commit.

It asks first. Before touching anything it hands you a decision packet: what it will record, whose words each decision came from, the exact file operations, and the exact commit message and contents. Nothing proceeds until you ratify that packet in so many words — a filename, a draft, or the state of the repository is never taken as approval. If a decision is missing it asks you for the decision, not for the edit. And a recorder closeout still cannot push, tag, publish, change visibility, select a license, weaken or skip the birth test, or start WO-001.

Ratification in conversation settles the decision but is not, by itself, the
durable lifecycle authorization required by Doctrine 8.7.6. The packet names a
canonical lifecycle record. After you ratify, a separately authorized
coordinator/recorder first transcribes your authorization there verbatim and
verifies the record. Only then may it perform the protected lifecycle mechanics
named by that record. This recording step is clerical and may be delegated; the
decision and authority remain yours.

Because bootstrap deliberately leaves the repository in lockout with no active pointer, a walled session has no grant and will be denied every mutation. Activate an uncounted bootstrap closeout work order naming exactly the closeout paths — the same instrument as `WO-000-birth-test.md` and, like it, not a counted work order under 6.1.3 — before directing the closeout.

**Delete the bundle before adoption completes.** Remove `writwall-adopt/` from the skills directory only after the final bootstrap/recorder action that needs it and before the adoption commit. It is a bootstrap tool under the narrow exception of Doctrine 1.2.3, not project context; leaving it installed would place the doctrine in the live corpus, which 1.2.4 and 8.6.1 forbid. What remains is what it installed into your project: the charter, the adapter under your tooling directory, and `governance/`. Those are yours from that moment on.

### If the wall is already registered and the bundle is missing

Do not ask the locked IDE session to fetch these instructions, weaken the hook,
or manufacture an activation pointer. Treat that session as the walled
Implementer in lockout. Use an external authorized adoption coordinator /
recorder with a local Writwall source distribution to inventory the partial
state and prepare the exact lifecycle packet. The copy/paste recovery prompt is
in `START-HERE.md` under **already-installed lockout**.

The no-pointer condition is reproducible, not perishable. An authorized
lifecycle action may re-establish the no-pointer state and a fresh session may
run Level 1. Unplanned denials are not retroactively promoted into a birth test.

If your project already has partial governance artifacts from an earlier revision, tell the skill which revision they came from. It will look for a migration guide bundled under `references/migration-guides/` and follow that instead of treating the artifacts as unknowns.

---

## 4. Route C: the scaffolder

```bash
./init.sh /path/to/your/project
```

Creates `governance/` with its subdirectories and `.gitkeep` files, copies templates A through E into `governance/templates/`, copies the pre-dispatch validator to `checks/check_work_order_dispatch.py`, and copies the Claude Code adapter to `.claude/hooks/` if `.claude/` exists. It accepts both a normal repository and a worktree whose `.git` is a file. It prints the Doctrine 6.4.1 sequence and exits. It does not inventory, does not birth-test, and does not commit, and it makes no claim that any wall works.

It is **create-only**. Every file that already exists is left untouched and reported as skipped; nothing is deleted or recursively replaced. Your charter and your `.claude/settings.json` hook registration are refused outright rather than skipped, because both carry local content or enforcement configuration that a scaffolder cannot safely merge. Have an exactly authorized coordinator/recorder perform those project-specific mechanics, or perform them yourself, using `adapters/claude-code/README.md` and `${CLAUDE_PROJECT_DIR}` rather than an absolute path.

**Operating envelope.** The wall is mechanically active only in sessions launched with the target repository as the **project root** and with its project `PreToolUse` hook visibly loaded. Claude Code loads project hooks from the project root and its settings hierarchy; a repository reachable only as an *additional working directory* is writable and unwalled at the same time. The standalone adapter supports CPython 3.10 through 3.14. Register the native Windows `py -3` or native POSIX `python3` command with `${CLAUDE_PROJECT_DIR}`, matcher `*`, and an explicit timeout; never use an absolute path. Run the installed adapter's read-only `--preflight` with the exact expected digest and native platform, then confirm with `/hooks` that matcher, source, portable command, and timeout are loaded before probing anything. Startup or timeout non-invocation still cannot be represented as fail-closed by a command hook.

A project used on only one native platform tests that actual Implementer
environment. Lacking the other platform does not by itself block adoption if
Level 1 passes on every channel available in the used environment and the Owner
accepts the unproved surfaces under Doctrine 6.4.2 and 8.3.4. It does block a
portable Windows-and-POSIX protected-control-plane claim: record the absent leg
as untested/indeterminate, keep the affected whole surfaces under
`unenforced_boundaries`, and birth-test any new native environment before its
first mutating session.

**Safe surface inventory.** Use a minimal provider profile for initial adoption:
disable unrelated connectors, plugins, MCP servers, and delegated agents before
the birth-test inventory. Probe an external mutation tool only against an
explicit disposable fixture whose side effect, verification, and cleanup are
authorized in the lifecycle packet. Authentication failure, provider rejection
before hook dispatch, an unavailable tool, or an unprobed channel is
indeterminate, never a pass. Do not use ordinary live account objects as
canaries.

Two narrow overrides exist, each naming its targets explicitly:

```bash
./init.sh --force-templates /path/to/your/project   # only governance/templates/[A-E]-*.md
./init.sh --force-adapter   /path/to/your/project   # only .claude/hooks/wo_capability_wall.py
```

Both are for refreshing verbatim distribution files after a revision change. Neither touches a charter, work order, decision record, log, or hook registration.

Every run ends with three lists: created, skipped, and refused. Read them.

---

## 5. The Owner's sequence (all routes end here)

This is your decision sequence. Every step below is yours to decide and yours to ratify, and no agent may decide, sign, or infer any of it. That is what Doctrine 6.4.1 fixes: the order, and the authority.

It does not fix whose fingers move. Once you have made a decision and ratified it explicitly, an agent you have authorized may perform the repository mechanics that record it — materializing a file, archiving a superseded one, renaming a finished record, staging, and making the local adoption commit. Route B's recorder closeout is that path; doing it all yourself is equally correct and always available. What is never delegable is the deciding.

In the order of Doctrine 6.4.1:

5.1 Confirm the doctrine revision you are binding to is ratified (DC.3.5). Check `DOCTRINE.md` DC.1. Revision 0.8 is current, ratified on 2026-08-21 by `decisions/DR-005.md`, superseding 0.7; a new adoption should bind to 0.8. Revision 0.7 was ratified on 2026-08-20 by `decisions/DR-004.md`; revision 0.6 was ratified on 2026-08-16 by `decisions/DR-001.md` and was the first authoritative revision of the methodology. Both 0.6 and 0.7 remain valid revisions to be bound to by a project that has not migrated. Revisions 0.1 through 0.5 were never ratified and you may not bind to any of them. Always check DC.1 yourself rather than trusting this sentence: DC.1 is the authority, and a revision that looks finished is not the same as one that has been ratified.

Binding to 0.8 means the Appendix B work order you complete in step 5.10 and every one after it follows 0.8's classification rule: every capability surface named under `grant` is classified exactly once, either in `enforced_by` (naming the mechanism that covers the whole surface) or in `unenforced_boundaries` (honored by instruction only). The template's default is `enforced_by: {}` — an empty mapping — with all eight minimum surfaces (`filesystem.write`, `filesystem.read.deny`, `shell.execute`, `network.egress`, `package.install`, `secrets.read`, `git.commit`, `git.push`) listed under `unenforced_boundaries`; move a surface into `enforced_by` only after you have named and validated the mechanism that covers it in full. After completing the frontmatter, run the pre-dispatch validator's `--emit-boundaries --work-order <path>` and replace only the content **between** the existing `<!-- BEGIN GENERATED BOUNDARIES -->` and `<!-- END GENERATED BOUNDARIES -->` marker comments, now under the `## B.7 Generated boundaries` heading (B.4 is BOUNDARIES, unchanged prose; Doctrine DC.2's 0.8 erratum explains the renumbering), with its exact output; then run the ordinary `--work-order <path>` check again, and it must pass before you activate the candidate. A project already bound to 0.6 or 0.7 does not gain any of this automatically: see section 6 and the applicable migration guide (`migration-guides/0.6-to-0.7.md`, `migration-guides/0.7-to-0.8.md`) for the explicit, Owner-ratified migration this requires.

The validator also checks repository-looking paths in B.3 and B.4 against the
machine-readable grant. A path that is mentioned for a read-only or
expected-denial purpose, rather than as writable authority, must be labeled in
frontmatter so the checker can distinguish it without interpreting prose:

```yaml
dispatch_validation:
  prose_path_exceptions:
    - path: governance/PLAN.md
      role: routed_read_only_plan
```

An exception is a label, not a grant. It authorizes no read, write, probe, or
lifecycle action; use a short, specific role and validate the finished record.

Doctrine 0.8 also adds Part 8.7, Protected Control Plane: no work order's or birth-test instrument's own grant, however authored, ever confers mutation authority over the active-work-order pointer, the installed enforcement configuration, the active work order/instrument's own frontmatter and body, or the denial-evidence log (8.7.1-8.7.2); activating or retiring the pointer, changing installed configuration, and the adoption-recorder lifecycle action are Owner lifecycle actions performed outside any capability grant, authorized in a durable Owner disposition before execution, never in chat alone (8.7.6). A birth-test instrument may still name an exact control-plane path as its own canary target by declaring `instrument_kind: birth-test` and labeling that path under `control_plane_probes` with role `control_plane_falsification_probe` (8.7.4.1-8.7.4.3); labeling confers no authority, and the runtime wall must still deny the probe. The shipped checker distinguishes that labeled falsification case from an invalid ordinary grant, and the shipped adapter source contains the categorical runtime floor. **Neither source fact is a live wall claim:** install only exact Owner-ratified bytes through a durable lifecycle packet. Test every native environment the project will actually use. A portable Windows-and-POSIX protected-control-plane claim requires separate fresh native sessions on both platforms across every exposed mutation channel; until both succeed, keep the affected whole surfaces under `unenforced_boundaries`. A missing unused platform does not invalidate adoption under 6.4.2, but it remains untested and may not inherit evidence from the tested host. Writwall's own RFI-22 tracked its cross-platform claim and closed only after complete Windows and native-Linux protected-control-plane matrices at WO-PL-026 closeout.

5.2 Record your baseline commit hash.

5.3 Dispose of the adoption mapping. Materialize `governance/PLAN.md` from whatever your ratified intent currently lives in, and archive the original so two documents never both look authoritative (6.3.2).

5.4 Write or prune your charter to Appendix A. If your agent tooling already auto-loads a file, that file is the charter; do not create a second one that points to it (5.2). Stay under budget (8.1.2).

5.5 Write `governance/ROUTING.md` over declared governed paths only.

5.6 Bootstrap `governance/STATE.md`: OBSERVED from the repository, INTERPRETED by a fresh agent, each claim with its source (7.8).

5.7 Install exact ratified adapter/settings bytes through an Owner lifecycle packet and run the adapter README's birth-test sequence. Level 1 proves no-work-order lockout; Level 2 proves ordinary path scope channel by channel; Level 3 uses a separately ratified birth-test instrument to falsify the protected-control-plane floor across every exposed mutation channel. Run it on every native environment the project will use. Separate fresh Windows and POSIX sessions are required only for a portable two-platform claim; if one platform is unavailable and unused, record it as untested/indeterminate and leave the affected whole surfaces unenforced rather than blocking adoption automatically. If any work order declares `grant.filesystem.read.deny`, also run the README's supplemental read-deny procedure with Owner-private sentinel content. Keep the strict whole-surface classification honest: configuration inspection and logic tests are not provider birth tests, and a partial channel observation does not move a surface into `enforced_by`.

Confirm `/hooks` before you probe: matcher, source, and a command that resolves through your provider's project-directory variable. That is **necessary configuration evidence, not proof of live enforcement** — it shows what the provider was configured to load, not that the session running your probes loaded it. Proof is local to one executing provider session and does not transfer to another session, parent or child context, UI, or provider invocation; a session that intends to mutate the repository establishes its own.

What counts as proof is a **live-wall canary**: an Owner-authorized, genuinely mutation-capable, out-of-grant call that survives provider input validation and so reaches the hook. Its target is named explicitly by the authorized procedure and deliberately excluded from the active `filesystem.write` grant. The pass condition is conjunctive — the provider blocks it before mutation, the target does not exist afterward, the denial log grows by exactly one record, and that record identifies the real executing session and the expected denial reason. An impossible-match `Edit` is **not** a valid canary: the provider rejects it during input validation, before hook dispatch, so it writes no record and proves nothing. Neither is direct adapter invocation or a synthetic payload. If the canary creates the file, writes no denial record, or is indeterminate, the wall is not proved live: stop, and treat any cleanup as a separately authorized action. A passing canary covers the channel it tested; it does not make shell-mediated writes or any other declared-unenforced surface mechanically enforced. See the adapter README for the full procedure.

5.8 Fill DR-001 from Appendix D, including D.7.1 operational definitions for every metric, before the first work order.

5.9 Make the adoption commit containing `governance/`, the charter, the adapter, and DR-001. Its message names the baseline hash. This is one local commit; it is not a push, a tag, or a release. You may make it yourself or have an authorized recorder make it on your behalf after you have ratified exactly what it will contain — in either case the commit records a decision that was already yours.

5.10 End onboarding and hand the adopted project to a fresh General. Earlier
releases called this continuity role `Owner-Agent / Project-Architect`; that
term remains compatibility vocabulary for older records, not the current route. The
recorder presents this exact prompt and stops:

```text
Act as a fresh General for this already-adopted project's continuity. Begin
read-only and verify the lifecycle from repository bytes rather than prior chat. Read the
charter, Plan, State, Routing, ratified adoption record, and open transactional records. State
the project's next decision plainly. Prepare, but do not activate, the smallest genuine work
order or bounded Operator packet; route it to a fresh Architect instead only when the next
decision requires new design or design-conformance judgment rather than routine continuity. Lead
with a concise Recommendation and material tradeoff; keep the detailed packet behind it as
supporting evidence rather than the conversational front door. When the next safe mechanical
action is available, ask once for one combined disposition and action. If that action uses a new
user-owned task, explicitly include creation and dispatch of the named task in that approval
request; never infer task-creation permission afterward. Once approved, perform every
mechanically available authorized step. Do not ask for the same decision again. The human Owner
alone ratifies intent and activates work; preserve a distinct fresh Reviewer after
implementation. The onboarding coordinator stops here and does not continue into project work.
```

The General prepares whatever genuine work the project needs next (6.1.4),
including a bounded external Operator packet when that is smaller than a
repository work order. It leads with its recommendation and material tradeoff;
the complete packet is supporting evidence. When a safe next mechanical action
is available, its single approval request combines the disposition with that
action. A new user-owned task is created or dispatched only when that same
request explicitly asks for it. After approval, the General performs all
mechanically available authorized steps without asking for the decision again.
New design or design-conformance judgment is routed to a fresh Architect.

For a repository work order, activation remains a distinct Owner decision.
After the candidate passes `--work-order`, the Owner-authorized lifecycle
creates `.claude/active-wo.txt` with exactly one LF-terminated, repository-
relative line naming it, then runs `--active`. The pilot begins. No bootstrap
or recorder run activates or implements that work.

---

## 6. Migrating between doctrine revisions

Nothing happens automatically (DC.4). When you decide to move a project from one ratified revision to another: read the DC.2 rows between them; list every local artifact the differences touch (charter structure, work-order frontmatter, adapter, brief format, routing rules); update them; write a decision record naming both revisions and the affected artifacts; commit. Where a `migration-guides/<from>-to-<to>.md` exists, follow it; it is the companion document for that specific transition, in the same spirit as the 0.1-to-0.6 remediation companion that produced this section. A project bound to 0.6 that wants to move to 0.7 follows `migration-guides/0.6-to-0.7.md` explicitly; a project bound to 0.7 that wants to move to the current 0.8 revision follows `migration-guides/0.7-to-0.8.md` explicitly. No script, adapter, skill, or agent invocation performs any migration on its own initiative, and a project remains correctly bound to its recorded revision until its Owner ratifies otherwise.

## 7. Public-source boundary

Adopters consume a released clean-history projection, not Writwall's private
governed repository or its checked-in `dist/` archive. The projection is built
from the exact allowlist in `projection/public-files.txt`, carries generated
manifest and provenance records, and is checked by
`checks/check_public_projection.py` before any publication decision. Commit
identifiers quoted in retained governance evidence refer to the private
governed source and are not claims about the projection's future Git history.
See `PUBLICATION.md` for the reproducible build and verification procedure.
