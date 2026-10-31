## Context

`verifyCmd` is an arbitrary shell command in an arbitrary stack. The pipeline cannot parse its
output into structured test results without knowing the runner, and the whole design holds that
only `sdlc.config.json` knows the stack.

## Goals / Non-Goals

**Goals:**

- Attribute a failure correctly without knowing the test framework.
- Surface downstream breakage before the implementer writes code.
- Tell an environmental failure apart from a defect.

**Non-Goals:**

- Parsing any specific test runner's output format.
- A call graph. Impact analysis here is textual and honest about being so.
- Replacing `sdlc trace`, which is the retrospective view and stays.

## Decisions

- **Compare signal lines, not parsed results.** The baseline stores the exit code plus the set
  of output lines that look like a failure or a warning, normalised to drop timings, durations,
  temporary paths, memory addresses and line/column numbers — the parts that change between two
  runs of the same unchanged code. Set difference then answers "new since the baseline" for any
  runner. It is a heuristic over text and the output says so; the alternative is a parser per
  framework, which contradicts the one-adapter design.
- **The baseline belongs to a merge base, not to a commit.** A receipt is void after the next
  commit, which is right for a verdict and wrong for a baseline: the baseline must survive every
  commit on the branch, or it is useless by the second one. It is keyed to the base it was taken
  at and is stale only when the base moves.
- **The impact analyst is read-only and separate from code review.** Reviewing a diff and
  finding its dependents are different searches; folding the second into the first means it gets
  skipped whenever the diff is interesting.
- **The environment fingerprint is computed once per process and cached.** Version probes are
  subprocesses; a receipt write should not pay for six of them twice.

## Risks / Trade-offs

- Normalisation can over-scrub and hide a real difference, or under-scrub and report noise. The
  full output of both runs is kept so a human can check.
- A textual impact analysis misses dynamic dispatch and reflection. The agent is told to say so
  rather than imply completeness.
