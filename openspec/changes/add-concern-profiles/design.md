## Context

`profile` is a single string naming a kind of project. Six whole taxonomy domains have no
coverage, and they do not divide along project kinds.

## Goals / Non-Goals

**Goals:**

- Cover B, E, F, G, J, K, N, S as review standards.
- Let a project take `service` and `concurrency` at once.
- Be explicit about the difference between reading code and measuring it.

**Non-Goals:**

- Shipping analysers, profilers, race detectors or benchmarks.
- One agent per domain. The brief is explicit that 226 agents is the wrong shape.

## Decisions

- **Two axes, not one longer list.** `profile` stays a single project kind; `concerns` is a
  list. Collapsing them would force a false choice between `service` and `concurrency`.
- **Five of six concerns are read by the reviewers that already exist.** Only architecture gets
  an agent, because finding dependents means walking an import graph rather than reading a
  diff — folded into code review, it is skipped exactly when the diff is interesting.
- **`init` proposes, never imposes.** Two independent matches in tracked source suggest a
  concern; one is a coincidence. A concern the maintainers did not choose produces noise on
  every review, and a noisy review tool gets switched off — that is the brief's X9.
- **Every concern names its deterministic tool and caps its own confidence.** A `PERF-*` or
  `MEM-*` finding from a diff is `medium` at best, and the profile says so in those words. The
  alternative — review prose that reads like measurement — is worse than no coverage, because
  the gate would believe it.
- **Concern rules go in the control spec's table.** `sdlc finding write` validates `ruleId`
  against that table, so a rule in a prompt but not in the table is refused at the point of
  use. A test asserts every rule any agent or profile cites resolves.

## Risks / Trade-offs

- Six more files of standards is more for a reviewer to hold. Mitigated by opt-in: a project
  that enables none is exactly as it was.
- Detection heuristics will mis-propose. Mitigated by proposing rather than imposing, and by
  `init` never re-adding a concern the maintainer removed.
