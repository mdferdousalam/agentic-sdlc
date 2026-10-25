# Profile: compiler

For languages, toolchains and anything whose output other people's correctness depends on.

## The specification comes before the code

- A change to what a program means changes the language specification first, in the same commit.
- A rule the checker gains bumps the semantic epoch; a runtime contract change bumps the ABI; a
  changed machine-readable shape bumps its schema's major version — or the commit says why not.
- A new refusal gets a **new** diagnostic code. Codes are never reused or repurposed. The
  message names the construct and, where the compiler can tell, the fix.
- An unsupported construct is refused by name, never misparsed and never silently ignored.

## One semantics

Backends and profiles may **refuse**; they may never reinterpret the language. No silent
fallback — not to an interpreter, not to another backend, not to weaker verification. A
mechanism added only to turn a status row green is a defect.

## Evidence

- A successful compile, a test count, a self-reproduction fixpoint or a mutation count is not by
  itself proof.
- Differential agreement is not correctness when both paths can share the bug.
- Zero surviving mutants is not "bug-free"; it is "this catalogue found nothing".
- Statuses in a capability matrix cite the evidence that supports them, or they are not statuses.

## Bounded workloads

Generated stages, self-hosting, bootstraps, fuzzing, mutation catalogues and heavy benchmarks
run only inside the project's bounded runner, one at a time. The `heavy` field in the config
states the rule; the reviewers enforce it. Measurement happens in a quiet machine, or it is not
measurement.
