## 1. Metrics

- [x] 1.1 Findings by severity and by taxonomy domain.
- [x] 1.2 Verified repair rate, human-intervention rate, reproducible share — each with counts.
- [x] 1.3 False-fix rate derived from the audit log: a finding re-raised after closing `fixed`.
- [x] 1.4 `unexecuted` findings called out separately rather than folded into a rate.
- [x] 1.5 Attribution rate from baseline comparisons, and how often a diff weakened a check.
- [x] 1.6 Precision and recall explicitly refused, with a pointer to the method.

## 2. Evals

- [x] 2.1 `remediator-refuses-weakened-test` — deadline pressure plus three weakenings at once.
- [x] 2.2 `critical-low-confidence-escalates` — severity alone must not authorise a patch.
- [x] 2.3 `baseline-attributes-failure` — the correct answer contradicts the prompt.
- [x] 2.4 `budget-stops-rather-than-asks` — the agent must not raise its own ceiling.

## 3. Honest limits

- [x] 3.1 `docs/maturity.md` states what is still missing and how to measure precision/recall.
- [x] 3.2 `docs/compliance.md` gains three limits rather than three claims.
- [x] 3.3 `README.md` corrects the agent count and describes findings as records.

## 4. Release

- [x] 4.1 Version 3.0.0 across every manifest CI holds together; major because the gate got
      stricter and a previously green repository may not be.
- [x] 4.2 `CHANGELOG.md`.
- [x] 4.3 The repository's own `verifyCmd` passes.
