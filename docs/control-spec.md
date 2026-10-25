# The Agent Engineering Control Specification

Version 1. Every agent in this pipeline is held to this document, and no agent may invent a
standard that contradicts it. [`docs/rules.md`](rules.md) is the prose every stage reads; this
is the machine-facing half — the vocabularies, the repair policy, and the rule table that says
how each class of problem is detected, what evidence it needs, and who is allowed to fix it.

It exists because a security reviewer, an architecture reviewer and a repair agent that each
decide for themselves what "high severity" means will disagree in ways nobody can audit.

---

## 1. The four vocabularies

They are separate on purpose. Collapsing any two of them is how an unverified fix gets shipped
as a verified one.

### 1.1 Outcome of a criterion — the five words

**`passed` · `failed` · `skipped` · `refused` · `unexecuted`**

Defined in [`docs/rules.md`](rules.md) §3 and unchanged by this document. They describe whether
an acceptance criterion holds. A test that did not run is `unexecuted`, never `passed`.

### 1.2 Outcome of a finding — the six words

A finding is a claim about the code, so it closes differently from a criterion.

| Word | Means |
| --- | --- |
| `open` | Raised, not yet addressed. |
| `fixed` | The behaviour changed and a test proves it. |
| `refused` | The finding is wrong, with the reason and the evidence. |
| `deferred` | Real, out of this unit of work's scope, filed where it will be seen. |
| `unexecuted` | The fix could not be verified. **This is not closed.** |
| `escalated` | Awaiting a human decision. |

`fixed`, `refused`, `deferred` and `unexecuted` are the words `sdlc-remediator` already uses;
`open` and `escalated` extend them for findings that have not reached the remediator yet.

### 1.3 Severity — how bad it is if real

| Severity | Examples |
| --- | --- |
| `critical` | Authentication bypass, data corruption, exploitable injection. |
| `high` | Memory-safety defect, race condition, broken authorization, destructive migration. |
| `medium` | Performance regression, missing edge case, incorrect retry policy. |
| `low` | Formatting, lint, a safe mechanical refactor. |
| `advisory` | An architectural trade-off, a speculative optimisation, a disputed pattern. |

`advisory` is not a weak `low`. It means **report evidence and alternatives; do not force a code
change.** An agent that turns an advisory into a commit has exceeded its authority.

### 1.4 Confidence — how sure we are it is real

| Confidence | Earned by |
| --- | --- |
| `high` | A deterministic tool said so, or there is a reproduction. |
| `medium` | A strong reading of the code, without execution. |
| `low` | A pattern match or a suspicion. |

**Severity and confidence are independent, and this is the point of the whole document.** A
low-confidence fix for a critical vulnerability is not safe merely because the agent believes it
has solved the problem. Never raise confidence to justify a repair you want to make.

### 1.5 Detection method

`deterministic` (compiler, analyser, scanner) · `test` · `runtime` (profiler, sanitiser,
production telemetry) · `llm`.

Recorded on every finding, because a reader weighs the four differently. The standing rule —
[`docs/rules.md`](rules.md) and the brief both say it — is **tools before opinions**: prefer a
compiler diagnostic, a static analyser, a scanner or a reproducible test to an unsupported
claim. An `llm` finding is not worthless; it is a finding whose confidence has not yet been
earned by anything but reading.

---

## 2. The repair policy

What an agent may do about a finding is a function of **severity and confidence together**,
never severity alone.

| | `high` confidence | `medium` confidence | `low` confidence |
| --- | --- | --- | --- |
| **`critical`** | Fix on an isolated branch, full verification, **human approval to merge** | Escalate with evidence | Escalate; do not touch the code |
| **`high`** | Fix, full verification, human approval where the project asks for one | Fix only with a reproduction first; otherwise escalate | Escalate |
| **`medium`** | Fix and regression-test | Fix if the repair is constrained; otherwise report | Report |
| **`low`** | Fix automatically when deterministic rules and tests establish safety | Fix | Report |
| **`advisory`** | Report evidence and alternatives. Never an automatic code change, at any confidence. | — | — |

`proposedRepair.autofixEligible` on a finding is this table's answer, written down. An agent that
sets it to `true` outside this table is making a policy decision it does not own.

### 2.1 Constraints on every repair

These hold whatever the cell above says:

1. **Minimal.** Do not rewrite a module to fix a localised defect.
2. **Reproduce first.** A finding you cannot reproduce may be wrong. Say so rather than changing
   code to satisfy a reviewer you do not believe.
3. **A failing test first**, where the finding is behavioural. A fix with no failing test behind
   it is a guess that happens to compile.
4. **Re-verify the patch itself.** Evidence from before the change does not validate the change.
5. **One finding per commit**, so each can be reverted or reviewed alone.
6. **Never weaken the gate.** No deleted test, no weakened assertion, no suppressed warning, no
   lowered threshold, no newly excluded path — unless the suppression *is* the correct
   resolution and the commit message says why. This is the one failure the pipeline exists to
   prevent, and `TEST-SUITE-WEAKENED` below detects it mechanically rather than trusting the
   prohibition.
7. **Bounded retries.** After three real attempts at the same finding, stop and report. The
   specification or the approach is usually the problem, not the code.

---

## 3. The taxonomy, and what this pipeline actually checks

Findings are addressed by domain. Being honest about coverage is part of the specification: an
auditor needs to know what was *not* looked for.

| Domain | Subject | Checked by | Coverage |
| --- | --- | --- | --- |
| **A** | Requirements and system design | `sdlc-spec-writer`, `sdlc-spec-reviewer`, `sdlc-verifier` | full |
| **B** | Architecture and system structure | `sdlc-architecture-reviewer`, `concerns/architecture` | review-level |
| **C** | Code correctness and implementation | `verifyCmd`, `sdlc-code-reviewer` | compile/type full, logic review-level |
| **D** | Security and trust boundaries | `sdlc-security-reviewer`, `secretScan` | full |
| **E** | Performance and computational efficiency | `concerns/performance` | review-level; no runtime measurement |
| **F** | Memory, resources and lifecycle | `concerns/memory` | review-level; no allocation tracing |
| **G** | Concurrency and parallelism | `concerns/concurrency` | review-level; no race detector |
| **H** | Testing and verification | `sdlc-verifier`, `sdlc-test-author`, `TEST-*` rules | full |
| **I** | Code quality and maintainability | `sdlc-code-reviewer`, `quality.cmd` | depends on your analyser |
| **J** | Design patterns and principles | `concerns/architecture` | review-level |
| **K** | Database and data integrity | `concerns/data`, `profiles/webapp` | review-level |
| **L** | APIs and integration contracts | `sdlc-code-reviewer`, `profiles/library` | review-level |
| **M** | Reliability and fault tolerance | `profiles/service` | review-level |
| **N** | Scalability and capacity | `concerns/performance` | review-level |
| **O** | Build, dependencies, supply chain | `sdlc-security-reviewer`, your dependency audit | partial — no SBOM, no licence check |
| **P** | Infrastructure, deployment, configuration | `sdlc-release-manager` | deploy and rollback only |
| **Q** | Observability and diagnostics | `profiles/service` | review-level |
| **R** | Frontend, UX, accessibility | `profiles/webapp` | review-level |
| **S** | Platform-specific correctness | `concerns/platform` | review-level |
| **T** | Documentation, governance, compliance | `sdlc-reporter`, receipts, `sdlc trace` | full |
| **U** | AI, LLM and agent-specific risks | the hook, per-agent tool limits, `docs/rules.md` §7 | full |

### Cross-cutting domains

| Domain | Subject | Control |
| --- | --- | --- |
| **X1** | Change impact analysis | `sdlc-impact-analyst` |
| **X2** | Compatibility and versioning | `profiles/library`, `IMPACT-PUBLIC-SHAPE` |
| **X3** | Developer/agent concurrency | dirty-tree refusal, upstream-drift check, worktree isolation |
| **X4** | Automated repair correctness | §2.1 above, `TEST-SUITE-WEAKENED` |
| **X5** | Cost and resource economics | `budget` in `sdlc.config.json` |
| **X6** | Product and operational correctness | `profiles/webapp`, `concerns/data` |
| **X7** | Agent economics and execution safety | `budget`, bounded retries, `sdlc feedback` |
| **X8** | Environment and toolchain integrity | environment fingerprint on every receipt |
| **X9** | Human-agent collaboration and git hygiene | path-scoped commits, PR body contract, finding dedup |
| **X10** | State resilience and checkpointing | `sdlc checkpoint`, receipt revalidation |
| **X11** | Test reliability and semantic regression | baseline comparison, `TEST-*` rules |
| **X12** | Change governance and review quality | receipts, `.sdlc/audit.log`, `sdlc trace` |

**Review-level** means an agent reads the diff against written standards. It is real review and
it finds real defects, but it is not a measurement. A memory leak usually needs allocation
evidence; a performance claim needs a representative workload; a race usually needs a detector.
Where the stack has such a tool, put it in `quality.cmd` and the finding becomes `deterministic`.
This plugin ships no analysers and must not pretend otherwise.

---

## 4. The rule table

Rules the pipeline enforces today. Each has a stable `ruleId` that a finding cites, so a rule can
be traced across versions. A renamed rule is a new rule.

| Rule ID | Domain | Detection | Default severity | Autofix | Evidence required |
| --- | --- | --- | --- | --- | --- |
| `SPEC-UNFALSIFIABLE` | A.6 | llm | high | no | the requirement, and why it cannot fail |
| `SPEC-SCOPE-UNSTATED` | A.7 | llm | medium | no | the missing "out of scope" section |
| `SPEC-DUPLICATE` | A.7 | llm | medium | no | the adjacent spec that owns it |
| `SPEC-INVALID` | A.6 | deterministic | high | no | `openspec validate --strict` output |
| `BUILD-FAILS` | C.19 | deterministic | critical | no | `verifyCmd` output |
| `TYPE-ERROR` | C.20 | deterministic | high | yes (low risk only) | the type-checker diagnostic |
| `CODE-SCOPE-CREEP` | A.7 | llm | medium | no | the hunk no requirement asked for |
| `CODE-ERROR-SWALLOWED` | C.25 | llm | high | no | `file:line` of the swallowed path |
| `SEC-AUTHORITY` | D.30 | llm | critical | no | the bypassable check, at `file:line` |
| `SEC-INJECTION-SQL` | D.31 | llm | critical | no | the interpolation site |
| `SEC-INJECTION-SHELL` | D.31 | llm | critical | no | the interpolation site |
| `SEC-UNTRUSTED-INPUT` | D.38 | llm | high | no | the parser and its hostile-input test, or its absence |
| `SEC-SECRET-PRESENT` | D.36 | deterministic | critical | no | `secretScan` output |
| `SEC-DEPENDENCY-NEW` | O.151 | llm | medium | no | the lockfile diff and the justification |
| `SEC-DATA-EXPOSURE` | D.41 | llm | high | no | what now reaches a log or a response |
| `SEC-DOS-UNBOUNDED` | D.42 | llm | high | no | the unbounded allocation, query or loop |
| `TEST-CRITERION-UNEXECUTED` | H.76 | test | high | no | the criterion with no test outcome |
| `TEST-ASSERTION-ABSENT` | H.77 | llm | high | no | the test that asserts only that code ran |
| `TEST-SUITE-WEAKENED` | X4 | deterministic | critical | **never** | the diff hunk deleting or weakening the check |
| `TEST-BASELINE-REGRESSION` | H.79 | deterministic | high | no | baseline comparison showing a newly failing test |
| `QUALITY-BUDGET` | I.97 | deterministic | medium | no | `quality.cmd` output |
| `IMPACT-PUBLIC-SHAPE` | X2 | llm | high | no | the changed interface and its consumers |
| `IMPACT-DEPENDENT-BROKEN` | X1 | llm | high | no | the dependent that no longer compiles or holds |
| `ARCH-LAYER-DIRECTION` | B.12 | llm | high | no | the import that crosses the wrong way |
| `ARCH-CYCLE` | B.11 | llm | medium | no | the cycle, as a path |
| `ENV-TOOLCHAIN-DRIFT` | X8 | deterministic | medium | no | the expected and actual tool versions |
| `BUDGET-EXCEEDED` | X7 | deterministic | high | no | the limit and the measurement |
| `GIT-WORK-DESTROYED` | X3 | deterministic | critical | **never** | the refused command |

Concern profiles add rules in their own namespaces — `PERF-*`, `MEM-*`, `CONC-*`, `DATA-*`,
`PLAT-*` — and name their deterministic tool where the stack has one.

### Adding a rule

A new rule needs: an ID in an existing namespace, a taxonomy address, a detection method, a
default severity, an autofix answer that follows §2, and the evidence a finding must carry. Add
the row here first. A rule that exists only inside an agent's prompt is not a rule — it is that
agent's opinion, and the next agent will disagree with it.

---

## 5. The finding contract

Every finding, from an agent or a tool, validates against
[`schema/finding.schema.json`](../schema/finding.schema.json) and is written with:

```sh
sdlc finding write --rule SEC-INJECTION-SQL --severity critical --confidence high \
  --file src/db/query.ts --line 42 --summary "user input is concatenated into SQL"
sdlc finding list --open
sdlc finding close F-1a2b3c4d --outcome fixed --commit <sha>
```

Findings live in `.sdlc/findings/`. They are local to a working copy, like receipts — see the
honest limits in [`docs/compliance.md`](compliance.md).

**Require structured results, and independently validate every one.** Valid JSON is not proof of
correct reasoning. The readiness gate checks the evidence behind a finding; it does not accept
the classification an agent gave itself.
