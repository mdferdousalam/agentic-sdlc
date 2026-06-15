# agentic-sdlc

A **stack-agnostic, agent-based SDLC pipeline** packaged as a Claude Code plugin. The
same pipeline — PRD → FRD → branch → DI → code → CVR → readiness gate → IR — runs on any
project. What varies per project is a single detected adapter file, `sdlc.config.json`;
the agents and skills are constant.

## Core idea

| Layer | Reusable? | Where it lives |
|------|-----------|----------------|
| Pipeline shape (stages + owners) | yes — shipped by this plugin | `agents/`, `skills/` |
| Stack bindings (pm, trunk, ORM, test runner, reviewers) | no — detected per project | `sdlc.config.json` |

Every agent reads `sdlc.config.json` instead of hardcoding `pnpm`, `main`, `drizzle`,
etc. Swap that file and the identical pipeline runs on a Go monorepo or a single-package
Next.js app.

## Install

```bash
# add this repo as a marketplace, then install the plugin
/plugin marketplace add mdferdousalam/agentic-sdlc
/plugin install agentic-sdlc

# or load locally for development
claude --plugin-dir ./agentic-sdlc
```

## Use

```bash
# 1. once per repo: detect stack, write sdlc.config.json, scaffold docs
/agentic-sdlc:sdlc-init

# 2. per feature: drives spec -> review -> branch -> DI in one shot
/agentic-sdlc:start-feature phase=1 module=auth feature=2fa

# 3. implement against the DI, then:
/agentic-sdlc:verification-report     # cross-verify build vs spec (CVR)
# run the readiness gate (sdlc-readiness-gate agent) -> READY
/agentic-sdlc:implementation-report   # close the feature (IR)
```

## Components

**Agents** (`agents/`)

- `sdlc-spec-writer` — writes PRD + FRD for a `{phase, module, feature}`.
- `sdlc-spec-reviewer` — gates the spec (APPROVED / CHANGES-REQUESTED) before branching.
- `sdlc-branch-opener` — the single owner of branch creation; validates the name,
  enforces doc-first, creates + pushes the branch, drafts the PR, updates the ledgers.
- `sdlc-readiness-gate` — the single pre-merge gate; runs the verify command and fans
  out to the project's configured reviewers.

**Skills** (`skills/`)

- `sdlc-init` — bootstrap: detect stack, write config, scaffold docs.
- `start-feature` — chain spec → review → branch → DI.
- `dev-instructions` (DI), `verification-report` (CVR), `implementation-report` (IR) —
  artifact generators, parameterized by config paths.

## Conventions written into each project

- `prd-frd-dev-instructions/MODULES_MAP.md` — canonical Phase → Module → Feature grid
  (status: `planned | in-progress | in-cvr | shipped`).
- `prd-frd-dev-instructions/SDLC.md` — the pipeline doc.
- `prd-frd-dev-instructions/BRANCH_LEDGER.md` — append-only branch history.
- Branch scheme: `phase-{N}/{module}/{feature}` (configurable).

## Non-negotiable standards the pipeline enforces

1. **No code merges without a DI → CVR → IR trail.**
2. **No configurable value ships hardcoded** — it must live in a normalized
   config/reference table (3NF, separation of concerns) with admin/moderator CRUD.
3. **DRY** — reuse shared packages before writing new code.
4. **Tests + intent comments** on all new code.

## Adapting to a new stack

`sdlc-init` infers everything it can from lockfiles, `turbo.json`/`nx.json`, commitlint,
test deps, and the ORM. It only asks you for what it cannot detect. Edit
`sdlc.config.json` afterward to override any field (trunk name, reviewer set, verify
command, branch scheme).
