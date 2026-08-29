# Claude Code adapter security boundary

This adapter is a project-local `PreToolUse` policy hook. It narrows modeled
Claude Code tool calls when the hook actually starts and receives the call. It
is not an operating-system sandbox, access-control system, secret manager, or
complete monitor of every provider, plugin, MCP server, subagent, process, or
future tool.

## Supported versions

The standalone adapter is tested with CPython 3.10 through 3.14. Installation
must use the native launcher for the host: `py -3` on native Windows and
`python3` on native POSIX. Claude Code's hook contract and exposed tool
inventory are version-sensitive; re-run preflight and the birth tests after a
provider or plugin change.

Only the current adapter in the latest published Writwall revision receives
security fixes. A project remains bound to its ratified Doctrine revision until
its Owner deliberately migrates it, but it may adopt a compatible adapter
security repair through its own decision and installation lifecycle.

## Security model

When loaded from the project root, the adapter:

- denies modeled mutation calls without one valid active work order;
- limits modeled file-edit calls to the work order's normalized write grant;
- protects the activation pointer, all project hook files, both project
  settings files, the active work order, and the denial log from agent-directed
  mutation;
- applies declared read-deny paths to the named built-in filesystem-read tools;
- governs the named built-in network tools; and
- denies unmodeled, MCP, and delegation mutation channels it can identify.

These are adapter behaviors, not proof that a provider invoked the adapter.
The public distribution deliberately contains no active project-hook
registration. Every adopter must install the canonical script, register the
native command, run `--preflight`, inspect the loaded hook, inventory the tools
actually exposed, and execute fresh provider-level birth tests.

## Known limits

- Missing interpreter, hook startup failure, timeout, disabled or shadowed
  project settings, and sessions launched from another project root are outside
  the adapter's control. Non-execution cannot be made fail-closed by this hook.
- A passing canary proves only the tested channel in that exact session. It
  does not prove every file, shell, MCP, delegation, network, or future channel.
- Read-deny applies only to the explicitly modeled built-in read tools. Opaque
  MCP resource readers are denied rather than inspected.
- An absent activation pointer deliberately leaves ordinary read-only review
  available. Once a pointer exists, malformed pointer, work-order, or grant
  state denies modeled reads as well as mutations; this can require Owner repair
  before the session continues.
- Shell calls are denied even when a work order says `restricted` or `allowed`,
  because the hook cannot prove their mutation targets stay outside the
  protected control plane.
- The append-only denial log is evidence, not a tamper-proof audit service.
  Anyone with operating-system or repository-owner access can alter it outside
  the hook.
- An Owner can replace or disable the control plane outside an Implementer
  grant. Writwall governs that lifecycle by explicit decision and evidence;
  it cannot make the Owner cryptographically subordinate to the hook.

The maintained operational detail and exact tool classification are in
`README.md` beside the adapter.

## Reporting a vulnerability

Use GitHub private vulnerability reporting for the Writwall repository when
it is available. If it is not available, open a minimal issue that identifies
the affected adapter revision and requests a private contact channel; do not
include exploit payloads, secrets, private repository paths, or third-party
data in a public issue.

A useful report includes the adapter SHA-256, Python and Claude Code versions,
native operating system, hook event/tool name, expected decision, observed
decision and exit status, and a smallest synthetic reproduction that contains
no private project material.
