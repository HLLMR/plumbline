# Doctrine Appendix A. CHARTER TEMPLATE (TIER-1 INJECTABLE)

Copy to the project root (or adopt the tooling's existing auto-loaded file), fill every bracket, and keep under budget.

```markdown
# [PROJECT] Session Charter
Injected every session. Budget: 2,500 tokens. Doctrine rev [x.y], DR-001.

## A.1 PROHIBITIONS (binding; violations are blocked and logged where enforcement exists)
A.1.1 You never amend this charter, governance/PLAN.md, governance/ROUTING.md,
      or any decision record. You propose; the Owner ratifies.
A.1.2 You act only inside the active work order's capability grant. With no
      active work order, no mutating action is permitted.
A.1.3 Needs outside your grant are RFIs, not improvisations.
A.1.4 [PROJECT KILL LIST: the plausible-but-rejected directions unique to
      this project. Dead approaches agents keep resurrecting. Forbidden
      dependencies. Out-of-scope features. Systems and data that must never
      be touched. Name each specifically. This list is where drift dies.]

## A.2 AUTHORITY ORDER
A.2.1 governance/PLAN.md (ratified intent). Conflicts are surfaced as RFIs,
      never silently resolved.
A.2.2 The active work order.
A.2.3 Documents attached by governance/ROUTING.md.

## A.3 CURRENT STATE (one line each; updated by the Owner at work-order
acceptance, never by agents)
A.3.1 [plan version, phase, what is frozen]
A.3.2 [current sequencing: what is next and what it is blocked on]
A.3.3 [pending owner decisions]

## A.4 ROUTING (read the mapped document before touching the path)
A.4.1 [path or subsystem] -> [document]
A.4.2 Unmapped and unsure -> RFI.

## A.5 REPORTING
End every work order with the report format specified in the work order,
addressed to the Reviewer. Completeness over brevity.

## A.6 ENVIRONMENT
[build and test commands, platform notes: the minimum an agent needs
every session]
```

_Extracted verbatim from DOCTRINE.md rev 0.8. Do not edit here; templates change only when the doctrine does._
