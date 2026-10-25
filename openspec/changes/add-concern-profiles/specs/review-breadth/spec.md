## ADDED Requirements

### Requirement: Cross-cutting concerns are selected independently of project kind

The configuration SHALL accept a list of cross-cutting concerns alongside the single
project-kind profile, and reviewing stages SHALL apply the core rules, the project-kind
profile, and every named concern.

#### Scenario: a service with concurrent code takes both

- **WHEN** the configuration names profile `service` and concern `concurrency`
- **THEN** reviewers hold the change to both sets of standards, not to one of them

### Requirement: Concerns are proposed from evidence, never imposed

`sdlc init` SHALL propose concerns based on what the repository demonstrably contains, and
SHALL NOT re-add a concern a maintainer has removed.

#### Scenario: detection proposes from repeated evidence

- **WHEN** a repository contains goroutines and mutexes in more than one file
- **THEN** `sdlc init` proposes the `concurrency` concern

#### Scenario: a removed concern stays removed

- **WHEN** a maintainer empties the `concerns` list and `sdlc init --write` runs again
- **THEN** the list is still empty

### Requirement: A reading is not a measurement

Every concern SHALL state the deterministic tool that would settle its findings, and findings
raised by reading alone SHALL be recorded at no higher than `medium` confidence.

#### Scenario: a performance finding from a diff

- **WHEN** a reviewer identifies a possible performance defect by reading the diff
- **THEN** the finding records `llm` detection at `medium` confidence, not `high`

### Requirement: Every cited rule resolves

A rule identifier used by any agent or profile SHALL exist in the control specification's rule
table, and a finding citing an unknown rule SHALL be refused.

#### Scenario: a finding under an unlisted rule

- **WHEN** `sdlc finding write` is given a rule identifier absent from the table
- **THEN** it exits non-zero and says the row must be added first
