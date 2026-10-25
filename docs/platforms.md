# Platforms — what each one can actually enforce

One pipeline, many hosts. What differs is not the stages but **how much a host can refuse**,
and that difference is stated here rather than glossed over. A rule a host cannot enforce is
still useful as an instruction; it is just not a guarantee, and you should know which is which.

```sh
sdlc install --list     # what is supported, and what is detected on this machine
sdlc install            # install for every detected host, plus git hooks
sdlc install cursor codex --dry-run
sdlc uninstall          # removes only our blocks and the files we own
```

## The capability matrix

| Host | Refuses a tool call | Gets commands | How | Verified |
| --- | --- | --- | --- | --- |
| **Claude Code** | **yes** | yes | `PreToolUse` hook, exit 2 | live: `git stash` and an ungated `git push` both refused in a real session |
| **opencode** | **yes** | yes | plugin, `tool.execute.before` | live in a real session |
| **Codex CLI** | **yes** | yes | `PreToolUse` in `~/.codex/hooks.json` | live: `git stash` refused, and an ungated `git push origin main` refused by the receipt rule — the dynamic gates work there, not just the static ones. The user's existing `Stop` hook still fired in the same session |
| **Cline** | **yes** | yes (workflows) | executable `.clinerules/hooks/PreToolUse`, exit 2 | format read from the installed extension v4.1.25; live refusal untested |
| **Gemini CLI** | **static patterns only** | yes (TOML) | `.gemini/policies/*.toml`, `decision = "deny"` | policy keys and `run_shell_command` read from the 0.65.0 bundle. **Live test not possible**: Google now returns `UNSUPPORTED_CLIENT` for this client's free tier and points at Antigravity |
| **Cursor** | no | yes | `.cursor/rules/*.mdc` (`alwaysApply`), `.cursor/commands/` | paths read from the installed Cursor CLI |
| **GitHub Copilot** | no | yes (prompt files) | `.github/copilot-instructions.md`, `.github/prompts/*.prompt.md` | read from the Copilot extension shipped in VS Code |
| **Roo Code** | no | — | `.roo/rules/` | read from the installed extension v3.54.0 |
| **Kilo Code** | no | — | `.kilocode/rules/` | by convention — **not verified** |
| **Windsurf** | no | yes (workflows) | `.windsurf/rules/`, `.windsurf/workflows/` | by convention — **not verified** (no brew cask) |
| **Continue** | no | — | `.continue/rules/` | by convention — **not verified** |
| **Aider** | no | — | `CONVENTIONS.md` + `AGENTS.md` | documented behaviour |
| **Zed, Amp, Warp, Junie, Factory, Devin, Jules** | no | — | `AGENTS.md` | the agents.md adopter list |

Everything also gets **AGENTS.md**, which agents.md's own adopter list says is read by Codex,
Jules, Factory, Aider, Zed, Warp, VS Code, Devin, Junie, Amp, Cursor, RooCode, Gemini CLI, Kilo
Code, GitHub Copilot, Ona, Windsurf and Augment Code.

Where a format is marked **not verified**, the adapter writes the conventional path *and*
`AGENTS.md`, so the host still gets the rules even if its own layout has moved.

## The three layers

**1. A native tool hook** — Claude Code, opencode, Codex, Cline. The action is refused before
it happens, with a reason the model reads. Best experience, and the only layer that can enforce
a receipt-dependent rule ("this merge needs a READY verdict for *this commit*").

**2. Git hooks** — every host, installed by default. Every agent shells out to `git`, so this
catches Cursor, Copilot, Windsurf and a human in a terminal equally.

```console
$ git push origin main
BLOCKED by agentic-sdlc: pushing a protected branch needs a passed gate receipt, and there is
no gate receipt.
```

**It is bypassable with `--no-verify`.** That is a deliberate property of git, not an oversight
here, and it is why the third layer exists. The hook raises the floor; it does not seal it.

**3. CI** — `sdlc install ci` writes a workflow that re-runs the verify command, the secret
scan and the quality budget on every pull request. An agent never runs there, so it cannot be
talked around, skipped or `--no-verify`'d. It does not read receipts — they are local to a
working copy by design — it re-does the work.

If you take one thing from this page: **on a host without a native hook, CI is your real gate.**

## What installation touches

| Host | Writes outside the repository |
| --- | --- |
| Codex | `~/.codex/hooks.json` (merged — other events are preserved), `~/.codex/prompts/sdlc-*.md` |
| opencode | `~/.config/opencode/{agents,commands,plugins}/` |
| everything else | nothing outside the repository |

Every file we share with you — `AGENTS.md`, `copilot-instructions.md`, a git hook — is written
as a marked block:

```text
<!-- BEGIN agentic-sdlc (generated — edit docs/rules.md or sdlc.config.json, then re-run) -->
...
<!-- END agentic-sdlc -->
```

Re-running updates only that block. `sdlc uninstall` removes the block and leaves your file.
An existing `pre-commit` hook is appended to, never replaced.

## Adding a host

An adapter is one function, `adapt_<name>(root, cfg, writer)`, in `bin/sdlc`, plus an entry in
`TARGETS` and a row in this table. Use `_agents_md`, `_rules_file` and `_prompt_files` rather
than writing files directly, so markers and idempotence come for free. Add the host to
`detect_platforms()` and a case to `tests/test_sdlc.py`.

**Verify the format against the real tool before you add the row.** A file in a plausible path
that the host ignores is worse than nothing: it shows up as coverage and gives someone
confidence they have not earned.

## Windows

Untested. The installer resolves `python3` or `python` at install time and writes the resolved
interpreter into the hooks, and the git hooks are `/bin/sh` scripts that need Git Bash. Until
someone runs the suite on Windows, this page says untested rather than supported.
