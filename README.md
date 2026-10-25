# agentic-sdlc

An agent-based SDLC pipeline that is **enforced, not suggested**.

Most agent workflows are a prompt that asks a model to be careful. This one asks too — and then
refuses, at the tool call, to let a stage be skipped. A branch cannot be created without an
approved specification. A push to the trunk cannot happen without a passed gate. A merge cannot
happen without a READY verdict for *that exact commit*. Those are not sentences in a system
prompt; they are a `PreToolUse` hook that exits non-zero.

It is stack-agnostic through a single detected adapter file, and it speaks
[OpenSpec](https://github.com/Fission-AI/OpenSpec) or plain PRD/FRD.

**Claude Code**

```sh
/plugin marketplace add mdferdousalam/agentic-sdlc
/plugin install agentic-sdlc
/agentic-sdlc:init --write          # detect the stack, write sdlc.config.json
/agentic-sdlc:feature "2FA for the admin login"
```

**Any other agent** — Cursor, Codex, Copilot, Gemini, Cline, Windsurf, Zed, Aider:

```sh
curl -fsSL https://raw.githubusercontent.com/mdferdousalam/agentic-sdlc/main/install.sh | sh
sdlc install     # detects your agents, sets each one up, adds the git hooks
sdlc doctor      # what is configured and what is missing
```

Or via whichever package manager you already use:

```sh
npx @mdferdousalam/agentic-sdlc install        # npm
uvx --from agentic-sdlc-cli sdlc install       # PyPI (or: pipx install agentic-sdlc-cli)
brew install mdferdousalam/tap/agentic-sdlc    # Homebrew
codex plugin marketplace add mdferdousalam/agentic-sdlc   # Codex, as a plugin
gemini extensions install https://github.com/mdferdousalam/agentic-sdlc
```

Needs `git` and Python 3.8+. No Python dependencies, no account, no sudo.
**[All routes, and how to uninstall](docs/install.md)** — including why the Codex plugin asks
you to trust its hook once, and what `install.sh` actually does before you pipe it anywhere.

## The pipeline

| # | Stage | Command | Owner | Leaves behind |
| --- | --- | --- | --- | --- |
| 0 | Adapt | `:init` | — | `sdlc.config.json` |
| 1 | Specify | `:feature` | `sdlc-spec-writer` | an OpenSpec change, or a PRD + FRD |
| 2 | Review the spec | ↑ | `sdlc-spec-reviewer` | `spec` receipt — approved or changes-requested |
| 3 | Branch | ↑ | `sdlc-branch-opener` | a branch, only on an approved spec |
| 4 | Implement | `:implement` | `sdlc-implementer` | code, tests, ticked checklist |
| 5 | Verify | `:verify` | `sdlc-verifier` | requirement-by-requirement evidence |
| 6 | Review | `:review` | `sdlc-code-reviewer`, `sdlc-security-reviewer` | findings with `file:line` |
| 7a | Mechanical gate | `:gate` | — | `gate` receipt — what a push to the trunk needs |
| 7b | Readiness | `:readiness` | `sdlc-readiness-gate` | `readiness` receipt — READY or NOT-READY |
| 8 | Land | `:land` | `sdlc-lander` | branch pushed, pull request with its evidence |
| 9 | Report | `:report` | `sdlc-reporter` | implementation report, documentation brought up to date |

Also `:gate` (the mechanical half on its own), `:status` (which receipts hold right now), `:doctor` (is the install sane), and
`sdlc-test-author` for the tests a review finds missing.

Eleven agents, each with one job and no permission to do another's. The reviewers cannot edit.
The gate cannot push. Only the lander touches the remote, and it cannot tag, release or publish
at all.

## What "enforced" means

Three receipts, each bound to a commit, a clock, and — for a specification — the content that
was approved:

```sh
sdlc status
#   spec        approved   9a1c4f21e  2026-10-25T09:04:11Z  current
#   readiness   ready      9a1c4f21e  2026-10-25T09:41:02Z  current
```

- Make another commit → the readiness receipt is for the old one, and the merge is refused.
- Edit the specification after approval → the digest no longer matches, and the branch stage
  refuses.
- Let three hours pass → the receipt is stale.

**Humans where humans matter.** `approvals` says which actions need a named person. Deployment
defaults to `human`, and an agent cannot satisfy it — the approval records who is accountable,
and an agent approving its own work records nothing. Approvals are scoped (a release approval
does not authorise a merge) and die with the next commit.

**Failure is routed, not dropped.** A gate failure is written back as enriched context with
`sdlc feedback`, so the retry starts informed instead of repeating itself. After three attempts
at one stage the tool says to stop: at that point the specification is usually the problem.

The same hook also refuses `git stash`, `reset --hard`, `clean`, `checkout -- .`, `add -A`,
`commit -a`, force-push, `tag`, every `publish`, `gh release`, `docker push`, and reading a
credential file. Each refusal explains itself and names the route that is allowed.

This cannot make a dishonest verdict honest — nothing can. It makes a **skipped** stage
impossible, which is the failure that actually happens.

## One adapter, any stack

`sdlc.config.json` is the only file that knows your project. Agents read it; none of them
hardcodes `pnpm`, `main` or `pytest`.

```jsonc
{
  "trunk": "main",
  "stack": "node",
  "pm": "pnpm",
  "test": { "unit": "vitest", "e2e": "playwright" },
  "spec": { "engine": "openspec", "docsRoot": "openspec/changes", "strict": true },
  "verifyCmd": "pnpm run lint && pnpm run typecheck && pnpm test",
  "secretScan": "gitleaks git --no-banner --redact -n 50",
  "profile": "webapp",
  "reviewers": ["sdlc-code-reviewer", "sdlc-security-reviewer"],
  "enforce": { "mergeNeedsReadiness": true, "pushToTrunkNeedsGate": true }
}
```

`:init` detects all of it — package manager from the lockfile, test runners from the
dependencies, trunk from git, spec engine from whether OpenSpec is present, verify command from
your own scripts. Re-running it never overwrites something you set by hand.
[Full reference](docs/configuration.md).

## Profiles: opinions you opt into

A rule like *"no hardcoded value that the spec marked configurable"* is right for an
admin-driven web app and meaningless for a compiler. So the core carries no such rule, and
profiles carry them instead — `"profile": "webapp"` and the reviewers hold you to it.

| Profile | Adds |
| --- | --- |
| [`webapp`](profiles/webapp.md) | configurability, data model and migrations, accessibility, tenant isolation |
| [`library`](profiles/library.md) | public API as a promise, semver from the diff, documented exports |
| [`service`](profiles/service.md) | timeouts and retries, idempotency, observability, limits, rollback |
| [`compiler`](profiles/compiler.md) | specification first, diagnostic codes, evidence vocabulary, bounded workloads |

Those are project *kinds*, and you pick one. **Concerns** cut across them, so you pick any
number — a Go service wants `service` and `concurrency` both:

```jsonc
{ "profile": "service", "concerns": ["concurrency", "data", "performance"] }
```

`architecture` (dependency direction, cycles, boundaries) · `performance` (N+1, pagination,
scale limits) · `memory` (lifetimes, cleanup, unbounded growth) · `concurrency` (races, lock
order, TOCTOU, cancellation) · `data` (constraints, transaction boundaries, reversible
migrations, idempotency) · `platform` (host assumptions, numerics, locale, shutdown).

`:init` proposes them from what your repository actually does and never imposes one. Each names
the deterministic tool for your stack and says it belongs in `quality.cmd` — until it is there,
those findings are a reading, not a measurement, and they are recorded as such.

Writing your own is one markdown file. Keep it to what a reviewer can check.

## OpenSpec, properly

When OpenSpec is present the specification *is* an OpenSpec change, and the pipeline uses the
parts of it that are machine-checkable:

- `openspec validate <id> --strict` — a malformed spec is an automatic
  changes-requested, quoted rather than paraphrased;
- `tasks.md` is the acceptance criteria: the implementer ticks each item in the commit that did
  it, the verifier maps each to `file:line` plus a test outcome, the gate treats a ticked
  unfinished item as a blocker;
- `openspec archive <id>` after landing, so `openspec list` keeps telling the truth.

Without OpenSpec you get PRD + FRD with numbered requirements and the identical downstream
behaviour. [How it fits](docs/openspec.md).

## Governance you can show someone

```sh
sdlc metrics      # stage outcomes, first-pass rates, which refusals fire, who acted
sdlc trace        # requirement → commit → test → receipts, as markdown or JSON
sdlc status       # which receipts hold right now, which are stale
```

Everything lands in an append-only `.sdlc/audit.log`. A first-pass gate rate of 100% is
reported as a finding, not a success — it usually means the gate is not checking anything.
[Standards mapping](docs/compliance.md) for NIST AI RMF, OWASP Agentic AI and OWASP NHI,
including what this does **not** give you.

## Four levels, each a configuration

Adoption is not a switch. [docs/maturity.md](docs/maturity.md) gives the config for each level:
human executes → human validates → human orchestrates → human sets constraints. Start where
your trust actually is, and let `sdlc metrics` tell you when to move.

## Five words

**passed · failed · skipped · refused · unexecuted.** Every report in the pipeline uses them and
only them. A test that did not run is `unexecuted` — not `passed`, and not `failed`. That one
distinction is what stops a green summary hiding an unrun check, and it is why the gate asks for
`file:line` and a command output behind every claim.

## Runs on whatever agent you use

```sh
sdlc install            # detect your agents, install for all of them, plus git hooks
sdlc install --list     # what is supported and what is detected here
```

| Host | Can it refuse a skipped stage? |
| --- | --- |
| Claude Code, opencode, Codex CLI, Cline | **Yes** — at the tool call, with a reason |
| Gemini CLI | Static patterns only, via its policy engine |
| Cursor, Copilot, Windsurf, Roo, Kilo, Continue, Aider | No tool hook — instructions, plus the layers below |
| Zed, Amp, Warp, Junie, Factory, Devin, Jules | `AGENTS.md` |

Two layers cover the hosts that cannot refuse anything:

- **git hooks**, installed by default — every agent shells out to `git`, so a push to a
  protected branch without a gate receipt is refused even from Cursor or a bare terminal.
  Bypassable with `--no-verify`, which is why the next one exists.
- **CI** — `sdlc install ci` writes a workflow that re-runs the gate where no agent can reach
  it. On a host without a native hook, this is your real enforcement.

The rules live in one Python CLI with no dependencies, so every host refuses exactly the same
things. **[The full capability matrix, with what is verified and what is not](docs/platforms.md).**

## Requirements

`git` and `python3` (standard library only — no dependencies, no network). Optional but
recommended: `gh` for pull requests, `gitleaks` for the secret scan, `openspec` for the spec
engine. `/agentic-sdlc:doctor` tells you what is missing and what it costs you.

## Documentation

- **[Getting started](GETTING-STARTED.md) — start here if this is new to you**
- [Installing](docs/install.md) — every route, and uninstalling
- [The pipeline in detail](docs/pipeline.md) — every stage, its inputs, its exit condition
- [Maturity levels](docs/maturity.md) — what to configure at each stage of adoption
- [Standards mapping](docs/compliance.md) — NIST AI RMF, OWASP, and the honest limits
- [Configuration reference](docs/configuration.md)
- [OpenSpec integration](docs/openspec.md)
- [Platforms — what each host can enforce](docs/platforms.md)
- [Using it with opencode](docs/opencode.md)
- [The rules every agent obeys](docs/rules.md)
- [Contributing](CONTRIBUTING.md) · [Changelog](CHANGELOG.md) · [Security](SECURITY.md)

## Licence

MIT © Engr Md Ferdous Alam
