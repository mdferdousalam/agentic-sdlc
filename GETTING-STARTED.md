# Getting started

A guided first hour. No prior knowledge of the pipeline assumed. If you have ten minutes, do
Part 1 and stop — it is useful on its own.

## What this actually is, in one paragraph

You ask an AI agent to build something. It writes code fast, and the hard part becomes knowing
whether the result is any good. This plugin puts stages between "asked" and "merged" — write
the spec, review the spec, branch, build, verify, review, gate, land — and then makes those
stages impossible to skip, by refusing the tool call. You still decide everything that matters.
The pipeline stops a confident agent from quietly skipping the step that would have caught it.

## Part 1 — install and look around (10 minutes)

**Using Claude Code?**

```sh
/plugin marketplace add mdferdousalam/agentic-sdlc
/plugin install agentic-sdlc
```

**Using anything else** — Cursor, Codex, Copilot, Gemini, Cline, Windsurf, Zed, Aider:

```sh
curl -fsSL https://raw.githubusercontent.com/mdferdousalam/agentic-sdlc/main/install.sh | sh
sdlc install        # detects your agents and sets each one up
```

Or with npm, if that is more your habit: `npx @mdferdousalam1989/agentic-sdlc install`.
Either way you need `git` and Python 3.8 or newer — nothing else.

It installs git hooks too, because on most hosts that is the only thing that can actually stop
a mistake. [What each host can and cannot enforce](docs/platforms.md) — worth two minutes
before you trust it.

Then, inside a project you work on:

```text
/agentic-sdlc:init --write
/agentic-sdlc:doctor
```

`init` looks at your repository and writes `sdlc.config.json` — your package manager, your
trunk branch, your test runner, your verify command. **Open that file and read it.** It is the
only place the pipeline learns about your project, and detection guesses. The field that
matters most is `verifyCmd`: the command that tells you the code is sound. If it is wrong or
empty, fix it now; nothing downstream works without it.

`doctor` tells you what is missing. `gitleaks not found` is worth fixing (`brew install
gitleaks`); the rest you can leave.

### See the enforcement for yourself

Ask your agent to run `git stash`. It will come back refused. That is the point: the rules are
not advice to a model that may or may not follow them.

## Part 2 — one real feature (30–45 minutes)

Pick something small and genuinely useful. Not a toy, not a rewrite.

### 1. Say what you want

```text
/agentic-sdlc:feature "add a --format=json flag to the export command"
```

Three things happen. A spec gets written. A second agent reviews it and usually asks for
changes — **this is the pipeline working, not failing**. Then, only once the spec is approved,
a branch is created.

> **Read the spec before it is approved.** Five minutes here saves an hour later. You are
> looking for: would someone who knows nothing else build the right thing from this? Is every
> requirement something you could check? Is anything missing that you were assuming?

### 2. Let it build

```text
/agentic-sdlc:implement
```

It works the checklist in order, writes tests, commits each item. If the spec turns out to be
ambiguous, it stops and asks rather than guessing. When that happens, answer the question and
let it carry on — that stop just prevented a silent wrong decision.

### 3. Check what was built against what you asked for

```text
/agentic-sdlc:verify
/agentic-sdlc:review
```

`verify` goes requirement by requirement and finds the code and the test for each. `review`
reads the diff for defects and, where it matters, security.

You will probably see `unexecuted` next to a requirement. It means nobody ran a test for it.
It is not a failure and it is not a pass, and the gate will treat it as blocking. That one word
is most of the value here.

### 4. The gate

```text
/agentic-sdlc:readiness
```

Clean tree, your verify command, a secret scan, the reviewers, every criterion checked against
real evidence. It answers READY or NOT-READY.

**NOT-READY on your first run is normal.** Fix what it found — `/agentic-sdlc:remediate` works
through findings one at a time — and run it again.

### 5. Land it

```text
/agentic-sdlc:land
```

Branch pushed, pull request opened, with the criteria and their evidence in the body. Review
the PR yourself and merge it the way you always do.

## When something is blocked

You will see a message like:

```text
BLOCKED by agentic-sdlc: merging needs a READY readiness receipt, and there is no readiness
receipt. Run `/agentic-sdlc:readiness`.
```

Every refusal names what is missing and what to do. Three rules:

1. **Do the thing it asks for.** It is almost always two minutes of work.
2. **Do not argue with the agent about it.** The refusal is a hook, not an opinion; the model
   cannot grant an exception and will waste your tokens trying.
3. **If a rule is genuinely wrong for your project, turn it off in the config** — `enforce` in
   `sdlc.config.json`. That is a visible, reviewable decision. Working around it is not.

`/agentic-sdlc:status` shows which stages have left evidence and which have not.

## The vocabulary, because it is used precisely

**passed** — it ran and succeeded. **failed** — it ran and did not.
**skipped** — the runner skipped it. **refused** — the system correctly declined.
**unexecuted** — nobody ran it.

The last three are not "passed". Most bad agentic reporting comes from collapsing them.

## Three things worth doing in week one

1. **Set a profile.** `"profile": "webapp"`, `library`, `service` or `compiler` in the config.
   The reviewers then hold you to the standards that match what you are building, instead of
   generic advice. See [profiles](profiles/README.md).
2. **Make `verifyCmd` strict.** It is the floor of every gate. If it does not catch a broken
   build today, it will not catch one next month either.
3. **Read one spec properly before approving it.** The single highest-leverage habit here. An
   agent will build the wrong thing beautifully if you let it.

## Common questions

**Do I have to use every stage?** No. The three enforced ones are branch-needs-approved-spec,
push-to-trunk-needs-gate, and merge-needs-readiness, and each can be turned off in `enforce`.
Start with whichever subset you will actually use.

**Does this work without OpenSpec?** Yes — the spec becomes a PRD and an FRD, and everything
downstream is identical. OpenSpec adds a validator and an archive if you want them.

**Does it work outside Claude Code?** Yes — `sdlc install` covers Codex, Cline, Cursor, Copilot, Gemini, Windsurf, Roo, Kilo, Continue, Aider and every AGENTS.md host. Four of them can refuse a tool call outright; the rest rely on the git hooks and CI. The [matrix](docs/platforms.md) is explicit about which is which.

**What if my team does not use agents yet?** The gates work on human changes too, and most
teams find the specification review is where the value shows up first.

**Where do I go next?** [The pipeline in detail](docs/pipeline.md) ·
[Configuration](docs/configuration.md) · [Maturity levels](docs/maturity.md) ·
[A worked example](examples/worked-example.md)
