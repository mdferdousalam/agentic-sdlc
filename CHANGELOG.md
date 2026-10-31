# Changelog

All notable changes to this plugin. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the versioning is [semantic](https://semver.org/).

## [3.0.1] — 2026-10-31

A security release. Every finding below was found by this pipeline's own readiness gate run
against 3.0.0, which returned NOT-READY. Five were critical. 3.0.0 is published and
bypassable; upgrade.

The test suite goes from 248 assertions to 341. Each fix carries the reproduction that
produced it, as a test.

### Fixed — the refusal path

- **The guard reads commands, not command lines.** Rules were matched as regular expressions
  against the raw text of a command line, which failed in both directions at once.
  `git -c core.pager=cat stash` was *allowed*, because a global option between `git` and the
  subcommand defeated every `\bgit\s+stash\b` pattern — 18 of 18 refusals could be bypassed
  this way, and the same hole let an ungated `git -c … push` past the protected-branch gate.
  Meanwhile `sdlc finding write --detail "git stash is refused"` was *refused*, because prose
  quoting a forbidden command read as the command itself; this blocked the readiness gate
  from writing its own NOT-READY receipt, which is to say the control could not record its
  own verdict.

  The line is now tokenised, split at the shell operators, stripped of heredoc bodies and of
  git's global options, and each rule is matched from the start of a command rather than
  anywhere in the text. `sh -c "<code>"` is parsed in turn rather than scanned as a string.
  Anything that cannot be parsed — an unbalanced quote, say — falls back to matching the raw
  line exactly as before, so a parse failure fails closed. Secret-shaped strings
  (`sk-…`, `ghp_…`, `AKIA…`) are still matched anywhere on the line: a secret is a secret
  wherever it sits.

  Closes the critical `F-d0c13a07` and the `F-67811454` false positives.

  **The first attempt at this made things worse, and the history is worth keeping.** It
  anchored each rule at position 0 of a simple command, which closed the false positive and
  reopened the bypass class it was written for: an independent code review and security
  review, run against the branch, each found it separately and measured 24 refusals that
  held before the change and were allowed after. `echo hello` followed by a newline and
  `git stash` was enough, with no intent to evade, because `shlex` reads an unquoted newline
  as whitespace and the two commands collapsed into one unit anchored on `echo`. So did
  `sudo -u ci git clean -fd`, `for f in a b; do git clean -fd; done`, `find . -exec`,
  `git submodule foreach`, and a quoted `<<` that read as a heredoc and discarded every
  following line unscanned.

  The anchoring was never needed. Collapsing an argument's own whitespace already stops a
  quoted sentence reading as the command it describes, so the rules are matched across the
  whole of a simple command. Unquoted newlines end commands; heredoc markers are found with
  the same quote-aware scan, and an unterminated one is a parse failure rather than licence
  to swallow the rest; wrapper options that take a separate value are stepped over; shell
  keywords are stripped; `--exec` values are parsed as the code they are; and an unperformed
  expansion is widened to the word separator the shell will make of it, so `git${IFS}stash`
  and `{git,stash}` are refused — both of which 3.0.0 allowed.

  Net of all that, the branch refuses three things 3.0.0 did not: `git push --all` and
  `git push --mirror`, which push the trunk without naming it, and `git branch -f`.

- **A publish route the maintainer did not authorise.** `.github/workflows/publish.yml`
  carried `workflow_dispatch` as a convenience, and a dispatch has no release tag, so the
  tag-versus-manifest check sat behind `if: github.event_name == 'release'` and was skipped
  on that path. `gh workflow run publish.yml --ref <anything>` would publish whatever version
  that ref held, under the trusted-publisher identity. The trigger is gone; the version check
  is unconditional; the mechanical gate moved to its own job, because a job that downloads
  `markdownlint-cli2` from the network should not also hold a credential that can publish.
  The guard now refuses `gh workflow run` by name, and `gh api` to a releases or dispatches
  path when a method or field flag makes it a write. A plain read of the same path is still
  allowed.

- **The guard refuses when it cannot evaluate its own rules.** Every host reads exit 2 as a
  block and any other non-zero exit as "carry on", so an unhandled exception was an *allow* —
  and `"enforce": "all"` was enough to cause one, because a string has no `.get`. The eleven
  config keys the guard reads are type-checked before use, and anything else that goes wrong
  becomes a refusal that says so.

- **A receipt dated in the future is not a receipt.** Staleness was `age > limit`, so a
  receipt dated next month had a negative age and never expired: a hand-written
  `readiness.json` unlocked a merge the guard had refused moments earlier. A timestamp more
  than two minutes ahead is refused. `treeClean` was written on every receipt and read by
  nothing; a receipt granted over a clean tree now stops holding once the tree is dirty.
  Acceptances are written to the audit log, not only refusals.

- **Loosening the configuration is itself a weakening.** Setting the six `enforce` flags to
  `false` turned every refusal into an allow and left no trace, and committing that edit
  passed `sdlc tests audit` in silence. Switching a flag off stays a legitimate choice — what
  changes is that it is visible. The suite audit now reports nine kinds of loosening: a
  refusal switched off, a branch dropped from `protected`, an action removed from
  `neverByAgent`, a human approval downgraded to an agent's, receipts given a longer life, a
  budget ceiling raised or removed, a budget that warns instead of refusing, a reviewer or
  concern dropped, and a trunk change — plus the keys that decide what the gate *runs*:
  `verifyCmd`, `gateCmd`, `secretScan`, `quality.cmd`, `quality.coverageNewPct` and
  `spec.strict`. Replacing `verifyCmd` with `true` weakens the pipeline more completely than
  any flag, and nothing reported it. And when a non-default flag lets a command through that
  the defaults would have refused, the audit log records which rule and which flag.

  A correction: an earlier draft of this entry said deleting `enforce` "reads as switching
  all six off — which is what it does". That was wrong twice over. `enforce.get(flag, True)`
  defaults every flag to *on*, so deleting the key changes nothing, and the detector
  correctly reports nothing. The detector's defaults now mirror the guard's exactly, which
  also fixes a real miss: `approvals.release` defaults to `human` in the guard, so an
  explicit downgrade to `agent` from an absent key is a loosening and was not reported.

- **A finding id is an id, not a path.** `finding show` and `finding close` joined the id
  straight into a path, so `../../../elsewhere/victim` read a file outside the repository and
  `close` rewrote it. The shape is checked and the resolved path confirmed to be inside
  `.sdlc/findings`.

- **A budget an agent can rename its way out of is not a ceiling.** It was keyed on the branch
  name. With the ceiling spent, `git checkout -b other` made the next call allowed and
  overwrote the counter. It is keyed on the merge base against the trunk now, which no rename
  moves and which a new branch from the same point shares; counters are held per task rather
  than overwriting; a task starting its own budget is audited.

### Added

- `openspec/changes/verification.md` — the verification stage, run for the first time. 18
  requirements, 31 scenarios: 29 passed, 0 failed, **2 unexecuted**, both now findings of
  their own. Three passing scenarios hold by observation and carry no regression test; they
  are marked, because a scenario nothing guards is one a later change can break in silence.

### Fixed — round two, from an independent review of this branch

A code review and a security review, run against the branch, each independently found that
the parser rewrite above had reopened the bypass class it was written to close. Both
reports are in the commit history. Everything below came out of them, or out of working
through the rest of what the gate had raised against 3.0.0.

- **A refused command is refused wherever on the line it sits.** The credential rule keyed
  on a verb list, so the next reader of the same path was allowed — `xxd` was listed, `base64`
  was not. The path is a subject in its own right now.
- **The findings store reaches the enforcement boundary.** A READY receipt let a merge
  through with an open critical against the same commit. Open critical and high findings
  block a merge and the refusal names them; advisory does not.
- **Three paths that failed open.** `tree_clean` compared git's output to the empty string,
  so git failing to run read as a clean tree. `known_rules` returned an empty set when the
  rule table would not parse, and the caller then accepted any rule id at all. `subject_digest`
  joined a receipt-supplied path to the root unchecked and read it whole into memory on every
  guard call that consults that receipt.
- **`fixed` needs a commit.** A claim that something was repaired, with nothing behind it, is
  how a false-fix rate stays at zero while the defects come back.
- **The budget cannot be re-keyed.** Moving the local trunk ref or editing `trunk` produced a
  new key and a fresh ceiling. Spend is summed across the window; `reset --as` clears it.
- **A reading is not a measurement.** Each concern profile says a finding it owns is `medium`
  at most when read from a diff. That was prose; it is checked now, for the rules the control
  spec declares as `llm`, and a reproduction still earns `high`.
- **The detector no longer contains the strings it scans for.** The markers moved to
  `schema/suppression-patterns.json`, so `bin/sdlc` comes out of `suiteAudit.exclude` and the
  file implementing every control is scanned again. The obvious alternative — inferring from
  a line's text whether a marker is quoted — was tried and reverted: one apostrophe defeats
  it, and this project has rejected that heuristic twice before.
- **The contract says what the pipeline does.** The stage map was missing Impact and the
  architecture reviewer; `concerns` was absent from it entirely; reviewer selection had two
  authorities and now has one, the config; and the generated rules file's links resolved to
  nothing on every host.
- **The impact stage leaves a receipt**, `sdlc metrics` reads a structured field instead of
  re-parsing prose, the finding schema has a consumer in CI, secrets are redacted from the
  audit log, and the four GitHub Actions are pinned to commit SHAs.

All 64 findings raised against this branch are closed. The test suite is 431 assertions, up
from 248 at 3.0.0.

### Known, and not fixed here

- Three paths remain in `suiteAudit.exclude`: the marker data file, the suite that tests the
  detector, and an eval fixture quoting a bad diff. Each has to contain the strings the
  detector looks for in order to be what it is, and none holds logic. They are declared in
  the config where a reviewer sees them, and acknowledging them is a maintainer's decision.
- Two scenarios in `openspec/changes/verification.md` are `unexecuted`, and three more pass
  by observation with no regression test. Both facts are recorded there rather than rounded
  up to a pass.
- Precision and recall are still unmeasured. That needs a seeded-defect corpus;
  `docs/maturity.md` says how.

## [3.0.0] — 2026-10-25

Findings become data, the gate can no longer be lowered to pass itself, and the six taxonomy
domains the reviewers were silent on are covered.

**Major, because the gate got stricter.** Nothing was removed and no configuration key
changed meaning, but three things that previously passed now block: a configured
`quality.cmd` actually runs, a diff that weakens the test suite is refused, and a budget
ceiling stops a task. A repository that was green on 2.3.0 may not be green on this. That is
the point, and it is a narrowing, so it is a major.

### Added

- **A finding contract.** `schema/finding.schema.json` and `sdlc finding write|list|show|close`.
  A finding now carries an identity, a rule, a taxonomy address, evidence, a root cause, a
  verification plan and a provenance — not just the word "blocking". Findings deduplicate by
  content, so the same one raised twice is one finding rather than two comments.
- **`docs/control-spec.md`**, normative for every agent: the four vocabularies, the repair
  policy, the A–U and X1–X12 coverage map with an honest `review-level` marker, and a table of
  56 rules. A rule that lives only in a prompt is that agent's opinion, and `sdlc finding
  write` refuses a rule the table does not list.
- **Severity and confidence as independent axes.** What an agent may repair unattended comes
  from the pair, never from severity alone: `critical` at `low` confidence escalates to a
  person, `high` at `medium` needs a reproduction first, and `advisory` is never committed at
  any confidence.
- **`sdlc baseline capture|compare|show`.** The branch-opener records what the verify command
  said *before* any work began; the verifier and gate classify every later failure as `new`,
  `pre-existing` or `fixed`. Comparison is over normalised signal lines, so it works in any
  stack without a parser per test runner. Keyed to the merge base, so it survives commits —
  unlike a receipt, which must not.
- **`sdlc tests audit`.** Deleted test files, removed assertions, new skip markers, new
  suppression directives and lowered thresholds. Every agent prompt already forbade these;
  this is the part that does not negotiate. `--acknowledge` records a human decision and
  deliberately does not waive the finding.
- **`budget`.** `maxToolCalls` and `maxWallClockMin`, refused at the tool call and resettable
  only by a person.
- **`sdlc checkpoint write|resume|show`.** Stores a long task's progress *and the repository
  state it assumed*; `resume` re-validates branch, commit ancestry, file digests and toolchain
  before saying it is safe to continue.
- **`concerns`**, a second profile axis beside `profile`. Six cross-cutting profiles —
  `architecture`, `performance`, `memory`, `concurrency`, `data`, `platform` — covering
  taxonomy domains B, E, F, G, J, K, N and S. A Go service wants `service` *and*
  `concurrency`, which one field could not express. `sdlc init` proposes them from what the
  repository actually contains and never imposes one.
- **`sdlc-impact-analyst`** and **`sdlc-architecture-reviewer`**, both read-only. The first
  reports dependents, published shapes and ordered migration steps *before* implementation;
  the second walks the import graph, which is a different search from reading a diff.
- **Environment fingerprint on every receipt**, so an environmental failure is distinguishable
  from a defect.
- **Metrics that measure outcomes**, not just activity: findings by severity and taxonomy
  domain, verified repair rate, false-fix rate, human-intervention rate and reproducible
  share.
- Four evals for the new refusals, and tests for every detection in both directions.

- **Publishing runs from a GitHub release, over OIDC.** `.github/workflows/publish.yml`
  authenticates with npm Trusted Publishing — no stored token, no one-time password, and
  provenance attached automatically. The trigger is a published release, so cutting one
  stays the maintainer's act and the workflow is only the hands that carry it out; it
  refuses if the tag and `package.json` disagree, and re-runs the gate rather than
  trusting that it ran earlier.

### Noted

Running `sdlc tests audit` against this repository reported six weakenings that were not
weakenings: its own detection patterns, its own test fixtures, and the eval that quotes a
skipped test. A marker inside a string literal suppresses nothing and prose cannot disable a
linter, so neither is excluded at the cost of a bypass — but six false positives on the
tool's own diff is how a tool gets ignored, so both are now excluded, with regression tests
in each direction. Found by dogfooding, which is the point of dogfooding.

### Fixed

- **`quality.cmd` never ran.** It was in the schema, documented as the Level 2 configuration,
  and reserved as a receipt kind — and no agent or command executed it. The only consumer was
  the generated CI workflow. The readiness gate and the mechanical gate now run it, and an
  unset budget is reported as `skipped` rather than passed. Found by auditing this plugin
  against its own design brief.
- The OpenSpec commands in the agents and docs used `openspec change validate` and
  `openspec change show`, which warn as deprecated on openspec 1.6. An agent reading our docs
  would copy the deprecated form and paste the warning into its report as a finding. Found by
  dogfooding: this repository now has the `openspec/` scaffolding its own config always said
  it had.

### Documented

`docs/maturity.md` now says plainly what this still does not give you — detection precision
and recall, runtime evidence, token accounting, sandboxing — and, for precision and recall,
how to measure them yourself with a seeded-defect corpus. `docs/compliance.md` gains three
more honest limits rather than three more claims.

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
