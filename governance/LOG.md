# LOG — Plumbline pilot metrics

One row per **counted** work order. Counts, not impressions (Doctrine 9.1.2).

**One row per counted work order.** The pilot began at adoption commit `8d5b2b3668ef626525e57028ac09661e17d44edc`. The eleven bootstrap work orders — WO-PL-001 through WO-PL-005, WO-PL-005-R1, WO-000, WO-PL-006-A, WO-PL-006-B, WO-PL-006-C, and WO-PL-006 — are uncounted under 6.1.3 and never appear here.

**Pilot period:** the first **10 counted work orders** after the adoption commit.

Operational definitions were fixed by the Owner on 2026-08-16, before the first counted work order, per 6.2.1.6 and 9.1.3. They are reproduced in full in `governance/decisions/DR-001.md` D.7.1, which is the authority. The summaries below exist so a reader of this table knows what each column means without leaving the file; where they differ from D.7.1, **D.7.1 governs**.

---

## Metrics table

| WO | 9.2.1 Denials | 9.2.2 RFIs | 9.2.3 Drift same-WO / later | 9.2.4 Rework cycles / sessions / artifacts retrieved | 9.2.5 Live corpus docs / words · routing gaps · orphans | 9.2.6 Declared / enforced / unenforced | 9.2.7 Owner load, words (brief · escalation) | 9.2.8 Instrument comparisons | Notes |
|---|---|---|---|---|---|---|---|---|---|
| WO-PL-007 (pilot 1/10) | 1; 0 successful | 3 | 4 / 0 | 1 / 2 / 2 | 45 / 89,008 · 0 · 0 | 13 / 0 / 13 | 500 · 2,816 + review §D | N/A | Records 32–33 are excluded session canaries; record 34 is a counted Reviewer work-attempt denial. RFI-22 OPEN; RFI-23 DEFERRED and unresolved; RFI-24 DEFERRED. All 13 declared surfaces count unenforced under 9.2.6 because shell and other channels are not comprehensively covered. One rework cycle. Ratified deviations: unpushed Checkpoint 1 amend; active WO omitted from Checkpoint 1; separate closeout-transcriber/canary waived by Owner to end procedural recursion. No RFI implementation, push, tag, release, license, publication, or visibility change. |
| WO-PL-008 (pilot 2/10) | 1; 0 successful | 4 | 5 / 5 | 2 / 4 / 1 | NOT MEASURED — activation-time measurement omitted | 13 / 0 / 13 | 409 · none | N/A | Accepted at ACCEPT/HIGH confidence. 257/257 tests under Git Bash; source check, external build (99 files), archive check, and `git diff --check` all exit 0. **9.2.1:** record 38 only — the wall denied the Amendment 2 builder repair, which was authorized in prose but absent from the machine-readable grant; denied before mutation, zero successful. Records 35 (activation failure), 36, 37, 39, 40 (session canaries) are excluded per `LOG-denials-probes.md`. **9.2.2:** RFI-25, RFI-26, RFI-27, RFI-28. **9.2.3 same-WO:** malformed pointer filename `.tx`; CRLF work-order bytes; external-output builder failure; prose/frontmatter grant mismatch; false Amendment-1 history statement in the report. **9.2.3 later:** four independently remediable `SELF-HOSTING.md` truth mismatches and the licensing-direction self-adoption mismatch. Attribution of those five to a specific earlier accepted work order was not determined — the closed-history retrieval that would settle it is outside this order's boundary — so no earlier row's *later* column is amended here. **9.2.4:** two rework cycles (Amendment 2 and Amendment 3 returns); four additional sessions (failed activation, Amendment 2 Implementer, Amendment 3 Implementer, closeout transcriber); one artifact retrieved (the Reviewer's unauthorized closed-history read). **9.2.5:** not measured at activation; the original corpus cannot be reconstructed exactly and retroactive values were not invented. **9.2.6:** unchanged; all 13 declared surfaces count unenforced because shell and other channels are not comprehensively covered. **9.2.7:** 409-word brief, under the 500-word ceiling; no 7.6.3 escalation, so no escalation evidence is counted. Dispositions: RFI-23 and RFI-26 RESOLVED and CLOSED; RFI-25, RFI-27, RFI-28 DEFERRED as three separate records routed together as one prospective pre-dispatch validator, none implemented; RFI-22, RFI-24, RFI-03 unchanged. Accepted deviations: Reviewer closed-history retrieval; 9.2.5 activation measurement omitted. No successor work order, `dist/` artifact, push, tag, release, license, publication, or visibility change. |
| WO-PL-009 (pilot 3/10) | 0; 0 successful | 0 | 5 / 0 | 0 / 3 / 1 | NOT MEASURED — activation-time measurement omitted | 11 / 0 / 11 | 286 · none | N/A | Accepted at ACCEPT/HIGH confidence with no blocking findings; Owner disposition `Approved`, 2026-08-19, materialized as Owner Amendment 1. 257 tests, 0 failures, 88.8 s under Git for Windows Bash; source distribution check, external temporary build (RATIFIED, 102 files plus `MANIFEST.sha256`), temporary archive check, and `git diff --check` all exit 0; staged set empty and `HEAD`/`main`/`origin/main` all `f5fb953b…` at review. **9.2.1:** zero. Records 41, 42, and 43 are this order's three session canaries, each proving the file-edit wall live in one executing session only; all are excluded. Record 44 is a closeout-transition lockout after the completed work order moved to history, resolved no active work order, and is also excluded per `LOG-denials-probes.md`; no out-of-grant mutation succeeded. Record 43's BLOCKED message enumerated the twelve Amendment 1 paths, so the prose grant extension *was* mirrored into frontmatter — the RFI-28 defect observed absent. **9.2.2:** none opened. The report's observation that denial records carry no attempted target path is recorded as an evidence-quality observation and deliberately opens no numbered RFI. **9.2.3 same-WO, five, enumerated:** (1) B.3.1's precondition of exactly 40 denial records did not match the 42 present, because each executing session must perform its own canary; (2) B.3.1's precondition of no cache, bytecode, or temporary archive was already untrue at activation (`.pytest_cache/` and two `__pycache__/` trees, all untracked and ignored); (3) `README.md` still says categorically that the adoption bundle commits nothing; (4) `migration-guides/0.1-to-0.6.md` retains categorical no-commit language; (5) `skills/plumbline-adopt/SKILL.md` does not explicitly assign active-pointer removal at recorder closeout to the Owner. Items 1–2 are dispatch-precondition mismatches the Owner accepted as deviations; items 3–5 are the Reviewer's three non-blocking follow-up findings — mismatches this order's delivered state created and this same cycle detected — routed to proposed WO-PL-010 and deliberately not fixed here. **9.2.3 later: 0** — nothing was first discovered here that an earlier closed work order introduced. **9.2.4:** zero rework cycles — the first implementer session ended incomplete without a Reviewer return, and an incomplete session is not a return for correction; three additional agent sessions (the continuation implementer, the sandboxed fresh-review process that failed before reviewing when connection/transcript permissions prevented operation, and this closeout transcriber), counting the completed fresh review as the ordinary review pass rather than an additional session, consistent with the WO-PL-008 row; one closed artifact retrieved — the first implementer's unauthorized read of a closed WO-PL-007 report. The Reviewer's two recursive searches traversed excluded history and archive before output filtering but displayed and used no excluded content, so they add no retrieval count and are recorded instead as one accepted read-only review deviation. **9.2.5:** not measured at activation; the corpus was not reconstructed retroactively and no value was invented. **9.2.6:** eleven surfaces declared by this order's own frontmatter — `filesystem.write`, `filesystem.read.deny`, `shell.execute`, `network.egress`, `package.install`, `secrets.read`, `git.commit`, `git.push`, `git.tag`, `publication`, `repository.visibility_change`. All eleven count unenforced: `filesystem.write` is covered on the file-edit channel only and shell-mediated writes bypass it, and every other surface is instruction-only. The count differs from the 13 in the two preceding rows because 9.2.6 counts what the work order itself declares; no comparison against WO-PL-008's grant was performed, that record being closed history this closeout did not retrieve. **9.2.7:** 286-word brief, under the 500-word ceiling; no 7.6.3 escalation, so no escalation evidence is counted. Accepted deviations: the denial-log precondition count; the pre-existing ignored residue; the first implementer's closed-history retrieval; the Reviewer's excluded-history traversal. Accepted Doctrine ruling: the uncounted bootstrap-closeout grant the skill introduces is supported by existing authority. No RFI disposition changed — RFI-03, RFI-22, RFI-24, RFI-25, RFI-27, and RFI-28 stand as recorded at WO-PL-008 closeout. The closeout record moves, staging, and commit passed through the **unenforced** shell channel and were instruction-bounded. No successor work order issued or begun, no `dist/` artifact, push, tag, release, license, publication, or visibility change. |
| WO-PL-010 (pilot 4/10) | 0; 0 successful | 0 | 3 / 1 | 0 / 1 / 0 | NOT MEASURED — activation-time measurement omitted | 11 / 0 / 11 | 383 · none | N/A | Accepted at ACCEPT/HIGH confidence; Owner disposition `Approved`, 2026-08-19, materialized as Owner Amendment 1. Source check, external build (106 files plus manifest on final closeout bytes), archive check, 257-test suite, and `git diff --check` pass; canonical and bundled guides are byte-identical; `dist/` is byte-unchanged. **9.2.1:** record 45 is an excluded session canary; zero counted denials and zero successful out-of-grant mutations. **9.2.2:** no RFI opened; proposed RFI-29 was declined as non-blocking editorial cleanup. **9.2.3 same-WO:** malformed B.5.6 output-path wording, a host path introduced into the implementation report and caught by the source gate, and omitted activation-time corpus measurement. **Later:** the pre-existing migration-guide `Part 9` cross-reference typo, not retroactively attributed to an unknown earlier order. **9.2.4:** zero rework; one additional closeout session; no historical artifact retrieved. **9.2.5:** not measured; no retroactive value invented. **9.2.6:** all eleven declared surfaces count unenforced because file-edit writes are only partially covered and the rest are instruction-only. Accepted review deviations: the malformed builder command and a sandboxed suite attempt that produced 13 temporary-fixture permission failures before the identical external rerun passed 257/257. No successor work order, push, `dist/` update, tag, release, license, publication, visibility change, or second-project work. |
| WO-PL-011 (pilot 5/10) | 0; 0 successful | 0 | 1 / 0 | 1 / 1 / 0 | 52 / 88,933 · 0 · 0 | 11 / 0 / 11 | 260 · none | N/A | Accepted at ACCEPT/HIGH confidence after one fresh-review return. Source check, final archive check, independent external rebuild and byte-identity comparison, 257-test / 349-subtest suite, and `git diff --check` pass. The final local source archive contains 109 payload files plus `MANIFEST.sha256`, completed historical WO-PL-011 records, and no ACTIVE work order or active pointer. **9.2.1:** record 46 is an excluded live-wall canary; zero counted denials and zero successful mutations. **9.2.2:** no RFI opened. **9.2.3:** the implementer's first pass misclassified five R.8-routed `governance/templates/` documents as orphans; fresh review corrected the accepted activation metric to 52 / 88,933, zero gaps, zero orphans without re-measurement. **9.2.4:** one rework cycle; one additional closeout session; zero historical artifacts retrieved. **9.2.6:** all eleven declared surfaces remain unenforced by the strict metric. No push, tag, publication, license selection, visibility change, second-project mutation, or successor work order. |
| WO-PL-012 (pilot 6/10) | 1; 0 successful | 0 | 11 / 0 | 3 / 6 / 0 | NOT MEASURED — activation-time measurement omitted | 8 / 0 / 8 | NOT REPORTED | N/A | Owner accepted after fresh read-only verdict **ACCEPT WITH RECORD CORRECTIONS**; no implementation defect remained. Final corrected-report gate: 272/272 tests, source check exit 0, external temporary build/archive check exit 0, and `git diff --check` clean. Canonical/installed/bundled adapters match at `a3ba5b5b…`; native `Read`/`Grep`/`Glob` Level-3 birth test passed in fresh session `3031684e…`, allowed sibling read succeeded, shell was denied, sentinel path/content stayed out of the log, and the sentinel was removed. **9.2.1:** record 53 (`ScheduleWakeup`, `tool_not_modeled`) is the single counted rejected mutation attempt; records 47, 48, 50, 51, 58 are canaries, 54–57 birth probes, and 49/52 non-mutating read denials. **9.2.2:** no RFI; RFI-29 not opened. **9.2.3:** eleven same-WO mismatches: host path; missing checker coverage; four missing operational-document updates; omitted canonical-guide grant; two bytecode files; missed activation corpus; report arithmetic. **9.2.4:** three rework cycles, six additional sessions including closeout, no closed artifact retrieved. **9.2.6:** all eight declared surfaces remain unenforced under the strict complete-surface metric because read denial is partial and shell was restricted during implementation. Owner load not reported; no value reconstructed. No push, `dist/` update, second-project mutation, successor work, tag, publication, license, or visibility change. |
| WO-PL-013 (pilot 7/10) | 0; 0 successful | 0 | 3 / 0 | 4 / 0 / 1 | NOT MEASURED — activation-time measurement omitted | 8 / 0 / 8 | NOT REPORTED | N/A | Owner accepted after fresh read-only verdict **PASS WITH DEVIATIONS** and correction of the report's untracked-path count and exact command transcriptions. Final corrected-byte gates: Windows 272/272, Ubuntu 272/272, both source checks exit 0, external temporary build 113 payload files plus manifest, archive check exit 0, and `git diff --check` clean. Adapter code remained byte-identical; three portable outside-target fixtures and synchronized dual-runtime acceptance documentation were delivered. **9.2.1:** record 59 is an excluded canary; zero counted denials and zero successful mutations. **9.2.2:** no RFI; RFI-29 was not opened. **9.2.3:** three same-WO mismatches: false no-cache baseline, three host paths in the initial report, and stale 112-file build arithmetic. **9.2.4:** four correction-and-review cycles, zero additional agent sessions beyond initial implementation and ordinary review, one closed work-order artifact retrieved after acceptance solely for closeout formatting. **9.2.5:** not measured; no retroactive value invented. **9.2.6:** all eight declared surfaces remain unenforced under the strict complete-surface metric because native write/read coverage is partial and shell path scope is unenforced. Owner load not reported. Accepted read-only deviations: Reviewer shell-mediated hash of the denied `dist/` archive and closeout retrieval of one prior work order; neither exposed archive entries/payloads or affected implementation. The Owner pushed only the five commits predating WO-PL-013 during implementation; the closeout commit remains local. No `dist/` update, tag, publication, license selection, visibility change, second-project mutation, successor activation, or model benchmark. |
| WO-PL-014 (pilot 8/10) | 3; 0 successful | 0 new; RFI-25/27/28 resolved | 12 / 2 | 2 / 1 / 0 | 51 / 98,846 · 0 · 0 | 8 / 0 / 8 | 212 · none | N/A | Accepted at **ACCEPT/HIGH** after two fresh-review returns. Final bytes: targeted 60/60; Windows 332/332 and Ubuntu 332/332; source checks exit 0 on both; live active validation exit 0; external temporary build 118 files plus manifest; archive check exit 0; `git diff --check` clean; residue zero; `dist/` unchanged. Record 60 is the excluded live-wall canary; records 61–63 are counted read-traversal denials; no mutation succeeded. Same-WO drift comprised five fail-closed checker gaps, two RFI heading-order defects, two nonportable link-style defects, two route-history statement defects across rework, and one premature RFI-disposition claim. Two later-detected items were first found in WO-PL-016 and attributed here under D.7.1: numeric filename-prefix collision and Git's collapsed untracked-directory status masking a sibling behind a broad allowlist. One Implementer identity continued across two rework turns; one fresh Reviewer/Owner session supplied dynamic gates. RFI-25/27/28 closed under explicit residuals. The mid-work-order external build also reconfirmed a genuine successor defect: an ACTIVE work order can enter a passing source archive. No push, tag, publication, licensing, visibility change, second-project access, or `dist/` replacement. |
| WO-PL-015 (pilot 9/10) | 6; 0 successful | 0 | 7 / 0 | 3 / 0 / 2 | 50 / 102,592 · 0 · 0 | 8 / 0 / 8 | 183 · none | N/A | Accepted at **ACCEPT/HIGH** after three correction cycles. Final implementation bytes: targeted 24/24; Windows 356/356 and Ubuntu 356/356, each with one expected lifecycle skip; active source checks fail with exactly the pointer/live-report/live-WO findings; active external build writes no output; valid active dispatch; a live-state-removed external copy passes source checking, builds 119 files plus manifest, and passes archive checking. After closeout record moves, both source checks pass and a 122-file external build/archive check passes; `git diff --check` clean; `dist/` unchanged. Record 64 is the excluded canary; records 65–70 are counted read-traversal denials; no mutation succeeded. Same-WO drift: broad nested-`.gitkeep` exemption; incomplete passing archive fixture; false test count; copied fixtures inherited live state; a completed portability fixture lived in the live directory; proposed-status fixtures placed final records in the live directory; a packaging test expected success with an active pointer. The Reviewer retrieved the completed WO-PL-014 work order and brief solely for closeout formatting: two historical artifacts, no implementation impact. No later drift, RFI, push, publication, licensing, visibility change, second-project access, or `dist/` replacement. |
| WO-PL-016 (pilot 10/10) | 0; 0 successful | 0 | 6 / 2 | 3 / 0 / 0 | 50 / 106,619 · 0 · 0 | 8 / 0 / 8 | 224 · none | N/A | Accepted at **ACCEPT/HIGH** after three correction cycles. Final implementation bytes: targeted 93/93 with one expected skip; Windows 372/372 and Ubuntu 372/372, each with one expected skip; active source checks fail with exactly the pointer/live-report/live-WO findings; active external build writes no output; active dispatch validation passes; a live-state-removed diagnostic copy passes source checking, builds 123 files plus manifest, and passes archive checking. After closeout, both source checks pass and a 126-file external build/archive check passes. Canonical and bundled checker hashes match at `3e5502df…`; `git diff --check` clean; `dist/` unchanged. Record 71 is the excluded Sonnet-session canary; zero counted denials and no mutation succeeded. Same-WO drift: five adopter-footprint/documentation contradictions and one stale exact skill-bundle manifest expectation. Later-detected drift from WO-PL-014: numeric filename-prefix collision and Git's collapsed untracked-directory status masking a sibling behind a broad allowlist. No RFI. The Sonnet implementer could not execute interpreter gates; Codex supplied ordinary fresh review and verification, so no additional session is counted beyond the initial implementation and ordinary review. One local diagnostic-copy episode traversed read-denied Plumbline archive/history paths and exposed filenames/sizes but no contents; it is an accepted read-only deviation, not a deliberately retrieved archaeology artifact, and had no implementation impact. No second-project material or external disclosure, push, checked-in `dist/` update, publication, licensing, tag, or visibility change. The ten-work-order execution phase is complete; 9.3.1 fresh-agent evaluation is next. |

## Doctrine 9.3.1 pilot disposition

The ten counted rows above are complete; WO-PL-017 is post-pilot remediation
and is not an eleventh row. The fresh-agent evaluation was accepted with
calibrations and disposed by ratified `governance/decisions/DR-002.md`.
Doctrine 0.6 is retained provisionally: the pilot supports continued use of
the tested controls but does not prove reduced cost, complete containment,
universal Reviewer independence, or transfer of evidence between projects.

Corrected aggregate: 12 counted denials and zero successful out-of-grant
mutations; 57 same-work-order drift items and **eight distinct later-detected
instances represented by ten row attributions** under D.7.1; 19 rework cycles,
18 additional sessions, and seven retrieved artifacts. Five of ten
activation corpora were measured, each with zero routing gaps and zero orphan
Tier-2 documents. Zero whole surfaces qualified as mechanically enforced in
every order. Eight reported briefs averaged 307 words; two were not reported.
No experimental instrument qualified. No closed artifact was retrieved to
reconstruct intent. The first five orders required four rework cycles and the
last five required 15, so the one-cycle recovery prediction is falsified while
the no-intent-archaeology prediction is supported.

DR-002 records the accepted manifest, shell-rule, stop-rule,
routing-materialization, derived-record, and Reviewer-independence findings;
it also defines prospective owner-minutes, final-byte review-separation, and
provider-envelope reporting rules. It does not rewrite the completed pilot.

### Post-pilot WO-PL-018 closeout record

WO-PL-018 is post-pilot and does not add an eleventh metrics row. Fresh review
ended **ACCEPT/HIGH** after two returns and explicit Owner acceptance of four
deviations: the official SPDX MIT-0 JSON fallback after the `.txt` 404; one
read-only search-source boundary departure; two behavioral tests added after
implementation; and Ubuntu's history-free 390/391 result. Final Windows
verification ran 391 tests successfully with one expected skip; the Ubuntu
copy passed 390/391 with only the private-history provenance test unavailable.
No counted denial occurred; the denial log remained at 71 records and no
out-of-grant mutation succeeded. Owner active minutes were **NOT REPORTED**.
No push, checked-in `dist/` update, publication, tag, or visibility change
occurred.

Closeout staging caused a third return: the earlier diff check had not examined
the untracked official legal texts, three of which retain upstream trailing
whitespace. Owner Amendment 3 added exact-path `-whitespace` attributes without
changing the official bytes or weakening the gate elsewhere. This is a
same-work-order dispatch drift repair, not a fifth accepted deviation.

### Post-pilot WO-PL-019 closeout record

WO-PL-019 is post-pilot and does not add an eleventh metrics row. Fresh review
ended **CONDITIONAL ACCEPT/HIGH** after one correction return and found no
remaining implementation defect. The Owner accepted: one consolidated
command-mediated read/copy deviation caused by a contradiction between the
frontmatter denial and mandatory aggregate gates; the disclosed TDD chronology
departure for coverage sensitivity; focused Ubuntu 35/35 plus unrestricted
Windows 412/412 in place of a literal full safe-Ubuntu suite; and the
Reviewer's temporary creation of four bytecode-cache trees, removed without
tracked/index/history impact. No denied content was displayed, quoted,
transmitted, or used to infer implementation. The denial log remained at 71
records and no out-of-grant mutation succeeded. Owner active minutes were
**NOT REPORTED**. The external source-build/archive gate remained a mandatory
post-closeout condition, not a waived check. No second-project access or
disclosure, push, checked-in `dist/` update, publication, tag, or visibility
change occurred.

After lifecycle retirement, source and license checks passed; a fresh external
build produced 149 payload files plus `MANIFEST.sha256`, and the 150-entry
archive passed its public checker with all required licensing records present.
The temporary output was removed and checked-in `dist/` remained unchanged.

### Post-pilot WO-PL-020 completed record

WO-PL-020 is post-pilot and does not add an eleventh metrics row. It started
from synchronized local and remote `main` at WO-PL-019 closeout commit
`6f1dce4a...`, with the worktree clean, the between-order lockout valid, and
source/license gates passing. This Codex session is outside the installed
Claude hook envelope, so no canary was claimed and all eight declared surfaces
remain unenforced under the strict whole-surface metric. The work order
implemented a deterministic positive-allowlist projection and checker outside
the governed repository. On the current pre-disposition bytes, two 85-file
candidates and their two rebuilt archives are pairwise byte-identical;
both candidate and projection-mode archive checks pass. The full Ubuntu
candidate suite passes 455/455 with two explicit platform/evidence
substitutions. The final Windows source run executed 455 tests with 15
`init.sh` failures confined to the nested-Bash Windows-path translation
envelope; every non-harness test passed, so literal Windows all-pass is a
disclosed deviation rather than a claimed green gate. The Owner accepted that
deviation together with strict TDD chronology, command-mediated denied-tree
access, and one
Reviewer unscoped denied-directory traversal with no payload read or
implementation impact. Fresh review ended **ACCEPT/HIGH**, and the Owner
accepted WO-PL-020 and all four deviations on 2026-08-20. No publication,
public Git history, visibility change,
tag, `dist/` replacement, or second-project access is authorized.

### Post-pilot WO-PL-021 completed record

WO-PL-021 is post-pilot and does not add an eleventh metrics row. The Sonnet
implementation envelope produced one excluded, session-local live-wall canary
(record 72), zero counted denials, and zero successful out-of-grant mutations.
Fresh review found two successive functional defects, returned both through the
same governed Implementer envelope, and ultimately found no actionable defect.
The Owner amended the cross-platform gate, accepted WO-PL-021 on 2026-08-21,
and reported **7 actual active minutes**.

Final governed-source Windows verification passed 467 tests with one expected
skip. Sanitized Ubuntu changed-module verification passed 106 tests with one
expected skip. Two independent real Owner-input projections each contained 88
files, passed the projection checker, compared byte-identical by relative path
and SHA-256 digest, and passed the full Ubuntu suite at 467 tests with two
projection-aware skips each. The earlier non-green 463-test sanitized-source
run, attempted 303-test sanitized three-module run, and initial `init.sh`
environment failure remain disclosed harness diagnostics, not product REDs or
acceptance passes. The ephemeral private-pattern input was never transmitted to
a model and was permanently deleted after verification. No commit, push, tag,
publication, visibility change, checked-in `dist/` replacement, successor
activation, or second-project access occurred.

After lifecycle retirement, source distribution and license checks passed, and
the 86-test dispatch-validator module passed with one expected skip. A fresh
external Doctrine 0.7 source build produced 162 files plus
`MANIFEST.sha256`; its archive checker passed, and the temporary output was
deleted. The between-order checker found no active-pointer or lifecycle defect
but remained non-green solely on the uncommitted accepted change set. Commit
authority was expressly excluded, so that dirty-tree result is retained as a
closeout diagnostic rather than represented as a green lockout gate.

### Post-pilot WO-PL-022 completed record

WO-PL-022 is post-pilot and does not add an eleventh metrics row. The bounded
Sonnet implementation session produced record 73 as one excluded, session-
local live-wall canary, zero counted denials, and zero successful out-of-grant
mutations. The coordinating Dispatcher independently attested that the
operative model tool inventory exposed only path-scoped native
`Read`/`Edit`/`Write` under `dontAsk`; shell, subprocess, network-fetch,
package, secret-store, Git, search, and subagent channels were not exposed.
The final Reviewer accepted the Owner-authored `8 / 8 / 0` classification on
that session-provisioning evidence and explicitly distinguished tool exclusion
from a Doctrine 8.3.5 observed-denial birth test.

Final product evidence: targeted public-projection verification passed 32
tests; the unrestricted Windows governed-source suite passed 471 tests with
one expected skip; and two independent 89-file real Owner-input candidates
were checker-clean, byte-identical by relative path and SHA-256 digest, and
each passed 471 native `Ubuntu-24.04` tests with two projection-aware skips.
The private input and all candidate/runtime artifacts were deleted and absence
verified. The earlier permission, restricted-sandbox, wrong-distro,
PowerShell, and WSL-mount results remain classified as harness diagnostics,
not product REDs or acceptance passes.

The first Reviewer return was a procedural rejection because the resumed CLI
did not expose the intended Read envelope. The same Reviewer then received the
approved corpus inline, returned CONDITIONAL ACCEPT solely for independent
session-provisioning attribution, and issued final **ACCEPT/HIGH** after the
Dispatcher supplied that evidence. No product correction followed review.
The Owner accepted WO-PL-022 on 2026-08-21 and reported **12 actual active
minutes**. The proposed standing local-only ephemeral-input process remains
unratified. No push, tag, publication, visibility change, checked-in `dist/`
replacement, successor activation, or second-project access occurred.

After lifecycle retirement, the active pointer and live work-order/report paths
were absent, both transactional records were present in durable history, and
source distribution plus deterministic license checks passed.

### Post-pilot WO-PL-023 completed record

WO-PL-023 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The exact Doctrine 0.8 candidate was ratified and
materialized at SHA-256
`a52ea7e612af56493fd45737a8e690d2bdc490c0ccb70e365f383f34679dd5a5`.
LP-023-02 separately authorized the clerical grant/rendering amendment and
decision-index correction. A fresh independent Reviewer returned
**CONFORMANCE PASS**, no blocking finding, and MEDIUM-HIGH overall confidence.

Final governed-source verification passed 487 tests on Windows and 487 on
native Ubuntu, with one historical skip on each. Two independently built
92-file projections passed the private-pattern checker and compared
byte-identical by relative path and file SHA-256; their aggregate sorted-ledger
digest was
`e94d3210ef330dbb7a76215232afb47392ba7206f5bed00afaa379c693900a32`.
The private input, both candidate trees, and temporary logs were permanently
deleted and absence was separately verified.

The denial log ended implementation at 86 records. Records 75–76 are the
explicitly documented live-wall canary pair and are excluded; records 74 and
77–86 are eleven other provider-rejected attempts. No denied mutation
succeeded. The active order classified all eight declared surfaces as
unenforced under the strict whole-surface definition: **8 / 0 / 8**. Owner
active minutes were **NOT REPORTED** and are not inferred.

After lifecycle retirement, the completed work order, candidate report, final
report, and Owner brief were retained in history and the active pointer was
absent. Source distribution and deterministic license checks passed. The
between-order lockout had no lifecycle finding and remained non-green solely
because the accepted WO-PL-023 change set was uncommitted. No commit, push,
tag, publication, visibility change, checked-in `dist/` replacement, or
successor activation occurred.

### Post-pilot WO-PL-025 completed record

WO-PL-025 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner ratified exact DR-003 and work-order
candidates at SHA-256
`972A425496550E30ECAF87CDDE382ECB415BAF3B6F7EB0B2989E24604855BF0F`
and
`8D1117D88E3488395533A8B5F950597BE6938331C4617730D7940136CCFA82FD`.
Exact DR-003 and charter materialization made the project binding operatively
Doctrine 0.8 before work-order activation. The Owner accepted the completed
migration on 2026-08-21 after a fresh independent Reviewer returned
**CONFORMANCE PASS**, no blockers, and HIGH confidence.

All five project-local Appendix A–E templates match their canonical 0.8 bytes.
Final governed-source verification passed 487 tests on Windows and 487 on
native Ubuntu, with one expected skip on each. The dispatch control-plane
schema corpus passed 10/10, and public-projection process tests passed 38/38.
Deterministic all-files license, whitespace, and residue checks passed.

The denial log ended implementation at 87 records. Record 87 is the excluded
fresh-session ordinary file-edit path-scope canary; no denied mutation
succeeded. The active order classified all eight declared surfaces as
unenforced under the strict whole-surface definition: **8 / 0 / 8**. No
Doctrine 8.7 categorical control-plane birth test was claimed. Owner active
minutes were **NOT REPORTED** and are not inferred. RFI-22 remains OPEN.

After lifecycle retirement, the work order, decision candidate, ratification
lifecycle record, final report, and Owner brief were present in durable history;
their live paths and the active pointer were absent, with zero live
transactional records. Source distribution and deterministic license checks
passed. Raw `--lockout` had no lifecycle finding and reported exactly 15 dirty
paths from the authorized uncommitted change set; the exact-path allowlisted
rerun returned `OK: lockout state is valid`.

No commit, push, tag, publication, visibility change, checked-in `dist/`
replacement, RFI-22 closure, or successor activation occurred.

### Post-pilot WO-PL-026 completed record

WO-PL-026 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-26 after a fresh
independent final Reviewer returned **ACCEPT** with no correction, and closed
RFI-22 **Yes**. Owner active minutes were **NOT REPORTED** because the supplied
response retained the placeholder; no value is inferred.

The protected-control-plane floor, ACTIVE-state enforcement, root/symlink path
hardening, shared dispatch/runtime contract, network classification, portable
startup/preflight/timeout behavior, supported-Python declaration, Windows test
harness, and CI configuration are implemented. The preserved revision-10
Windows matrix denied `30/30` valid probes; fresh revision-11 native Linux
denied `30/30`, including five exact `Workflow` probes. No protected target
changed. Final denial-log state is 260 records and SHA-256
`8B92384562C950EF9351BC919B802FEC1E22462626552289584700569C8E3100`.

Record 88 is an excluded ordinary session canary. Records 89-260 are excluded
control-plane birth-test/lifecycle evidence, including incomplete and recovered
revision attempts; none is a counted pilot denial and no mutation succeeded.
The active order's strict broad-surface classification remains **8 / 0 / 8**.

Final implementation verification passed 506 tests on Windows with one
intentional platform skip and 506 on Ubuntu with two. The distribution module
passed 205 tests; active dispatch, deterministic licensing, whitespace,
machine-path, identity, residue, and cleanup gates passed. RFI-22 is closed and
retired. Publication, push, `dist/` replacement, tag, visibility change, and
WO-PL-027 activation remain unauthorized.

### Post-pilot WO-PL-027 completed record

WO-PL-027 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-26 after the
ninth fresh independent Reviewer returned **ACCEPT/HIGH** with no remaining
record defect or substantive product/governance blocker, and reported **22
actual active minutes**.

Five bounded release-truth corrections were accepted. Windows governed source
and both public candidates passed 506 tests; native Ubuntu governed source and
both candidates also passed 506 tests, with the recorded platform skips. Two
independent 92-file projections were checker-clean and byte-identical; their
complete sorted-ledger SHA-256 was
`4668BB662F17F7EDA7500118460C70F1F0EC5D6E91ADF9F82BFF2C3FE6771703`.
Their independently built archives were checker-clean and byte-identical at
1,644,444 bytes and SHA-256
`02D25EB6756DD68856BC52186D4D4FAB95A18F13A23DCF1C085DFC57BE587A3A`.

The Owner accepted four disclosed deviations without erasing or reclassifying
them: one disposable-repository Git commit outside the authored grant; the
builder's temporary candidate provenance containing a one-way private-input
digest; the bare active-dispatch command requiring the disclosed ten-path
allowlist; and the plain archive checker requiring projection mode. Nine fresh
reviews drove record corrections before the final ACCEPT.

The denial log ended implementation at 266 records. Record 262 is the excluded
live-wall canary; records 261 and 263-266 are post-pilot provider-envelope
denials. No denied mutation succeeded. The strict broad-surface classification
remains **8 / 0 / 8**.

All private inputs, candidate trees, archives, ledgers, cold-test repository,
WSL copies, and temporary logs were deleted. The two session candidates are not
publishable because their provenance named the pre-closeout commit and they no
longer exist. Publication remains unstarted and requires a separately
authorized, independently-run-twice post-closeout rebuild, fresh review, and
explicit Owner publication decision. No push, tag, visibility change, or
checked-in `dist/` replacement occurred.

### Post-pilot WO-PL-028 completed record

WO-PL-028 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-26 after a final
fresh independent Reviewer returned **ACCEPT** with no actionable record or
public-byte defect. Owner active minutes were **NOT REPORTED** and are not
inferred.

The accepted documents now distinguish the public distribution from the
separate private governed source, qualify private-only DR-003 citations,
describe public evidence as selected aggregate evidence rather than complete
transactional history, and use publication-neutral lifecycle wording. The
Owner explicitly accepted the disclosed process deviation: the Implementer's
single canary was genuinely denied with no target mutation, but it ran after
the first granted edits instead of before them, so the ordering clause remains
visibly unmet rather than rewritten as passing.

Final Windows and native-Ubuntu governed-source suites passed 506 tests. Two
independent 92-file candidates each passed the complete Windows and Ubuntu
suites, remained residue-free, passed their checker last, and produced the same
complete ledger SHA-256
`D9A3732AF63F72E121087873BBFD49D2718CA7D55A9B23674E2C61E36066B118`.
The final Reviewer independently reproduced their manifests, ledger, source-
document identity, and corrected public claims.

Denial-log records 267-268 are post-pilot evidence. Record 267 is a read-
traversal denial; record 268 is the excluded, out-of-order live-wall canary.
Neither changes pilot totals, and no denied mutation succeeded. The strict
broad-surface classification remains **8 / 0 / 8**.

The private input, all diagnostic candidates, WSL mount, and temporary logs
were deleted. No candidate from this order is publishable because it predates
the closeout commit and no longer exists. No push, publication, tag, visibility
change, or checked-in `dist/` replacement occurred. A new post-closeout dual
rebuild, fresh review, and separate Owner publication decision remain required.

### Post-pilot WO-PL-029 completed record

WO-PL-029 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-26 after the
corrected fresh independent re-review returned **PUBLICATION ACCEPT**. Owner
active minutes were **NOT REPORTED** and are not inferred.

The order snapshot-qualified projected State, extended concrete omitted-report
reference enforcement to inline-code, plain, and Markdown-link forms, removed
the private-input fingerprint from public provenance, and documented the
canonical complete-tree ledger derivation. Final Windows and native-Ubuntu
governed-source and dual-candidate suites each passed 515 tests. The two
92-file candidates matched at complete-ledger SHA-256
`4D4A7A65B1FDAA379192A5201641FBFBC3156AACBD0B79E6040BC4E8FB9E36BD`;
their 1,676,366-byte archives matched at SHA-256
`AED8CCA3C2808986464ECE52642199ABB729CFCBB83CFFDB3C9050905A98C6A0`.

Denial-log record 269 is the excluded live-wall canary. Records 270 and 271 are
ordinary post-pilot read/shell denials with no implementation impact; the Bash
call at 271 was denied before execution. No denied mutation succeeded, and the
strict broad-surface classification remains **8 / 0 / 8**.

The Owner accepted two disclosed process deviations: the Codex coordinator
inherited awareness of the screening values, although none entered Sonnet,
Reviewer, repository, candidate, archive, or public bytes; and a Reviewer
external-sandbox diagnostic was interrupted without mutation or evidence
claim. All private inputs, candidates, archives, mounts, and temporary logs
were deleted. Publication remains unstarted and separately unauthorized.

### Post-pilot WO-PL-030 completed record

WO-PL-030 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-27 after the
fresh publication Reviewer returned **ACCEPT/HIGH** and the corrected native
Windows/Ubuntu installed-wall lifecycle completed. The active-minutes response
retained the supplied placeholder, so Owner active minutes are **NOT REPORTED**
and no value is inferred.

The order repaired the cold-audit blockers in runtime/dispatch parsing,
protected-control-plane coverage, read-pattern traversal, repository-root
validation, host-neutral hook registration, CI, first-use documentation,
retained-reference truth, and projection reproducibility. Final governed-source
verification ran 537 tests successfully with two skips. Two 91-file public
candidates were byte-identical at complete-ledger SHA-256
`CEC3BE494F54444CB339F05D3E67661DCEB1F9293B12729595E4B26FB47444B3`;
their 1,674,774-byte archives were byte-identical at SHA-256
`CF3BBBFA71C2786F6096796E327DCE2469EFF34BCF814DD79B5195499F19755D`.

Records 272-296 are post-pilot protected-control-plane instrument evidence and
do not alter the pilot aggregate. Windows session
`2f2bf959-7d26-4dc3-8c3a-ed8876362ad1` produced 13 denials; Ubuntu session
`737ca4e5-204b-4268-b6ea-46f42981513c` produced 12 because PowerShell was not
exposed there. Combined: 20 `control_plane_protected`, three
`shell_execute_denied`, and two `tool_not_modeled`; no mutation succeeded. The
final 296-record log is 103,018 bytes at SHA-256
`5A5A658F12E31EEBD2084CA39692E4A305D3934CF069409A7CC5AD4B120674DB`.

All disclosed lifecycle/provider/transport/probe-order and cleanup deviations
remain visible in the accepted report. Exact recovery followed every incomplete
attempt. The final canonical and installed adapter bytes match at
`A899A4B3CC572766EA21DAE1C4648452031780D73003D7288AA67539FBA28D45`;
temporary instruments, prompts, backups, mounts, candidates, archives, private
input, and test residue are absent. The strict broad-surface classification
remains **8 / 0 / 8**. No push, publication, tag, visibility change, checked-in
`dist/` replacement, or successor work order occurred.

### Post-pilot WO-PL-031 completed record

WO-PL-031 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-27 after a fresh
Reviewer returned **ACCEPT** on the final correction pass. Owner active minutes
are **NOT REPORTED** and no value is inferred.

The order corrected public-source and documentation truth around projected
commands, traversal-pattern confinement, portable protected-control-plane
aliases, malformed pointed-work-order read behavior, explicit project-root
authority, and boundary-aware private-path screening. The first fresh review
found three substantive gaps; the next found two precision issues; the final
review returned ACCEPT. Final governed-source Windows verification ran 549
tests successfully with two skips. Two independent 92-file public candidates
each passed 549 tests on Windows and native Ubuntu, passed projection/privacy,
license, and distribution gates, and were byte-identical at complete-ledger
SHA-256
`1BDC6C2B2D3A8A4B57186A3B65313B0691D4135D5ED07A80061395C77A1EC510`.
Their candidate-built archives were byte-identical at SHA-256
`068A50EF8366251955BE6A365DBB6024376BB6919208424D023CD1853378AEDE`.

The session ran on Codex outside the Claude Code hook, so no canary or
mechanical-enforcement claim is made and no denial record was added. The strict
broad-surface classification is **8 / 0 / 8**; no out-of-grant mutation
succeeded. All candidates, archives, private input, and test residue were
deleted and absence verified. Canonical and bundled adapter bytes match at
`DD29AF2A39D25E0270AD9ACC23EE912F81E39C674E1179759F4A3010C6A0C1A0`;
the installed private hook remains at its prior accepted digest and requires a
separately governed installation and birth test before the governed-source
release gate can be clean. No push, publication, tag, visibility change,
checked-in `dist/` replacement, or successor activation occurred.

### Post-pilot WO-PL-032 completed record

WO-PL-032 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-27 after the
fresh bounded Reviewer returned **ACCEPT/HIGH**. The active-minutes response
retained the supplied placeholder, so Owner active minutes are **NOT REPORTED**
and no value is inferred.

The order synchronized the protected installed hook to the accepted canonical
and bundled digest
`DD29AF2A39D25E0270AD9ACC23EE912F81E39C674E1179759F4A3010C6A0C1A0`.
Native Windows session `d3f0677c-02a1-4c98-9a7f-5c3d097c916e` and native
Ubuntu session `576d5d84-52a6-4328-b116-256ae47f420d` each produced four exact
ordered denials: one `write_target_out_of_grant` canary followed by three
`control_plane_protected` Writes. Every target remained unchanged. The final
305-record ledger preserves the original 296-record file byte-for-byte and is
106,288 bytes at SHA-256
`1BA6B5714859657D0F0DC9DAC004F108E59C4CB50FF8681E7025E4ECD84D8DAA`.

Record 297 preserves the first Windows instrument's diagnostic canary; records
298-305 are the accepted two-platform evidence. All nine are excluded probes
and change no pilot metric. Windows ran 549 tests successfully with two skips;
focused Windows and Ubuntu suites each passed 114 tests; active dispatch,
licensing, and whitespace checks passed. All launcher and read-before-write
diagnostics remain visible in the accepted report. Temporary backups, mount,
keeper, and canary were deleted or remained absent. The strict broad-surface
classification remains **8 / 0 / 8**, with zero successful protected-control-
plane mutation. Publication, push, tag, visibility change, and checked-in
`dist/` replacement remain unperformed. The authorized post-closeout dual
rebuild and fresh publication review remain next.

### Post-pilot WO-PL-033 completed record

WO-PL-033 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-28 and reported
active minutes **NOT REPORTED**.

The order rebuilt the public front door around Plumbline's distinctive
authority-and-enforcement layer, four-step loop, shortest honest first-value
route, adverse pilot economics, and Claude-Code-only mechanical boundary. It
replaced malformed SPDX-derived Creative Commons texts with official canonical
legal code, added executable recurrence and Python-version guards, and repaired
the methodology/project decision boundary in the public records.

Final governed-source and two independent public-candidate Windows suites each
passed 553 tests with two expected skips. Both candidates passed 553 tests on
native Ubuntu with three expected skips, were checker-clean at 92 files, and
matched complete-ledger SHA-256
`9D2A2E0E3B41CFEC6CA70F86CA51B85D1A9B93C8299219A8FC45ADC0DE4D3604`.
Their checker-clean archives matched SHA-256
`B9AD70B59EF1A3BBDD40BFCB266653E57C362F1051901443ED175B81F2C67C35`.

Records 306-309 came from a separately Owner-started VS Code Claude session
that attempted to relink the remote while WO-PL-033 was active. The wall denied
two shell channels, one broad read traversal, and one out-of-grant Edit before
mutation. The original 305 records remain a line-for-line exact prefix; no
denied mutation succeeded. The authorized coordinator later relinked `origin`
to the renamed private `plumbline-archive` remote.

The ignored reviewer ZIP, private screening input, both candidates and
archives, WSL mount/keeper, and temporary logs were deleted and verified
absent. No checked-in `dist/` replacement, tag, visibility change, or public
history transfer occurred. The new virgin public repository remains the target
for a fresh clean-history projection and separate Owner publication decision.

### Post-pilot WO-PL-039 completed record

WO-PL-039 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-29 and reported
active minutes **NOT REPORTED**.

The order corrected the unchanged-public-URL cache failure exposed after PR #3.
README now names the accepted wall-glyph banner through its SHA-256 prefix;
tests bind that suffix to the file bytes and require the retired URL to remain
absent. GitHub's live social-preview object is byte-identical to the accepted
source at SHA-256
`5200A1511A781CFE49BAF10177880CFC6E4E18EB8F9A55CA9E17AB4F9B35A312`.

CI action refs are exact-SHA pinned, weekly Dependabot maintenance is present,
and one stable `CI required` job represents the full matrix. The default branch
now requires a pull request, linear history, conversation resolution, squash-
only merge, and that strict status; deletion and non-fast-forward updates are
blocked. Supported vulnerability, dependency, scanning, push-protection, and
Actions restrictions are enabled. Plan-limited non-provider patterns and
validity checks remain disabled and are not represented as enabled.

Windows passed 657 tests with two expected skips. A native Ubuntu public
candidate passed 657 with three expected skips. Two independent 117-file
candidates were checker-clean and byte-identical at complete-ledger SHA-256
`7D215B5B432C3F147B06A175639A3FA234DF4C8B02C492C2ED8592A11D96CCA1`.
The first fresh review returned two record/process blockers; the private input
and candidates were immediately deleted and absence-verified, and the record
was corrected to distinguish static pre-acceptance CI proof from the mandatory
live-green public-PR gate. Corrected fresh re-review returned **ACCEPT**.

No denial was generated: the Codex implementation surface was outside the
installed Claude Code hook, and the strict classification remained **8 / 0 /
8**. No source commit, source push, public PR, release, tag, deployment, Pages,
domain, collaborator, visibility, secret, or `dist/` change occurred before
acceptance. The Owner authorized ordinary closeout/private commit and the
post-closeout issue #4 projection PR, with merge only after live `CI required`
passes; WO-PL-040 remains inactive.

### Post-pilot WO-PL-040 completed record

WO-PL-040 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-29 and reported
active minutes **NOT REPORTED**.

The order adds the standard-library `writwall start` bootstrap kernel. It
classifies actual lifecycle bytes before routing, makes the complete adoption
bundle local, records unratified intake, emits an exact next-agent prompt, and
separates repository and external-Operator packets. The sanitized reference
walkthrough preserves eight-domain DNS authority migration, DNS-before-mail
ordering, and separate historical-mail inventory, cleanup, and migration
without accessing any live provider, account, record, mailbox, credential,
server, website, or other project.

Three fresh reviews materially improved the result. The first found
contradictory ACTIVE-state, link/path, scenario, intake, and coverage defects.
The second verified those corrections and found non-atomic publication. The
final implementation uses a complete same-filesystem sibling stage and one
atomic rename with verified failure cleanup; fault injection proves no target
output or stage survives a caught publication failure. The final fresh review
returned **ACCEPT WITH NON-BLOCKING POLISH**.

The atomic-final suite passed 687 tests with two skips. Two independent
120-file projections were checker-clean and byte-identical at complete
projection-manifest SHA-256
`F08B7CB5ED00006B8F525BA210D525E556FA135084401AD72CBE6FC1513A8D1F`.
The original command-mediated archive/history fixture-read departure and the
identity-ledger grant omission remain disclosed under Owner-approved Amendment
1. The denial log remained 310 records and byte-unchanged. No external system,
production operation, release, tag, or successor implementation occurred
before acceptance.

### Post-pilot WO-WW-004 completed record

WO-WW-004 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-30 and reported
active minutes **NOT REPORTED**.

The order replaced the mandatory absolute-path private-pattern file with a
durable, project-specific OS-local profile initialized by `writwall start` and
resolved automatically by projection build/check commands. Normal output and
repository records contain only readiness and entry count; the explicit file
override remains for controlled compatibility. Temporary candidate cleanup
does not delete the durable profile.

The first fresh review returned four same-work-order findings: ancestor-link
redirection, concurrent lost updates, private values in command arguments, and
an absolute credential-rejection claim the implementation could not prove.
The correction rejects owned-component links/reparse entries, serializes
updates with a per-profile lock, uses hidden input or controlled stdin, rejects
common credential-shaped forms, and states the residual human boundary
plainly. Fresh re-review returned **ACCEPT**. No later-detected drift or RFI was
recorded.

Windows passed 715 tests with two skips; the focused suite passed 109 tests.
Native Ubuntu passed the eight-test privacy suite and created the profile at
mode `0600`; its two unavailable isolated-install tests required absent `pip`,
which was not installed. Two independent 131-file no-path candidates were
checker-clean and byte-identical, then deleted while the profile remained.
Codex was outside the installed Claude Code hook, so the strict classification
remained **8 / 0 / 8** and no denial was generated. Issue #10 proceeds through
the separately authorized post-closeout public PR; issue #11 remains separate.

### Post-pilot WO-WW-005 completed record

WO-WW-005 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-31 and reported
active minutes **NOT REPORTED**.

The order replaced the exact-SHA checkout v4 and setup-python v5 pins with the
official Node-24-native checkout `v7.0.1` and setup-python `v7.0.0` revisions.
Official release metadata and action manifests established the release tags,
commit SHAs, and `node24` runtime before dispatch. The 3-OS by 5-Python matrix,
read-only permission, full-history checkout, declared build-backend
provisioning, focused/full test split, and stable `CI required` job are
unchanged.

The exact-pin public-interface regression failed on the old checkout pin, then
passed after only the two workflow references changed. Three focused contract
tests and the complete 715-test Windows suite passed, with two skips. Fresh
review found no implementation defect and returned one report-only command-
evidence omission; corrected re-review returned **ACCEPT**. No denial, RFI,
same-work-order implementation drift, later-detected drift, dependency change,
or public mutation occurred before acceptance. The public issue #11 PR and its
live complete matrix remain the separately authorized closeout tail.

### Post-pilot WO-WW-006 completed record

WO-WW-006 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-31, accepted the
disclosed deviations, and reported active minutes **NOT REPORTED**.

The order adds a reusable no-network external-candidate gate for the day-zero
coordinator and proposes package version `0.9.0` as the first release that
contains `writwall start`. The gate builds a wheel, installs it into a
disposable environment, verifies installed version and help, runs a real
non-interactive architect intake, checks every promised handoff packet, and
proves the input candidate remained unchanged.

The first fresh review returned three material gaps: an install route pointed
to an unpublished tag, negative tests covered only a missing contract, and the
report omitted reproducible commands. The correction uses obtainable public
`main` until the tag exists, covers six material failure classes, and records
the exact command interfaces. A distinct final fresh review returned
**ACCEPT — HIGH confidence** with no actionable finding.

Final Windows and native Ubuntu suites each passed 723 tests, with two and
three expected skips respectively. Two independent 133-file Windows
projections passed the installed release and authoritative privacy/projection
gates and were byte-identical at manifest SHA-256
`19435E0CD341F1EB73E8F32932F72E07C616D6E88ED1352D16CA53829DA07A6D`;
the same final candidate passed both gates natively on Ubuntu. The denial log
remained 310 records and byte-unchanged. Temporary candidates, Ubuntu state,
sentinel, and mount were removed and proven absent.

Accepted deviations are the omitted test path in the initial grant, the
temporary-install grant contradiction, exact WSL residue and recovery, one
unnecessary pre-activation closed-record formatting read, one wrong-context
checker diagnostic, and the first-review correction cycle. No push, public
projection mutation, tag, GitHub release, deployment, or external media,
website, DNS, or mail operation occurred. Publication of `v0.9.0` remains a
separate unmade Owner decision.

### Post-pilot WO-WW-008 completed record

WO-WW-008 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-31 and reported
active minutes **NOT REPORTED**.

The order corrected one record-only publication blocker returned after
WO-WW-007: the State snapshot incorporated accepted WO-WW-007 while its Derived
sentence ended at WO-WW-006. The accepted implementation changed exactly that
endpoint and the two mechanically dependent State identity digests. Ordinary
closeout then advanced the final State endpoint through WO-WW-008 and re-derived
the same two State digest fields on the closeout bytes. Appending this completion
record also refreshed the retained LOG source digest; no identity classification,
context, or transform changed.

Identity, licensing, dispatch, and whitespace gates passed. Distribution
reported exactly the three expected live-work transients. The focused identity,
projection, distribution, dispatch, and licensing suite passed 462 tests with
two skips. Fresh review returned one report-only reproducibility correction;
corrected re-review returned **ACCEPT — HIGH confidence**. No denial, RFI,
product change, release change, public mutation, or external-project mutation
occurred before acceptance.

### Post-pilot WO-WW-009 completed record

WO-WW-009 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-08-31 and reported
active minutes **NOT REPORTED**.

The authorized `v0.9.1` release stopped before tagging when the coordinator
found that merged public bytes still declared package version `0.9.0`. The work
order added a mandatory intended-tag input to the external release gate and
requires canonical ASCII `vMAJOR.MINOR.PATCH` syntax plus exact equality with
candidate metadata before any build. Package metadata and current README,
adoption, start, publication, and contribution instructions now agree on
`v0.9.1`; truthful historical `v0.9.0` statements remain.

Four vertical RED/GREEN cycles covered mismatched, malformed, omitted, and
coherent release identity. Fresh review returned two bounded corrections: the
current State aggregate still described already-merged PR #17 as pending, and
Python's Unicode-aware `\d` admitted non-ASCII version digits. Corrected State
records merged PR #17 and closed issue #16; explicit ASCII `[0-9]` plus a new
public-interface regression rejects Arabic-Indic digits. Re-review returned
**ACCEPT — HIGH confidence**.

The affected Windows suite passed 44 tests; the complete Windows suite passed
729 with two expected skips; native Ubuntu passed 13 affected tests using only
process-local bundled build dependencies. Identity, licensing, active dispatch,
and whitespace passed; distribution reported exactly the three expected active
records. No tag, release, public issue #20 PR, pilot regeneration, adoption, or
external-project mutation occurred before acceptance.

### Post-pilot WO-WW-010 completed record

WO-WW-010 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-09-01 and reported
active minutes **NOT REPORTED**.

External Pilot A exposed public issue #22 when the generated pre-adoption
charter's ordinary no-pointer prohibition also caused a conforming provider to
refuse the exact Level 1 probes before hook dispatch. No forbidden mutation
succeeded and no adoption was claimed. The accepted correction adds one
temporary engine-visible bootstrap contract: ordinary no-pointer work remains
forbidden; only exact calls named by a durably Owner-ratified lifecycle may be
attempted solely so the wall can deny them; denial is the only valid outcome;
and any success or missing evidence stops adoption.

The first fresh review returned four blockers in contract-test strength, the
permanent-template negative assertion, record truth, and the missing final
governed-source Windows rerun. All were corrected. The same Reviewer returned
**ACCEPT — HIGH confidence** after independently confirming the corrected
contract tests, permanent-template exclusion, active dispatch, identity, three
expected release transients, and byte-identical bundle pairs.

Final governed-source Windows passed 735 tests with two skips; native Ubuntu
passed 735 with three. Two independent 136-file public candidates were
checker-clean and byte-identical at complete-ledger SHA-256
`D14629AE590B8E1DC556D428B0B06F6EC4EAAA07F4146E374654815C9BEA800F`.
Identity, licensing, dispatch, and whitespace passed. Disclosed deviations were
environment-only Python/Git diagnostics, test-mediated and one coordinator
read-boundary departure with no implementation impact, and detected/removed
bytecode residue. No commit, push, public projection mutation, release, or
external-project mutation occurred before acceptance.

### Post-pilot WO-WW-011 completed record

WO-WW-011 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-09-01 and reported
active minutes **NOT REPORTED**.

The first authorized post-WO-WW-010 public candidates were projection-clean and
byte-identical but correctly failed the existing intended-tag gate because
current metadata still declared `0.9.1`. Both candidates were deleted. A narrow
RED/GREEN release-identity order advanced package metadata, current install URLs,
publication/contribution commands, and executable tests to exact `0.9.2` /
`v0.9.2` while preserving historical `v0.9.0` and `v0.9.1` facts. The release
checker itself remained byte-unchanged.

Windows passed the complete 735-test suite with two skips; native Ubuntu passed
all 13 release-gate tests. Two independent 136-file candidates passed projection
and installed-release gates and were byte-identical at manifest SHA-256
`DAF33DFC8CFF973B2590B4A2D591C1A61596BF2AEFAB3EC2FC2762EEB11E0514`.
Fresh review returned one report-only distribution-evidence omission; after
correction and exact rerun, re-review returned **ACCEPT — HIGH confidence**.

One Ubuntu test trap left its temporary F: mount busy because the shell still
occupied the mounted working directory; a separate command from `/` removed the
mount and empty mountpoint and verified absence. No persistent environment,
repository, public, or external-project mutation occurred before acceptance.

### Post-pilot WO-WW-012 completed record

WO-WW-012 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-09-01 and reported
active minutes **NOT REPORTED**.

Fresh publication review of the otherwise valid post-WO-WW-011 candidates found
that the wheel's exhaustive installed-file map omitted the canonical bootstrap
charter addendum and that the release gate did not require it while claiming a
complete handoff. Both invalid candidates were deleted before this order began.
RED tests proved the missing required inventory, missing packaging entry, and
fail-open omission path. GREEN added the exact existing asset to the wheel map
and mandatory handoff inventory without broad discovery or another source copy.

Windows passed 738 tests with two skips; native Ubuntu passed all 16 release
tests. Two independent 136-file candidates passed projection and installed
`v0.9.2` release gates and were byte-identical at manifest SHA-256
`56F9B5F262A399642ECC098329312C0BA75A6B962884CDDEC4C2ECC89178E724`.
Fresh review returned one record-only wording correction; corrected re-review
returned **ACCEPT — HIGH confidence**. Temporary candidates, cache residue, and
the Ubuntu mount were deleted and verified absent. No public mutation, release,
tag, deployment, visibility change, or External Pilot A mutation occurred before
acceptance. The unrelated Owner deletion of `dist/plumbline-0.6.zip` (private governed-source reference, not present in this candidate) remained outside this
work order.

### Post-pilot WO-WW-013 completed record

WO-WW-013 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-09-01 and reported
active minutes **NOT REPORTED**.

The first post-WO-WW-012 projection pair failed closed because that completed
record named an omitted private distribution path without the exact same-line
private-source qualifier. Both candidates were deleted. The first correction
wrapped the qualifier onto the next physical line and remained RED; the next
pair exposed the same literal unnecessarily repeated in the newly issued Plan.
That pair was also deleted. The LOG qualifier was kept on the path's physical
line and the Plan was rewritten without the literal; no checker was weakened.

Two final 136-file candidates passed projection and installed `v0.9.2` release
gates and were byte-identical at manifest SHA-256
`0ED0848BDF05F56B9564D9904B3A4711DEEC15BCFA918F928B57C5C13DF7B07B`.
The unchanged governed-source release suite passed 16/16. Identity, licensing,
dispatch, and whitespace passed. Fresh review returned **ACCEPT — HIGH
confidence**. All temporary candidates were deleted and verified absent. No
product, checker, public, release, tag, deployment, visibility, or External
Pilot A mutation occurred before acceptance.

### Post-pilot WO-WW-014 completed record

WO-WW-014 is post-pilot and does not add an eleventh metrics row or change the
accepted ten-order aggregate. The Owner accepted it on 2026-09-01 and reported
active minutes **NOT REPORTED**.

Fresh final publication review blocked an otherwise valid `v0.9.2` candidate
pair because an earlier current-use Plan section retained a concrete sibling
project path. The Plan reference is now host-neutral, and the independent
projection checker rejects concrete Windows, macOS, Linux-home, and mounted-drive
paths in current public records without echoing their values. Canonical path
placeholders and historical evidence remain permitted.

Windows passed 743 tests with two skips; the Windows and Ubuntu projection suites
each passed 68 tests. Two 136-file candidates passed projection and installed
`v0.9.2` release gates and were byte-identical at manifest SHA-256
`6B0B72CDBA64CDA7BA684BCFAE7139AE185C965BBE5FCE0066B22C28DFC744E5`.
Fresh review initially blocked on missing replay commands. The source gate then
rejected the first corrected record for embedding concrete local command paths;
environment-derived commands resolved both findings, and corrected re-review
returned **ACCEPT — HIGH confidence**. The order's candidates were deleted. One
inaccessible invalid candidate from the preceding publication review remains
isolated under the OS temporary area after ordinary and native-Ubuntu cleanup
were denied by its ACL; it contains no accepted release bytes or private input.
No public mutation, release, tag, deployment, visibility change, or External
Pilot A mutation occurred before acceptance.

---

## Column definitions

**9.2.1 Denials.** One mutation attempt rejected by the enforcement provider and attributable to the active work order. Count raw denial events; identify surface and mutation channel. Birth-test and regression-test probes are excluded from pilot totals and recorded separately in `LOG-denials-probes.md`. Every **successful** out-of-grant mutation is recorded as a deviation in Notes. Predicted count for successes: zero.

**9.2.2 RFIs.** Each distinct numbered RFI first opened during the work order. Replies and updates to an existing RFI do not add counts.

**9.2.3 Drift.** One independently remediable mismatch between delivered repository state and the active work order, ratified plan, or routed requirement. *Same-WO* means detected after implementation begins and before the Owner accepts and closes that work order. *Later* means first discovered after closure; a later instance is attributed to **both** the discovering work order and the earlier accepted work order that introduced it, so the same instance appears twice in this column across two rows.

**9.2.4 Recovery cost.** Three sub-counts. A rework cycle begins when the Reviewer or Owner returns an implementation for correction and ends with a new implementation report and review; the initial implementation/review pass is **not** a rework cycle. Also record additional agent sessions required, and closed historical artifacts deliberately retrieved to reconstruct intent. That third figure is the pilot's archaeology-cost indicator and is the one that tests the "one revert, not archaeology" prediction.

**9.2.5 Live corpus and routing.** Measured **at work-order activation**. Count each distinct document reachable through Tier-1 injection, deterministic Tier-2 routing, open transactional-record supply, or configured search and retrieval paths — each document once — and record document count and whitespace-delimited word count. Exclude source code and binary assets unless explicitly declared as routed context. Exclude `governance/history/`, `governance/archive/`, root `archive/`, `bootstrap/`, and closed reports unless the active work order explicitly authorizes retrieval. A routing gap is one declared governed path or subsystem with no valid deterministic route at activation. Orphan Tier-2 documents, those no route points to, are counted separately.

**9.2.6 Grant enforcement.** Enumerate every declared capability surface for the work order, including project-specific surfaces. Record total declared, mechanically enforced, and unenforced-by-declaration, with the mechanism and covered mutation channels for each in Notes. **A partially covered surface is unenforced.** A surface is mechanically enforced only when every mutation channel capable of reaching it is covered *and* the installation has passed its birth test.

**9.2.7 Owner reading load.** Whitespace-delimited words of **mandatory** Owner reading. Ordinary disposition: C.1 through C.6 of the Owner brief, excluding reviewer-only notes. Ceiling **500 words per work order**. On escalation under 7.6.3, count the brief and the exact linked evidence separately; the 500-word ceiling does not apply to escalated evidence, but the triggering 7.6.3 condition is recorded in Notes. Material the Owner opens voluntarily is not counted.

**9.2.8 Experimental instruments.** No instrument is qualified at adoption; the pilot gate is Reviewer-only controlled inference. Record **`N/A`, not zero**, while no instrument runs. If one is introduced, a comparison is one independently adjudicable claim evaluated by both instrument and Reviewer; count disagreements and record the Owner's resolution and which assessment was sustained.

---

## Predictions being tested (9.2)

| Clause | Prediction |
|---|---|
| 9.2.1 | Violations occur but are blocked; the count is visible and the damage is zero |
| 9.2.2 | Ambiguities halt work early instead of being improvised through |
| 9.2.3 | Detection latency collapses to the current work order |
| 9.2.4 | One rework cycle, not archaeology |
| 9.2.5 | Live corpus flat over time while history grows; gaps trend to zero and each is a logged RFI |
| 9.2.6 | Reported per work order; the gap is itself a finding about available tooling |
| 9.2.7 | Below the 500-word ceiling by default; escalations rare and always tied to a 7.6.3 condition |
| 9.2.8 | Logged with outcome; the record of who was right feeds a later qualification event under 8.4.4 |

If the predictions fail, this log says which control failed and how. That is a finding (9.3.2), and it is stated publicly if the results are published.
