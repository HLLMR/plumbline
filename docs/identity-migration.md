# From Plumbline to Writwall

This project released publicly as **Plumbline** before it had an evidenced
inception name search. That was a process defect. Promotion stopped when the
collision was discovered; the repository did not claim that the other projects
copied this methodology or that a legal dispute had been established.

The repair happened in two governed steps:

1. WO-PL-036 built a reproducible name-clearance collector and offline checker,
   published the original failure as a worked example, and recorded exact
   automated and named-human evidence. The Owner rejected Plumbline, Grantcord,
   and Writcord and accepted **Writwall** on 2026-08-28.
2. WO-PL-037 migrated current product surfaces while preserving records under
   the names they actually carried. A machine-checked manifest pins every
   public file that still contains the former identity.

The canonical evidence is public:

- [`examples/name-clearance-incident-2026-08.md`](../examples/name-clearance-incident-2026-08.md)
  explains the late discovery and its limits.
- [`examples/name-clearance-ledgers/writwall-candidate.json`](../examples/name-clearance-ledgers/writwall-candidate.json)
  records the accepted candidate and exact source dispositions.
- [`identity/legacy-references.json`](../identity/legacy-references.json)
  classifies retained former-name files and binds them to exact bytes.
- `python -B checks/check_identity.py` verifies current identity, stale paths and
  coordinates, chronology, and every retained-file digest.

The evidence proves what was searched and how the migration was checked. It is
not legal clearance, exclusivity, or a claim that no confusing use can exist.

## Why the old name remains

History is evidence. Rewriting an accepted decision, pilot report, denial log,
or name-search result to say Writwall would imply that the replacement identity
existed before the Owner selected it. Those files retain Plumbline and are
listed in the legacy-reference manifest. Current onboarding, commands, assets,
package paths, repository links, and release surfaces use Writwall.

## Owner-controlled external cutover packet

This packet is prepared by WO-PL-037 but is not authority to execute it. The
Owner applies it only after accepting the work order and after a new projection
has passed the complete release gates.

| Hold point | Authorized action after acceptance | Verification | Rollback boundary |
|---|---|---|---|
| Private record | Close WO-PL-037 in the private governed source; commit and push only its accepted implementation and closeout records to the private archive remote | Private branch clean, remote matches the accepted commit, pointer absent | Reopen through a new governed correction; never rewrite accepted history |
| Public bytes | Build two fresh external projections from the closeout commit using the Owner-private pattern input; require identical complete checksum ledgers and all Windows/Ubuntu gates | Candidate contains Writwall current surfaces, classified Plumbline provenance only, no private match, and a clean identity check | Delete candidates before any public mutation and stop |
| Public repository | Apply the verified candidate as one reviewable identity-migration commit to the existing public repository, preserving its initial Plumbline release commit | Public diff matches the candidate ledger; CI passes on the exact commit | Revert the public commit before repository rename if verification fails |
| Repository identity | Rename the public GitHub repository from `HLLMR/plumbline` to `HLLMR/writwall`; keep the private governed-source archive repository unchanged | New URL resolves, old URL redirects, clone/fetch and issue #2 work, Actions and security settings remain enabled | Rename back before publishing a Writwall release; verify both URLs again |
| Repository chrome | Set the description to “Document-governed authority and capability bounds for AI-assisted development”; set the homepage to the final Writwall page; upload `docs/assets/writwall-og.png` as social preview; retain accurate governance/security topics | Anonymous repository view shows the new name, description, links, social image, README assets, and badges | Restore the prior description/homepage/image captured immediately before mutation |
| Release | After all preceding checks, publish `v0.8.1` as “Writwall identity migration” and attach a freshly built `writwall-0.8.zip`; keep the historical `v0.8` Plumbline release visible | Latest-release badge, archive checker, asset checksum, tag target, and release notes all match the accepted commit | Stop before publication on any mismatch; after publication, correct forward rather than rewriting provenance |
| Launch channels | Update the separately maintained website, scheduled Show HN copy, LinkedIn/content cards, logos, and links from the approved Writwall launch packet only after the repository and release URLs are live | Every public link resolves anonymously and all copy says the project was formerly Plumbline | Pause scheduled promotion; restore the captured prior draft where the platform supports revision |

No external surface is changed merely because this file exists. Credentials,
private patterns, private archives, and unrelated project material never enter
the public candidate or this record.

## Current visual identity

The current Writwall mark is a two-line wall placed at the `writ|wall`
boundary. It replaces the line-and-bob device inherited during the emergency
name migration. The former device remains legitimate historical evidence in
accepted records and prior-release screenshots; it is not current brand art.
