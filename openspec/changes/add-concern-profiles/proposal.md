## Why

The reviewers cover requirements, security, testing and governance well, and cover architecture,
performance, memory, concurrency, data integrity and platform correctness not at all. Those six
are most of the defect taxonomy by volume, and they are where an agent-written change is most
likely to be confidently wrong.

They cannot go in the core, because the core is stack-agnostic and a rule like "no query inside
a loop" is meaningless for a compiler. The existing `profile` field is the natural home, except
that it holds one value and names a *kind* of project — and these are not kinds. A Go service
needs `service` and `concurrency`; making that one choice means losing half of what you need.

## What Changes

- `concerns` joins `profile` as a second, multi-valued axis: cross-cutting standards applied in
  addition to the project kind.
- Six concern profiles cover taxonomy domains B, E, F, G, J, K, N and S.
- Each names the deterministic tool for the stacks that have one, and is explicit that a
  finding raised by reading is not a measurement.
- A dedicated architecture reviewer, because reading an import graph is a different search from
  reading a diff.

## Capabilities

### New Capabilities

- `review-breadth`: the cross-cutting standards a review is held to, selected per project, and
  honest about which of them are measured and which are read.

### Modified Capabilities

<!-- none -->

## Impact

`profiles/concerns/*.md` (new, six), `agents/sdlc-architecture-reviewer.md` (new),
`schema/sdlc.config.schema.json`, `bin/sdlc` (concern detection), `docs/control-spec.md`
(28 concern rules), `agents/sdlc-code-reviewer.md`, `agents/sdlc-spec-reviewer.md`,
`agents/sdlc-security-reviewer.md`, `agents/sdlc-readiness-gate.md`, `profiles/README.md`,
`docs/configuration.md`, `README.md`, `sdlc.config.json`, `tests/test_sdlc.py`.
