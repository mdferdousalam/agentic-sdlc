---
description: Implement the current unit of work against its approved specification
argument-hint: "[which item, if not all]"
---
Scope: $ARGUMENTS (empty means the specification's checklist, in order)

!`"${CLAUDE_PLUGIN_ROOT}/bin/sdlc" status 2>&1 | head -20; echo '--- tree ---'; git status --short | head -15`

Use the `sdlc-implementer` agent. One item at a time, test first where the stack allows, commit
path-scoped, tick the checklist in the same commit. Stop when the scope is done — verification
and review are other stages.
