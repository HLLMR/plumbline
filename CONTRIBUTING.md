# Contributing to Plumbline

Thank you for helping improve Plumbline.

## Doctrine and methodology decisions

The Owner is the sole ratifier of Plumbline intent. Proposed changes to
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

Plumbline does not require a contributor license agreement. Contributions are
accepted under the license assigned to their destination path in
[LICENSE-MAP.md](LICENSE-MAP.md).

## Development and checks

The complete repository test suite supports CPython 3.11 through 3.14. The
standalone Claude Code adapter has a narrower standard-library contract and is
also tested on CPython 3.10. Run the same scopes as CI from the repository root.
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
