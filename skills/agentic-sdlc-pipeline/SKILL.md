---
name: agentic-sdlc-pipeline
description: >
  The agent-based SDLC pipeline: how to take a unit of work from request to merged, which agent
  owns each stage, and which receipt each stage leaves. Use when asked to set up, explain, run
  or debug the SDLC pipeline, when a user says "use the pipeline / follow SDLC", or when
  deciding which /agentic-sdlc command comes next.
---

# The pipeline

Read `${CLAUDE_PLUGIN_ROOT}/docs/rules.md` before running any stage. Read the project's
`sdlc.config.json` to learn its stack — never assume one.

| # | Stage | Command | Owner | Leaves |
| --- | --- | --- | --- | --- |
| 0 | Adapt | `/agentic-sdlc:init` | — | `sdlc.config.json` |
| 1 | Specify | `/agentic-sdlc:feature` | `sdlc-spec-writer` | a specification |
| 2 | Review the spec | ↑ same command | `sdlc-spec-reviewer` | `spec` receipt |
| 3 | Branch | ↑ same command | `sdlc-branch-opener` | a branch |
| 4 | Implement | `/agentic-sdlc:implement` | `sdlc-implementer` | code and tests |
| 5 | Verify | `/agentic-sdlc:verify` | `sdlc-verifier` | `verification` receipt |
| 6 | Review | `/agentic-sdlc:review` | `sdlc-code-reviewer`, `sdlc-security-reviewer` | `review`, `security` receipts |
| 7a | Mechanical gate | `/agentic-sdlc:gate` | — | `gate` receipt |
| 7b | Readiness | `/agentic-sdlc:readiness` | `sdlc-readiness-gate` | `readiness` receipt |
| 8 | Land | `/agentic-sdlc:land` | `sdlc-lander` | branch pushed, pull request |
| 9 | Report | `/agentic-sdlc:report` | `sdlc-reporter` | implementation report, docs |
| 10 | Release | `/agentic-sdlc:release` | `sdlc-release-manager` | `postdeploy` receipt, or a rollback |
| — | Triage | `/agentic-sdlc:triage` | `sdlc-triager` | a scoped unit of work, or a reasoned dismissal |
| — | Remediate | `/agentic-sdlc:remediate` | `sdlc-remediator` | one commit per finding, re-verified |

`/agentic-sdlc:status` says which receipts hold right now; `/agentic-sdlc:doctor` checks the
install and the configuration.

## What makes it different from a checklist

Three stages are enforced by a `PreToolUse` hook, not by instruction:

- a branch needs an **approved spec** receipt whose digest still matches the specification;
- a push to a protected branch needs a **passed gate** receipt for that exact commit;
- a merge needs a **READY readiness** receipt for that exact commit, plus a human
  `approval_merge` where the project asks for one;
- a deployment needs a human `approval_release` **and** a READY receipt — an agent cannot
  approve its own release.

A new commit voids a receipt. Editing an approved specification voids its approval. The hook
also refuses destructive git, publishing and credential reads. None of this makes a dishonest
verdict honest; it makes a skipped stage impossible.

## Starting in an existing repository

1. `/agentic-sdlc:init --write`, then read the config and correct it. `verifyCmd` must be real.
2. Choose a profile if one fits (`${CLAUDE_PLUGIN_ROOT}/profiles/`); "none" is fine.
3. `/agentic-sdlc:doctor` until it is clean.
4. `/agentic-sdlc:feature "<what you want>"`.

## When a stage says no

That is the pipeline working. Fix the cause, re-run the stage, and let it write a new receipt.
Never edit a receipt, and never route around the hook — if the route is blocked, the route is
wrong.
