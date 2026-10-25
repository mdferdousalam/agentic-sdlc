/**
 * agentic-sdlc for opencode.
 *
 * The same enforcement the Claude Code plugin gets from its PreToolUse hook: every shell
 * command and file edit is offered to `bin/sdlc guard`, which exits 2 when the pipeline would
 * be skipped or something irreversible attempted. The rules live in the Python CLI, so both
 * hosts refuse exactly the same things and there is one place to fix a rule.
 *
 * Installed by `bin/sdlc-install-opencode`, which rewrites PLUGIN_ROOT below.
 */

import { spawnSync } from "node:child_process"

const PLUGIN_ROOT = "__PLUGIN_ROOT__"
const CLI = `${PLUGIN_ROOT}/bin/sdlc`

function ask(tool: string, input: unknown, cwd: string): string | undefined {
  const r = spawnSync(CLI, ["guard"], {
    input: JSON.stringify({ tool_name: tool, tool_input: input, cwd }),
    encoding: "utf8",
    timeout: 10_000,
  })
  // Exit 2 is the block contract; anything else means "no opinion", including a broken CLI —
  // a guard that cannot run must not take the session down with it.
  if (r.status === 2) return (r.stderr || "blocked by agentic-sdlc").trim()
  return undefined
}

export default {
  id: "agentic-sdlc",

  async setup(ctx: any) {
    const cwd: string = ctx?.app?.path?.cwd ?? ctx?.location?.directory ?? process.cwd()

    await ctx.tool.hook("execute.before", (input: any) => {
      const tool = String(input?.tool ?? "")
      const args = input?.input ?? {}
      const mapped =
        tool === "bash" || tool === "shell" ? "Bash"
        : tool === "edit" || tool === "write" || tool === "apply_patch" ? "Edit"
        : null
      if (!mapped) return
      const problem = ask(mapped, args, cwd)
      if (problem) throw new Error(problem)
    })

    await ctx.shell.hook("create.before", (input: any) => {
      const problem = ask("Bash", { command: String(input?.command ?? "") }, String(input?.cwd ?? cwd))
      if (problem) throw new Error(problem)
    })
  },
}
