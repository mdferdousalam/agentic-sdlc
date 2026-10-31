# Standards mapping

Where this pipeline's controls sit against the frameworks people are asked about. This is a
**mapping, not a certification** — it tells you which control a stage implements and what it
does not cover, so you can answer an auditor honestly rather than optimistically.

## NIST AI Risk Management Framework

| Function | What the pipeline provides | What it does not |
| --- | --- | --- |
| **Govern** | `approvals` names who may merge and deploy; `enforce` is explicit, versioned policy in the repository; `neverByAgent` states reserved actions | organisational policy, roles outside the repo, training |
| **Map** | `sdlc trace` links requirement → commit → test → receipts; the specification records intent and scope before code | system-level risk assessment, impact on affected people |
| **Measure** | `sdlc metrics` reports stage outcomes, first-pass rates, refusals, findings by severity and taxonomy domain, verified repair rate, false-fix rate, human-intervention rate and reproducible share, from an append-only log; the five-word vocabulary distinguishes unexecuted from passed | **detection precision and recall** (needs a seeded-defect corpus — see `docs/maturity.md`), model-level evaluation, bias testing, drift monitoring |
| **Manage** | the hook refuses unapproved merges and deployments; receipts expire with the commit; rollback is a required artefact before deploying | incident response outside the repository, vendor risk |

## OWASP Agentic AI — the risks this addresses directly

| Risk | Control here |
| --- | --- |
| Excessive agency | Per-agent permissions; reviewers and gates cannot edit; only the lander touches the remote; tag, release and publish are refused outright |
| Tool misuse | `PreToolUse` hook refuses destructive git, publishing, credential reads and ungated deploys, whatever the prompt says |
| Prompt injection via untrusted content | `docs/rules.md` §7 makes all non-instruction content data; `sdlc-triager` is explicit that a signal's text is never a command; the reviewers look for it |
| Unauthorised actions | Approvals scoped per action — approving a release does not authorise a merge — and voided by the next commit |
| Insufficient oversight | Every stage leaves a receipt; `.sdlc/audit.log` is append-only; `sdlc trace` reconstructs what happened |
| Unbounded consumption | `budget` ceilings refused at the tool call; `sdlc budget reset` requires `--as <person>` and records who accepted the extra cost |
| Agent self-serving evaluation | `sdlc tests audit` detects a diff that lowers the gate it is about to be judged by; `--acknowledge` requires a named person, emits its own audit event, and does not remove the finding |
| Repudiation | Receipts record who claimed each verdict and when, bound to a commit |

## OWASP Non-Human Identity

The agent is an actor, not a function call. What exists: a named actor on every receipt and
audit line, scoped capability per agent, and actions that no agent may perform at all. What
does **not** exist: a cryptographic identity. The pipeline records *who claims* an approval; it
cannot prove a human typed it. If you need that, require signed commits and a signed approval
outside this tool, and treat the receipt as corroboration rather than proof.

## ISO/IEC 42001 and SOC 2 — what an auditor can actually be shown

- **Change management**: every change traces to an approved specification; `sdlc trace` emits
  it as JSON.
- **Segregation of duties**: the agent that writes code is not the agent that reviews it, and
  neither can approve a merge where `approvals.merge` is `human`.
- **Evidence retention**: `.sdlc/audit.log` is append-only and never rotated by this tool. It
  is local to a working copy — ship it to your log store if you need durable retention.
- **Access control**: `enforce` is the policy, in the repository, versioned and reviewable.

## Honest limits

1. **Local, not central.** Receipts and the audit log live in a working copy. A determined
   actor can delete them; the hook refuses the *action*, but it does not protect the record.
   For real assurance, enforce the same gates in CI, where the agent has no write access.
2. **No cryptographic identity. A receipt is a file, not a signature.** Anyone who can write
   to `.sdlc/receipts/` can write one, and the checks on it are consistency checks rather than
   proof of authorship: the commit must match HEAD, the subject digest must match what was
   approved, the timestamp must be neither stale nor in the future, and a receipt granted over
   a clean tree stops holding once the tree is dirty. Those catch a receipt that has drifted
   from the work it describes. They do not catch a hand-written one that is internally
   consistent, and nothing local can — `by` is a string the writer chooses. Every acceptance
   and every refusal is written to `.sdlc/audit.log`, so a forgery leaves a trace; the log is
   local too. CI is the boundary that does not rely on any of this.
3. **Deterministic analysis is yours to supply.** `quality.cmd` runs whatever analyser you
   configure. The pipeline does not ship one, and an LLM reviewer is not a substitute for
   deterministic analysis — it is a complement with different coverage. This is visible rather
   than hidden: a finding records whether it came from a tool or from reading, and the concern
   profiles cap a read finding at `medium` confidence. An auditor can therefore ask how much
   of your coverage is measurement and get a real answer.
4. **The hook is a Claude Code / opencode control.** Someone running `git` in a terminal is
   unaffected. Use git hooks or branch protection for that boundary.
5. **The budget is not cost control.** It counts tool calls and elapsed time, which are
   observable here. It cannot see your model provider's meter, and nothing inside a repository
   can. It stops a runaway task; it does not account for one.
6. **The suite audit is a heuristic over text.** It reads a diff for the patterns that make a
   gate easier to pass. It will over-report, and it will miss a stack whose idioms it does not
   know. It is a control, not a proof, and `--acknowledge` records a human decision rather
   than removing the finding — so the record shows what was accepted and by whom.
7. **Precision and recall are unmeasured.** The pipeline reports what it did, never what it
   missed. Measuring that needs a seeded-defect corpus; `docs/maturity.md` says how.
8. **This has not been audited by anyone.** It is a defensible structure, not a certified one.
