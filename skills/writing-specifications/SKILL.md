---
name: writing-specifications
description: >
  How to write a specification this pipeline can verify — falsifiable requirements, specified
  refusals, stated scope, named open questions. Use when writing or reviewing a PRD, FRD,
  OpenSpec proposal or tasks list, or when a spec review returns changes-requested.
---

# A specification the pipeline can verify

The test of a specification here is mechanical: can the verifier, months later, take each line
and find evidence for or against it? If not, the line is prose, not a requirement.

## Falsifiable, one deliverable at a time

For each requirement, name the observation that would show it unmet.

| Not verifiable | Verifiable |
| --- | --- |
| Improve error handling | On a 5xx from the payment provider, the order stays `pending`, the user sees `PAY-003`, and the job retries three times at 1s/4s/16s |
| Make the parser robust | `parse()` refuses an unterminated string with `E0012`, naming the line and column |
| Add caching | A second identical request within 60s is served from cache, and a write invalidates it within one request |

## Specify the refusals

Most defects live where nothing was specified: the empty input, the duplicate, the expired
token, the concurrent write, the half-finished upload. Every error a user can reach has a name,
a code where the project uses codes, and a stated message. "The implementation will decide" is
how two call sites end up disagreeing.

## State the scope, both ways

Write what is **out** of scope as deliberately as what is in. An explicit non-goal stops the
implementer gold-plating and stops the reviewer raising it as a gap.

## Name the open questions

An unknown written down is a question; an unknown assumed is a defect with a delay. Mark the
ones that are the maintainer's — publishing, a safety rule, removing something users have,
licensing, scope — and leave them open rather than deciding them.

## Cite, do not restate

If an authority document already defines something, cite the section. A restatement is a second
copy that will drift, and the drift will be discovered by someone trusting the wrong one.

## Size

One unit of work is one branch, one review and one merge. If the checklist has twenty items
spanning three subsystems, it is three units wearing one name — split it, and say what order
they go in.
