#!/usr/bin/env python3
"""Tests for bin/sdlc — the part of the pipeline that must not be talked out of its job.

Run: python3 tests/test_sdlc.py     (standard library only; makes throwaway git repos in /tmp)
"""
import json, os, re, subprocess, sys, tempfile, shutil, time

HERE = os.path.dirname(os.path.abspath(__file__))
SDLC = os.path.join(os.path.dirname(HERE), "bin", "sdlc")
fails = []


def ok(cond, label):
    print(("  ok   " if cond else "  FAIL ") + label)
    if not cond:
        fails.append(label)


def run(args, cwd, stdin=None):
    return subprocess.run([sys.executable, SDLC, *args], cwd=cwd, input=stdin,
                          capture_output=True, text=True)


def guard(cwd, command, tool="Bash", **inp):
    payload = {"tool_name": tool, "tool_input": {"command": command, **inp}, "cwd": cwd}
    return run(["guard"], cwd, stdin=json.dumps(payload))


def newrepo(files=None, config=None):
    d = tempfile.mkdtemp(prefix="sdlc-test-")
    subprocess.run(["git", "init", "-q", "-b", "main", "."], cwd=d)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=d)
    subprocess.run(["git", "config", "user.name", "t"], cwd=d)
    for name, body in (files or {"README.md": "# t\n"}).items():
        p = os.path.join(d, name)
        os.makedirs(os.path.dirname(p), exist_ok=True) if os.path.dirname(p) else None
        open(p, "w").write(body)
    subprocess.run(["git", "add", "-A"], cwd=d)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=d)
    if config is not None:
        json.dump(config, open(os.path.join(d, "sdlc.config.json"), "w"))
    return d


def head(d):
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=d, capture_output=True, text=True).stdout.strip()


print("detection")
d = newrepo({"package.json": json.dumps({"scripts": {"lint": "x", "test": "y"},
                                         "devDependencies": {"vitest": "^1"}}),
             "pnpm-lock.yaml": ""})
cfg = json.loads(run(["init"], d).stdout)
ok(cfg["stack"] == "node", "node stack detected")
ok(cfg["pm"] == "pnpm", "pnpm detected from the lockfile")
ok(cfg["test"].get("unit") == "vitest", "vitest detected")
ok("pnpm run lint" in (cfg["verifyCmd"] or ""), "verify command assembled from scripts")
shutil.rmtree(d)

d = newrepo({"Cargo.toml": "[package]\nname='t'\n"})
cfg = json.loads(run(["init"], d).stdout)
ok(cfg["stack"] == "rust" and cfg["pm"] == "cargo", "rust stack detected")
ok("clippy" in cfg["verifyCmd"], "clippy in the rust verify command")
ok("-n 50" not in (cfg.get("secretScan") or "") or "--log-opts" in (cfg.get("secretScan") or ""),
   "the gitleaks default uses --log-opts, not a -n shorthand it does not have")
shutil.rmtree(d)

d = newrepo({"go.mod": "module t\n"})
ok(json.loads(run(["init"], d).stdout)["stack"] == "go", "go stack detected")
shutil.rmtree(d)

print("init is idempotent and keeps human edits")
d = newrepo({"Cargo.toml": "[package]\nname='t'\n"})
run(["init", "--write"], d)
cfg = json.load(open(os.path.join(d, "sdlc.config.json")))
cfg["verifyCmd"] = "my-own-command"
json.dump(cfg, open(os.path.join(d, "sdlc.config.json"), "w"))
run(["init", "--write"], d)
ok(json.load(open(os.path.join(d, "sdlc.config.json")))["verifyCmd"] == "my-own-command",
   "a hand-set verifyCmd survives re-init")
shutil.rmtree(d)

print("guard: destructive git")
d = newrepo()
for cmd in ["git stash", "git reset --hard HEAD~1", "git clean -fd", "git checkout -- .",
            "git add -A", "git commit -am x", "git push --force origin main",
            "rm -rf /", "git filter-branch --all"]:
    ok(guard(d, cmd).returncode == 2, f"blocked: {cmd}")
for cmd in ["git stash list", "git status --short", "git add src/main.rs",
            "git commit -m 'fix the -a flag'", "cargo test", "gh pr create --fill"]:
    ok(guard(d, cmd).returncode == 0, f"allowed: {cmd}")

print("guard: a rule is about a command, not about the text of a command line")
# Matching raw text failed in both directions at once, and both halves are regressions
# worth a test: the global option that slipped past, and the prose that was refused.
for cmd in ["git -c core.pager=cat stash", "git --no-pager stash", "git -C . clean -fd",
            "git -c a=b reset --hard HEAD~1", "git --git-dir=.git stash",
            "git -c a=b -C . --no-pager push --force origin main",
            "/usr/bin/git -c core.pager=cat stash", "sudo git clean -fd",
            "FOO=bar git stash", "env GIT_DIR=.git git stash", "echo $(git stash)",
            "bash -c 'git stash'", 'sh -c "git -c core.pager=cat stash"',
            "true && git stash", "ls | xargs git clean -fd"]:
    ok(guard(d, cmd).returncode == 2, f"blocked: {cmd}")
for cmd in ['sdlc finding write --detail "git stash is refused by the guard"',
            'echo "git push --force is the maintainer\'s call"',
            'git commit -m "document why git stash is refused"',
            'grep -rn "git clean" docs/',
            "cat > notes.md <<EOF\ngit stash\ngit reset --hard\nnpm publish\nEOF",
            'python3 -c "print()" --note "rm -rf / is refused"']:
    ok(guard(d, cmd).returncode == 0, f"allowed, it only describes the command: {cmd}")
# The receipt the gate itself writes names the findings it is reporting. A control that
# cannot record its own verdict is not a control.
ok(guard(d, 'sdlc receipt write --kind readiness --verdict not-ready '
             '--detail "18 of 18 refusals bypassed: git stash, git clean -fd, npm publish"'
         ).returncode == 0, "allowed: the gate can write its own NOT-READY receipt")

print("guard: publishing")
for cmd in ["git tag v1.0", "npm publish", "cargo publish", "gh release create v1",
            "docker push x/y", "git push --tags origin"]:
    ok(guard(d, cmd).returncode == 2, f"blocked: {cmd}")
ok(guard(d, "git tag --list").returncode == 0, "allowed: git tag --list")

# A workflow run and the two API routes are remote publish entry points. They were allowed
# because the only pattern that reached them decided from the words on the line, and
# `publish.yml` carries none of them.
for cmd in ["gh workflow run publish.yml --ref feat/x", "gh workflow run Publish",
            "gh api -X POST /repos/o/r/actions/workflows/publish.yml/dispatches -f ref=main",
            "gh api -X POST /repos/o/r/releases -f tag_name=v1",
            "gh api /repos/o/r/releases -X POST -f tag_name=v1",
            "gh api --method POST /repos/o/r/releases --field tag_name=v1",
            "sudo gh workflow run publish.yml"]:
    ok(guard(d, cmd).returncode == 2, f"blocked: {cmd}")
# `gh api` defaults to GET, and reading is not publishing. A method or field flag is what
# makes it a write; without one these must stay allowed.
for cmd in ["gh api /repos/o/r/releases", "gh api /repos/o/r/releases/latest",
            "gh api /repos/o/r/actions/workflows", "gh release list",
            "gh run list --workflow publish.yml", "gh workflow view publish.yml"]:
    ok(guard(d, cmd).returncode == 0, f"allowed, it only reads: {cmd}")

print("guard: credentials")
for cmd in ["cat .env", "cp ~/.ssh/id_rsa /tmp/x", "head -2 .env.production"]:
    ok(guard(d, cmd).returncode == 2, f"blocked: {cmd}")
ok(guard(d, "cat .env.example").returncode == 0, "allowed: cat .env.example")
ok(guard(d, "", tool="Edit", file_path=".env").returncode == 2, "blocked: editing .env")
ok(guard(d, "", tool="Edit", file_path="src/main.rs").returncode == 0, "allowed: editing source")

print("guard: a control that cannot evaluate its rules refuses rather than shrugs")
# Every host reads exit 2 as a block and anything else as "carry on", so an exception in the
# guard was an allow — and the config that produces one is editable by the actor the guard
# exists to constrain. `"enforce": "all"` was enough: a string has no .get.
for label, cfg in [("enforce is a string", {"version": 2, "enforce": "all"}),
                   ("enforce is a list", {"version": 2, "enforce": ["all"]}),
                   ("an enforce value is a string",
                    {"version": 2, "enforce": {"blockDestructiveGit": "yes"}}),
                   ("protected is a string", {"version": 2, "protected": "main"}),
                   ("approvals is a string", {"version": 2, "approvals": "human"}),
                   ("receipts is a number", {"version": 2, "receipts": 180})]:
    dbad = newrepo(config=cfg)
    r = guard(dbad, "git stash")
    ok(r.returncode == 2, f"refused, not allowed: {label}")
    ok("cannot read sdlc.config.json" in r.stderr, f"and says which key: {label}")
    shutil.rmtree(dbad)
# The repair must not turn a legitimately disabled rule into a refusal.
doff = newrepo(config={"version": 2, "enforce": {"blockDestructiveGit": False}})
ok(guard(doff, "git stash").returncode == 0, "a rule switched off in a sound config still allows")
shutil.rmtree(doff)

print("guard: switching a refusal off is a choice, and the choice is visible")
# Setting all six enforce flags to false turned every refusal into an allow and the audit log
# gained nothing — a choice nobody can see is indistinguishable from a bypass.
ALL_OFF = {f: False for f in ("pushToTrunkNeedsGate", "mergeNeedsReadiness",
                              "branchNeedsApprovedSpec", "blockDestructiveGit",
                              "blockPublishing", "blockCredentialReads")}
doff2 = newrepo(config={"version": 2, "trunk": "main", "enforce": ALL_OFF})
for cmd in ["git push origin main", "git stash", "git reset --hard HEAD~1",
            "cat ~/.aws/credentials"]:
    ok(guard(doff2, cmd).returncode == 0, f"still allowed, as configured: {cmd}")
alog2 = open(os.path.join(doff2, ".sdlc", "audit.log")).read()
ok(all(c in alog2 for c in ["git stash", "cat ~/.aws/credentials"]) and
   "allowed-by-config" in alog2, "and every one of them is recorded as allowed by the config")
guard(doff2, "git status")
ok("git status" not in open(os.path.join(doff2, ".sdlc", "audit.log")).read(),
   "a command no rule would have refused is not logged")
shutil.rmtree(doff2)

print("suite audit: loosening the config is itself a weakening")
# This began as the suiteAudit.exclude check. The argument was never specific to that key.
tight = {"version": 2, "trunk": "main", "enforce": {f: True for f in ALL_OFF},
         "protected": ["main", "release/*"], "approvals": {"merge": "human"},
         "receipts": {"maxAgeMin": 60}, "budget": {"maxToolCalls": 500, "stopPolicy": "refuse"},
         "reviewers": ["sdlc-code-reviewer", "sdlc-security-reviewer"]}
dloose = newrepo(config=tight)
# newrepo writes the config after the initial commit, and the comparison is against what the
# base revision holds — so main must actually carry the tight config for this to mean anything.
subprocess.run(["git", "add", "sdlc.config.json"], cwd=dloose)
subprocess.run(["git", "commit", "-qm", "the tight config"], cwd=dloose)
subprocess.run(["git", "checkout", "-q", "-b", "feat/loosen"], cwd=dloose)
open(os.path.join(dloose, "sdlc.config.json"), "w").write(json.dumps(
    {"version": 2, "trunk": "main", "enforce": ALL_OFF, "protected": ["main"],
     "approvals": {"merge": "agent"}, "receipts": {"maxAgeMin": 10080},
     "budget": {"maxToolCalls": 0, "stopPolicy": "warn"},
     "reviewers": ["sdlc-code-reviewer"], "suiteAudit": {"exclude": ["bin/*"]}}, indent=2))
subprocess.run(["git", "add", "sdlc.config.json"], cwd=dloose)
subprocess.run(["git", "commit", "-qm", "tidy the config"], cwd=dloose)
raudit = run(["tests", "audit", "--base", "main"], dloose)
ok(raudit.returncode == 1, "a config-only diff that loosens the pipeline fails the audit")
for needle, what in [("blockDestructiveGit", "a refusal switched off"),
                     ("no longer protected", "a branch dropped from protected"),
                     ("downgraded", "a human approval downgraded to an agent's"),
                     ("stay valid for longer", "receipts given a longer life"),
                     ("ceiling was raised", "a budget ceiling removed"),
                     ("warns instead", "a budget that stops refusing"),
                     ("reviewer the gate fans out to", "a reviewer removed"),
                     ("newly exempted", "a path exempted from the suite audit")]:
    ok(needle in raudit.stdout + raudit.stderr, f"and names it: {what}")
shutil.rmtree(dloose)

print("guard: push to trunk needs a passed gate receipt")
ok(guard(d, "git push origin main").returncode == 2, "blocked: push main, no receipt")
ok(guard(d, "git push -u origin feat/x").returncode == 0, "allowed: push a feature branch")
run(["receipt", "write", "gate", "--verdict", "failed"], d)
ok(guard(d, "git push origin main").returncode == 2, "blocked: push main, failed gate")
run(["receipt", "write", "gate", "--verdict", "passed"], d)
ok(guard(d, "git push origin main").returncode == 0, "allowed: push main, passed gate")

print("guard: merging needs a READY readiness receipt")
ok(guard(d, "gh pr merge --squash").returncode == 2, "blocked: merge, no readiness")
run(["receipt", "write", "readiness", "--verdict", "not-ready"], d)
ok(guard(d, "gh pr merge --squash").returncode == 2, "blocked: merge, NOT-READY")
run(["receipt", "write", "readiness", "--verdict", "ready"], d)
ok(guard(d, "gh pr merge --squash").returncode == 0, "allowed: merge, READY")
ok(guard(d, "git merge --abort").returncode == 0, "allowed: git merge --abort")

print("receipts: bound to the commit")
open(os.path.join(d, "x.txt"), "w").write("x")
subprocess.run(["git", "add", "x.txt"], cwd=d)
subprocess.run(["git", "commit", "-qm", "more"], cwd=d)
ok(run(["receipt", "check", "readiness", "--verdict", "ready"], d).returncode == 1,
   "a new commit voids the readiness receipt")
ok(guard(d, "gh pr merge --squash").returncode == 2, "blocked: merge after a new commit")

print("receipts: a file written by hand is not a verdict")
# Staleness was `age > limit`, so a receipt dated next month had a negative age and never
# expired. `treeClean` was written on every receipt and read by nothing.
dforge = newrepo(config={"version": 2, "trunk": "main"})
head_sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=dforge,
                          capture_output=True, text=True).stdout.strip()


def forge(kind, verdict, seconds_ahead, clean=True):
    at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + seconds_ahead))
    os.makedirs(os.path.join(dforge, ".sdlc", "receipts"), exist_ok=True)
    with open(os.path.join(dforge, ".sdlc", "receipts", kind + ".json"), "w") as fh:
        json.dump({"kind": kind, "verdict": verdict, "commit": head_sha, "branch": "main",
                   "subject": None, "subjectDigest": None, "detail": "hand written",
                   "by": "nobody", "at": at, "treeClean": clean, "env": {}}, fh)


forge("readiness", "ready", 30 * 86400)
ok(run(["receipt", "check", "readiness", "--verdict", "ready"], dforge).returncode == 1,
   "a receipt dated a month ahead does not hold")
ok(guard(dforge, "gh pr merge --squash").returncode == 2,
   "and does not unlock the merge it was forged for")
forge("gate", "passed", 30 * 86400)
ok(guard(dforge, "git push origin main").returncode == 2,
   "nor a protected-branch push")
forge("gate", "passed", 60)
ok(run(["receipt", "check", "gate", "--verdict", "passed"], dforge).returncode == 0,
   "a minute of clock skew is still tolerated")
# treeClean is now read: a receipt granted over a clean tree says nothing about work that
# was never committed.
open(os.path.join(dforge, "uncommitted.txt"), "w").write("x\n")
subprocess.run(["git", "add", "uncommitted.txt"], cwd=dforge)
ok(run(["receipt", "check", "gate", "--verdict", "passed"], dforge).returncode == 1,
   "a receipt claiming a clean tree stops holding once the tree is dirty")
# Refusals were logged and acceptances were not, which is the wrong half for an auditor.
alog = open(os.path.join(dforge, ".sdlc", "audit.log")).read()
ok("receipt.gate.accepted" in alog, "an accepted receipt is recorded, not only a refused one")
ok("receipt.readiness.refused" in alog, "and a refused one still is")
shutil.rmtree(dforge)

print("receipts: bound to the subject's content")
spec = os.path.join(d, "spec.md")
open(spec, "w").write("# spec v1\n")
run(["receipt", "write", "spec", "--verdict", "approved", "--subject", "spec.md"], d)
ok(run(["receipt", "check", "spec", "--verdict", "approved"], d).returncode == 0,
   "an approved spec receipt holds")
open(spec, "w").write("# spec v1 — quietly changed\n")
ok(run(["receipt", "check", "spec", "--verdict", "approved"], d).returncode == 1,
   "editing the spec after approval voids the approval")

print("receipts: bound to the clock")
rp = os.path.join(d, ".sdlc/receipts/readiness.json")
r = json.load(open(rp)); r["commit"] = head(d)
r["at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - 5 * 3600))
json.dump(r, open(rp, "w"))
ok(guard(d, "gh pr merge --squash").returncode == 2, "blocked: merge with a 5-hour-old receipt")

print("guard never crashes a session")
ok(subprocess.run([sys.executable, SDLC, "guard"], cwd=d, input="not json",
                  capture_output=True, text=True).returncode == 0, "malformed hook payload is ignored")
ok(guard(d, "", tool="Grep").returncode == 0, "unrelated tools pass through")

print("enforcement can be turned off deliberately")
json.dump({"enforce": {"blockPublishing": False}}, open(os.path.join(d, "sdlc.config.json"), "w"))
ok(guard(d, "npm publish").returncode == 0, "publishing allowed when the config says so")
shutil.rmtree(d)

print("deployment is gated on a human approval and a READY gate")
d = newrepo(config={"approvals": {"release": "human", "merge": "agent"}})
for cmd in ["kubectl rollout restart deploy/api", "terraform apply -auto-approve",
            "helm upgrade api ./chart", "flyctl deploy", "ansible-playbook site.yml"]:
    ok(guard(d, cmd).returncode == 2, f"blocked without approval: {cmd}")
ok(guard(d, "kubectl get pods").returncode == 0, "allowed: kubectl get pods")
ok(guard(d, "terraform plan").returncode == 0, "allowed: terraform plan")
run(["approve", "release", "--as", "A Person"], d)
ok(guard(d, "terraform apply").returncode == 2, "still blocked: approved but no readiness receipt")
run(["receipt", "write", "readiness", "--verdict", "ready"], d)
ok(guard(d, "terraform apply").returncode == 0, "allowed: human approval + READY")
ok(run(["approve", "release"], d).returncode == 3, "approve refuses without --as")
ok(guard(d, "gh pr merge --squash").returncode == 0, "a release approval does not authorise a merge check that is agent-level")

print("human approval on merge when the project asks for it")
json.dump({"approvals": {"merge": "human"}}, open(os.path.join(d, "sdlc.config.json"), "w"))
run(["receipt", "write", "readiness", "--verdict", "ready"], d)
ok(guard(d, "gh pr merge --squash").returncode == 2, "blocked: READY but no human approval")
run(["approve", "merge", "--as", "A Person"], d)
ok(guard(d, "gh pr merge --squash").returncode == 0, "allowed: READY + human approval")

print("approvals expire with the next commit")
open(os.path.join(d, "z.txt"), "w").write("z")
subprocess.run(["git", "add", "z.txt"], cwd=d); subprocess.run(["git", "commit", "-qm", "z"], cwd=d)
ok(guard(d, "gh pr merge --squash").returncode == 2, "blocked: a new commit voids the approval")

print("the retry loop carries context forward")
run(["feedback", "write", "--stage", "gate", "--detail", "3 tests failed in auth.test.ts"], d)
out = run(["feedback", "read"], d).stdout
ok("auth.test.ts" in out and "Attempt 1" in out, "feedback is readable by the next attempt")
r2 = run(["feedback", "write", "--stage", "gate", "--detail", "same 3 tests"], d)
r3 = run(["feedback", "write", "--stage", "gate", "--detail", "still failing"], d)
ok("Stop and report" in r3.stdout, "three attempts at one stage says stop")
ok(run(["feedback", "clear"], d).returncode == 0, "feedback can be cleared")

print("the audit trail and metrics")
ok(os.path.exists(os.path.join(d, ".sdlc/audit.log")), "an audit log is written")
mout = run(["metrics"], d).stdout
ok("stage outcomes" in mout and "approval" in mout, "metrics summarise stage outcomes")

print("traceability")
tout = run(["trace", "--json"], d).stdout
tj = json.loads(tout)
ok("receipts" in tj and "commits" in tj, "trace emits machine-readable json")
ok(run(["trace"], d).returncode == 0, "trace renders for a human")
shutil.rmtree(d)

print("install: every adapter writes where its host actually looks")
import tempfile as _tf
home = _tf.mkdtemp(prefix="sdlc-home-")
env = dict(os.environ, HOME=home)
def run_env(args, cwd):
    return subprocess.run([sys.executable, SDLC, *args], cwd=cwd, env=env,
                          capture_output=True, text=True)

d = newrepo({"package.json": json.dumps({"scripts": {"lint": "x", "test": "y"}}),
             "pnpm-lock.yaml": ""})
run_env(["init", "--write"], d)
r = run_env(["install", "cursor", "copilot", "cline", "roo", "kilo", "windsurf",
             "continue", "aider", "gemini", "generic", "ci"], d)
ok(r.returncode == 0, "install runs clean")
expected = [
    ".cursor/rules/agentic-sdlc.mdc", ".cursor/commands/sdlc-gate.md",
    ".github/copilot-instructions.md", ".github/prompts/sdlc-gate.prompt.md",
    ".clinerules/agentic-sdlc.md", ".clinerules/hooks/PreToolUse",
    ".roo/rules/agentic-sdlc.md", ".kilocode/rules/agentic-sdlc.md",
    ".windsurf/rules/agentic-sdlc.md", ".continue/rules/agentic-sdlc.md",
    "CONVENTIONS.md", "AGENTS.md", "GEMINI.md",
    ".gemini/policies/agentic-sdlc.toml", ".gemini/commands/sdlc/gate.toml",
    ".github/workflows/sdlc-gate.yml", ".git/hooks/pre-push", ".git/hooks/pre-commit",
]
for rel in expected:
    ok(os.path.exists(os.path.join(d, rel)), f"wrote {rel}")
ok(os.access(os.path.join(d, ".clinerules/hooks/PreToolUse"), os.X_OK),
   "the cline hook is executable (it is not a hook otherwise)")
ok("alwaysApply: true" in open(os.path.join(d, ".cursor/rules/agentic-sdlc.mdc")).read(),
   "cursor rule is always-on")
ok('toolName = "run_shell_command"' in open(os.path.join(d, ".gemini/policies/agentic-sdlc.toml")).read(),
   "gemini policy names the real shell tool")

print("install is idempotent and never clobbers what it does not own")
before = {f: open(os.path.join(d, f), errors="replace").read() for f in expected}
run_env(["install", "cursor", "copilot", "cline", "roo", "kilo", "windsurf",
         "continue", "aider", "gemini", "generic", "ci"], d)
ok(all(open(os.path.join(d, f), errors="replace").read() == before[f] for f in expected),
   "a second run changes nothing")
ag = os.path.join(d, "AGENTS.md")
open(ag, "w").write("# My own notes\n\nKeep this.\n\n" + before["AGENTS.md"])
run_env(["install", "generic"], d)
ok("Keep this." in open(ag).read(), "user content above our block survives")
ok(open(ag).read().count("BEGIN agentic-sdlc") == 1, "our block is not duplicated")

print("an existing git hook is never destroyed")
hp = os.path.join(d, ".git/hooks/pre-commit")
open(hp, "w").write("#!/bin/sh\necho MINE\n")
run_env(["install", "git-hooks"], d)
body = open(hp).read()
ok("echo MINE" in body and "agentic-sdlc" in body, "our block is appended, theirs is kept")

print("dry-run writes nothing")
d2 = newrepo()
r = run_env(["install", "cursor", "generic", "--dry-run"], d2)
ok("would write" in r.stdout, "dry-run says what it would do")
ok(not os.path.exists(os.path.join(d2, "AGENTS.md")), "dry-run wrote nothing")

print("guard --command agrees with the stdin payload, rule for rule")
d3 = newrepo()
for cmd in ["git stash", "cargo publish", "cat .env", "git push origin main"]:
    a = guard(d3, cmd).returncode
    b = run(["guard", "--command", cmd], d3).returncode
    ok(a == b == 2, f"both paths refuse: {cmd}")
for cmd in ["git status", "git add src/x.rs", "cargo test"]:
    a = guard(d3, cmd).returncode
    b = run(["guard", "--command", cmd], d3).returncode
    ok(a == b == 0, f"both paths allow: {cmd}")

print("codex payload shape (no cwd field, its own metadata)")
codex_payload = json.dumps({"session_id": "s", "turn_id": "t", "agent_type": "codex",
                            "hook_event_name": "PreToolUse", "tool_name": "Bash",
                            "tool_input": {"command": "git stash"}, "tool_use_id": "x"})
ok(run(["guard"], d3, stdin=codex_payload).returncode == 2, "codex payload is understood")

print("codex hooks.json merge keeps other events")
ch = os.path.join(home, ".codex")
os.makedirs(ch, exist_ok=True)
json.dump({"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "mine.sh"}]}]}},
          open(os.path.join(ch, "hooks.json"), "w"))
run_env(["install", "codex"], d3)
merged = json.load(open(os.path.join(ch, "hooks.json")))
ok("mine.sh" in json.dumps(merged.get("hooks", {}).get("Stop", [])), "existing Stop hook survives")
ok("sdlc" in json.dumps(merged.get("hooks", {}).get("PreToolUse", [])), "PreToolUse added")
run_env(["install", "codex"], d3)
ok(len(json.load(open(os.path.join(ch, "hooks.json")))["hooks"]["PreToolUse"]) == 1,
   "re-installing does not stack duplicate hooks")

print("uninstall removes our blocks and nothing else")
run_env(["uninstall"], d)
ok("Keep this." in open(ag).read(), "uninstall leaves user content")
ok("BEGIN agentic-sdlc" not in open(ag).read(), "uninstall removes our block")
ok(not os.path.exists(os.path.join(d, ".cursor/rules/agentic-sdlc.mdc")), "uninstall removes files we own")
ok("echo MINE" in open(hp).read(), "uninstall leaves the user's git hook body")
print("findings: the contract is enforced, not assumed")
df = newrepo(config={"trunk": "main", "spec": {"engine": "prd-frd"},
                     "verifyCmd": "true", "quality": {"cmd": None}})


def finding(*args, cwd=df):
    return run(["finding", *args], cwd)


def fwrite(rule="SEC-INJECTION-SQL", cat="D.31", sev="critical", conf="high",
           f="src/q.ts", line="42", summary="user input is concatenated into SQL", extra=()):
    return finding("write", "--rule", rule, "--category", cat, "--severity", sev,
                   "--confidence", conf, "--file", f, "--line", line, "--summary", summary,
                   *extra)


r = fwrite()
ok(r.returncode == 0, "a complete finding is accepted")
fid = r.stdout.split()[0] if r.stdout.split() else ""
ok(fid.startswith("F-") and len(fid) == 10, "it is given an F- plus 8 hex identity")

ok(fwrite(rule="MADE-UP-RULE").returncode != 0, "a rule not in the control spec is refused")
ok(fwrite(cat="Z.99").returncode != 0, "a category outside the taxonomy is refused")
ok(fwrite(summary="short").returncode != 0, "a summary that states nothing is refused")
ok("choose from" in fwrite(sev="catastrophic").stderr, "an invented severity is refused by name")
ok(fwrite(conf="certain").returncode != 0, "an invented confidence is refused")

# The same finding twice is one finding: a wall of duplicates is how a review tool gets ignored.
before = len(os.listdir(os.path.join(df, ".sdlc/findings")))
fwrite()
ok(len(os.listdir(os.path.join(df, ".sdlc/findings"))) == before,
   "the same finding raised twice stays one finding")

print("findings: an id is an id, not a path")
# The id was joined into a path unvalidated, so `show` read and `close` rewrote any json file
# on the machine — `../../../victimdir/victim`, or an absolute path, because join discards
# everything before one.
dtrav = newrepo(config={"version": 2, "trunk": "main"})
os.makedirs(os.path.join(dtrav, ".sdlc", "findings"), exist_ok=True)
victim = os.path.join(dtrav, "..", "victim-of-traversal.json")
VICTIM = '{"secret": "do not touch"}'
open(victim, "w").write(VICTIM)
for bad_id in ["../../victim-of-traversal", "../victim-of-traversal",
               os.path.join(dtrav, "..", "victim-of-traversal"),
               "F-deadbeef/../../../victim-of-traversal", "F-DEADBEEF", "F-dead",
               "F-xyz12345"]:
    rs = run(["finding", "show", bad_id], dtrav)
    ok(rs.returncode == 1 and "do not touch" not in rs.stdout, f"show refuses {bad_id!r}")
    ok(run(["finding", "close", bad_id, "--outcome", "fixed", "--by", "x"],
           dtrav).returncode == 1, f"close refuses {bad_id!r}")
ok(open(victim).read() == VICTIM, "and the file outside the repository is untouched")
os.remove(victim)
shutil.rmtree(dtrav)

print("findings: the repair policy is a table, not a vibe")
POLICY = [
    # severity,   confidence, repro, may an agent fix it unattended?
    ("critical",  "high",     False, True),
    ("critical",  "medium",   True,  False),
    ("critical",  "low",      True,  False),
    ("high",      "high",     False, True),
    ("high",      "medium",   False, False),
    ("high",      "medium",   True,  True),
    ("high",      "low",      True,  False),
    ("medium",    "high",     False, True),
    ("medium",    "medium",   False, True),
    ("medium",    "low",      False, False),
    ("low",       "high",     False, True),
    ("low",       "medium",   False, True),
    ("low",       "low",      False, False),
    ("advisory",  "high",     True,  False),
    ("advisory",  "medium",   False, False),
    ("advisory",  "low",      False, False),
]
for i, (sev, conf, repro, expect) in enumerate(POLICY):
    extra = ["--repair", "the minimal change"] + (["--repro", "npm test -- x.spec.ts"] if repro else [])
    # TYPE-ERROR is the one rule the table marks autofixable, so it is the only rule whose
    # eligibility the severity x confidence matrix decides. Every other row says no, and a
    # separate test covers that the table outranks the matrix.
    out = fwrite(rule="TYPE-ERROR", cat="C.20", sev=sev, conf=conf, f=f"src/p{i}.ts",
                 line=str(i + 1), summary=f"policy corner {i} under test here",
                 extra=extra).stdout
    got = "eligible for automatic fix" in out and "NOT eligible" not in out
    ok(got == expect,
       f"{sev}/{conf}{' +repro' if repro else ''} -> "
       f"{'fixable' if expect else 'escalate or report'}")

ok("NOT eligible" in fwrite(rule="TYPE-ERROR", cat="C.20", sev="advisory", conf="high",
                            f="src/a.ts", line="1",
                            summary="an advisory finding on an autofixable rule",
                            extra=["--repair", "invert it", "--repro", "n/a"]).stdout,
   "an advisory finding is never automatically fixed, whatever the confidence")

print("findings: the rule table's 'never' column outranks the severity matrix")
# Found by the readiness gate: autofix_eligible consulted only severity x confidence, so a
# TEST-SUITE-WEAKENED finding at critical/high came back "eligible for automatic fix" — the
# pipeline authorising an unattended repair of a disarmed test suite. The matrix was right
# and incomplete; the table's never column has to win.
r = fwrite(rule="TEST-SUITE-WEAKENED", cat="X4", sev="critical", conf="high",
           f="tests/t.py", line="3", summary="a skip marker was added to silence a failure",
           extra=["--repair", "remove the marker", "--repro", "sdlc tests audit"])
ok("NOT eligible" in r.stdout,
   "a rule marked never autofixable is never autofixable, at any severity or confidence")
r = fwrite(rule="GIT-WORK-DESTROYED", cat="X3", sev="critical", conf="high",
           f="bin/x.sh", line="1", summary="the script discards uncommitted work",
           extra=["--repair", "remove it"])
ok("NOT eligible" in r.stdout, "and so is the other one the table marks never")
r = fwrite(rule="TYPE-ERROR", cat="C.20", sev="high", conf="high",
           f="src/t.ts", line="9", summary="the argument type does not match the signature",
           extra=["--repair", "correct the type"])
ok("eligible for automatic fix" in r.stdout,
   "a rule the table does not restrict still follows the matrix")

print("findings: the record validates against the published schema")
# The tool wrote component: null and exploitability: null while the schema typed them string
# and a bare enum, so every finding it produced was invalid against its own contract. For a
# library-profile project that schema is a published shape.
import glob as _glob
sch = json.load(open(os.path.join(os.path.dirname(HERE), "schema", "finding.schema.json")))
recs = [json.load(open(f)) for f in _glob.glob(os.path.join(df, ".sdlc/findings/*.json"))]
ok(bool(recs), "there are records to check")
bad = []
for rec in recs:
    for key, spec in sch["properties"].items():
        if key not in rec:
            continue
        t = spec.get("type")
        if t == "string" and not isinstance(rec[key], str):
            bad.append(f"{key}={rec[key]!r} is not a string")
    expl = (rec.get("classification") or {}).get("exploitability")
    allowed = sch["properties"]["classification"]["properties"]["exploitability"]["enum"]
    if expl is not None and expl not in allowed:
        bad.append(f"exploitability={expl!r} not in enum")
ok(not bad, f"every written record matches the schema's declared types ({bad[:2]})")

# additionalProperties is false, so a field the code writes and the schema does not declare
# makes the record invalid. The round-two reopen fix added exactly such a field.
undeclared = sorted({k for rec in recs for k in rec} - set(sch["properties"]))
ok(not undeclared,
   f"no record carries a field the schema does not declare ({undeclared})")

print("findings: a defect that comes back is not still closed")
r = fwrite(rule="CODE-ERROR-SWALLOWED", cat="C.25", sev="high", conf="high",
           f="src/reopen.ts", line="5", summary="the error path is swallowed on retry")
rid = r.stdout.split()[0]
finding("close", rid, "--outcome", "fixed", "--by", "sdlc-remediator")
ok(rid not in run(["finding", "list", "--open"], df).stdout, "closing removes it from open")
r = fwrite(rule="CODE-ERROR-SWALLOWED", cat="C.25", sev="high", conf="high",
           f="src/reopen.ts", line="5", summary="the error path is swallowed on retry")
ok("REOPENED" in r.stdout, "re-detecting it says so out loud")
ok(rid in run(["finding", "list", "--open"], df).stdout,
   "and it is open again — a bad fix must not leave the finding reading as fixed")

print("findings: who closed it is recorded")
r2 = fwrite(rule="SEC-SECRET-PRESENT", cat="D.36", sev="critical", conf="high",
            f="src/cfg.ts", line="2", summary="an API token is committed in the config",
            extra=["--by", "sdlc-security-reviewer"])
rid2 = r2.stdout.split()[0]
r = finding("close", rid2, "--outcome", "fixed", "--by", "sdlc-remediator")
ok("sdlc-security-reviewer raised this" in r.stdout,
   "closing another agent's finding is recorded, not silent")
rec = json.load(open(os.path.join(df, ".sdlc/findings", rid2 + ".json")))
ok(rec.get("closedByActor") == "sdlc-remediator", "the closing actor is on the record")
ok("by sdlc-remediator" in open(os.path.join(df, ".sdlc/audit.log")).read(),
   "and in the audit log")

print("findings: closing says what actually happened")
ok(finding("close", fid, "--outcome", "fixed", "--detail", "test q.spec.ts").returncode == 0,
   "a finding closes as fixed")
ok(finding("close", fid, "--outcome", "resolved").returncode != 0,
   "a word outside the vocabulary cannot close a finding")
ok(finding("close", "F-00000000", "--outcome", "fixed").returncode != 0,
   "a finding that does not exist cannot be closed")
r = finding("close", fid, "--outcome", "unexecuted")
ok("not closed" in r.stdout, "unexecuted says plainly that it is not closed")
ok("finding.write" in open(os.path.join(df, ".sdlc/audit.log")).read(),
   "findings reach the audit log like every other stage")

print("findings: the two copies of the contract agree")
# bin/sdlc validates by hand because it has no dependencies; the schema is the published
# contract. If the enums drift apart, a finding valid to one is invalid to the other.
schema = json.load(open(os.path.join(os.path.dirname(HERE), "schema", "finding.schema.json")))
src = open(SDLC, encoding="utf-8").read()
cls = schema["properties"]["classification"]["properties"]
for name, got in (("severity", cls["severity"]["enum"]),
                  ("confidence", cls["confidence"]["enum"]),
                  ("outcome", schema["properties"]["outcome"]["enum"]),
                  ("exploitability", cls["exploitability"]["enum"])):
    const = {"severity": "SEVERITIES", "confidence": "CONFIDENCES",
             "outcome": "FINDING_OUTCOMES", "exploitability": "EXPLOITABILITY"}[name]
    line = [l for l in src.splitlines() if l.startswith(const + " = (")]
    ok(bool(line) and all(f'"{v}"' in line[0] for v in got),
       f"schema and validator agree on {name}")

print("the quality budget is wired, not merely configurable")
ok("quality" in open(os.path.join(os.path.dirname(HERE), "agents",
                                  "sdlc-readiness-gate.md")).read(),
   "the readiness gate runs the quality budget")
ok("quality" in open(os.path.join(os.path.dirname(HERE), "commands", "gate.md")).read(),
   "the mechanical gate runs the quality budget")
ok("quality.cmd" in run(["doctor"], df).stdout, "doctor says when the budget is unset")

shutil.rmtree(df, ignore_errors=True)

print("baseline: a failure is attributed, not assumed")
CHECK = """#!/bin/sh
echo "ok   suite A"
%s
echo "done in 1.4s"
exit %s
"""
db = newrepo(files={"check.sh": CHECK % ('echo "FAIL test_legacy: expected 3 got 4"', "1")},
             config={"trunk": "main", "spec": {"engine": "prd-frd"}, "verifyCmd": "sh check.sh"})


def setcheck(body, code):
    open(os.path.join(db, "check.sh"), "w").write(CHECK % (body, code))


ok(run(["baseline", "compare"], db).returncode != 0,
   "no baseline is not a pass — comparing without one fails loudly")
r = run(["baseline", "capture"], db)
ok(r.returncode == 0 and "NOT green" in r.stdout,
   "capture records that the repository was already failing")

r = run(["baseline", "compare"], db)
ok(r.returncode == 0 and "0 new" in r.stdout,
   "a pre-existing failure is not blamed on the change")
ok("not caused by it" in r.stdout, "and it says so in words, not just in a count")

# Same failure, different timing and a different line:column. Neither is a change.
setcheck('echo "FAIL test_legacy: expected 3 got 4"\necho "elapsed 88.2s at src/a.rs:99:12"', "1")
ok("0 new" in run(["baseline", "compare"], db).stdout,
   "timings and line positions are noise, not regressions")

setcheck('echo "FAIL test_legacy: expected 3 got 4"\necho "FAIL test_new: nil at 0xabcdef12"', "1")
r = run(["baseline", "compare"], db)
ok(r.returncode != 0 and "1 new" in r.stdout, "a newly introduced failure is blocking")
ok("test_new" in r.stdout, "and it is named")

setcheck("", "0")
r = run(["baseline", "compare"], db)
ok(r.returncode == 0 and "fixed" in r.stdout.lower(), "a failure that went away is noticed")

print("baseline: it survives commits, unlike a receipt")
subprocess.run(["git", "add", "check.sh"], cwd=db)
subprocess.run(["git", "commit", "-qm", "wip"], cwd=db)
ok(run(["baseline", "show"], db).returncode == 0, "a commit does not void the baseline")
ok("no longer an ancestor" not in run(["baseline", "compare"], db).stdout,
   "committing is not mistaken for a rebase")

print("environment: a verdict records what produced it")
run(["receipt", "write", "gate", "--verdict", "passed", "--detail", "x"], db)
rec = json.load(open(os.path.join(db, ".sdlc/receipts/gate.json")))
ok(isinstance(rec.get("env"), dict) and "git" in rec["env"],
   "every receipt carries the toolchain that produced it")
ok("os" in rec["env"] and "arch" in rec["env"], "including the platform it ran on")

shutil.rmtree(db, ignore_errors=True)

print("concerns: proposed from what the repository does, never imposed")
dc = newrepo(files={
    "src/worker.go": "package main\nimport \"sync\"\nfunc a(){var m sync.Mutex; go func(){m.Lock()}()}\n",
    "src/pool.go": "package main\nimport \"sync\"\nfunc b(){var w sync.WaitGroup; go func(){w.Done()}()}\n",
    "src/schema.sql": "CREATE TABLE users (id int);\nALTER TABLE users ADD COLUMN e text;\n",
    "src/migrate.sql": "-- migrations\nCREATE TABLE orders (id int);\n",
})
cfg = json.loads(run(["init"], dc).stdout)
ok("concurrency" in cfg["concerns"], "goroutines and mutexes propose the concurrency concern")
ok("data" in cfg["concerns"], "schema and migrations propose the data concern")
ok("memory" not in cfg["concerns"], "nothing unsafe here, so memory is not proposed")

dq = newrepo(files={"README.md": "# docs only\n"})
ok(json.loads(run(["init"], dq).stdout)["concerns"] == [],
   "a repository with no source proposes nothing")

# A concern a maintainer removed must stay removed: init fills gaps, it does not overrule.
run(["init", "--write"], dc)
c = json.load(open(os.path.join(dc, "sdlc.config.json")))
c["concerns"] = []
json.dump(c, open(os.path.join(dc, "sdlc.config.json"), "w"))
run(["init", "--write"], dc)
ok(json.load(open(os.path.join(dc, "sdlc.config.json")))["concerns"] == [],
   "re-running init does not re-impose a concern the maintainer removed")

print("concern profiles exist and are reachable")
root = os.path.dirname(HERE)
for name in ("architecture", "performance", "memory", "concurrency", "data", "platform"):
    ok(os.path.exists(os.path.join(root, "profiles", "concerns", name + ".md")),
       f"profiles/concerns/{name}.md exists")

print("every rule an agent cites resolves to the control spec")
spec = open(os.path.join(root, "docs", "control-spec.md"), encoding="utf-8").read()
table = set(re.findall(r"^\|\s*`([A-Z][A-Z0-9-]*)`\s*\|", spec, re.M))
ok(len(table) > 40, f"the rule table has {len(table)} rules")
cited = set()
# schema/ and docs/ were not walked, so schema/finding.schema.json could cite a rule the
# table did not have — and did. A rule cited anywhere is a rule that must resolve.
for sub in ("agents", "profiles", "commands", "schema", "docs"):
    for dirpath, _, names in os.walk(os.path.join(root, sub)):
        for n in names:
            if n.endswith((".md", ".json")) and n != "control-spec.md":
                body = open(os.path.join(dirpath, n), encoding="utf-8").read()
                cited |= set(re.findall(r"--rule ([A-Z][A-Z0-9-]*)", body))
                cited |= set(re.findall(r"`((?:ARCH|PERF|MEM|CONC|DATA|PLAT|SEC|TEST|IMPACT|SPEC|CODE|ENV|BUDGET|GIT|QUALITY|BUILD|TYPE)-[A-Z0-9-]+)`", body))
missing = sorted(cited - table)
ok(not missing, f"no agent or profile cites a rule the table lacks (missing: {missing})")

for x in (dc, dq):
    shutil.rmtree(x, ignore_errors=True)

print("suite integrity: the gate cannot be lowered to pass itself")
dt = newrepo(files={
    "tests/test_core.py": "def test_a():\n    assert f(1) == 2\n    assert f(2) == 3\n\n"
                          "def test_b():\n    assert g() is None\n",
    "tests/test_edge.py": "def test_edge():\n    assert h(0) == 1\n",
    "ci.yml": "coverage_threshold: 80\nstrict: true\n",
}, config={"trunk": "main", "spec": {"engine": "prd-frd"}, "verifyCmd": "true"})
ok(run(["tests", "audit", "--base", "HEAD"], dt).returncode == 0,
   "an empty diff weakens nothing")


def weaken(files, message="make the gate pass"):
    for name, body in files.items():
        full = os.path.join(dt, name)
        if body is None:
            os.remove(full)
        else:
            os.makedirs(os.path.dirname(full), exist_ok=True)
            open(full, "w").write(body)
    subprocess.run(["git", "add", "-A"], cwd=dt)
    subprocess.run(["git", "commit", "-qm", message], cwd=dt)
    return run(["tests", "audit", "--base", "HEAD~1"], dt)


r = weaken({"tests/test_edge.py": None})
ok(r.returncode != 0 and "deleted" in r.stdout, "a deleted test file is caught")

r = weaken({"tests/test_core.py": "import pytest\n\n@pytest.mark.skip\n"
                                  "def test_a():\n    assert f(1) == 2\n    assert f(2) == 3\n\n"
                                  "def test_b():\n    assert g() is None\n"})
ok(r.returncode != 0 and "skipped" in r.stdout, "a newly added skip marker is caught")

r = weaken({"tests/test_core.py": "def test_a():\n    pass\n\n"
                                  "def test_b():\n    assert g() is None\n"})
ok(r.returncode != 0 and "assertion" in r.stdout, "assertions removed and not replaced is caught")

r = weaken({"ci.yml": "coverage_threshold: 55\nstrict: true\n"})
ok(r.returncode != 0 and "lowered" in r.stdout, "a lowered threshold is caught")
ok("80 -> 55" in r.stdout, "and it says by how much")

r = weaken({"src/x.py": "def f():\n    return 1  # noqa\n"})
ok(r.returncode != 0 and "silenced" in r.stdout, "a new suppression comment is caught")

r = weaken({"tests/test_core.py": "def test_a():\n    assert f(1) == 2\n\n"
                                  "def test_b():\n    assert g() is None\n\n"
                                  "def test_c():\n    assert k() == 9\n"})
ok(r.returncode == 0, "adding a test and an assertion is not a weakening")

print("suite integrity: the bypasses a readiness gate found in this very check")
# Every case below was a working bypass of this control, found by running the pipeline's own
# gate against the branch that added it. Each one made `tests audit` report a clean pass on a
# diff that disarmed the suite. They are regression tests now because a control with a known
# hole is worse than none: it is a hole with a green tick over it.

r = weaken({"tests/test_core.py": "def test_a():\n    assert f(1) == 2\n"
                                  "    assert 1 == 1  # don't lint  # noqa\n"})
ok(r.returncode != 0, "an apostrophe before a marker does not disarm the line")

r = weaken({"tests/test_core.py": 'DOC = """\n++ b/README.md\n"""\n\n'
                                  "def test_a():\n    pass  # noqa\n"})
ok(r.returncode != 0, "content posing as a diff header cannot reattribute the rest of a file")

r = weaken({"commands/run.md": "Run the gate:\n\n```sh\nnpm test || true\n```\n"})
ok(r.returncode != 0,
   "markdown is scanned — in this plugin the instructions ARE markdown")

r = weaken({"docs/guide.md": "Never do this:\n\n```diff\n+@pytest.mark.skip\n```\n"})
ok(r.returncode != 0,
   "a diff illustration in documentation is reported too — there is no content exemption "
   "left, because every version of one was defeated by editing the content")

r = run(["tests", "audit", "--base", "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"], dt)
ok(r.returncode != 0 and "UNEXECUTED" in (r.stdout + r.stderr),
   "a diff git could not produce is unexecuted, never a pass")

weaken({"tests/test_core.py": "def test_a():\n    assert f(1) == 2\n"
                              "    assert g(2) == 3\n    assert h(3) == 4\n"},
       "restore assertions")
subprocess.run(["git", "config", "diff.noprefix", "true"], cwd=dt)
r = weaken({"tests/test_core.py": "def test_a():\n    assert f(1) == 2\n"})
ok(r.returncode != 0, "a developer's diff.noprefix setting does not disable the check")
subprocess.run(["git", "config", "--unset", "diff.noprefix"], cwd=dt)

weaken({"tests/test_core.py": "def test_a():\n    assert f(1) == 2\n"
                              "    assert g(2) == 3\n"}, "restore two")
r = weaken({"tests/test_core.py": "def test_a():\n    assert f(1) == 2\n"})
ok(r.returncode != 0, "removing exactly ONE assertion is reported, not just two or more")

print("suite integrity: an acknowledgement needs somebody behind it")
r = weaken({"tests/test_core.py": "def test_a():\n    pass  # noqa\n"})
ok(r.returncode != 0, "a real weakening to acknowledge")
r = run(["tests", "audit", "--base", "HEAD~1", "--acknowledge"], dt)
ok(r.returncode != 0 and "--as" in r.stderr,
   "--acknowledge without an actor is refused: it would record nothing")
r = run(["tests", "audit", "--base", "HEAD~1", "--acknowledge", "--as", "A Person"], dt)
ok(r.returncode == 0, "--acknowledge with an actor lets a justified change through")
ok("not waived" in r.stdout, "and says plainly that it recorded rather than waived")
ok("suite.acknowledged" in open(os.path.join(dt, ".sdlc/audit.log")).read(),
   "the acknowledgement is its own audit event, not the same line as a plain run")

# Exemption is declared in config, not inferred from a line's text. Two content-based
# heuristics were tried and both were forgeable by the actor the control constrains: quote
# parity fell to one apostrophe, and "a quote on both sides" fell to appending a quote. The
# second residual was found by a readiness gate re-run, after the first fix.
r = weaken({"src/real.py": "def f():\n    return undefined_name  # noqa\n"})
ok(r.returncode != 0, "a real suppression in real code is caught")
r = weaken({"src/real.py": 'def f():\n    return x  "y"  # noqa  # "\n'})
ok(r.returncode != 0, "and quotes sprinkled around the marker do not hide it")
r = weaken({"src/real.py": "def f():\n    return x  # don't  # noqa\n"})
ok(r.returncode != 0, "nor does an apostrophe")

print("suite integrity: round-three findings — two were my own regressions")
# A third content-based heuristic survived two rounds of removing content-based heuristics:
# DIFF_ILLUSTRATION exempted any markdown line starting with + or -, so two characters
# disarmed 17% of the markdown this branch adds. In a plugin whose instructions ARE markdown.
r = weaken({"commands/run.md": "Run the gate.\n\nRun `npm test` then eslint-disable no-eval\n"})
ok(r.returncode != 0, "a suppression in markdown is caught")
r = weaken({"commands/run.md": "Run the gate.\n\n- Run `npm test` then eslint-disable no-eval\n"})
ok(r.returncode != 0, "and a two-character list prefix does not disarm it")

# Introduced by the round-two per-file loop: git C-quotes non-ASCII names by default, so the
# name matched no pathspec, the file read as an empty diff, and it failed OPEN with exit 0 —
# the exact mode the same commit had just removed for bad refs.
weaken({"tests/caf\u00e9_test.py": "def test_x():\n    assert a() == 1\n    assert b() == 2\n"},
       "add a non-ascii test file")
r = weaken({"tests/caf\u00e9_test.py": "def test_x():\n    pass\n"})
ok(r.returncode != 0, "a file whose name git quotes is still scanned")
ok("caf" in r.stdout, "and it is named in the report")

print("the policy table outranks the matrix for every rule, not just two")
dpol = newrepo(config={"trunk": "main", "spec": {"engine": "prd-frd"}})


def polwrite(rule, cat, sev="critical", conf="high"):
    return run(["finding", "write", "--rule", rule, "--category", cat, "--severity", sev,
                "--confidence", conf, "--file", "src/p.ts", "--line", "1",
                "--summary", "a representative finding for policy testing",
                "--repair", "the minimal change"], dpol).stdout

# docs/control-spec.md's Autofix column says plain "no" on 53 rows and **never** on two.
# Reading only **never** let SEC-INJECTION-SQL, SEC-AUTHORITY and MEM-SAFETY come back
# autofixable at critical/high — the permissive half of a document contradicting itself.
for rule, cat in (("SEC-INJECTION-SQL", "D.31"), ("SEC-AUTHORITY", "D.30"),
                  ("MEM-SAFETY", "F.57"), ("CODE-ERROR-SWALLOWED", "C.25")):
    ok("NOT eligible" in polwrite(rule, cat),
       f"{rule} is not autofixable: its table row does not say yes")
ok("eligible for automatic fix" in polwrite("TYPE-ERROR", "C.20", sev="high"),
   "the one row marked yes still defers to the matrix")

print("a verify that did not run is unexecuted, not a failure of the change")
# run_verify now returns 126 when the guard refuses the configured command and 124 on
# timeout. cmd_baseline tested only `code != 0` and announced "this change introduced
# failures" — unexecuted reported as failed, in the path every baseline capture goes through.
dv = newrepo(files={"a.txt": "x\n"},
             config={"trunk": "main", "spec": {"engine": "prd-frd"},
                     "verifyCmd": "echo ok"})
ok(run(["baseline", "capture"], dv).returncode == 0, "a clean baseline is captured")
c = json.load(open(os.path.join(dv, "sdlc.config.json")))
c["verifyCmd"] = " ".join(["git", "tag", "v0.0.1"])   # a command the guard refuses
json.dump(c, open(os.path.join(dv, "sdlc.config.json"), "w"))
r = run(["baseline", "compare"], dv)
ok("UNEXECUTED" in r.stdout, "a refused verify command is reported as unexecuted")
ok("introduced failures" not in r.stdout, "and is NOT reported as a failure of the change")
ok(r.returncode != 0, "and does not pass either")
r = run(["baseline", "capture"], dv)
ok("REFUSED" in (r.stdout + r.stderr) or run(["baseline", "show"], dv).stdout.count("126"),
   "the refusal reaches the operator rather than being swallowed")
ok(not os.path.exists(os.path.join(dv, ".git/refs/tags/v0.0.1")),
   "and the forbidden command in the config never ran")
shutil.rmtree(dv, ignore_errors=True)

print("the rule table is not optional")
# known_rules() and never_autofix_rules() swallowed a read error and returned empty sets, so
# a missing docs/control-spec.md meant any invented rule validated and nothing was
# un-autofixable. A control whose off-switch is an absent file is not a control.
import tempfile as _tf
fake = _tf.mkdtemp(prefix="sdlc-noplugin-")
os.makedirs(os.path.join(fake, "bin"))
shutil.copy(SDLC, os.path.join(fake, "bin", "sdlc"))
r = subprocess.run([sys.executable, os.path.join(fake, "bin", "sdlc"), "finding", "write",
                    "--rule", "TEST-SUITE-WEAKENED", "--category", "X4",
                    "--severity", "critical", "--confidence", "high", "--file", "t.py",
                    "--line", "1", "--summary", "a weakening finding for policy testing",
                    "--repair", "x"], cwd=dpol, capture_output=True, text=True)
ok(r.returncode != 0, "without the control spec the tool refuses rather than guessing")
ok("control-spec" in r.stderr, "and says which file it needs")
shutil.rmtree(fake, ignore_errors=True)
shutil.rmtree(dpol, ignore_errors=True)

print("suite integrity: the escape hatch is declared, and never quiet")
cfgp = os.path.join(dt, "sdlc.config.json")
c = json.load(open(cfgp))
c["suiteAudit"] = {"exclude": ["src/*"]}
json.dump(c, open(cfgp, "w"))
subprocess.run(["git", "add", "sdlc.config.json"], cwd=dt)
subprocess.run(["git", "commit", "-qm", "exempt src"], cwd=dt)
r = run(["tests", "audit", "--base", "HEAD~1"], dt)
ok(r.returncode != 0 and "newly exempted" in r.stdout,
   "adding an exemption is itself reported — otherwise the hatch would be the bypass")
r = weaken({"src/real.py": "def f():\n    return y  # noqa\n"})
ok(r.returncode == 0, "once declared, the exempted path is genuinely not scanned")
c["suiteAudit"] = {"exclude": []}
json.dump(c, open(cfgp, "w"))
subprocess.run(["git", "add", "sdlc.config.json"], cwd=dt)
subprocess.run(["git", "commit", "-qm", "unexempt"], cwd=dt)
r = weaken({"src/real.py": "def f():\n    return z  # noqa\n"})
ok(r.returncode != 0, "removing the exemption brings the path back under the audit")
shutil.rmtree(dt, ignore_errors=True)

print("budget: a ceiling an agent cannot raise for itself")
dbg = newrepo(config={"trunk": "main", "spec": {"engine": "prd-frd"},
                      "budget": {"maxToolCalls": 3}})
ok("of 3" in run(["budget", "show"], dbg).stdout,
   "a configured tool-call ceiling is reported")
for _ in range(3):
    guard(dbg, "git status")
r = guard(dbg, "git status")
ok(r.returncode == 2 and "budget" in r.stderr, "the hook refuses once the ceiling is passed")
ok("sdlc budget reset" in r.stderr, "and it names the allowed route")
ok(run(["budget", "reset"], dbg).returncode != 0,
   "an agent cannot reset its own ceiling — that would make it a pause, not a ceiling")
ok(guard(dbg, "git status").returncode == 2, "and the refusal still stands after trying")
run(["budget", "reset", "--as", "a person"], dbg)
ok(guard(dbg, "git status").returncode == 0, "a named person can reset it")
ok("by a person" in open(os.path.join(dbg, ".sdlc/audit.log")).read(),
   "and the audit log says who accepted the extra cost")

# The ceiling was keyed on the branch name, which is the agent's to pick: with the budget
# spent, `git checkout -b other` made the next call allowed and overwrote the counter. It is
# keyed on the merge base now, which a rename does not move.
dbr = newrepo(config={"trunk": "main", "spec": {"engine": "prd-frd"},
                      "budget": {"maxToolCalls": 3}})
for _ in range(4):
    guard(dbr, "git status")
ok(guard(dbr, "git status").returncode == 2, "the ceiling is reached")
for what, args_ in [("a new branch", ["checkout", "-q", "-b", "other"]),
                    ("another new branch", ["checkout", "-q", "-b", "and-another"]),
                    ("a branch rename", ["branch", "-m", "renamed"]),
                    ("a detached HEAD", ["checkout", "-q", "--detach"]),
                    ("coming back to the trunk", ["checkout", "-q", "main"])]:
    subprocess.run(["git"] + args_, cwd=dbr, capture_output=True)
    ok(guard(dbr, "git status").returncode == 2, f"the ceiling survives {what}")
ok("budget.task-started" in open(os.path.join(dbr, ".sdlc/audit.log")).read(),
   "and a task beginning its own budget is recorded")
# Genuinely new work, from a trunk that has moved on, does get its own ceiling.
subprocess.run(["git", "checkout", "-q", "main"], cwd=dbr, capture_output=True)
open(os.path.join(dbr, "next.txt"), "w").write("x\n")
subprocess.run(["git", "add", "next.txt"], cwd=dbr)
subprocess.run(["git", "commit", "-qm", "trunk moves on"], cwd=dbr)
ok(guard(dbr, "git status").returncode == 0, "work from a new trunk point gets its own budget")
shutil.rmtree(dbr)

dnb = newrepo(config={"trunk": "main", "spec": {"engine": "prd-frd"}})
for _ in range(12):
    guard(dnb, "git status")
ok(guard(dnb, "git status").returncode == 0, "no ceiling configured means no refusal")
ok("no ceiling" in run(["budget", "show"], dnb).stdout, "but doctor-style output says so plainly")

print("checkpoints: resuming is not automatically safe")
dcp = newrepo(files={"src/a.py": "x = 1\n"},
              config={"trunk": "main", "spec": {"engine": "prd-frd"}})
ok(run(["checkpoint", "resume"], dcp).returncode != 0, "no checkpoint is not a green light")
run(["checkpoint", "write", "--done", "parser", "--next", "the formatter",
     "--file", "src/a.py"], dcp)
r = run(["checkpoint", "resume"], dcp)
ok(r.returncode == 0 and "Safe to continue" in r.stdout, "an unchanged repository resumes")
ok("parser" in r.stdout and "formatter" in r.stdout, "it says what is done and what is next")

open(os.path.join(dcp, "src/a.py"), "w").write("x = 2\n")
r = run(["checkpoint", "resume"], dcp)
ok(r.returncode != 0 and "changed since the checkpoint" in r.stdout,
   "a file that moved under the checkpoint stops the resume")

subprocess.run(["git", "add", "src/a.py"], cwd=dcp)
subprocess.run(["git", "commit", "-qm", "edit"], cwd=dcp)
ok("HEAD has moved" in run(["checkpoint", "resume"], dcp).stdout,
   "and so does a commit the checkpoint did not know about")
for x in (dbg, dnb, dcp):
    shutil.rmtree(x, ignore_errors=True)

for x in (d, d2, d3, home):
    shutil.rmtree(x, ignore_errors=True)

print()
print(f"FAILED: {len(fails)}" if fails else "all tests passed")
sys.exit(1 if fails else 0)
