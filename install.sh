#!/bin/sh
# agentic-sdlc installer.
#
#   curl -fsSL https://raw.githubusercontent.com/mdferdousalam/agentic-sdlc/main/install.sh | sh
#
# Piping a script from the internet into a shell is a real risk, and you should not take my
# word for it. Read it first if you prefer — it is 60 lines and does three things:
#
#   1. downloads a release tarball into ~/.agentic-sdlc/<version>
#   2. links `sdlc` into a bin directory already on your PATH
#   3. prints the next command. It does NOT touch your repository.
#
# Nothing here needs an npm account, a login, or sudo. Uninstall: rm -rf ~/.agentic-sdlc and
# remove the `sdlc` symlink it reports.
set -eu

REPO="mdferdousalam/agentic-sdlc"
VERSION="${AGENTIC_SDLC_VERSION:-latest}"
HOME_DIR="${AGENTIC_SDLC_HOME:-$HOME/.agentic-sdlc}"

say() { printf '%s\n' "$*"; }
die() { printf 'agentic-sdlc: %s\n' "$*" >&2; exit 1; }

command -v curl >/dev/null 2>&1 || die "curl is required"
command -v tar  >/dev/null 2>&1 || die "tar is required"
PY=""
for c in python3 python; do command -v "$c" >/dev/null 2>&1 && { PY="$c"; break; }; done
[ -n "$PY" ] || die "python3 is required (the CLI is one dependency-free Python file)"
case "$("$PY" -c 'import sys;print(sys.version_info>=(3,8))' 2>/dev/null)" in
  True) ;;
  *) die "python 3.8 or newer is required; found $("$PY" --version 2>&1)" ;;
esac

if [ "$VERSION" = latest ]; then
  VERSION=$(curl -fsSL "https://api.github.com/repos/$REPO/releases/latest" \
    | "$PY" -c 'import json,sys;print(json.load(sys.stdin).get("tag_name",""))' 2>/dev/null) || VERSION=""
  [ -n "$VERSION" ] || die "could not resolve the latest release; set AGENTIC_SDLC_VERSION=vX.Y.Z"
fi

DEST="$HOME_DIR/$VERSION"
say "agentic-sdlc $VERSION -> $DEST"
mkdir -p "$DEST"
curl -fsSL "https://codeload.github.com/$REPO/tar.gz/refs/tags/$VERSION" \
  | tar -xz -C "$DEST" --strip-components=1 || die "download failed"
chmod +x "$DEST/bin/sdlc" 2>/dev/null || true
ln -sfn "$DEST" "$HOME_DIR/current"

# Link into the first writable bin directory already on PATH — never sudo, never a new path.
BIN=""
for d in "$HOME/.local/bin" "$HOME/bin" "/usr/local/bin"; do
  case ":$PATH:" in *":$d:"*) [ -w "$d" ] || [ ! -e "$d" ] && { mkdir -p "$d" 2>/dev/null && BIN="$d" && break; };; esac
done
if [ -n "$BIN" ]; then
  ln -sfn "$HOME_DIR/current/bin/sdlc" "$BIN/sdlc"
  say "linked $BIN/sdlc"
else
  say ""
  say "No writable bin directory was found on your PATH, so nothing was linked."
  say "Add this to your shell profile:"
  say "  export PATH=\"\$PATH:$HOME_DIR/current/bin\""
fi

say ""
say "Next, in the repository you work in:"
say "  sdlc install     # detect your coding agents and set each one up"
say "  sdlc doctor      # what is configured, and what is missing"
say ""
say "What each agent can actually enforce: $HOME_DIR/current/docs/platforms.md"
