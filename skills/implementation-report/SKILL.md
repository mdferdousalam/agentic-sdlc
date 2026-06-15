---
name: implementation-report
description: >
  Generate the Implementation Report (IR) that closes a feature: what shipped, how it
  was verified, deviations from the DI, and follow-ups. Use after the readiness gate
  returns READY and before/at merge, or when asked to "write the IR / file the
  implementation report".
---

# /implementation-report — Implementation Report (IR)

The IR is the closing artifact: a durable record of what was delivered for this
`{phase, module, feature}` and the proof it was verified.

## Setup

1. Read `sdlc.config.json` for `docsRoot`.
2. Read the feature's `PRD`, `FRD`, `DI`, and the latest `CVR`.
3. Read the branch diff and the readiness-gate verdict.

## Output

Write `<docsRoot>/<phase>/<module>/<feature>/IR_of-DI-v1.0_r1.md`:

```markdown
# Implementation Report — <phase>/<module>/<feature> (of DI v1.0, r1)

## Summary
<what shipped, in 2-3 sentences>

## Files created / changed
<grouped by package; counts + notable files>

## Data & config
- Migrations applied / seeds added.
- Config/reference tables introduced and the admin CRUD surface for them.

## Acceptance criteria — final status
| AC | Status | Test |

## Verification
- verifyCmd result; readiness-gate verdict (READY) with reviewers run.
- CVR reference (file + verdict).

## Deviations from DI
<each deviation + justification, or "none">

## Follow-ups / debt
<spawned tasks, known gaps, out-of-scope items>
```

## On completion

- Update the feature's row in `<docsRoot>/MODULES_MAP.md` to status `shipped`.
- Update its `BRANCH_LEDGER.md` record status to `merged` (once the branch owner merges).

## Hard rules

- Do not file an IR if the readiness gate has not returned READY — say so and stop.
- The IR must reflect what is actually on the branch; verify the diff, do not restate
  the DI as if it were done.
