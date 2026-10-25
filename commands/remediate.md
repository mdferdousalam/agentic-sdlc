---
description: Fix the findings a review or gate produced — one per commit, each re-verified
argument-hint: "[which findings]"
---
Findings: $ARGUMENTS (empty means the blocking findings from the last review or gate)

!`"${CLAUDE_PLUGIN_ROOT}/bin/sdlc" feedback read 2>/dev/null; echo '--- tree ---'; git status --short | head`

Use the `sdlc-remediator` agent. One finding per commit, hardest first, each with a failing test
where the finding is behavioural, each re-verified before the next. Never suppress a warning to
close a finding.

End with the table: finding, outcome in the five words, commit, test.
