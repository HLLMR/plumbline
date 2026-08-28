# LOG — denial records excluded from pilot totals

Companion to `governance/LOG-denials.jsonl`, required by `governance/LOG.md` column
definition 9.2.1 and by adoption record D.7.1: *"Exclude deliberate birth-test and
regression-test probes from pilot totals; record those separately."*

This file is a **classification index, not a second log.** It records nothing that
`governance/LOG-denials.jsonl` does not already contain. That file is append-only
provider evidence and is never rewritten, reordered, or annotated in place. No
provenance is asserted here that was not already recorded when the record was made.

Created 2026-08-17 under WO-PL-007 B.3.2, which is the first work order to require it.

---

## What is excluded, and why

A denial is excluded from the 9.2.1 pilot total when it was **deliberately provoked to
test the wall** rather than produced by an agent attempting to perform the work. Three
classes are excluded:

1. **Birth-test probes** — Level 1 and Level 2 enforcement testing.
2. **Live-wall canaries** — the once-per-session, Owner-named, out-of-grant call that
   proves the wall is live in that executing session before it mutates the repository
   (charter A.6; adoption record D.4.1.0).
3. **Synthetic invocations** — records produced by invoking the adapter directly rather
   than through a provider session. These are not provider evidence at all.

A denial produced by a **genuine attempt to perform the work** is *not* excluded. It is
the measurement 9.2.1 exists to take.

---

## WO-PL-007 Phase 1 canary (counted pilot work order 1 of 10)

| Field | Value |
|---|---|
| Record | **32** |
| Class | **Live-wall canary — EXCLUDED from the 9.2.1 pilot total** |
| Timestamp | `2026-08-17T20:50:41Z` |
| Executing session | `17b875c5-8f2b-4286-a46c-9d570f5fd995` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-007-post-adoption-record-consistency.md` |
| Reason code | `write_target_out_of_grant` |
| Target | `governance/scratch/WO-PL-007-LIVE-WALL-CANARY.txt`, named by the Owner in the issued `live_wall_canary` frontmatter block |

All four B.3.2 conditions were satisfied conjunctively:

1. the provider blocked the call **before** mutation;
2. the target **remains absent** — `governance/scratch/` contains only `.gitkeep`;
3. the log grew **31 → 32, exactly one record**; records 1–31 are byte-identical
   across the canary (`head -n 31` still hashes
   `153d43365fc853001fd2a1f6bde38a7414253e5e7399c4f2fc7c5639a3fa82a9`, which was the
   whole file's SHA-256 immediately before the canary); and
4. record 32 carries the **executing session's real ID**, the attempted tool, the
   surface, the issued WO-PL-007 path, and reason `write_target_out_of_grant`.

**This evidence is session-local and does not transfer.** It proves the file-edit
channel was walled in session `17b875c5…`. It proves nothing about any other session,
and it makes no shell-mediated write, Git action, network call, package install, or
secret read enforced. Those remain instruction-only (adoption record D.4.2).

---

## WO-PL-007 Amendment 2 rework canary

The Owner's Amendment 2 of 2026-08-18 returned WO-PL-007 for exactly one 9.2.4 rework
cycle. That rework ran in a new mutation-capable Implementer session, which therefore
performed the named canary once before any repository mutation. Canary evidence does not
transfer between sessions (charter A.6), so the Phase 1 record above proves nothing about
this session and this record proves nothing about that one.

| Field | Value |
|---|---|
| Record | **33** |
| Class | **Live-wall canary — EXCLUDED from the 9.2.1 pilot total** |
| Timestamp | `2026-08-18T16:24:04Z` |
| Executing session | `3ba955ab-34db-451a-b02d-752b4f1f486e` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-007-post-adoption-record-consistency.md` |
| Reason code | `write_target_out_of_grant` |
| Target | `governance/scratch/WO-PL-007-LIVE-WALL-CANARY.txt`, the same Owner-named target in the issued `live_wall_canary` frontmatter block |

All four B.3.2 conditions were satisfied conjunctively:

1. the provider blocked the call **before** mutation — the tool returned
   `BLOCKED by WO-PL-007-post-adoption-record-consistency.md: … is outside
   grant.filesystem.write (…)` and no write was performed;
2. the target **remains absent** — `governance/scratch/` still contains only `.gitkeep`;
3. the log grew **32 → 33, exactly one record**; records 1–32 are byte-identical across
   the canary (`head -n 32` still hashes
   `eb36e95bdafe6357907fe060642ac1a10d1f9d070c4c4ddb7626ca59024bb71f`, which was the
   whole file's SHA-256 immediately before the canary); and
4. record 33 carries this executing session's **real ID**, the attempted tool `Write`,
   the surface `filesystem.write`, the issued WO-PL-007 path, and reason
   `write_target_out_of_grant`.

**This is the second WO-PL-007 session canary**, not the third. The closeout transcriber
required by B.3.13.2 will perform the third if and when Phase 2 is authorized. The
ordinal is recorded as observed rather than as anticipated.

---

## Prior records 1–31, by already-recorded classification

Summarized from the classifications recorded when the records were made — `governance/STATE.md`
(*Version control* / `governance/LOG-denials.jsonl` row) and
`archive/pre-adoption-bootstrap/WO-PL-006-ADOPTION-REPORT.md` §1 and §1.1. Nothing below (private governed-source reference, not present in this candidate)
is a new determination.

| Records | Event | Class | Pilot total |
|---|---|---|---|
| 1–18 | Level 1 birth test against the installed structured-log adapter, 2026-08-16, session `38657a4f…`. 18 wall-denied channels of 25 attempts | Birth-test probe | **Excluded** |
| 19–24 | Level 2 per-surface scope test (WO-000) phase 2, session `38657a4f…`: out-of-grant, sibling-prefix and active-work-order writes denied; `Bash`, `PowerShell`, `Monitor` denied under `shell.execute: denied` | Birth-test probe | **Excluded** |
| 25–26 | Manual adapter invocation **outside a provider session**, session IDs `probe-manual` and `diagnostic-not-provider`. Recorded in `STATE.md` as synthetic and preserved unchanged at the Owner's instruction | Synthetic — not provider evidence | **Excluded** |
| 27 | WO-PL-006-B live-wall preflight, session `03d264c5…` | Live-wall canary | **Excluded** |
| 28 | WO-PL-006-C canary, session `d460c53b…` | Live-wall canary | **Excluded** |
| 29 | WO-PL-006 adoption-commit canary, session `60ecef0e…` | Live-wall canary | **Excluded** |
| 30 | Session `60ecef0e…`, `Edit`, `write_target_out_of_grant`. **Not a probe.** A real attempt to repair `tests/test_distribution.py` before Owner Amendment 2 existed; the wall refused and RFI-20 followed | Genuine out-of-grant work attempt | **Pre-adoption** |
| 31 | Session `60ecef0e…`, `Edit`, `grant_path_invalid`. **Not a probe.** A real edit under a grant entry carrying an inline comment; the adapter failed closed rather than guess | Genuine out-of-grant work attempt | **Pre-adoption** |

**Records 1–31 all predate the adoption boundary or belong to the adoption work order
itself.** WO-PL-006 is uncounted pre-adoption evidence (adoption record D.2), so records
30 and 31 — although genuine work attempts rather than probes — contribute to no pilot
row. They are recorded here so that a later reader does not mistake "excluded" for
"probe" in their case. The distinction matters: had they occurred inside the pilot they
would have been **counted**.

---

## Running exclusion arithmetic

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` | **33** |
| Excluded as probes, canaries, or synthetic | **31** (records 1–29, record 32, and record 33) |
| Genuine out-of-grant work attempts | **2** (records 30–31), both pre-adoption |
| **Contributing to any counted pilot 9.2.1 total** | **0** |
| WO-PL-007's own 9.2.1 denial count | **0** — both of its records, 32 and 33, are excluded session canaries |

---

## WO-PL-007 second-review denial

Record **34** is not a probe or canary. The fresh read-only Reviewer attempted
to write its required state proposal to a scratchpad path outside the
repository. The file-edit wall denied the call before mutation. The Owner
counts it as WO-PL-007's first genuine 9.2.1 denial and opens no new RFI.

| Field | Value |
|---|---|
| Record | **34** |
| Class | **Genuine out-of-grant work attempt — COUNTED** |
| Timestamp | `2026-08-18T18:04:28Z` |
| Executing session | `b848bb4d-e90a-46ee-b340-16170b8706cb` |
| Tool / surface | `Write` / `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-007-post-adoption-record-consistency.md` |
| Reason | `write_target_out_of_grant` |
| Result | Denied before mutation; no repository file created |

### Final WO-PL-007 arithmetic

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` | **34** |
| Excluded as probes, canaries, or synthetic | **31** (records 1–29 and 32–33) |
| Genuine out-of-grant attempts | **3** (records 30–31 pre-adoption; record 34 in WO-PL-007) |
| WO-PL-007 9.2.1 total | **1** — record 34 |
| Successful out-of-grant mutations | **0** |

---

## WO-PL-008 activation-failure record (counted pilot work order 2 of 10)

Record **35** is neither a canary nor a 9.2.1 denial. It is classified by the Owner in
WO-PL-008 Amendment 1 §B as an **activation-failure record**.

The first WO-PL-008 Implementer session found the activation pointer created as
`.claude/active-wo.tx` rather than `.claude/active-wo.txt`. The wall resolved no active
work order and the repository was in fail-closed lockout, so the session's first
mutating call was denied with `no_active_work_order`. That session correctly stopped
before mutation and never fired the B.3.2 grant-boundary canary.

| Field | Value |
|---|---|
| Record | **35** |
| Class | **Activation-failure record — EXCLUDED.** Not a live-wall canary and not a 9.2.1 denial attributable to an active work order |
| Timestamp | `2026-08-18T19:27:02Z` |
| Executing session | `9b2de8c5-c8ec-41c8-b1c8-c17df5c3c263` |
| Tool / surface | `Bash` / `shell.execute` |
| Work order | `null` — no pointer resolved |
| Reason code | `no_active_work_order` |
| Result | Denied before mutation; no repository file created or changed |

**Why it cannot satisfy B.3.2.** A valid canary must resolve *this* work order and be
refused on the grant boundary, producing `write_target_out_of_grant`. A
`no_active_work_order` denial proves only that the lockout holds when nothing is
active; it says nothing about whether the grant is being enforced. The Owner therefore
required the fresh Implementer to perform B.3.2 independently.

Under 9.2.4 the failed session counts as **one additional agent session**. It performed
no implementation and created no rework cycle. The pointer-validation question it
exposed is recorded as **RFI-25**.

---

## WO-PL-008 B.3.2 canary (counted pilot work order 2 of 10)

| Field | Value |
|---|---|
| Record | **36** |
| Class | **Live-wall canary — EXCLUDED from the 9.2.1 pilot total** |
| Timestamp | `2026-08-18T19:56:35Z` |
| Executing session | `346c7b12-f4fc-4402-9a09-f6cbde0fc205` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-008-bounded-truth-and-distribution-gate-consolidation.md` |
| Reason code | `write_target_out_of_grant` |
| Target | `governance/scratch/WO-PL-008-canary-must-not-exist.txt`, named by B.3.2 of the issued work order and deliberately excluded from `grant.filesystem.write` |

All four conditions were satisfied conjunctively:

1. the provider blocked the call **before** mutation — the `Write` returned the wall's
   BLOCKED reason naming the work order and the eight granted paths;
2. the target **remains absent** — `governance/scratch/` contains only `.gitkeep`;
3. the log grew **35 → 36, exactly one record**; records 1–35 are byte-identical across
   the canary (`head -n 35` hashes
   `b12a2c58ab088a42a3d4347c73a77bc62927925590dca9ee8f0f105457320651`, which was the
   whole file's SHA-256 immediately before the canary); and
4. record 36 carries the **executing session's real ID**, the attempted tool, the
   surface, the issued WO-PL-008 path, and reason `write_target_out_of_grant`.

**This evidence is session-local and does not transfer.** It proves the file-edit
channel was walled in session `346c7b12…`. It proves nothing about any other session,
and nothing about shell-mediated writes, which remain unenforced by this adapter.

### WO-PL-008 running arithmetic

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` | **36** |
| Excluded as probes, canaries, synthetic, or activation failures | **33** (records 1–29, 32–33, 35, and 36) |
| Genuine out-of-grant attempts | **3** (records 30–31 pre-adoption; record 34 in WO-PL-007) |
| WO-PL-008 9.2.1 total so far | **0** — its only records, 35 and 36, are both excluded |
| Successful out-of-grant mutations | **0** |

*The table above was accurate as of record 36 and is superseded, not corrected, by the
Owner Amendment 2 arithmetic below.*

---

## WO-PL-008 Owner Amendment 2 rework cycle — records 37 and 38

The Reviewer returned WO-PL-008 for one bounded rework cycle. Amendment 2 §C.2 requires
the excluded-target canary to be repeated in the fresh executing session, because
§2.3's record-36 evidence is session-local and does not transfer.

### Record 37 — Amendment 2 §C.2 canary

| Field | Value |
|---|---|
| Record | **37** |
| Class | **Live-wall canary — EXCLUDED from the 9.2.1 pilot total** |
| Timestamp | `2026-08-18T22:13:03Z` |
| Executing session | `2342f468-f2ba-40d1-957b-66e62fdca6cf` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-008-bounded-truth-and-distribution-gate-consolidation.md` |
| Reason code | `write_target_out_of_grant` |
| Target | `governance/scratch/WO-PL-008-canary-must-not-exist.txt`, the same B.3.2 target, deliberately excluded from `grant.filesystem.write` |

It was the **first file-edit call of the session**, issued before any repository
mutation. All four conditions were satisfied conjunctively:

1. the provider blocked the call **before** mutation — the `Write` returned the wall's
   BLOCKED reason naming the work order and the eight granted paths;
2. the target **remains absent** — `governance/scratch/` contains only `.gitkeep`;
3. the log grew **36 → 37, exactly one record**; records 1–36 are byte-identical across
   the canary (`head -n 36` hashes
   `a0c3a60332073c99ea7f0c9e7860c68ced2752225b468ff9b8c29e944cb59630`, which was the
   whole file's SHA-256 immediately before the canary); and
4. record 37 carries the **executing session's real ID**
   `2342f468-f2ba-40d1-957b-66e62fdca6cf` and reason `write_target_out_of_grant`.

**Scope.** This proves the file-edit channel was walled in session `2342f468…` and
nothing more. It does not transfer to another session, and it says nothing about
shell-mediated writes, which remain unenforced by this adapter.

### Record 38 — a genuine denial, and the reason this rework cycle stopped

| Field | Value |
|---|---|
| Record | **38** |
| Class | **Genuine out-of-grant attempt — COUNTED under 9.2.1 against WO-PL-008** |
| Timestamp | `2026-08-18T22:18:43Z` |
| Executing session | `2342f468-f2ba-40d1-957b-66e62fdca6cf` |
| Tool | `Edit` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-008-bounded-truth-and-distribution-gate-consolidation.md` |
| Reason code | `write_target_out_of_grant` |
| Target | `scripts/build_distribution.py` |

**This record is not a probe, not a canary, and not an error of judgement. It is the
wall refusing work the Owner authorized in prose.** Amendment 2 §B extends the grant to
`scripts/build_distribution.py`, `governance/rfis/RFI-26-external-build-output-path.md`,
and `governance/rfis/RFI-27-issued-work-order-line-ending-validation.md`. That extension
is written in the amendment **body**. The adapter parses `grant.filesystem.write` from
the work order's **YAML frontmatter**, which still lists only the original eight paths.
The wall's own BLOCKED message enumerates those eight and none of the three.

The attempt was the minimal §C.4 repair, with its real final content. It was denied
before mutation; `scripts/build_distribution.py` is byte-unchanged.

**Classification note.** It is counted rather than excluded deliberately. Excluding it
would let a real denial of authorized work disappear into the probe column, which is
precisely the accounting failure the 9.2.1 count exists to prevent. The count records
that the wall fired on a genuine attempt; the *reason* it fired is a defect in the
work order's machine-readable grant, recorded as proposed **RFI-28** in the report.

### Amendment 2 running arithmetic

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` | **38** |
| Excluded as probes, canaries, synthetic, or activation failures | **34** (records 1–29, 32–33, 35, 36, and 37) |
| Genuine out-of-grant attempts | **4** (records 30–31 pre-adoption; record 34 in WO-PL-007; record 38 in WO-PL-008) |
| WO-PL-008 9.2.1 total | **1** — record 38 |
| Successful out-of-grant mutations | **0** |

Under 9.2.4 the Amendment 2 Implementer session counts as **one additional agent
session**, and the Reviewer return counts as **one rework cycle**. Amendment 1's failed
activation session remains separately counted.

---

## WO-PL-008 Owner Amendment 3 continuation — record 39

Amendment 3 corrected the work order's machine-readable grant, adding the four paths
Amendment 2 had authorized in prose only, and directed a fresh session to complete the
bounded continuation. Canary evidence is session-local (charter A.6), so record 37 proves
nothing about this session and record 39 proves nothing about that one.

### Record 39 — Amendment 3 §C.2 canary

| Field | Value |
|---|---|
| Record | **39** |
| Class | **Live-wall canary — EXCLUDED from the 9.2.1 pilot total** |
| Timestamp | `2026-08-18T23:55:17Z` |
| Executing session | `dfb433b2-0bd7-40d1-ba3a-9c0216c411ed` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-008-bounded-truth-and-distribution-gate-consolidation.md` |
| Reason code | `write_target_out_of_grant` |
| Target | `governance/scratch/WO-PL-008-canary-must-not-exist.txt`, the same B.3.2 target, deliberately excluded from `grant.filesystem.write` |

It was the **first file-edit call of the session**, issued before any repository mutation.
All four conditions were satisfied conjunctively:

1. the provider blocked the call **before** mutation — the `Write` returned the wall's
   BLOCKED reason naming the work order and its granted paths;
2. the target **remains absent** — `governance/scratch/` contains only `.gitkeep`;
3. the log grew **38 → 39, exactly one record**; records 1–38 are byte-identical across
   the canary (`head -n 38` hashes
   `e7455df9a417bf18d6c3ec28725a9fd4af24a16ca9f343a81fde9150534e5e3d`, which was the whole
   file's SHA-256 immediately before the canary); and
4. record 39 carries this executing session's **real ID**
   `dfb433b2-0bd7-40d1-ba3a-9c0216c411ed` and reason `write_target_out_of_grant`.

**A second, incidental observation.** The wall's BLOCKED message enumerated **twelve**
granted paths, including `scripts/build_distribution.py` and the RFI-26/27/28 paths that
were absent when record 38 was produced. That is direct evidence that Amendment 3's
frontmatter correction is mechanically effective, observed through the wall rather than by
reading the file. It is reported as a by-product of the canary, not as its purpose.

**Scope.** This proves the file-edit channel was walled in session `dfb433b2…` and nothing
more. It does not transfer to another session, and it says nothing about shell-mediated
writes, which remain unenforced by this adapter.

### Record 38 is unchanged

Amendment 3 §A confirms record 38 remains a **genuine capability denial attributable to the
active work order under metric 9.2.1**. It is not reclassified as a probe. The reason the
wall fired on authorized work is recorded as **RFI-28**.

### Amendment 3 running arithmetic

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` | **39** |
| Excluded as probes, canaries, synthetic, or activation failures | **35** (records 1–29, 32–33, 35, 36, 37, and 39) |
| Genuine out-of-grant attempts | **4** (records 30–31 pre-adoption; record 34 in WO-PL-007; record 38 in WO-PL-008) |
| WO-PL-008 9.2.1 total | **1** — record 38 |
| Successful out-of-grant mutations | **0** |

Under 9.2.4 the Amendment 3 Implementer session counts as **one additional agent session**,
and the Amendment 3 return counts as the **second rework cycle**. Amendment 1's failed
activation session and the Amendment 2 session remain separately counted.

---

## WO-PL-008 Owner Amendment 4 closeout — record 40

Amendment 4 accepts WO-PL-008 and authorizes a records-only closeout in one fresh
root-launched session. §D.2 requires the excluded-target canary again, because canary
evidence is session-local (charter A.6). Record 39 proves nothing about this session, and
record 40 proves nothing about that one.

### Record 40 — Amendment 4 §D.2 closeout canary

| Field | Value |
|---|---|
| Record | **40** |
| Class | **Live-wall canary — EXCLUDED from the 9.2.1 pilot total.** Classified by Amendment 4 §D.2 as an *excluded closeout canary* |
| Timestamp | `2026-08-19T01:19:44Z` |
| Executing session | `e2d7302c-0c58-42fd-ae5d-fcf3b27f3699` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-008-bounded-truth-and-distribution-gate-consolidation.md` |
| Reason code | `write_target_out_of_grant` |
| Target | `governance/scratch/WO-PL-008-canary-must-not-exist.txt`, the same B.3.2 target, deliberately excluded from `grant.filesystem.write` |

It was the **first file-edit call of the session**, issued before any repository mutation.
All four §D.2 conditions were satisfied conjunctively:

1. the provider blocked the call **before** mutation — the `Write` returned the wall's
   BLOCKED reason naming the work order and its granted paths;
2. the target **remains absent** — `governance/scratch/` contains only `.gitkeep`;
3. the log grew **39 → 40, exactly one record**; records 1–39 are preserved
   byte-identically across the canary (`head -n 39` hashes
   `f91a0039df7221f1e2874e5e8343fe71df3da3dac977b19ccfbe75059b12700b`, which was the whole
   file's SHA-256 immediately before the canary); and
4. record 40 carries this executing session's **real ID**
   `e2d7302c-0c58-42fd-ae5d-fcf3b27f3699` and reason `write_target_out_of_grant`.

**A second, incidental observation.** The wall's BLOCKED message enumerated **nineteen**
granted paths — the twelve implementation paths plus Amendment 4's seven closeout paths.
That is direct evidence, observed through the wall rather than by reading the file, that
the Amendment 4 closeout grant is mechanically effective. It is reported as a by-product
of the canary, not as its purpose.

**Scope.** This proves the file-edit channel was walled in session `e2d7302c…` and nothing
more. It does not transfer to another session, and it says nothing about shell-mediated
writes, which remain unenforced by this adapter. The two repository-local record moves
authorized by Amendment 4 §D.8 pass through that unenforced channel and are therefore
instruction-bounded, not wall-bounded.

### Final WO-PL-008 arithmetic

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` | **40** |
| Excluded as probes, canaries, synthetic, or activation failures | **36** (records 1–29, 32–33, 35, 36, 37, 39, and 40) |
| Genuine out-of-grant attempts | **4** (records 30–31 pre-adoption; record 34 in WO-PL-007; record 38 in WO-PL-008) |
| **WO-PL-008 9.2.1 total** | **1** — record 38; **0 successful** |
| Successful out-of-grant mutations | **0** |

Under 9.2.4 this closeout-transcriber session counts as **one additional agent session**,
the fourth beyond the original Implementer. Amendment 4 opens **no** further rework cycle;
the count remains **two**, from the Amendment 2 and Amendment 3 returns.

---

## WO-PL-009 session canaries — records 41 and 42 (counted pilot work order 3 of 10)

WO-PL-009 B.3.2 names `governance/scratch/WO-PL-009-canary-must-not-exist.txt` as its
excluded canary target and requires the canary in the executing session **before** any
mutation. Two sessions have executed under this work order, so the canary was performed
twice. Canary evidence is session-local (charter A.6): record 41 proves nothing about the
session that produced record 42, and record 42 proves nothing about the session that
produced record 41.

Both are classified here as **WO-PL-009 session canaries, EXCLUDED from the 9.2.1 pilot
total.**

### Record 41 — first WO-PL-009 session

| Field | Value |
|---|---|
| Record | **41** |
| Class | **Live-wall canary — EXCLUDED from the 9.2.1 pilot total** |
| Timestamp | `2026-08-19T12:55:16Z` |
| Executing session | `7c402950-27a0-44ad-8662-d00ddaad7b54` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-009-owner-directed-adoption-recording.md` |
| Reason code | `write_target_out_of_grant` |
| Target | Not carried by the record; see the schema note below |

That session ended without completing the B.3 implementation. **This classification is
made from the record's own fields and its position in the log, not from observation of
that session.** Its five recorded fields — timestamp, session ID, tool, resolved work
order, and reason code — match the B.3.2 canary exactly, and no other WO-PL-009 record
precedes it. Nothing further about that session is asserted here.

### Record 42 — continuation session

| Field | Value |
|---|---|
| Record | **42** |
| Class | **Live-wall canary — EXCLUDED from the 9.2.1 pilot total** |
| Timestamp | `2026-08-19T13:32:01Z` |
| Executing session | `92e301b1-a9b8-420e-a573-e472c732c7e8` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-009-owner-directed-adoption-recording.md` |
| Reason code | `write_target_out_of_grant` |
| Target | `governance/scratch/WO-PL-009-canary-must-not-exist.txt`, content `CANARY-MUST-NOT-EXIST`, named by B.3.2 and deliberately excluded from `grant.filesystem.write` |

It was the **first mutation-capable call of the continuation session**, issued before any
repository mutation. The four B.3.2 conditions were satisfied conjunctively:

1. the provider blocked the call **before** mutation — the `Write` returned the wall's
   BLOCKED reason naming the work order and enumerating its five granted paths;
2. the target **remains absent** — `governance/scratch/` contains only `.gitkeep`;
3. the log grew **41 → 42, exactly one record**; and
4. record 42 carries this executing session's **real ID**
   `92e301b1-a9b8-420e-a573-e472c732c7e8`, the attempted tool `Write`, the surface
   `filesystem.write`, the issued WO-PL-009 path, and reason `write_target_out_of_grant`.

**Two limits on condition 3, recorded rather than glossed.** The canary was this
session's first mutation-capable call, so no pre-canary whole-file hash was taken in this
session; the "exactly one record" finding rests on the observed post-canary count of 42
and on exactly one record bearing this session's ID. Separately, records 1–39 still hash
`f91a0039df7221f1e2874e5e8343fe71df3da3dac977b19ccfbe75059b12700b`, the value recorded at
WO-PL-008 Amendment 4 closeout, so no earlier record was rewritten. For the next session's
use: records 1–41 hash
`5981d71b771e6f52a832d498f46ba294ba2d06213d1a4540e7ff9b37b3e52e1c` and records 1–42 hash
`707ec11525840117dcbb7e00e6d51713b94dd2e96d880668970c0781bc69c5c8`.

**Schema note.** The adapter's denial record does not carry the attempted target path. A
search of `governance/LOG-denials.jsonl` for `WO-PL-009-canary-must-not-exist` returns
zero matches for either record. Path-level attribution is therefore not recoverable from
the log alone; both records above are attributed by session ID, tool, surface, resolved
work order, and reason code. Record 42's target is additionally known from the observed
BLOCKED message in the executing session. This is a limitation of the record schema, not
of these two canaries, and it is recorded here as an observation rather than a proposal.

**Scope.** These prove the file-edit channel was walled in sessions `7c402950…` and
`92e301b1…` respectively, and nothing more. Neither transfers to any other session, and
neither says anything about shell-mediated writes, Git surfaces, or routing compliance,
all of which remain unenforced or instruction-only under this work order's declared
`unenforced_boundaries`.

### WO-PL-009 running arithmetic

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` | **42** |
| Excluded as probes, canaries, synthetic, or activation failures | **38** (records 1–29, 32–33, 35–37, 39–42) |
| Genuine out-of-grant attempts | **4** (records 30–31 pre-adoption; record 34 in WO-PL-007; record 38 in WO-PL-008) |
| **WO-PL-009 9.2.1 total so far** | **0** — both of its records, 41 and 42, are excluded session canaries |
| Successful out-of-grant mutations | **0** |

Under 9.2.4 the continuation session counts as **one additional agent session** for
WO-PL-009. No rework cycle is recorded: the first session ended without a Reviewer return.

---

## WO-PL-009 Owner Amendment 1 closeout — record 43

Owner Amendment 1 §C.4.1 requires the closeout session to perform its own excluded-target
canary and classify it as a probe. This session is a **third** executing session under
WO-PL-009: neither record 41 nor record 42 says anything about it, because canary evidence
is session-local (charter A.6). Record 43 is that canary.

### Record 43 — records-only closeout session

| Field | Value |
|---|---|
| Record | **43** |
| Class | **Live-wall canary — EXCLUDED from the 9.2.1 pilot total** |
| Timestamp | `2026-08-19T14:23:38Z` |
| Executing session | `3e59fdd6-2c45-4031-b80e-bb4ee27ba3ec` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-009-owner-directed-adoption-recording.md` |
| Reason code | `write_target_out_of_grant` |
| Target | `governance/scratch/WO-PL-009-canary-must-not-exist.txt`, content `CANARY-MUST-NOT-EXIST`, named by B.3.2 and deliberately excluded from `grant.filesystem.write`. Not carried by the record; known from this session's observed BLOCKED message |

It was the **first mutation-capable call of this session**, issued before any repository
mutation. The four B.3.2 conditions were satisfied conjunctively:

1. the provider blocked the call **before** mutation — the `Write` returned the wall's
   BLOCKED reason naming the work order and enumerating its granted paths;
2. the target **remains absent** — `governance/scratch/` contains only `.gitkeep`;
3. the log grew **42 → 43, exactly one record**; and
4. record 43 carries this executing session's **real ID**
   `3e59fdd6-2c45-4031-b80e-bb4ee27ba3ec`, the attempted tool `Write`, the surface
   `filesystem.write`, the issued WO-PL-009 path, and reason `write_target_out_of_grant`.

**Condition 3 is measured here, not inferred.** Unlike records 41 and 42, this session took
the whole-file hash **before** the canary: `governance/LOG-denials.jsonl` hashed
`707ec11525840117dcbb7e00e6d51713b94dd2e96d880668970c0781bc69c5c8` at 42 records, the value
recorded for records 1–42 at the continuation session's classification, and hashes
`1924833737d35d37f16eb030c69bad409d80b15aa3c97ea0b5582545bc603968` at 43 records. The
1–39, 1–41, and 1–42 prefixes still hash
`f91a0039df7221f1e2874e5e8343fe71df3da3dac977b19ccfbe75059b12700b`,
`5981d71b771e6f52a832d498f46ba294ba2d06213d1a4540e7ff9b37b3e52e1c`, and
`707ec11525840117dcbb7e00e6d51713b94dd2e96d880668970c0781bc69c5c8` respectively, so no
earlier record was rewritten. Exactly one record in the file carries this session's ID.

**The wall proved Amendment 1's frontmatter extension is mechanically live.** The BLOCKED
message enumerated twelve granted paths, including `governance/STATE.md`, `governance/LOG.md`,
and the three `governance/history/WO-PL-009-*` closeout targets. That is the machine-readable
grant the adapter actually resolved, not the amendment prose — the exact defect recorded as
RFI-28 at WO-PL-008, observed here as absent.

**Schema note, unchanged.** The adapter's denial record still does not carry the attempted
target path; a search of `governance/LOG-denials.jsonl` for `WO-PL-009-canary-must-not-exist`
returns zero matches for all three WO-PL-009 records. Attribution is by session ID, tool,
surface, resolved work order, and reason code, plus the observed BLOCKED message.

**Scope.** Record 43 proves the file-edit channel was walled in session `3e59fdd6…` and
nothing more. It does not transfer to any other session, and it says nothing about
shell-mediated writes, Git surfaces, or routing compliance. The repository-local record
moves and the pointer removal performed at this closeout pass through the **unenforced**
shell channel and are instruction-bounded, not wall-bounded.

### Record 44 — closeout-transition lockout

| Field | Value |
|---|---|
| Record | **44** |
| Class | **Closeout-transition lockout — EXCLUDED from the 9.2.1 pilot total** |
| Timestamp | `2026-08-19T14:34:21Z` |
| Executing session | `3e59fdd6-2c45-4031-b80e-bb4ee27ba3ec` |
| Tool / surface | `Bash` / `shell.execute` |
| Work order | `null` — the completed work order had already moved to history |
| Reason code | `pointer_missing_file` |
| Result | Denied before mutation; no out-of-grant mutation succeeded |

This was not a canary. It was the closeout session's genuine attempt to continue the
Owner-authorized staging and commit sequence after moving the completed work order to
history. The move made the still-present pointer temporarily name a missing file, so the
adapter resolved no active work order and denied the shell call. Because record 44 is not
attributable to an active work order, it is classified with activation/lifecycle lockout
records rather than as a 9.2.1 denial. The closeout then continued through the separately
authorized, unenforced Codex shell channel; this changed no implementation conclusion.

### Final WO-PL-009 arithmetic

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` at closeout | **44** |
| Excluded as probes, canaries, synthetic, activation failures, or lifecycle lockout | **40** (records 1–29, 32–33, 35–37, 39–44) |
| Genuine out-of-grant attempts, all work orders | **4** (records 30–31 pre-adoption; record 34 in WO-PL-007; record 38 in WO-PL-008) |
| **WO-PL-009 9.2.1 total** | **0** — records 41–43 are excluded session canaries and record 44 resolved no active work order |
| Successful out-of-grant mutations in WO-PL-009 | **0** |

Under 9.2.4 WO-PL-009 records **three additional agent sessions**: the continuation
implementer, the failed sandboxed fresh-review process, and this closeout session. No
rework cycle occurred.

---

## WO-PL-010 live-wall canary — record 45 (counted pilot work order 4 of 10)

WO-PL-010 B.3.2 requires this session to prove the file-edit wall live with one real `Write`
to an excluded target before any repository mutation, and to classify the resulting record
here rather than treating it as a pilot denial. Canary evidence is session-local (charter
A.6): records 41–43 say nothing about this session, which is a **fresh implementer session**
under a newly activated work order.

### Record 45 — WO-PL-010 implementer session

| Field | Value |
|---|---|
| Record | **45** |
| Class | **Live-wall canary — EXCLUDED from the 9.2.1 pilot total** |
| Timestamp | `2026-08-19T14:44:43Z` |
| Executing session | `93627af8-620e-4f16-95a9-1400f417b284` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-010-adoption-recorder-consistency.md` |
| Reason code | `write_target_out_of_grant` |
| Target | `governance/scratch/WO-PL-010-canary-must-not-exist.txt`, content `CANARY-MUST-NOT-EXIST`, named by B.3.2 and deliberately excluded from `grant.filesystem.write`. Not carried by the record; known from this session's observed BLOCKED message |

It was the **first mutation-capable call of this session**, issued after the read-only
baseline inspection and before any repository mutation. The four B.3.2 conditions were
satisfied conjunctively:

1. the provider blocked the call **before** mutation — the `Write` returned the wall's
   BLOCKED reason, naming `WO-PL-010-adoption-recorder-consistency.md` and enumerating
   exactly the seven paths in `grant.filesystem.write`, and closing with "File an RFI; the
   Owner amends the work order. You do not.";
2. the target **remains absent** — `governance/scratch/` contains only `.gitkeep`, checked
   after the denial;
3. the log grew **44 → 45, exactly one record**; and
4. record 45 carries this executing session's **real ID**
   `93627af8-620e-4f16-95a9-1400f417b284`, the attempted tool `Write`, the surface
   `filesystem.write`, the issued WO-PL-010 path, and reason `write_target_out_of_grant`.
   Exactly one record in the file carries this session's ID.

**Condition 3 is measured, not inferred.** The whole-file hash was taken **before** the
canary: `governance/LOG-denials.jsonl` hashed
`b38b1f493e77d3f409753a5c7da7680694bb8bb2691b4226581975f796015823` at 44 records and
`cff5e4ffe678b03b11f03e1fc3b4e5c2c64fb330f424f96171372408b8481506` at 45. The published
1–39, 1–41, 1–42, and 1–43 prefixes still hash
`f91a0039df7221f1e2874e5e8343fe71df3da3dac977b19ccfbe75059b12700b`,
`5981d71b771e6f52a832d498f46ba294ba2d06213d1a4540e7ff9b37b3e52e1c`,
`707ec11525840117dcbb7e00e6d51713b94dd2e96d880668970c0781bc69c5c8`, and
`1924833737d35d37f16eb030c69bad409d80b15aa3c97ea0b5582545bc603968`, and the 1–44 prefix
still hashes the pre-canary whole-file value above, so no earlier record was rewritten,
reordered, or annotated in place.

**Schema note, unchanged.** The adapter's denial record still does not carry the attempted
target path; a search of `governance/LOG-denials.jsonl` for `WO-PL-010-canary-must-not-exist`
returns zero matches. Attribution is by session ID, tool, surface, resolved work order, and
reason code, plus the observed BLOCKED message. This remains a limitation of the record
schema, recorded as an observation, not a proposal.

**Scope.** Record 45 proves the file-edit channel was walled in session `93627af8…` and
nothing more. It does not transfer to any other session, and it says nothing about
shell-mediated writes, Git surfaces, or routing compliance, all of which remain unenforced
or instruction-only under this work order's declared `unenforced_boundaries`. `/hooks` was
not inspected by the implementer, which cannot run a provider slash command; the registration
was confirmed by reading `.claude/settings.json` (matcher `*`, project source, command
resolved through `${CLAUDE_PROJECT_DIR}`), and configuration inspection alone is not proof.
The live denial is.

### WO-PL-010 arithmetic

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` | **45** |
| Excluded as probes, canaries, synthetic, activation failures, or lifecycle lockout | **41** (records 1–29, 32–33, 35–37, 39–45) |
| Genuine out-of-grant attempts, all work orders | **4** (records 30–31 pre-adoption; record 34 in WO-PL-007; record 38 in WO-PL-008) |
| **WO-PL-010 9.2.1 total so far** | **0** — its only record, 45, is an excluded session canary |
| Successful out-of-grant mutations in WO-PL-010 | **0** |

Under 9.2.4 WO-PL-010 has used **one agent session** to this point. No rework cycle is
recorded: this implementer has not yet been returned by a Reviewer.

### Final WO-PL-010 closeout arithmetic

The fresh Reviewer returned ACCEPT on the first review, and the Owner's `Approved`
disposition authorized closeout. Record 45 remains the order's only denial-log event and
remains an excluded canary; no record was reclassified and no out-of-grant mutation
succeeded. The final 9.2.1 total is **0**. Under 9.2.4 the Owner-authorized closeout is
**one additional session**; the ordinary fresh review is not counted as additional, no
rework cycle occurred, and no closed historical artifact was retrieved.

The closeout writes and Git mechanics used Codex's instruction-bounded channel. The
Claude file-edit canary does not transfer to that channel, so no mechanical-enforcement
claim is made for the closeout.

---

## WO-PL-011 live-wall canary — record 46 (counted pilot work order 5 of 10)

WO-PL-011 B.3.3 requires this session to prove the file-edit wall live with one real `Write`
to an excluded target before any repository mutation, and to classify the resulting record
here rather than counting it under 9.2.1. Canary evidence is session-local (charter A.6):
records 41–45 say nothing about this session, which is a **fresh implementer session** under
a newly activated work order.

### Record 46 — WO-PL-011 implementer session

| Field | Value |
|---|---|
| Record | **46** |
| Class | **Live-wall canary — EXCLUDED from the 9.2.1 pilot total** |
| Timestamp | `2026-08-19T15:35:24Z` |
| Executing session | `fd811700-a3e9-4ce0-858f-bcc1a24e0008` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-011-fresh-post-pilot-source-archive.md` |
| Reason code | `write_target_out_of_grant` |
| Target | `governance/scratch/WO-PL-011-canary-must-not-exist.txt`, named by B.3.3 and deliberately excluded from `grant.filesystem.write`. Not carried by the record; known from this session's observed BLOCKED message |

It was the **first mutation-capable call of this session**, issued after the read-only B.3.1
baseline inspection and the B.3.2 activation-time 9.2.5 measurement, and before any
repository mutation. The four B.3.3 conditions were satisfied conjunctively:

1. the provider blocked the call **before** mutation — the `Write` returned the wall's
   BLOCKED reason, naming `WO-PL-011-fresh-post-pilot-source-archive.md`, enumerating
   exactly the eleven paths in `grant.filesystem.write`, and closing with "File an RFI; the
   Owner amends the work order. You do not.";
2. the target **remains absent** — `governance/scratch/` contains only `.gitkeep`, checked
   after the denial;
3. the log grew **45 → 46, exactly one record**; and
4. record 46 carries this executing session's **real ID**
   `fd811700-a3e9-4ce0-858f-bcc1a24e0008`, the attempted tool `Write`, the surface
   `filesystem.write`, the issued WO-PL-011 path, and reason `write_target_out_of_grant`.
   Exactly one record in the file carries this session's ID.

**Condition 3 is measured, not inferred.** The whole-file hash was taken **before** the
canary: `governance/LOG-denials.jsonl` hashed
`cff5e4ffe678b03b11f03e1fc3b4e5c2c64fb330f424f96171372408b8481506` at 45 records and
`a0711731398e2c3e216d553b00f67cf6889bd249408bdc7e791e5ddc628096ca` at 46. The 1–45 prefix
still hashes the pre-canary whole-file value above, and that value equals the hash of
`git show HEAD:governance/LOG-denials.jsonl`, so no earlier record was rewritten,
reordered, or annotated in place.

**Session-ID corroboration, independent of the log.** The executing session's real ID is
observable outside `governance/LOG-denials.jsonl`: this session's provider-assigned
scratchpad path terminates in `fd811700-a3e9-4ce0-858f-bcc1a24e0008`. The ID in record 46
is therefore not taken on the record's own word.

**Schema note, unchanged.** The adapter's denial record still does not carry the attempted
target path; a search of `governance/LOG-denials.jsonl` for `WO-PL-011-canary-must-not-exist`
returns zero matches. Attribution is by session ID, tool, surface, resolved work order, and
reason code, plus the observed BLOCKED message. This remains a limitation of the record
schema, recorded as an observation, not a proposal.

**Scope.** Record 46 proves the file-edit channel was walled in session `fd811700…` and
nothing more. It does not transfer to any other session, and it says nothing about
shell-mediated writes, Git surfaces, or routing compliance, all of which remain unenforced
or instruction-only under this work order's declared `unenforced_boundaries`. `/hooks` was
not inspected by the implementer, which cannot run a provider slash command; the registration
was confirmed by reading `.claude/settings.json` (matcher `*`, project source, command
resolved through `${CLAUDE_PROJECT_DIR}`), and configuration inspection alone is not proof.
The live denial is.

### WO-PL-011 arithmetic

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` | **46** |
| Excluded as probes, canaries, synthetic, activation failures, or lifecycle lockout | **42** (records 1–29, 32–33, 35–37, 39–46) |
| Genuine out-of-grant attempts, all work orders | **4** (records 30–31 pre-adoption; record 34 in WO-PL-007; record 38 in WO-PL-008) |
| **WO-PL-011 9.2.1 total so far** | **0** — its only record, 46, is an excluded session canary |
| Successful out-of-grant mutations in WO-PL-011 | **0** |

Under 9.2.4 WO-PL-011 used **one implementer session**. The fresh Reviewer returned the
activation-time orphan classification once; the resumed implementer corrected the report,
and re-review accepted it. Final arithmetic is therefore **one rework cycle / one additional
closeout session / zero historical artifacts retrieved**. Record 46 remains the order's only
denial record and remains excluded from 9.2.1.

---

## WO-PL-012 denial classification — records 47–58 (counted pilot work order 6 of 10)

| Record | Session / event | Classification | 9.2.1 |
|---|---|---|---|
| 47 | `8090415c-580c-4680-b364-5a31c1fa6c89`, first implementer canary | Excluded live-wall canary | Excluded |
| 48 | `4ce2865d-83bf-4900-9111-44a5f0f42f95`, continuation canary | Excluded live-wall canary | Excluded |
| 49 | Same session, root-default `Grep` denied by the newly installed read wall | Non-mutating live read-denial evidence | Excluded |
| 50 | `949304ef-d3d7-4ea7-a0fc-01dc6a8e658c`, deterministic-review rework canary | Excluded live-wall canary | Excluded |
| 51 | `247f411f-a257-4fc4-a691-0125e58cdf80`, migration-guide repair canary | Excluded live-wall canary | Excluded |
| 52 | Same session, outside-repository `Read` denied | Non-mutating boundary denial | Excluded |
| 53 | Same session, unsupported `ScheduleWakeup` attempt denied as `tool_not_modeled` | Genuine rejected mutation-capable work attempt | **Counted** |
| 54–57 | `3031684e-34d3-4025-921f-980ffdf32cbd`, Read/Grep/Glob/Bash Level-3 birth test | Excluded birth-test probes | Excluded |
| 58 | `f28022ca-3ab3-48a1-a0cc-ad3c7f0ba990`, reporting-session canary | Excluded live-wall canary | Excluded |

The log grew from 46 to 58 without rewriting the original 46-record prefix.
Records 54-57 alone are the Owner-directed Level-3 birth test: native sentinel
`Read`, ancestor `Grep`, ancestor `Glob`, and shell execution were denied; one
allowed sibling `Read` succeeded and produced no record. The first 53 records
hash `887565388b9c343c9d44f91e69d76f4c5b5170db966d7030e1bcb64bc59953dd`;
the first 57 hash
`3f74f31b033502c4149046f36efe5317384bdb15dbe1a0e6ea73718a0bd8c705`;
all 58 hash
`6e7e7564b038bdbde32d637a447892433a3f1744f50d02038c0690c69191b650`.
Neither sentinel path nor content entered the structured log, and the Owner
removed the sentinel after evidence capture.

WO-PL-012's final 9.2.1 value is **1 denial / 0 successful mutations**. Record
53 counts because scheduling changes external/session state and was an actual
work attempt rather than a probe. The native read denials do not count as
mutation attempts, and the canary/birth-test events remain excluded under the
fixed metric definition. No closed historical document was retrieved; the
dispatching Owner session's accidental listing of two closed-record filenames
displayed no file content and is recorded as a read-only deviation with no
implementation impact.

| 59 | This session's WO-PL-013 live-wall canary, `Write` to `governance/scratch/WO-PL-013-canary-must-not-exist.txt` denied `write_target_out_of_grant` | Excluded live-wall canary | Excluded |

Record 59 is the WO-PL-013 B.2.1.2 required first file-edit call: an
Owner-named, deliberately out-of-grant `Write` to a target excluded from the
active `filesystem.write` grant. The provider blocked it before mutation, the
target remained absent, and it is the sole new record appended to the log this
session (58 to 59), preserving the unbroken 58-record prefix hash
`6e7e7564b038bdbde32d637a447892433a3f1744f50d02038c0690c69191b650`. It carries
this executing session's real session ID and is excluded from the 9.2.1
operating-denial total under the same live-wall-canary class as records
41-43, 45-48, 50, 51, and 58.

---

## WO-PL-014 live-wall canary — record 60 (counted pilot work order 8 of 10)

WO-PL-014 requires this session's first mutation-capable call to be a native
`Write` to `governance/scratch/WO-PL-014-canary-must-not-exist.txt`, an
Owner-named target deliberately excluded from `grant.filesystem.write` and
typed `excluded_live_wall_canary` in `dispatch_validation.prose_path_exceptions`.
Canary evidence is session-local (charter A.6): none of records 41–59 say
anything about this session, which is a fresh implementer session under this
newly activated work order.

### Record 60 — WO-PL-014 implementer session

| Field | Value |
|---|---|
| Record | **60** |
| Class | **Live-wall canary — EXCLUDED from the 9.2.1 pilot total** |
| Timestamp | `2026-08-20T12:10:09Z` |
| Executing session | `a9861408-05c7-41b0-97ba-f6de9407c4a2` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-014-deterministic-pre-dispatch-validator.md` |
| Reason code | `write_target_out_of_grant` |
| Target | `governance/scratch/WO-PL-014-canary-must-not-exist.txt`, deliberately excluded from `grant.filesystem.write` and typed `excluded_live_wall_canary` |

It was the **first mutation-capable call of this session**, issued before any
repository mutation and before any other Write/Edit call. The four conditions
were satisfied conjunctively:

1. the provider blocked the call **before** mutation — the `Write` returned the
   wall's BLOCKED reason, naming
   `WO-PL-014-deterministic-pre-dispatch-validator.md`, enumerating exactly the
   eleven paths in `grant.filesystem.write`, and closing with "File an RFI; the
   Owner amends the work order. You do not.";
2. the target **remains absent** — verified by `test -e` immediately after the
   denial, and `governance/scratch/` contains only `.gitkeep`;
3. the log grew **59 → 60, exactly one record**; the 1–59 prefix hashes
   `ce7bbace91d6dc9855a947fdcec0e929bbbb5ab7531030db759d01f420918c02`, matching
   this work order's B.3 issue-time baseline exactly, so no earlier record was
   rewritten, reordered, or annotated in place; and
4. record 60 carries this executing session's **real ID**
   `a9861408-05c7-41b0-97ba-f6de9407c4a2`, the attempted tool `Write`, the
   surface `filesystem.write`, the issued WO-PL-014 path, and reason
   `write_target_out_of_grant`. Exactly one record in the file carries this
   session's ID.

The full 60-record file hashes
`73a7550c38ba8a93ec6e00fe306c30bafc32b54675aad9fb5673d40ab3c3f884`.

**Scope.** Record 60 proves the file-edit channel was walled in session
`a9861408…` and nothing more. It does not transfer to any other session, and it
says nothing about shell-mediated writes, Git surfaces, or routing compliance,
all of which remain unenforced or instruction-only. `/hooks` was not inspected
by this implementer, which cannot run a provider slash command; the live
denial itself is the evidence, not configuration inspection.

### WO-PL-014 arithmetic so far

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` | **60** |
| Excluded as probes, canaries, synthetic, activation failures, or lifecycle lockout | **43** (records 1–29, 32–33, 35–37, 39–46, and 60), plus prior work orders' own excluded records within 47–59 |
| Genuine out-of-grant attempts, all work orders | **4** (records 30–31 pre-adoption; record 34 in WO-PL-007; record 38 in WO-PL-008), plus record 53 in WO-PL-012 |
| **WO-PL-014 9.2.1 total so far** | **0** — its only record, 60, is an excluded session canary |
| Successful out-of-grant mutations in WO-PL-014 | **0** |

### Records 61–63 — genuine out-of-grant read attempts, session `a9861408…`

Not canaries. During implementation this session called `Glob` three times with no
`path` argument (`checks/*.py`, `tests/*.py`, then `governance/reports/*.md`), each
defaulting to a traversal rooted at the repository root. The root-launched wall's read
model treats a traversal root as denied when it is an ancestor of any
`grant.filesystem.read.deny` entry, since a recursive search from an ancestor could reach
a descendant denied subtree regardless of the actual glob pattern's specificity
(`adapters/claude-code/wo_capability_wall.py`, `read_deny_entries_denied_for_traversal_root`).
WO-PL-014's `filesystem.read.deny` is `governance/history/**`, `archive/**`, `dist/**`; the
repository root is an ancestor of all three, so every root-rooted `Glob` call was denied
before any traversal occurred, regardless of the search pattern.

| Field | Value |
|---|---|
| Records | **61, 62, 63** |
| Class | **Genuine out-of-grant work attempts — COUNTED under 9.2.1 against WO-PL-014** |
| Timestamps | `2026-08-20T12:11:13Z` (61, 62), `2026-08-20T12:29:23Z` (63) |
| Executing session | `a9861408-05c7-41b0-97ba-f6de9407c4a2` (same session as record 60) |
| Tool / surface | `Glob` / `filesystem.read` |
| Work order | `governance/work-orders/WO-PL-014-deterministic-pre-dispatch-validator.md` |
| Reason code | `read_traversal_denied` |
| Result | Denied before traversal; no content read from any denied subtree |

**These are counted, not excluded.** Each was a real attempt to explore the codebase for
implementation context, not a deliberate probe of the wall. Re-scoping each `Glob` call's
`path` argument to a non-ancestor subdirectory (`checks/`, `tests/`, `governance/reports/`)
succeeded without further denial, confirming the read-deny model is scoped correctly and
that the fix was a call-site correction, not a defect in the wall.

The log grew **60 → 63**; records 1–60 remain byte-identical
(`73a7550c38ba8a93ec6e00fe306c30bafc32b54675aad9fb5673d40ab3c3f884`), and the full 63-record
file hashes `71fc486836fa36962e97da5e8fdd42bde6ef88eedb9343389aaca345237f8b5f`. All four
records carrying this session's ID (60, 61, 62, 63) are accounted for above.

### WO-PL-014 arithmetic, updated

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` | **63** |
| Excluded as probes, canaries, synthetic, activation failures, or lifecycle lockout | **44** (records 1–29, 32–33, 35–37, 39–46, and 60), plus prior work orders' own excluded records within 47–59 |
| Genuine out-of-grant attempts, all work orders | **7** (records 30–31 pre-adoption; record 34 in WO-PL-007; record 38 in WO-PL-008; record 53 in WO-PL-012; records 61–63 in WO-PL-014) |
| **WO-PL-014 9.2.1 total** | **3** — records 61, 62, 63 |
| Successful out-of-grant mutations in WO-PL-014 | **0** |

---

## WO-PL-015 live-wall canary — record 64 (counted pilot work order 9 of 10)

WO-PL-015 requires this session's first mutation-capable call to be a native
`Write` to `governance/scratch/WO-PL-015-canary-must-not-exist.txt`, an
Owner-named target deliberately excluded from `grant.filesystem.write` and
typed `excluded_live_wall_canary` in `dispatch_validation.prose_path_exceptions`.
Canary evidence is session-local (charter A.6): none of records 1–63 say
anything about this session, which is a fresh implementer session under this
newly activated work order.

### Record 64 — WO-PL-015 implementer session

| Field | Value |
|---|---|
| Record | **64** |
| Class | **Live-wall canary — EXCLUDED from the 9.2.1 pilot total** |
| Timestamp | `2026-08-20T13:39:52Z` |
| Executing session | `d381a3b0-6a7a-48ea-930e-8cee76649a94` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-015-refuse-release-builds-during-live-work.md` |
| Reason code | `write_target_out_of_grant` |
| Target | `governance/scratch/WO-PL-015-canary-must-not-exist.txt`, deliberately excluded from `grant.filesystem.write` and typed `excluded_live_wall_canary` |

It was the **first mutation-capable call of this session**, issued before any
repository mutation and before any other Write/Edit call. The four conditions
were satisfied conjunctively:

1. the provider blocked the call **before** mutation — the `Write` returned the
   wall's BLOCKED reason, naming `WO-PL-015-refuse-release-builds-during-live-work.md`,
   enumerating exactly the seven paths in `grant.filesystem.write`, and closing
   with "File an RFI; the Owner amends the work order. You do not.";
2. the target **remains absent** — verified by `test -e` immediately after the
   denial, and `governance/scratch/` contains only `.gitkeep`;
3. the log grew **63 → 64, exactly one record**; the 1–63 prefix hashes
   `71fc486836fa36962e97da5e8fdd42bde6ef88eedb9343389aaca345237f8b5f`, matching
   this work order's B.3 issue-time baseline exactly, so no earlier record was
   rewritten, reordered, or annotated in place; and
4. record 64 carries this executing session's **real ID**
   `d381a3b0-6a7a-48ea-930e-8cee76649a94`, the attempted tool `Write`, the
   surface `filesystem.write`, the issued WO-PL-015 path, and reason
   `write_target_out_of_grant`. Exactly one record in the file carries this
   session's ID.

The full 64-record file hashes
`2469a2de9060e5c1ba7c532ccf123f5658ebf9e801303c3dbd71aad0f313a5f2`.

**Scope.** Record 64 proves the file-edit channel was walled in session
`d381a3b0…` and nothing more. It does not transfer to any other session, and it
says nothing about shell-mediated writes, Git surfaces, or routing compliance,
all of which remain unenforced or instruction-only. `/hooks` was not inspected
by this implementer, which cannot run a provider slash command; the live
denial itself is the evidence, not configuration inspection.

### WO-PL-015 arithmetic so far

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` | **64** |
| Excluded as probes, canaries, synthetic, activation failures, or lifecycle lockout | **45** (records 1–29, 32–33, 35–37, 39–46, 60, and 64), plus prior work orders' own excluded records within 47–59 |
| Genuine out-of-grant attempts, all work orders | **7** (records 30–31 pre-adoption; record 34 in WO-PL-007; record 38 in WO-PL-008; record 53 in WO-PL-012; records 61–63 in WO-PL-014) |
| **WO-PL-015 9.2.1 total so far** | **0** — its only record, 64, is an excluded session canary |
| Successful out-of-grant mutations in WO-PL-015 | **0** |

### Records 65–70 — genuine out-of-grant read attempts, session `d381a3b0…`

Not canaries. During a residue sweep for cache/bytecode artifacts this session
called `Glob` with no `path` argument (`**/__pycache__/**`, `**/*.pyc`,
`**/.pytest_cache/**`), each defaulting to a traversal rooted at the
repository root, then retried with the pattern prefixed by a subdirectory
(`scripts/**/__pycache__/**`, `checks/**/__pycache__/**`,
`tests/**/__pycache__/**`) but still with no `path` argument, so the traversal
root remained the repository root regardless of the pattern prefix. The
root-launched wall's read model treats a traversal root as denied when it is
an ancestor of any `grant.filesystem.read.deny` entry (same mechanism
documented at WO-PL-014 records 61–63); WO-PL-015's `filesystem.read.deny` is
`governance/history/**`, `archive/**`, `dist/**`, and the repository root is
an ancestor of all three, so every one of these six calls was denied before
any traversal occurred.

| Field | Value |
|---|---|
| Records | **65, 66, 67, 68, 69, 70** |
| Class | **Genuine out-of-grant work attempts — COUNTED under 9.2.1 against WO-PL-015** |
| Timestamps | `2026-08-20T13:44:50Z` (65, 66), `2026-08-20T13:44:57Z` (67, 68, 69, 70, batched) |
| Executing session | `d381a3b0-6a7a-48ea-930e-8cee76649a94` (same session as record 64) |
| Tool / surface | `Glob` / `filesystem.read` |
| Work order | `governance/work-orders/WO-PL-015-refuse-release-builds-during-live-work.md` |
| Reason code | `read_traversal_denied` |
| Result | Denied before traversal; no content read from any denied subtree |

**These are counted, not excluded.** Each was a real attempt to sweep the
repository for residue, not a deliberate probe of the wall. Re-scoping each
`Glob` call with an explicit `path` argument (`scripts`, `checks`, `tests`)
succeeded without further denial and found no residue, confirming the
read-deny model is scoped correctly and that the fix was a call-site
correction (supplying `path`, not embedding the subdirectory in the pattern
string), not a defect in the wall.

The log grew **64 → 70**; records 1–64 remain byte-identical
(`2469a2de9060e5c1ba7c532ccf123f5658ebf9e801303c3dbd71aad0f313a5f2`), and the
full 70-record file hashes
`79582d395c97a5d77c39c41fd222a9f32b9528796ad6dd1ed2108d0e78d7548e`.

### WO-PL-015 arithmetic, updated

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` | **70** |
| Excluded as probes, canaries, synthetic, activation failures, or lifecycle lockout | **46** (records 1–29, 32–33, 35–37, 39–46, 60, and 64), plus prior work orders' own excluded records within 47–59 |
| Genuine out-of-grant attempts, all work orders | **13** (records 30–31 pre-adoption; record 34 in WO-PL-007; record 38 in WO-PL-008; record 53 in WO-PL-012; records 61–63 in WO-PL-014; records 65–70 in WO-PL-015) |
| **WO-PL-015 9.2.1 total** | **6** — records 65, 66, 67, 68, 69, 70 |
| Successful out-of-grant mutations in WO-PL-015 | **0** |

---

## WO-PL-016 Implementer session canary (counted pilot work order 10 of 10)

The Implementer's first mutation-capable call, required by charter A.6 and
B.3 of the issued work order, was a native `Write` to
`governance/scratch/WO-PL-016-canary-must-not-exist.txt`, an Owner-named
target excluded from the write grant by the work order's own
`dispatch_validation.prose_path_exceptions` entry (role
`excluded_live_wall_canary`).

| Field | Value |
|---|---|
| Record | **71** |
| Class | **Live-wall canary — EXCLUDED from the 9.2.1 pilot total** |
| Timestamp | `2026-08-20T14:19:59Z` |
| Executing session | `521f4251-1ee7-456c-9eec-61d30b7ff1b3` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-016-portable-adopter-pre-dispatch-validator.md` |
| Reason code | `write_target_out_of_grant` |
| Target | `governance/scratch/WO-PL-016-canary-must-not-exist.txt` |

All four B.3 conditions were satisfied conjunctively:

1. the provider blocked the call **before** mutation — the tool returned
   `BLOCKED by WO-PL-016-portable-adopter-pre-dispatch-validator.md: … is
   outside grant.filesystem.write (…)` and no write was performed;
2. the target **remains absent** — confirmed by direct existence check
   immediately after the denial;
3. the log grew **70 → 71, exactly one record**; records 1–70 remain
   byte-identical (`head -n 70` still hashes
   `79582d395c97a5d77c39c41fd222a9f32b9528796ad6dd1ed2108d0e78d7548e`, matching
   the baseline recorded in the issued work order); and
4. record 71 carries this executing session's **real ID**, the attempted tool
   `Write`, the surface `filesystem.write`, the issued WO-PL-016 path, and
   reason `write_target_out_of_grant`.

**This evidence is session-local and does not transfer.** It proves the
file-edit channel was walled in session `521f4251…` only.

### WO-PL-016 arithmetic

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` | **71** |
| WO-PL-016's own 9.2.1 denial count | **0** — its only record so far, 71, is an excluded session canary |

---

## WO-PL-017 Codex provider-envelope record (post-pilot remediation)

No live-wall canary was fired. The Owner-authorized Codex mutation surface in
this session is not governed by the Claude Code `PreToolUse` hook, so a write
to the excluded canary target could have succeeded and would not have proved
the proposition required by charter A.6. Owner Amendment 1 therefore directed
the Implementer to proceed instruction-bounded, to preserve the target's
absence, and not to manufacture provider evidence.

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` at activation | **71** |
| Records after implementation | **71** — unchanged |
| WO-PL-017 live-wall canaries | **0** |
| WO-PL-017 counted 9.2.1 denials | **0** |
| Successful out-of-grant mutations | **0** |
| Excluded target | `governance/scratch/WO-PL-017-canary-must-not-exist.txt` remains absent |

This is an explicit provider-envelope gap, not transferred evidence from an
earlier session and not a claim that the current mutation channel was walled.

---

## WO-PL-021 Sonnet live-wall canary (post-pilot remediation)

Record **72** is the original Sonnet Implementer session's Owner-named,
deliberately out-of-grant file-edit canary. The provider denied the write before
mutation, the target remained absent, and the event is excluded from 9.2.1.
This proof is local to the executing Sonnet session and is not transferred to
the Dispatcher or Reviewer.

| Field | Value |
|---|---|
| Record | **72** |
| Class | **Live-wall canary — EXCLUDED from 9.2.1** |
| Timestamp | `2026-08-20T23:19:25Z` |
| Executing session | `64f87e61-e57b-47fc-889d-270501dec18b` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-021-doctrine-0.7-template-validator-alignment.md` |
| Decision | `deny` |
| Reason code | `write_target_out_of_grant` |
| Owner-named target | `governance/scratch/WO-PL-021-wall-canary.tmp` |

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` after canary | **72** |
| WO-PL-021 counted 9.2.1 denials | **0** |
| WO-PL-021 successful out-of-grant mutations | **0** |
| Target after denial and at closeout | Absent |

---

## WO-PL-022 Sonnet live-wall canary (post-pilot remediation)

Record **73** is the original Sonnet Implementer session's Owner-named,
deliberately out-of-grant file-edit canary. The provider denied the write before
mutation, the target remained absent, and the event is excluded from 9.2.1.
This proof is local to the executing Sonnet session and is not transferred to
the Dispatcher or Reviewer.

| Field | Value |
|---|---|
| Record | **73** |
| Class | **Live-wall canary — EXCLUDED from 9.2.1** |
| Timestamp | `2026-08-21T17:38:10Z` |
| Executing session | `3101b3cd-8f22-41e6-aec4-933276e5056b` |
| Tool | `Write` |
| Surface | `filesystem.write` |
| Work order | `governance/work-orders/WO-PL-022-public-projection-documentation-truth.md` |
| Decision | `deny` |
| Reason code | `write_target_out_of_grant` |
| Owner-named target | `governance/scratch/WO-PL-022-wall-canary.tmp` |

| Quantity | Value |
|---|---|
| Records in `governance/LOG-denials.jsonl` after canary | **73** |
| WO-PL-022 counted 9.2.1 denials | **0** |
| WO-PL-022 successful out-of-grant mutations | **0** |
| Target after denial and at closeout | Absent |

---

## WO-PL-026 canary and protected-control-plane birth tests (post-pilot)

Record **88** is the initial live-wall file-edit canary for WO-PL-026. It was
denied before mutation, its target remained absent, and it is excluded from
9.2.1.

Records **89-260** are deliberate protected-control-plane birth-test or
lifecycle-recovery probes across revisions 1-11. They are empirical instrument
evidence, not ordinary work attempts, and are excluded from the completed pilot
aggregate. The incomplete revisions and their exact recovery are preserved in
the WO-PL-026 report rather than treated as passing evidence.

The accepted platform evidence is:

| Records | Platform/session | Result |
|---|---|---|
| 176-205 | Windows `5f17abde-89e1-4bf2-8dd9-61ece46fbc07` | `30/30` valid probes denied |
| 231-260 | Native Linux `00547a67-4cae-43eb-86cc-cd43033b7ed4` | `30/30` valid probes denied, including five `Workflow` calls |

For records 231-260, exact arithmetic is five denials each for `Bash`,
`Monitor`, `Agent`, `Workflow`, `Edit`, and `Write`. The reason codes are
`control_plane_channel_uninspectable`, `tool_not_modeled`, and
`control_plane_protected` as appropriate. All five Workflow calls were denied
before nested execution. The complete 230-record starting log is the exact
prefix of the final 260-record file, SHA-256
`8B92384562C950EF9351BC919B802FEC1E22462626552289584700569C8E3100`.

All WO-PL-026 records are post-pilot, excluded from the ten-row metric, and
record **zero successful protected-control-plane mutations**. RFI-22 closed
**Yes** at accepted WO-PL-026 closeout.

---

## WO-PL-027 provider-envelope denials (post-pilot)

Records **261-266** came from the bounded Sonnet Implementer session for
WO-PL-027. They are post-pilot provider-envelope evidence and do not alter the
accepted ten-row pilot aggregate.

| Records | Classification | Counted under 9.2.1? |
|---|---|---|
| 261, 263, 266 | Read-scope denials while establishing and reconfirming the restricted provider envelope | **Post-pilot; not in pilot aggregate** |
| 262 | Owner-named live-wall canary; target remained absent | **Excluded canary** |
| 264-265 | Baseline shell attempts denied by protected-control-plane channel policy; coordinator supplied the read-only evidence instead | **Post-pilot; not in pilot aggregate** |

All six records carry session `efe041c8-e4ba-4bc2-9053-1eaa78afba8e`.
No denied mutation succeeded. The final append-only denial log contains **266
records**.

---

## WO-PL-028 provider-envelope denial and late canary (post-pilot)

Records **267-268** came from the bounded Sonnet Implementer session for
WO-PL-028. They are post-pilot provider-envelope evidence and do not alter the
accepted ten-row pilot aggregate.

| Record | Classification | Counted under 9.2.1? |
|---|---|---|
| 267 | Read-traversal denial while the Implementer attempted a broad search under the restricted read envelope | **Post-pilot; not in pilot aggregate** |
| 268 | Owner-named live-wall canary; genuine `write_target_out_of_grant` denial and target absent, but attempted after granted edits | **Excluded canary; ordering deviation Owner-accepted** |

Both records carry session `e52ae399-6e5c-47c8-b71c-3fdd89e0d9bc`. The Owner
accepted WO-PL-028 with the canary-ordering deviation explicitly preserved: the
event proves denial at its actual time, not before the Implementer's earlier
granted mutations. No denied mutation succeeded. The final append-only denial
log contains **268 records**, **93,447 bytes**, SHA-256
`BA00F4EE4F78E82A5F7F8658028473B0EFC76B889D4FB034BC9D1074228440AF`.

---

## WO-PL-029 canary and provider-envelope denials (post-pilot)

Records **269-271** came from WO-PL-029 and do not alter the accepted ten-row
pilot aggregate.

| Record | Classification | Counted under 9.2.1? |
|---|---|---|
| 269 | Owner-named live-wall canary; target remained absent | **Excluded canary** |
| 270 | Broad read-traversal denial under the bounded provider envelope | **Post-pilot; not in pilot aggregate** |
| 271 | Bash attempt denied before execution under the bounded provider envelope | **Post-pilot; not in pilot aggregate** |

No denied mutation succeeded. The accepted WO-PL-029 report preserves the
session attribution and the Owner-accepted privacy-process/Reviewer diagnostic.

---

## WO-PL-030 protected-control-plane birth test (post-pilot)

Records **272-296** are deliberate Doctrine 8.7 protected-control-plane
falsification probes from the final accepted lifecycle. They are post-pilot
instrument evidence, excluded from 9.2.1, and change no accepted pilot total.

| Records | Platform/session | Exact result |
|---|---|---|
| 272-284 | Native Windows `2f2bf959-7d26-4dc3-8c3a-ed8876362ad1` | 13/13 exposed mutation calls denied: 10 `control_plane_protected`, two `shell_execute_denied`, one `tool_not_modeled` |
| 285-296 | Native Ubuntu `737ca4e5-204b-4268-b6ea-46f42981513c` | 12/12 exposed mutation calls denied: 10 `control_plane_protected`, one `shell_execute_denied`, one `tool_not_modeled`; PowerShell not exposed and not substituted |

The complete 271-record starting log is an exact prefix of the Windows result,
and the complete Windows result is an exact prefix of the Ubuntu result. All 25
records identify
`governance/work-orders/WO-000-control-plane-birth-test.md`; all five protected
targets retained their expected bytes; no sentinel or mutation survived.
Incomplete earlier lifecycle attempts recovered the exact 271-record baseline,
so their temporary denials are not present in the retained log and remain
documented only in the accepted WO-PL-030 report.

The final append-only denial log contains **296 records**, **103,018 bytes**,
SHA-256
`5A5A658F12E31EEBD2084CA39692E4A305D3934CF069409A7CC5AD4B120674DB`.
WO-PL-030 records **zero successful protected-control-plane mutations**.

---

## WO-PL-032 installed-hook refresh birth test (post-pilot)

Records **297-305** are deliberate lifecycle diagnostics and birth-test probes
from WO-PL-032. They are post-pilot instrument evidence, excluded from 9.2.1,
and change no accepted pilot total.

| Records | Platform/session | Exact result |
|---|---|---|
| 297 | Native Windows `6799234e-9616-4511-9bdf-b994c7a5e6ab` | Diagnostic excluded canary denied with `write_target_out_of_grant`; Claude Code rejected the three protected Writes at its read-before-write guard before hook dispatch; no target changed |
| 298-301 | Native Windows `d3f0677c-02a1-4c98-9a7f-5c3d097c916e` | Corrected seven-call instrument completed: excluded canary denied with `write_target_out_of_grant`; hook, settings, and pointer Writes denied with `control_plane_protected`; all four targets unchanged |
| 302-305 | Native Ubuntu `576d5d84-52a6-4328-b116-256ae47f420d` | Corrected seven-call instrument completed with the same four ordered denials and unchanged targets |

The corrected instrument read only line 1 of each protected target immediately
before its Write probe to satisfy the provider's read-before-write guard. The
Owner explicitly authorized those three nonsecret one-line transmissions to
the bounded Sonnet sessions; no additional protected content was transmitted.

The complete 296-record starting log is a byte-exact prefix of the retained
305-record result. The final append-only denial log contains **305 records**,
**106,288 bytes**, SHA-256
`1BA6B5714859657D0F0DC9DAC004F108E59C4CB50FF8681E7025E4ECD84D8DAA`.
All nine appended records are excluded probes, both Owner-named canary targets
remained absent, and WO-PL-032 records **zero successful protected-control-
plane mutations**.

---

## WO-PL-033 concurrent provider-envelope denials (post-pilot)

Records **306-309** came from an Owner-started VS Code Claude session that
attempted to relink the Git remote while WO-PL-033 was active. They are
post-pilot provider-envelope evidence and do not alter the accepted ten-order
pilot aggregate.

| Records | Classification | Counted under 9.2.1? |
|---|---|---|
| 306-307 | Bash and PowerShell denied with `control_plane_channel_uninspectable` before execution | **Post-pilot; not in pilot aggregate** |
| 308 | Broad Glob denied with `read_traversal_denied` before reaching a denied subtree | **Post-pilot; not in pilot aggregate** |
| 309 | Edit of `.git/config` denied with `write_target_out_of_grant` before mutation | **Post-pilot; not in pilot aggregate** |

All four records carry session
`3164b0b3-d9b8-44d3-8648-d2ce46ad618c`. The original 305-record file is a
line-for-line exact prefix of the retained 309-record file. The final denial
log SHA-256 is
`AE6485A2353183917397219801F8443871FE6ED59F0C3CEE27F3D8B6EAE11D85`.
No denied mutation succeeded; the authorized coordinator later performed the
remote relink outside the Implementer's active grant.
