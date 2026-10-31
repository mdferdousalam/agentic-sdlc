#!/usr/bin/env node
// Thin launcher. The CLI itself is one dependency-free Python file; this exists so that
// `npx @mdferdousalam1989/agentic-sdlc install` works, and so Windows gets a real shim instead of
// relying on a shebang npm cannot honour there.
"use strict";

const { spawnSync } = require("node:child_process");
const { join } = require("node:path");
const { existsSync } = require("node:fs");

const script = join(__dirname, "..", "bin", "sdlc");
if (!existsSync(script)) {
  console.error(`agentic-sdlc: ${script} is missing — the package did not install cleanly.`);
  process.exit(1);
}

// Windows commonly has `py` or `python` rather than `python3`.
const candidates = process.platform === "win32"
  ? ["python", "py", "python3"]
  : ["python3", "python"];

for (const exe of candidates) {
  const probe = spawnSync(exe, ["-c", "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"],
                          { stdio: "ignore" });
  if (probe.error || probe.status !== 0) continue;
  const run = spawnSync(exe, [script, ...process.argv.slice(2)], { stdio: "inherit" });
  process.exit(run.status === null ? 1 : run.status);
}

console.error(
  "agentic-sdlc needs Python 3.8 or newer on PATH.\n" +
  `Tried: ${candidates.join(", ")}.\n` +
  "The CLI is a single file with no Python dependencies — any 3.8+ interpreter will do."
);
process.exit(1);
