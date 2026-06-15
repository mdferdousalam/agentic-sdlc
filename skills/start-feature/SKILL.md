---
name: start-feature
description: >
  One-command entry point that drives a feature through the front of the SDLC pipeline:
  spec-writer (PRD+FRD) -> spec-reviewer -> branch-opener -> /dev-instructions. Use when asked to
  "start a feature", "kick off <feature>", or to begin work on a new module/feature.
  Args: phase=<phase-N> module=<slug> feature=<slug>.
---

# /start-feature — chain the front of the pipeline

Caps coordination cost: one invocation instead of four manual agent calls.

## Args

Parse from `$ARGUMENTS`: `phase`, `module`, `feature`
(e.g. `phase=2 module=discover-match feature=job-postings`).
If any are missing, read `<docsRoot>/MODULES_MAP.md` and propose the next `planned`
feature, then confirm before proceeding.

## Preconditions

- `sdlc.config.json` must exist. If not, stop and tell the user to run
  `/agentic-sdlc:sdlc-init`.
- Validate the inputs against the branch scheme regex before doing anything that
  mutates state.

## Sequence (stop on any failure)

1. **Spec.** Invoke the `sdlc-spec-writer` agent with `{phase, module, feature}`. It
   writes `PRD_v1.0.md` + `FRD_v1.0.md`.
2. **Review.** Invoke the `sdlc-spec-reviewer` agent on those files.
   - If `CHANGES-REQUESTED`: relay the checklist, loop back to step 1 (spec-writer
     revises), and re-review. Do not advance until `APPROVED`.
3. **Branch.** Invoke the `sdlc-branch-opener` agent. It validates the name, enforces
   doc-first, creates + pushes the branch, drafts the PR, and updates the ledgers.
4. **DI.** Invoke `/dev-instructions` to produce the Developer Instructions the implementer follows.

## Output

Summarize: spec paths, review verdict, branch name + PR URL, DI path. Then tell the
user what comes next: implement against the DI, then run `/verification-report`, the
`sdlc-readiness-gate`, and `/implementation-report` before merge.
