# Concern: memory and resources

Taxonomy domain **F** (memory, resources and lifecycle management). Rules in the `MEM-*`
namespace.

Enable with `"concerns": ["memory"]`. Checked by `sdlc-code-reviewer`.

## What this concern can and cannot do

A leak is usually proved by allocation evidence over time, not by reading. A `MEM-*` finding
raised from the diff is `medium` confidence; a sanitiser, a heap profile or a soak test makes
it `high`. Say which you have.

## Ownership and lifetime

- Every resource has one owner and one release point. Two owners is a double free; none is a
  leak.
- A resource acquired in a function is released on **every** exit from it, including the error
  path, the early return and the cancellation. "Cleanup at the end" is not cleanup if the
  function can return before the end.
- Prefer the language's scope-bound release — RAII, `defer`, `with`, `try`-with-resources,
  `using`. A manual close that a future edit can step over is a defect waiting for a
  maintainer.

## Files, sockets, handles, connections

- Every open has a close on the failure path. Connection pools, file descriptors and watchers
  are the three that leak quietly for weeks.
- A pool states its maximum, its timeout and what happens when it is exhausted.

## Unbounded growth

- A collection, queue, buffer, cache or map that only ever grows is `MEM-UNBOUNDED` and is
  blocking. Name the eviction policy or the bound.
- A retained reference that outlives its usefulness — a listener never removed, a closure
  capturing a large object, a static registry nobody prunes — is the ordinary cause of "memory
  grows until restart".
- Recursion over user-controlled depth exhausts the stack. Bound it or make it iterative.

## Memory safety, where the language allows it

- Use-after-free, double free, dangling references, out-of-bounds access and buffer overflow
  are `critical`. They do not get an `advisory`.
- Any `unsafe` block, raw pointer arithmetic, manual lifetime or foreign-function boundary
  states the invariant it is upholding, in a comment, in the same commit.
- Integer overflow before an allocation size is a memory-safety bug, not an arithmetic one.

## The tool beats the opinion

AddressSanitizer and LeakSanitizer, Valgrind, Miri (Rust), `go test -race` plus `pprof` heap
profiles, `tracemalloc` (Python), heap snapshots in a browser. One soak run in `quality.cmd`
beats every paragraph above.
