---
id: RFI-24
status: DEFERRED
opened: 2026-08-17 under WO-PL-007 (counted pilot work order 1 of 10)
subject: An agent cannot durably retire the work order that supplies its own grant
disposition: DEFERRED — WO-PL-007 uses the fail-closed Owner-direct retirement tail
---

# RFI-24 — Active-work-order retirement mechanics

## 1. The adapter accepts a pointer only under `governance/work-orders/`

`.claude/active-wo.txt` resolves to an active work order only when the resolved file lies under
`governance/work-orders/`. A pointer resolving anywhere else is not a valid active work order.

## 2. Moving the active record to history invalidates the pointer immediately

Retiring a completed work order means moving it to `governance/history/`. The instant that move
lands, the pointer no longer resolves to a file under `governance/work-orders/`, so the active work
order ceases to exist from the adapter's point of view. There is no interval in which the record is
both retired and still authoritative.

## 3. After invalidation a closeout agent has no authority to commit

With no valid active work order, the repository is in fail-closed lockout: no grant is in force, so
no mutating action is permitted. A closeout agent therefore cannot rely on the work order to
authorize or mechanically scope any subsequent action — including the very commit that would make the
retirement durable. The work order cannot witness its own retirement.

## 4. Shell-mediated move-and-commit is not an acceptable workaround

The move and the commit *would* succeed through the shell, because `filesystem.write` via shell and
every Git surface are observed unenforced (adoption record D.4.2). That is precisely why it is
unacceptable: it would complete the retirement by relying on a **known bypass** rather than on an
effective file grant. Using an unenforced channel to accomplish what the enforced channel forbids
converts a declared gap into an operating procedure, and would misrepresent the result as a clean
same-work-order closeout.

## 5. WO-PL-007's disposition — **DEFERRED**

WO-PL-007 does not solve this. It routes around it with the fail-closed Owner-direct retirement tail
in B.3.13.3 through B.3.13.5:

- a fresh closeout transcriber stages the accepted records **while the pointer is still valid**, and
  stops without committing;
- the **Owner alone** then performs the lifecycle transition, the move to `governance/history/`, the
  staging of that move, and the single records-only commit;
- from the instant of the move until the pointer is removed, fail-closed lockout applies to every
  agent, and no agent tool call is permitted or required; and
- the Owner removes the pointer last and confirms its absence.

**The Owner-direct tail is a procedure, not a fix.** It demonstrates that the retirement can be
completed safely by moving the final steps outside agent authority; it does not give an agent a
supported way to retire the work order that binds it. Anyone reading this disposition as evidence
that the mechanics are solved has read it backwards.

This RFI grants no change to the adapter, the provider configuration, the adapter documentation, the
tests, the canonical or bundled copies, or the birth-test evidence. None was made under WO-PL-007.

## 6. Future Owner question

> Should a later work order introduce a supported closeout mechanism that permits durable same-work-order
> retirement without an Owner-direct Git tail?

The cost of answering **no** is that every counted work order's closeout requires direct Owner
execution of the final lifecycle move and commit, which does not scale to an adopter with many work
orders and is the more consequential half of the question for the pilot.

## 7. Owner reaffirmation — DEFERRED

Recorded 2026-08-18 at WO-PL-007 closeout. RFI-24 remains DEFERRED. The
Owner-direct tail is still a procedure, not a supported agent retirement
mechanism. The Owner waived a separate closeout-transcriber session for this
closeout to terminate procedural recursion; that waiver is recorded as a
deviation and does not resolve this RFI.
