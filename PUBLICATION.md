# Public projection and publication boundary

Writwall's governed source repository remains private. Its clean-history
public candidate is derived from the exact positive allowlist in
`projection/public-files.txt`; it is not produced by changing the visibility
of the governed repository or copying its Git metadata.

## Coordinator-bearing release gate

The day-zero coordinator first shipped in `v0.9.0`; `v0.8.1` predates
`pyproject.toml`, `writwall_cli/**`, and the installed `writwall start` entry
point. Before creating a release tag, run this gate against the final external
candidate on native Windows and native Ubuntu, naming the exact intended tag:

```text
python checks/check_coordinator_release.py <candidate-directory> --expected-tag v0.9.3
```

The command fails before building unless the canonical intended tag matches
the candidate's package version. It is network-free. It copies the candidate into temporary build
space, builds a wheel using the already-provisioned backend declared in
`pyproject.toml`, creates a fresh virtual environment without assuming the
host can bootstrap `pip` inside it, installs through the already-provisioned
host `pip`, checks
the installed version and help interface, runs the coordinator against a
disposable external project, verifies the complete create-only handoff, and
then verifies that the input candidate tree did not change. A pass is release
readiness evidence; it does not create a tag, GitHub release, or publication.

Build and verify a candidate with the managed project privacy screen initialized
by `writwall start`:

```text
python scripts/build_public_projection.py --output <empty-external-directory>
python checks/check_public_projection.py <candidate-directory>
```

The screen is durable per-user state outside the repository. Neither command
prints its location, values, matches, or value-derived hashes. The explicit
`--private-pattern-file` option remains only as a controlled compatibility
override; it is not the ordinary human workflow. See `docs/privacy-screen.md`.

The private input remains mandatory at build and check time for the local
zero-match gate: its patterns are matched, closed, against candidate text.
No value-derived fingerprint of the private input — including a digest — is
written into the candidate, `PROJECTION-PROVENANCE.md`, or ordinary command
output. Its path, patterns, digest, and matches are never copied into the
candidate or printed by the commands.

Run the full candidate test suite with bytecode writes suppressed
(`PYTHONDONTWRITEBYTECODE=1`, or an equivalent mechanism for the platform's
Python launcher) so that no `__pycache__` or `.pyc` residue is generated
inside the candidate during testing. `check_public_projection.py` must be
the last operation performed on the retained candidate bytes: run it only
after the full test suite and any cleanup are complete, against the exact
tree that would become the public root. A checker run before the test suite,
or against a pre-test or partially cleaned subset, does not certify the
retained bytes and must be re-run against the final tree before that tree is
treated as checked.

`PROJECTION-PROVENANCE.md` in the candidate explains the evidence boundary.
Legacy commit identifiers in projected records refer to the private governed
source and intentionally do not resolve in a fresh public history. Where a
record discusses recovery from Git history, a deterministic projection note
clarifies that the statement applies only to the private governed source.

The candidate retains public-safe live self-hosting governance and aggregate
pilot evidence. It excludes private transactional history, the pre-adoption
archive, stale distribution files, active work records, private sidecars, and
unknown paths. Its distribution archive must be rebuilt from projected bytes.

The candidate replaces the governed source's root `CLAUDE.md` with a fixed,
public-only notice saying that the checkout is ungoverned and ordinary
contribution is allowed. It excludes `.claude/settings.json` and installed
`.claude/hooks/wo_capability_wall.py`. The private root charter auto-loads
private-instance instructions that do not govern an ordinary public checkout
and therefore never enters candidate bytes. The other two are host-local control-plane
installation artifacts: shipping the private repository's Windows launcher
would silently disable the hook on POSIX, while shipping a POSIX launcher
would be wrong for native Windows. The canonical, uninstalled adapter remains
under `adapters/claude-code/`. Adopters must copy it into their project,
register the native command for their host, run its preflight, and birth-test
the actual provider session before claiming enforcement.

The candidate carries pilot evidence and post-pilot remediation through the
latest accepted work order, not only WO-PL-017 through WO-PL-020. WO-PL-017
through WO-PL-020 specifically ran in Codex, outside this repository's
installed Claude Code hook, and were instruction-bounded; see
`governance/LOG.md` and `SELF-HOSTING.md` for the exact provider and evidence
boundary of each later work order. The candidate makes no claim that every
declared capability surface is mechanically enforced, in this repository or
in any session or provider, and no wall-enforcement claim transfers between
sessions or providers.

## Complete-tree ledger (optional aggregate)

`PROJECTION-MANIFEST.sha256` is the shipped, per-payload manifest the
builder and checker use for candidate integrity. Separately, an Owner or
coordinator may compute one additional, optional aggregate digest of the
entire retained candidate tree — the complete-tree ledger — to compare two
independently built candidates byte-for-byte. It is derived as follows:

1. Recursively enumerate every retained regular file in the candidate root.
2. Express each file's path relative to the candidate root using `/` as the
   path separator.
3. For each file, form the line `<lowercase file SHA-256><two spaces><relative path>`.
4. Sort the complete set of lines ordinally (byte-wise) by the full line text.
5. Join the sorted lines with a single LF (`\n`) between lines, plus one
   trailing LF at the end.
6. UTF-8 encode the resulting text without a byte-order mark.
7. Take the SHA-256 of those encoded bytes; that digest is the complete-tree
   ledger.

The complete-tree ledger digests two independently built candidates for
equality; it is not shipped inside the candidate and is distinct from
`PROJECTION-MANIFEST.sha256`, which enumerates only the allowlisted
payloads plus `PROJECTION-PROVENANCE.md` and is verified per-entry by the
checker as part of every run.

The accepted licenses are recorded in `LICENSE-MAP.md` and `REUSE.toml`.
Writwall's names and revision designations remain reserved as described in
`NAMING.md`.

Building or checking a candidate does not publish it. The Owner separately
decides whether to create a new public repository, make a fresh root commit,
configure a new remote, and publish.
