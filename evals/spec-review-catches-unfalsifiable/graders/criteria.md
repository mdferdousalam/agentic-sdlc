---
type: llm
weight: 1
---
A successful response:

- returns a verdict of **changes-requested** (or an unambiguous "not ready to build"), not an
  approval;
- identifies FR-1 ("gracefully"), FR-2 ("fast" with no number) and AC-1 ("users are happy") as
  unverifiable — it must name at least two of these three specifically;
- does **not** flag FR-3, which is correctly falsifiable: it names the command, the output, the
  exit codes and the error identifier;
- says, for at least one finding, what would make it verifiable (a number, a threshold, an
  observable behaviour), rather than only labelling it vague.

It fails if it approves the specification, if it rewrites the specification instead of
reporting on it, or if it treats FR-3 as a problem.
