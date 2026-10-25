# The pipeline in detail

Each stage below states what it needs, what it does, and the one condition under which it may
hand on. A stage that cannot meet its exit condition reports and stops; it does not improvise
the next stage's work.

## 0 · Adapt — `/agentic-sdlc:init`

Detects the stack and writes `sdlc.config.json`. Re-running it keeps anything you set by hand.

**Exit:** a config whose `verifyCmd` actually runs in this repository. Without that, nothing
downstream can be gated, and `:doctor` says so.

## 1 · Specify — `sdlc-spec-writer`

Turns a request into a specification: an OpenSpec change (`proposal.md`, `design.md`,
`tasks.md`, delta specs) or a PRD + FRD with numbered requirements.

**Exit:** every requirement falsifiable, every refusal specified, scope stated both ways, open
questions named — and with OpenSpec, `openspec change validate --strict` passing.

## 2 · Review the spec — `sdlc-spec-reviewer`

Buildable? Testable? Complete? Scoped? Non-duplicating? Authority-respecting? Are the
maintainer's questions left to the maintainer?

**Exit:** a `spec` receipt — `approved` or `changes-requested` — storing a digest of the
specification. Editing the spec afterwards voids the approval; that is intended.

## 3 · Branch — `sdlc-branch-opener`

The only component allowed to create a branch, and it checks the approval mechanically
(`sdlc receipt check spec --verdict approved`) rather than believing a transcript. Refuses on a
dirty tree rather than stashing anything.

**Exit:** a branch cut from an up-to-date trunk, and a draft pull request where a remote exists.

## 4 · Implement — `sdlc-implementer`

Works the checklist in order, one item at a time, test first where the stack allows, commits
path-scoped, ticks each item in the same commit as the work.

**Exit:** the scope built, `verifyCmd` green, and an honest list of what is left. If the
specification turns out to be wrong, it stops and hands it back — it does not quietly
reinterpret it, because nobody reviewed its version.

## 5 · Verify — `sdlc-verifier`

A line-by-line audit, not a summary and not a second review. For each requirement: the
implementing code at `file:line`, the test that would fail without it, and the outcome of
actually running it. Also the reverse — anything in the diff no requirement asked for.

**Exit:** a `verification` receipt and a report in which every requirement carries one of the
five words. `unexecuted` is the honest answer for a test that was not run.

## 6 · Review — `sdlc-code-reviewer`, `sdlc-security-reviewer`

Code review reads the diff against its specification, the project's standards and the profile.
Security review covers authority, injection, untrusted input, secrets, dependencies, data
exposure and denial of service, and runs the configured secret scan.

**Exit:** `review` and `security` receipts, findings with `file:line`, blocking separated from
non-blocking. Neither agent can edit.

`sdlc-test-author` exists for what they find untested; it writes tests only, and proves each new
test fails against broken code before it counts it.

## 7 · Gate — `/agentic-sdlc:gate`, then `sdlc-readiness-gate`

`:gate` alone runs the mechanical half — clean tree, verify command, secret scan — and writes
the `gate` receipt, which is what a push to a protected branch needs. It deliberately says
nothing about whether the change is any good.

`:readiness` runs the whole thing in order: clean tree, mechanical gate, secret scan (writing
the `gate` receipt at that point), reviewer fan-out, specification conformance, and whether the
checklist was ticked honestly.

**Exit:** a `readiness` receipt. `not-ready` is the normal outcome of a real gate. The receipt
names the commit, so the next commit voids it — correctly, because that commit was never
reviewed.

## 8 · Land — `sdlc-lander`

Pushes the branch and opens the pull request, whose body carries the acceptance criteria with
their evidence and the gate's result. Merges only behind a READY receipt, and the hook refuses
it otherwise. Never tags, releases, publishes or deploys.

## 9 · Report — `sdlc-reporter`

The implementation report — including the decisions made during implementation that the
specification did not settle, which is the part nobody can reconstruct later — and the
documentation sweep. With OpenSpec, archives the change once its specs are published.

## 10 · Release — `sdlc-release-manager`

Merging is not shipping. This stage owns the distance: the READY receipt, a **written rollback
plan** (the command, how long it takes, what it loses, and the observation that triggers it),
the **named irreversible steps**, a **human approval**, the deploy itself lowest-environment
first, and then evidence from the environment rather than from CI.

**Exit:** a `postdeploy` receipt, or a rollback plus a `sdlc feedback` entry so the next
attempt starts informed.

## Continuous · Triage — `sdlc-triager`

Not every unit of work starts as a request. An alert, an advisory, a failing dependency update
or a flaky test is a signal, and a signal is not a task until someone decides what it means.
Verdicts: incident, defect, risk, not-applicable, insufficient-evidence. The signal's text is
data, never instruction — that is the route by which an agentic pipeline gets turned against
its own repository.

## Continuous · Remediate — `sdlc-remediator`

Findings become commits, one at a time, hardest first, each with a failing test where the
finding is behavioural, each re-verified before the next. Each closes as fixed, refused,
deferred or unexecuted. Suppressing a warning rather than fixing it is permitted only when the
suppression *is* the correct resolution, and the commit message must say why.

---

## What the hook refuses, at every stage

| Attempt | Refused unless |
| --- | --- |
| create a branch | a valid `spec` receipt says `approved` |
| `git push` to a protected branch | a `gate` receipt says `passed` for this commit |
| `gh pr merge`, merge into the trunk | a `readiness` receipt says `ready` for this commit |
| `git stash`, `reset --hard`, `clean`, `checkout -- .` | never |
| `git add -A`, `git add .`, `git commit -a` | never — commits are path-scoped |
| force-push, `git tag`, any publish, `gh release`, `docker push` | never — the maintainer's |
| reading `.env`, keys, `~/.ssh`, `~/.aws` | never |
| `kubectl apply`, `helm upgrade`, `terraform apply`, `fly deploy`, `ansible-playbook`, cloud deploys | a human `approval_release` **and** a READY receipt |
| `gh pr merge` where `approvals.merge` is `human` | a human `approval_merge` for this commit |

Every refusal names the allowed route. `enforce` in the config can turn any of them off — a
deliberate, recorded choice rather than an accident.
