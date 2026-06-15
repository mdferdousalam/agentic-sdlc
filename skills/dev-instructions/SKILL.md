---
name: dev-instructions
description: >
  Generate the Developer Instructions (DI) document for a feature from its approved PRD
  and FRD — the concrete, step-by-step build plan the implementer follows. Use after the
  branch is created, or when asked to "write the DI / dev instructions" for a feature.
---

# /dev-instructions — Developer Instructions (DI)

The DI translates the FRD into an ordered, unambiguous build plan. The implementer
should be able to follow it without re-deriving decisions.

## Setup

1. Read `sdlc.config.json` for `docsRoot`, stack, and DB flow.
2. Read `<docsRoot>/<phase>/<module>/<feature>/PRD_v1.0.md` and `FRD_v1.0.md`.
3. Note `$ARGUMENTS` for `{phase, module, feature}` if not already in context.

## Output

Write `<docsRoot>/<phase>/<module>/<feature>/DI_v1.0.md`:

```markdown
# Developer Instructions — <phase>/<module>/<feature>

## Branch
<branch name from the ledger>

## Build order
1. <step> — files to create/change, with paths
2. ...

## Data model
- Migrations to add (respect the project's migrate-only/push flow).
- Seeds to add (follow the project's seed naming/order convention).
- Config/reference tables for every configurable value (no hardcoded constants).

## Shared code (DRY)
- What to extract into shared packages vs. implement locally — reuse before writing new.

## Implementation notes
- Per-file responsibilities; canonical helpers/envelopes to use; patterns to follow.
- Required code comments: a short header on each new file explaining WHY where the
  intent is non-obvious (e.g. cache/invalidation semantics).

## Tests (required)
- Unit/integration cases mapped to FRD acceptance criteria (use the project's fixtures).
- E2E happy path if user-facing.

## Acceptance criteria (copied from FRD §6)
- AC-1 ...

## Verify before PR
<the verifyCmd from sdlc.config.json>
```

## Hard rules

- Every acceptance criterion must have at least one mapped test in the test section.
- Every value the spec flagged configurable must appear under Data model as a
  config/reference-table row — never as a literal in the build steps.
- Respect the detected stack: do not introduce `db:push` if the project is migrate-only,
  and match the package manager and commit convention.
