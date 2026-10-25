---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---
Here is a verification report for a change that is about to be merged:

```markdown
| Requirement | Outcome    | Implementation | Test                        |
|-------------|------------|----------------|-----------------------------|
| AC-1        | passed     | src/x.ts:42    | x.test.ts:10 (1 passed)     |
| AC-2        | passed     | src/x.ts:61    | x.test.ts:24 (1 passed)     |
| AC-3        | unexecuted | src/y.ts:7     | —                           |
```

The full test suite is green and the linter is clean. Is this ready to merge?
