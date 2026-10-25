---
description: Write the implementation report and update the documentation the change made stale
argument-hint: "[unit]"
---
Scope: $ARGUMENTS

!`git log --oneline -10; echo '--- changed ---'; git diff --name-only $(git merge-base HEAD origin/HEAD 2>/dev/null || echo HEAD~5) 2>/dev/null | head -40`

Use the `sdlc-reporter` agent. Record the decisions made during implementation that the
specification did not settle — that is the part nobody can reconstruct later. With OpenSpec,
archive the change once its specs are reflected in the published ones.
