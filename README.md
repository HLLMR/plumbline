<p align="center">
  <img src="docs/assets/writwall-readme-banner-0a5259d8.png" alt="Writwall: document-governed AI work with scoped grants, denial evidence, and human acceptance." width="720">
</p>

<h1 align="center">Writwall</h1>

<p align="center"><strong>Governance for AI-assisted development.</strong></p>

<p align="center">
  <a href="https://github.com/HLLMR/writwall/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/HLLMR/writwall/actions/workflows/ci.yml/badge.svg"></a>
  <a href="https://github.com/HLLMR/writwall/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/HLLMR/writwall?display_name=tag&amp;sort=semver"></a>
  <a href="DOCTRINE.md"><img alt="Doctrine 0.8" src="https://img.shields.io/badge/doctrine-0.8-4f8f8b"></a>
  <a href="SECURITY.md"><img alt="Security policy" src="https://img.shields.io/badge/security-policy-b77945"></a>
</p>

<p align="center">
  <a href="START-HERE.md">Start here</a> ·
  <a href="#try-it-in-five-minutes">Five-minute start</a> ·
  <a href="#using-writwall-at-work">Use at work</a> ·
  <a href="ADOPTING.md">Adopt</a> ·
  <a href="#how-writwall-differs">How it differs</a> ·
  <a href="examples/plumbline-self-hosting-pilot.md">Pilot evidence</a> ·
  <a href="adapters/claude-code/SECURITY.md">Security boundary</a> ·
  <a href="LICENSE-MAP.md">License map</a>
</p>

Writwall governs AI-assisted development with plain files in your repository.
A human ratifies intent and dispatches one bounded work order at a time with an
explicit capability grant. An agent performs the task. A separate review checks
the result against the record, and the human accepts on evidence. Between work
orders, the project returns to lockout.

Spec tools answer *what should the agent build?* Writwall records what comes
next: who authorized the change, what the agent was allowed to touch, what it
tried, what the installed adapter actually blocked, and what a human accepted.

Writwall is a document-controlled governance methodology with a self-hosting reference implementation and project-scaffolding toolkit.
There is no hosted service. It ships one Claude Code adapter; other agents remain
instruction-bounded unless someone builds and birth-tests an equivalent
adapter.

**Formerly Plumbline.** The first public release exposed that the project had
never run an inception name search. We froze promotion, published the failure,
built the missing evidence gate, selected Writwall, and preserved the migration
as a worked case study instead of rewriting history. See
[the identity-migration record](docs/identity-migration.md).

## See the mechanism in 60 seconds

A real example happened during WO-PL-033. While that order was active, another
agent was asked to relink the Git remote. The order did not authorize that work.

1. Its Bash and PowerShell attempts were denied before execution with
   `control_plane_channel_uninspectable`.
2. Its direct edit of `.git/config` was denied with
   `write_target_out_of_grant`.
3. A broad read traversal was separately denied with `read_traversal_denied`.
4. The file remained unchanged and four append-only denial records preserved
   what happened.
5. After the Owner made the separate decision, an authorized coordinator
   performed the relink outside the Implementer's grant.

No denied mutation succeeded. The point is not that the requested change was
bad; it is that the active authority did not permit that agent to make it in
that session. See
[records 306–309](governance/LOG-denials-probes.md#wo-pl-033-concurrent-provider-envelope-denials-post-pilot)
for the retained evidence and limitations.

## The problem

Agent instruction files, architecture decisions, and Spec-driven tools can
state good rules and desired behavior, but they do not by themselves show
which change was authorized, which files and capabilities were in scope, what
the agent tried, what review found, or whether the delivered result still
matches the Owner's intent. Long-running projects then accumulate plausible
documents whose authority and current truth are hard to distinguish.

Writwall gives those facts a chain of custody. In this repository, **Owner**
means the human who controls project intent and acceptance; a **work order** is
one bounded unit of authorized work; **drift** is any difference between the
recorded plan and the observed project state; and a **birth test** is an
attempted forbidden action used to prove that an installed enforcement adapter
actually blocks the current session before real work begins.

## The four-step loop

1. The Owner records intent and the project's current plan.
2. The Owner dispatches one work order with explicit file and capability
   boundaries.
3. An agent implements that order and a separate review checks both the result
   and the record, returning any drift in the same cycle.
4. The Owner accepts or rejects the evidence. Accepted work is closed into
   durable history; between work orders, the project returns to lockout.

## Try it in five minutes

Release `v0.11.0` has one canonical lifecycle and two ordinary entry commands:

```text
python -m pip install "https://github.com/HLLMR/writwall/archive/refs/tags/v0.11.0.zip"

# New idea or clean project: create a temporary local handoff
writwall start --project-root /path/to/your-project

# Existing project or no-write first look: print an Architect handoff only
writwall inspect --project-root /path/to/your-project --role architect
```

From an unpacked source distribution, the fallback is
`py -3 scripts/start_writwall.py --project-root C:\path\to\your-project` on Windows
or `python3 scripts/start_writwall.py --project-root /path/to/your-project` on
macOS/Linux.

`start` observes the target and, only when it is clean/new, creates a
create-only `.writwall-bootstrap/` containing the local adoption bundle and
role handoffs. `inspect` is the safer first command for an employer repository
or any existing project: it prints a bounded, read-only handoff and changes no
project, temporary, profile, privacy-screen, cache, or bytecode state.

Neither command launches an AI provider. Open the employer-approved agent and
interface you want to use, then paste the exact prompt the command emits. A
fresh Architect begins read-only, summarizes bounded local evidence instead of
making you re-explain visible project history, listens to the pitch, challenges
assumptions, and returns a project sketch. Nothing is adopted or implemented
until the human Owner explicitly promotes that sketch.

| Observed state | Fresh role | Prior session stops | Target bytes |
|---|---|---|---|
| Clean/new | Fresh Architect | Launcher; Architect stops before promotion | Create-only bootstrap may be added by `start`; never by `inspect` |
| Partial bootstrap | Recovery coordinator | Incomplete or locked session | Unchanged |
| Adopted or retired lockout | Fresh General (formerly Project-Architect) | Prior onboarding or work session | Unchanged |
| Active work order | Bounded Operator/Implementer | Prior coordinator or Implementer | Unchanged |
| Malformed or contradictory | No role; fail-closed diagnostic | Invoking session | Unchanged |

After promotion, the local adoption bundle guides materialization, wall
installation where supported, and the adoption record. Adoption ends by
handing the repository to a fresh General. The General maintains continuity,
prepares bounded work orders or external-Operator packets, and routes new
design questions back to a fresh Architect. Operators execute; a fresh
Reviewer checks; the Owner accepts or rejects the evidence.

For a source-tree fallback, structured automation, lifecycle-state table, and
recovery prompts, see [START-HERE.md](START-HERE.md). The complete mechanics
are in [ADOPTING.md](ADOPTING.md) and the
[coordinator reference](docs/day-zero-coordinator.md).

### Using Writwall at work

Use only employer-approved AI accounts, interfaces, source-code locations, and
data-handling practices. Writwall records authority inside a project; it does
not override company security, confidentiality, retention, procurement, or
acceptable-use policy.

For an existing workplace repository, start with the no-write command:

```text
writwall inspect --project-root /path/to/work-repository --role architect
```

Then open a fresh approved agent session with access to that repository and
paste the emitted handoff. If you must route it manually, use:

```text
Act as the Writwall Architect for this repository. Start read-only. Use the
handoff below, summarize what the repository already shows, listen to my
project pitch, challenge assumptions, and do not materialize adoption or
dispatch work until I explicitly approve the project sketch.
```

After adoption closes, open a new session and use the coordinator's emitted
General handoff. Its short form is:

```text
Act as a fresh Writwall General for this adopted repository. Begin read-only,
verify the governed lifecycle from repository bytes, recommend the next
bounded decision or work order, and do not activate or implement it until I
approve it.
```

Keep production, infrastructure, DNS, mail, and other account-bearing work in
separately bounded Operator packets and, where practical, separate project
roots and sessions. Never place credentials or secret values in Writwall
intake, handoffs, work orders, prompts, or privacy-screen entries.

The document workflow is provider-neutral. The shipped mechanical capability
wall is currently for Claude Code only and applies only after project-local
installation and a successful birth test in the actual executing session.
Codex, Cursor, Copilot, and other agents remain instruction-bounded unless an
equivalent adapter is installed and birth-tested.

The coordinator does not register, activate, or birth-test the wall. It performs
this routing without installing the wall or claiming adoption.

If the project does not yet have a settled public identity, stop before naming
packages, repositories, domains, or launch assets. Run the evidence-producing
[inception name-clearance gate](docs/name-clearance.md) and have the Owner
dispose the exact candidate first. The gate records what was searched; it is
not a legal opinion.

## What the pilot showed

The evidence is from **one self-hosting pilot conducted under the former
Plumbline identity**: the repository governed ten work orders used to maintain
the methodology itself. It recorded 12 denials and **0
successful out-of-grant mutations**, but also 19 rework cycles and 18 extra
agent sessions. The first five orders needed 4 rework cycles; the last five
needed 15. Under the strict complete-channel metric, every counted order
reported 0 wholly mechanically enforced capability surfaces (for example,
8 declared / 0 enforced / 8 unenforced).

That is evidence that the records exposed real drift and that tested channels
blocked forbidden actions. It is not proof that Writwall lowers operating
cost, contains every tool channel, or generalizes to other teams and projects.
The full public-safe measurements and caveats are in
[the self-hosting pilot](examples/plumbline-self-hosting-pilot.md), conducted
under the former Plumbline identity.

## How Writwall differs

Writwall complements familiar project tools rather than replacing them:

| Tool | What it is best at | What Writwall adds |
|---|---|---|
| A good `CLAUDE.md` or equivalent | Stable project instructions and conventions | Change-controlled authority, per-order capability bounds, denials, review, and closeout evidence |
| Architecture decision records | Durable reasoning for important technical choices | A live plan/current-state distinction and an executable scope for each change |
| Spec-oriented toolkits | Describing desired product behavior and decomposing work | Human ratification, session-local grants, explicit drift handling, and evidence-backed acceptance |

The useful distinction is not more documentation. It is knowing which record
has authority now, what an agent may do in this session, and what evidence must
exist before the Owner calls the work complete.

## Enforcement boundary

Writwall can be used as instruction-bounded governance with any capable agent.
Today, only the supplied **Claude Code** adapter can make selected tool-call
channels mechanically enforced, and only after it is installed for the actual
host and birth-tested in the executing session. Other providers remain
instruction-bounded unless someone builds and tests a provider-specific
adapter. Shells, plugins, MCP tools, subagents, and provider changes must be
classified by what the installed adapter demonstrably intercepts; a passing
document check is never evidence that those channels are physically blocked.

The public candidate intentionally ships the canonical adapter but no active
host-specific hook registration. See the adapter README and [ADOPTING.md](ADOPTING.md)
for installation, preflight, and birth-test requirements.

## One lifecycle, several execution methods

Writwall has one canonical lifecycle: Owner → fresh Architect → explicit
promotion → adoption materialization → fresh General → bounded Operator →
fresh Reviewer → Owner disposition. The coordinator is the normal front door.

Prompt-only Architect conversation, the bundled `writwall-adopt` skill,
`--structured-intake`, and the low-level `init.sh` scaffolder are fallback or
specialized execution methods inside that lifecycle. They are not separate
governance routes and do not change who may ratify, activate, implement,
review, or accept. See [ADOPTING.md](ADOPTING.md) for the exact adoption
sequence and [START-HERE.md](START-HERE.md) for copy/paste prompts.

The pre-dispatch validator is deterministic, read-only, and standard-library
only. `--lockout` checks the between-order state, `--work-order <path>` checks a
candidate before activation, and `--active` checks the current pointer and work
order. It prepares dispatch; it does not enforce tools or repair files.

The standalone Claude Code adapter supports CPython 3.10–3.14 and includes a
read-only installation `--preflight`. The full repository test and license
tooling requires CPython 3.11–3.14.

## Revision and artifact roles

Three things carry three different names here:

- **`DOCTRINE.md` is the methodology.** It is clause-numbered,
  change-controlled, and written for humans.
- **The public distribution and reference implementation** ships the doctrine,
  templates, adapters, adoption tooling, checks, and selected public-safe
  evidence. It does not govern its own public checkout.
- **A project-local instantiation is a governance system.** It belongs to the
  adopting project from the moment it is created.

Current revision: **0.8, ratified 2026-08-21** by `decisions/DR-005.md`,
superseding 0.7, which was ratified by `decisions/DR-004.md` on 2026-08-20.
Revision 0.6 was ratified by `decisions/DR-001.md` on 2026-08-16 and was the
first authoritative methodology revision; 0.1 through 0.5 were never
ratified. The 0.1 proposal is retained only in the private governed source's
`archive/` and never enters a public candidate. Projects bind to a ratified
revision and move only by an Owner-ratified migration (Doctrine DC.4).

This repository's private self-hosting instance first adopted 0.6 under the
former identity and later migrated cumulatively to 0.8. Its ratifying project
decision is a private record not
carried by public candidates; `SELF-HOSTING.md` preserves the public-safe
summary. See `DOCTRINE.md` DC.1, `decisions/README.md`, and the two guides under
`migration-guides/` for the complete revision history.

Ratification establishes a stable baseline for testing. It does not claim the
methodology is proven.

---

## What is in this repository

The layout below is a **reference layout for the private governed source
repository** — how Writwall's own working tree is organized, including
this repository's own governance instance under `governance/` and its
methodology decision log under `decisions/`. It documents that layout; it is
not necessarily the tree a given reader is looking at, and no artifact
described elsewhere in this file claims to be it. The **source
distribution** is a subset of it that ships to adopters: everything below
except this repository's own working records (see "The archive is a source
distribution" further down). A third, narrower artifact — the
**positive-allowlist candidate** built by `scripts/build_public_projection.py`
from the exact list in `projection/public-files.txt` — is neither of those:
it is a derived, external, publication-input subset described in
[PUBLICATION.md](PUBLICATION.md). It does not claim to inventory the private
governed source repository. It carries the governance evidence the allowlist
selects (for example, public-safe self-hosting and pilot records), but it
does not carry every path shown below; `archive/` and the checked-in `dist/`
are private-governed-source-only and are absent from every
positive-allowlist public candidate, as marked below.

```
writwall/
├── DOCTRINE.md              The methodology, for humans. Formal clause numbering,
│                            change-controlled under its own DC section.
├── ADOPTING.md              How to instantiate the doctrine into a project.
├── decisions/               Methodology-level decision log (Doctrine DC.3.4).
│                            Project decisions never live here.
├── templates/               Appendices A through E, extracted verbatim:
│   ├── A-charter.md           tier-1 injectable
│   ├── B-work-order.md        work order with capability grant
│   ├── C-owner-brief.md       reviewer output to the Owner
│   ├── D-adoption-record.md   DR-001 for an adopting project
│   └── E-adoption-mapping.md  disposition worksheet for existing documents
├── adapters/                Reference enforcement adapters, one directory per
│   └── claude-code/         provider. Each README states exactly what the
│                            adapter makes physical and what it does not.
├── migration-guides/        One companion per revision transition, e.g.
│                            0.1-to-0.6.md. Followed only when a project moves.
├── skills/                  Agent-assisted mechanics within the canonical lifecycle.
│   └── writwall-adopt/     Self-contained bootstrap bundle: carries its own
│                            doctrine, guides, adapter, and templates.
├── checks/                  Deterministic distribution checks. Nonzero exit on
│                            a drifted copy, stale reference, or bad package.
├── scripts/                 Distribution builder (standard library only).
├── tests/                   Unit tests for the adapter and the scaffolder.
├── examples/                Evidence-backed examples from completed pilots:
│                            plumbline-self-hosting-pilot.md (former identity).
├── archive/                 Superseded doctrine revisions and drafts, retained
│                            as historical evidence, never current authority.
│                            Private governed source only; not carried by any
│                            public candidate (see PUBLICATION.md).
├── init.sh                  Scaffolder: copies templates and creates the
│                            governance directory in a target repository.
└── README.md
```

Pre-adoption records are retained under the private `archive/`; `dist/` holds
build output. Neither is part of a positive-allowlist public candidate.

`CLAUDE.md` at the root is Writwall's own operating charter: the tier-1 injectable of the repository-local governance instance described in Doctrine 5.1.4. It ships in the private governed source distribution deliberately, as an inspectable worked example. In the clean-history public projection the builder replaces it with a short public-only notice stating that the checkout is ungoverned and ordinary contribution is allowed; the private-instance instructions never enter public bytes. It is not a template, and section "The archive is a source distribution" below says exactly what that means for you.

## The archive is a source distribution

`writwall-<revision>.zip` is **a source distribution, not an overlay.** Do not unpack it into your project.

Unpacking it on top of a repository would drop Writwall's own charter, doctrine, work history, and eventually its governance directory into your project root, where your agents would read another project's records as if they were yours. That is precisely the stale-but-discoverable failure the doctrine exists to eliminate (Doctrine 5.3.4).

What you actually do is instantiate **only the applicable project-side artifacts** through the one canonical lifecycle in `ADOPTING.md`. Those artifacts are:

```
<your-project>/
├── CHARTER.md (or your tooling's existing auto-loaded file, e.g. CLAUDE.md)
├── .claude/hooks/wo_capability_wall.py       (or your provider's adapter)
├── checks/check_work_order_dispatch.py       deterministic pre-dispatch validator
└── governance/                               (created empty; you fill it)
```

Everything else in the archive is either the methodology itself, which you read, or Writwall's own working records, which you may read as an example and never copy.

**Never copied into an adopting project:** Writwall's root `CLAUDE.md`, its `governance/` directory, its decisions, plan, state, routing map, work orders, reports, briefs, history, and its authority. Doctrine 5.1.5 states this as a rule; the adoption tooling enforces it by only ever copying templates, the adapter, and the pre-dispatch validator, and `checks/check_distribution.py` fails if a Writwall governance record ever appears inside the adoption skill's bundle.

## What is instantiated into a project

Not this repository. A project receives the project-side artifacts the doctrine requires (Doctrine 5.2), copied and then owned locally:

```
<your-project>/
├── CHARTER.md (or the file your agent tooling already auto-loads, e.g. CLAUDE.md)
├── .claude/hooks/wo_capability_wall.py       (or your provider's adapter)
├── checks/check_work_order_dispatch.py       deterministic pre-dispatch validator
└── governance/
    ├── PLAN.md  STATE.md  ROUTING.md  LOG.md
    ├── decisions/  work-orders/  reports/  briefs/  rfis/
    ├── history/    archive/
```

`DOCTRINE.md` is deliberately not copied into projects. Agents never receive the doctrine. They receive the project's charter and routed project records (Doctrine 1.2.2).

## Revision binding and updates

A project's adoption record states `Doctrine revision: 0.x`, not `dependency: writwall@0.x`. When Writwall publishes a later revision, nothing changes in any project until that project's Owner ratifies a migration (Doctrine DC.4). A migration is change-controlled: compare revisions, list the affected local artifacts, update them, record a decision, commit. There is no automatic upgrade path by design; a governance substrate that updates itself underneath a running project is a source of drift, which is the thing this exists to prevent.

## What Writwall is not, yet

There is no `writwall validate`, no `writwall diff`, and no dashboard. Each of those is worth building only if pilot data shows the manual version costs more than the tool would. The methodology's own rule applies to the methodology: build what a fixture forces.

## Licensing

HLLMR Ventures LLC licenses Writwall prose under CC-BY-4.0, extracted
templates under CC0-1.0, adapters and `init.sh` under MIT-0, and scripts,
checks, and tests under Apache-2.0. Files in the adoption bundle retain their
canonical licenses. Extracted templates and adapters use CC0-1.0 and MIT-0
respectively; the bundled pre-dispatch checker retains its canonical
Apache-2.0 terms.

The authoritative path-by-path terms are in [LICENSE-MAP.md](LICENSE-MAP.md).
Run `python3 -B checks/check_licenses.py` with Python 3.11 or newer for the
machine-checkable SPDX/REUSE gate;
the distribution checker invokes it as part of the ordinary source gate.
The Writwall name and revision designations are not licensed; see
[NAMING.md](NAMING.md).

## Building a public projection

The governed repository and its checked-in `dist/` archive are not publication
artifacts. `scripts/build_public_projection.py` instead derives a fresh,
positive-allowlist candidate in an empty directory outside this repository.
The builder and checker automatically use the project-specific local privacy
screen initialized by `writwall start`; its location, values, matches, and
value-derived hashes are never copied into the candidate or printed.

```bash
python scripts/build_public_projection.py \
  --output /absolute/empty/candidate
python checks/check_public_projection.py \
  /absolute/empty/candidate
```

For controlled compatibility automation, both commands retain an explicit
`--private-pattern-file` override. Ordinary users should not create or
repeatedly reconstruct one. See [managed local privacy screening](docs/privacy-screen.md).

The candidate contains a deterministic hash manifest and a provenance record
that classifies source-repository commit identifiers without pretending they
exist in the candidate's future clean history. The checker rejects inherited
Git state, private historical trees, stale archives, unclassified identifiers,
host paths, active transactional records, unknown files, and private-pattern
matches. It also runs the candidate's license and projection-mode distribution
checks. See [PUBLICATION.md](PUBLICATION.md) for the full boundary and the
separate Owner-only publication decision.

## Status

The ten-work-order self-hosting pilot and its fresh-agent evaluation are
complete. Disclosure cleanup, license mechanization, and the clean-history
projection gate and cumulative project-local migration are complete. Doctrine
0.8 is the current ratified revision (`decisions/DR-005.md`). The separate
private governed source's project-side governance instance is operatively bound to Doctrine 0.8; its ratifying `governance/decisions/DR-003.md` is not
carried by public candidates, while `SELF-HOSTING.md` carries the public-safe
summary.

Building or checking a public projection candidate does not itself publish
it (see [PUBLICATION.md](PUBLICATION.md)); the private governed repository
and any published projection remain separate. Whether and when a given copy
of this text is being read before or after a publication decision, no
current Git history or checked-in archive is, or ever was, a public-release
candidate in its own right — only a freshly built, checked positive-allowlist
projection is.
