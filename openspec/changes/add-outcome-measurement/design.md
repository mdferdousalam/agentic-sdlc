## Context

The brief lists ten outcome metrics. Nine are derivable from the finding store and the audit
log. The tenth pair — precision and recall — needs ground truth about defects the pipeline did
not find, which a repository does not have about itself.

## Goals / Non-Goals

**Goals:**

- Report the measures the records now support.
- State each measure's definition in its own output.
- Be explicit about the measure that is missing, and say how to get it.

**Non-Goals:**

- Estimating precision or recall from anything other than a seeded corpus.
- A dashboard. This is a command that prints what the log says.

## Decisions

- **Every rate prints its numerator and denominator.** A metric whose definition is unstated
  is how a dashboard starts lying, and these are rates over small numbers where the definition
  matters more than the percentage.
- **False-fix rate is derived from the audit log**, not stored: a finding whose id is raised
  again after being closed `fixed` did not stay fixed. That is the honest signal available
  without a second bookkeeping system.
- **`unexecuted` findings are called out separately**, not folded into a rate. They are the
  number that quietly becomes a lie, because each one *looks* closed.
- **Precision and recall are refused rather than approximated.** A plausible-looking number
  with no ground truth behind it would be worse than the blank, because someone would quote
  it. The method goes in `docs/maturity.md` so the gap is actionable rather than just honest.

## Risks / Trade-offs

- Small denominators make early percentages meaningless. Mitigated by always printing the
  counts beside the rate.
