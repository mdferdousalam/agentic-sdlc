## Context

Reviewers emit markdown. The readiness gate reads that markdown and rules on it. Nothing between
the two is machine-readable, so `sdlc metrics` can only count receipts, and the repair stage has
no policy to consult about what it may fix on its own.

## Goals / Non-Goals

**Goals:**

- One finding shape, validated, that any agent or tool can emit.
- Severity and confidence as independent axes, because a low-confidence fix for a critical
  finding is not safe merely because an agent is sure.
- One document that is normative for every reviewing agent.
- Close the `quality.cmd` gap.

**Non-Goals:**

- Shipping an analyser. `quality.cmd` is a seam; the project supplies the tool.
- Replacing the five evidence words. Those describe a criterion; findings need their own.
- Detection precision and recall metrics — those need a seeded-defect corpus, not a schema.

## Decisions

- **Hand-written validator, not a dependency.** `bin/sdlc` is standard-library only and offline.
  The JSON Schema is the contract for editors and CI; `bin/sdlc` enforces the same constraints
  in code. Two expressions of one contract, so a test keeps them honest.
- **Finding outcomes extend the remediator's existing four words** (`fixed`, `refused`,
  `deferred`, `unexecuted`) with `open` and `escalated`, rather than inventing a third
  vocabulary.
- **`autofixEligible` is derived from the policy table, not chosen by the agent.** An agent that
  sets it outside the table is making a decision it does not own.
- **Findings live in `.sdlc/findings/`**, local to a working copy like receipts, with the same
  honest limit: a determined actor can delete them.

## Risks / Trade-offs

- A structured finding is more work per finding. Mitigated by keeping the required fields to
  what a reviewer already had to know, and leaving the rest optional.
- Two copies of the contract (schema and validator) can drift. Mitigated by a test that feeds
  the schema's own examples through the validator.
- A rule table invites rule inflation. The table only carries rules something actually checks.
