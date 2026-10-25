## 1. Baseline

- [x] 1.1 `sdlc baseline capture` runs `verifyCmd`, extracts failure and warning signals,
      normalises away timings, durations, temporary paths, addresses and line/column numbers,
      and writes `.sdlc/baseline.json` keyed to the merge base.
- [x] 1.2 `sdlc baseline compare` re-runs the command and classifies each signal as `new`,
      `pre-existing` or `fixed`; a new signal exits non-zero.
- [x] 1.3 No baseline means `unexecuted`, never passed.
- [x] 1.4 `sdlc baseline show` prints what was captured and when.
- [x] 1.5 Baseline events reach the audit log.

## 2. Environment

- [x] 2.1 Tool versions are probed once per process and cached.
- [x] 2.2 Every receipt carries the fingerprint; `sdlc status` and `sdlc doctor` can show it.
- [x] 2.3 A fingerprint that has changed since the baseline is reported, because it explains
      failures the diff does not.

## 3. Impact

- [x] 3.1 `agents/sdlc-impact-analyst.md` is read-only and reports dependents, published shapes
      and implied migrations, and states its own limits.
- [x] 3.2 `commands/impact.md` drives it.
- [x] 3.3 The branch-opener captures the baseline; the verifier and readiness gate compare.
- [x] 3.4 The pipeline skill and `docs/pipeline.md` carry the new stage.

## 4. Proof

- [x] 4.1 Tests: a pre-existing failure is not blamed; a new failure is; a fixed one is noticed;
      no baseline is `unexecuted`; the baseline survives a commit.
- [x] 4.2 The repository's own `verifyCmd` passes.
