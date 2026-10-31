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

## What this still does not give you

Being specific about the gaps is part of the tool. Each of these is real, each is named in the
research this pipeline is built from, and none of them can be honestly claimed by a package of
markdown and one dependency-free script.

**Detection precision and recall.** `sdlc metrics` reports what the pipeline *did*, never how
much it *missed*. Precision and recall need a corpus of seeded defects with known answers, and
no repository has that about itself. If you need the numbers: take a tagged commit, inject a
set of defects you choose — an off-by-one, a missing authorization check, an unbounded
collection, a race — run the pipeline against each, and count what it found and what it
invented. Run it again when you change a prompt. Without that, "the reviewers are good" is an
impression.

**Runtime evidence.** Profiling, allocation tracing, race detection under load, fuzzing,
mutation testing and fault injection all need to *run* the system under conditions this tool
does not create. The concern profiles name the tool for each and point at the `quality.cmd`
seam; putting one there is what turns a `medium`-confidence reading into a `high`-confidence
measurement. Until you do, `PERF-*`, `MEM-*` and `CONC-*` findings are careful opinions.

**Token and money accounting.** `budget` counts tool calls and wall-clock because those are
observable from inside a repository. It cannot see your host's token meter. A ceiling that
stops the work is worth more than a number that describes the overspend afterwards, but it is
not the same thing as cost control, and this does not pretend otherwise.

**Workspace isolation at scale.** `git worktree` separates two tasks. It does not sandbox an
agent's filesystem or network, and the hook is not a security boundary against a process that
simply does not call it. See `docs/compliance.md`.

**Anything outside the repository.** Incident response, on-call, vendor risk, organisational
policy, training, and the people who have to live with a bad deploy.

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
- **`unexecuted` findings accumulating** → fixes are being declared without being proved. This
  is the number that quietly becomes a lie, because every one of them *looks* closed.
- **False-fix rate above zero** → work is coming back after being closed `fixed`. One is
  normal; a trend means the verification step is not verifying.
- **Reproducible share falling** → findings are increasingly claims rather than observations,
  and the repair policy will escalate more of them. That is the policy working, and a sign the
  reviewers need a deterministic tool rather than more prompt.
- **`sdlc tests audit` firing often** → the gate is being treated as an obstacle rather than a
  standard. Find out why before raising the threshold back.
