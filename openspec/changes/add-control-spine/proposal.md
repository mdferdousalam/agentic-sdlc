## Why

The pipeline's findings are prose. A reviewer writes "blocking" or "non-blocking" and nothing
else is recorded: no severity, no confidence, no rule identity, no provenance. That makes three
things impossible at once — a repair policy (what may an agent fix unattended?), outcome metrics
beyond counting receipts, and any shared standard between reviewers, who currently each decide
for themselves what matters.

There is also a dangling control: `quality.cmd` and `quality.coverageNewPct` are in the config
schema, documented as the Level 2 configuration, and `quality` is a reserved receipt kind — but
no agent or command ever runs them. The deterministic-analysis budget is advertised and inert.

## What Changes

- A finding becomes a validated record with an identity, a rule, severity, confidence,
  evidence, a root cause and provenance.
- Severity and confidence become separate vocabularies, and a repair policy maps the pair of
  them to what an agent is allowed to do.
- One versioned control specification holds the vocabularies, the repair policy, the taxonomy
  coverage map and the rule table, so no agent invents its own standard.
- The readiness gate and the mechanical gate run `quality.cmd` and record a `quality` receipt.

## Capabilities

### New Capabilities

- `engineering-controls`: the shared vocabularies, the repair policy, the finding record, and
  the deterministic quality budget that every reviewing and repairing stage is held to.

### Modified Capabilities

<!-- none: no published capability changes its requirements -->

## Impact

`schema/finding.schema.json` (new), `docs/control-spec.md` (new), `docs/rules.md`, `bin/sdlc`
(new `finding` subcommand, `RECEIPT_KINDS`, doctor), `agents/sdlc-readiness-gate.md`,
`agents/sdlc-code-reviewer.md`, `agents/sdlc-security-reviewer.md`, `agents/sdlc-remediator.md`,
`commands/gate.md`, `tests/test_sdlc.py`.
