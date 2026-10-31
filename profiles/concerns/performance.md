# Concern: performance

Taxonomy domains **E** (performance and computational efficiency) and **N** (scalability and
capacity). Rules in the `PERF-*` namespace.

Enable with `"concerns": ["performance"]`. Checked by `sdlc-code-reviewer`.

## What this concern can and cannot do

It reviews code against standards. **It does not measure.** A performance claim without a
representative workload is an opinion, and this file will not let a reviewer pretend otherwise:
every `PERF-*` finding raised by reading is `medium` confidence at most. Measurement is a
benchmark in `quality.cmd`, or it has not happened.

## Complexity and work per request

- A loop nested inside a loop over user-controlled length is a finding. State the complexity
  and the input size at which it stops being acceptable.
- Work that does not depend on the input belongs outside the loop; work that does not depend on
  the request belongs outside the request.
- A new allocation, copy or serialisation on a hot path needs a reason. Passing by value what
  could be borrowed, re-serialising what is already serialised, and parsing the same
  configuration per call are the usual three.

## Data access

- A query inside a loop is `PERF-N-PLUS-ONE` and is blocking. The fix is one query, not a cache.
- Every list endpoint is paginated. An unpaginated query over a table expected to grow is
  blocking, however small the table is today.
- A new filter or sort on a growing table arrives with its index, or with the reason it does not
  need one.
- A cache needs three answers before it is an improvement: what invalidates it, what happens on
  a miss storm, and what a stale read costs. Without them it is a correctness bug with better
  latency.

## Network and I/O

- Round trips in series that could be in parallel; payloads that carry fields nobody reads;
  a retry policy with no jitter. Each is a finding with a named fix.
- Blocking I/O on an asynchronous path blocks everything sharing that thread. Name the call.

## Scale

- State the limit: at what concurrency, queue depth, connection count or data volume does this
  stop working? "It scales" is not an answer, and neither is silence.
- Unbounded concurrency, unbounded queue growth and connection-pool exhaustion are blocking.
- A hot partition — a tenant, a key, a shard taking disproportionate traffic — is a design
  finding, not an operations problem.

## The tool beats the opinion

`cargo bench` / criterion, `go test -bench` and `pprof`, `hyperfine`, `pytest-benchmark`,
Lighthouse or `bundlesize` for the web, `EXPLAIN ANALYZE` for a query. Put the one that fits in
`quality.cmd` with a budget, and a `PERF-*` finding can finally be `high` confidence.
