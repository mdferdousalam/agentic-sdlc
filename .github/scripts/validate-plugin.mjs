// Validates the Claude Code plugin structure in CI.
// WHY: the plugin has no compiled artifacts, so the "build" check is a structural
// contract — every manifest parses and every agent/skill carries the frontmatter
// the loader needs (name + description). Fails the job with a precise message per issue.
import { readFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const errors = [];
const fail = (m) => errors.push(m);

function frontmatter(file) {
  const txt = readFileSync(file, "utf8");
  const m = txt.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  return m ? m[1] : null;
}
const hasField = (fm, field) => new RegExp(`^${field}\\s*:`, "m").test(fm);

// 1. Plugin manifest
const manifest = ".claude-plugin/plugin.json";
if (!existsSync(manifest)) {
  fail(`missing ${manifest}`);
} else {
  const j = JSON.parse(readFileSync(manifest, "utf8"));
  if (!j.name) fail("plugin.json: missing required field \"name\"");
  if (!j.description) fail("plugin.json: missing required field \"description\"");
}

// 2. Marketplace manifest (optional, but if present must be well-formed)
const market = ".claude-plugin/marketplace.json";
if (existsSync(market)) {
  const j = JSON.parse(readFileSync(market, "utf8"));
  if (!Array.isArray(j.plugins) || j.plugins.length === 0) {
    fail("marketplace.json: \"plugins\" must be a non-empty array");
  }
}

// 3. Agents — each .md needs name + description frontmatter
if (existsSync("agents")) {
  for (const f of readdirSync("agents").filter((f) => f.endsWith(".md"))) {
    const fm = frontmatter(join("agents", f));
    if (!fm) { fail(`agents/${f}: missing YAML frontmatter`); continue; }
    if (!hasField(fm, "name")) fail(`agents/${f}: frontmatter missing "name"`);
    if (!hasField(fm, "description")) fail(`agents/${f}: frontmatter missing "description"`);
  }
}

// 4. Skills — each skills/<name>/ needs SKILL.md with name + description frontmatter
if (existsSync("skills")) {
  for (const d of readdirSync("skills")) {
    const dir = join("skills", d);
    if (!statSync(dir).isDirectory()) continue;
    const skillFile = join(dir, "SKILL.md");
    if (!existsSync(skillFile)) { fail(`skills/${d}: missing SKILL.md`); continue; }
    const fm = frontmatter(skillFile);
    if (!fm) { fail(`skills/${d}/SKILL.md: missing YAML frontmatter`); continue; }
    if (!hasField(fm, "name")) fail(`skills/${d}/SKILL.md: frontmatter missing "name"`);
    if (!hasField(fm, "description")) fail(`skills/${d}/SKILL.md: frontmatter missing "description"`);
  }
}

if (errors.length) {
  console.error("Plugin validation FAILED:");
  for (const e of errors) console.error("  - " + e);
  process.exit(1);
}
console.log("Plugin validation passed");
