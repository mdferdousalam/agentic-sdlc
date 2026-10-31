---
description: Who depends on what this change touches — before it is written, not after the gate
---
!`git log --oneline -1; echo '--- spec receipt ---'; "${CLAUDE_PLUGIN_ROOT}/bin/sdlc" receipt show spec 2>/dev/null | head -5`

Launch `sdlc-impact-analyst` for the current unit of work.

It reads the specification rather than a diff, because the useful time to learn that a published
interface has consumers is before the implementer commits to a shape. Summarise: the dependents
it found, the published shapes it touches, the ordered migration steps, what is irreversible,
and what a textual search could not see.

Anything blocking becomes a finding. Nothing here edits code.
