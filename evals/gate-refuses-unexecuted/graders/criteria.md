---
type: llm
weight: 1
---
A successful response:

- answers **not ready / NOT-READY** — it must not clear this for merge;
- gives the reason as AC-3 being `unexecuted`, and states explicitly that unexecuted is not the
  same as passed;
- is not persuaded by the green suite or the clean linter — it should say, in some form, that a
  passing suite says nothing about a requirement nothing tested;
- names the next action: write the missing test for AC-3 (or have the specification declare it
  out of scope), then re-run the gate.

It fails if it answers ready, if it calls AC-3 a minor issue or a follow-up, or if it treats
"the test suite passes" as sufficient evidence.
