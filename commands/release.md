---
description: Deploy a merged change and prove it works there — with a rollback plan and a human approval
argument-hint: "<environment>"
---
Environment: $ARGUMENTS

!`"${CLAUDE_PLUGIN_ROOT}/bin/sdlc" status 2>&1 | sed -n '/receipts/,$p'`

!`grep -A8 '"release"' sdlc.config.json 2>/dev/null || echo 'no release config — set release.deployCmd, smokeCmd and rollbackCmd before deploying anything'`

Use the `sdlc-release-manager` agent. The order is not negotiable: READY receipt, written
rollback plan, named irreversible steps, human approval, deploy the lowest environment first,
observe the system itself, then decide.

If the human approval is missing, print the exact command for a person to run, and stop. Do not
run it yourself — an approval you grant yourself records nothing.
