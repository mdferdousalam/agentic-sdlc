---
name: verification-report
description: >
  Generate the Cross-Verification Report (CVR) for a feature: verify the implementation
  on the branch against its DI, FRD, and PRD, item by item. Use after implementation and
  before the readiness gate, or when asked to "run the CVR / cross-verify this feature".
---

# /verification-report — Cross-Verification Report (CVR)

The CVR is the evidence that what was built matches what was specified. It is a
line-by-line audit, not a summary.

## Setup

1. Read `sdlc.config.json` for `docsRoot` and `verifyCmd`.
2. Read the feature's `PRD_v1.0.md`, `FRD_v1.0.md`, `DI_v1.0.md`.
3. Inspect the actual diff on the branch against `trunk` and the affected source files.

## Procedure

- For each **FRD functional requirement** and **acceptance criterion**: locate the
  implementing code and the covering test. Mark `met / partial / missing` with
  `file:line` evidence.
- For each **DI build step**: confirm it was done as specified or note the justified
  deviation.
- **Configurability audit:** confirm every value the spec marked configurable is read
  from a config/reference table and is admin-CRUD-able — not hardcoded. Any violation
  is a blocking finding.
- Run `verifyCmd` and record the result.

## Output

Write `<docsRoot>/<phase>/<module>/<feature>/CVR_of-DI-v1.0_r1.md`
(increment `_rN` on re-runs):

```markdown
# CVR — <phase>/<module>/<feature> (of DI v1.0, r1)

## Verify command
<verifyCmd> -> pass/fail (paste key output)

## Requirement coverage
| FR / AC | Status | Evidence (file:line) | Test |
|---------|--------|----------------------|------|
| FR-1 | met | ... | ... |

## DI step conformance
| Step | Status | Note |

## Configurability audit
| Configurable value | Sourced from table? | CRUD exposed? | Verdict |

## Blocking findings
## Non-blocking findings
## Verdict: PASS | FAIL
```

## Hard rules

- A missing test for any acceptance criterion is a blocking finding.
- A hardcoded configurable value is a blocking finding.
- Cite `file:line` for every "met" claim — no unsupported passes.
