---
description: Detect this project's stack and write sdlc.config.json
argument-hint: "[--write]"
---
!`"${CLAUDE_PLUGIN_ROOT}/bin/sdlc" init $ARGUMENTS`

!`"${CLAUDE_PLUGIN_ROOT}/bin/sdlc" doctor`

Read what detection produced. Then, in at most ten lines: say what this project is, and name
anything in the config that is wrong or missing for it — especially `verifyCmd`, `trunk` and
`spec.engine`. Fix what is plainly wrong by editing `sdlc.config.json`; never invent a command
the project cannot run. If `--write` was not passed, say so and show the command to write it.

If `profile` is unset, suggest one from `${CLAUDE_PLUGIN_ROOT}/profiles/` only if it clearly
fits; "none" is a perfectly good answer.
