---
description: Push the branch and open the pull request; merge only behind a READY receipt
argument-hint: "[--merge]"
---
Options: $ARGUMENTS

!`git status --short; echo '--- branch ---'; git rev-parse --abbrev-ref HEAD; echo '--- receipts ---'; "${CLAUDE_PLUGIN_ROOT}/bin/sdlc" status 2>&1 | sed -n '/receipts/,$p'`

Use the `sdlc-lander` agent. Merge only if `--merge` was passed **and**
`sdlc receipt check readiness --verdict ready` exits 0. Never tag, release, publish or deploy.
