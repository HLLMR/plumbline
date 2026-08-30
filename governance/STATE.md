> **Snapshot note: this record is a snapshot of the private governed source at the source commit named in `PROJECTION-PROVENANCE.md`. Push, publication, visibility, and queued-work statements below describe that checkpoint, not the current public copy.**

# STATE — Writwall

As-is, not should-be. Ratified intent lives in `governance/PLAN.md`; this file
records the repository state observed after the Plumbline 0.8 public release,
accepted WO-PL-034 public-front-door polish, accepted WO-PL-035 onboarding
repair, accepted WO-PL-036 name-clearance and replacement selection, and
accepted WO-PL-037 controlled migration to the current **Writwall** identity,
accepted WO-PL-038 wall-glyph identity correction, accepted WO-PL-039
cache-safe public-identity and repository hardening, and accepted WO-PL-040
executable day-zero coordination.

**Derived:** 2026-08-29 from the ten accepted pilot records, the Doctrine 9.3.1
fresh-agent evaluation, ratified DR-002 and project-migration DR-003, and
accepted WO-PL-017 through WO-PL-023 and WO-PL-025 through WO-PL-033 records,
the WO-PL-024 sequencing recovery, and the verified public-release event.
**Boundary:** post-adoption, all 10 counted pilot work orders and their
evaluation complete; WO-PL-017 remediation complete; DR-003 ratified;
WO-PL-018 through WO-PL-023 complete; WO-PL-024 void before implementation;
WO-PL-025 complete and the project operatively bound to Doctrine 0.8;
WO-PL-026 complete and RFI-22 closed; WO-PL-027 through WO-PL-033 complete;
Plumbline 0.8 publicly released from a one-commit clean-history projection;
WO-PL-034 through WO-PL-038 complete; **Writwall** selected and implemented as
the current identity with the two-line wall glyph; WO-PL-039 complete and
accepted, with public PR #5 merged after the required CI passed and issue #4
closed; WO-PL-040 complete and accepted; WO-PL-041 authorized but not active.
The hash of the commit containing this file is intentionally recorded only
externally.

---

## OBSERVED

### Authority and adoption

| Fact | Value |
|---|---|
| Doctrine | Revision 0.8, ratified and operative for this project from materialization of `governance/decisions/DR-003.md` (private governed-source record, not carried by public candidates) before WO-PL-025 activation |
| Methodology decision | `decisions/DR-001.md` |
| Project adoption record | `governance/decisions/DR-001.md`, ratified |
| Pilot evaluation decision | `governance/decisions/DR-002.md`, ratified 2026-08-20; retain Doctrine 0.6 provisionally |
| Project migration decision | `governance/decisions/DR-003.md` (private governed-source record, not carried by public candidates), ratified 2026-08-21; cumulative migration from 0.6 to 0.8 became operative on exact decision and charter materialization before WO-PL-025 activation |
| Baseline commit | `a905c87987f31094121c11a3b8163f97ef1abcf4` |
| Adoption commit | `8d5b2b3668ef626525e57028ac09661e17d44edc` |
| Checkpoint 1 | `d790a2b8d500a1c3a5e10af9f0a78d1c3c3f4e3a` |
| WO-PL-007 | COMPLETE, retained in `governance/history/`; counted pilot work order 1 of 10 |
| WO-PL-008 | COMPLETE, accepted 2026-08-18; counted pilot work order 2 of 10. Records retained in `governance/history/` |
| WO-PL-009 | **COMPLETE**, accepted 2026-08-19; counted pilot work order **3 of 10**. Records retained in `governance/history/` |
| WO-PL-010 | **COMPLETE**, accepted 2026-08-19; counted pilot work order **4 of 10**. Records retained in `governance/history/` |
| WO-PL-011 | **COMPLETE**, accepted 2026-08-19; counted pilot work order **5 of 10**. Fresh local source archive created; records retained in `governance/history/` |
| WO-PL-012 | **COMPLETE**, accepted 2026-08-19; counted pilot work order **6 of 10**. Native Claude Code read-deny enforcement implemented and birth-tested; records retained in `governance/history/` |
| WO-PL-013 | **COMPLETE**, accepted 2026-08-19; counted pilot work order **7 of 10**. Portable outside-target fixtures and a local Windows-plus-POSIX acceptance rule delivered; records retained in `governance/history/` |
| WO-PL-014 | **COMPLETE**, accepted 2026-08-20; counted pilot work order **8 of 10**. Deterministic pre-dispatch validator delivered after two fresh-review returns; records retained in `governance/history/` |
| WO-PL-015 | **COMPLETE**, accepted 2026-08-20; counted pilot work order **9 of 10**. Transient live-work release gate delivered after three fresh-review correction cycles; records retained in `governance/history/` |
| WO-PL-016 | **COMPLETE**, accepted 2026-08-20; counted pilot work order **10 of 10**. Portable adopter pre-dispatch validator delivered after three fresh-review correction cycles; records retained in `governance/history/` |
| WO-PL-017 | **COMPLETE**, accepted 2026-08-20; post-pilot remediation, not counted. Complete manifest enforcement and evaluation disposition delivered after two fresh-review correction returns; records retained in `governance/history/` |
| WO-PL-018 | **COMPLETE**, accepted 2026-08-20; post-pilot disclosure cleanup and license records, not counted. DR-003's license map is documented, official license texts and contribution/naming boundaries are present, and distribution checks cover the required records and current public-facing claims; accepted after three review returns; records retained in `governance/history/` |
| WO-PL-019 | **COMPLETE**, accepted 2026-08-20; post-pilot license mechanization, not counted. SPDX/REUSE coverage, a public license checker, executable headers, and distribution integration are complete; records retained in `governance/history/` |
| WO-PL-020 | **COMPLETE**, accepted 2026-08-20; post-pilot clean-history public projection, not counted. Deterministic positive-allowlist builder/checker and reproducible external candidate/archive verification complete; records retained in `governance/history/`; publication is not authorized |
| WO-PL-021 | **COMPLETE**, accepted 2026-08-21; post-pilot Doctrine 0.7 template/validator alignment, not counted. Amended cross-platform and two-build projection gates passed; records retained in `governance/history/`; project governance remains bound to Doctrine 0.6; publication is not authorized |
| WO-PL-022 | **COMPLETE**, accepted 2026-08-21; post-pilot public projection documentation truth, not counted. Full Windows and two real native-Ubuntu candidate suites passed; final fresh review returned ACCEPT/HIGH; Owner reported 12 actual active minutes; records retained in `governance/history/`; publication is not authorized |
| WO-PL-023 | **COMPLETE**, accepted 2026-08-21; post-pilot Doctrine 0.8, adopter-contract, and projection-integrity remediation, not counted. Windows and native Ubuntu each passed 487 tests; fresh review returned CONFORMANCE PASS; two independent 92-file projections were checker-clean and byte-identical; records retained in `governance/history/`; project governance remains bound to Doctrine 0.6; publication is not authorized |
| WO-PL-024 | **VOID BEFORE IMPLEMENTATION**, disposed 2026-08-21. Prematurely activated under project binding 0.6; candidate/active structural validation only; no implementation, RED/GREEN test, product test, provider birth test, commit, or push. Work order and exact Owner lifecycle record retained in `governance/history/`; identifier permanently consumed |
| WO-PL-025 | **COMPLETE**, accepted 2026-08-21; post-pilot cumulative project migration from Doctrine 0.6 to 0.8, not counted. Exact DR-003 and charter binding materialization made 0.8 operative before activation; all five project templates match canonical 0.8; Windows and native Ubuntu each passed 487 tests; fresh review returned CONFORMANCE PASS/HIGH; records retained in `governance/history/`; no commit, push, publication, or successor activation |
| WO-PL-026 | **COMPLETE**, accepted 2026-08-26; post-pilot capability-wall hardening and portability, not counted. Protected-control-plane floor implemented; Windows and native Linux birth-test matrices each denied `30/30` valid probes with zero protected mutation; Windows and Ubuntu each passed 506 tests; fresh final review returned ACCEPT with no correction; RFI-22 closed Yes; records retained in `governance/history/`; publication and WO-PL-027 remain unstarted |
| WO-PL-027 | **COMPLETE**, accepted 2026-08-26; post-pilot verification-only public release candidate, not counted. Five bounded release-truth corrections accepted; Windows and native Ubuntu governed-source and dual-candidate suites passed; two 92-file projections and their archives were byte-reproducible; ninth fresh review returned ACCEPT/HIGH; Owner reported 22 actual active minutes; records retained in `governance/history/`. Session candidates were deleted and are not publishable; publication remains a separate unmade Owner decision after a post-closeout rebuild and review |
| WO-PL-028 | **COMPLETE**, accepted 2026-08-26; post-pilot publication-truth and final-byte remediation, not counted. Publication-neutral public/private identity and evidence boundaries corrected; final Windows/native-Ubuntu governed-source and dual-candidate suites passed; two 92-file projections were checker-clean and byte-identical; final fresh review returned ACCEPT; Owner accepted the disclosed canary-ordering deviation and reported active minutes **NOT REPORTED**; records retained in `governance/history/`. Diagnostic candidates were deleted and are not publishable; publication remains a separate unmade Owner decision after a new post-closeout rebuild and review |
| WO-PL-029 | **COMPLETE**, accepted 2026-08-26; post-pilot publication snapshot/privacy remediation, not counted. Projected State is snapshot-qualified; concrete omitted report references are checked across inline-code, plain, and Markdown-link forms; private-input fingerprints are absent from public provenance; complete-ledger derivation is canonical. Final Windows/native-Ubuntu governed-source and dual-candidate suites passed; two 92-file projections and their archives were byte-identical; fresh re-review returned PUBLICATION ACCEPT. Owner accepted the disclosed coordinator-awareness privacy-process deviation and no-impact Reviewer diagnostic; active minutes **NOT REPORTED**. Records retained in `governance/history/`; all candidates/private inputs were deleted, so publication remains a separate unmade Owner decision after a new post-closeout rebuild and review |
| WO-PL-030 | **COMPLETE**, accepted 2026-08-27; post-pilot public-release blocker closure, not counted. Host-neutral public hook registration, truthful CI/first-use documentation, runtime/dispatch hardening, retained-reference enforcement, and canonical projection behavior are implemented. Final source and two independent public candidates passed Windows and native Ubuntu; fresh publication review returned ACCEPT/HIGH. Canonical and installed adapter bytes match; native Windows/Ubuntu control-plane matrices denied all 25 exposed mutations with zero success. Owner active minutes **NOT REPORTED**. Records retained in `governance/history/`; publication remains a separate unmade Owner decision after a new post-closeout dual rebuild and review |
| WO-PL-031 | **COMPLETE**, accepted 2026-08-27; post-pilot final public-source hardening, not counted. Projection command context, conservative traversal grammar, portable control-plane aliases, malformed pointed-work-order read lockout, explicit project-root authority, and boundary-aware private-path checks are implemented. Final governed source and two independent 92-file public candidates passed Windows and native Ubuntu; final fresh re-review returned ACCEPT. Owner active minutes **NOT REPORTED**. Records retained in `governance/history/`; the installed private hook remains on the prior accepted digest pending a separately governed installation/birth test, and publication remains a separate unmade Owner decision |
| WO-PL-032 | **COMPLETE**, accepted 2026-08-27; post-pilot installed-hook refresh and publication gate, not counted. Installed, canonical, and bundled hook bytes match the accepted digest; native Windows and Ubuntu Sonnet sessions each produced four exact birth-test denials with zero mutation; full and focused regression gates passed; fresh read-only review returned ACCEPT/HIGH. Owner active minutes **NOT REPORTED**. Records retained in `governance/history/`; publication remains a separate unmade Owner decision after the authorized post-closeout dual rebuild and review |
| WO-PL-033 | **COMPLETE**, accepted 2026-08-28; post-pilot public front door and release hygiene, not counted. README now leads with the authority-and-enforcement layer, honest first-value route, pilot economics, and provider boundary; official CC legal text and executable license guards are present; methodology/project decision references are truthful. Final governed source and two independent 92-file candidates passed Windows and native Ubuntu; candidates and archives were byte-identical. Owner active minutes **NOT REPORTED**. Records retained in `governance/history/`; publication remains a separate Owner decision using a new clean-history repository |
| WO-PL-034 | **COMPLETE**, accepted 2026-08-28; post-publication public-front-door polish, not counted. The Owner rejected the first generated illustration and accepted the launch kit's exact regenerated type-only README/social assets plus the evidence-first tonal revision. Active minutes **NOT REPORTED**; records retained in `governance/history/` |
| WO-PL-035 | **COMPLETE**, accepted 2026-08-28; post-publication human-onboarding and public-contribution repair, not counted. A human-first start page, coordinator prompts, safe bootstrap/recovery rules, issue/PR workflow, and deterministic cross-document checks are complete. The first fresh novice review returned six material findings; all were corrected and a different fresh Reviewer returned ACCEPT. Active minutes **NOT REPORTED**; records retained in `governance/history/` |
| WO-PL-036 | **COMPLETE**, accepted 2026-08-28; post-publication inception name-clearance evidence and replacement selection, not counted. Public collector/checker, worked incident, four canonical ledgers, and release-disposition pins are complete. Owner rejected Plumbline, Grantcord, and Writcord and accepted **Writwall** after named-human web/common-law and USPTO review. Windows passed 638 tests, native Ubuntu passed 74 focused/integration tests, two 112-file projections reproduced byte-for-byte, and the fifth fresh Reviewer returned ACCEPT. Active minutes **NOT REPORTED**; records retained in `governance/history/`; identity migration remains unstarted |
| WO-PL-037 | **COMPLETE**, accepted 2026-08-29; controlled identity migration from Plumbline to **Writwall**, not counted. Current product surfaces, adoption skill, code constants, repository coordinates, and visual assets are migrated; historical Plumbline facts remain pinned by `identity/legacy-references.json`. Windows and Ubuntu governed-source/candidate suites passed; two private-pattern candidates were byte-identical; live-wall canary record 310 is valid; fresh Sonnet review returned **ACCEPT WITH NON-BLOCKING POLISH**. Owner active minutes **NOT REPORTED**. The closeout records one unauthorized read-only history traversal with no implementation impact. Records retained in `governance/history/`; no push, public-repository rename, release, tag, `dist/` replacement, website edit, or external launch action occurred |
| WO-PL-038 | **COMPLETE**, accepted 2026-08-29; post-migration wall-glyph identity correction, not counted. The Owner rejected the inherited plumb-line/bob device and accepted the two-line wall at the `writ|wall` boundary. Focused and complete tests, identity, licensing, dispatch, and whitespace checks passed; fresh review returned **ACCEPT** after one report-only transient-count correction. Active minutes **NOT REPORTED**. Public issue #2 projection/PR update merged as public PR #3; the merged bytes were correct, but GitHub continued serving the retired banner from its unchanged published image URL, now recorded as public issue #4 |
| WO-PL-039 | **COMPLETE**, accepted 2026-08-29; post-migration cache-safe public identity and repository hardening, not counted. README now uses a digest-bound wall-glyph banner path; the live GitHub social preview is byte-identical to the accepted wall source; CI actions are full-SHA pinned behind one stable required check; supported repository rules, merge hygiene, Actions restrictions, vulnerability reporting, scanning, push protection, and topics are active. Windows passed 657 tests with two skips; the native Ubuntu candidate passed 657 with three skips; two 117-file candidates were checker-clean and byte-identical; corrected fresh re-review returned **ACCEPT**. Owner active minutes **NOT REPORTED**. Records retained in `governance/history/`; post-closeout public PR #5 merged only after both live `CI required` checks passed and public issue #4 closed |
| WO-PL-040 | **COMPLETE**, accepted 2026-08-29; executable day-zero coordinator, lifecycle-state routing, atomic create-only bootstrap handoff, external-Operator packet model, and sanitized eight-domain DNS/mail walkthrough. Three fresh reviews drove fail-closed multi-ACTIVE/link handling, complete scenario/intake coverage, and atomic publication. Final suite 687 OK with two skips; two 120-file candidates checker-clean and byte-identical; final review ACCEPT WITH NON-BLOCKING POLISH. Owner active minutes **NOT REPORTED**; records retained in `governance/history/` |
| Pilot progress | **10 of 10 counted work orders complete; fresh-agent evaluation accepted with calibrations and disposed by DR-002** |
| Post-pilot sequence | **WO-PL-017 through WO-PL-023 COMPLETE**; WO-PL-024 **VOID BEFORE IMPLEMENTATION**; WO-PL-025 through WO-PL-040 **COMPLETE**; Plumbline 0.8 is the historical public release; **Writwall migration, repository hardening, and executable day-zero coordination accepted**; WO-PL-041 authorized but inactive pending closeout/public issue #1 sequence |
| Bootstrap history | Eleven completed work orders retained as uncounted pre-adoption evidence under `archive/pre-adoption-bootstrap/` |

### Verification accepted at WO-PL-016 closeout

Fresh review returned the implementation through three correction cycles, then
returned **ACCEPT/HIGH** with no remaining implementation defect. The final
checks exercised active refusal and clean eligibility separately.

| Check | Result |
|---|---|
| Native Windows full suite | **372 tests, 0 failures**, one expected lifecycle skip |
| Native Ubuntu WSL full suite | **372 tests, 0 failures**, one expected lifecycle skip |
| Active source distribution checks | **Exit 1** on Windows and Ubuntu, exactly three transient-state findings |
| Active external build | **Exit 1 before output creation** |
| Clean-state external build | Live-state-removed diagnostic copy: **123 payload files plus `MANIFEST.sha256`**; real post-closeout tree: **126 plus manifest**; both archive checks exit 0 |
| `git diff --check` | Clean |
| Staged changes | None |
| `dist/` | Unchanged; no final or replacement artifact created |
| Git history at review | Local HEAD unchanged at `a51916c`; WO-PL-016 closeout is one later local commit and is not pushed |
| Temporary archive | External verification artifact only; checked-in `dist/` unchanged |

The canonical, installed, and bundled adapters are byte-identical at
`a3ba5b5b465a06cdac357c8024dac5c0c5da4db4d946eac6565a3aa02f80c3fe`.
WO-PL-013 changed no adapter code. The canonical and bundled adapter README
copies are byte-identical and now require native Windows and native POSIX test
legs for adapter or adapter-test changes. This local acceptance rule is
instruction-only; no hosted CI was added. Native read-tool protection remains
a birth-tested channel, not a claim that every filesystem-read channel is
walled. No publication, tag, license selection, visibility change, or `dist/`
replacement occurred.

### Enforcement evidence

| Fact | Value |
|---|---|
| Adapter | Canonical, bundled, and installed copies byte-identical at `DD29AF2A39D25E0270AD9ACC23EE912F81E39C674E1179759F4A3010C6A0C1A0` after accepted WO-PL-032 installation and birth testing |
| Registration | Project `PreToolUse`, matcher `*`, command through `${CLAUDE_PROJECT_DIR}` |
| Birth tests | Level 1 passed; Level 2 mixed; WO-PL-012 Level 3 native read-tool test passed; WO-PL-013 added a passing Windows-plus-POSIX regression gate without changing the adapter |
| Declared/enforced/unenforced for WO-PL-016 | 8 / 0 / 8 under the strict complete-surface definition. Native write/read-tool controls are real but partial; shell remained restricted and path scope through shell remains unenforced |
| Declared/enforced/unenforced for WO-PL-022 | **8 / 8 / 0** under the Owner-authored work-order classification accepted by the final Reviewer. Native filesystem channels combined the live project hook with provider path scoping; the remaining six surfaces relied on independently attested session tool exclusion. That provisioning attestation is not represented as a Doctrine 8.3.5 observed-denial birth test |
| Declared/enforced/unenforced for WO-PL-023 | **8 / 0 / 8** under the active order's strict complete-surface declaration. Native read/write controls produced observed denials but did not cover every channel; no whole declared surface is represented as mechanically enforced |
| Declared/enforced/unenforced for WO-PL-025 | **8 / 0 / 8** under the strict complete-surface declaration. Record 87 proves only the fresh session's ordinary file-edit path scope; no Doctrine 8.7 categorical control-plane birth test or whole-surface enforcement is claimed |
| Declared/enforced/unenforced for WO-PL-026 | **8 / 0 / 8** under the strict complete-surface declaration. The protected control plane is categorically denied through every exposed mutation-capable channel in the accepted Windows/POSIX birth-test matrices, but that does not make any entire broad capability surface wholly enforced |
| Declared/enforced/unenforced for WO-PL-027 | **8 / 0 / 8** under the strict complete-surface declaration. The bounded Sonnet session produced observed native read/write and shell denials, but no entire declared surface is represented as comprehensively enforced |
| Declared/enforced/unenforced for WO-PL-028 | **8 / 0 / 8** under the strict complete-surface declaration. The bounded Sonnet session produced native read/write denials, but no entire declared surface is represented as comprehensively enforced |
| Declared/enforced/unenforced for WO-PL-029 | **8 / 0 / 8** under the strict complete-surface declaration. The bounded Sonnet session produced native write, read-traversal, and shell denials, but no entire declared surface is represented as comprehensively enforced |
| Declared/enforced/unenforced for WO-PL-030 | **8 / 0 / 8** under the strict complete-surface declaration. The protected control plane is categorically denied through every exposed Windows/POSIX mutation channel in the accepted birth-test matrices, but that does not make any complete broad capability surface wholly enforced |
| Declared/enforced/unenforced for WO-PL-031 | **8 / 0 / 8** under the strict complete-surface declaration. This Codex session was instruction-bounded and made no live-hook canary or whole-surface enforcement claim |
| Declared/enforced/unenforced for WO-PL-032 | **8 / 0 / 8** under the strict complete-surface declaration. Native Write interception and the protected-control-plane floor produced accepted Windows/Ubuntu evidence, but no entire broad capability surface is represented as comprehensively enforced |
| Declared/enforced/unenforced for WO-PL-033 | **8 / 0 / 8** under the strict complete-surface declaration. Codex implementation was instruction-bounded; a separate Claude Code session produced four genuine wall denials, but no complete broad capability surface is represented as comprehensively enforced |
| Denial log | **309** append-only records, SHA-256 `AE6485A2353183917397219801F8443871FE6ED59F0C3CEE27F3D8B6EAE11D85`. Records 306-309 are WO-PL-033 post-pilot denials from the Owner-started VS Code session and do not alter the accepted pilot aggregate; no denied mutation succeeded |
| Successful out-of-grant mutations in WO-PL-016 | **0** |
| Successful out-of-grant mutations in WO-PL-022 | **0** |
| Successful out-of-grant mutations in WO-PL-023 | **0** |
| Successful out-of-grant mutations in WO-PL-025 | **0** |
| Successful protected-control-plane mutations in WO-PL-026 | **0** |
| Successful out-of-grant mutations in WO-PL-027 | **0** |
| Successful out-of-grant mutations in WO-PL-028 | **0** |
| Successful out-of-grant mutations in WO-PL-029 | **0** |
| Successful protected-control-plane mutations in WO-PL-030 | **0** |
| Successful out-of-grant mutations in WO-PL-031 | **0** |
| Successful protected-control-plane mutations in WO-PL-032 | **0** |
| Successful out-of-grant mutations in WO-PL-033 | **0** |

#### Recent denial-record classification

Classifications are recorded in `governance/LOG-denials-probes.md`. Records 1–40
belong to earlier work and are unchanged, including record 38, which remains
WO-PL-008's single counted 9.2.1 denial and is not reclassified.

| Record | Classification | Counted under 9.2.1? |
|---|---|---|
| 41 | Live-wall canary, first WO-PL-009 implementer session | **Excluded** |
| 42 | Live-wall canary, continuation implementer session | **Excluded** |
| 43 | Live-wall canary, records-only closeout session | **Excluded** |
| 44 | Closeout-transition lockout after the completed work order moved to history; no active work order resolved | **Excluded** |
| 45 | WO-PL-010 implementer live-wall canary | **Excluded** |
| 46 | WO-PL-011 implementer live-wall canary | **Excluded** |
| 47, 48, 50, 51, 58 | WO-PL-012 session canaries | **Excluded** |
| 49, 52 | WO-PL-012 non-mutating read denials | **Excluded** |
| 53 | Unsupported `ScheduleWakeup` mutation attempt | **Counted** |
| 54–57 | WO-PL-012 Level-3 birth-test probes | **Excluded** |
| 59 | WO-PL-013 live-wall canary | **Excluded** |
| 60 | WO-PL-014 live-wall canary | **Excluded** |
| 61–63 | WO-PL-014 genuine read-traversal attempts | **Counted** |
| 64 | WO-PL-015 live-wall canary | **Excluded** |
| 65–70 | WO-PL-015 genuine read-traversal attempts | **Counted** |
| 71 | WO-PL-016 live-wall canary | **Excluded** |
| 72 | WO-PL-021 Sonnet live-wall canary | **Excluded** |
| 73 | WO-PL-022 Sonnet live-wall canary | **Excluded** |
| 74 | WO-PL-023 non-mutating read-traversal denial | **Post-pilot; not in pilot aggregate** |
| 75–76 | WO-PL-023 live-wall canary write/read pair | **Excluded** |
| 77–83 | WO-PL-023 non-canary read/write denials | **Post-pilot; not in pilot aggregate** |
| 84–86 | WO-PL-023 out-of-repository read denials during local verification setup | **Post-pilot; not in pilot aggregate** |
| 87 | WO-PL-025 fresh-session ordinary file-edit path-scope canary | **Excluded** |
| 88 | WO-PL-026 fresh-session ordinary file-edit canary | **Excluded** |
| 89-260 | WO-PL-026 protected-control-plane birth-test and lifecycle-recovery probes | **Post-pilot instrument evidence; excluded** |
| 261, 263-266 | WO-PL-027 provider-envelope read/shell denials | **Post-pilot; not in pilot aggregate** |
| 262 | WO-PL-027 live-wall canary | **Excluded** |
| 267 | WO-PL-028 read-traversal denial | **Post-pilot; not in pilot aggregate** |
| 268 | WO-PL-028 live-wall canary, fired after granted edits | **Excluded; ordering deviation Owner-accepted** |
| 269 | WO-PL-029 live-wall canary | **Excluded** |
| 270 | WO-PL-029 broad read-traversal denial | **Post-pilot; not in pilot aggregate** |
| 271 | WO-PL-029 Bash attempt denied before execution | **Post-pilot; not in pilot aggregate** |
| 272-284 | WO-PL-030 native Windows protected-control-plane birth-test, session `2f2bf959-7d26-4dc3-8c3a-ed8876362ad1` | **Post-pilot instrument evidence; excluded** |
| 285-296 | WO-PL-030 native Ubuntu protected-control-plane birth-test, session `737ca4e5-204b-4268-b6ea-46f42981513c` | **Post-pilot instrument evidence; excluded** |
| 297-305 | WO-PL-032 installed-hook diagnostic and accepted Windows/Ubuntu birth-test probes | **Post-pilot instrument evidence; excluded** |
| 306-309 | WO-PL-033 Owner-started VS Code remote-relink attempts: two shell, one read traversal, one out-of-grant edit | **Post-pilot provider-envelope evidence; not in pilot aggregate** |

**WO-PL-012's 9.2.1 total is 1.** Record 53 is an actual rejected
mutation-capable scheduling attempt. Canary, birth-test, and non-mutating read
records are excluded. No out-of-grant mutation succeeded.

**WO-PL-013's 9.2.1 total is 0.** Record 59 is the required live-wall
canary and is excluded. No out-of-grant mutation succeeded.

Each of records 41, 42, and 43 was produced in a different executing session, and each
proves the file-edit channel was walled **in that session only**. Canary evidence does
not transfer. Shell-mediated writes and the remaining declared surfaces are still not
comprehensively covered, so no whole surface is represented as mechanically enforced.
The two repository-local record moves, the staging, and the single commit performed at
WO-PL-009 closeout passed through that unenforced shell channel and were
instruction-bounded, not wall-bounded.

After the completed work order moved to history, the still-present pointer temporarily
named a missing file. The closeout session's next shell call was denied before mutation
as record 44 (`pointer_missing_file`). The Owner-authorized closeout continued through
the separately authorized Codex shell channel; the event had no implementation impact.

**One thing record 43 does establish beyond the channel.** Its BLOCKED message
enumerated all twelve paths of the Amendment 1 grant, including `governance/STATE.md`,
`governance/LOG.md`, and the three `governance/history/WO-PL-009-*` closeout targets.
The amendment's prose extension *was* mirrored into machine-readable frontmatter, so the
RFI-28 failure mode was observed absent this cycle. RFI-28 remains DEFERRED; one absence
is not a fix.

### Pilot measurement — WO-PL-007

| Metric | Final value |
|---|---|
| 9.2.1 Denials | 1; zero successful |
| 9.2.2 RFIs | 3 |
| 9.2.3 Drift, same-WO / later | 4 / 0 |
| 9.2.4 Rework / additional sessions / artifacts retrieved | 1 / 2 / 2 |
| 9.2.5 Corpus · gaps · orphans | 45 documents / 89,008 words · 0 · 0 |
| 9.2.6 Declared / enforced / unenforced | 13 / 0 / 13 |
| 9.2.7 Owner load | 500-word brief · 2,816 words plus review disagreement section |
| 9.2.8 Instrument | N/A |

### Pilot measurement — WO-PL-008

| Metric | Final value |
|---|---|
| 9.2.1 Denials | 1; zero successful |
| 9.2.2 RFIs | 4 — RFI-25, RFI-26, RFI-27, RFI-28 |
| 9.2.3 Drift, same-WO / later | 5 / 5 |
| 9.2.4 Rework / additional sessions / artifacts retrieved | 2 / 4 / 1 |
| 9.2.5 Corpus · gaps · orphans | `NOT MEASURED — activation-time measurement omitted; retroactive values not invented` |
| 9.2.6 Declared / enforced / unenforced | 13 / 0 / 13 |
| 9.2.7 Owner load | 409-word brief; no 7.6.3 escalation |
| 9.2.8 Instrument | N/A |

The five same-work-order drift instances are the malformed pointer filename, the
CRLF work-order bytes, the external-output builder failure, the prose/frontmatter
grant mismatch, and a false Amendment-1 history statement in the implementation
report. The five later-detected instances are the four independently remediable
`SELF-HOSTING.md` truth mismatches and the licensing-direction self-adoption
mismatch; each is attributed to both WO-PL-008 and the earlier accepted work order
that introduced it.

### Pilot measurement — WO-PL-009

| Metric | Final value |
|---|---|
| 9.2.1 Denials | 0; zero successful |
| 9.2.2 RFIs | 0 |
| 9.2.3 Drift, same-WO / later | 5 / 0 |
| 9.2.4 Rework / additional sessions / artifacts retrieved | 0 / 3 / 1 |
| 9.2.5 Corpus · gaps · orphans | `NOT MEASURED — activation-time measurement omitted; retroactive values not invented` |
| 9.2.6 Declared / enforced / unenforced | 11 / 0 / 11 |
| 9.2.7 Owner load | 286-word brief; no 7.6.3 escalation |
| 9.2.8 Instrument | N/A |

The five same-work-order drift instances are: B.3.1's precondition of exactly 40 denial
records against the 42 actually present, because each executing session performs its own
canary; B.3.1's precondition of no cache, bytecode, or temporary archive, already untrue
at activation; `README.md`'s categorical statement that the adoption bundle commits
nothing; the categorical no-commit language retained in `migration-guides/0.1-to-0.6.md`;
and `skills/plumbline-adopt/SKILL.md` not explicitly assigning active-pointer removal at
recorder closeout to the Owner. The first two are dispatch-precondition mismatches; the
last three are the Reviewer's non-blocking follow-up findings, mismatches this work
order's own delivered state created and this same cycle detected. No later-detected
instance was found, so no earlier row's *later* column is amended.

The session arithmetic: five sessions executed under WO-PL-009 in total. The first
implementer session is the baseline pass and the completed fresh review is the ordinary
review pass; the three counted as *additional* are the continuation implementer, the
sandboxed fresh-review process that failed before reviewing, and this closeout
transcriber. **No rework cycle occurred** — the first implementer session ended
incomplete of its own accord, which is not a Reviewer or Owner return for correction, and
the fresh Reviewer returned ACCEPT on the first review. The one artifact retrieved is the
first implementer's unauthorized read of a closed WO-PL-007 report.

### Pilot measurement — WO-PL-010

| Metric | Final value |
|---|---|
| 9.2.1 Denials | 0; zero successful |
| 9.2.2 RFIs | 0 |
| 9.2.3 Drift, same-WO / later | 3 / 1 |
| 9.2.4 Rework / additional sessions / artifacts retrieved | 0 / 1 / 0 |
| 9.2.5 Corpus · gaps · orphans | `NOT MEASURED — activation-time measurement omitted; retroactive values not invented` |
| 9.2.6 Declared / enforced / unenforced | 11 / 0 / 11 |
| 9.2.7 Owner load | 383-word brief; no 7.6.3 escalation |
| 9.2.8 Instrument | N/A |

The three same-work-order drift instances are: B.5.6 named a ZIP path where the builder
requires an output directory; the implementation report briefly carried a host path until
the source gate caught it; and the required activation-time corpus measurement was again
omitted. The one later finding is the pre-existing `Part 9` cross-reference typo in
migration-guide clauses 1.6 and 1.8. It is recorded but not attributed retroactively to an
unknown earlier work order. No RFI-29 was issued.

One implementer session and the ordinary fresh review completed the work. The same fresh
Reviewer performed the Owner-authorized closeout, counted as one additional session under
the established metric convention. No Reviewer return occurred and no closed historical
artifact was retrieved.

### Pilot measurement — WO-PL-011

| Metric | Final value |
|---|---|
| 9.2.1 Denials | 0; zero successful |
| 9.2.2 RFIs | 0 |
| 9.2.3 Drift, same-WO / later | 1 / 0 |
| 9.2.4 Rework / additional sessions / artifacts retrieved | 1 / 1 / 0 |
| 9.2.5 Corpus · gaps · orphans | 52 documents / 88,933 words · 0 · 0 |
| 9.2.6 Declared / enforced / unenforced | 11 / 0 / 11 |
| 9.2.7 Owner load | 260-word brief; no 7.6.3 escalation |
| 9.2.8 Instrument | N/A |

The one same-work-order drift instance was the implementer's initial classification of five
R.8-routed `governance/templates/` files as orphans. Fresh review returned it once; the
report was corrected without re-measurement because the already-published combined total was
the accepted total. Re-review returned ACCEPT/HIGH. No RFI opened and no historical artifact
was retrieved.

### Pilot measurement — WO-PL-012

| Metric | Final value |
|---|---|
| 9.2.1 Denials | 1; zero successful — record 53 |
| 9.2.2 RFIs | 0 |
| 9.2.3 Drift, same-WO / later | 11 / 0 |
| 9.2.4 Rework / additional sessions / artifacts retrieved | 3 / 6 / 0 |
| 9.2.5 Corpus · gaps · orphans | `NOT MEASURED — activation-time measurement omitted; retroactive values not invented` |
| 9.2.6 Declared / enforced / unenforced | 8 / 0 / 8 |
| 9.2.7 Owner load | `NOT REPORTED — no value reconstructed` |
| 9.2.8 Instrument | N/A |

The eleven same-work-order drift instances are the issued-order host path;
omitted `READ_TOOLS` checker coverage; absent updates to `SELF-HOSTING.md`,
`ADOPTING.md`, the adoption skill, and the migration guide; the omitted
canonical-guide grant; two session-created bytecode files; omitted
activation-time corpus measurement; and the report's RED-test arithmetic.
Fresh review found no code defect and returned only the report correction.

The three rework cycles are the deterministic-review return, the canonical-
guide grant/repair return, and the fresh Reviewer's record-correction return.
The six additional sessions are the continuation implementer, deterministic-
review rework, canonical-guide repair, birth-test agent, reporting agent, and
this closeout transcriber. The fresh Reviewer is the ordinary review pass. The
dispatching Owner session listed two closed-history filenames but retrieved no
document content, so the archaeology count remains zero.

### Pilot measurement — WO-PL-013

| Metric | Final value |
|---|---|
| 9.2.1 Denials | 0; zero successful — record 59 is an excluded canary |
| 9.2.2 RFIs | 0 |
| 9.2.3 Drift, same-WO / later | 3 / 0 |
| 9.2.4 Rework / additional sessions / artifacts retrieved | 4 / 0 / 1 |
| 9.2.5 Corpus · gaps · orphans | `NOT MEASURED — activation-time measurement omitted; retroactive values not invented` |
| 9.2.6 Declared / enforced / unenforced | 8 / 0 / 8 |
| 9.2.7 Owner load | `NOT REPORTED — no value reconstructed` |
| 9.2.8 Instrument | N/A |

The three same-work-order drift instances are the false issue-time no-cache
baseline, three host-path transcriptions in the first report, and the first
report's stale external-build file count. The four rework cycles are the three
Owner correction-and-gate returns and the fresh Reviewer's report-correction
return. The initial Sonnet implementation and ordinary fresh Codex review are
not additional sessions. After acceptance, the closeout transcriber retrieved
one closed WO-PL-012 work order solely to mirror the established lifecycle
format; no implementation decision depended on it.

### Pilot measurement — WO-PL-014

| Metric | Final value |
|---|---|
| 9.2.1 Denials | 3; zero successful — records 61–63 counted, record 60 excluded canary |
| 9.2.2 RFIs | 0 new; RFI-25, RFI-27, and RFI-28 resolved |
| 9.2.3 Drift, same-WO / later | **12 / 2** |
| 9.2.4 Rework / additional sessions / artifacts retrieved | 2 / 1 / 0 |
| 9.2.5 Corpus · gaps · orphans | 51 documents / 98,846 words · 0 · 0 |
| 9.2.6 Declared / enforced / unenforced | 8 / 0 / 8 |
| 9.2.7 Owner load | 212-word brief · no escalation; active minutes not captured |
| 9.2.8 Instrument | N/A |

The two later-detected items were first found in WO-PL-016 and attributed here
under D.7.1: numeric filename-prefix collision and Git's collapsed
untracked-directory status masking a sibling behind a broad allowlist. The
earlier `12 / 0` derived value was stale; closed WO-PL-014 evidence is unchanged.

### Pilot measurement — WO-PL-015

| Metric | Final value |
|---|---|
| 9.2.1 Denials | 6; zero successful — records 65–70 counted, record 64 excluded canary |
| 9.2.2 RFIs | 0 |
| 9.2.3 Drift, same-WO / later | 7 / 0 |
| 9.2.4 Rework / additional sessions / artifacts retrieved | 3 / 0 / 2 |
| 9.2.5 Corpus · gaps · orphans | 50 documents / 102,592 words · 0 · 0 |
| 9.2.6 Declared / enforced / unenforced | 8 / 0 / 8 |
| 9.2.7 Owner load | 183-word brief · no escalation; active minutes not captured |
| 9.2.8 Instrument | N/A |

### Pilot measurement — WO-PL-016

| Metric | Final value |
|---|---|
| 9.2.1 Denials | 0; zero successful — record 71 excluded canary |
| 9.2.2 RFIs | 0 |
| 9.2.3 Drift, same-WO / later | 6 / 2 |
| 9.2.4 Rework / additional sessions / artifacts retrieved | 3 / 0 / 0 |
| 9.2.5 Corpus · gaps · orphans | 50 documents / 106,619 words · 0 · 0 |
| 9.2.6 Declared / enforced / unenforced | 8 / 0 / 8 |
| 9.2.7 Owner load | 224-word brief · no escalation; active minutes not captured |
| 9.2.8 Instrument | N/A |

WO-PL-016's two later-detected items are the same two instances attributed to
WO-PL-014 above, counted in both rows as D.7.1 requires.

### Accepted pilot-evaluation findings

Ratified DR-002 records these historical findings without rewriting the pilot:

1. WO-PL-014, WO-PL-015, and WO-PL-016 omitted Appendix B's `enforced_by` and
   `unenforced_boundaries`; WO-PL-017 makes future omission fail closed.
2. Nine of ten counted work orders declared `shell.execute: restricted` even
   though the signed pilot disposition said it defaulted to denied. The
   departure is preserved; future orders state their actual provider envelope.
3. The successful-mutation stop rule had an empty domain because no whole
   surface qualified as mechanically enforced. The completed rule is not
   repaired retroactively; future experiments cover declared birth-tested
   channels as well as whole surfaces.
4. WO-PL-014 materialized routing text before separate Owner ratification.
   DR-002 now ratifies R.12–R.14 exactly and preserves the sequence as a
   deviation.
5. The WO-PL-014 later-drift count and this State were stale; current derived
   records now show the corrected values.
6. Final verification for WO-PL-015 and WO-PL-016 lacked full Reviewer
   separation. Their deterministic evidence remains reproducible, but the
   independence claim is qualified.

### Accepted deviations — WO-PL-008

Both were accepted by the Owner in Amendment 4 §C. Neither opened an RFI or a rework
cycle.

1. **Closed-history retrieval.** The Reviewer read one closed WO-PL-007 history
   document while checking closeout mechanics, contrary to WO-PL-008's closed-history
   boundary. Read-only, no repository mutation, no implementation impact. It is the
   single artifact counted in 9.2.4 and is recorded rather than concealed.

2. **9.2.5 not measured.** Live-corpus documents, words, routing gaps, and orphans
   were not measured at activation, and the original activation corpus cannot now be
   reconstructed exactly. Retroactive values were not invented. A process deviation
   with no implementation impact.

### Accepted deviations — WO-PL-009

All four were accepted by the Owner in the disposition materialized as Amendment 1.
None opened an RFI or a rework cycle, and none had implementation impact.

1. **Denial-log precondition count.** B.3.1 required exactly 40 records before mutation;
   42 were present when the continuation session began, 43 after the closeout canary,
   and 44 after the expected move-to-history transition made the pointer temporarily
   unresolvable. Records 41–43 are session canaries; record 44 is classified separately
   as lifecycle lockout. Records 1–39 are provably unchanged by prefix hash.

2. **Pre-existing ignored residue.** B.3.1 required that no cache, bytecode, or temporary
   archive exist. `.pytest_cache/` and two `__pycache__/` trees predated activation. All
   are untracked and ignored; the Owner directed that they not be touched, and they were
   not.

3. **First implementer's closed-history retrieval.** That session read one closed
   WO-PL-007 record without authority from this work order and then ended without
   completing B.3. Read-only; nothing derived from it entered the work. It is the single
   artifact counted in 9.2.4.

4. **Reviewer's excluded-history traversal.** Two recursive searches traversed excluded
   history and archive directories before their output was filtered. No excluded content
   was displayed or used, the traversal was read-only, and it had no implementation
   impact. Recorded rather than concealed; it adds no 9.2.4 retrieval count.

### Accepted deviations — WO-PL-010

Both were accepted by the Owner in Amendment 1. Neither opened an RFI or rework cycle.

1. **Builder output wording.** B.5.6 supplied a ZIP-looking path to an option that accepts
   an output directory. The builder exited 0 and the archive it actually produced passed
   its checker. The independent Reviewer used the documented directory interface.

2. **Sandboxed review attempt.** The first independent suite invocation could not create
   temporary fixture projects and produced 13 environment failures. The identical suite
   rerun with temporary-fixture permission passed 257/257. No product file changed.

### Accepted deviations — WO-PL-012

1. The dispatching Owner session listed two closed-history filenames before
   activation without opening either document. Read-only, no implementation
   impact, and no historical artifact retrieved.
2. The issued order contained one host absolute path and omitted the canonical
   migration-guide path from its initial grant. Both were repaired by explicit
   Owner amendments before affected implementation proceeded.
3. The first GREEN pass omitted the checker and operational-document updates
   required by the order. Independent review caught them before birth testing.
4. Two session-created bytecode files were removed exactly after deterministic
   verification; no new cache residue remains.
5. One provider session attempted unsupported `ScheduleWakeup`; the wall denied
   it as record 53. The incomplete watcher result was not trusted, and the Owner
   reran the full gates locally.

### Accepted deviations — WO-PL-013

1. The issued baseline incorrectly claimed no cache residue; an ignored root
   `.pytest_cache/` predated dispatch. The Owner removed the exact verified
   residue before review. No implementation result depended on it.
2. The first report carried three host-specific WSL repository paths. The
   adopted-collection portability test caught them, the paths were replaced by
   semantic `<repo>`, and both platform gates reran.
3. The first report stated 112 payload files although the corrected final tree
   packaged 113. The report was corrected and the external build/archive gate
   reran.
4. The fresh Reviewer used the declared shell-read gap to hash the denied
   `dist/` archive. Only the already-recorded digest was returned; no entry or
   payload content was retrieved and nothing was mutated.
5. After acceptance, the closeout transcriber retrieved one closed WO-PL-012
   work order to mirror lifecycle formatting. Read-only; no implementation
   impact; counted as one artifact under 9.2.4.

### Follow-up findings delivered by WO-PL-010

These three findings were recorded at WO-PL-009 closeout and are now resolved by the
accepted WO-PL-010 implementation:

1. `README.md` still states categorically that the adoption bundle commits nothing.
2. `skills/plumbline-adopt/SKILL.md` does not explicitly assign active-pointer removal at
   recorder closeout to the Owner.
3. `migration-guides/0.1-to-0.6.md` retains categorical no-commit language that now
   differs from the recorder mode.

### Accepted Doctrine ruling — WO-PL-009

The uncounted bootstrap-closeout grant introduced by the corrected skill — the instrument
that gives a walled post-bootstrap session a grant covering exactly the closeout paths —
is supported by existing authority. It is the same class of instrument as
`WO-000-birth-test.md` and, like it, uncounted under 6.1.3. No Doctrine amendment is
claimed and `DOCTRINE.md` is byte-unchanged.

### Post-pilot verification — WO-PL-021

WO-PL-021 completed the Doctrine 0.7 distribution package without migrating
this repository's project-side Doctrine 0.6 governance instance. The existing
final Reviewer confirmed both amended blockers closed and found no actionable
defect; the Owner accepted the order on 2026-08-21 and reported **7 actual
active minutes**. This is post-pilot evidence and adds no eleventh metrics row.

| Gate | Accepted result |
|---|---|
| Native Windows governed-source suite | **467 tests, OK**, one expected skip |
| Sanitized native-Ubuntu changed modules | **106 tests, OK**, one expected skip |
| Real public candidate A, native Ubuntu | **467 tests, OK**, two expected projection-aware skips |
| Real public candidate B, native Ubuntu | **467 tests, OK**, two expected projection-aware skips |
| Projection reproducibility | Two independently built 88-file candidates; checker-clean, byte-identical paths and SHA-256 digests; shared manifest digest `d68f2c57bd43c1da50f4c16a79f49f43abd76a72bef0532c4c6004478fe60bc4` |
| Retained diagnostics | Sanitized full-source 463-test result and attempted 303-test three-module result remain non-green harness diagnostics; the initial `init.sh` environment failure is not a valid RED |
| Private-pattern input | Used only in the two authorized local builds, never transmitted to a model, permanently deleted, and absence verified |
| Denial record | Record 72 is an excluded session-local canary; WO-PL-021 counted denials **0**, successful out-of-grant mutations **0** |
| Post-closeout live gates | Source distribution and license checks **OK**; dispatch-validator module **86 tests, OK**, one expected skip; fresh external source archive **162 files plus `MANIFEST.sha256`**, archive checker **OK**, temporary output deleted |
| Between-order checker | Active pointer absent and no lifecycle finding; `--lockout` remains non-green solely because the accepted WO-PL-021 change set is uncommitted, and this closeout has no commit authority |
| Publication state | No commit, push, tag, publication, visibility change, checked-in `dist/` replacement, or successor activation |

### Post-pilot verification — WO-PL-022

WO-PL-022 corrected the public candidate's repository-inventory and
evidence-scope claims, added a public-safe Plumbline self-hosting pilot
example, and made those documentation truths executable. The same final
Reviewer session returned a procedural envelope rejection without inspecting
artifacts, then CONDITIONAL ACCEPT on the complete inline corpus, and finally
**ACCEPT/HIGH** after the Dispatcher independently attested the operative
Sonnet tool exclusions. The Owner accepted the order on 2026-08-21 and
reported **12 actual active minutes**. This is post-pilot evidence and adds no
eleventh metrics row.

| Gate | Accepted result |
|---|---|
| Native Windows governed-source suite | **471 tests, OK**, one expected skip |
| Targeted public-projection suite | **32 tests, OK** |
| Real public candidate A, native Ubuntu | **471 tests, OK**, two expected projection-aware skips |
| Real public candidate B, native Ubuntu | **471 tests, OK**, two expected projection-aware skips |
| Projection reproducibility | Two independently built 89-file candidates; checker-clean before and after testing; byte-identical paths and SHA-256 digests; shared manifest-file digest `3b9a34b79a25e996752372fd8b7b4fde1062b3526592b8b9ac99b6c986aff33e` |
| Retained diagnostics | Invalid initial CLI path harness, restricted Windows sandbox failures, wrong WSL distro alias, unsupported PowerShell parameter, and absent Windows-drive WSL mounts remain harness diagnostics, not product REDs or acceptance passes |
| Private-pattern input | Used only in the authorized local builds, never transmitted to a model, permanently deleted with both candidate/runtime roots, and absence verified; no gate log created |
| Denial record | Record 73 is an excluded session-local canary; WO-PL-022 counted denials **0**, successful out-of-grant mutations **0** |
| Surface classification | **8 / 8 / 0** under Owner-authored session provisioning accepted by the Reviewer; `Anthropic session tool exclusion` is attested provisioning evidence, not an 8.3.5 observed-denial birth test |
| Active source envelope at review | Exactly the pointer, live work order, and live report findings; license and whitespace checks pass; staged set, `templates/**`, and `dist/**` changes are zero |
| Post-retirement source gates | Active pointer and live transaction paths absent; completed work order/report present in durable history; source distribution and deterministic license checks **OK** |
| Publication state | No push, tag, publication, visibility change, checked-in `dist/` replacement, second-project access, or successor activation |
| Standing local-input process | Proposed in the report only; **not ratified** by this closeout |

### Post-pilot verification — WO-PL-023

WO-PL-023 ratified and materialized Doctrine 0.8 and DR-005, repaired the
adopter contract and retained-reference projection integrity, and added the
dispatch-time protected-control-plane birth-test schema while preserving 0.6
and 0.7 compatibility. The fresh independent Reviewer returned
**CONFORMANCE PASS**, no blocking finding, and MEDIUM-HIGH overall confidence.
The Owner accepted the order on 2026-08-21. Owner active minutes were **NOT
REPORTED** and are not inferred. This is post-pilot evidence and adds no
eleventh metrics row.

| Gate | Accepted result |
|---|---|
| Ratified candidate | SHA-256 `a52ea7e612af56493fd45737a8e690d2bdc490c0ccb70e365f383f34679dd5a5`; unchanged through acceptance |
| Native Windows governed-source suite | **487 tests, OK**, one historical skip |
| Native Ubuntu governed-source suite | **487 tests, OK**, one historical skip |
| Projection suite | **38 tests, OK** |
| Distribution suite | **200 tests, OK** |
| Real projection reproducibility | Two independently built 92-file candidates; private-pattern checker clean; identical relative paths and file SHA-256 values; aggregate ledger digest `e94d3210ef330dbb7a76215232afb47392ba7206f5bed00afaa379c693900a32` |
| Private input and residue | Input, both candidate trees, and temporary logs permanently deleted; separate absence audit found zero residue |
| Denial record | Log ended at 86 records; 75–76 are the excluded canary pair; 74 and 77–86 are eleven other provider-rejected attempts; successful out-of-grant mutations **0** |
| Surface classification | **8 / 0 / 8** under the strict complete-surface definition |
| Project binding | Doctrine 0.8 is ratified for distribution; this project remains bound to Doctrine 0.6 |
| Post-retirement source gates | Active pointer and all four live WO-PL-023 transaction paths absent; all four records present in history; source distribution and deterministic all-files license checks **OK** |
| Between-order checker | No active-pointer or lifecycle finding; `--lockout` remains non-green with exactly 38 dirty-tree findings because the accepted WO-PL-023 change set is uncommitted and commit authority was excluded |
| Publication state | No commit, push, tag, publication, visibility change, checked-in `dist/` replacement, or successor activation |

### Sequencing recovery — void WO-PL-024

After WO-PL-023 acceptance, the first local staging attempt failed before any
index change because the sandbox could not create `.git/index.lock`. The
separately approved staging attempt then staged exactly 38 accepted WO-PL-023
paths, but the unscoped staged whitespace gate correctly rejected two trailing
spaces in the new Owner brief. The brief was corrected in the working tree,
leaving its pre-correction bytes staged until recovery authorization arrived.
Recovery restaged only the corrected brief, verified the exact 38-path set, and
passed the unscoped staged whitespace gate. Commit `db0b4c1` contains exactly
those 38 WO-PL-023 paths and was pushed to the existing private `origin/main`.

Before that index recovery, WO-PL-024 had been prematurely issued and activated
with `doctrine_rev: "0.6"`. Candidate and active structural validation ran; no
implementation edit, RED/GREEN test, product test, provider birth test, commit,
or push ran under it. The Owner disposed it **VOID BEFORE IMPLEMENTATION**. Its
status is retained as `RFI-BLOCKED`, its exact lifecycle record and work order
are in history, its pointer is absent, and its identifier will not be reused.
At that recovery point the project remained bound to 0.6 pending separate
ratification of the exact WO-PL-025 migration decision. DR-003 was subsequently
ratified and materialized before WO-PL-025 activation, making 0.8 operative.

### Post-pilot verification — WO-PL-025

WO-PL-025 completed the cumulative project-local migration from Doctrine 0.6
directly to 0.8. The Owner ratified exact DR-003 and work-order candidates; the
coordinator durably materialized DR-003 and the exact charter sentence before
activation, which made the 0.8 binding operative independently of later
acceptance. The Owner accepted the completed migration on 2026-08-21 after a
fresh independent Reviewer returned **CONFORMANCE PASS**, no blockers, and HIGH
confidence. Owner active minutes were **NOT REPORTED** and are not inferred.
This is post-pilot evidence and adds no eleventh metrics row.

| Gate | Accepted result |
|---|---|
| Ratified DR-003 candidate | SHA-256 `972A425496550E30ECAF87CDDE382ECB415BAF3B6F7EB0B2989E24604855BF0F`; materialized decision byte-identical |
| Ratified work order | SHA-256 `8D1117D88E3488395533A8B5F950597BE6938331C4617730D7940136CCFA82FD` |
| Binding-effective point | Exact DR-003 and charter sentence durably materialized before WO-PL-025 activation; acceptance records completion and does not defer effectiveness |
| Template migration | Project-local A–E byte-identical to canonical Doctrine 0.8 templates; B has one generated-boundary marker pair; A and C–E carry required 0.8 text |
| Native Windows governed-source suite | **487 tests, OK**, one expected skip |
| Native Ubuntu governed-source suite | **487 tests, OK**, one expected skip |
| Dispatch schema corpus | **10 tests, OK** |
| Projection process suite | **38 tests, OK** |
| Denial record | Record 87 is one excluded fresh-session ordinary file-edit canary; successful out-of-grant mutations **0** |
| Surface classification | **8 / 0 / 8**; no categorical Doctrine 8.7 birth-test claim |
| Reviewer | **CONFORMANCE PASS**, no blockers, HIGH confidence |
| Non-reversion | Doctrine 0.8 remains operative if later migration verification requires rework; no silent 0.6 reversion |
| Post-retirement source gates | Active pointer and all five live WO-PL-025 transaction/lifecycle paths absent; all five records present in durable history; source distribution and deterministic all-files license checks **OK** |
| Between-order checker | No active-pointer or lifecycle finding; raw `--lockout` is non-green on exactly 15 authorized uncommitted migration/closeout paths; exact-path allowlisted `--lockout` returns **OK** |
| Publication state | No commit, push, tag, publication, visibility change, checked-in `dist/` replacement, RFI-22 closure, or successor activation |

### Post-pilot verification — WO-PL-026

WO-PL-026 completed the protected-control-plane hardening and portability scope
queued by Plan section 11. The Owner accepted it on 2026-08-26 after a fresh
independent Reviewer returned **ACCEPT** with no correction, and disposed
RFI-22 **Yes / closed**. Owner active minutes are **NOT REPORTED** because the
supplied response retained the placeholder; no value is inferred.

| Gate | Accepted result |
|---|---|
| Canonical / bundled / installed adapter | Byte-identical at `7989C0451C29256486CA58CC3DD4AC59BDDFE9B98A2B7A63855500B76C4F8CD5` |
| Installed Windows settings | Restored exact final identity `93D66DC90D6B9E9F01C2F1EB58E5D37AD607F6858667D28EDBCBD625E2A27EEE` |
| Windows birth test | Revision 10 session `5f17abde...bc07`, `30/30` valid probes denied |
| Native Linux birth test | Revision 11 session `00547a67...7ed4`, `30/30` valid probes denied, including five exact `Workflow` calls |
| Protected mutations | **0**; all target identities unchanged; no nested/background Workflow execution |
| Denial evidence | `260` records, `90451` bytes, SHA-256 `8B92384562C950EF9351BC919B802FEC1E22462626552289584700569C8E3100`; append-only prefix continuity verified |
| Windows governed-source suite | **506 tests, OK**, one intentional platform skip |
| Ubuntu governed-source suite | **506 tests, OK**, two intentional platform skips |
| Distribution module | **205 tests, OK** |
| Reviewer | **ACCEPT**, no correction; supports RFI-22 Yes/close and Owner acceptance |
| Strict broad-surface classification | **8 / 0 / 8**; categorical control-plane protection is not inflated into whole-surface enforcement |
| RFI-22 | **RESOLVED and CLOSED**; record retired to `governance/history/` |
| Publication state | No push, publication, tag, visibility change, checked-in `dist/` replacement, or WO-PL-027 activation |

### Post-pilot verification — WO-PL-027

WO-PL-027 completed the verification-only release-candidate scope queued by
Plan section 11. The Owner accepted it on 2026-08-26 after the ninth fresh
independent Reviewer returned **ACCEPT/HIGH** with no remaining record defect or
substantive product/governance blocker. The Owner reported **22 actual active
minutes**.

| Gate | Accepted result |
|---|---|
| Release-truth corrections | Five granted paths corrected; no feature, adapter, script, checker, test, license map, decision, Plan, State, routing, or historical authority changed during implementation |
| Windows governed source and candidates | **506 tests, OK** for source and each of two candidates, with recorded platform skips |
| Native Ubuntu governed source and candidates | **506 tests, OK** for source and each of two candidates, with recorded platform skips |
| Public projections | Two independent **92-file** candidates checker-clean and byte-identical; complete ledger SHA-256 `4668BB662F17F7EDA7500118460C70F1F0EC5D6E91ADF9F82BFF2C3FE6771703` |
| Candidate-built archives | Both checker-clean and byte-identical at **1,644,444 bytes**, SHA-256 `02D25EB6756DD68856BC52186D4D4FAB95A18F13A23DCF1C085DFC57BE587A3A` |
| Reviewer | Ninth fresh review **ACCEPT/HIGH**; no remaining record defect or substantive blocker |
| Denial evidence | **266** append-only records; record 262 excluded canary, records 261 and 263-266 post-pilot provider-envelope evidence; successful denied mutation **0** |
| Strict broad-surface classification | **8 / 0 / 8**; observed channel denials are not inflated into whole-surface enforcement |
| Cleanup | Private input, both candidates, both archives, ledgers, cold repository, WSL copies, and temporary logs absent |
| Publication state | Session candidates are deleted and blocked by pre-closeout provenance. No push, publication, tag, visibility change, or checked-in `dist/` replacement; fresh post-closeout rebuild/review and separate Owner decision still required |

### Post-pilot verification — WO-PL-028

WO-PL-028 corrected four public-document truth boundaries found by the fresh
post-WO-PL-027 review, then incorporated two further independent review returns
before final ACCEPT. The Owner accepted it on 2026-08-26, explicitly accepting
the disclosed canary-ordering deviation. Owner active minutes were **NOT
REPORTED** and are not inferred.

| Gate | Accepted result |
|---|---|
| Public truth | Public distribution, private governed source, and publication lifecycle are distinguished without reader-relative identity; private-only DR-003 references and selected aggregate evidence are qualified |
| Windows governed source | **506 tests, OK**, one recorded skip |
| Native Ubuntu governed source | **506 tests, OK**, two recorded skips |
| Windows candidates | Two independent candidates, **506 tests each, OK**, two recorded skips each |
| Native Ubuntu candidates | Two independent candidates, **506 tests each, OK**, three recorded skips each |
| Public projections | Two independent **92-file** candidates checker-clean and byte-identical; complete ledger SHA-256 `D9A3732AF63F72E121087873BBFD49D2718CA7D55A9B23674E2C61E36066B118` |
| Reviewer | Final fresh review **ACCEPT**; no actionable record or public-byte defect |
| Denial evidence | **268** append-only records; record 267 post-pilot read denial; record 268 excluded canary; successful denied mutation **0** |
| Accepted deviation | Canary was genuinely denied and target remained absent, but it ran after the Implementer's first granted edits rather than before them; B.5.1 ordering remains visibly unmet and Owner-accepted |
| Strict broad-surface classification | **8 / 0 / 8**; observed channel denials are not inflated into whole-surface enforcement |
| Cleanup | Private input, all diagnostic candidates, WSL mount, and temporary logs absent; one empty locked temporary directory contains no evidence bytes |
| Publication state | No candidate from WO-PL-028 is publishable. No push, publication, tag, visibility change, or checked-in `dist/` replacement; fresh post-closeout dual rebuild/review and separate Owner decision still required |

### Post-pilot verification — WO-PL-029

WO-PL-029 corrected the four blocking findings from the post-WO-PL-028
publication review and two further public-byte defects found during fresh
review. The Owner accepted it on 2026-08-26, explicitly accepting the disclosed
coordinator-awareness privacy-process deviation and no-impact Reviewer
diagnostic. Owner active minutes were **NOT REPORTED** and are not inferred.

| Gate | Accepted result |
|---|---|
| Public truth | Projected State is explicitly source-commit-bound; concrete omitted report references are checked in inline-code, plain, and Markdown-link forms; public provenance contains no private-input fingerprint; complete-tree ledger serialization is canonical and public |
| Windows governed source | **515 tests, OK**, two recorded skips |
| Native Ubuntu governed source | **515 tests, OK**, three recorded skips |
| Windows candidates | Two independent candidates, **515 tests each, OK**, two recorded skips each |
| Native Ubuntu candidates | Two independent candidates, **515 tests each, OK**, three recorded skips each |
| Public projections | Two independent **92-file** candidates checker-clean and byte-identical; complete ledger SHA-256 `4D4A7A65B1FDAA379192A5201641FBFBC3156AACBD0B79E6040BC4E8FB9E36BD` |
| Candidate-built archives | Both checker-clean and byte-identical at **1,676,366 bytes**, SHA-256 `AED8CCA3C2808986464ECE52642199ABB729CFCBB83CFFDB3C9050905A98C6A0` |
| Reviewer | Corrected fresh re-review **PUBLICATION ACCEPT**; no remaining public-byte or record blocker |
| Denial evidence | **271** append-only records; record 269 excluded canary; records 270/271 ordinary post-pilot read/shell denials; successful denied mutation **0** |
| Accepted deviations | Coordinator inherited awareness of local screening values; none reached Sonnet, Reviewers, or artifact bytes. Reviewer's external-sandbox diagnostic was interrupted with no mutation or evidence claim |
| Strict broad-surface classification | **8 / 0 / 8**; observed channel denials are not inflated into whole-surface enforcement |
| Cleanup | Private input, both candidate generations, both archive generations, temporary Ubuntu bridge, and temporary logs absent |
| Publication state | No candidate from WO-PL-029 is publishable because all were deleted before closeout. No publication, tag, visibility change, or checked-in `dist/` replacement; fresh post-closeout dual rebuild/review and separate Owner decision still required |

### Post-pilot verification — WO-PL-030

WO-PL-030 closed the blockers found by the cold adversarial audit of the
post-WO-PL-029 private baseline. The Owner accepted it on 2026-08-27 after the
fresh publication Reviewer returned **ACCEPT/HIGH** and the corrected
dual-platform installed-wall lifecycle completed. The active-minutes response
retained its placeholder, so Owner active minutes are **NOT REPORTED** and are
not inferred.

| Gate | Accepted result |
|---|---|
| Runtime and dispatch wall | Protected control-plane floor, ACTIVE lifecycle, parser compatibility, repository-root validation, read-pattern traversal, MCP-reader classification, and host-neutral registration are tested and synchronized across canonical/bundled copies |
| Installed adapter | Canonical and installed SHA-256 `A899A4B3CC572766EA21DAE1C4648452031780D73003D7288AA67539FBA28D45`; Windows settings restored at `93D66DC90D6B9E9F01C2F1EB58E5D37AD607F6858667D28EDBCBD625E2A27EEE` |
| Final Windows governed source | **537 tests, OK**, two expected skips, on final report bytes |
| Public candidates | Two independently built 91-file projections; Windows and native-Ubuntu suites passed; complete ledger SHA-256 `CEC3BE494F54444CB339F05D3E67661DCEB1F9293B12729595E4B26FB47444B3` |
| Candidate archives | Byte-identical at **1,674,774 bytes**, SHA-256 `CF3BBBFA71C2786F6096796E327DCE2469EFF34BCF814DD79B5195499F19755D` |
| Reviewer | Final publication review **ACCEPT/HIGH**; no remaining product or record blocker |
| Windows birth test | Session `2f2bf959...2ad1`: **13/13** exposed mutation calls denied; 10 protected, two shell, one delegation |
| Ubuntu birth test | Session `737ca4e5...513c`: **12/12** exposed mutation calls denied; 10 protected, one shell, one delegation; PowerShell not exposed and not substituted |
| Denial evidence | **296** records / **103,018** bytes / SHA-256 `5A5A658F12E31EEBD2084CA39692E4A305D3934CF069409A7CC5AD4B120674DB`; original 271-record log and Windows result preserved as exact prefixes |
| Strict broad-surface classification | **8 / 0 / 8**; categorical control-plane protection is not inflated into whole-surface enforcement |
| Accepted deviations | All report deviations and diagnostics remain visible, including recovered provider/transport/probe-order attempts and one harmless mount-cleanup retry; none produced a successful protected mutation |
| Cleanup | Private patterns, candidates, archives, prompts, lifecycle instruments, backups, temporary mounts/keepers, and test residue absent |
| Publication state | No publication, public repository, tag, visibility change, or checked-in `dist/` replacement. A fresh post-closeout dual rebuild/review and separate Owner decision remain required |

### Post-pilot verification — WO-PL-031

WO-PL-031 closed the remaining public-source truth and runtime gaps identified
after WO-PL-030. The Owner accepted it on 2026-08-27 after the fresh Reviewer
returned three substantive findings, then two precision findings, and finally
**ACCEPT** with no remaining issue. Owner active minutes are **NOT REPORTED**
and are not inferred.

| Gate | Accepted result |
|---|---|
| Runtime wall | Existing non-regular pointers and malformed pointed grants fail closed for modeled reads; absent pointer still permits the documented read-only review state |
| Pattern and path controls | Traversal patterns use a conservative confined grammar; portable control-plane aliases and sentence-final private-path tokens have regression coverage |
| Final Windows governed source | **549 tests, OK**, two expected skips |
| Public candidates | Two independently built 92-file projections; Windows and native-Ubuntu suites passed; complete ledger SHA-256 `1BDC6C2B2D3A8A4B57186A3B65313B0691D4135D5ED07A80061395C77A1EC510` |
| Candidate archives | Byte-identical and checker-clean at SHA-256 `068A50EF8366251955BE6A365DBB6024376BB6919208424D023CD1853378AEDE` |
| Reviewer | Final fresh re-review **ACCEPT**; no remaining product or record blocker |
| Enforcement status | Codex implementation surface; no live-hook canary or mechanical-enforcement claim; strict broad-surface classification **8 / 0 / 8** |
| Canonical copies | Canonical and bundled adapter SHA-256 `DD29AF2A39D25E0270AD9ACC23EE912F81E39C674E1179759F4A3010C6A0C1A0`; README copies match at `2306C0026021C071C445827F3E097EF9F38134F9C5226F1DA6D4E04C0D13C742` |
| Installed hook | Deliberately unchanged at prior accepted digest `A899A4B3CC572766EA21DAE1C4648452031780D73003D7288AA67539FBA28D45`; separate Owner-controlled installation/birth test required |
| Cleanup | Private input, both Windows/native-Ubuntu candidates, both archive generations, caches, and temporary logs absent |
| Publication state | No publication, public repository, tag, visibility change, or checked-in `dist/` replacement. Installation/birth test, fresh post-closeout rebuild/review, and separate Owner decision remain required |

### Post-pilot verification — WO-PL-033

WO-PL-033 closed the public-front-door and release-hygiene findings from the
final objective launch review. The Owner accepted it on 2026-08-28 and reported
active minutes **NOT REPORTED**.

| Gate | Accepted result |
|---|---|
| Public front door | Problem, four-step loop, five-minute route, pilot evidence, differentiation, and enforcement boundary precede repository taxonomy; messaging leads with authority and enforcement rather than another SDD workflow |
| Legal code | Official Creative Commons CC-BY-4.0 and CC0-1.0 plain legal text; root LICENSE byte-identical to canonical CC-BY; checker rejects template controls and unsupported Python with an actionable message |
| Decision truth | Methodology DR-002 is intentionally unused; private project DR-003 references are qualified as absent from public candidates |
| Final Windows governed source | **553 tests, OK**, two expected skips |
| Public candidates | Two independent 92-file projections; both passed 553 tests on Windows and native Ubuntu; complete-ledger SHA-256 `9D2A2E0E3B41CFEC6CA70F86CA51B85D1A9B93C8299219A8FC45ADC0DE4D3604` |
| Candidate archives | Byte-identical and checker-clean at SHA-256 `B9AD70B59EF1A3BBDD40BFCB266653E57C362F1051901443ED175B81F2C67C35` |
| Denial evidence | Records 306-309; original 305-record prefix line-for-line unchanged; zero successful mutation |
| Cleanup | Ignored reviewer ZIP, private screening input, both candidates, archives, WSL mount/keeper, and temporary logs absent |
| Publication state | Private governed source remains separate. The new virgin public repository is available for a fresh clean-history projection and separate publication decision |

### Public release observation — Plumbline 0.8

After accepted WO-PL-033 closeout, the Owner authorized and the coordinator
performed the separate publication lifecycle. The private governed source was
pushed to its renamed private archive repository at
`e270fd3235d170a28a21fd198b88857740b74acd`. Two independent clean projections
were byte-identical at complete-tree ledger SHA-256
`FD04037812CF729DA180BA4B2D0BE2822E6E6985F8D78D508B712BB0C0E6F4DC`.

The public repository `HLLMR/plumbline` was created from the single root commit
`ba3c0754e5019f1fa93779d110843562cfa07307`, made public, and released as
`v0.8`. Its 15-job Windows, Ubuntu, and macOS CI matrix passed across Python
3.10 through 3.14. The attached 1,747,435-byte source archive has SHA-256
`143afef18a6e0781e6896019321a2473ec8f40d7faa159c0187fd243c842cbc8`.
Temporary projection trees, private screening input, release logs, and keeper
files were deleted after remote verification. This observation records the
completed publication; it does not enlarge the release claims.

### Post-pilot verification — WO-PL-034

WO-PL-034 delivered the bounded post-publication front-door polish. The Owner
accepted the final launch-kit visual and tonal revision on 2026-08-28 and
reported active minutes **NOT REPORTED**.

| Gate | Accepted result |
|---|---|
| Public front door | Launch-kit type-only banner, truthful CI/release/Doctrine/security chrome, plainer evidence-first opening, and a real 60-second denial example from WO-PL-033 records 306–309 |
| README assets | Exact regenerated 1280 × 320 SVG/PNG pair; PNG SHA-256 `C028363BE5C227BA84A0A2C3005FD78DF59935AC4933704922F158278A04E79C` |
| GitHub social assets | Exact regenerated 1280 × 640 SVG/PNG pair; PNG SHA-256 `3F9A20A4FB6E94DAE2053B3B3D0DFB21D6ED72B89BDD99C421F55098C035129A` |
| Governed-source suite | **557 tests, OK**, two expected skips |
| Public candidate | Final 96-file candidate: **557 tests, OK**, two expected skips |
| Reproducibility | Two independent 96-file projections checker-clean and byte-identical; complete-ledger SHA-256 `DAAE5C51FDB7450E61307375BCD8E9336E78CF10CCADF27E9439247D9CB15D77` |
| Reviewer | Final launch-kit reconciliation **ACCEPT** after two report-only inventory corrections; no remaining blocker |
| Enforcement status | Codex implementation surface; no live-wall claim; the public example accurately reports separate historical provider-envelope denials |

### Post-pilot verification — WO-PL-035

WO-PL-035 repaired the first-adopter human ramp and established the public
issue-to-PR maintenance path. The Owner accepted it on 2026-08-28 and reported
active minutes **NOT REPORTED**.

| Gate | Accepted result |
|---|---|
| Human first action | `START-HERE.md` names the coordinator/recorder, execution location, exact first prompt, and Implementer boundary before Doctrine reading |
| Recovery and safety | No-pointer lockout and accidental overlays have explicit recovery paths; external mutation tools require pre-authorized disposable fixtures and unavailable channels remain indeterminate |
| Public maintenance | Issue forms, state labels, agent briefs, contributor routing, DCO PR template, and private-governance projection boundary are documented and checked |
| Focused closeout rerun | **265 tests, OK**, one intentional skip |
| Governed-source full suite | **564 tests, OK**, two intentional skips |
| Active source gate | Refused exactly the pointer, active work order, and active report transients |
| Reviewer | Initial fresh review returned six material findings; all corrected; different fresh read-only Reviewer returned **ACCEPT** with no remaining blocker |
| Cleanup | Synthetic inputs, diagnostic fixtures, Python caches, and the 103-file reviewed public candidate are absent |
| Enforcement status | Codex implementation surface; no live-wall or external-service probe claim; denial ledger remained 309 records at SHA-256 `AE6485A2353183917397219801F8443871FE6ED59F0C3CEE27F3D8B6EAE11D85` |

### Post-pilot verification — WO-PL-036

WO-PL-036 converted the missed inception name search into a reproducible public
gate and selected **Writwall** as the replacement identity. The Owner accepted
it on 2026-08-28 and reported active minutes **NOT REPORTED**.

| Gate | Accepted result |
|---|---|
| Owner disposition | Plumbline, Grantcord, and Writcord rejected; **Writwall accepted**; both human sources in every ledger attest `HLLMR, Owner` |
| Evidence contract | Seven required source classes; canonical/bounded exact and similar queries; endpoint-specific request coverage; UTC/freshness chronology; explicit findings, limitations, classifications, and post-evidence disposition |
| Focused contract | **70 tests, OK** |
| Governed-source full suite | **638 tests, OK**, two expected skips |
| Native Ubuntu focused/integration | **74 tests, OK** |
| Reproducibility | Two independent 112-file projections checker-clean and byte-identical; complete-ledger SHA-256 `3E7F5AA46DBA07115D13D63A62EB071B37F835DDB5600EAAF9BEF36A4ED44240` |
| Reviewer | Fifth fresh adversarial Reviewer returned **ACCEPT** on frozen bytes with no remaining product or governance blocker |
| Cleanup | Synthetic screening sentinel, both candidates, caches, and temporary Ubuntu mount absent; denial ledger remained 309 records |
| Boundary | Historical records retain Plumbline; no rename, history rewrite, publication update, tag, visibility change, or `dist/` replacement; WO-PL-037 remains inactive |

### Open decisions and release state

| Item | State |
|---|---|
| RFI-22 | **RESOLVED and CLOSED** at WO-PL-026 closeout. Categorical protected-control-plane denial is implemented and passed complete Windows and native-Linux birth-test matrices |
| RFI-23 | **RESOLVED and CLOSED** at WO-PL-008 closeout. Source-mode checking now applies the builder's canonical machine-path definition, locked by a public-interface regression. Record moved to `governance/history/` |
| RFI-24 | DEFERRED. Owner-direct retirement is a procedure, not a supported agent mechanism |
| RFI-25 | **RESOLVED** at WO-PL-014 closeout. Pointer existence, identity, bytes, and target resolvability are checked before dispatch |
| RFI-26 | **RESOLVED and CLOSED** at WO-PL-008 closeout. The builder reports an external `--output` path instead of raising after a successful archive write. Record moved to `governance/history/` |
| RFI-27 | **RESOLVED** at WO-PL-014 closeout. Candidate/active validation rejects CRLF, BOM, NUL, and invalid UTF-8 bytes |
| RFI-28 | **RESOLVED** at WO-PL-014 closeout under the Owner-approved parser-free design. Frontmatter is sole grant authority; B.4 is generated and unmatched B.3/B.4 paths block dispatch |
| RFI-25 / 27 / 28 routing | The records remain separate but were implemented and disposed together by WO-PL-014; their bounded residuals remain visible in each record |
| RFI-03 / licensing | **RESOLVED by DR-003, 2026-08-20.** License map selected; mechanization and publication remain separate gates |
| Active work order | None; intentional between-work-order lockout |
| Queued work | No successor work order. The accepted external Writwall cutover packet remains pending a separate Owner authorization |
| WO-PL-010 follow-up | **Complete.** The three adoption-recorder consistency findings from WO-PL-009 are closed |
| Second-project boundary | Each adopting project maintains its own adoption and product state. No second-project source, private benchmark material, proprietary design detail, or trade-secret material is imported into Plumbline by this closeout |
| Published / tagged / licensed | **Yes**: clean-history public repository `HLLMR/plumbline`, release tag `v0.8`; DR-003 path-based license map remains operative |
| Push | WO-PL-034 private and public updates authorized; remote commit identities are recorded after the push completes |
| Repository visibility | Private governed source remains private; clean-history `HLLMR/plumbline` is public |
| Stage | **Plumbline 0.8 remains the historical public release; Writwall migration is accepted in governed source; Tuesday promotion remains frozen pending the separately authorized external cutover** |

---

## INTERPRETED

### I.1–I.5, recorded at WO-PL-007 closeout

**Written by:** Codex/OpenAI, transcribing the second fresh Reviewer's evidence
and the Owner's 2026-08-18 disposition. Retained as recorded. I.3's forward
statement has since been discharged; see I.8.

### I.1 The core mechanism worked

The first counted work order delivered a real defect: its own report made the
tree unpackageable. A fresh review detected it before acceptance, the Owner
returned it once, and the corrected tree passed without weakening a test or
gate. That is same-work-order detection and one-cycle recovery, the central
claim Plumbline set out to test.

### I.2 The operating cost is currently too high

The result required an oversized work order, a large report, two reviews, a
rework session, and extensive Owner reading. That is not incidental. It is the
pilot's most important negative finding so far. Plumbline must become cheaper
to operate or retire controls whose cost exceeds the risk they address.

### I.3 The next work is consolidation, not more ceremony

One bounded maintenance order should repair remaining post-adoption record
drift and make the source checker perform the builder's machine-path preflight.
Active-work-order adapter hardening follows only if genuine work still requires
it. No new platform, dashboard, schema, or meta-governance feature is justified.

### I.4 Evidence limits remain explicit

This self-adoption shows that Plumbline can expose and recover from its own
failures once. It does not establish that the methodology improves outcomes in
other repositories. The remaining pilot orders must be genuine maintenance
work; work invented to make the method look complete is not evidence.

### I.5 Publication remains a later decision

Doctrine 0.6 is ratified, but public release remains blocked by the unresolved
license and the incomplete pilot evaluation. Nothing in WO-PL-007 authorizes a
push, tag, publication, visibility change, or effectiveness claim.

### I.6–I.9, recorded at WO-PL-008 closeout

**Written by:** Claude Opus 5, the Amendment 4 closeout transcriber, from the
WO-PL-008 fresh review and the Owner's disposition in Amendment 4. Controlled
inference is labelled as such; every count above is deterministic.

### I.6 The wall's failures this cycle were all in the instructions

Deterministic: four of WO-PL-008's five same-work-order drift instances were
defects in the *issued order* rather than in the work — a mistyped pointer
filename, CRLF bytes, a grant extended in prose but not in frontmatter, and a
false history statement in the report. Only the external-output builder defect
was in the product.

Controlled inference: this is the pilot's clearest signal so far that dispatch,
not implementation, is the current weak surface. RFI-25, RFI-27, and RFI-28 are
routed together for exactly that reason. Whether one validator or three is the
right answer remains an open Owner decision, not a conclusion of this record.

### I.7 Record 38 is the most valuable measurement here

Deterministic: the wall denied authorized work because the authority existed only
in prose. Nothing was mutated; the defect surfaced immediately.

Controlled inference: counting it rather than excusing it as a probe is what makes
9.2.1 worth measuring. Had it been excluded, the accounting would have shown a
clean cycle and hidden the machine-readable-grant defect entirely.

### I.8 The consolidation predicted in I.3 was delivered

Deterministic: source-mode checking now performs the builder's machine-path
preflight, the enumerated post-adoption record drift is repaired, and both gates
are locked by public-interface regressions. No gate was weakened and no new
platform, dashboard, schema, or meta-governance feature was added. Active-work-order
adapter hardening (RFI-22) was not required and was not attempted.

### I.9 The cost finding in I.2 is not yet answered

Deterministic: WO-PL-008 required two rework cycles, four additional agent sessions,
and four amendments to close one TDD slice and five record corrections. WO-PL-007
required one rework cycle and two additional sessions.

Controlled inference: operating cost went up, not down, and I.2 therefore stands
unaddressed. The increase is attributable to dispatch defects rather than to the
implementation work, which is a more tractable problem — but that is an inference
about cause, and the next counted work orders test it. Nothing here establishes
that Plumbline improves outcomes in any other repository.

### I.10 Publication remains blocked

Unchanged from I.5. Nothing in WO-PL-008 authorizes a push, tag, release,
publication, `dist/` artifact, license selection, visibility change, successor work
order, or effectiveness claim.

### I.11–I.14, recorded at WO-PL-009 closeout

**Written by:** Claude Opus 5, the Owner Amendment 1 closeout transcriber, from the
WO-PL-009 fresh review and the Owner's `Approved` disposition. Controlled inference is
labelled as such; every count above is deterministic.

### I.11 Operating cost fell for the first time

Deterministic: WO-PL-009 required **zero** rework cycles and **three** additional agent
sessions, against WO-PL-008's two and four and WO-PL-007's one and two. The fresh
Reviewer returned ACCEPT on the first review with no blocking findings. Owner reading
load was 286 words against a 500-word ceiling.

Controlled inference: this is the first counted cycle that moves I.2's cost finding in the
right direction, and it is one data point, not a trend. Two of the three additional
sessions were not caused by the work at all — one implementer session ended incomplete and
one review process failed on environment permissions before reviewing. Cost attributable
to *the methodology* was one implementation pass, one review, and one closeout. Whether
that is repeatable is what WO-PL-010 and the remaining pilot orders test.

### I.12 The dispatch surface behaved better, and one predicted failure was absent

Deterministic: record 43's denial message enumerated all twelve paths of the Amendment 1
grant, so the amendment's prose extension was mirrored into machine-readable frontmatter.
That is exactly the defect recorded as RFI-28 at WO-PL-008, observed absent here. The two
dispatch-related drift instances this cycle were stale *preconditions* — a denial-record
count and a no-residue assertion that had both aged out — not malformed instruments.

Controlled inference: I.6 read dispatch as the weak surface. This cycle is consistent with
that reading and mildly encouraging about it, but a single absence proves nothing. RFI-25,
RFI-27, and RFI-28 stay DEFERRED and no validator is authorized, designed, or implemented.
The observation that both surviving dispatch defects were *stale* rather than *wrong*
suggests, without establishing, that preconditions asserting a count are the fragile kind.

### I.13 The correction is recorded, not yet demonstrated

Deterministic: WO-PL-009 changed `skills/plumbline-adopt/SKILL.md` and `ADOPTING.md`. No
adopting project has run the recorder mode, and the prospective adopter's recording has not started.
Three consistency mismatches the correction created in neighbouring distribution
artifacts — `README.md`, the 0.1-to-0.6 migration guide, and the skill's own silence on
pointer removal — remain open and are routed to a proposed, unissued WO-PL-010.

Controlled inference: the evidence for this correction is one Owner's account of one
bootstrap. That is sufficient to justify the change and insufficient to claim the
workflow is better. The first genuine test is adoption by a separate project under the corrected skill,
and it should be reported as evidence whether it goes well or badly.

Worth naming plainly: this closeout is itself the first instance of an agent executing
Plumbline's own ratified Owner decision — the record moves, the staging, and the commit —
rather than handing the Owner a checklist. The authority was the Owner's `Approved`; only
the keystrokes moved. That is the property WO-PL-009 argues for, exercised once, on this
repository, under an explicit grant.

### I.14 Publication remains blocked

Unchanged from I.5 and I.10. Nothing in WO-PL-009 authorizes a push, tag, release,
publication, `dist/` artifact, license selection, visibility change, successor work order,
or effectiveness claim. The repository remains pilot-stage, unpublished, and unlicensed,
with `origin/main` one commit behind local `main` after this closeout.

### I.15–I.18, recorded at WO-PL-010 closeout

**Written by:** Codex/OpenAI, transcribing the fresh review and the Owner's `Approved`
disposition. Controlled inference is labelled; counts above are deterministic.

### I.15 The recorder rule is now coherent across its distributed surfaces

Deterministic: README, the adoption skill, and both migration-guide copies now distinguish
commit-free bootstrap from explicitly Owner-directed recorder closeout. Pointer removal is
an Owner decision even when its keystroke is delegated. The guide copies are byte-identical.

Controlled inference: this removes contradictory instructions but does not yet prove the
workflow in an adopting project. A separate adopter remains the first prospective real exercise.

### I.16 Operating cost improved again, with an important caveat

Deterministic: WO-PL-010 closed with zero rework cycles, one additional closeout session,
and an Owner brief below the 500-word ceiling. The first fresh review returned ACCEPT.

Controlled inference: two consecutive zero-rework orders are encouraging, but the work
orders and reports remain large, and the activation corpus metric was missed for a third
cycle. I.2 is improved, not discharged.

### I.17 Dispatch remains the weak surface

Deterministic: the issued acceptance command confused an output directory with a ZIP path,
and activation again omitted 9.2.5. The source gate independently caught the implementer's
temporary host-path defect before acceptance. No out-of-grant mutation succeeded.

Controlled inference: the product gates are doing useful work; the dispatch process still
needs simplification or validation. RFI-25, RFI-27, and RFI-28 remain the prospective
pre-dispatch-validator route, not an authorized implementation.

### I.18 Publication remains blocked

Nothing in WO-PL-010 authorizes a push, release artifact, tag, publication, license,
visibility change, second-project work, or effectiveness claim. The repository remains pilot-stage,
unpublished, and unlicensed, with four of ten counted work orders complete.

### I.19–I.22, recorded at WO-PL-011 closeout

**Written by:** Codex/OpenAI, transcribing the independent review and the Owner's `Proceed`
authorization. Controlled inference is labelled; counts above are deterministic.

### I.19 The archive is current, local, and reproducible

Deterministic: the checked-in source archive was built only after WO-PL-011's completed
records replaced the live work-order and report paths. Its manifest passes, an external
rebuild is byte-identical, and no ACTIVE work order or pointer is packaged.

### I.20 Activation-time corpus measurement finally ran

Deterministic: 52 routed documents / 88,933 words, zero routing gaps, zero orphans. Fresh
review corrected one route-interpretation error in one rework cycle.

Controlled inference: measurement is now operational but still manual. The correction is
evidence that independent review remains necessary while routing lacks mechanical support.

### I.21 This does not establish deployment readiness by itself

The archive is ready to supply a read-only inventory for an adopting project. It is not an
overlay and must not be unpacked into that project. Adoption remains a separate Owner
decision after document mapping, provider selection, and boundary review.

### I.22 Publication remains blocked

No push, tag, publication, license selection, visibility change, or public release occurred.
The repository remains pilot-stage and unpublished, with five of ten counted work orders
complete.

### I.23–I.26, recorded at WO-PL-012 closeout

**Written by:** Codex/OpenAI, transcribing the fresh Reviewer's evidence and the
Owner's `Accepted` disposition. Controlled inference is labelled; counts above
are deterministic.

### I.23 The native read wall works inside its tested envelope

Deterministic: unit tests, source checks, and a fresh project-root birth test
agree. `Read`, ancestor-rooted `Grep`, and ancestor-rooted `Glob` were denied
before content/traversal; an allowed sibling read succeeded; the structured log
exposed neither sentinel path nor content.

Controlled inference: this closes the specific private-read protection gap in
an adopting project that authorized WO-PL-012. It does not make shell-mediated reads, MCP resources,
additional working directories, hook launch failure, or other providers safe.

### I.24 Dispatch and operating cost remain the dominant weakness

Deterministic: the implementation itself passed final review without a code
defect, but the order required three rework cycles and six additional sessions.
Two Owner-authored dispatch defects and one report arithmetic defect were found
before acceptance. Activation-time corpus measurement was missed again.

Controlled inference: the adapter is better; the process is still too costly.
The evidence strengthens the case for the already-routed pre-dispatch validator,
but does not authorize it or collapse it into a separate project's adapter-adoption work.

### I.25 A separate adopter is ready for an adapter adoption pass

The synchronized Plumbline adapter is now source-checked and birth-tested here.
Any adopter still requires its own project-root installation comparison, grant
mapping, and fresh-session birth test before relying on the protected read
surface. Evidence does not transfer between repositories or provider sessions.

### I.26 Publication remains blocked

No push, `dist/` replacement, tag, publication, license selection, visibility
change, or public release occurred. Plumbline remains pilot-stage and
unpublished, with six of ten counted work orders complete.

### I.27–I.30, recorded at WO-PL-013 closeout

**Written by:** Codex/OpenAI, transcribing the fresh Reviewer's evidence and the
Owner's `Accepted` disposition. Controlled inference is labelled; counts above
are deterministic.

### I.27 The portability defect was in the tests, not the wall

Deterministic: three outside-repository fixtures used a Windows path literal.
Under POSIX, that literal was relative, causing two visible failures and one
vacuously green test. All three now derive a native absolute path outside their
own temporary repository. Adapter bytes and behavior are unchanged.

### I.28 Dual-runtime evidence is now the acceptance rule

Deterministic: the final tree passed 272/272 tests under native Windows Python
and 272/272 under native Ubuntu Python. Canonical and bundled documentation are
synchronized and require both legs for future adapter or adapter-test changes.

Controlled inference: this cheaply prevents the observed cross-platform test
class from recurring unnoticed, but remains a manually reviewed rule rather
than a mechanically enforced CI gate.

### I.29 Review still catches errors, and dispatch cost remains material

Deterministic: three same-work-order drift instances and two report-record
corrections were caught before acceptance; no implementation defect or
successful out-of-grant mutation remained. Activation-time corpus measurement
was omitted again.

Controlled inference: the evidence further supports evaluating the already
routed pre-dispatch validator, but WO-PL-013 neither authorizes nor implements
it. The cost question is not resolved by green tests.

### I.30 Public-release work requires a disclosure boundary

No `dist/` replacement, tag, license selection, visibility change, or public
release occurred. Plumbline remains pilot-stage and unpublished, with seven of
ten counted work orders complete. Any later licensing or disclosure work must
keep second-project source, private benchmark material, proprietary design details, and
trade-secret material outside Plumbline; cross-project facts must be reduced to
the minimum public-safe provenance necessary for Plumbline's own record.

### I.31–I.34, recorded at WO-PL-016 closeout

**Written by:** Codex/OpenAI, transcribing the bounded Sonnet implementation,
the executed verification evidence, and the Owner's standing authorization.
Controlled inference is labelled; counts above are deterministic.

### I.31 The ten-work-order pilot execution phase is complete

Deterministic: WO-PL-016 is counted order 10 of 10. Its final bytes pass 372
tests on Windows and Ubuntu, active release checks refuse exactly the three live
records, and an otherwise identical clean diagnostic copy passes source,
external build, and archive checking. The canonical and bundled adopter checker
are byte-identical.

Controlled inference: completion of ten orders is the evaluation trigger, not
proof of effectiveness. No licensing or publication step begins until the
Doctrine 9.3.1 fresh-agent evaluation receives an Owner disposition.

### I.32 The dispatch validator is now genuinely portable

Deterministic: both supported adoption routes install the same checker
create-only; generic `WO-NNN` and uppercase namespaced identifiers are accepted;
malformed identifiers, filename mismatches, grant divergence, unexpected dirty
paths, and bundle drift remain fail-closed. No Plumbline working record is
introduced through either route.

Controlled inference: this addresses the recurring dispatch defects that
selected WO-PL-014/016. It does not replace the capability wall or mechanically
enforce Owner authority.

### I.33 Review value and process cost remain mixed

Deterministic: fresh review found six same-WO mismatches and two defects first
introduced in WO-PL-014, requiring three correction cycles. One local
diagnostic-copy episode traversed read-denied Plumbline archive/history paths;
it exposed filenames and sizes but no contents, had no implementation impact,
and involved no second-project material or external service.

Controlled inference: the checker reduced one class of dispatch risk, but this
last order still incurred meaningful review and recovery cost. The pilot
evaluation must assess the full ten-row evidence rather than extrapolate from
the final green suite.

### I.34 Publication remains blocked

No push, checked-in `dist/` replacement, tag, publication, license selection,
visibility change, second-project access, or public release occurred. Plumbline remains
private and unlicensed. WO-PL-017/018/019 stay queued behind pilot evaluation,
Owner disposition, and private chain-of-title confirmation.

### I.35–I.39, recorded during WO-PL-017

**Written by:** Codex/OpenAI, transcribing the fresh Opus evaluation and the
Owner's ratified DR-002 disposition. Controlled inference is labelled; closed
pilot evidence is unchanged.

### I.35 The pilot supports continued use, not proof

Deterministic: ten counted orders produced 12 counted denials, zero successful
out-of-grant mutations, 57 same-work-order drift items, eight distinct
later-detected instances represented by ten row attributions under D.7.1, and
no intent-reconstruction archaeology. Every measured activation
corpus had zero routing gaps and zero orphan Tier-2 documents.

Controlled inference: the controls merit continued use under Doctrine 0.6,
provisionally. The evidence does not prove reduced cost, complete containment,
universal Reviewer independence, or transfer to another repository.

### I.36 The cost prediction failed

Deterministic: the first five counted orders required four rework cycles; the
last five required 15. The scopes differ, but the adopted prediction of one
cycle is not supported. Eight reported briefs stayed below 500 words; Owner
active minutes were never captured.

Controlled inference: brief length is controlled, total operating economics
are not. Prospective closeout asks for self-reported Owner minutes and records
`NOT REPORTED` when none are supplied.

### I.37 Manifest and routing controls needed repair

Deterministic: the final three counted work orders lacked complete Appendix B
classification, and WO-PL-014 materialized routing text before separate Owner
ratification. DR-002 ratifies the exact current R.12–R.14 wording and preserves
the historical sequence as a deviation. WO-PL-017 makes incomplete future
classification fail closed.

### I.38 Stop-rule and shell limitations remain explicit

Deterministic: nine of ten orders declared restricted shell despite the signed
default-denied plan, and the completed pilot's successful-mutation stop rule
had no qualifying whole surface on which to fire.

Controlled inference: these are limitations to design around prospectively,
not measurements to rewrite after the pilot. Future orders disclose the actual
provider envelope; future experiments define stop conditions over declared,
birth-tested channels as well as whole surfaces.

### I.39 Publication remains blocked

WO-PL-017 completed the blocking remediation and WO-PL-018 completed disclosure
cleanup and license records. WO-PL-019 completed license mechanization;
WO-PL-020 completed the clean-history candidate gate.
DR-003 selects the license map, but
no publication, visibility change, push, tag, second-project access, or
checked-in `dist/` update is authorized here.

### I.40 WO-PL-018 completed the license-record boundary

Deterministic: the repository now carries DR-003's selected license texts,
license map, contribution terms, naming reservation, disclosure cleanup, and
distribution-check coverage. Fresh review found no remaining implementation or
record correction after three returns. The Owner accepted four explicit
deviations: the official SPDX MIT-0 JSON fallback after a `.txt` 404, one
read-only search-source boundary departure, two behavioral tests added after
implementation, and the history-free Ubuntu 390/391 result. Publication and
license mechanization remain separate gates. The third return corrected a
staging-only visibility gap in the whitespace check through exact-path Git
attributes while preserving official license bytes; it required no fifth
deviation.

### I.41 WO-PL-019 completed deterministic license mechanization

Deterministic: every packageable source path now resolves to exactly one
DR-003 license through an executable SPDX header or `REUSE.toml`. The public
license checker passes with zero findings; its failure categories and
distribution integration are exercised through public processes. All
executable Python modules retain their docstrings, canonical adapter/checker
copies remain byte-identical, and official legal bytes remain unchanged.

Fresh review ended **CONDITIONAL ACCEPT/HIGH** with no implementation defect.
The Owner accepted one consolidated command-mediated denied-tree read
deviation, the disclosed TDD chronology deviation, focused Ubuntu evidence in
place of a literal full safe-Ubuntu suite, and the Reviewer's temporary
bytecode-cache residue as having no implementation impact. The post-closeout
external build/archive gate remained mandatory rather than waived. No
second-project repository or content was accessed or disclosed.

After lifecycle retirement, source and license checks passed. A fresh external
build produced 149 payload files plus the manifest; the 150-entry archive
passed its checker with the required licensing records present. Temporary
output was removed and checked-in `dist/` remained unchanged.

### I.42 WO-PL-020 is a derivation gate, not publication

Deterministic: the accepted order builds only an external candidate from an exact
positive allowlist and checks generated manifest/provenance records, private
pattern absence, lifecycle state, licensing, and projection-mode distribution
rules. Two current 85-file candidates are byte-identical; two rebuilt
projection archives are byte-identical and pass explicit archive
checks. The full public candidate suite passes 455/455 on Ubuntu with two
explicit platform/evidence substitutions. Final Windows discovery ran 455
tests; 15 `init.sh` cases failed solely in the nested-Bash Windows-path
translation envelope while every non-harness test passed. The Owner accepted
that deviation together with the disclosed TDD chronology, command-mediated
denied-tree read, and Reviewer traversal deviations. It
does not initialize Git, configure a remote, publish, change
visibility, replace `dist/`, or access a second project.

Controlled inference: a passing candidate is evidence that a publication input
can be reproduced from the private governed source. It is not itself a release
or an Owner decision to publish.

### I.43 WO-PL-021 aligned the distribution without migrating the project

Deterministic: canonical and bundled Doctrine 0.7 templates, migration guidance,
and validator behavior now agree with DR-004. The amended platform gate passed
on the full Windows governed source, the targeted sanitized Ubuntu changed
modules, and both full real Ubuntu public candidates. The two independently
built 88-file candidates were byte-identical and checker-clean; the ephemeral
Owner-controlled private-pattern input was deleted after local verification.

Controlled inference: Doctrine 0.7 is ready as a distribution package, while
this repository's own governance remains ratified at 0.6. Projection remains a
verification and derivation gate, not publication or project migration.

### I.44 WO-PL-022 makes public evidence scope testable

**Written by:** Codex/OpenAI, transcribing the bounded Sonnet implementation,
the final Reviewer's evidence, and the Owner's 2026-08-21 acceptance.

Deterministic: the public candidate now distinguishes the private governed
source, source distribution, and positive-allowlist candidate; discloses that
WO-PL-017 through WO-PL-020 were Codex/instruction-bounded; includes a
Plumbline-only aggregate pilot example; and fails executable checks when those
truths drift. Final Windows and two real Ubuntu candidate suites passed, both
candidates remained byte-identical, and all private temporary inputs and
outputs were deleted.

Controlled inference: the candidate is a reproducible, evidence-bounded input
to a later publication decision, not a publication act or proof of private
history. WO-PL-022's `8 / 8 / 0` classification depends partly on independently
attested session tool exclusion; that provisioning judgment must not be
retold as an observed-denial birth test. The proposed standing process for
local-only ephemeral verification inputs remains unratified.

### I.45 WO-PL-023 separates dispatch falsification from runtime authority

**Written by:** Codex/OpenAI, transcribing the ratified Doctrine candidate,
the fresh Reviewer's evidence, and the Owner's 2026-08-21 acceptance.

Deterministic: Doctrine 0.8 and DR-005 define protected-control-plane
semantics, distinguish labeled birth-test falsification probes from grants of
authority, and preserve 0.6/0.7 dispatch compatibility. Canonical and bundled
artifacts agree; Windows and native Ubuntu suites passed; and two independent
92-file projections were checker-clean and byte-identical before their private
input and outputs were destroyed.

Controlled inference: dispatch validation now rejects ordinary protected-path
grants and recognizes a labeled expected-denial probe, but the runtime adapter
does not yet enforce the 8.7 floor. RFI-22 therefore remains open and the
renumbered WO-PL-026 remains necessary but unbegun after project migration.
The verified projection is input to the later WO-PL-027 and Owner publication
gates, not publication. Plumbline's project governance remains bound to
Doctrine 0.6.

### I.46 WO-PL-024 exposed a binding-before-implementation sequencing rule

**Written by:** Codex/OpenAI, transcribing the Owner's 2026-08-21 correction
disposition and the preserved index/lifecycle evidence.

Deterministic: WO-PL-024 was activated as a 0.6-bound work order after the
methodology distribution had ratified 0.8, but before this project migrated.
Only candidate/active structural validation ran. The Owner voided it before
implementation, preserved both records in history, retired the pointer, and
permanently consumed the identifier. The corrected WO-PL-023 brief and exact
38-path staged set passed the unscoped whitespace gate and became private
commit `db0b4c1`.

Controlled inference: methodology ratification and project binding are
separate events under DC.4. Wall hardening that depends on 0.8 control-plane
semantics must follow, not precede, the project's own ratified migration. The
corrected queue therefore places cumulative project migration at WO-PL-025,
wall hardening at WO-PL-026, and verification-only release work at WO-PL-027.

### I.47 WO-PL-025 makes the project binding explicit before dependent work

**Written by:** Codex/OpenAI, transcribing the exact ratified migration records,
the fresh Reviewer's evidence, and the Owner's 2026-08-21 acceptance.

Deterministic: exact DR-003 and charter bytes made the project binding
operatively 0.8 before WO-PL-025 activation. The migration then replaced all
five project-local templates with canonical 0.8 bytes and passed the full
Windows and native Ubuntu suites. Acceptance records the completed migration;
it is not the event that first made the 0.8 work order valid.

Controlled inference: sequencing project migration before wall hardening
removed the defect exposed by void WO-PL-024. It does not establish categorical
control-plane enforcement: the honest classification remains 8 / 0 / 8,
RFI-22 remains open, and WO-PL-026 requires a separate Owner decision before
activation or implementation.

### I.48 WO-PL-028 makes publication truth stable across the lifecycle

**Written by:** Codex/OpenAI, transcribing the bounded Sonnet implementation,
the independent review returns, and the Owner's 2026-08-26 acceptance.

Deterministic: the public documents now distinguish the separate private
governed source from a positive-allowlist public artifact, identify private-
only evidence as absent, describe publicly carried evidence as selected rather
than complete, and avoid statements that become false when publication status
changes. Two final 92-file projections matched byte-for-byte after complete
Windows and native-Ubuntu suites and final checker runs; the final Reviewer
returned ACCEPT. All diagnostic candidates and private inputs were deleted.

Controlled inference: this closes the documentation-truth defects found after
WO-PL-027, but it does not publish anything. The accepted canary-ordering
deviation weakens only the pre-mutation process evidence for this order; it
does not alter the genuine denial record, the zero-mutation result, or the
independently verified public bytes. A publishable artifact still requires a
new post-closeout dual rebuild, fresh review, and explicit Owner decision.

### I.49 WO-PL-029 makes projection lifecycle truth mechanically durable

**Written by:** Codex/OpenAI, transcribing the bounded Sonnet implementation,
the two independent review returns, and the Owner's 2026-08-26 acceptance.

Deterministic: projected State now identifies itself as a source-commit
snapshot; omitted report references are checked across inline-code, plain, and
Markdown-link forms; no value-derived private-input fingerprint enters public
provenance; and the optional complete-tree ledger has one reproducible public
serialization. Final source and dual-candidate Windows/Ubuntu suites passed,
the candidates and candidate-built archives were byte-identical, and the fresh
re-review returned PUBLICATION ACCEPT.

Controlled inference: these controls make a future post-closeout candidate a
credible publication input, not a publication act. The coordinator-awareness
deviation prevents a literal claim that the screening values were never known
to any model in this work order, but no value or fingerprint entered Sonnet,
Reviewer, repository, candidate, archive, or public bytes. All session
candidates were deleted. Publication still requires a new post-closeout dual
build, fresh review, and explicit Owner decision.

### I.50 WO-PL-030 converts the cold audit into executable release controls

**Written by:** Codex/OpenAI, transcribing the final publication Reviewer's
evidence, the completed Windows/Ubuntu lifecycle, and the Owner's 2026-08-27
acceptance.

Deterministic: the clean public root is host-neutral; CI and first-use examples
are executable; runtime and dispatch parsing agree on the repaired protected-
control-plane contract; retained-reference and projection rules fail closed;
canonical and installed adapter bytes match; and 25 exposed protected mutation
calls across native Windows and Ubuntu were denied with exact append-only
evidence and zero success. Final source and independently rebuilt public
candidates passed their declared platform gates, and the fresh publication
Reviewer returned ACCEPT/HIGH.

Controlled inference: this closes every reproduced blocker from the cold audit
of the private baseline and proves the protected-control-plane matrix on the
two tested native providers. It does not prove every broad capability surface,
every future provider version, or publication itself. The honest classification
remains 8 / 0 / 8, and release still requires a new post-closeout dual rebuild,
fresh review, and explicit Owner publication decision.

### I.51 WO-PL-031 closes the final public-source truth gaps without hiding installation drift

**Written by:** Codex/OpenAI, transcribing the fresh Reviewer's correction
returns and the Owner's 2026-08-27 acceptance.

Deterministic: the projected contribution command is context-correct; traversal
patterns are admitted only when confinement is provable; portable aliases cover
the complete protected floor; an existing malformed pointer or grant fails
closed for modeled reads; project-root authority is explicit; and host-path
screening recognizes real token boundaries without treating arbitrary
substrings as paths. Final governed source and two independent 92-file
candidates passed Windows and native Ubuntu. Both candidate ledgers and their
archives reproduced byte-for-byte, and final fresh re-review returned ACCEPT.

Controlled inference: the public source is ready for the next release gate, but
the installed private hook intentionally remains on the previously accepted
digest because WO-PL-031 did not authorize a protected-control-plane install.
That difference is recorded as a remaining gate, not concealed by weakening
the checker. Publication still requires separately governed installation and
birth testing, a new post-closeout dual rebuild and review, and an explicit
Owner publication decision.

### I.52 WO-PL-032 closes installation drift with two-platform evidence

**Written by:** Codex/OpenAI, transcribing the native provider evidence, fresh
Reviewer's verification, and the Owner's 2026-08-27 acceptance.

Deterministic: installed, canonical, and bundled hook bytes are identical at
`DD29AF2A39D25E0270AD9ACC23EE912F81E39C674E1179759F4A3010C6A0C1A0`;
normal Windows registration is restored; native Windows and Ubuntu Sonnet
sessions each produced the exact four ordered denials after bounded one-line
precondition reads; all protected targets remained unchanged; and the original
296-record ledger is a byte-exact prefix of the final 305-record ledger. The
full Windows suite, focused Windows/Ubuntu suites, active dispatch, licensing,
and whitespace gates passed, and fresh review returned ACCEPT/HIGH.

Controlled inference: the evidence proves the accepted installed hook blocked
the tested Write channel and protected control-plane targets on the two tested
native providers. It does not make any complete broad capability surface fully
enforced or authorize publication. The already authorized post-closeout dual
rebuild and fresh publication review must still run on the committed closeout
bytes before the Owner makes a separate publication decision.
