---
name: sdlc-init
description: >
  Bootstrap the agent-based SDLC pipeline into the current repository. Detects the
  project's stack, writes sdlc.config.json (the adapter every SDLC agent reads),
  scaffolds the docs directory (MODULES_MAP.md, SDLC.md, BRANCH_LEDGER.md), and prints
  the first command. Run this once per new project. Use when asked to "set up the SDLC
  pipeline", "init sdlc", or "bootstrap the pipeline".
---

# /sdlc-init — bootstrap the pipeline into this repo

Goal: make this repo pipeline-ready without assuming any stack. The kit (agents +
skills) is constant; this command produces the per-project **adapter** so the same
pipeline runs anywhere.

## Step 1 — Detect the stack (infer, don't ask, where possible)

Probe the repo and record findings. Ask the user ONLY for what you genuinely cannot
infer.

- **Package manager:** lockfile — `pnpm-lock.yaml`→pnpm, `package-lock.json`→npm,
  `yarn.lock`→yarn, `bun.lockb`→bun; else `Cargo.toml`→cargo, `go.mod`→go, etc.
- **Monorepo tool:** `turbo.json`→turbo, `nx.json`→nx, `lerna.json`→lerna,
  `pnpm-workspace.yaml`/workspaces field → workspaces; else `none`.
- **Trunk branch:** `git symbolic-ref refs/remotes/origin/HEAD`, or current branch;
  detect `main` / `master` / `Development`. Confirm with the user if ambiguous.
- **Commits:** `commitlint.config.*` or husky hooks present → `conventional`; else `free`.
- **Tests:** dependency scan — `vitest`/`jest`/`mocha`/`pytest`/`go test`;
  `playwright`/`cypress` for e2e.
- **DB / ORM:** `drizzle`, `prisma`, `typeorm`, `sequelize`, alembic, etc.; detect
  migrate-only vs push flow and the seeds directory.
- **Reviewers:** list any project-specific reviewer agents in `.claude/agents/`.
- **Verify command:** assemble from the package manager + scripts
  (type-check + lint + test, plus a migration check if a DB is present).

## Step 2 — Write `sdlc.config.json` at the repo root

```jsonc
{
  "trunk": "main",
  "pm": "pnpm",
  "monorepo": "turbo",
  "commits": "conventional",
  "test": { "unit": "vitest", "e2e": "playwright" },
  "db": { "orm": "drizzle", "flow": "migrate-only", "seedsDir": "packages/db/seeds" },
  "docsRoot": "prd-frd-dev-instructions",
  "branchScheme": "phase-{phase}/{module}/{feature}",
  "reviewers": [],
  "verifyCmd": "pnpm type-check && pnpm lint && pnpm test"
}
```

Fill every field from Step 1. Leave `db` null if there is no database. Leave
`reviewers` as the detected list (may be empty — the readiness gate degrades gracefully).
Show the user the file and confirm before writing.

## Step 3 — Scaffold the docs root

Create `<docsRoot>/` with:

- `MODULES_MAP.md` — canonical feature grid. Header row:
  `| Phase | Module | Feature | Status | Branch | Docs |`. Statuses:
  `planned | in-progress | in-cvr | shipped`. This is the machine-editable source of
  truth the agents read and update; any human dashboard (e.g. a /modules-map page) is
  synced from it.
- `SDLC.md` — the pipeline doc (stages, owners, artifact paths). Generate it from the
  `reference/pipeline.md` content below, substituting the detected `docsRoot`.
- `BRANCH_LEDGER.md` — append-only header: `branch, phase, module, feature, created_at, pr_url, status`.

## Step 4 — Print the first command

Tell the user the pipeline is ready and show the entry point:

```
/agentic-sdlc:start-feature phase=1 module=<module-slug> feature=<feature-slug>
```

## Pipeline reference (write into SDLC.md)

| Stage | Artifact | Owner | Location |
|------|----------|-------|----------|
| 1 PRD | Product Requirements | `sdlc-spec-writer` | `<docsRoot>/<phase>/<module>/<feature>/PRD_v1.0.md` |
| 2 FRD | Functional Requirements | `sdlc-spec-writer` | `.../FRD_v1.0.md` |
| 2b Review | Spec gate | `sdlc-spec-reviewer` | verdict (no file) |
| 3 Branch | Branch + draft PR | `sdlc-branch-opener` | git + `BRANCH_LEDGER.md` |
| 4 DI | Developer Instructions | `/new-di` | `.../DI_v1.0.md` |
| 5 Code | Implementation | project scaffolding skills | source tree |
| 6 CVR | Cross-Verification Report | `/new-cvr` | `.../CVR_of-DI-v1.0_r1.md` |
| 7 Gate | Pre-merge review | `sdlc-readiness-gate` | verdict (no file) |
| 8 IR | Implementation Report | `/new-ir` | `.../IR_of-DI-v1.0_r1.md` |
| 9 Merge | Merge + status update | branch owner | `MODULES_MAP.md` status |

Hard rule to record in SDLC.md: **no code merges without a DI → CVR → IR trail, and no
configurable value ships hardcoded** — it must live in a config/reference table with
admin CRUD.
