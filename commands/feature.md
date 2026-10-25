---
description: Start a unit of work — specify it, review the spec, open the branch
argument-hint: "<what you want built>"
---
Unit of work: $ARGUMENTS

!`"${CLAUDE_PLUGIN_ROOT}/bin/sdlc" status 2>&1 | head -20`

Drive these three stages in order, stopping at the first that does not pass:

1. `sdlc-spec-writer` — write the specification.
2. `sdlc-spec-reviewer` — review it and record the `spec` receipt. If the verdict is
   `changes-requested`, hand the findings back to the writer **once**, then review again. Two
   rounds is the limit; after that, report what is unresolved and stop.
3. `sdlc-branch-opener` — only on an approved receipt, create the branch.

Write no implementation code in this command. Finish by printing the next exact command.
