<!-- BEGIN agentic-sdlc (generated — edit docs/rules.md or sdlc.config.json, then re-run) -->
## The agentic SDLC pipeline

This project uses the agentic-sdlc pipeline. Work moves through stages, each owned
by one agent and closed by a receipt bound to a commit. Do not skip a stage: on some
hosts the skip is refused outright, and on all of them a git hook and CI will catch
it later, more expensively.

### Commands

```sh
sdlc status            # which stages have left evidence, which have not
sdlc trace             # requirement -> commit -> test -> receipts
sdlc receipt check readiness --verdict ready
sdlc feedback read     # why the last attempt failed, before you retry
```
<!-- END agentic-sdlc -->
