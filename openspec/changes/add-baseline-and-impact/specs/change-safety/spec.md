## ADDED Requirements

### Requirement: A baseline is captured before work begins

The system SHALL record, at the point a unit of work starts, the result of the project's verify
command, the set of failure and warning signals in its output, and the versions of the tools
that produced it. The record SHALL be keyed to the base commit the work branches from, and
SHALL survive subsequent commits on that branch.

#### Scenario: a baseline is captured on a repository with failing tests

- **WHEN** `sdlc baseline capture` runs where the verify command already fails
- **THEN** it records the non-zero exit and the failing signals, and reports that the
  repository was not green when the work started

#### Scenario: a baseline survives a commit

- **WHEN** a commit is made after the baseline was captured
- **THEN** the baseline is still current, because it is keyed to the base and not to HEAD

### Requirement: A failure is attributed, not assumed

The system SHALL compare the current verify result against the baseline and SHALL classify each
failure signal as newly introduced, pre-existing, or fixed. A pre-existing failure SHALL NOT be
reported as caused by the change.

#### Scenario: a pre-existing failure is not blamed on the change

- **WHEN** a test that was already failing at the baseline is still failing
- **THEN** `sdlc baseline compare` reports it as pre-existing and does not count it against the
  change

#### Scenario: a newly introduced failure is blocking

- **WHEN** a failure signal appears that was not in the baseline
- **THEN** `sdlc baseline compare` exits non-zero and names the signal

#### Scenario: no baseline exists

- **WHEN** `sdlc baseline compare` runs and no baseline was captured
- **THEN** it says so and reports the comparison as `unexecuted` rather than as passed

### Requirement: Downstream impact is reported before implementation

The pipeline SHALL provide a read-only stage that reports which code depends on what a unit of
work will change, which published interfaces it touches, and which migrations it implies. The
stage SHALL state the limits of its analysis rather than implying completeness.

#### Scenario: a change to a published interface names its consumers

- **WHEN** the impact analyst examines a change that alters an exported symbol
- **THEN** it lists the call sites it found and states that dynamic dispatch and reflection are
  outside what a textual search can see

### Requirement: Receipts carry an environment fingerprint

Every receipt SHALL record the versions of the tools that produced the result it attests to, so
that a failure can be attributed to the environment rather than to the change.

#### Scenario: a verdict records what produced it

- **WHEN** any stage writes a receipt
- **THEN** the receipt carries the versions of the relevant toolchain binaries
