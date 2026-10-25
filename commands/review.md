---
description: Review the current change — code, and security where it applies
argument-hint: "[--security-only]"
---
Options: $ARGUMENTS

!`git diff --stat $(git merge-base HEAD origin/HEAD 2>/dev/null || echo HEAD~1) 2>/dev/null | tail -25; echo '--- log ---'; git log --oneline -5`

Launch `sdlc-code-reviewer`, and `sdlc-security-reviewer` as well whenever the diff touches
authentication, input parsing, dependencies, file or network I/O, or anything handling a
credential. Run them in one message so they work concurrently. Summarise both verdicts and the
blocking findings; do not fix anything here.
