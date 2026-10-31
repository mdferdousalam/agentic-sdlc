## Why

`sdlc metrics` counted receipts. It could say how many gates ran and how many passed first
time, and nothing at all about whether the pipeline was any good: whether repairs held,
whether fixes came back, how much a human had to step in, how much of the coverage was
measurement rather than reading. An agent system judged by how many issues it reports is
judged by the wrong number.

Now that findings are records rather than prose, most of what the brief asks for is
computable. One thing is not, and saying so is part of the work.

## What Changes

- Metrics report findings by severity and taxonomy domain, verified repair rate, false-fix
  rate, human-intervention rate and reproducible share.
- Detection precision and recall are explicitly *not* reported, with the method for measuring
  them written down instead.
- Four evals cover the new refusals.
- The limits are documented where someone looking for them will find them.

## Capabilities

### New Capabilities

- `measurement`: judging the pipeline by outcomes, and being explicit about the outcome it
  cannot judge.

### Modified Capabilities

<!-- none -->

## Impact

`bin/sdlc` (`cmd_metrics`), `evals/*` (four new), `docs/maturity.md`, `docs/compliance.md`,
`README.md`, `CHANGELOG.md`, and the version across every manifest.
