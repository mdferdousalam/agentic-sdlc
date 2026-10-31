# Verification — the five changes that make up 3.0.0

Cross-verification of what was built against what was specified, scenario by scenario, for
`add-agent-operations`, `add-baseline-and-impact`, `add-concern-profiles`, `add-control-spine`
and `add-outcome-measurement`.

- **Commit** `674772d`
- **Date** 2026-10-31
- **Method** every row names the evidence that establishes it. A row is `passed` only where a
  named assertion in `tests/test_sdlc.py` covers it and the suite passes, or where the
  behaviour was observed directly by running the command named. A row with neither is
  `unexecuted` — nobody ran it. That is not a pass.
- **Suite state** `python3 tests/test_sdlc.py` → exit 0, 341 assertions.
- **Scope** 18 requirements, 31 scenarios.

## Outcome

| | count |
| --- | --- |
| `passed` | 29 |
| `failed` | 0 |
| `unexecuted` | 2 |

Two scenarios have no mechanical evidence and are recorded as such below. Neither is a defect
in the code; both describe behaviour that exists only as instructions to a reviewing agent,
which this repository cannot execute against itself.

Separately, **three passing scenarios are covered by observation rather than by a regression
test** (S29, S31, and the acknowledgement half of S04). They hold today and nothing would
notice if a later change broke them. They are listed with that caveat rather than counted as
fully guarded.

## agent-operations

| # | Scenario | Outcome | Evidence |
| --- | --- | --- | --- |
| S01 | a deleted test file is caught | passed | `tests/test_sdlc.py` — "suite integrity: the gate cannot be lowered to pass itself" |
| S02 | a lowered threshold is caught | passed | same section; `NUM_SETTING` comparison of removed against added |
| S03 | strengthening the suite is not a finding | passed | same section — adding a test and an assertion is asserted not to be a weakening |
| S04 | a justified weakening is recorded, not waived | passed¹ | "suite integrity: an acknowledgement needs somebody behind it" — `--acknowledge` without `--as` is refused, and `suite.acknowledged` is its own audit event. ¹The *recorded, not waived* half is observed, not asserted: no test checks the finding survives the acknowledgement |
| S05 | the ceiling stops the task | passed | "budget: a ceiling an agent cannot raise for itself", extended 2026-10-31 to cover branch renames and detached HEAD |
| S06 | no ceiling configured | passed | same section — 12 calls with no ceiling produce no refusal, and `budget show` says so plainly |
| S07 | a file changed under the checkpoint | passed | "checkpoints: resuming is not automatically safe" |
| S08 | the repository still matches | passed | same section — an unchanged repository resumes and reports what is done and next |

## change-safety

| # | Scenario | Outcome | Evidence |
| --- | --- | --- | --- |
| S09 | a baseline is captured on a repository with failing tests | passed | "baseline: a failure is attributed, not assumed" |
| S10 | a baseline survives a commit | passed | "baseline: it survives commits, unlike a receipt" |
| S11 | a pre-existing failure is not blamed on the change | passed | "baseline: a failure is attributed" — classified `pre-existing` |
| S12 | a newly introduced failure is blocking | passed | same section — classified `new` |
| S13 | no baseline exists | passed | "a verify that did not run is unexecuted, not a failure of the change"; confirmed live — `sdlc baseline compare` on this branch prints "no baseline: this comparison is `unexecuted`, not passed" |
| S14 | a change to a published interface names its consumers | **unexecuted** | `sdlc-impact-analyst` is agent prose. No assertion in the suite covers it, no receipt kind records that the stage ran, and the readiness gate does not check for one. Nobody has run this against a real interface change and recorded the result |
| S15 | a verdict records what produced it | passed | "environment: a verdict records what produced it" — `env` on every receipt |

## review-breadth

| # | Scenario | Outcome | Evidence |
| --- | --- | --- | --- |
| S16 | a service with concurrent code takes both | passed | "concerns: proposed from what the repository does, never imposed" |
| S17 | detection proposes from repeated evidence | passed | same section — goroutines and mutexes propose `concurrency`; nothing unsafe means `memory` is not proposed |
| S18 | a removed concern stays removed | passed | same section — re-running `init` over a config with `concerns: []` leaves it empty |
| S19 | a performance finding from a diff | **unexecuted** | `profiles/concerns/performance.md:12` states that a `PERF-*` finding raised by reading is `medium` confidence at most. That is a sentence in a profile an agent reads. Nothing enforces it: `finding write --rule PERF-N-PLUS-ONE --confidence high` is accepted today |
| S20 | a finding under an unlisted rule | passed | "findings: the contract is enforced, not assumed" — an unknown `ruleId` is refused; and "every rule an agent cites resolves to the control spec" |

## engineering-controls

| # | Scenario | Outcome | Evidence |
| --- | --- | --- | --- |
| S21 | a complete finding is accepted | passed | "findings: the contract is enforced, not assumed" |
| S22 | an incomplete finding is refused | passed | same section — missing summary, invented severity, invented confidence, category outside the taxonomy |
| S23 | a critical finding with low confidence is not auto-fixable | passed | "findings: the repair policy is a table, not a vibe" |
| S24 | a low-severity high-confidence finding is repaired automatically | passed | same section |
| S25 | an advisory finding is reported, not committed | passed | same section — advisory is never autofix-eligible at any confidence |
| S26 | a configured quality command fails the gate | passed | "the quality budget is wired, not merely configurable" |
| S27 | no quality command is configured | passed | same section — reported `skipped`, never `passed` |
| S28 | a reviewer cites a rule | passed | "every rule an agent cites resolves to the control spec" — every `--rule` in every agent prompt resolves to a row in `docs/control-spec.md` |

## measurement

| # | Scenario | Outcome | Evidence |
| --- | --- | --- | --- |
| S29 | a rate is reported with its basis | passed¹ | Observed live: `sdlc metrics` prints "verified repair rate 100% (23 fixed with proof / 23 repairs attempted)" and "reproducible 78% (33 carry a reproduction)". ¹The test asserts only that stage outcomes appear, not that a rate carries its basis |
| S30 | unverified fixes are called out | passed | "findings: closing says what actually happened" — closing as `unexecuted` prints "An unexecuted finding is not closed — the fix was never verified" |
| S31 | precision is asked for | passed¹ | Observed live: `sdlc metrics` ends "Detection precision and recall are NOT here: they need a corpus of seeded defects with known answers, which no repository has about itself." ¹No test asserts this; a later edit could drop the paragraph silently |

## What this verification does not establish

- It verifies the five changes against **their own scenarios**. It says nothing about the
  defects found since — the 19 findings still open at this commit.
- `verifyCmd` for this repository is its own test suite, so "the suite passes" and "the
  change is verified" share a single source of evidence. An independent check would need a
  second suite, or a seeded-defect corpus. `docs/maturity.md` says how.
- No baseline exists for this branch, so no comparison distinguishes a failure this work
  introduced from one that was always there. The branch predates `sdlc baseline capture`
  being wired into the branch-opener; capturing one now would record the current state as
  the baseline, which proves nothing.
- S14 and S19 are the two scenarios this pipeline specified and did not build a way to check.
  Both are review-level by design. Saying so is the point of recording them as `unexecuted`
  rather than quietly as passed.
