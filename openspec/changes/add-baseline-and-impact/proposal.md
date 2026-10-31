## Why

The pipeline runs `verifyCmd` after a change and treats the result as a verdict on that change.
It has no idea what the command said *before* the work started. So a test that was already
failing is attributed to the patch, an agent burns three attempts "fixing" it, and a warning
that was always there looks like a regression. The reverse is worse: a genuinely new failure
hides among pre-existing ones and the gate reports a pass.

There is a second blind spot with the same shape. Nothing in the pipeline asks who *depends* on
the code being changed. The verifier checks the unit against its own specification and the gate
checks the unit's own tests, so a change that satisfies its spec and breaks three callers passes
every stage. `sdlc trace` reconstructs this afterwards, which is the wrong time.

And when a command fails, the pipeline cannot say whether the cause was the patch or the
machine — a missing binary, a wrong runtime version, a lockfile for another architecture.

## What Changes

- A baseline is captured before work starts and compared afterwards, so a failure is
  attributable: newly broken, pre-existing, or fixed.
- A read-only impact analyst reports who depends on what this change touches, before the
  implementer starts rather than after the gate.
- Every receipt carries an environment fingerprint, so an environmental failure is
  distinguishable from a defect.

## Capabilities

### New Capabilities

- `change-safety`: knowing what was already broken, who else depends on this, and whether the
  machine or the patch is at fault.

### Modified Capabilities

<!-- none -->

## Impact

`bin/sdlc` (new `baseline` subcommand, environment fingerprint, receipt shape),
`agents/sdlc-impact-analyst.md` (new), `commands/impact.md` (new),
`agents/sdlc-branch-opener.md`, `agents/sdlc-verifier.md`, `agents/sdlc-readiness-gate.md`,
`skills/agentic-sdlc-pipeline/SKILL.md`, `docs/pipeline.md`, `tests/test_sdlc.py`.
