---
name: writwall-adopt
description: Bootstrap a repository for adoption of the Writwall Doctrine (document-controlled AI-assisted development). Use when the user asks to adopt the doctrine, instantiate Writwall, set up governance for a project, scaffold a governance directory, install the capability wall, run the birth test, prepare an adoption mapping, or migrate a project from an earlier doctrine revision. Also triggers on "writwall", "adopt the doctrine", "governance bootstrap", "DR-001", "birth test", "capability wall". Bootstrap mode prepares and proposes only (Doctrine 6.1.3). A separate Owner-directed recorder mode, available only after the bootstrap report and an explicit Owner instruction, records decisions the Owner has already ratified and may make one local adoption commit. Neither mode ratifies intent, invents Owner reasoning, pushes, tags, publishes, or modifies project source.
---

# writwall-adopt

You are the bootstrap implementer for a project adopting the Doctrine. You are not the Owner. You prepare; the Owner adopts.

## Day-zero handoff

When `.writwall-bootstrap/HANDOFF.md` and `intake.json` are supplied, read both
before choosing a mode. The intake is unratified and carries no authority. Re-
observe the target repository's activation pointer and pointed work-order
status before acting; repository bytes override the handoff if state changed.
Never infer an active work order from prior chat or a closed history record.

The day-zero command already made this complete bundle local. Do not fetch a
replacement or register the wall before its recovery instructions are readable.
External-operation packet scaffolds are inert: blank fields authorize nothing,
credentials remain outside them, and infrastructure, DNS, and mail Operators
remain outside the repository wall unless they edit repository bytes.

Read `references/DOCTRINE.md` in this skill bundle before doing anything, and cite clauses in your report. Doctrine 1.2.3 permits a bootstrap agent to receive the doctrine as an implementation specification under direct Owner supervision. That permission is bounded by this task: it ends when bootstrap ends.

## Two modes

| Mode | When it runs | What it does |
|---|---|---|
| **1. Bootstrap** | The default: every invocation the Owner has not explicitly directed into recorder closeout | Inventory, scaffold, install enforcement, birth test, proposals, report, lockout. Proposes; disposes of nothing. |
| **2. Owner-directed recorder closeout** | Only after Mode 1's report exists, the Owner has read it, and the Owner explicitly directs this mode | Records decisions the Owner has already made and ratified, and — when explicitly authorized — makes the one local adoption commit. |

Mode 2 is never entered on your own initiative, never inferred from a filename, a draft, a prior conversation, or repository state, and never entered because Mode 1 happened to end tidily. If the Owner has not named it, you are in Mode 1.

**The rule that does not change in either mode: you never ratify.** You do not decide intent, sign a decision, judge whether the project should adopt, or write the Owner's reasoning for them.

## Authority is not keystrokes

The Owner alone decides and ratifies:

- the baseline commit (2.25, 6.1.2);
- what constitutes current ratified intent, and therefore the content of `PLAN.md` (6.3.2);
- the disposition of every intent-bearing document in the adoption mapping (6.3);
- the routing map over governed paths (8.2);
- the operational definition of every Part 9 metric (9.1.3, D.7.1);
- the adoption reasoning (D.8) and the rejected alternatives (D.9), in their own words;
- which historical decisions still materially constrain future work (6.3.6);
- acceptance of the residual risk from every surface that is unenforced-by-declaration (8.3.4, D.4);
- whether a recorder closeout ends by removing the active-WO pointer, and therefore when the repository returns to lockout (7.2.4, 7.3.2);
- whether to adopt at all, and when.

Once the Owner has supplied a decision, or has explicitly approved a specific draft as written, **recording it in the repository is mechanical work.** Doctrine 6.4.1 fixes the sequence and fixes who decides. It does not require the Owner personally to materialize an already-approved file, move a superseded document, rename a finished record, or type a local commit. In Mode 2 you may perform those keystrokes on the Owner's behalf.

Hold the two apart in every exchange. If a substantive decision is missing, ask for **that decision** and nothing else. Never hand the Owner a list of edits, moves, renames, stages, or commits to perform by hand merely because the decision behind them has already been made. Refusing clerical work is not a safety property; it is friction that buys nothing.

If you believe the Doctrine genuinely forbids what the Owner is directing, stop and say so, citing the clause, and let the Owner decide. Do not proceed on your own reading, and do not treat your objection as an amendment to anything.

## This bundle is temporary and self-contained

Everything this skill needs is inside its own directory. It reads nothing from the Writwall repository and the target project never depends on Writwall (Doctrine 5.1.2).

The complete bundle must be local and readable **before the wall is
registered**. Do not install a hook and then rely on network retrieval for this
skill or its references: correct no-pointer lockout may deny that retrieval. If
you enter a project where the wall is already registered and this bundle is
missing, stop acting as the in-wall Implementer. Ask the Owner to use an
external authorized coordinator / recorder with a local Writwall source to
prepare the exact recovery lifecycle; never reconstruct the missing authority
from memory or weaken the wall.

```
writwall-adopt/
├── SKILL.md
├── references/
│   ├── DOCTRINE.md                        the methodology, for you, for this task only
│   └── migration-guides/                  followed only in migration mode
│       ├── 0.1-to-0.6.md
│       └── 0.6-to-0.7.md
└── assets/
    ├── adapters/claude-code/
    │   ├── README.md                      what the wall does and does not enforce
    │   └── wo_capability_wall.py          the adapter, installed unmodified
    ├── checks/
    │   └── check_work_order_dispatch.py   the pre-dispatch validator, installed unmodified
    └── templates/
        ├── A-charter.md   B-work-order.md   C-owner-brief.md
        ├── D-adoption-record.md            E-adoption-mapping.md
```

`assets/checks/check_work_order_dispatch.py` is the same deterministic, read-only pre-dispatch validator this repository uses on itself. It checks the between-work-order lockout state (`--lockout`), a candidate work order before pointer creation (`--work-order <path>`), or the currently activated work order and pointer (`--active`); it detects a missing, malformed, or mistargeted activation pointer, CRLF/non-UTF-8 work-order bytes, and an unsafe or malformed machine-readable grant. It never repairs, creates, or removes anything, and it is not the capability wall: it proves a work order is well-formed and correctly activated before a mutating session starts, not that any mutation channel is actually enforced during that session.

What this bundle carries is the methodology, the migration guides, the adapter, the pre-dispatch validator, and the templates. `LICENSE-MAP.md` states the license inherited by each bundled path. It carries none of Writwall's own working records, and you must never introduce any. Writwall's charter, governance directory, plan, state, routing map, decisions, work orders, reports, and history are that repository's records under Doctrine 5.1.5. They may be read as a worked example; they are never copied into a project you are bootstrapping, and they never carry authority over it.

**Make this complete bundle local before the wall is registered. Remove it from
the project's live agent surface before adoption completes.** Keep it until the
final bootstrap or recorder operation that needs it, then delete
`writwall-adopt/` before the adoption commit. Do not remove it merely because
Mode 1 entered lockout while Mode 2 still needs its exact instructions. It is a
bootstrap tool, not project context: leaving it in place after adoption would
put the doctrine inside the live corpus, which Doctrine 1.2.4 and 8.6.1 forbid.
What stays behind is what you installed into the project: the charter, the
adapter under the tooling directory, the pre-dispatch validator at
`checks/check_work_order_dispatch.py`, and `governance/`. Those are the
project's own files from that moment on.

After adoption, no Dispatcher, Implementer, or Reviewer invocation receives the doctrine. Never instruct a project workflow agent to read it, and never route to it (1.2.4). They receive the charter, the work order, routed Tier-2 material, and reports.

## Standing rules (non-negotiable)

1. Inventory before you change anything. Present the inventory and wait for the Owner's go-ahead before Phase B.
2. Intent-bearing material is never deleted. Superseded artifacts move to `governance/archive/` or `governance/history/` with a header stating why and when. In Mode 2, bootstrap-only residue that carries no intent may be removed, and only under the explicit disposition described there.
3. You do not dispose of intent-bearing documents (plans, specs, principles, prior decisions). You fill the Appendix E worksheet as PROPOSED rows. The Owner disposes. In Mode 2 you execute the disposition the Owner chose; you do not choose it.
4. You do not modify anything under the project's source, test, fixture, policy, or asset directories, in either mode. Bootstrap and closeout touch the charter file, the agent tooling directory (for Claude Code, `.claude/`), `governance/`, and the single adopter-facing `checks/check_work_order_dispatch.py` path only. If that checker path already exists, leave it untouched and report it as skipped.
5. In Mode 1 you make no commits, no pushes, and stage nothing. In Mode 2 you may stage the exact adoption set and make one local adoption commit, and only when the Owner has explicitly authorized that commit for this closeout. Pushing, tagging, publishing, changing repository visibility, and selecting a license are prohibited in both modes.
6. Every unknown becomes a numbered RFI in the report. Do not resolve unknowns by assumption.
7. You do not improve the doctrine, the templates, or the adapter. Observations go in the report.
8. If the Owner asks you to skip, weaken, or reinterpret the birth test, decline and cite 6.4.2 and 8.3.5; that refusal holds in both modes. In Mode 1, also decline to create DR-001 or make the adoption commit, citing 6.2 and 6.1.3 — and say plainly that both become available in Mode 2 once the Owner has supplied and ratified their content. Never decline an action merely because it is clerical.
9. Start birth testing with a minimal provider profile. Disable unrelated
   plugins, connectors, MCP servers, and delegation tools where practical. An
   external mutation tool is probed only against an explicit disposable
   fixture whose side effect, verification, and cleanup authority are named in
   the lifecycle packet. Authentication failure, provider rejection before hook
   dispatch, an unavailable tool, or an unprobed channel is **indeterminate, never a pass**.
   Never improvise against an ordinary live account object.

## Procedure (Mode 1: bootstrap)

**Inception identity gate.** Treat every supplied project, package, repository,
domain, product, or command name as a `working_candidate`. Before any such name
becomes canonical or public, use `assets/scripts/collect_name_clearance.py` to
create the seven-source evidence ledger, complete the named-human
web/common-law and USPTO reviews described in
`references/name-clearance.md`, and run the offline
`assets/checks/check_name_clearance.py`. Do not represent an unavailable source
as clear and do not run network searches merely because this bundle is local.
Return checker-clean evidence to the Owner for an explicit later disposition.
If identity is deferred or internal-only, record the future trigger: repeat the
gate before the first public repository slug, package name, domain, logo,
announcement, customer-facing use, or launch route. Command aliases are identity
surfaces and follow the same collision check.

**Phase A: Inventory.** Run `git log --oneline -20`, `git status --short`, list the agent tooling directory, and find any existing governance-like artifacts (charter files, hooks, work orders, governance directories, prior-revision templates). Identify the baseline commit candidate: the parent of the first commit that introduced any doctrine artifact, or HEAD if none. If the full Writwall distribution may have been overlaid into the target, stop ordinary bootstrap and use a separate clean distribution plus its `PROJECTION-MANIFEST.sha256`: classify byte-identical matches only as proposed overlay residue and every differing or pre-existing path as unknown. Propose an exact keep/remove/move disposition; delete nothing before the Owner ratifies it. Write `REMEDIATION-INVENTORY.md` at the repo root. Stop and present it.

**Phase B: Layout.** Create `governance/` per Doctrine 5.2 (`PLAN.md` is NOT created by you; `STATE.md` OBSERVED only; `ROUTING.md` proposed only; `decisions/`, `work-orders/`, `reports/`, `briefs/`, `rfis/`, `history/`, `archive/`, `LOG.md` with the 9.2 column header, `LOG-denials.jsonl` empty). Copy the templates from `assets/templates/` into `governance/templates/`. Move any prior-revision artifacts to `history/` or `archive/` with headers.

**Phase C: Charter.** If the tooling already auto-loads a file (Claude Code: `CLAUDE.md`), that file is the charter (5.2). Restructure it to the clause layout of `assets/templates/A-charter.md`, preserving every substantive line, and add at the top: "Doctrine rev [x], pre-adoption. This charter is in bootstrap. No work order under it is counted until DR-001 exists." Before wall registration or any Level 1 call, also copy the complete rule from `assets/bootstrap-charter-addendum.md` verbatim into that engine-visible charter. Ordinary no-pointer work remains forbidden. That temporary addendum is the sole bootstrap exception: it permits only the exact expected-denial calls named by a durably Owner-ratified lifecycle, solely so the wall can deny them; it confers no mutation authority, denial is the only valid outcome, and any success stops adoption. Verify the token budget (8.1.2); if over, report which section, do not trim.

**Phase D: Enforcement.** Install `assets/adapters/claude-code/wo_capability_wall.py` unmodified at `.claude/hooks/wo_capability_wall.py` only through the exact Owner-ratified adoption lifecycle after its authorization is durably recorded and verified. The adapter supports CPython 3.10-3.14. Register it for PreToolUse with matcher `*`, an explicit timeout, `${CLAUDE_PROJECT_DIR}`, and the native command: `py -3` on Windows or `python3` on POSIX. The adapter classifies tools itself so an unknown tool denies rather than silently escaping the wall. Never register an absolute path.

Also install `assets/checks/check_work_order_dispatch.py` unmodified at `checks/check_work_order_dispatch.py`, create-only: if the project already has a file at that path, leave it untouched and note it as skipped rather than overwriting it. This validator is a project-side convenience the Owner can run before activating a work order (Doctrine 6.4.1 step 8); it does not replace the capability wall and enforces nothing on its own.

**Operating envelope.** The wall is mechanically active only in sessions launched with the target repository as the **project root** and with its project `PreToolUse` hook visibly loaded. Claude Code loads project hooks from the project root and its settings hierarchy; a repository reachable only as an *additional working directory* is writable and unwalled at the same time. Run the installed adapter's read-only `--preflight` with its exact expected digest, project settings path, and native platform. Then confirm with `/hooks` that matcher `*`, project source, portable command, and timeout are loaded before probing. Startup or timeout non-invocation is not fail-closed. Create `governance/work-orders/WO-000-birth-test.md` from the example in `assets/adapters/claude-code/README.md`.

Inventory every mutation and network channel actually present in this installation before testing: mutation-capable built-in tools, provider-specific command tools, `WebFetch`/`WebSearch`, every connected MCP or plugin tool, every tool that delegates to another session, and any other tool that writes, publishes, schedules, or performs egress. Do not work from a fixed list. Cross-check against the six classification lists in the adapter README and record any installed tool missing from all of them.

Before probing, reduce that inventory to the smallest profile the project
actually needs. For any external tool that remains, require the Owner-ratified
explicit disposable target and cleanup procedure from standing rule 9. Do not
turn “inventory every channel” into authority to mutate every connected
service.

Run the README's birth-test sequence exactly, using only bootstrap-safe paths under `governance/`. Level 1 inventories no-work-order lockout; Level 2 records ordinary grant scope channel by channel. The source adapter requires exact `status: ACTIVE`, treats `WebFetch`/`WebSearch` as network egress, rejects root/traversal/symlink/junction/alias widening, and denies shell/delegation/MCP/unmodeled mutation channels that cannot prove the protected control plane unchanged. Those logic facts do not qualify a whole surface.

Doctrine 8.7 Level 3 requires an exact Owner-ratified birth-test instrument and durable lifecycle packet. A normal work order cannot grant a protected target. The instrument may name each exact target only as `control_plane_falsification_probe`; that label confers no authority, and the runtime must deny every probe through every exposed mutation-capable channel in a fresh native session on every platform the project will use. A portable Windows-and-POSIX claim requires both native legs. An unavailable unused platform is recorded as untested/indeterminate and leaves affected whole surfaces unenforced; it does not by itself block adoption after the actual environment passes Level 1 and the Owner accepts that boundary. Do not install settings, mutate the pointer, or activate the instrument under a work-order grant. An unavailable or indeterminate required probe blocks the claim made for that environment.

If the work order you are bootstrapping toward will declare `grant.filesystem.read.deny`, do not describe that surface as enforced until the adapter README's supplemental read-deny procedure has also been run: the Owner creates one sentinel file under a denied path with content withheld from you, adds that exact path to the grant, and a fresh session observes the modeled read tools (`Glob`, `Grep`, `LS`, `NotebookRead`, `Read`) deny it before content exposure while an allowed sibling read succeeds. You never receive or report the sentinel content. Keep every unqualified whole surface under `unenforced_boundaries`.

Copy `LOG-denials.jsonl` into the report, stating which probe produced each entry and that all of them are pre-adoption; the adapter writes one structured JSON record per denial and does not label entries as pre-adoption. Remove the active-WO pointer when done so the repository sits in lockout.

The no-pointer state may be re-established later through an authorized
lifecycle action and observed in a fresh session. Do not manufacture urgency or
call the first no-pointer window irreplaceable. Unplanned denials remain log
evidence but are not retroactively promoted into a birth test.

**Phase E: Dispatcher/Reviewer text.** Write `governance/dispatcher-reviewer-instructions.md` for the Owner to paste into their review model. In migration mode, use the text in `references/migration-guides/0.1-to-0.6.md` Part 7.3; otherwise derive it from Doctrine 4.2, 7.2.1, 7.6.1, and Appendix C. Supply the charter, work order, report, plan sections, and routed Tier-2 material to those roles. Do not tell them to read the doctrine.

**Phase F: Proposals.** Fill `governance/ADOPTION-MAPPING-PROPOSED.md` (Appendix E) with one PROPOSED row per intent-bearing or reference document, citing 6.3.2 through 6.3.5. Draft `governance/decisions/DR-001-DRAFT.md` from Appendix D with all Owner fields (D.2, D.7.1, D.8, D.9) left blank and marked. Bootstrap `STATE.md` OBSERVED only.

**Report.** Write `REMEDIATION-REPORT.md` at the repo root: inventory summary and baseline candidate; every artifact moved or created with old and new path and governing clause; exact hook registration; the mutation-channel inventory; birth certificates with their pre-adoption context; RFI list; observations; and the statement that nothing was committed, no source changed, and the repository is in lockout. Then stop.

Tell the Owner the remaining steps are the Owner's sequence in the Writwall `ADOPTING.md` section 5, and that they have two ways to finish it: perform the repository mechanics themselves, or supply the outstanding decisions and direct a Mode 2 recorder closeout. Say which decisions are still outstanding. Do not start Mode 2 in the same breath, and do not press for it.

## Mode 2: Owner-directed recorder closeout

You are the recorder. Every decision you record is the Owner's; every keystroke is yours.

### Entry conditions — all of them, verified, before anything else

1. Mode 1's report exists and the Owner has read it.
2. The Owner has explicitly directed a recorder closeout in this session, in their own words. Not implied, not inferred, not carried over.
3. The birth test has been run and recorded, and level 1 passed (6.4.2). If it did not, the project has not adopted and there is nothing to close out: stop and say so.
4. Every substantive decision in **Authority is not keystrokes** above is either supplied by the Owner or embodied in a specific draft the Owner has explicitly approved as written. Any gap stops the closeout for that gap alone.
5. Enforcement is resolved for this session. Bootstrap ends in lockout with no active pointer, so a walled session will deny every mutation until the Owner activates a grant. Ask the Owner to activate an uncounted bootstrap closeout work order naming exactly the closeout paths — the same instrument as `WO-000-birth-test.md`, and like it not a counted work order under 6.1.3 — or to state that enforcement is not yet installed. Where the wall is active, prove it live in this session with the Owner-named canary described in the adapter README before you mutate anything, and record the result.

### The decision packet — present it, then stop

Before touching a file, give the Owner one compact packet:

- each decision you are about to record, with its source: the Owner's own words, or the exact draft they approved;
- the exact file operations that follow, one line each: path, operation, and the decision it records;
- the exact commit message and the exact list of paths the commit will contain;
- the repository-relative path of the canonical durable lifecycle record, and
  the exact authorization text or packet digest it will contain before any
  protected lifecycle mechanic begins;
- whether the closeout ends by removing the active-WO pointer, and whether the Owner removes it or names that removal here for you to perform;
- anything still missing, stated as a question about the decision rather than about the edit.

Then stop and wait. The Owner's explicit statement in this conversation settles
the decision and may authorize you to record it, but chat alone is not the
durable lifecycle authorization required by Doctrine 8.7.6. Silence, a
filename, a draft, a prior conversation, and repository state are not
ratification, and you may not read them as such. After the Owner ratifies the
exact packet, first transcribe that authorization verbatim into the packet's
named canonical lifecycle record and verify the recorded text or digest. Do not
begin any protected lifecycle mechanic until that durable record exists.

### What you may execute after durable recording and verification

- Materialize `governance/PLAN.md` from the intent source the Owner identified, and archive the original with a header so two documents never both look authoritative (6.3.2).
- Execute every disposition in the adoption mapping exactly as the Owner dispositioned it (6.3.3 through 6.3.6).
- Finalize labels: drop PROPOSED and DRAFT markers from records the Owner has ratified, and rename the files accordingly.
- Write or rename `DR-001` (6.2). Owner-authored fields — D.8 reasoning, D.9 rejected alternatives — are transcribed **verbatim** from what the Owner supplied. You do not paraphrase, polish, complete, or infer them. A blank you cannot fill from the Owner's words is a question, not a gap to close.
- Update the bootstrap markers: remove the "pre-adoption / in bootstrap" line and the complete `assets/bootstrap-charter-addendum.md` text from the charter, and update `STATE.md` to the state you can observe.
- Remove bootstrap-only residue that carries no intent — `REMEDIATION-INVENTORY.md`, `REMEDIATION-REPORT.md` if the Owner dispositioned it, and this skill bundle — only where the Owner's disposition covers it. Intent-bearing material is still archived, never deleted (standing rule 2).
- Stage exactly the adoption set, and make one local adoption commit whose message names the baseline hash (2.25, 6.1.2). One commit, in this repository, and only if the Owner authorized it in the packet.
- Remove the active-WO pointer, returning the repository to lockout, and only where the ratified packet names that removal. Activating a work order is the Owner's decision (7.2.4), and so is ending one; the removal itself is a keystroke you may perform on their behalf once they have named it. Never infer that authority from a closeout that ended tidily, from a grant you consider spent, or from lockout being the correct resting state. If the packet does not name it, leave the pointer where it is and report it as outstanding for the Owner.

### What remains prohibited in Mode 2

Inventing or completing Owner intent; signing, ratifying, or deciding anything; weakening or skipping the birth test; pushing; tagging; publishing; changing repository visibility; selecting a license; touching project source; amending the Doctrine; and dispatching or beginning WO-001. The first counted work order is whatever the project genuinely needs next (6.1.4), and it is a separate Owner decision after adoption.

### Verify before you report

- the changed paths are exactly the packet's list — no more, no fewer;
- the project's own tests and checks pass, run as the project runs them;
- the commit contains exactly the adoption set, and you report its hash;
- nothing remains staged after the commit;
- the active-WO pointer is in the state the Owner directed: removed, so the repository sits in lockout, where the ratified packet named its removal; otherwise still in place and reported as outstanding;
- this skill bundle is gone from the skills directory. If the provider will not let a running skill delete its own bundle, say so plainly and ask the Owner to remove it.

### Closeout report

Report to the Owner: each decision recorded and whose words it came from; every path changed and why; the commit hash and its contents; the verification results above; the canary or enforcement state you observed; anything you declined and the clause behind it; and the RFIs still open. Then stop.

The Owner's ratification of the decision packet **was** the adoption decision. The commit and the mechanics above only record it. So when they have all succeeded, report completion plainly and stop — do not ask the Owner to confirm again what they have already ratified, and do not describe adoption as pending their further word. If any step did not succeed, say exactly which one and stop there instead; a closeout you cannot complete is reported, never assumed.

After a successful closeout report, present the exact handoff below for a fresh
Owner-Agent / Project-Architect, then stop. Do not continue as Architect, create
or dispatch a user-owned task, activate a work order, or begin product work in
the onboarding context. The fresh Architect may request task creation and
dispatch only by including them explicitly in its single combined approval
request.

```text
Act as a fresh Owner-Agent / Project-Architect. Begin read-only and verify
the lifecycle from repository bytes rather than prior chat. Read the charter,
Plan, State, Routing, ratified adoption record, and open transactional records.
State the project's next decision plainly. Draft, but do not activate or
implement, the smallest genuine work order or bounded external Operator packet.
Lead with a concise Recommendation and material tradeoff; keep the detailed
packet behind it as supporting evidence rather than the conversational front
door. When the next safe mechanical action is available, ask once for one
combined disposition and action. If that action uses a new user-owned task,
explicitly include creation and dispatch of the named task in that approval
request; never infer task-creation permission afterward. Once approved, perform
every mechanically available authorized step. Do not ask for the same decision again.
The human Owner alone ratifies intent and activates work; preserve a distinct
fresh review after implementation. The onboarding coordinator stops here and
does not continue into project work.
```

## Migration mode

If the Owner states the repository was bootstrapped under an earlier doctrine revision, look for `references/migration-guides/<from>-to-<to>.md` in this bundle and follow it instead of treating prior artifacts as unknowns. This bundle ships the 0.1-to-0.6 and 0.6-to-0.7 guides. Each requires the project's Owner to explicitly ratify migration before it is followed; neither runs on your own initiative. If no guide for the stated transition is bundled, say so, treat prior artifacts as Phase A inventory items, and propose dispositions; do not guess at what the earlier revision meant.
