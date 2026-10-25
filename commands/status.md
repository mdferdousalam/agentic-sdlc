---
description: Where this unit of work stands — stages, receipts, what is next
---
!`"${CLAUDE_PLUGIN_ROOT}/bin/sdlc" status 2>&1`

!`git log --oneline -5; git status --short | head -10`

In at most eight lines: which stages have left a valid receipt, which have not, and the single
next command. If a receipt is stale, say which commit invalidated it.
