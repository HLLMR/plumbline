# Claude Code adapter: wo_capability_wall.py

Reference enforcement adapter for Doctrine 8.3. Read this whole file before trusting the hook.

This README is the maintained operational statement for the adapter. It is kept synchronized with the script's module docstring and with the tool-classification constants in the script; the deterministic check in `checks/check_distribution.py` fails if the coverage block below and the script's constants disagree. The two texts are synchronized, not identical, and neither is a verbatim copy of the other.

---

## Enforcement operating envelope, read first

> Writwall's Claude Code wall is mechanically active only in sessions launched with this repository as the project root and with its Project `PreToolUse` hook visibly loaded. A session in which Writwall is merely an additional working directory does not load this hook and is outside the enforced operating envelope. Such a session must not mutate Writwall; that prohibition is instruction-only and is not represented as a wall.

Substitute your own project for "Writwall" when you install this adapter elsewhere. The envelope is a property of how Claude Code loads hooks, not of this repository.

Current provider behavior this depends on:

- **Project hooks load from the project root** and its applicable settings hierarchy. The project root is the directory Claude Code was launched in.
- **Additional working directories provide file access but do not load their hooks.** A repository reachable through `--add-dir` is writable and unwalled at the same time.
- **`${CLAUDE_PROJECT_DIR}` is supplied to hook commands**, so a registration never needs a machine-specific absolute path.
- **`/hooks` displays the loaded hook, its source, and its command**, which is how you confirm the envelope before testing inside it. It is necessary configuration evidence and not proof of live enforcement; see [the live-wall canary](#the-live-wall-canary) for what proof requires.
- **Some tool calls are rejected by provider input validation before `PreToolUse` dispatch.** A malformed call never reaches the hook and produces no denial record. This is why a canary must be a genuinely valid, mutation-capable call.

This was not theoretical. On 2026-08-16 a Level 1 birth test in this repository failed for exactly this reason: the hook was registered here while the session's project root was elsewhere, so it never loaded, and a `Write` with no active work order succeeded.

## Provider limitation

**This hook cannot make its own availability physical.** Current Claude Code command-hook behavior is not fail-closed on hook startup failure or timeout. A hook that cannot start, that times out, or that exits with a non-blocking status and no valid deny payload does not block the tool call. The adapter's ordinary denials use Claude Code's documented structured `permissionDecision: "deny"` response with exit 0; exit code 2 is the hard blocking fallback for malformed input and unexpected exceptions.

The consequence is precise and must be recorded in the adoption record rather than glossed:

- The adapter **can** fail closed for the errors it catches: unparseable hook events, unreadable or unsafe work-order pointers, malformed frontmatter, missing or invalid grants, unsupported path syntax, unmodeled tools.
- The adapter **cannot** fail closed on its own non-execution. If the interpreter is missing, the file is deleted, the command line is wrong, or the hook exceeds its timeout, the tool call is not blocked by this adapter.

A project that requires the stronger guarantee must add a provider layer with independently verified fail-if-unavailable semantics and repeat the birth test (8.3.5) against that layer. Claude Code currently exposes sandbox settings including `sandbox.enabled`, `sandbox.failIfUnavailable`, and `sandbox.allowUnsandboxedCommands: false`. **This repository does not install or configure them, and their platform support must be verified before they are relied upon.** A setting name that is wrong, unsupported on your platform, or silently ignored is the worst failure this clause can have: it produces the appearance of a wall with none of the physics. Verify against current documentation, then birth-test.

Reference documentation, to be re-checked at each birth test:

- https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/tools-reference
- https://code.claude.com/docs/en/configuration
- https://code.claude.com/docs/en/sandboxing

---

## What it makes physical (mechanically enforced)

1. **No-work-order and lifecycle lockout** (Doctrine 7.3.2, 8.3.5.1). With no valid `.claude/active-wo.txt`, every modeled mutation-capable tool is denied. A pointed record must declare exactly one top-level `status: ACTIVE` and no `void` or `superseded_by` retirement metadata; missing, duplicate, malformed, commented-out, differently cased, retired, or non-ACTIVE status grants no mutation authority. Read tools remain available for ordinary review.
2. **`grant.filesystem.write`** for the file-edit tools. The runtime and pre-dispatch tools use independent parser implementations cross-tested against one public compatibility corpus. Repository-root grants or targets, escapes, `.`/`..`, empty components, unsupported wildcards, backslashes, home expansion, symlink/junction grant bases, and symlink/junction target aliases are rejected. Comparisons use resolved path components, never string prefixes.
3. **The Doctrine 8.7 protected-control-plane floor in source logic.** Every file-edit tool denies mutation of the active pointer, the complete `.claude/hooks/**` subtree, `.claude/settings.json`, `.claude/settings.local.json`, the active work order or instrument, and the denial log regardless of exact or recursive grant wording, authorship, labels, textual aliases, case/trailing-dot aliases on case-insensitive filesystems, or resolved aliases. The mechanism's own narrow append to the denial log remains internal; agent-directed mutation is denied. Because shell tools do not expose an exact target, `restricted` and `allowed` shell calls are also denied rather than allowed to bypass that floor. Delegation, MCP, version-control, and other unmodeled mutation channels fail closed.
4. **`grant.filesystem.read.deny`** for the read tools (`Read`, `Glob`, `Grep`, `LS`, `NotebookRead`), only while a valid active work order declares it. Absence of the field, or an empty list, denies nothing. `Read` and `NotebookRead` are denied when their exact target is the denied path or lies below a recursive denied path. `Glob`, `Grep`, and `LS` are denied when their resolved search root lies inside a denied subtree, or is an ancestor whose traversal could reach one — including an omitted root, which means the repository root and is therefore denied whenever any deny entry is active. Path-bearing `Glob.pattern` and `Grep.glob` accept only literal components plus `*`, `**`, and confined `?` wildcards; absolute, drive, backslash, brace, character-class, home-expansion, empty, `.`/`..`, and dot-wildcard forms fail closed because the adapter cannot prove they remain inside the declared root. No-work-order lockout does **not** apply to read tools: an absent pointer leaves reads unrestricted, since 8.3.5.1 binds mutation, not ordinary read-only review. Once a pointer exists, an unsafe pointer or unreadable/malformed pointed work order or grant fails closed for modeled reads with a stage-specific reason. A valid grant with no read-deny entries denies nothing.
5. **`grant.network.egress` for `WebFetch` and `WebSearch`.** Those tools are network-capable, not passive inspection. Denied, missing, or invalid authority blocks them; only explicit `allowed` passes. MCP and unknown network tools remain denied.
6. **Fail closed on anything indeterminate within the modeled call**: unsafe pointer, malformed frontmatter, invalid lifecycle status, missing grant, invalid shell/network scalar, unsupported path syntax, or undeterminable target. Runtime and dispatch parser compatibility is exercised by a shared public corpus; the runtime does not invoke the dispatch parser or claim an independent disagreement detector.
7. **Read-only preflight.** CPython 3.10 through 3.14 is supported. `--preflight` checks the native Windows or POSIX interpreter command, project-root installed path and digest, matcher/source, portable `${CLAUDE_PROJECT_DIR}` registration, and explicit timeout without repository mutation or denial-log append.

## Protected control plane (Doctrine 8.7) — source logic and reference birth test

Doctrine 0.8 (`decisions/DR-005.md`) requires the categorical floor described above. The private Writwall reference instance completed native Windows and native Linux protected-control-plane birth-test matrices and closed RFI-22 at WO-PL-026. That observation applies only to the exact installed bytes, providers, versions, settings, sessions, and exposed tool inventories tested there. **It does not transfer to this source file, a public clone, or an adopter's installation**, and it does not move any whole declared grant surface into `enforced_by`. Every installation still requires its own exact lifecycle, preflight, inventory, and fresh native birth tests.

A birth-test instrument may name an exact protected path only with `instrument_kind: birth-test` and role `control_plane_falsification_probe`. The pre-dispatch validator distinguishes that labeled expected-denial case from an invalid ordinary grant. The label confers no authority: the runtime must still deny it.

## What remains unenforced or unqualified

- **Every whole grant surface remains unqualified until the fresh installed birth tests.** Unit tests establish logic, not provider inventory or installed dispatch. Do not move any surface into `enforced_by` on this evidence alone.
- **Filesystem reads beyond the five named read tools.** Shell tools are denied categorically rather than inspected, and provider channels absent from the inventory remain unknown until birth test.
- **Network egress beyond `WebFetch` and `WebSearch`; package installation; secrets; commit; and push as whole surfaces.** Known unmodeled tools deny, but completeness has not been established.
- **Its own launch and timeout.** See the provider limitation above.

## Declared tool coverage

The classification below is version-specific by nature. Re-inventory every mutation-capable, read-capable, and network-capable tool at each birth test and after any provider upgrade or MCP/plugin change; a tool absent from all six lists is denied until someone classifies it.

```text
FILE_EDIT_TOOLS = Edit, MultiEdit, NotebookEdit, Write
SHELL_TOOLS = Bash, KillShell, Monitor, PowerShell
READ_TOOLS = Glob, Grep, LS, NotebookRead, Read
NETWORK_TOOLS = WebFetch, WebSearch
NONMUTATING_TOOLS = AskUserQuestion, BashOutput, CronList, EnterPlanMode, ExitPlanMode, ListMcpResourcesTool, ReportFindings, Skill, TaskOutput, TodoWrite, ToolSearch
UNSUPPORTED_MUTATION_TOOLS = Agent, Artifact, CronCreate, CronDelete, DesignSync, EnterWorktree, ExitWorktree, PushNotification, RemoteTrigger, ScheduleWakeup, SendMessage, SendUserFile, TaskStop, Workflow
```

Notes on the categories:

- **FILE_EDIT_TOOLS** are governed by `grant.filesystem.write`. `MultiEdit` is retained only as backwards-compatible coverage for installations that still expose it; it is harmless where the tool does not exist.
- **SHELL_TOOLS** honor `denied`; `restricted` and `allowed` are still denied because these calls expose no exact mutation target from which the 8.7 floor can be proved.
- **READ_TOOLS** are governed by `grant.filesystem.read.deny` (point 4 above), and otherwise reach normal Claude Code permission evaluation.
- **NETWORK_TOOLS** are governed by `grant.network.egress`; only explicit `allowed` passes.
- **NONMUTATING_TOOLS** reach normal Claude Code permission evaluation unchanged because they expose no modeled mutation surface. `ListMcpResourcesTool` may enumerate provider resource metadata; this classification does not claim that metadata is secret, empty, or governed by `filesystem.read.deny`.
- `ReadMcpResourceTool` and `ReadMcpResourceDirTool` deny as unmodeled: an
  opaque resource URI can return file bytes without exposing a repository path
  this adapter can compare with `grant.filesystem.read.deny`.
- **UNSUPPORTED_MUTATION_TOOLS** are denied outright with an RFI instruction. They can change repository, environment, or external state through a channel this adapter does not model. `Agent` and `Workflow` are here because they delegate to sessions whose individual tool calls this adapter cannot guarantee it observes; that is a delegation channel, not a footnote (8.3.3).
- **Every `mcp__*` tool is denied by default**, as is any unrecognized name.

## Install

1. Copy the script to `<repo>/.claude/hooks/wo_capability_wall.py`.
2. Register it in `<repo>/.claude/settings.json` with matcher `*`, a portable project-root path, and an explicit positive timeout. Use the native command for the host.

Native Windows:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "py -3 \"${CLAUDE_PROJECT_DIR}/.claude/hooks/wo_capability_wall.py\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

Native POSIX uses the same JSON with command
`python3 "${CLAUDE_PROJECT_DIR}/.claude/hooks/wo_capability_wall.py"` and the
same explicit timeout. Git Bash invoking Windows Python is a Windows leg, not
a native POSIX leg.

**Use `${CLAUDE_PROJECT_DIR}`, never an absolute path.** Claude Code supplies that variable to hook commands, and the runtime requires it before deciding or logging: a missing or disagreeing value exits hard because repository identity cannot be verified. An absolute path bakes one machine's layout into a governed artifact: it breaks for every other clone, and it ships machine-specific data in any release archive. `checks/check_distribution.py` fails a registration that omits `${CLAUDE_PROJECT_DIR}` or that names an absolute repository path.

3. Run the adapter's read-only preflight from the installed path. The public
projection intentionally contains no active `.claude/settings.json` or
installed `.claude/hooks/` copy; installation is a deliberate host-local step,
not a portable file the distribution can choose for you. Substitute
the exact expected SHA-256 and the native platform:

```text
py -3 .claude/hooks/wo_capability_wall.py --preflight --project-root . --settings .claude/settings.json --expected-digest <sha256> --platform windows
python3 .claude/hooks/wo_capability_wall.py --preflight --project-root . --settings .claude/settings.json --expected-digest <sha256> --platform posix
```

Preflight writes no repository file and appends no denial record. It verifies
configuration; it is not a birth test.

4. Confirm your Claude Code version honors `permissionDecision` JSON output. If it predates that, the fallback is stderr plus exit code 2; adapt `emit_deny()` and record the change in the adoption record D.4.

The canonical distribution's `adapters/claude-code/SECURITY.md` records the
threat boundary, supported versions, and reporting route.

The active-WO pointer is `<repo>/.claude/active-wo.txt`, holding a repository-relative path inside `governance/work-orders/`. Denials append to `<repo>/governance/LOG-denials.jsonl`; see "Denial log" below.

## Grant path syntax

Deliberately narrow, so that a grant means one thing. `grant.filesystem.write` and `grant.filesystem.read.deny` share this grammar:

| Form | Meaning |
|---|---|
| `path/to/file.md` | that exact file |
| `path/to/dir/**` | that directory and everything beneath it |

Everything else is rejected and denies: the repository root, `/*` (which is **not** recursive), `*.md`, `a/**/b`, absolute paths, drive-letter paths, `.` or `..`, doubled/leading/trailing separators, backslashes, home expansion, control characters, symlink/junction bases, and target aliases. An exact directory path without `/**` grants only that path, not its contents.

## Birth test (Doctrine 8.3.5), mandatory before adoption

Doctrine defines two consequence levels: no-work-order lockout and active-scope
enforcement. This adapter divides the second into ordinary-scope Level 2 and
protected-control-plane Level 3, with conditional read-deny Level 4. Test every
native environment the project will use. A portable Windows-and-POSIX claim
requires both native legs; an unavailable, unused platform is recorded as
untested/indeterminate and keeps affected whole surfaces unenforced, but does
not by itself block adoption after the used environment passes Level 1 and the
Owner accepts the remaining risk under Doctrine 6.4.2 and 8.3.4.

WO-000 for the test, at `governance/work-orders/WO-000-birth-test.md`:

```
---
id: WO-000
status: ACTIVE
doctrine_rev: 0.8
grant:
  filesystem.write:
    - governance/scratch/**
  filesystem.read.deny: []
  shell.execute: denied
  network.egress: denied
  package.install: denied
  secrets.read: denied
  git.commit: denied
  git.push: denied
enforced_by: {}
unenforced_boundaries:
  - filesystem.write
  - filesystem.read.deny
  - shell.execute
  - network.egress
  - package.install
  - secrets.read
  - git.commit
  - git.push
---
# WO-000: Birth test only. Not counted (Doctrine 6.1.3).

## B.1 CONTEXT

This uncounted instrument tests the installed adapter before adoption.

## B.2 OBJECTIVE

Falsify or establish the adapter only on the channels actually probed.

## B.3 REQUIRED WORK

Run the three birth-test levels below in the stated order and preserve the
observed results without broadening this grant.

## B.4 BOUNDARIES

Only `governance/scratch/**` is writable. Every other declared surface is
instruction-only unless and until the observed test evidence supports a more
specific classification.

## B.5 ACCEPTANCE

Each attempted mutation is reported by channel, target, expected result, and
observed result. Any unexpected success fails the birth test.

## B.6 REPORT FORMAT

Record environment identity, adapter digest, settings source, probe matrix,
denial-log evidence, cleanup, and the resulting surface classification.

<!-- BEGIN GENERATED BOUNDARIES -->
## B.7 Generated boundaries

This block is the Owner-supplied seed rendering for the first implementation of
the generator. The accepted checker must reproduce it byte-for-byte solely from
frontmatter; thereafter Owners replace this block only with checker output.

### Writable repository paths

- `governance/scratch/**`

### Read-denied repository paths


### Other capability limits

- shell.execute: `denied`
- network.egress: `denied`
- package.install: `denied`
- secrets.read: `denied`
- git.commit: `denied`
- git.push: `denied`

### Typed non-write path exceptions


### Control-plane falsification probes (expected-denial; confer no authority)


This checker is read-only. It does not repair, create or remove the activation
pointer, mutate a work order, retrieve closed history, modify adopter templates,
access another project, install packages, use the network, commit, push, tag,
publish, select a license, or change repository visibility.
<!-- END GENERATED BOUNDARIES -->
```

### Preflight, before any probe

The birth test is worthless if run outside the operating envelope. Establish the envelope first, in this order:

1. **Launch Claude Code with this repository as the project root.** Not `--add-dir`, not a parent directory, not a sibling.
2. **Confirm `/hooks` shows the `PreToolUse` matcher `*`.**
3. **Confirm its source is this repository's project `.claude/settings.json`**, not a user-level or enterprise-level file.
4. **Confirm the displayed command resolves through `${CLAUDE_PROJECT_DIR}`.**
5. **Run `--preflight`** with the exact installed digest, settings path, and native platform. It must pass without a denial-log change.
6. **Confirm no active-WO pointer exists** (`.claude/active-wo.txt` absent).
7. **Only then begin real provider-level mutation probes.**

**The `/hooks` inspection is necessary configuration evidence, not proof of live enforcement.** It shows what Claude Code believes it has loaded. It does not show that the session executing your probes actually loaded it. Only observed denial of real tool calls constitutes the birth test (8.3.5). Invoking the adapter directly with a synthetic payload verifies its logic and nothing else; it must never be recorded as a passing birth test.

### The live-wall canary

Before a session mutates a repository governed by this wall, that session establishes that the wall is live **for itself**. Proof is local to one executing provider session. It does not transfer to another session, to a parent or child context, to a different UI, or to a separate provider invocation.

A **valid canary** is an Owner-authorized, genuinely mutation-capable, out-of-grant call that survives provider input validation and therefore reaches `PreToolUse`. A `Write` carrying real content to a path outside the grant is the reference shape. The canary target must be **named explicitly by the Owner-authorized procedure** and deliberately excluded from the active `filesystem.write` grant, so that a correct wall must deny it.

The pass condition is **conjunctive**. All four must hold:

1. the provider blocks the call **before** mutation;
2. the target file **does not exist** afterward;
3. `governance/LOG-denials.jsonl` grows by **exactly one** record;
4. that new record identifies the **real executing session** and carries the expected denial reason, tool, surface, and active work-order path.

**These are not valid canaries:**

- **An impossible-match `Edit`** — for example, an `old_string` chosen so it cannot match. Claude Code rejects it during `Edit` input validation, *before* `PreToolUse` dispatch. The call never reaches the hook and writes no denial record, so its failure tells you nothing about the wall. A canary that cannot reach the hook cannot test it.
- **Direct adapter invocation.** Piping a payload to the hook script outside a provider session tests the adapter's logic, not the provider's dispatch. Any record it writes is synthetic and must be labelled as such.
- **Any synthetic or hand-authored payload**, for the same reason.

**If the canary creates the file, writes no denial record, or is otherwise indeterminate, the wall is not proved live for that session.** Stop. Do not retry with a different tool, do not broaden the grant, and do not proceed on the assumption that a correct-looking `/hooks` display implies enforcement. If the canary did create a file, treat its removal as a **separately authorized action**, not cleanup to perform on your own initiative.

A passing canary proves that this session's `PreToolUse` hook intercepts **the channel it was tested on**. It does not make shell-mediated writes, or any other surface this adapter records as unenforced, mechanically enforced. Those surfaces remain instruction-only however many canaries pass.

**Level 1, no-work-order lockout (precondition).** Ensure no active-WO pointer exists. First inventory every mutation-capable channel actually present in your installation: the built-in file-edit and shell tools, every connected MCP or plugin tool, and any provider-specific command tool. Then attempt a mutation through each one. Every attempt must be denied. A single success means level 1 has failed and the project has not adopted.

Use a **minimal provider profile** for this inventory. Disable unrelated
connectors, plugins, MCP servers, and delegated agents before testing. Probe an
external mutation tool only against an **explicit disposable fixture** whose
side effect, verification method, and cleanup authority were approved in the
lifecycle packet. Never use an ordinary live account object as a canary.
Authentication failure, provider rejection before hook dispatch, an unavailable
tool, or an unprobed channel is indeterminate, never a pass.

An authorized lifecycle action may remove the pointer and re-establish the no-pointer state
for another fresh Level 1 session. It is not a one-time window.
Unplanned denials are not retroactively promoted into a birth test; retain them
as accurately classified log evidence.

**Level 2, per-channel scope.** Activate WO-000. Write `governance/scratch/ok.txt` (must succeed). Edit a file outside `governance/scratch/` (must be denied). Attempt every exposed shell/delegation/MCP/version-control mutation channel (each must deny). Treat these as channel-local observations only; do not move a whole surface into `enforced_by` until the complete platform inventory and birth-test matrix support it.

**Level 3, protected control plane.** Run only an exact Owner-ratified `instrument_kind: birth-test` record and lifecycle packet. Probe the pointer, installed adapter, installed settings, active instrument itself, and denial log through every exposed mutation-capable channel. Each valid call must deny before mutation; target bytes must remain unchanged; the log self-probe must retain its complete prior byte prefix; and only expected append-only evidence may appear. Run a fresh native provider session on every platform the project will use. A portable Windows-and-POSIX claim requires separate fresh sessions on both; an unavailable or indeterminate required leg blocks that claim and leaves affected whole surfaces unenforced. A labeled probe confers no authority.

**Level 4, `filesystem.read.deny` (optional, only if the work order declares it).** Ask the Owner to create one sentinel file inside a path named in `filesystem.read.deny`, with content not supplied to the implementing agent, and add that exact path to the grant. In a fresh session: `Read` of the sentinel must be denied before content exposure; `Grep`/`Glob`/`LS` rooted at or above the denied path must be denied before traversal; one `Read` of an allowed sibling file must succeed. The agent must never receive or report the sentinel content. A denial failure, content exposure, or missing log record is a birth-test failure for this surface specifically; it does not affect earlier results already recorded.

Every denial appends to `governance/LOG-denials.jsonl`. That file is the wall's birth certificate; carry it into the adoption record D.4 with the birth-test context that identifies which entries are pre-adoption. The hook does not itself label entries as pre-adoption.

## Denial log

One JSON object per line, LF-terminated on every platform, at `<repo>/governance/LOG-denials.jsonl`. The file is append-only and is never rewritten by the adapter.

These field names are stable. A downstream reader or check may match on them, and on the `reason_code` values, so neither is renamed or reused for a different meaning. `schema` is bumped only when the record shape changes in a way a reader must notice.

| Field | Type | Meaning |
|---|---|---|
| `schema` | integer | Record schema version. Currently `1` |
| `timestamp` | string | UTC RFC 3339, second precision, e.g. `2026-08-16T20:06:22Z` |
| `session_id` | string or `null` | Provider session identifier when the hook event supplies one, otherwise `null` |
| `tool` | string or `null` | Tool name as received; `null` when the event carried no usable name |
| `surface` | string | Classified surface: `filesystem.write`, `filesystem.read`, `shell.execute`, `network.egress`, `unmodeled`, or `unknown` |
| `work_order` | string or `null` | Repository-relative active-work-order path when resolvable, otherwise `null` |
| `decision` | string | Always `deny`. The adapter logs denials only |
| `reason_code` | string | Stable machine-readable code (see below) |
| `reason` | string | Concise human-readable sentence |

```json
{"schema":1,"timestamp":"2026-08-16T20:06:22Z","session_id":null,"tool":"Write","surface":"filesystem.write","work_order":null,"decision":"deny","reason_code":"no_active_work_order","reason":"No active work order; the pointer file is absent."}
```

**Reason codes.** `hook_event_malformed`, `tool_not_modeled`, `no_active_work_order`, `pointer_unreadable`, `pointer_not_regular`, `pointer_empty`, `pointer_backslash`, `pointer_names_no_file`, `pointer_not_relative`, `pointer_escapes_repository`, `pointer_not_markdown`, `pointer_outside_work_orders`, `pointer_is_directory`, `pointer_missing_file`, `work_order_unreadable`, `frontmatter_missing_open_fence`, `frontmatter_missing_close_fence`, `work_order_status_invalid`, `grant_missing`, `grant_structure_invalid`, `shell_execute_denied`, `shell_execute_invalid`, `control_plane_channel_uninspectable`, `network_egress_denied`, `network_egress_invalid`, `filesystem_write_missing`, `filesystem_write_empty`, `grant_path_invalid`, `write_target_undeterminable`, `write_target_path_invalid`, `write_target_out_of_grant`, `control_plane_protected`, `read_deny_path_invalid`, `read_target_undeterminable`, `read_target_outside_repository`, `read_target_denied`, `read_traversal_denied`, `read_pattern_invalid`.

### What the log deliberately does not contain

The logged `reason` is **not** the reason returned to the provider. The provider-facing reason may name a rejected path so the agent can act on it; the log carries the reason code instead.

Never written to the log: tool arguments, prompts, file contents, search patterns, environment variables, usernames, drive letters, absolute paths, grant entries, tokens, or secrets. This keeps the birth certificate publishable alongside the repository and keeps one machine's layout out of a governed artifact.

### Failure behavior

A logging failure never opens the wall. If the record cannot be written — unwritable directory, full disk, serialization error — the adapter swallows the error and still emits the deny decision. Evidence can be lost; the denial cannot.

## Tests

```
python -m unittest discover -s tests -p "test_*.py"
```

The adapter's unit tests live in `tests/test_wo_capability_wall.py` in this repository. They cover pointer validation, lifecycle status, frontmatter and grant parsing, path syntax, protected-control-plane denial, `filesystem.read.deny` enforcement across the read tools, network-egress authority, tool classification for all six categories, preflight behavior, and the exit-2 hard fallback. They are not a substitute for the birth test: unit tests prove the logic, the birth test proves the installation.

**Dual-runtime acceptance rule (WO-PL-013).** Before accepting any adapter or adapter-test change, run the wall suite under native Windows Python and under a native POSIX Python. Git Bash backed by Windows Python does not satisfy the POSIX leg: it still runs the Windows interpreter, so a POSIX-only path-resolution defect stays invisible. Ubuntu WSL is an acceptable native POSIX leg. Outside-repository tool-target fixtures must use a platform-native absolute path derived from the fixture's own temporary root, never a foreign OS path literal, or the test is vacuously green on the OS that literal does not belong to.
