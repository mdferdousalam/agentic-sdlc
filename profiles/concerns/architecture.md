# Concern: architecture

Taxonomy domains **B** (architecture and system structure) and **J** (design patterns and
engineering principles). Rules in the `ARCH-*` namespace.

Enable with `"concerns": ["architecture"]`. Checked by `sdlc-architecture-reviewer` and by
`sdlc-spec-reviewer` when a change proposes a new boundary.

## Dependency direction

- The project's layers are named somewhere — a README, a module graph, a lint rule. If they are
  not, that absence is the first finding: an unwritten architecture cannot be violated, only
  eroded.
- Dependencies point one way. A lower layer that imports an upper one is `ARCH-LAYER-DIRECTION`,
  and it is `high` severity even when it compiles: it is how a codebase stops being separable.
- A new import that crosses a boundary the project declared forbidden is blocking. "It was
  easier" is not an exception; the exception is a specification that changes the boundary.

## Cycles and coupling

- A new import cycle between modules is `ARCH-CYCLE`. Report it as a path, not as a claim.
- A module that imports more than it is imported by, and keeps growing, is becoming a god
  object. Name it while it is still one finding rather than twenty.
- Coupling to a concrete type where the project has an interface for exactly this is
  `advisory` unless the specification said otherwise — which is the point of the advisory
  severity: report the trade-off and let a human decide.

## Boundaries

- A component's boundary is where its invariants are enforced. If a caller can construct an
  invalid state and the component cannot tell, the boundary is in the wrong place.
- Separation of concerns is checkable: can you state what this module is for in one sentence
  without "and"? Two sentences is two modules.
- Shared mutable state across a boundary is a boundary that does not exist.

## Patterns

- A pattern applied because it is a pattern is `advisory`, not a defect. Say what it costs —
  indirection, a file to open, a name to learn — and let the maintainer weigh it.
- A factory with one implementation, a strategy with one strategy, an interface with one
  implementer and no test double: name the indirection, and the condition under which it would
  earn its place.
- Premature generalisation and premature optimisation are the same finding wearing two hats.

## The tool beats the opinion

Where the stack has one, it belongs in `quality.cmd` and the finding becomes `deterministic`:
`cargo-deny` and `cargo modules` (Rust), `go-arch-lint` and `go mod graph` (Go),
`dependency-cruiser` or `eslint-plugin-boundaries` (TypeScript), `import-linter` (Python),
ArchUnit (JVM). A reviewer's reading of an import graph is `medium` confidence at best.
