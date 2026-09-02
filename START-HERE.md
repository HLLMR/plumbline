# Start here: the human operating guide

You do not need to understand the Doctrine before beginning. You need to know
which role you are talking to, where that agent is running, and what decision
belongs to you.

The safest default is: **prepare adoption with a coordinator before opening a
walled Implementer session.** Make the self-contained `writwall-adopt` bundle
local before the wall is registered. The wall may intentionally deny network
access once the project enters lockout; an agent cannot fetch instructions it
does not already have.

## Who does what

| Function | Who or what performs it | May share an agent? |
|---|---|---|
| **Owner** | You. You decide intent, ratify records, authorize lifecycle actions, and accept results. | Never delegated. |
| **Adoption coordinator / recorder** | A chat or coding agent that can inspect the project and prepare or record your decisions. During recovery it runs outside the walled Implementer grant. | May also act as Dispatcher on a small project. |
| **Dispatcher** | Turns ratified Plan intent into one bounded work order. | May be the coordinator in a fresh turn or session. |
| **Implementer** | The coding agent operating inside the project with one active work order. | Does not review or authorize its own work. |
| **Reviewer** | A fresh read-only agent given the work order, report, and changed result. | Use a fresh session with no implementation role; a different provider is optional, not required. |

These are functions, not permanent job titles. One model can perform several
functions sequentially for a small project, but it does not carry authority
between them and does not review its own implementation in the same context.

## Pick an operating model

### Small project

Use one capable coordinator for interviewing, dispatch drafting, and recorder
mechanics; use your IDE coding agent as the walled Implementer; open a fresh
session for Reviewer work. This is the lightest credible arrangement.

Talk first to the coordinator outside the walled IDE, or to the IDE agent
**before** any project hook is registered. Give it the public Writwall source
or the complete local adoption bundle.

### Split-role project

Use an external adoption coordinator / recorder (for example a general-purpose
coding task or chat with repository access), a walled Implementer inside the
IDE, and a fresh Reviewer. This is the recommended path when the wall is
already installed, the repository has substantial existing intent, or the IDE
session cannot perform protected lifecycle mechanics.

### Provider-neutral

Use any capable model for coordinator, Dispatcher, Implementer, and Reviewer
functions. Without a birth-tested provider adapter, the grants are
instruction-bounded rather than mechanically enforced. The records and review
flow still work; describe the enforcement boundary honestly.

## Normal path: start before the wall is registered

If this is a new project and its public name is not already settled, run the
[inception name-clearance gate](docs/name-clearance.md) before creating package
names, repository slugs, domains, logos, or launch copy. The coordinator may
collect evidence, but the Owner chooses the identity; unavailable sources are
not clear results.

1. Release candidate `v0.9.3` contains the terminal Architect handoff but is
   not yet published. After publication, install it without unpacking it over
   your project; until then, use the checked source-tree fallback below:

   ```text
   python -m pip install "https://github.com/HLLMR/writwall/archive/refs/tags/v0.9.3.zip"
   ```

   Release `v0.9.0` first introduced the coordinator. Release `v0.9.1` corrected
   first-use bytecode residue. Release `v0.9.2` corrects the bootstrap
   expected-denial contract. Release candidate `v0.9.3` adds lifecycle-aware
   routing and the terminal Architect handoff.
   If you are testing an unpublished release candidate, use its checked external
   candidate tree and the release gate in `PUBLICATION.md`.
2. Run one command:

   ```text
   # Installed command
   writwall start --project-root /path/to/your-project

   # Source-tree fallback on Windows
   py -3 scripts/start_writwall.py --project-root C:\path\to\your-project

   # Source-tree fallback on macOS or Linux
   python3 scripts/start_writwall.py --project-root /path/to/your-project
   ```

   The same command is the entry point throughout the project lifecycle:

   | Observed state | Fresh role receiving the output | Session that stops | May target bytes change? |
   |---|---|---|---|
   | Clean/new | Adoption coordinator | The human's current launcher returns after creating the bootstrap; the adoption coordinator later stops at closeout | Yes: create-only `.writwall-bootstrap/` |
   | Partial bootstrap or recovery | Recovery coordinator | The incomplete adoption or locked session | No |
   | Adopted or retired lockout | Owner-Agent / Project-Architect | The onboarding coordinator or prior work session | No |
   | Active work order | Bounded Implementer | Any prior coordinator or Implementer context | No |
   | Malformed or contradictory | No role; precise stop diagnostic | The invoking session | No |

3. If you choose to track Owner active minutes, start the timer when the first
   question tells you to; do not reconstruct time later. Answer one question at
   a time without entering secrets. You may point it at an existing brief. The
   command observes actual repository lifecycle state. Only a clean/new target
   enters intake, creates `<project>/.writwall-bootstrap/`, and initializes a
   durable local privacy screen outside the repository. Later valid states emit
   a fresh-role prompt without changing target bytes. Add only private names, codenames, client
   identifiers, or domains; never add credentials or secret values. See
   [`docs/privacy-screen.md`](docs/privacy-screen.md).
4. Open its `HANDOFF.md`. Start the agent and location it names and paste the
   exact prompt. The complete local `writwall-adopt` bundle is already beside
   the handoff.
5. Keep that temporary directory until recorder closeout no longer needs it;
   remove it before the adoption commit. Register and birth-test the wall only
   through the exact lifecycle the coordinator prepares and you ratify.

The command does not install Writwall, interpret intake as ratified intent,
create an activation pointer, contact an external system, or replace the
Owner-Agent. It stops on contradictory state instead of guessing from prior
chat. See [`docs/day-zero-coordinator.md`](docs/day-zero-coordinator.md) for
the complete contract.
It may start with an unnamed idea; see
[`docs/architect-interview.md`](docs/architect-interview.md) for qualification,
identity, topology, and role-packet behavior.

### Manual fallback

If Python is unavailable, copy the complete `skills/writwall-adopt/` directory
into a temporary project-local location before registering any wall, confirm
it is readable, then use the prompt below. For Claude Code, a temporary
`.claude/skills/writwall-adopt/` location is supported. Keep the bundle until
the final authorized recorder action that needs it and remove it before the
adoption commit.

Paste this first:

```text
Act as my Writwall adoption coordinator, not as an Implementer. Use the local
writwall-adopt bundle and follow its bootstrap mode. I decide and ratify; you
perform every clerical step an authorized recorder may perform. Ask me one question at a time
in plain language, with your recommendation first.
Do not install or register the wall until you have confirmed that the complete
bundle and recovery instructions are locally available. Do not begin product
work or ask about WO-001 until adoption is complete.
```

## If the archive was already unpacked into your project

Stop before deleting or continuing. Do not assume every Writwall-looking file
is disposable: an existing project may already have a `README.md`, `CLAUDE.md`,
`.github/`, `checks/`, or governance material of its own.

Use a separate clean Writwall distribution and an external coordinator to
inventory the overlay. Compare candidate files with that clean distribution's
`PROJECTION-MANIFEST.sha256`; treat byte-identical matches only as proposed
overlay residue, and treat every differing or pre-existing path as unknown.
The coordinator proposes an exact keep/remove/move disposition. You ratify it;
an authorized recorder may then perform those exact mechanics. Never run a
blanket delete or unpack a second archive over the first.

Paste this recovery prompt:

```text
Act as my Writwall accidental-overlay recovery coordinator. Inventory only;
do not delete, overwrite, move, install, or register anything. Compare this
project against a separate clean Writwall distribution and its manifest.
Classify exact matches as proposed overlay residue and every differing or
pre-existing path as unknown. Give me an exact disposition packet and ask one
question at a time. Do not begin adoption until I ratify the recovery packet.
```

If your coding agent supports skills, the shorter invocation is:

```text
Use the writwall-adopt skill. Bootstrap this repository for Doctrine 0.8
adoption. Baseline commit candidate: determine and propose. Ask one question at
a time and do not begin product work.
```

## Recovery path: already-installed lockout

If `.claude/active-wo.txt` is absent and the wall denies mutation or network
access, **stop using that session as the coordinator**. That session is behaving
as a walled Implementer in lockout. Do not weaken the hook, invent a pointer, or
ask it to fetch missing instructions.

Open an external coordinator / recorder with access to the target repository
and the downloaded Writwall source, then paste:

```text
Act as my Writwall adoption coordinator for an already-installed lockout, not
as the walled Implementer. The target has a registered wall and no active-work-
order pointer. Use the local public Writwall source; do not ask the locked
session to fetch it or bypass the wall. Inventory the incomplete adoption,
prepare the exact birth-test and recorder lifecycle packets, and ask me one
question at a time in plain language. I ratify decisions; after exact
ratification, first record my authorization verbatim in the packet's named
durable lifecycle record and verify it. Only then perform the protected
repository mechanics named in that record on my behalf. Do not probe any
external service unless I have named a disposable target and cleanup authority
in advance. Do not begin WO-001.
```

An authorized lifecycle action may remove a pointer and re-establish the no-
pointer state for a fresh Level 1 session. The condition is not a one-time
window. Unplanned denials remain honest log evidence, but unplanned denials are
not retroactively promoted into a birth test.

## Make the birth test safe

Before registering the wall or starting Level 1, confirm the provider's
engine-visible pre-adoption charter contains the complete text of
`assets/bootstrap-charter-addendum.md` from the local adoption bundle. That temporary
rule resolves the bootstrap boundary without weakening it: ordinary no-pointer
work remains forbidden, while exact calls named by a durably Owner-ratified
birth-test lifecycle may be dispatched solely so the wall can deny them. The
attempt confers no mutation authority; denial is the only valid outcome, and
any success stops adoption. Remove the addendum before the adoption commit.

Start with a **minimal provider profile**. Disable unrelated plugins,
connectors, MCP servers, and delegated agents before inventorying the mutation
surface. If an external mutation tool must remain available, test it only when
the lifecycle packet names an **explicit disposable fixture**, expected side
effect, verification method, and cleanup authority.

Never aim a first-run probe at ordinary Drive, Notion, Figma, email, calendar,
deployment, or production objects. Authentication failure, provider rejection
before hook dispatch, an unavailable tool, or an unprobed channel is
**indeterminate, never a pass**. Reduce the active surface or retain the honest
unenforced classification.

The human may need to perform genuinely interactive provider actions such as
viewing Claude Code's `/hooks`, completing authentication, or privately creating
a read-deny sentinel. Those are exceptions. File creation, pointer changes,
validation, Git mechanics, and recorder closeout are not automatically human
chores; an exactly authorized recorder may perform them.

## Recorder closeout prompt

After the coordinator presents the exact decision and lifecycle packet and you
agree with every substantive decision, ratify that exact packet. Then say:

```text
Enter writwall-adopt recorder closeout mode. Record only the exact packet I
ratified. First durably record this authorization in the packet's named
lifecycle record and verify it; a chat exchange alone is not lifecycle authorization.
Then perform the authorized clerical operations and local
adoption commit on my behalf; do not infer or improve my decisions. Remove the
temporary bootstrap bundle before the adoption commit, return the project to
lockout, and do not dispatch WO-001.
```

## Terminal Project-Architect handoff

Adoption closeout ends the onboarding session. After the adoption commit, open
a fresh Owner-Agent / Project-Architect and paste exactly:

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

The Architect leads with a concise recommendation and material tradeoff; its
detailed packet remains supporting evidence. If the next safe step can be done,
its one approval request includes both the disposition and that action. Creating
a new user-owned task must be explicitly included in that request. Once you
approve it, the Architect performs every authorized mechanical step available
without asking the same question again. It still does not infer ratification,
activate a work order it was told only to draft, or implement product work.

After you separately approve and activate a work order, start a fresh Implementer:

```text
Act as a fresh Implementer for the active work order only. Confirm the active dispatch
and required live-wall canary before mutation. Execute the order, preserve RED
and GREEN evidence, write its report, and stop before acceptance or closeout.
```

For review, start a fresh session:

```text
Act as a read-only Reviewer. Review the active work order, implementation diff,
test evidence, and report for conformance and record truth. Do not implement a
fix. Return ACCEPT or specific findings with severity and evidence.
```

The complete adoption contract, artifact sequence, and provider-specific birth
test details are in [ADOPTING.md](ADOPTING.md). Read those after choosing the
operating model above.
