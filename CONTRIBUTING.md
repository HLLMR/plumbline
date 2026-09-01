# Contributing to Writwall

Thank you for helping improve Writwall.

## Public issue and pull-request workflow

1. Open an issue first using the public bug or enhancement form. Never include
   secrets, private paths, disclosure patterns, other-project material, or the
   private governed-source history.
2. Triage applies one category (`bug` or `enhancement`) and one workflow state.
   An issue becomes `ready-for-agent` only after a durable agent brief states
   current behavior, desired behavior, acceptance criteria, and exclusions.
3. Writwall's own implementation is governed in its private governed source.
   Accepted changes reach the public repository through the checked clean projection;
   private work orders and reports do not enter the public branch.
4. Create a feature branch in the public repository and open a pull request
   linked with `Closes #<number>`. Direct commits to public `main` are not the
   maintenance path.
5. Run the focused regression, complete suite, distribution, license, and
   projection gates. A fresh Reviewer checks the public diff and evidence.
6. Merge only after required CI and review pass. The merged PR closes the public
   issue; an unmerged private fix does not.

The exact label vocabulary and contributor-agent routing are under
[`docs/agents/`](docs/agents/). The pull-request template keeps the public and
private boundaries visible during review.

## New public identities

Any proposal to rename this project, publish a named subproject, or introduce a
new package identity begins with the evidence-producing
[`docs/name-clearance.md`](docs/name-clearance.md) gate. Do not spend design or
launch effort on a candidate until its required sources are available, its
findings are classified, and the Owner records an exact disposition. The
ledger proves the search procedure, not legal clearance.

## Doctrine and methodology decisions

The Owner is the sole ratifier of Writwall intent. Proposed changes to
`DOCTRINE.md` or `decisions/` should therefore begin as an issue describing the
problem, evidence, and proposed outcome. Pull requests that directly rewrite
ratified doctrine or decision records will not be accepted as authority.

## Other contributions

Documentation corrections, adapters, checks, scripts, and tests may be
submitted by pull request. Every contributed commit must include a Developer
Certificate of Origin sign-off:

```text
Signed-off-by: Your Name <your-email@example.com>
```

By adding that line, you certify the [Developer Certificate of Origin 1.1](https://developercertificate.org/).
Use `git commit -s` to add the line automatically.

Writwall does not require a contributor license agreement. Contributions are
accepted under the license assigned to their destination path in
[LICENSE-MAP.md](LICENSE-MAP.md).

## Development and checks

The complete repository test suite supports CPython 3.11 through 3.14. The
standalone Claude Code adapter has a narrower standard-library contract and is
also tested on CPython 3.10. Run the same scopes as CI from the repository root.
Before running the suite, provision the build backend declared by
`pyproject.toml`:

```text
python -m pip install --disable-pip-version-check --no-input --only-binary=:all: "setuptools>=77"
```

This is a build/test prerequisite, not a Writwall runtime dependency. The
installed coordinator and adapter remain standard-library-only.

Before proposing a coordinator-bearing release, run the reusable external-tree
gate against the final checked public candidate on native Windows and native
Ubuntu:

```text
python checks/check_coordinator_release.py <external-candidate-directory> --expected-tag v0.9.2
```

The gate copies the candidate to temporary build space, builds and installs the
declared package without network access or an `ensurepip` assumption, runs the installed coordinator against
a disposable project, verifies the complete handoff, and proves the candidate
tree remained byte-identical.
The distribution command shown below is the governed-source form; the public
projection deterministically substitutes `--projection` because it deliberately
omits private governed-source evidence:

```text
python -B -m unittest tests.test_wo_capability_wall tests.test_check_work_order_dispatch tests.test_init_sh
python -B -m unittest discover -s tests
python -B checks/check_distribution.py --projection
python -B checks/check_licenses.py
```

The public projection is deliberately shipped without an active
`.claude/settings.json` registration or installed `.claude/hooks/` copy, so a
fresh public clone does not silently select the wrong host interpreter. If you
install the adapter locally, a missing `.claude/active-wo.txt` means the wall is
in its intended no-work-order lockout and will deny modeled mutations. Do not
create a fake pointer or weaken the hook to get around that state; either work
without installing the project hook, or ask the maintainer to dispatch a
governed work order.
