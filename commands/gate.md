---
description: The mechanical gate — verify command, secret scan and quality budget — and the receipt a push needs
---
!`"${CLAUDE_PLUGIN_ROOT}/bin/sdlc" config 2>/dev/null | grep -E '"(verifyCmd|gateCmd|secretScan|cmd)"'; echo '--- tree ---'; git status --short --untracked-files=no | head; echo '--- head ---'; git log --oneline -1`

Run the repository's mechanical gate, in this order, and report each stage in the five words:

1. **Clean tree.** Uncommitted tracked changes mean the thing you would bless is not the thing
   in the commit. Stop there.
2. **`gateCmd` if the config sets one, otherwise `verifyCmd`.** Quote the real output. Do not
   re-run it hoping for a different answer; if you do re-run it, report both results.
3. **`secretScan`.** Any finding is blocking. If no scanner is configured, record that stage as
   `skipped` and say so — never as passed.
4. **`quality.cmd`** if the config sets one — the deterministic analysis budget on what this
   change adds. A non-zero exit is blocking. Record it separately, because it answers a
   different question from `verifyCmd`:

   ```sh
   sdlc receipt write quality --verdict passed|failed|skipped --detail "<what ran>"
   ```

   Unset is `skipped`, never passed. An LLM reviewer is not a substitute for a static analyser.

Then record the result, truthfully either way:

```sh
sdlc receipt write gate --verdict passed --detail "<what ran>"
sdlc receipt write gate --verdict failed --detail "<what failed>"
```

This receipt is what the harness requires before a push to a protected branch. It is **not** a
readiness verdict: it says the mechanical checks passed, not that the change is reviewed or that
the specification is satisfied. Merging still needs `/agentic-sdlc:readiness`.
