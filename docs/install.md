# Installing

Six ways in. They all land on the same CLI; pick whichever matches how you already install
things. Everything needs `git` and Python 3.8+ — there are no Python dependencies.

| Route | Command | Needs |
| --- | --- | --- |
| **Claude Code plugin** | `/plugin marketplace add mdferdousalam/agentic-sdlc` then `/plugin install agentic-sdlc` | Claude Code |
| **Shell** | `curl -fsSL https://raw.githubusercontent.com/mdferdousalam/agentic-sdlc/main/install.sh \| sh` | curl |
| **npm** | `npx @mdferdousalam/agentic-sdlc install` | Node 16+ |
| **PyPI** | `uvx --from agentic-sdlc-cli sdlc install` or `pipx install agentic-sdlc-cli` | Python |
| **Homebrew** | `brew install mdferdousalam/tap/agentic-sdlc` | macOS/Linux |
| **Codex plugin** | `codex plugin marketplace add mdferdousalam/agentic-sdlc` then `codex plugin add agentic-sdlc@agentic-sdlc` | Codex CLI |
| **Gemini extension** | `gemini extensions install https://github.com/mdferdousalam/agentic-sdlc` | Gemini CLI |
| **Git clone** | `git clone … && agentic-sdlc/bin/sdlc install` | git |

Then, in the repository you work in:

```sh
sdlc install     # detect your agents, set each one up, add the git hooks
sdlc doctor      # what is configured, what is missing, and the command for each gap
```

## A note on the Codex plugin route

Installing the Codex plugin brings its `PreToolUse` hook with it, but **Codex will not run a
plugin's hook until you trust it**. On your next interactive session Codex shows the hook for
review; trust it once and enforcement is live. Verified: untrusted, only `Stop` fires and a
`git stash` goes through; trusted, the same command is refused.

If you would rather not deal with the review prompt, `sdlc install codex` writes the hook into
your own `~/.codex/hooks.json` instead, which Codex treats as already trusted because it is
your configuration. That path is verified working, including the receipt-dependent push gate.

Never pass `--dangerously-bypass-hook-trust` as a workaround. It disables review for *every*
hook in the session, not just this one.

## A note on `curl | sh`

Piping a script from the internet into a shell is a real risk and you should not take anyone's
word for it. [`install.sh`](../install.sh) is about sixty lines, and it downloads a release
into `~/.agentic-sdlc`, links `sdlc` into a bin directory already on your `PATH`, and touches
nothing in your repository. No sudo. Read it first if you prefer:

```sh
curl -fsSL https://raw.githubusercontent.com/mdferdousalam/agentic-sdlc/main/install.sh -o install.sh
less install.sh && sh install.sh
```

Pin a version with `AGENTIC_SDLC_VERSION=v2.2.0`, or relocate it with `AGENTIC_SDLC_HOME`.

## Uninstalling

```sh
sdlc uninstall              # remove our blocks and the files we own from this repository
rm -rf ~/.agentic-sdlc      # shell install
npm rm -g @mdferdousalam/agentic-sdlc
pipx uninstall agentic-sdlc-cli
brew uninstall agentic-sdlc
```

`sdlc uninstall` removes only our marked blocks and the files we own. Your `AGENTS.md`,
Copilot instructions and existing git hooks keep everything that was yours.

## Maintainer: cutting a release

```sh
packaging/build-pypi.sh --check     # builds dist/, installs the wheel in a venv, runs it
python3 -m twine upload dist/*      # PyPI
npm publish --access public         # npm
```

Then bump `url`, `version` and `sha256` in `packaging/homebrew/agentic-sdlc.rb`
(`curl -fsSL <url> | shasum -a 256`) and copy it into the tap. `package.json` and
`.claude-plugin/plugin.json` must agree on the version — CI checks that.
