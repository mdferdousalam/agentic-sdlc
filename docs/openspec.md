# OpenSpec integration

[OpenSpec](https://github.com/Fission-AI/OpenSpec) is spec-driven change governance: proposals,
designs, task lists and delta specs in a layout tools can read. This pipeline uses it as the
specification engine whenever it is present, because three of its properties are things a
pipeline needs and prose cannot give.

## Why it earns its place here

**A validator.** `openspec change validate <id> --strict --json` fails on a malformed
specification. The spec reviewer runs it first and quotes the failure, so "changes-requested"
is sometimes a machine's verdict rather than a model's opinion.

**A task list that is the acceptance criteria.** `tasks.md` is one checklist item per
deliverable. The implementer ticks each in the commit that did it; the verifier maps each to
`file:line` and a test outcome; the readiness gate treats a ticked unfinished item as a blocker.
Progress stops being a feeling.

**An archive.** `openspec archive <id>` moves a landed change out of the active list, so
`openspec list` keeps describing reality rather than accumulating finished work.

## Setup

```sh
npm install -g @fission-ai/openspec    # or your package manager of choice
openspec init                          # once per repository
/agentic-sdlc:init --write             # detects openspec and sets spec.engine
```

## The mapping

| Pipeline idea | OpenSpec artefact |
| --- | --- |
| Why this work exists | `openspec/changes/<id>/proposal.md` |
| What was chosen, over what | `<id>/design.md` |
| Acceptance criteria | `<id>/tasks.md` |
| Requirements on a published capability | `<id>/specs/<capability>/spec.md` |
| Well-formed | `openspec change validate <id> --strict` |
| Done | every task ticked, in the commit that did it |
| History | `openspec archive <id>` |

## Writing `tasks.md` so the rest works

Each item must be one deliverable with an observable outcome.

> ✗ Wire up the parser
> ✓ `parse()` refuses an unterminated string with `E0012`, naming line and column, with a test

The first cannot be verified, so the verifier will mark it `unexecuted` and the gate will block.
The second tells the implementer what to build, the test author what to assert, and the verifier
what to look for.

## Without OpenSpec

`spec.engine` falls back to `prd-frd`: a PRD (what and why) and an FRD with numbered `FR-n` and
`AC-n`. Everything downstream behaves identically — the verifier addresses requirements by
identifier either way. Adopt OpenSpec when you want the validator and the archive; the pipeline
does not require it.
