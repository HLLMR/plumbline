# Doctrine Appendix B. WORK ORDER TEMPLATE

```markdown
---
id: WO-[n]
status: ACTIVE                 # ACTIVE | COMPLETE | RFI-BLOCKED
doctrine_rev: [x.y]
grant:                         # capability manifest, enforced by adapter
  filesystem.write: [path, path]
  filesystem.read.deny: [protected paths, if any]
  shell.execute: restricted    # denied | restricted | allowed
  network.egress: denied
  package.install: denied
  secrets.read: denied
  git.commit: denied
  git.push: denied
  # project-specific surfaces (db.write, infra.apply, model.run) as needed
enforced_by: {}                # which mechanism walls each enforced surface;
                               # empty by default. An Owner moves a surface
                               # here only after naming and validating the
                               # mechanism that covers the whole surface.
unenforced_boundaries:         # every declared surface not in enforced_by,
  - filesystem.write            # classified exactly once. Honored by
  - filesystem.read.deny        # instruction only; never called walls. If
  - shell.execute                # that risk is unacceptable this WO does
  - network.egress               # not run under this provider (8.3.4).
  - package.install
  - secrets.read
  - git.commit
  - git.push
---
# WO-[n]: [title]

## B.1 CONTEXT
[Two to four sentences. Cite plan sections by number. Paste routed excerpts
here if the tooling cannot inject them.]

## B.2 OBJECTIVE
[The falsifiable goal.]

## B.3 REQUIRED WORK
[Numbered. Each item verifiable.]

## B.4 BOUNDARIES
[Restate the grant in prose where it matters, plus any unenforced boundaries
the implementer must honor on instruction alone. Those are the weakest part
of this work order and the report must confirm each was respected. See B.7
for the checker-generated classification, which is authoritative for exact
grant classification; this section is human-readable elaboration and never
contradicts it.]

## B.5 ACCEPTANCE
[Exact commands and expected results. What the Reviewer verifies from the
report alone.]

## B.6 REPORT FORMAT
[Sections required in the work report.]

<!-- BEGIN GENERATED BOUNDARIES -->
## B.7 Generated boundaries

[Placeholder. After completing the frontmatter above, run the project's
pre-dispatch boundary generator and replace only the content between the
BEGIN and END marker comments above and below with its exact output, keeping
both marker comments in place exactly as they appear. Validate the resulting
work order before activation. This block is machine-generated solely from
frontmatter; B.4 is its human-readable prose counterpart and never
contradicts it.]
<!-- END GENERATED BOUNDARIES -->
```

_Extracted verbatim from DOCTRINE.md rev 0.8. Do not edit here; templates change only when the doctrine does._
