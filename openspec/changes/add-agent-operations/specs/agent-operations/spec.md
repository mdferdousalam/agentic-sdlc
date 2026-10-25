## ADDED Requirements

### Requirement: Weakening the gate is detected, not merely forbidden

The system SHALL examine a change for deleted test files, removed test declarations, removed
assertions, newly added skip markers, newly added suppression directives and lowered numeric
thresholds, and SHALL report each with the evidence that identified it.

#### Scenario: a deleted test file is caught

- **WHEN** a change deletes a file under a test path
- **THEN** `sdlc tests audit` exits non-zero and names the file

#### Scenario: a lowered threshold is caught

- **WHEN** a change reduces a numeric setting such as a coverage threshold
- **THEN** the audit names the setting and both values

#### Scenario: strengthening the suite is not a finding

- **WHEN** a change adds a test and an assertion and removes none
- **THEN** the audit exits zero

#### Scenario: a justified weakening is recorded, not waived

- **WHEN** the audit runs with `--acknowledge`
- **THEN** it exits zero, records the acknowledgement, and the findings remain visible

### Requirement: An agent cannot raise its own ceiling

Where a budget is configured, the system SHALL refuse further tool calls once the ceiling is
reached, SHALL name the command that resets it, and SHALL NOT allow an agent to reset it
implicitly.

#### Scenario: the ceiling stops the task

- **WHEN** a task exceeds `budget.maxToolCalls`
- **THEN** the hook refuses the next tool call and names `sdlc budget reset`

#### Scenario: no ceiling configured

- **WHEN** no budget is set
- **THEN** nothing is refused, and `sdlc budget show` states plainly that nothing will stop a
  runaway task

### Requirement: A checkpoint is not automatically safe to resume

Resuming SHALL re-validate the branch, the commit, the digests of the files the checkpoint
named, and the toolchain, and SHALL refuse to declare the resume safe when any differs.

#### Scenario: a file changed under the checkpoint

- **WHEN** a file the checkpoint recorded has changed
- **THEN** `sdlc checkpoint resume` exits non-zero and names the file

#### Scenario: the repository still matches

- **WHEN** nothing the checkpoint recorded has changed
- **THEN** it reports the completed steps, the next step, and that it is safe to continue
