---
description: Cross-verify what was built against what was specified
argument-hint: "[unit]"
---
Unit: $ARGUMENTS (empty means the one this branch is named for)

!`git log --oneline -8; echo '--- diff ---'; git diff --stat $(git merge-base HEAD origin/HEAD 2>/dev/null || echo HEAD~1) 2>/dev/null | tail -20`

Use the `sdlc-verifier` agent. Requirement by requirement, with `file:line` and a real test
outcome in the five words. Do not write tests here and do not fix code here — report gaps.
