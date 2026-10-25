# Using the pipeline with opencode

[opencode](https://opencode.ai) has agents, commands and plugins, but no plugin marketplace, so
the same pipeline is installed by copying it in:

```sh
bin/sdlc-install-opencode            # ~/.config/opencode by default
opencode reload                      # a stale background server shows none of it
sdlc doctor                          # in the repository you will work in
```

Options: `--prefix <dir>`, `--model <provider/model>` (pin every agent to one model),
`--dry-run`.

## What the installer changes, and why

| Claude Code | opencode |
| --- | --- |
| `tools: [Read, Bash, Grep]` in frontmatter | `permission: { edit: deny, bash: allow }` |
| `${CLAUDE_PLUGIN_ROOT}` | this checkout's absolute path |
| `hooks/hooks.json` → `PreToolUse` | `plugins/agentic-sdlc.ts` → `tool.execute.before` and `shell.create.before` |
| `/agentic-sdlc:land` | `/sdlc-land` |

An agent whose Claude Code frontmatter lists no writing tool becomes `edit: deny` — so the
reviewers and the gate genuinely cannot edit, which in opencode is enforced by the host rather
than by the agent's good intentions.

## One rule set, two hosts

Both hosts call the same `bin/sdlc guard` with the same JSON and treat exit code 2 as a block.
There is one place to fix a rule and no way for the two to drift. If the guard cannot run at
all, it stays silent rather than taking the session down — enforcement that breaks your editor
gets uninstalled, and then you have none.

## Re-running

Re-run the installer after pulling a new version. It overwrites only the files it owns:
`agents/sdlc-*.md`, `commands/sdlc-*.md`, `plugins/agentic-sdlc.ts`.

## With free or small models

The pipeline was built partly for this case. Small models are not careless so much as
forgetful: they skip a stage, not out of malice but because nothing stopped them. Receipts and
the hook are exactly that stop. Pin the bigger model you have to the reviewers and the gate
(`reviewers` in the config, `--model` at install) and let a cheaper one implement.
