# Writwall license map

Copyright 2026 HLLMR Ventures LLC.

This map implements [DR-003](decisions/DR-003.md). It is authoritative over
the root `LICENSE` for every path assigned differently below.

| Scope | License | SPDX identifier |
|---|---|---|
| `DOCTRINE.md`, `README.md`, `START-HERE.md`, `ADOPTING.md`, `SELF-HOSTING.md`, `CLAUDE.md`, `migration-guides/**`, `decisions/**`, `governance/**`, `archive/**`, `examples/**`, `identity/**`, `docs/assets/**`, `docs/agents/**`, `docs/architect-interview.md`, `docs/day-zero-coordinator.md`, `docs/name-clearance.md`, `docs/identity-migration.md`, `.github/ISSUE_TEMPLATE/**`, `.github/pull_request_template.md`, and other prose or public visual assets | Creative Commons Attribution 4.0 International | `CC-BY-4.0` |
| `templates/**` | Creative Commons CC0 1.0 Universal | `CC0-1.0` |
| `adapters/**`, `.claude/hooks/wo_capability_wall.py`, and `init.sh` | MIT No Attribution | `MIT-0` |
| `pyproject.toml`, `writwall_cli/**`, `scripts/**`, `checks/**`, `tests/**`, and `.github/workflows/**` | Apache License 2.0 | `Apache-2.0` |
| `skills/writwall-adopt/**` | The license of each canonical source file, as listed in the bundle's own map | per canonical file |

The full CC-BY-4.0 legal code is at `LICENSE` and
`LICENSES/CC-BY-4.0.txt`. The other legal codes are under `LICENSES/` by SPDX
identifier. Those canonical legal-code copies are not modified.

Appendices A through E appear both inside `DOCTRINE.md` and as extracted files
under `templates/`. HLLMR Ventures LLC deliberately licenses the prose within
the doctrine under CC-BY-4.0 and the extracted templates under CC0-1.0.

Files copied into `skills/writwall-adopt/` do not acquire an umbrella license.
Each inherits the license of its canonical source; see
`skills/writwall-adopt/LICENSE-MAP.md`.

The Writwall name, Writwall revision designations, and associated marks are
not licensed by any license in this map. See [NAMING.md](NAMING.md).

`REUSE.toml` supplies machine-checkable annotations for files without in-file
headers. `python checks/check_licenses.py` verifies every tracked project file,
the explicit metadata exclusions, the four allowed identifiers, and their
canonical legal codes. The distribution gate runs the same check.

`projection/public-files.txt` and generated `PROJECTION-MANIFEST.sha256` are
CC-BY-4.0 metadata under `REUSE.toml`. The projection builder, checker, and
tests are Apache-2.0. Generated `PROJECTION-PROVENANCE.md` is CC-BY-4.0 prose;
every copied file keeps the license assigned to its canonical source path.
