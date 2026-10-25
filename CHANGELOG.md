# Changelog

All notable changes to this plugin. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the versioning is [semantic](https://semver.org/).

## [2.3.0] — 2026-10-25

Published through every package manager a developer is likely to already have.

### Added

- **More ways in.** `packaging/build-pypi.sh` builds a PyPI distribution
  (`agentic-sdlc-cli` — the unscoped `agentic-sdlc` is taken on PyPI too), staging the agents,
  commands, docs and profiles into the wheel so the plugin root resolves the same way it does
  from a checkout. `packaging/homebrew/agentic-sdlc.rb` is a tap-ready formula with the real
  release checksum. `.codex-plugin/plugin.json` and `.agents/plugins/marketplace.json` make the
  repository installable as a **Codex plugin**, and `gemini-extension.json` as a **Gemini
  extension** — both straight from the git URL, no registry involved.
- **`docs/install.md`** — all eight routes in one table, what each needs, and how to uninstall.

### Verified

The Codex plugin route was tested both ways, and the result is worth knowing: a plugin's hook
is **not run until Codex has been asked to trust it**. Untrusted, only `Stop` fired and
`git stash` went through; trusted, the same command was refused. `sdlc install codex` avoids
the prompt because a hook in your own `~/.codex/hooks.json` is already your configuration —
that path is verified working, receipt-dependent push gate included.

The PyPI wheel was installed into a clean virtualenv and run. The Homebrew formula carries the
real `v2.2.0` tarball checksum and is syntax-checked.

### Fixed

- The detected `secretScan` default used `gitleaks git … -n 50`, and gitleaks 8.x has no `-n`
  shorthand on that subcommand — the gate's secret stage failed to run at all. It is now
  `--log-opts="-n 50"`, with a regression test. Found by running this repository's own gate
  against itself.

## [2.2.0] — 2026-10-25

A front door for everyone who is not using Claude Code. Until now the only one-command install
was `/plugin install`; everybody else had to clone a repository and run a Python script. That,
rather than any missing adapter, was what would have stopped other developers adopting this.

### Added

- **`install.sh`** — `curl -fsSL .../install.sh | sh`. Downloads a release into
  `~/.agentic-sdlc`, links `sdlc` into a bin directory already on your PATH, and touches
  nothing in your repository. No account, no sudo, no Python dependencies. It refuses to
  proceed on Python older than 3.8 rather than failing later with something cryptic.
- **npm package `@mdferdousalam/agentic-sdlc`** — `npx @mdferdousalam/agentic-sdlc install`.
  Scoped because the unscoped name belongs to an unrelated project. The `bin` is a small Node
  launcher rather than the Python file directly, so Windows gets a real shim instead of
  depending on a shebang npm cannot honour there; it tries `python`, `py`, `python3` on Windows
  and `python3`, `python` elsewhere, and says exactly what is missing if none works.

### Verified

Installing the packed npm
tarball into a clean project and pushing: the generated `pre-push` hook
refused an ungated push to `main`, and allowed it once a gate receipt existed. CI now checks
the installer with `shellcheck`, that `package.json` and `plugin.json` agree on the version,
and that the packed tarball's CLI actually runs.

## [2.1.0] — 2026-10-25

The pipeline stops being a Claude Code feature.

### Added

- **`sdlc install [targets…]`** — one generator, fifteen targets, from the same canonical
  `agents/`, `commands/` and `docs/rules.md`. With no arguments it detects the agents on the
  machine and installs for all of them. `--list` shows what is supported and what each host can
  actually enforce; `--dry-run` writes nothing; `sdlc uninstall` removes only our blocks and the
  files we own.
- **Three more hosts that genuinely refuse a skipped stage**, not just instruct:
  - **Codex CLI** — a `PreToolUse` entry merged into `~/.codex/hooks.json`, preserving every
    other event already configured there. Codex uses the same hook wire contract as Claude Code.
  - **Cline** — an executable `.clinerules/hooks/PreToolUse`, exit 2 blocks.
  - **Gemini CLI** — no pre-tool hook exists, so the static refusals become
    `.gemini/policies/agentic-sdlc.toml` rules (`decision = "deny"`), with the
    receipt-dependent gates left to the git hooks. Commands ship as `.gemini/commands/sdlc/*.toml`.
- **Instruction and command adapters** for Cursor (`.cursor/rules/*.mdc` with `alwaysApply`,
  `.cursor/commands/`), GitHub Copilot (`copilot-instructions.md`, `.github/prompts/*.prompt.md`),
  Windsurf, Roo, Kilo, Continue and Aider — plus `AGENTS.md` everywhere, which the agents.md
  adopter list says is read by 20+ tools.
- **Git hooks, installed by default** (`--no-git-hooks` to opt out). Every agent shells out to
  git, so this is the only local enforcement that reaches Cursor, Copilot and a bare terminal
  alike. An existing hook is appended to inside a marked block, never replaced.
- **`sdlc install ci`** — a GitHub Actions gate that re-runs the verify command, secret scan and
  quality budget where no agent can reach them. It does not read receipts; it re-does the work.
- **`sdlc guard --command "<cmd>"`** — the same rules without a hook payload, which is how the
  git hooks call it. Tested to agree with the stdin path rule for rule.
- **`docs/platforms.md`** — the capability matrix, saying for each host whether it can refuse a
  tool call, how the format was verified, and which three are only conventional and unverified.
- **`sdlc doctor` is platform-aware** — which hosts are present, which are installed here, and
  the exact command for each gap.

### Changed

- Everything written into a file we share with you is a marked block, so re-running updates only
  our section and `uninstall` leaves your content. This applies to `AGENTS.md`, `GEMINI.md`,
  `CONVENTIONS.md`, Copilot instructions, every rules file and both git hooks.
- The hook command resolves `python3` or `python` at install time rather than assuming a
  shebang works, which is a prerequisite for Windows.
- `bin/sdlc-install-opencode` is **deprecated** — it now calls `sdlc install opencode`. Removal
  in 3.0.0.

### Verified

Live, in real sessions:

- **Codex CLI** — `git stash` refused, and `git push origin main` refused for want of a gate
  receipt. The second one matters: it proves the *receipt-dependent* gates work on Codex, not
  only the static pattern rules. The user's pre-existing `Stop` hook fired in the same session,
  so the `hooks.json` merge is safe in practice and not just in the unit test.
- **git hooks** — an ungated push to `main` refused from a plain terminal with no agent
  involved; a feature branch allowed; `--no-verify` bypasses it exactly as documented.

**Not verified:** the live refusal inside a Cline session, and the Cursor, Copilot and Roo
pickup, which need interactive IDE sessions. Gemini could not be tested at all — Google now
returns `UNSUPPORTED_CLIENT` for this client's free tier. Kilo, Windsurf and Continue use
conventional paths that are not confirmed against a real tool; those adapters also write
`AGENTS.md`, so the rules land either way. Windows remains untested.

## [2.0.0] — 2026-10-25

A rewrite. v0.1.0 was a document pipeline that asked a model to be careful; this is a pipeline
whose stages cannot be skipped.

### Added — lifecycle, governance and adoption

Informed by a review of published agentic-SDLC material (Sonar's AC/DC framework, CodeRabbit's
guide, Weave Intelligence's ASDLC, Optiver's engineering account, NHI Management Group's
governance glossary, and the agentic-ai-sdlc/Framework repository). Two further sources the
maintainer supplied — a Medium article and an Infosys page — returned HTTP 403 and were not
read; nothing here is attributed to them.

- **The lifecycle no longer stops at the merge.** `sdlc-release-manager` and
  `/agentic-sdlc:release` own deployment, post-deploy verification against the environment
  itself, and the rollback decision. A written rollback plan and named irreversible steps are
  required *before* deploying, and `release.*` in the config carries the commands.
- **Human approval gates.** `approvals.merge` and `approvals.release` (release defaults to
  `human`). `sdlc approve <what> --as '<name>'` is a person's command; an agent that runs it
  records nothing. Approvals are scoped — a release approval does not authorise a merge — and
  are voided by the next commit. Deployment commands (kubectl, helm, terraform, serverless,
  fly, ansible, cloud CLIs) are refused without both an approval and a READY receipt.
- **The hybrid retry loop.** `sdlc feedback write|read|clear` carries a gate's failure back to
  the next attempt as enriched context rather than dropping it, and says to stop after three
  attempts at the same stage.
- **`sdlc-remediator` and `/agentic-sdlc:remediate`** — work through findings one commit at a
  time, each re-verified, each closed as fixed / refused / deferred / unexecuted. Suppressing a
  warning to close a finding is called out as the failure the pipeline exists to prevent.
- **`sdlc-triager` and `/agentic-sdlc:triage`** — turn an alert, advisory, bug report or flaky
  test into a scoped unit of work or a reasoned dismissal, treating the signal's text as data
  and never as instruction.
- **Governance you can show someone**: `sdlc metrics` (stage outcomes, first-pass rates,
  refusals, actors), `sdlc trace` (requirement → commit → test → receipts, markdown or JSON),
  and an append-only `.sdlc/audit.log`. A 100% first-pass rate is reported as a finding.
- **`docs/maturity.md`** — four adoption levels, each expressed as a configuration rather than
  an aspiration, with the metric that says you are ready to move up.
- **`docs/compliance.md`** — mapping to NIST AI RMF, OWASP Agentic AI, OWASP Non-Human
  Identity and ISO 42001/SOC 2 evidence, with five stated limits including no cryptographic
  identity and no shipped analyser.
- **`GETTING-STARTED.md`** — a guided first hour for someone who has never used this.
- **`quality` config** — a deterministic-analysis budget on *new* code, because the research on
  agent-written code reports rising warnings and complexity rather than falling ones.
- **An eval suite** (`evals/`, four cases) for `claude plugin eval`: does the spec reviewer
  catch unfalsifiable requirements, does the gate refuse an `unexecuted` criterion behind a
  green suite, is a refusal negotiable under social pressure, does the release manager insist
  on a rollback plan and a human approval.

### Added — the enforced pipeline

- **Enforcement.** `hooks/hooks.json` registers a `PreToolUse` hook calling `bin/sdlc guard`,
  which exits 2 to refuse a tool call. A branch needs an approved spec; a push to a protected
  branch needs a passed gate; a merge needs a READY verdict for that exact commit. Destructive
  git, publishing and credential reads are refused outright.
- **Receipts.** `sdlc receipt write|check|show` records each stage's verdict bound to a commit,
  a clock and — for a specification — a digest of the content approved. A new commit voids a
  receipt; editing an approved spec voids its approval.
- **`bin/sdlc`** — stack detection, config, receipts, the guard, `status` and `doctor`. Python
  3.8+, standard library only, no network.
- **Seven new agents**: `sdlc-implementer` (v0.1.0 had no agent that wrote code),
  `sdlc-test-author`, `sdlc-code-reviewer`, `sdlc-security-reviewer`, `sdlc-verifier`,
  `sdlc-lander`, `sdlc-reporter`.
- **Eleven slash commands** — `:init`, `:feature`, `:implement`, `:verify`, `:review`,
  `:gate`, `:readiness`, `:land`, `:report`, `:status`, `:doctor`.
- **OpenSpec as a first-class engine.** `spec.engine` is detected; the spec reviewer runs
  `openspec change validate --strict`, `tasks.md` becomes the acceptance criteria the verifier
  and the gate check against, and the reporter archives the change after landing.
- **Profiles** — `webapp`, `library`, `service`, `compiler`: opt-in standards a reviewer can
  check, selected by `"profile"`.
- **A JSON Schema** for the adapter, and a config that is re-detected without overwriting
  anything set by hand.
- **opencode support** — `bin/sdlc-install-opencode` installs the same agents, commands and
  enforcement, calling the same guard.
- **Tests** — 46 cases over detection, the guard, receipt binding and config overrides, run in
  CI. The validator now checks agent/filename agreement, command→agent references, hook wiring
  and that the CLI is executable.

### Changed

- **The evidence vocabulary is five words** — passed, failed, skipped, refused, unexecuted —
  replacing `met/partial/missing` and `pass/fail`. A test that did not run is `unexecuted`, and
  the gate treats it as such.
- **Specifications are no longer hand-versioned.** `PRD_v1.0.md` and `CVR_of-DI-v1.0_r1.md`
  become `PRD.md` and `verification.md`; git keeps the history.
- `sdlc.config.json` gains `spec`, `secretScan`, `profile`, `receipts`, `enforce`, `heavy`, and
  a `version` field.
- Every agent now reads `docs/rules.md` rather than restating the rules, so they cannot drift
  apart.

### Removed

- **The configurability audit from the core.** "No hardcoded value the spec marked
  configurable", reference tables, admin CRUD surfaces and 3NF were rules from the application
  the kit was extracted from, and they produced noise on every other kind of project. They now
  live in `profiles/webapp.md` and apply when you ask for them.
- **The DI stage.** A third document between the FRD and the code mostly restated the FRD; the
  implementer reads the specification directly. What the DI uniquely carried — the decisions
  taken while building — is now in the implementation report, where it is written after the
  fact and is therefore true.
- The `sdlc-init`, `start-feature`, `dev-instructions`, `verification-report` and
  `implementation-report` skills, replaced by commands and agents. Three reference skills
  remain: `agentic-sdlc-pipeline`, `openspec-with-sdlc`, `writing-specifications`.

### Migration from 0.1.x

1. `/agentic-sdlc:init --write` — rewrites `sdlc.config.json` in the v2 shape, keeping your
   `trunk`, `verifyCmd` and anything else you had set.
2. Add `.sdlc/` to `.gitignore`.
3. Set `"profile": "webapp"` if you relied on the configurability and data-model rules.
4. Existing `PRD_v1.0.md` / `FRD_v1.0.md` still read fine; new specs drop the version suffix.
5. `/agentic-sdlc:doctor`.

## [0.1.0] — 2026-10

First release: PRD → FRD → branch → DI → code → CVR → readiness gate → IR, four agents, five
skills, and a detected `sdlc.config.json`.
