# Profile: webapp

For product applications with users, an admin surface and a database. Adds these standards to
the core rules. They are checked by `sdlc-spec-reviewer` and `sdlc-code-reviewer`.

## Configurability

Anything a non-engineer will want to change — a threshold, a label, a fee, a rate, a status
name, an email template, a feature flag — is read from configuration or a reference table, and
is editable through the admin surface. A literal in code for one of these is a blocking finding.

The specification must say which values are configurable. A spec that hardcodes one is
`changes-requested`.

## Data model

- A new table or column states its purpose, its nullability, its indexes and its retention.
- Reference data lives in reference tables, not in enums compiled into the application, unless
  the value is part of the code's own logic.
- Every migration is reversible, or says explicitly why it is not, and is tested against a
  database with representative data — not an empty one.
- No destructive migration without an explicit, separately approved step.

## Interface and accessibility

- Every interactive element is reachable and operable by keyboard, and has an accessible name.
- Colour is never the only carrier of meaning; contrast meets WCAG AA.
- Every form field has a label, an error state, and a described validation rule.
- Loading, empty, error and permission-denied states exist for every view that can reach them.

## Multi-tenancy and authorisation

- Every query that reads tenant data is scoped by tenant, and there is a test that a second
  tenant cannot read the first's.
- Authorisation is checked on the server for every mutation, not only hidden in the interface.

## Performance

- No query inside a loop over user-controlled length; no unpaginated list endpoint.
- A new index accompanies a new filter or sort on a table expected to grow.
