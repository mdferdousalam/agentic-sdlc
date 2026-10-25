# Profile: service

For long-running network services. The questions are about the second year of operation, not
the first deploy.

## Failure is specified

- Every outbound call states its timeout, its retry policy and what happens when it exhausts
  them. "Retry forever" is not a policy.
- Every failure path either degrades in a stated way or fails loudly. Nothing is swallowed.
- Partial writes are impossible, or the recovery path is specified and tested.
- Idempotency: any operation a client may retry states its idempotency key and behaviour.

## Operability

- Every new code path is observable: a log line with the correlation identifier, a metric, or a
  span. A failure mode that cannot be seen cannot be operated.
- Logs carry no personal data, credential or full payload by default.
- A new configuration value has a default, a documented range, and a stated behaviour when
  absent or invalid at startup.

## Load and limits

- Unbounded allocation, unbounded queues, unpaginated queries and user-controlled loop bounds
  are blocking findings.
- A new endpoint states its expected rate and its limit behaviour.

## Change safety

- A schema change is forward and backward compatible across one deploy, or the specification
  states the ordered migration.
- Rollback is possible, and the specification says what rolling back loses.
