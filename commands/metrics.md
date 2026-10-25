---
description: What the pipeline actually did — stage outcomes, refusals, actors
argument-hint: "[--since YYYY-MM-DD]"
---
!`"${CLAUDE_PLUGIN_ROOT}/bin/sdlc" metrics $ARGUMENTS 2>&1`

Read the numbers and say, in at most eight lines: which stage fails most often and what that
suggests, whether any refusal is firing repeatedly enough to indicate a workflow problem rather
than a near-miss, and one concrete change worth making.

A first-pass rate near 100% is a finding, not a success: it usually means a gate is not
checking anything.
