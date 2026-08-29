# Security policy

Writwall's executable security boundary is its provider-specific adapter, not
the methodology prose by itself. The maintained Claude Code threat model,
supported behavior, known limits, birth-test requirements, and vulnerability-
reporting route are documented in
[`adapters/claude-code/SECURITY.md`](adapters/claude-code/SECURITY.md).

Report a suspected vulnerability through GitHub's **Security** tab using
**Report a vulnerability**. That creates a private vulnerability report for
maintainer review. Do not disclose an unpatched vulnerability in a public
issue. Ordinary defects and documentation corrections still belong in the
public issue tracker.

The public projection deliberately ships no active project-hook registration.
Installing an adapter is a separate Owner-controlled action and requires the
native preflight and provider-level birth tests described beside that adapter.
