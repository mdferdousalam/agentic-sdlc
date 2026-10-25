---
name: openspec-with-sdlc
description: >
  How the SDLC pipeline uses OpenSpec as its specification engine — creating a change,
  validating it, turning tasks.md into acceptance criteria, and archiving after landing. Use
  when a repo has openspec/ or spec.engine is "openspec", or when asked how OpenSpec and the
  pipeline fit together.
---

# OpenSpec as the pipeline's spec engine

When `spec.engine` is `openspec`, the specification is an OpenSpec change rather than a PRD and
an FRD. The pipeline gains three things from it: a layout other tools understand, a validator
that fails on a malformed spec, and an archive step that keeps "what is proposed" honest.

## The mapping

| Pipeline idea | OpenSpec artefact |
| --- | --- |
| Why this work exists | `openspec/changes/<id>/proposal.md` |
| What was chosen, and over what | `<id>/design.md` |
| The acceptance criteria | `<id>/tasks.md` — one checklist item per deliverable |
| Requirements on a published capability | `<id>/specs/<capability>/spec.md` |
| The spec is well-formed | `openspec change validate <id> --strict` |
| The work is done | every `tasks.md` item ticked, in the commit that did it |
| The change is history | `openspec archive <id>` |

## The commands that matter

```sh
openspec list                              # active changes — check before proposing
openspec list --specs                      # published capabilities
openspec change show <id>                  # read one
openspec change validate <id> --strict     # the spec reviewer runs this first
openspec archive <id>                      # the reporter runs this after landing
```

`openspec change validate --strict --json` is machine-readable: a failure is an automatic
`changes-requested` and the reviewer quotes it rather than paraphrasing.

## Writing tasks.md so the rest of the pipeline works

`tasks.md` is not a to-do list; it is the acceptance criteria the verifier and the readiness
gate check against. Each item must name **one deliverable with an observable outcome**. "Wire up
the parser" cannot be verified. "`parse()` refuses an unterminated string with error `E0012`,
with a test" can.

The implementer ticks each item in the same commit as the work; the verifier maps each item to
`file:line` plus a test outcome; the readiness gate treats an unticked finished item as
sloppiness and a ticked unfinished item as a blocker.

## Archiving

Archive only after the change has landed and its delta specs are reflected in the published
ones. `openspec list` should show what is genuinely in flight — a finished change left active
is a lie the next session will believe.
