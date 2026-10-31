## 1. Suite integrity

- [x] 1.1 `sdlc tests audit` detects deleted test files, removed test declarations, removed
      assertions, skip markers, suppression directives and lowered thresholds.
- [x] 1.2 A deleted file's lines are attributed to that file, not to the previous one in the diff.
- [x] 1.3 `--acknowledge` records a human decision; it does not waive the finding.
- [x] 1.4 The readiness gate runs it before believing a green gate; the remediator runs it on
      its own work, being the stage most tempted.

## 2. Budget

- [x] 2.1 `budget` in the config schema: `maxToolCalls`, `maxWallClockMin`, `maxRetries`, `stopPolicy`.
- [x] 2.2 `guard_problem` refuses past the ceiling, checked after the destructive-command rules.
- [x] 2.3 `sdlc budget show|reset`; only a person resets, and the refusal names the command.
- [x] 2.4 Unset means unenforced, and the output says so rather than implying safety.

## 3. Checkpoints and concurrency

- [x] 3.1 `sdlc checkpoint write|resume|show`, recording steps, next step and file digests.
- [x] 3.2 `resume` re-validates branch, commit ancestry, file digests and toolchain.
- [x] 3.3 The branch-opener detects upstream drift and an existing branch, and offers a worktree.

## 4. Proof

- [x] 4.1 Tests for every detection above, both directions, plus the budget and checkpoint paths.
- [x] 4.2 The repository's own `verifyCmd` passes.
