---
description: The pre-merge gate — mechanical checks, secret scan, reviewers, criteria → READY or NOT-READY
---
!`"${CLAUDE_PLUGIN_ROOT}/bin/sdlc" status 2>&1 | head -20; echo '--- tree ---'; git status --short --untracked-files=no | head`

Use the `sdlc-readiness-gate` agent. Follow its order exactly: clean tree, mechanical gate,
secret scan, reviewers, specification conformance, the record. Record the receipt either way —
`not-ready` is the normal outcome of a real gate.
