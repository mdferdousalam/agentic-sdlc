#!/usr/bin/env python3
"""Tests for bin/sdlc — the part of the pipeline that must not be talked out of its job.

Run: python3 tests/test_sdlc.py     (standard library only; makes throwaway git repos in /tmp)
"""
import json, os, subprocess, sys, tempfile, shutil, time

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

print("guard: publishing")
for cmd in ["git tag v1.0", "npm publish", "cargo publish", "gh release create v1",
            "docker push x/y", "git push --tags origin"]:
    ok(guard(d, cmd).returncode == 2, f"blocked: {cmd}")
ok(guard(d, "git tag --list").returncode == 0, "allowed: git tag --list")

print("guard: credentials")
for cmd in ["cat .env", "cp ~/.ssh/id_rsa /tmp/x", "head -2 .env.production"]:
    ok(guard(d, cmd).returncode == 2, f"blocked: {cmd}")
ok(guard(d, "cat .env.example").returncode == 0, "allowed: cat .env.example")
ok(guard(d, "", tool="Edit", file_path=".env").returncode == 2, "blocked: editing .env")
ok(guard(d, "", tool="Edit", file_path="src/main.rs").returncode == 0, "allowed: editing source")

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
    out = fwrite(sev=sev, conf=conf, f=f"src/p{i}.ts", line=str(i + 1),
                 summary=f"policy corner {i} under test here", extra=extra).stdout
    got = "eligible for automatic fix" in out and "NOT eligible" not in out
    ok(got == expect,
       f"{sev}/{conf}{' +repro' if repro else ''} -> "
       f"{'fixable' if expect else 'escalate or report'}")

ok("NOT eligible" in fwrite(rule="ARCH-CYCLE", cat="B.11", sev="advisory", conf="high",
                            f="src/a.ts", line="1",
                            summary="an architectural trade-off worth noting",
                            extra=["--repair", "invert it", "--repro", "n/a"]).stdout,
   "an advisory finding is never automatically fixed, whatever the confidence")

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

for x in (d, d2, d3, home):
    shutil.rmtree(x, ignore_errors=True)

print()
print(f"FAILED: {len(fails)}" if fails else "all tests passed")
sys.exit(1 if fails else 0)
