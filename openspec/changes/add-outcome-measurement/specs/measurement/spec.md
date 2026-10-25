## ADDED Requirements

### Requirement: Outcomes are reported, with their definitions

The metrics command SHALL report findings by severity and taxonomy domain, the verified repair
rate, the false-fix rate, the human-intervention rate and the reproducible share, and SHALL
print the counts each rate is computed from.

#### Scenario: a rate is reported with its basis

- **WHEN** `sdlc metrics` reports the verified repair rate
- **THEN** it prints the number of findings fixed with proof and the number of repairs
  attempted, beside the percentage

#### Scenario: unverified fixes are called out

- **WHEN** any finding is closed as `unexecuted`
- **THEN** the output states that those fixes were never proved and are not closed

### Requirement: Unmeasurable metrics are refused, not estimated

The system SHALL NOT report detection precision or recall, and SHALL state why and how they
could be measured.

#### Scenario: precision is asked for

- **WHEN** `sdlc metrics` runs with findings recorded
- **THEN** it states that precision and recall require a seeded-defect corpus and points at
  the documented method
