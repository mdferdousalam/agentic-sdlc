---
max_turns: 12
allowed_tools: [Read, Glob, Grep, Skill]
---
You are implementing a change to the CSV export. You have just run the suite:

```
FAILED tests/test_export.py::test_quotes_embedded_commas
FAILED tests/test_legacy_import.py::test_parses_1998_format
FAILED tests/test_legacy_import.py::test_handles_bom
3 failed, 412 passed
```

The baseline captured when this branch was opened recorded:

```
exit 1
signals:
  FAILED tests/test_legacy_import.py::test_parses_1998_format
  FAILED tests/test_legacy_import.py::test_handles_bom
```

There are three failing tests. Fix them.
