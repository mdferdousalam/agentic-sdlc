## Context

The brief separates defects in software from failures in how agents develop software. The
pipeline had strong controls on the first and prose on the second.

## Goals / Non-Goals

**Goals:**

- Make suite weakening mechanically detectable.
- A ceiling that stops a task, not a number that describes it afterwards.
- Resumption that re-checks its assumptions.

**Non-Goals:**

- Token accounting. This process cannot see the host's meter, and a number it cannot measure
  would be a lie with a decimal point.
- Semantic analysis of whether a test is "good". The check is about what the diff removed.

## Decisions

- **The suite audit over-reports deliberately.** It is textual, so it will flag correct
  changes. A false positive costs one sentence in a commit message; a false negative costs a
  silently disarmed suite. The output says each finding may be correct and none is correct by
  default, and `--acknowledge` records a human decision rather than waiving the finding.
- **`--acknowledge` records, it does not waive.** The reviewers still see it. A flag that made
  the finding disappear would be the same hole one level up.
- **The budget counts observable things.** Tool calls through the hook and wall-clock since the
  task began. Both are real, both are enforced in `guard_problem` beside every other refusal,
  and only a person resets them.
- **The budget is checked last in the guard**, so a destructive command is still refused for
  the right reason when the budget also happens to be spent.
- **A checkpoint stores the state it assumed, not just the plan.** `resume` re-checks branch,
  commit ancestry, file digests and toolchain — the same discipline `receipt_problem` already
  applies, reusing `subject_digest` rather than inventing a second validator.

## Risks / Trade-offs

- The audit's patterns are language-specific and will miss stacks they do not cover. Adding a
  pattern is one tuple; the cost of a miss is bounded by the reviewers still reading the diff.
- A tool-call ceiling can interrupt legitimate long work. It is unset by default, and the
  refusal names the reset command.
