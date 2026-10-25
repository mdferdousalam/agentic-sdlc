---
description: Check the pipeline install, the configuration and the repository
---
!`"${CLAUDE_PLUGIN_ROOT}/bin/sdlc" doctor 2>&1`

!`"${CLAUDE_PLUGIN_ROOT}/bin/sdlc" config 2>&1 | head -40`

Explain each problem in one line and give the exact command that fixes it. If everything is
fine, say so in one line and stop.
