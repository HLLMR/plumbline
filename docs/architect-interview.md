# Architect interview

The Architect is the conversational first stage of Writwall's one canonical lifecycle;
it is not a second adoption route. For a new or clean project,
`writwall start --project-root <project>` is the idea-first front door. By default — with only
`--project-root` — it is conversation-first: it asks nothing on the command
line and never blocks on stdin. For an existing project it hands a fresh
Architect a bounded, local, non-secret inventory (Git branch, cleanliness, a
few recent commit subjects, and top-level project-relative names); the
Architect begins read-only, uses that evidence before asking the Owner to
restate anything already visible in repository bytes, summarizes what it
found, and asks whether to explore that work or start elsewhere. For a
genuinely empty target it opens with exactly: "Tell me what you are
thinking," and imposes no fixed question list. A supplied project or command
name is always a `working_candidate`; generated files never make it
canonical, available, cleared, or accepted.

For an existing project where the human wants conversation before any
bootstrap write, use `writwall inspect --project-root <project> --role
architect`. It prints a fresh Architect handoff from bounded lifecycle
evidence and changes no project or local state. It also provides the explicit
Architect re-entry path after adoption. This role selection is conversational,
not authority: it does not adopt, activate, implement, or alter lifecycle.

If the Owner promotes the resulting project sketch, adoption materialization
ends by handing the ratified repository to a fresh General. The Architect does
not continue as that General, and either role routes bounded work to Operators
rather than implementing by conversational momentum.

Add `--structured-intake` (or `--non-interactive` with the matching flags)
to run the former full structured questionnaire instead. It may begin with
an unnamed idea or a supplied brief. In that mode, the deterministic
coordinator asks one question at a time and records the problem or
opportunity, intended user, why the outcome matters, current evidence and
assumptions, smallest useful outcome, success signal, constraints,
non-goals, material risks, stop or kill conditions, existing assets,
repository/runtime/deployment environment, preferred agent/interface,
external systems and Operators, and optional Owner-time capture. These
answers remain unratified until the Owner explicitly accepts, rejects, or
revises them.

The output separates adaptive judgment from mechanics:

- `discovery.json` is the complete unratified qualification record. In the
  conversation-first default it also carries `local_observations` (bounded
  local evidence, kept separate from Owner-supplied statements) and
  `unresolved_questions`;
- `ARCHITECT.md` is the exact prompt for continued adaptive architecture: it
  owns pre-adoption discovery and later design-conformance judgment. Before
  requesting promotion into adoption mechanics, the Architect returns a
  concise project sketch, a recommended Owner/Architect/General/Operator
  topology, a provisional first backlog, key uncertainties and risks, and
  one explicit Owner promotion decision. If the idea stays exploratory or is
  rejected, no adoption, work order, or construction control is created;
- `GENERAL.md` is the exact prompt for post-adoption continuity: preparing
  bounded dispatch, routing work, and performing only explicitly authorized
  recorder mechanics;
- `OPERATOR.md` is inert until a ratified plan and active work order;
- `OWNER-AGENT.md` and `REPOSITORY-OPERATOR.md` are compatibility aliases
  for `ARCHITECT.md` and `OPERATOR.md`, kept for existing consumers of those
  two filenames;
- `REVIEWER.md` keeps fresh review separate from implementation;
- `NAME-CLEARANCE.md` routes the canonical seven-source evidence process; and
- `OWNER-RATIFICATION.md` is the explicit stop before implementation.

Every one of these packets, plus `discovery.json` itself, carries the same
one resolved canonical project root; see
[`day-zero-coordinator.md`](day-zero-coordinator.md#canonical-project-root)
for the invariant and its Git-worktree handling.

Topology is deterministic advice. Local-only work receives the smallest local
role set. External account boundaries add separately bounded Operator packets.
Production, identity, DNS, or mail boundaries receive a high-impact topology
whose operation packets retain independent preconditions, authority,
verification, rollback, credential boundaries, and returned evidence. One
agent may act sequentially as Architect and Operator on a small project only
in separate sessions after Owner ratification. The human Owner and a fresh
non-implementing Reviewer remain separate roles.

Command names and aliases are identity surfaces. Before adding an alias, record
collision evidence through the same inception name-clearance route; do not
invent a short alias merely for ergonomics. The canonical executable for this
release is `writwall start`.

The coordinator performs no network search, implementation, repository
creation, provider setup, credential handling, deployment, DNS change, or mail
operation. It publishes one create-only directory atomically or stops without
overwriting target bytes.
