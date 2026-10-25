## ADDED Requirements

### Requirement: Findings are validated records

Every finding raised by an agent or a tool SHALL be expressible as a record carrying an
identity, a taxonomy category, a rule identifier, a one-sentence summary, evidence, a
classification, an outcome and provenance. A record missing any of these SHALL be rejected.

#### Scenario: a complete finding is accepted

- **WHEN** `sdlc finding write` is given a rule, a severity, a confidence, a file and a summary
- **THEN** it writes a record to `.sdlc/findings/` with a generated `F-xxxxxxxx` identity and
  exits 0

#### Scenario: an incomplete finding is refused

- **WHEN** `sdlc finding write` is given a severity that is not one of the five severity words
- **THEN** it exits non-zero, names the offending field, and writes nothing

### Requirement: Severity and confidence are independent

The system SHALL record how bad a finding is if real (`critical`, `high`, `medium`, `low`,
`advisory`) separately from how sure it is that the finding is real (`high`, `medium`, `low`).
Neither value SHALL be derivable from the other.

#### Scenario: a critical finding with low confidence is not auto-fixable

- **WHEN** a finding is classified `critical` severity and `low` confidence
- **THEN** the repair policy marks it not eligible for automatic repair, and the correct outcome
  is `escalated`

### Requirement: The repair policy governs what an agent may fix

An agent SHALL determine whether it may repair a finding unattended from the severity and
confidence pair together, as tabulated in the control specification, and never from severity
alone. An `advisory` finding SHALL NOT produce an automatic code change at any confidence.

#### Scenario: a low-severity high-confidence finding is repaired automatically

- **WHEN** a finding is `low` severity and `high` confidence and the repair is deterministic
- **THEN** the remediator may fix it without escalation, still one finding per commit

#### Scenario: an advisory finding is reported, not committed

- **WHEN** a finding is classified `advisory`
- **THEN** the remediator reports evidence and alternatives and makes no code change

### Requirement: The quality budget runs and is recorded

Where `quality.cmd` is configured, the mechanical gate and the readiness gate SHALL run it and
SHALL record the result as a `quality` receipt. Where it is not configured, the stage SHALL be
recorded as `skipped` and SHALL NOT be reported as passed.

#### Scenario: a configured quality command fails the gate

- **WHEN** `quality.cmd` exits non-zero during the readiness gate
- **THEN** the gate writes a `quality` receipt with verdict `failed` and returns NOT-READY

#### Scenario: no quality command is configured

- **WHEN** `quality.cmd` is null
- **THEN** the gate records the quality stage as `skipped`, says so in the verdict, and does not
  treat it as passed

### Requirement: One control specification is normative

The repository SHALL carry a single versioned control specification stating the vocabularies,
the repair policy, the taxonomy coverage map and the rule table. A rule that exists only inside
an agent's prompt SHALL NOT be treated as a rule.

#### Scenario: a reviewer cites a rule

- **WHEN** a reviewing agent raises a finding
- **THEN** the finding's `ruleId` resolves to a row in the control specification's rule table
