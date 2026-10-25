# A worked example — rate limiting on a login endpoint

A real unit of work from request to merged, in a Node service with OpenSpec installed. Nothing
here is hypothetical about the mechanics: every command is one you can run, and every refusal is
one the hook actually produces.

## 0 · Adapt, once

```console
$ /agentic-sdlc:init --write
wrote sdlc.config.json
$ /agentic-sdlc:doctor
note     gitleaks not found (secret scanning)
doctor: ok
```

`brew install gitleaks`, re-run `:init --write`, and `secretScan` fills itself in. The gate will
otherwise record that stage as `skipped` — honestly, but you will not want that in a service
that handles credentials.

Set the profile, since this is a service:

```jsonc
{ "profile": "service", "reviewers": ["sdlc-code-reviewer", "sdlc-security-reviewer"] }
```

## 1–3 · Specify, review, branch

```text
/agentic-sdlc:feature "rate limit POST /login: 5 attempts per 15 minutes per account+IP"
```

The spec writer produces `openspec/changes/login-rate-limit/` and validates it. The reviewer
comes back:

```
SPEC: changes-requested — AC-3 is not falsifiable; the lockout response is unspecified
  1. tasks.md item 3 "handle abuse gracefully" — name the observable behaviour
  2. proposal.md — what status and body does a locked-out request get? 429 with what headers?
  3. design.md — what happens to the counter when the password is corrected on attempt 4?
```

That is the stage doing its job. The writer fixes the three, the reviewer approves, and the
receipt is written:

```console
$ sdlc receipt show spec
{ "kind": "spec", "verdict": "approved",
  "subject": "openspec/changes/login-rate-limit",
  "subjectDigest": "sha256:4f2a9c1e8b3d7a05", ... }
```

Only then does the branch exist. Try it the other way round and:

```console
$ git switch -c feat/login-rate-limit
BLOCKED by agentic-sdlc: ... needs an approved spec
```

## 4 · Implement

```text
/agentic-sdlc:implement
```

Item by item, test first. The implementer hits a gap the spec did not settle — does the limit
count failed attempts only, or all? — and stops rather than choosing:

> tasks.md item 2 does not say whether a successful login resets the counter. Two defensible
> readings with different security properties. Handing back for a one-item spec revision.

Good. A guess here is a security decision made by accident.

## 5–6 · Verify and review

```console
$ /agentic-sdlc:verify
| AC-1 | passed     | src/limiter.ts:31 | limiter.test.ts:12 `blocks the 6th attempt` | 1 passed |
| AC-2 | passed     | src/limiter.ts:48 | limiter.test.ts:40 `resets after 15 minutes`| 1 passed |
| AC-4 | unexecuted | src/login.ts:77   | —                                            | no test  |

$ /agentic-sdlc:review
SECURITY: fail — the counter keys on IP alone behind the proxy; X-Forwarded-For is attacker-controlled
  1. src/limiter.ts:22 — trust only the proxy's rightmost hop, or key on account+IP as specified
```

Two findings a summary would have hidden: one untested criterion, one real vulnerability that
the specification had actually ruled out and the implementation reintroduced.

## 7 · The gate

```console
$ /agentic-sdlc:readiness
Verdict: NOT-READY
| Clean tree | passed |
| Mechanical (pnpm run lint && pnpm test) | passed |
| Secret scan | passed |
| Reviewers | code: pass; security: fail |
| Criteria with evidence | 3 of 4 — AC-4 unexecuted |
```

`pnpm test` is green and the change is still not ready. That gap is the entire point.

Fix the proxy handling, `sdlc-test-author` writes the missing AC-4 test and proves it fails
against the old code, re-run `:readiness` → READY.

## 8–9 · Land and report

```text
/agentic-sdlc:land --merge
```

The pull request body carries the four criteria with evidence and the gate table. If you had
made one more commit after the gate:

```console
BLOCKED by agentic-sdlc: merging needs a READY readiness receipt, and the readiness receipt is
for 9a1c4f21e but HEAD is 3b77de004 — the work changed after it was granted.
```

Re-run the gate on the real commit. Then `:report` writes the implementation report — including
the counter-reset decision and why — and archives the OpenSpec change.

## What the pipeline caught here

A spec with an unfalsifiable criterion. An ambiguity that would have become a silent security
decision. An untested criterion behind a green test run. A vulnerability the spec had excluded.
A merge of a commit nobody reviewed.

None of those is exotic. They are the ordinary failures of shipping under time pressure, and
each was caught by a stage that could not be skipped rather than by somebody remembering.
