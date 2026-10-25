# Contributing

## What this repository is

Markdown and one Python file. The agents are prose addressed to a model; `bin/sdlc` is the part
that does not negotiate. Changes to the second need tests; changes to the first need judgement
about what a model will actually do with the words.

## Before you open a pull request

```sh
python3 tests/test_sdlc.py              # 46 cases: detection, guard, receipts, overrides
node .github/scripts/validate-plugin.mjs # structure: manifests, agents, commands, hooks, CLI
npx --yes markdownlint-cli2              # prose
```

All three run in CI. The validator is strict on purpose: an agent whose frontmatter `name`
disagrees with its filename is invisible to the Task tool, and a command referencing an agent
that does not exist fails at the worst moment.

## Adding or changing a rule the hook enforces

1. Add the pattern to the right group in `bin/sdlc` (`DESTRUCTIVE`, `PUBLISHING`, `STAGING`,
   `CREDENTIALS`), with a `why` that tells the reader the allowed route.
2. Add **both** cases to `tests/test_sdlc.py`: the command that must be blocked, and the nearby
   command that must not be. Most false positives are a missing second case — `git stash list`
   is not `git stash`.
3. If it should be switchable, add a key under `enforce` in the schema and honour it.

A rule the agents are merely told about is not enforcement. If it matters, it goes in the guard.

## Adding an agent

- One job. If you need the word "and" to describe it, it is two agents.
- Filename, frontmatter `name` and every reference in `commands/` must agree.
- State what it may **not** do, including the adjacent stage it must not wander into.
- Point it at `docs/rules.md` rather than restating the rules.
- If it ends a stage, it writes that stage's receipt — and no other agent's.

## Adding a profile

A profile is standards for a *kind* of project, and every line must be something a reviewer can
check against a diff. Taste is not a standard. If a rule only makes sense for one company's
codebase, it belongs in that repository, not here.

## Style

Write for someone reading at speed under pressure. Short sentences. No ornament, no "simply",
no "just". Say what is true, including when the honest answer is that something is not checked.

## Releasing

Update `CHANGELOG.md` and the `version` in `.claude-plugin/plugin.json` in the same commit.
Semver from the diff: a removed or renamed agent, command or config key is a major.
