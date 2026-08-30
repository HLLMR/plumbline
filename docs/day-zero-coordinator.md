# Day-zero coordinator

The day-zero coordinator is Writwall's single human entry point. It is a
standard-library Python command that runs from a clean Writwall source
distribution and prepares a temporary handoff inside the target project.

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

The command asks one question at a time. Its first question offers Owner-time
capture and tells you to start the timer before answering. It then offers an
existing brief-file path before asking you to restate the project purpose and
recommends the smallest credible role split before external functions are
assigned. Do not enter passwords, API tokens, private keys, mailbox contents,
DNS record values, or other secrets. The answers are stored as ordinary local
text.

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

## What it observes

The coordinator reads the target repository before assigning a role:

- no Writwall markers: clean/new bootstrap;
- incomplete Writwall-shaped material: recovery coordinator;
- adopted repository with no pointer: lockout and Dispatcher route;
- a valid pointer to an exact `status: ACTIVE` order: Implementer route;
- closed work in history with no pointer: retired lockout, never an active-
  Implementer continuation;
- malformed, missing, retired, or contradictory active state: stop without
  generating a handoff.

Repository bytes are authoritative for this observation. A prior chat message
or remembered work-order name is not lifecycle state.

## What it creates

The command refuses to run if `<project>/.writwall-bootstrap/` already exists,
including a dangling symlink, junction, or reparse entry. It also rejects
linklike lifecycle paths and stops when more than one ACTIVE work order exists.
It builds a complete temporary sibling on the same filesystem and publishes it
with one atomic directory rename; a caught pre-publication failure verifies
that the stage is gone and leaves no target output.
On success that temporary, create-only directory contains:

- `HANDOFF.md`: observed state, role routing, exact next prompt, authority
  boundaries, and optional Owner-time instructions;
- `intake.json`: machine-readable, explicitly unratified answers;
- `discovery.json`: complete idea qualification and deterministic unratified topology;
- `OWNER-AGENT.md`, `REPOSITORY-OPERATOR.md`, and `REVIEWER.md`: exact,
  separately bounded role prompts;
- `NAME-CLEARANCE.md` and `OWNER-RATIFICATION.md`: identity and Owner gates;
- `writwall-adopt/`: the complete local adoption skill bundle;
- `operations/*.md`: inert packet scaffolds for separately named external
  Operator functions.

The bundle remains local until the authorized recorder no longer needs it and
is removed before the adoption commit. The command does not modify an existing
project file, register a hook, create `.claude/active-wo.txt`, or claim the
project has adopted Writwall.

## Roles and external systems

The human remains Owner. The Owner-Agent coordinates, drafts, routes, records
ratified decisions, and performs exactly authorized lifecycle mechanics. A
repository Operator works under one active work order. An infrastructure,
DNS, mail, deployment, or other external Operator receives a bounded packet
and returns evidence; it remains outside the repository wall unless it edits
repository bytes. A fresh Reviewer checks the relevant order, result, report,
and returned evidence.

The Owner-Agent keeps the proverbial keys—authority and routing—not literal
passwords or cryptographic material. External packets separate preconditions,
permitted and prohibited actions, verification, rollback, evidence, and
credential handling. Blank packet fields authorize nothing.
An operation-packet scaffold confers no authority by itself.

## Owner active minutes

If enabled, capture starts when the first intake question appears and stops
when the coordinator returns the ratifiable adoption packet or next-work-order
candidate. Count human reading, deciding, responding, authentication, and
unavoidable UI work. Exclude agent execution and waiting. If capture is
declined, the handoff records `NOT REPORTED`; no later agent reconstructs it.

The manual routes remain in [`START-HERE.md`](../START-HERE.md) and
[`ADOPTING.md`](../ADOPTING.md) for environments without a supported Python
runtime or for recovery that requires an external coordinator.
