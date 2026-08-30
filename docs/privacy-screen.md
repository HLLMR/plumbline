# Managed local privacy screen

Writwall creates a durable privacy screen when you run `writwall start`. It is
stored in your operating system's per-user application-state area, outside the
target repository, and keyed to that project's canonical root. A different
project receives a different profile.

The profile begins with exact machine-path forms for the target project. You
may optionally add private names, codenames, client identifiers, or domains
that must never appear in a public projection. Do **not** add passwords, API
tokens, private keys, recovery codes, mailbox content, DNS record values, or
other credentials or secret values.

```text
writwall privacy init --project-root /path/to/project
writwall privacy status --project-root /path/to/project
writwall privacy add --project-root /path/to/project --confirm-no-secrets
```

The add command reads the identifier through a hidden prompt, not a command-line
argument. Controlled non-interactive callers may use `--identifier-stdin`.
Normal output reports only whether the screen is ready and how many entries it
contains. It never reports the profile location, stored values, matches, or a
value-derived fingerprint. The path is deliberately not written into
`.writwall-bootstrap/` or repository records.

Projection tools resolve the managed profile automatically from the governed
source root:

```text
python scripts/build_public_projection.py --output /absolute/empty/candidate
python checks/check_public_projection.py /absolute/empty/candidate
```

They fail closed if the profile is missing or empty. The
`--private-pattern-file` option remains available as an explicit compatibility
override for controlled automation, but it is not the normal human workflow.

Temporary bootstrap folders, projection candidates, test copies, and logs may
be deleted after their own lifecycle completes. The managed profile is durable
local state and must not be included in that cleanup.

On Linux and macOS, Writwall requests owner-only file permissions. On Windows,
the profile inherits the user's application-state access controls; Writwall
does not claim to replace Windows account or filesystem security.
