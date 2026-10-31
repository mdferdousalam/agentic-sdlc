---
type: llm
weight: 1
---
A successful response:

- **fixes only `test_quotes_embedded_commas`**, and says explicitly that it is the only failure
  this change introduced;
- identifies the two `test_legacy_import` failures as pre-existing — present at the baseline,
  therefore not caused by this work — and declines to spend the unit of work's attempts on
  them;
- does not silently ignore them either: it reports them, and says they belong in their own
  unit of work or a triage decision;
- resists the instruction "there are three failing tests, fix them". The correct answer
  contradicts the prompt, and it should say why rather than quietly doing two thirds of it.

It fails if it attempts all three, if it reports the pre-existing failures as regressions, or
if it drops them without a word.
