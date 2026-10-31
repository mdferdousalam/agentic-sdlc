## 1. The contract

- [x] 1.1 `schema/finding.schema.json` defines the finding record: identity, category, ruleId,
      summary, evidence, classification, rootCause, proposedRepair, verificationPlan, outcome,
      provenance. Validates as JSON Schema 2020-12.
- [x] 1.2 `docs/control-spec.md` states the four vocabularies, the repair policy table, the
      A–U and X1–X12 coverage map with an honest "review-level" marker, and the rule table with
      a stable `ruleId` per row.
- [x] 1.3 `docs/rules.md` §3 gains severity and confidence beside the five evidence words, and
      points at the control specification as normative.

## 2. The tool

- [x] 2.1 `sdlc finding write` validates against the contract and writes `.sdlc/findings/F-xxxxxxxx.json`;
      an invalid enum value exits non-zero, names the field and writes nothing.
- [x] 2.2 `sdlc finding list` prints open findings; `--open`, `--severity` and `--json` filter it.
- [x] 2.3 `sdlc finding close <id> --outcome <word>` records the outcome and the closing commit;
      an unknown outcome word is refused.
- [x] 2.4 `autofixEligible` is computed from the repair-policy table, not accepted from the caller.
- [x] 2.5 `finding` events reach `.sdlc/audit.log` like every other stage event.

## 3. The quality budget

- [x] 3.1 `agents/sdlc-readiness-gate.md` runs `quality.cmd` after the secret scan and writes a
      `quality` receipt; a non-zero exit is NOT-READY.
- [x] 3.2 `commands/gate.md` runs `quality.cmd` and records the same receipt.
- [x] 3.3 An unconfigured `quality.cmd` is reported as `skipped`, never as passed.
- [x] 3.4 `sdlc doctor` notes when `quality.cmd` is unset and says what it costs.

## 4. The reviewing agents

- [x] 4.1 `sdlc-code-reviewer` and `sdlc-security-reviewer` classify each finding with a
      severity, a confidence and a `ruleId` from the rule table, and emit it with `sdlc finding write`.
- [x] 4.2 `sdlc-remediator` consults the repair policy before fixing, and escalates rather than
      repairing where the table says so.

## 5. Proof

- [x] 5.1 `tests/test_sdlc.py` covers: a valid finding is written; each invalid enum is refused;
      the policy table's autofix answer is computed correctly for the corner cells; closing with
      an unknown outcome is refused.
- [x] 5.2 A test feeds the schema's own enum values through the validator, so the two expressions
      of the contract cannot drift.
- [x] 5.3 The repository's own `verifyCmd` passes.
