---
description: Requirement to commit to test to pull request, for an auditor or a future maintainer
argument-hint: "[--json]"
---
!`"${CLAUDE_PLUGIN_ROOT}/bin/sdlc" trace $ARGUMENTS 2>&1`

Explain in a few lines what this change can and cannot prove about itself: which stages left
evidence, which did not run, and whether a reader a year from now could reconstruct why each
line exists. Name the weakest link.
