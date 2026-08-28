# Security policy

Plumbline's executable security boundary is its provider-specific adapter, not
the methodology prose by itself. The maintained Claude Code threat model,
supported behavior, known limits, birth-test requirements, and vulnerability-
reporting route are documented in
[`adapters/claude-code/SECURITY.md`](adapters/claude-code/SECURITY.md).

The public projection deliberately ships no active project-hook registration.
Installing an adapter is a separate Owner-controlled action and requires the
native preflight and provider-level birth tests described beside that adapter.
