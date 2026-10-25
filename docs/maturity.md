# The four levels, and how to configure each one

Adopting this pipeline is not a switch. The industry framing that holds up best describes the
human's role changing as a platform matures — from executor, to validator, to orchestrator, to
constraint-setter. The stages do not disappear; what changes is who initiates them and what
governs the handoff.

Here that is not an abstraction: each level is a configuration. Start at the level that matches
the trust you actually have, and move up when the metrics say you have earned it.

## Level 1 — the human executes, agents assist

You direct the work and approve each step. The pipeline runs, but you are inside every stage.

```jsonc
{ "approvals": { "merge": "human", "release": "human" },
  "enforce": { "pushToTrunkNeedsGate": true, "mergeNeedsReadiness": true,
               "branchNeedsApprovedSpec": false } }
```

Specifications are optional here; the refusals that protect your working tree are not. Use
`/agentic-sdlc:feature` by hand, read every diff.

**Move up when:** you stop finding surprises in the diffs.

## Level 2 — the human validates

Agents produce whole units of work; you verify behaviour rather than inspect every line. This
is where the pipeline starts to pay for itself, and where most teams should sit.

```jsonc
{ "approvals": { "merge": "human", "release": "human" },
  "enforce": { "branchNeedsApprovedSpec": true, "mergeNeedsReadiness": true },
  "reviewers": ["sdlc-code-reviewer", "sdlc-security-reviewer"],
  "quality": { "cmd": "<your static analysis>", "coverageNewPct": 80 } }
```

The specification becomes mandatory, because at this level an unclear intent does not slow
someone down — it produces a confident, wrong pull request. Validation becomes a loop:
candidate → gate → failure routed back as enriched context → retry. `sdlc feedback` is what
makes the retry smarter than the attempt before it.

**Move up when:** `sdlc metrics` shows the gate passing first-time more often than not, and the
refusals that fire are near-misses rather than workflow problems.

## Level 3 — the human orchestrates

Agents run long tasks unattended. Work arrives from signals — a failing dependency check, an
advisory, a pattern in production telemetry — through `/agentic-sdlc:triage`. You set the rules
and review the exceptions.

```jsonc
{ "approvals": { "merge": "agent", "release": "human" },
  "enforce": { "branchNeedsApprovedSpec": true, "mergeNeedsReadiness": true },
  "release": { "deployCmd": "...", "smokeCmd": "...", "rollbackCmd": "...",
               "environments": ["staging", "production"] } }
```

Merging becomes rule-based for work that passed every gate; **deployment stays human**. The
constraint stops being review bandwidth and becomes the quality of your gates: at this level
the readiness gate is the only thing between an agent and your trunk, so a gate that does not
really check is now a direct risk rather than a missed opportunity.

**Move up when:** your post-deploy evidence is good enough that you would trust a rollback
decision made without you. Most teams should not.

## Level 4 — the human sets constraints

Paths run from signals without a human trigger, inside boundaries you defined. This is a
horizon, not a destination to rush: it requires evaluation infrastructure, workspace isolation,
cost governance and incident response that most organisations have not built. This plugin gives
you the gates and the audit trail; it does not give you those.

Be honest about where you are. Running at level 3 with level 1 gates is not maturity, it is
unmanaged risk with better vocabulary.

## What to watch as you climb

```sh
sdlc metrics --since 2026-01-01
```

- **First-pass gate rate rising** → the specifications are getting clearer.
- **First-pass rate at 100%** → your gate is not checking anything. That is a finding.
- **The same refusal firing repeatedly** → a workflow problem, not a near-miss. Fix the
  workflow, do not relax the rule.
- **Blocking findings rising while velocity rises** → the verification debt the research warns
  about. Slow down before it compounds.
