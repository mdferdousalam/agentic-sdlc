## 1. The concern profiles

- [x] 1.1 `profiles/concerns/architecture.md` — domains B and J.
- [x] 1.2 `profiles/concerns/performance.md` — domains E and N.
- [x] 1.3 `profiles/concerns/memory.md` — domain F.
- [x] 1.4 `profiles/concerns/concurrency.md` — domain G.
- [x] 1.5 `profiles/concerns/data.md` — domain K and the data half of X6.
- [x] 1.6 `profiles/concerns/platform.md` — domain S and the toolchain half of X8.
- [x] 1.7 Each names its deterministic tool and caps the confidence of a read finding.

## 2. Selection

- [x] 2.1 `concerns` in the config schema, multi-valued, documented beside `profile`.
- [x] 2.2 `sdlc init` proposes concerns from two or more independent matches in tracked source.
- [x] 2.3 Re-running `init` never re-imposes a removed concern.

## 3. Review

- [x] 3.1 `agents/sdlc-architecture-reviewer.md` walks the import graph, prefers the project's
      linter, and reports `ARCH-UNDECLARED` when the project states no structure at all.
- [x] 3.2 The code, spec and security reviewers read the named concerns.
- [x] 3.3 The readiness gate fans out to the architecture reviewer when the concern is enabled.
- [x] 3.4 28 concern rules added to the control specification's table.

## 4. Proof

- [x] 4.1 Tests: detection proposes and does not impose; every concern file exists; every rule
      cited anywhere resolves to the table.
- [x] 4.2 The repository's own `verifyCmd` passes.
