# Concern: concurrency

Taxonomy domain **G** (concurrency and parallelism). Rules in the `CONC-*` namespace.

Enable with `"concerns": ["concurrency"]`. Checked by `sdlc-code-reviewer`.

## What this concern can and cannot do

Concurrency defects are the ones least visible to reading and least reliably caught by tests:
they are timing-dependent, so a passing suite is weak evidence. A `CONC-*` finding from the
diff is `medium` confidence. A race detector, a stress run or a deterministic scheduler makes
it `high`. **A test that passed once has not shown the absence of a race.**

## Shared state

- Every piece of state reachable from two threads is either immutable, owned by one of them, or
  behind a lock — and the diff says which.
- A data race is `high` severity even when the window looks small. Small windows are what
  production load is for.
- "It is only read concurrently" is only safe if nothing writes it, ever, including at startup.

## Locks

- State the lock order wherever two locks can be held at once. Inconsistent order is a deadlock
  waiting for the right interleaving.
- No I/O, no blocking call, no callback into unknown code while holding a lock.
- A read-modify-write that looks atomic because it is one line is not atomic. Name the
  operation that makes it so.
- Lock contention on a hot path is a performance finding; see `concerns/performance`.

## Time-of-check to time-of-use

- Check-then-act on anything shared — a file, a row, a flag, a balance — is `CONC-TOCTOU`.
  Make it one atomic operation, or state why the window is harmless.
- `exists()` then `open()`, `select` then `update`, "is it free?" then "take it" — the three
  that recur.

## Asynchrony

- Every spawned task is awaited, joined or deliberately detached with a comment saying so. A
  task nobody holds is a leak and swallows its own failure.
- Every unhandled rejection or dropped future is a failure you will never hear about.
- Cancellation propagates: a cancelled parent cancels its children, and cleanup still runs.
- Every timeout has a value, and every value has a reason. "No timeout" is a policy, and
  usually the wrong one.
- Backpressure is stated: what happens when the producer outruns the consumer? An unbounded
  channel answers "we crash later".

## Ordering

- Do not assume completion order, scheduling order or message order unless the mechanism
  guarantees it. Write down which guarantee you are relying on.
- Idempotency: anything that can be retried says what a duplicate does.

## The tool beats the opinion

`go test -race`, ThreadSanitizer, Loom (Rust), `-fsanitize=thread`, Lincheck (JVM),
deterministic-simulation or stress harnesses. Put one in `quality.cmd` and run it repeatedly —
once is not a run.
