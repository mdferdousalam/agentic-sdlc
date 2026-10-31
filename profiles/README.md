# Profiles — the opinions that are not universal

The pipeline core is stack-agnostic on purpose. A profile is where a *kind* of project's
standards live, applied only when `"profile"` in `sdlc.config.json` names it.

This separation is deliberate. A rule like "no hardcoded value that the spec marked
configurable" is right for an admin-driven web application and meaningless for a compiler.
Baking it into the core would make the core lie about being stack-agnostic, and would make
every reviewer on every other kind of project produce noise.

| Profile | For | Adds |
| --- | --- | --- |
| `webapp` | product applications with an admin surface | configurability, data model, accessibility, migration safety |
| `library` | published packages and SDKs | public API compatibility, semver, documentation of every exported symbol |
| `service` | long-running network services | operability, failure modes, observability, backpressure |
| `compiler` | language and toolchain projects | specification-first, evidence vocabulary, bounded heavy workloads |

## The second axis: concerns

A project kind is one choice. **Concerns are not** — they cut across kinds. A Go service needs
`service` *and* `concurrency`; a Rust compiler needs `compiler` *and* `memory`. Forcing those
into one field would make you pick the less useful half, so they are a separate list:

```jsonc
{ "profile": "service", "concerns": ["concurrency", "data", "performance"] }
```

| Concern | Taxonomy | Adds |
| --- | --- | --- |
| [`architecture`](concerns/architecture.md) | B, J | dependency direction, cycles, boundaries, indirection that does not pay |
| [`performance`](concerns/performance.md) | E, N | complexity, N+1, pagination, caching, round trips, scale limits |
| [`memory`](concerns/memory.md) | F | ownership, lifetimes, cleanup on every exit, unbounded growth, safety |
| [`concurrency`](concerns/concurrency.md) | G | races, lock order, TOCTOU, task leaks, cancellation, backpressure |
| [`data`](concerns/data.md) | K, X6 | constraints, transaction boundaries, reversible migrations, idempotency |
| [`platform`](concerns/platform.md) | S, X8 | host assumptions, numerics, encoding, locale, shutdown, toolchain pinning |

`sdlc init` *proposes* concerns from what the repository evidently does — goroutines and mutexes
suggest `concurrency`, migrations suggest `data`. It never imposes one. A concern the
maintainers did not choose produces noise on every review, and a review tool that produces noise
gets switched off.

Each concern file ends by naming the **deterministic tool** for the stacks that have one, and
saying it belongs in `quality.cmd`. Until it is there, every finding the concern raises is a
reading rather than a measurement, and the profiles say so in those words: a `PERF-*` or
`MEM-*` finding from a diff is `medium` confidence at best. This plugin ships no analysers and
will not pretend to.

## Writing your own

Either axis is one markdown file of standards the reviewers read in addition to the core rules.
Keep it to what a reviewer can check, and give each rule an ID in `docs/control-spec.md` — a
rule that lives only in a prompt is an opinion.
