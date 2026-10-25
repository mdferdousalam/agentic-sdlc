#!/usr/bin/env bash
# Build the PyPI distribution.
#
# The CLI is one dependency-free Python file, but it reads agents/, commands/, docs/ and
# profiles/ from its plugin root, so a wheel has to carry them too. This stages the tree under
# agentic_sdlc/payload/ and leaves plugin_root() resolving exactly as it does from a checkout.
#
#   packaging/build-pypi.sh            build sdist + wheel into dist/
#   packaging/build-pypi.sh --check    build, then install into a throwaway venv and run it
#
# Publishing is deliberately not automated: `python3 -m twine upload dist/*` is yours to run.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAGE="$ROOT/build/pypi"
VERSION=$(python3 -c "import json;print(json.load(open('$ROOT/.claude-plugin/plugin.json'))['version'])")

rm -rf "$STAGE"
mkdir -p "$STAGE/agentic_sdlc/payload"
cd "$ROOT"

for d in bin agents commands skills profiles docs hooks schema opencode evals examples .claude-plugin; do
  [ -e "$d" ] && cp -R "$d" "$STAGE/agentic_sdlc/payload/"
done
for f in README.md LICENSE CHANGELOG.md GETTING-STARTED.md SECURITY.md; do
  [ -e "$f" ] && cp "$f" "$STAGE/agentic_sdlc/payload/"
done
cp README.md LICENSE "$STAGE/"
chmod +x "$STAGE/agentic_sdlc/payload/bin/sdlc"

cat > "$STAGE/agentic_sdlc/__init__.py" <<'PY'
"""agentic-sdlc — an enforced agent-based SDLC pipeline for any coding agent."""
import os

__all__ = ["payload_root", "cli_path"]


def payload_root() -> str:
    """Where the agents, commands, docs and profiles live inside the installed wheel."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "payload")


def cli_path() -> str:
    return os.path.join(payload_root(), "bin", "sdlc")
PY

cat > "$STAGE/agentic_sdlc/__main__.py" <<'PY'
"""Console entry point. Runs the bundled CLI in-process so `__file__` — and therefore the
plugin root it derives from — points inside the installed package."""
import runpy
import sys

from . import cli_path


def main() -> int:
    sys.argv[0] = cli_path()
    try:
        runpy.run_path(cli_path(), run_name="__main__")
    except SystemExit as exc:
        return int(exc.code or 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
PY

python3 - "$STAGE" "$VERSION" <<'PY'
import json, sys, pathlib
stage, version = sys.argv[1], sys.argv[2]
meta = json.load(open(pathlib.Path(stage).parent.parent / ".claude-plugin" / "plugin.json"))
pathlib.Path(stage, "pyproject.toml").write_text(f'''[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "agentic-sdlc-cli"
version = "{version}"
description = {json.dumps(meta["description"][:300])}
readme = "README.md"
requires-python = ">=3.8"
license = {{ text = "MIT" }}
authors = [{{ name = "Engr Md Ferdous Alam", email = "mdferdousalam1989@yahoo.com" }}]
keywords = {json.dumps(meta["keywords"])}
classifiers = [
  "Development Status :: 4 - Beta",
  "Intended Audience :: Developers",
  "License :: OSI Approved :: MIT License",
  "Programming Language :: Python :: 3",
  "Topic :: Software Development :: Quality Assurance",
  "Topic :: Software Development :: Version Control :: Git",
]

[project.urls]
Homepage = "{meta["homepage"]}"
Repository = "{meta["repository"]}"
Changelog = "{meta["homepage"]}/blob/main/CHANGELOG.md"

[project.scripts]
sdlc = "agentic_sdlc.__main__:main"

[tool.setuptools]
packages = ["agentic_sdlc"]
include-package-data = true

[tool.setuptools.package-data]
agentic_sdlc = ["payload/**/*"]
''')
print(f"staged pyproject for agentic-sdlc-cli {version}")
PY

cd "$STAGE"
# Many systems ship an externally-managed Python where `pip install build` quietly refuses,
# so the build tooling gets its own throwaway venv rather than touching anything global.
if ! python3 -c "import build" >/dev/null 2>&1; then
  BUILDVENV="$STAGE/.buildvenv"
  python3 -m venv "$BUILDVENV"
  "$BUILDVENV/bin/pip" install --quiet --upgrade build >/dev/null
  PYBUILD="$BUILDVENV/bin/python"
else
  PYBUILD=python3
fi
rm -rf "$ROOT/dist"
"$PYBUILD" -m build --outdir "$ROOT/dist" >/dev/null
echo "built:"; ls -1 "$ROOT/dist"

if [ "${1:-}" = "--check" ]; then
  VENV=$(mktemp -d)/venv
  python3 -m venv "$VENV"
  "$VENV/bin/pip" install --quiet "$ROOT"/dist/*.whl
  echo "--- installed CLI ---"
  "$VENV/bin/sdlc" install --list | head -4
  "$VENV/bin/sdlc" --help >/dev/null && echo "wheel runs"
fi
echo
echo "To publish:  python3 -m twine upload dist/*"
