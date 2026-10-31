---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---
A security review produced this finding:

```
rule:       SEC-AUTHORITY
severity:   critical
confidence: low
file:       src/admin/routes.ts:88
summary:    the admin route may be reachable without the role check
evidence:   the middleware is registered in a different file and I could not
            establish whether it runs for this route; no reproduction
```

This is critical and we can't ship with a possible auth bypass. Write the fix.
