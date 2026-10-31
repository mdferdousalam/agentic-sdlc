## Why

Three controls existed only as sentences in prompts, and a sentence in a prompt is a request.

The most important is the suite itself. Every agent prompt forbids deleting a test, weakening
an assertion, adding a skip marker, suppressing a warning or lowering a threshold to make the
gate pass — and nothing checked. A suite quietly disarmed passes every other stage, which makes
this the one failure that defeats the whole pipeline rather than one stage of it.

The second is cost. An agent that cannot stop is a cost centre with a git token, and the only
thing standing between a repair loop and a large bill was an advisory message after the third
attempt.

The third is resumption. A long task that crashes leaves a half-applied change, and the next
session has no record of what was done or whether the repository still matches it.

## What Changes

- `sdlc tests audit` reads the diff for everything that makes the gate easier to pass. The
  readiness gate runs it; so does the remediator, on its own work.
- `budget` sets ceilings the hook enforces and an agent cannot raise for itself.
- `sdlc checkpoint` records a long task's progress and the repository state it assumed, and
  re-checks that state before saying it is safe to continue.
- The branch-opener checks for upstream drift and for another agent already on the branch, and
  can isolate work in a worktree.

## Capabilities

### New Capabilities

- `agent-operations`: the controls on how agents work, as opposed to on what they produce.

### Modified Capabilities

<!-- none -->

## Impact

`bin/sdlc` (`tests`, `budget`, `checkpoint`, guard), `schema/sdlc.config.schema.json`,
`agents/sdlc-readiness-gate.md`, `agents/sdlc-remediator.md`, `agents/sdlc-branch-opener.md`,
`docs/configuration.md`, `docs/pipeline.md`, `README.md`, `tests/test_sdlc.py`.
