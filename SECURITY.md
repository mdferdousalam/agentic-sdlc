# Security Policy

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

Use GitHub's private vulnerability reporting:
**Security tab → "Report a vulnerability"**
(<https://github.com/mdferdousalam/agentic-sdlc/security/advisories/new>).

Or email **<mdferdousalam1989@yahoo.com>** with details and reproduction steps.

You can expect an initial response within a few days.

## Scope

This repository ships agent and skill definitions (Markdown + JSON) for a Claude
Code plugin. It contains no runtime server code. The most relevant concerns are:

- Secrets or credentials accidentally committed (guarded by secret scanning + push
  protection + a gitleaks CI job).
- Prompt content that could induce unsafe automated actions (e.g. destructive git
  operations). The `sdlc-branch-opener` agent is explicitly constrained to never
  force-push, amend, merge, or rebase — report any wording that could be read to
  permit those.
