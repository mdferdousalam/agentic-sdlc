# Concern: data integrity

Taxonomy domain **K** (database and data integrity), and the data half of **X6** (product and
operational correctness). Rules in the `DATA-*` namespace.

Enable with `"concerns": ["data"]`. Checked by `sdlc-code-reviewer` and `sdlc-spec-reviewer`.
Overlaps `profiles/webapp` deliberately: a service with a database needs these whether or not
it has an admin surface.

## What this concern can and cannot do

A constraint that exists only in code, a transaction boundary that is wrong, an idempotency
key that is missing — these are visible by reading. Whether the migration actually reverses,
and whether the constraint holds under concurrent writes, are not. A `DATA-*` finding raised
from the diff is `medium` confidence; a migration run forward and back against representative
data, or a test that races two writers, makes it `high`. Say which you have.

## Schema

- A new table or column states its purpose, its nullability, its default, its indexes and how
  long the data is kept. A column whose retention nobody can state is a future compliance
  question.
- A constraint belongs in the database, not only in the application. Two applications will
  eventually write to that table, and one of them will be a migration script.
- Nullable-by-default is a decision. Make it deliberately or not at all.

## Transactions

- State the boundary: what is inside the transaction and what is outside. A side effect inside
  a transaction that can be retried will happen twice.
- State the isolation level where it matters, and what anomaly you are accepting. Read-committed
  is a choice with consequences, not a default to inherit silently.
- Lost update, dirty read and write skew each have a fix — a constraint, a lock, a version
  column. Name which one this code relies on.
- No network call inside a transaction.

## Migrations

- Every migration is reversible, or says in the same commit why it is not and what rolling back
  would lose. `DATA-MIGRATION-IRREVERSIBLE` is not a blocker by itself; an unstated one is.
- Forward and backward compatible across one deploy, or the specification states the ordered
  steps: add the column, backfill, start writing, start reading, stop writing the old one, drop
  it. Shipping those as one step is the usual outage.
- Tested against a database with representative data. An empty database proves the syntax.
- A destructive migration — a drop, a truncate, a type narrowing — is a separately approved
  step. The release stage must know about it before deploying, not during.

## Correctness of the data itself

- Idempotency: anything a client may retry states its key and what a duplicate does. Duplicate
  payments and duplicate orders are this finding, not a support ticket.
- Partial writes are impossible, or the recovery path is specified and tested.
- Money is not a float. Time is stored with its zone, or in UTC with that stated. A date is not
  a timestamp. Rounding is specified where it is visible to a user.
- Deletion means deletion where someone asked for it: soft-delete that leaves the data readable
  does not satisfy a deletion request, and the specification should say which one this is.

## The tool beats the opinion

`sqlc`/`sqlx` compile-time checks, `EXPLAIN ANALYZE`, migration linters (`squawk`,
`atlas lint`), property tests over invariants, and a restore drill. A backup nobody has
restored is not a backup.
