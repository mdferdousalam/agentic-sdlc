# Configuration reference — `sdlc.config.json`

The only file in your project that knows your stack. Written by `/agentic-sdlc:init`, validated
by [`schema/sdlc.config.schema.json`](../schema/sdlc.config.schema.json). Point your editor at
the schema for completion.

Also read from `.opencode/sdlc.json` if you prefer to keep it out of the repository root.

| Field | Type | What it does |
| --- | --- | --- |
| `trunk` | string | The branch work merges into. Detected from `origin/HEAD`. |
| `stack`, `pm`, `monorepo` | string | Detected; informational, but reviewers mention them. |
| `commits` | `conventional` \| `descriptive` | The commit style the implementer and lander follow. |
| `test` | object | Runners by kind: `{"unit":"vitest","e2e":"playwright"}`. |
| `spec.engine` | `openspec` \| `prd-frd` | Which specification form stage 1 produces. |
| `spec.docsRoot` | string | Where specifications live. |
| `spec.strict` | boolean | OpenSpec: validate with `--strict`. |
| `branchScheme` | string | Placeholders filled from the unit of work, e.g. `{kind}/{slug}`. |
| `verifyCmd` | string | **The mechanical check.** Lint, types, tests. Without it nothing can be gated. |
| `gateCmd` | string | A heavier project gate, run instead of `verifyCmd` when set. |
| `secretScan` | string | A command that fails if a credential is in the branch's commits. |
| `heavy` | string | Prose rule for workloads that must be bounded or serialised. |
| `profile` | string | The **kind** of project: `webapp`, `library`, `service`, `compiler`. One per project. |
| `concerns` | string[] | **Cross-cutting** standards from `profiles/concerns/`, applied as well: `architecture`, `performance`, `memory`, `concurrency`, `data`, `platform`. A Go service wants `service` and `concurrency`. |
| `reviewers` | string[] | Agents the readiness gate fans out to. |
| `protected` | string[] | Branches needing a passed gate before a push. Globs allowed. |
| `receipts.maxAgeMin` | integer | How long a receipt stays valid. Default 180. |
| `enforce.*` | boolean | What the hook refuses. See below. |
| `neverByAgent` | string[] | Actions reserved to a human, stated for the agents to read. |
| `budget.*` | object | Ceilings an agent cannot raise for itself: `maxToolCalls`, `maxWallClockMin`, `maxRetries`, `stopPolicy`. Unset means nothing stops a runaway task. |

## `enforce`

| Key | Default | Refuses |
| --- | --- | --- |
| `pushToTrunkNeedsGate` | true | `git push` to a protected branch without a passed `gate` receipt |
| `mergeNeedsReadiness` | true | `gh pr merge` / merge into the trunk without a READY receipt |
| `branchNeedsApprovedSpec` | true | (checked by the branch-opener) a branch without an approved spec |
| `blockDestructiveGit` | true | `stash`, `reset --hard`, `clean`, `checkout -- .`, `add -A`, `commit -a`, force-push |
| `blockPublishing` | true | `tag`, `publish`, `gh release`, `docker push` |
| `blockCredentialReads` | true | reading `.env`, keys, `~/.ssh`, `~/.aws` |

Turning one off is legitimate — a solo prototype may not want a gate — but do it in the config,
where it is visible and reviewable, not by arguing with the agent.

## Budgets, checkpoints and suite integrity

```sh
sdlc budget show                 # what this task has spent against its ceiling
sdlc budget reset --as 'name'    # a person clears it; an agent does not raise its own ceiling
sdlc tests audit                 # has this diff made the gate easier to pass?
sdlc checkpoint write --done "parser" --next "the formatter" --file src/parse.rs
sdlc checkpoint resume           # re-checks the assumptions before continuing
```

`budget` is the honest half of cost control: this process cannot see your host's token meter,
so it counts what it can observe — tool calls through the hook, wall-clock since the task
began, and repair attempts — and **refuses** at the ceiling. A ceiling that stops the work is
worth more than a token count that describes it afterwards.

`sdlc tests audit` is the mechanical form of the rule every agent prompt already states: do not
delete a test, weaken an assertion, add a skip marker, suppress a warning or lower a threshold
to make the gate pass. It reads the diff, so it over-reports by design — a false positive costs
one sentence in the pull request, a false negative costs a silently disarmed suite.

`sdlc checkpoint` stores a long task's progress *and the repository state it assumed*.
`resume` re-checks that state — branch, commit, file digests, toolchain — before saying it is
safe to continue, because a checkpoint is a record of what was true, not a licence to carry on
as if it still is.

## Receipts

```sh
sdlc status                                          # what holds, what is stale
sdlc receipt write readiness --verdict ready --detail "4 reviewers, 0 blocking"
sdlc receipt check readiness --verdict ready         # exit 0 only if it holds
sdlc receipt show spec
```

Stored in `.sdlc/receipts/`. They describe *this working copy*, so add `.sdlc/` to
`.gitignore` — a receipt that travels in a commit is a receipt that lies.

## Worked example — a Go service

```jsonc
{
  "trunk": "main",
  "stack": "go", "pm": "go",
  "test": { "unit": "go test" },
  "spec": { "engine": "prd-frd", "docsRoot": "docs/specs" },
  "verifyCmd": "gofmt -l . && go vet ./... && go test -race ./...",
  "secretScan": "gitleaks git --no-banner --redact -n 50",
  "profile": "service",
  "concerns": ["concurrency", "data"],
  "reviewers": ["sdlc-code-reviewer", "sdlc-security-reviewer"],
  "protected": ["main", "release/*"]
}
```
