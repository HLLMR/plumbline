# Day-zero coordinator

The day-zero coordinator is Writwall's single human entry point across the
project lifecycle. It is a standard-library Python command that runs from a clean Writwall
source distribution. It prepares a temporary handoff inside a clean/new target
or prints a zero-write fresh-role handoff for every later valid state.

It is intentionally smaller than an AI agent. It does not interpret intent,
install a capability wall, ratify adoption, activate a work order, contact a
provider, or mutate production. It makes the complete adoption bundle local,
records unratified intake, observes repository lifecycle state, and tells the
human which agent to open next and what to paste.

## Run it

Use the installed command, or run the preserved fallback from an unpacked
Writwall source directory rather than an overlaid target:

```text
# Installed command
writwall start --project-root /path/to/your-project

# Source-tree fallback on Windows
py -3 scripts/start_writwall.py --project-root C:\path\to\your-project

# Source-tree fallback on macOS or Linux
python3 scripts/start_writwall.py --project-root /path/to/your-project
```

By default — with only `--project-root` — the command is conversation-first:
it asks nothing on the command line and never blocks on stdin. It observes
the target, fills every required field from local evidence and plain
defaults, and hands the result to a fresh Architect. Do not enter passwords,
API tokens, private keys, mailbox contents, DNS record values, or other
secrets in any explicit flag you do supply; answers are stored as ordinary
local text.

Add `--structured-intake` to run the former full questionnaire instead: it
asks one question at a time. Its first question offers Owner-time capture
and tells you to start the timer before answering. It then offers an
existing brief-file path before asking you to restate the project purpose,
and recommends the smallest credible role split before external functions
are assigned.

Before publishing the bootstrap handoff, the coordinator creates or refreshes
the target's managed privacy screen outside the repository. It seeds exact
machine-path sentinels automatically and offers optional private
name/codename/client/domain collection. It requires an explicit no-secrets
confirmation and rejects common credential-shaped assignments and private-key
headers, but it cannot recognize every arbitrary secret. It writes only screen
readiness and entry count into the handoff.
See [`privacy-screen.md`](privacy-screen.md).

For deterministic automation or testing of an existing brief, use
`--non-interactive` together with `--project-name`, either `--purpose` or
`--brief-file`, `--agent`,
`--location`, `--environment`, `--owner-time yes|no`, and
`--confirm-no-secrets`. Repeat
`--external-operator` for each separately governed external function. Run
`--help` for the complete interface.

For an unnamed idea, omit `--project-name` and supply `--problem`,
`--intended-user`, `--why-matters`, `--evidence`, `--smallest-outcome`,
`--success-signal`, at least one each of `--constraint`, `--non-goal`, `--risk`,
`--kill-condition`, and `--asset`, plus the environment/interface fields above.
Interactive use asks these one at a time. See
[`architect-interview.md`](architect-interview.md).

`--scenario dns-mail-migration` provides a sanitized five-packet starting
shape: move authoritative DNS for eight domains first, verify it, then change
mail routing, while historical mailbox inventory/cleanup/migration remains a
separate function. It supplies no provider, domain, account, record, or mailbox
value.

## What it observes and routes

The coordinator classifies before intake or privacy initialization:

| Human command | Observed state | Fresh role receiving output | Prior session stops | Target bytes |
|---|---|---|---|---|
| `writwall start --project-root <project>` | No Writwall markers | Architect (conversation-first) | Launcher returns; the Architect stops before adoption mechanics until the Owner promotes | Create-only bootstrap may be added |
| `... --structured-intake` | No Writwall markers | Adoption coordinator | Launcher returns; coordinator later stops at closeout | Create-only bootstrap may be added |
| Same command | Partial `.writwall-bootstrap/` or Writwall-shaped material | Recovery coordinator | Incomplete adoption or locked session | Unchanged |
| Same command | Adopted or retired lockout | Fresh General (the continuity role previously labeled Project-Architect) | Onboarding coordinator or prior work session | Unchanged |
| Same command | Exact pointer to the only `status: ACTIVE` order | Bounded Operator/Implementer | Prior coordinator or Implementer context | Unchanged |
| Same command | Malformed, missing, retired, or contradictory active state | No role; precise diagnostic | Invoking session | Unchanged |

Repository bytes are authoritative for this observation. A prior chat message
or remembered work-order name is not lifecycle state.

### Conversation-first opening

For a clean/new target, the ordinary (non-`--structured-intake`,
non-`--non-interactive`) invocation gathers a deterministic, local-only,
bounded inventory before handing off: whether a Git repository is present,
its current branch, a best-effort clean/dirty label (only when a `git`
executable is on PATH; left unobserved otherwise), a few recent commit
subjects read from the local reflog, and a one-level, project-relative
listing of top-level entries — never file contents, never a path outside
the resolved project root, and never a linked-worktree `gitdir:` pointer
followed outside that root. Common dependency/build/cache directories are
skipped.

If that inventory finds existing work, the Architect opening begins
read-only, uses the recorded evidence before asking the Owner to restate
anything already visible in repository bytes, summarizes the apparent
project in plain language, and asks whether the Owner wants to explore that
work or start elsewhere. If the target is genuinely empty, the opening
imposes no fixed question list and reads exactly: "Tell me what you are
thinking." Neither observation is ratified intent; `discovery.json` records
it under `local_observations`, kept separate from Owner-supplied statements,
alongside a deterministic, explicitly `unratified_recommendation` topology
and a short `unresolved_questions` list.

Adopted and retired lockout require affirmative, internally consistent
ratification evidence from `governance/decisions/DR-001.md` or the supported
alternate `governance/ADOPTION-RECORD.md` path, not merely one of those paths
existing, and not merely carrying a Signature, an Owner, and a date -- a
signed document that is not an adoption record at all does not qualify
either. The coordinator requires each candidate to carry an Appendix D
adoption-record title, all of sections D.1 through D.9, a concrete D.2
baseline commit (a 7-40 character hex identifier) with adoption-effective
language, a D.3 Doctrine revision, and a Signature section with an Owner
attribution and a date, with no unresolved `- [ ]` outstanding-checklist
item and no draft/proposed/pending/unsigned/placeholder status signal in the
fields where ratification status actually lives (its headings, D.1, D.3, and
Signature). Closed work-order history alone never establishes adoption, and
an unrelated ratified decision -- whether at a different path or, this
being the specific defect this classifier closes, sitting at the exact
adoption-record path itself -- never satisfies it. An explicit draft/
unsigned candidate routes to recovery; a candidate that is signed but not a
recognizable, complete adoption record fails closed with a diagnostic that
names only the path, never its contents, instead of reporting adopted or
retired lockout. When both adoption-record paths coexist, the coordinator
accepts them only if both are ratified and agree on baseline, Doctrine
revision, and Owner; otherwise it fails closed.

## What it creates

Only clean/new mode performs intake, initializes privacy, or creates target
bytes. In that mode, the command builds a complete temporary sibling on the
same filesystem and publishes it with one atomic directory rename; a caught
pre-publication failure verifies that the stage is gone and leaves no target
output. On success that temporary, create-only directory contains:

- `HANDOFF.md`: observed state, local evidence (conversation-first mode
  only), role routing, exact next prompt, authority boundaries, and optional
  Owner-time instructions;
- `intake.json`: machine-readable, explicitly unratified answers;
- `discovery.json`: local observations, Owner-supplied statements,
  unresolved questions, and a deterministic unratified topology
  recommendation, kept in separate, explicitly labeled sections;
- `ARCHITECT.md`, `GENERAL.md`, and `OPERATOR.md`: the primary, exact,
  separately bounded role prompts for pre-adoption discovery and
  design-conformance judgment, post-adoption continuity and dispatch, and
  bounded work-order execution, respectively;
- `OWNER-AGENT.md` and `REPOSITORY-OPERATOR.md`: compatibility aliases for
  `ARCHITECT.md` and `OPERATOR.md`, kept for existing consumers of those two
  filenames;
- `REVIEWER.md`: a fresh, separate review function;
- `NAME-CLEARANCE.md` and `OWNER-RATIFICATION.md`: identity and Owner gates;
- `writwall-adopt/`: the complete local adoption skill bundle;
- `operations/*.md`: inert packet scaffolds for separately named external
  Operator functions.

An existing partial `.writwall-bootstrap/` is recovery evidence: it is never
overwritten or republished. Linklike lifecycle paths, multiple ACTIVE work
orders, and other contradictions fail closed before any write.

The clean/new bundle remains local until the authorized recorder no longer needs it and
is removed before the adoption commit. The command does not modify an existing
project file, register a hook, create `.claude/active-wo.txt`, or claim the
project has adopted Writwall.

## Canonical project root

The coordinator resolves the Owner-supplied target directory once and records
that one resolved, absolute path as the canonical project root in
`intake.json`, `discovery.json`, `HANDOFF.md`, every Architect/Operator/
Reviewer/ratification/name-clearance packet, and every external-Operator
packet. A portable relative path or a bare `.` is never a substitute for this
identity: a receiving agent must be able to locate the one real project
directory from any single generated file, not from the working directory an
agent happens to be launched in.

If the supplied directory sits inside a Git worktree, the coordinator
discovers the worktree top level (from the `.git` entry itself, without
requiring a `git` executable) and uses it only when the supplied path *is*
that top level. A directory nested inside a worktree, but not its top level,
stops before any privacy or bootstrap write with a diagnostic naming the
discovered root; rerun with `--project-root` set to that exact directory. A
non-Git directory remains fully supported and is recorded canonically as
supplied.

Durable project artifacts — governance records, source, plans, reports, and
work orders — belong under this one canonical root. Three other kinds of
storage are explicitly not that: the OS-local privacy screen (per-user state
outside the repository, location never disclosed); this bootstrap directory
and any other temporary staging (bounded evidence or atomic publication
bytes, removed after use); and an external Operator's own evidence staging
(returned sanitized evidence is incorporated under the canonical root by the
General or a separately authorized repository Operator, never a shadow
repository the external Operator creates on its own).

## Roles and external systems

The human remains Owner. The **Architect** owns pre-adoption discovery and
later design-conformance judgment: it interviews, drafts, routes, and
performs exactly authorized lifecycle mechanics. After adoption, a fresh
**General** owns continuity — preparing bounded dispatch, routing work, and
performing only explicitly authorized recorder mechanics — without ratifying
intent or judging design conformance itself. An **Operator** works only
under one active, Owner-ratified work order. An infrastructure, DNS, mail,
deployment, or other external Operator receives a bounded packet and returns
evidence; it remains outside the repository wall unless it edits repository
bytes. A fresh **Reviewer** checks the relevant order, result, report, and
returned evidence. `OWNER-AGENT.md` and `REPOSITORY-OPERATOR.md` remain as
compatibility aliases for the Architect and Operator packets.

The Architect and General keep the proverbial keys—authority and
routing—not literal passwords or cryptographic material. External packets
separate preconditions, permitted and prohibited actions, verification,
rollback, evidence, and credential handling. Blank packet fields authorize
nothing. An operation-packet scaffold confers no authority by itself.

## Owner active minutes

If enabled, capture starts when the first intake question appears and stops
when the coordinator returns the ratifiable adoption packet or next-work-order
candidate. Count human reading, deciding, responding, authentication, and
unavoidable UI work. Exclude agent execution and waiting. If capture is
declined, the handoff records `NOT REPORTED`; no later agent reconstructs it.

For adopted/retired lockout, the printed General prompt begins read-only,
derives lifecycle from bytes, keeps detailed packets behind a concise
recommendation and material tradeoff, and requests one combined disposition
and safe next action. If that action requires a new user-owned task, the
request explicitly includes creation and dispatch. Approval triggers every
mechanically available authorized step without a redundant permission turn;
it never erases Owner ratification or fresh review.

The manual routes remain in [`START-HERE.md`](../START-HERE.md) and
[`ADOPTING.md`](../ADOPTING.md) for environments without a supported Python
runtime or for recovery that requires an external coordinator.
