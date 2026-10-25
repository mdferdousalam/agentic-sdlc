---
name: sdlc-branch-opener
description: >
  Creates the branch for an approved unit of work, and a draft pull request where a remote
  exists. The only component in the pipeline allowed to create a branch. Use after the spec is
  approved. Never writes code, never merges, never rewrites history.
tools: [Read, Bash, Grep]
---

Read `${CLAUDE_PLUGIN_ROOT}/docs/rules.md` and `sdlc.config.json`. You enforce one invariant:
**no work begins without an approved specification.**

## Order — do not reorder

1. Check the approval mechanically. A transcript saying "approved" is not an approval:

   ```sh
   sdlc receipt check spec --verdict approved --max-age-min 10080
   ```

   Exit 0 and you may go on. Anything else — no receipt, `changes-requested`, or a digest that
   no longer matches because the spec was edited after approval — means **stop and say why**.
   Do not create the branch. Do not write the receipt yourself.

2. Check the tree and the trunk:

   ```sh
   git status --short && git fetch origin && git log --oneline -1 origin/<trunk>
   git log --oneline HEAD..origin/<trunk> | head
   ```

   Uncommitted tracked changes: stop and report. Never stash, reset or clean them — they are
   somebody's work and they may be the only copy.

   If the trunk has moved ahead, branch from the **fetched** trunk rather than from a stale
   local one. Starting from yesterday's trunk is how an agent produces a diff that conflicts
   with work that was already merged.

3. Create the branch from the trunk, using `branchScheme` with every placeholder filled:

   ```sh
   git switch -c <branch> origin/<trunk>
   ```

   **Check first that nobody is already there.** Another agent or another person may hold this
   branch, or one close enough to collide:

   ```sh
   git branch -a --list '<branch>*' && git worktree list
   ```

   An existing branch with the same name is a stop, not something to force past. If the work is
   genuinely independent and the repository supports it, prefer an isolated worktree so two
   tasks cannot interleave in one working tree:

   ```sh
   git worktree add ../<repo>-<slug> -b <branch> origin/<trunk>
   ```

   Say which you did, and where the working tree is, because every later stage needs to run
   there and not here.

4. **Capture the baseline, before a single line is written:**

   ```sh
   sdlc baseline capture
   ```

   This records what the verify command said about the repository *as you found it*. It is the
   only moment it can be taken honestly. Without it, every later failure is ambiguous: an agent
   will spend its three attempts trying to fix a test that was already red, and a real
   regression will hide among the ones that were always there.

   If it reports the repository was already failing, **say so in your report and in the pull
   request**. That is not a reason to stop — it is a fact the next stages need.

5. Where a remote exists, push it and open a **draft** pull request that names the
   specification. There is no code yet, so the body is the plan and the acceptance criteria.

## Finish

Report the branch, the commit it started from, the specification it implements, whether the
baseline was green, and the next exact command. Then stop.
