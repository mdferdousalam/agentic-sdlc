// Validates the plugin's structural contract in CI.
// WHY: there is nothing to compile, so "does it build" means "would Claude Code load every
// piece of this, and do the pieces agree with each other". Each failure names the file and the
// field, so a contributor can fix it without reading this script.
import { readFileSync, existsSync, readdirSync, statSync, accessSync, constants } from "node:fs";
import { join } from "node:path";

const errors = [];
const warn = [];
const fail = (m) => errors.push(m);

const frontmatter = (file) => {
  const m = readFileSync(file, "utf8").match(/^---\r?\n([\s\S]*?)\r?\n---/);
  return m ? m[1] : null;
};
const field = (fm, name) => {
  const m = fm.match(new RegExp(`^${name}\\s*:\\s*(.*)$`, "m"));
  return m ? m[1].trim() : null;
};
const has = (fm, name) => new RegExp(`^${name}\\s*:`, "m").test(fm);

// 1. Manifests
const manifest = ".claude-plugin/plugin.json";
let plugin = {};
if (!existsSync(manifest)) fail(`missing ${manifest}`);
else {
  plugin = JSON.parse(readFileSync(manifest, "utf8"));
  for (const f of ["name", "description", "version"])
    if (!plugin[f]) fail(`plugin.json: missing required field "${f}"`);
  if (plugin.version && !/^\d+\.\d+\.\d+/.test(plugin.version))
    fail(`plugin.json: version "${plugin.version}" is not semver`);
}
const market = ".claude-plugin/marketplace.json";
if (existsSync(market)) {
  const j = JSON.parse(readFileSync(market, "utf8"));
  if (!Array.isArray(j.plugins) || j.plugins.length === 0)
    fail('marketplace.json: "plugins" must be a non-empty array');
  else if (plugin.name && !j.plugins.some((p) => p.name === plugin.name))
    fail(`marketplace.json: no entry named "${plugin.name}"`);
}

// 2. Agents — frontmatter, and the name must match the filename or the Task tool cannot find it
const agentNames = new Set();
if (existsSync("agents")) {
  for (const f of readdirSync("agents").filter((f) => f.endsWith(".md"))) {
    const p = join("agents", f);
    const fm = frontmatter(p);
    if (!fm) { fail(`${p}: missing YAML frontmatter`); continue; }
    for (const k of ["name", "description"]) if (!has(fm, k)) fail(`${p}: frontmatter missing "${k}"`);
    const name = field(fm, "name");
    if (name) {
      agentNames.add(name);
      if (name !== f.replace(/\.md$/, "")) fail(`${p}: frontmatter name "${name}" does not match the filename`);
    }
    const body = readFileSync(p, "utf8");
    if (!body.includes("docs/rules.md")) warn.push(`${p}: does not point the agent at docs/rules.md`);
  }
}

// 3. Commands — frontmatter description, and no stale ${CLAUDE_PLUGIN_ROOT} typos
if (existsSync("commands")) {
  for (const f of readdirSync("commands").filter((f) => f.endsWith(".md"))) {
    const p = join("commands", f);
    const fm = frontmatter(p);
    if (!fm) { fail(`${p}: missing YAML frontmatter`); continue; }
    if (!has(fm, "description")) fail(`${p}: frontmatter missing "description"`);
    const body = readFileSync(p, "utf8");
    for (const m of body.matchAll(/\$\{?CLAUDE_PLUGIN_ROOT\}?/g))
      if (m[0] !== "${CLAUDE_PLUGIN_ROOT}") fail(`${p}: write \${CLAUDE_PLUGIN_ROOT}, not ${m[0]}`);
    for (const m of body.matchAll(/`sdlc-[a-z-]+`/g)) {
      const n = m[0].slice(1, -1);
      if (!agentNames.has(n)) fail(`${p}: references agent "${n}", which does not exist`);
    }
  }
}

// 4. Skills
if (existsSync("skills")) {
  for (const d of readdirSync("skills")) {
    const dir = join("skills", d);
    if (!statSync(dir).isDirectory()) continue;
    const sf = join(dir, "SKILL.md");
    if (!existsSync(sf)) { fail(`skills/${d}: missing SKILL.md`); continue; }
    const fm = frontmatter(sf);
    if (!fm) { fail(`${sf}: missing YAML frontmatter`); continue; }
    for (const k of ["name", "description"]) if (!has(fm, k)) fail(`${sf}: frontmatter missing "${k}"`);
    const name = field(fm, "name");
    if (name && name !== d) fail(`${sf}: frontmatter name "${name}" does not match the directory`);
  }
}

// 5. Hooks — the enforcement contract; a plugin without them is advisory only
const hooksFile = "hooks/hooks.json";
if (!existsSync(hooksFile)) fail(`missing ${hooksFile} — without it the pipeline cannot enforce anything`);
else {
  const h = JSON.parse(readFileSync(hooksFile, "utf8"));
  const pre = h?.hooks?.PreToolUse;
  if (!Array.isArray(pre) || pre.length === 0) fail("hooks.json: no PreToolUse entry");
  else {
    const cmds = pre.flatMap((e) => (e.hooks || []).map((x) => x.command || ""));
    if (!cmds.some((c) => c.includes("${CLAUDE_PLUGIN_ROOT}/bin/sdlc")))
      fail("hooks.json: PreToolUse does not call ${CLAUDE_PLUGIN_ROOT}/bin/sdlc guard");
  }
}

// 6. The CLI must exist and be executable, or every hook silently does nothing
const cli = "bin/sdlc";
if (!existsSync(cli)) fail(`missing ${cli}`);
else {
  try { accessSync(cli, constants.X_OK); } catch { fail(`${cli} is not executable (chmod +x)`); }
  const first = readFileSync(cli, "utf8").split("\n")[0];
  if (!first.startsWith("#!")) fail(`${cli}: missing shebang`);
}

// 7. Schema parses, and the profiles the README advertises exist
if (existsSync("schema/sdlc.config.schema.json")) JSON.parse(readFileSync("schema/sdlc.config.schema.json", "utf8"));
for (const p of ["webapp", "library", "service", "compiler"])
  if (!existsSync(`profiles/${p}.md`)) fail(`profiles/${p}.md is referenced by the docs but missing`);

for (const w of warn) console.warn("  warn - " + w);
if (errors.length) {
  console.error("Plugin validation FAILED:");
  for (const e of errors) console.error("  - " + e);
  process.exit(1);
}
console.log(`Plugin validation passed (${agentNames.size} agents)`);
